"""Extraction eCRF : têtes de sélection et de normalisation au-dessus de GLiNER2.

Ce fichier ne dépend que de `torch`, `transformers` et du paquet `gliner2`.

Pour chaque champ de l'eCRF, un softmax unique porte sur trois ensembles d'options : les
spans du document, les valeurs observées à l'entraînement pour ce champ, et l'abstention.
Si un span est retenu, un transducteur caractère le réécrit sous forme canonique.

    S = span_rep ⊗ schema            le score que GLiNER2 calcule déjà (0 paramètre ajouté)
    options = { S } ∪ { vocabulaire } ∪ { ⊥ }
    softmax → si copie : transducteur(texte du span, libellé du champ) → valeur
            → si vocabulaire : la chaîne telle quelle
            → si ⊥ : champ laissé vide
    on remplit si p > 0.5   (seuil déduit de la matrice de coût, aucun paramètre libre)

Le modèle ne contient aucun paramètre indexé par champ ni par classe : un champ n'intervient
que par son libellé, encodé en caractères, et les options de vocabulaire sont des chaînes
encodées par l'encodeur. Les mêmes poids s'appliquent donc à un autre schéma ou à une classe
non observée à l'entraînement.

COMPATIBILITÉ. Le modèle a été entraîné avec un fork de GLiNER2 dont la seule divergence
est un patch de focal loss dans le calcul de la LOSS D'ENTRAÎNEMENT, derrière la variable
d'environnement `GLINER_FOCAL`, désactivé par défaut. L'inférence est identique à
l'upstream. Les seuls attributs utilisés ici — `compute_span_rep`, `count_embed`,
`_encode_batch`, `processor`, `encoder` — sont ceux du `Extractor` standard.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import torch
import torch.nn as nn

PAD, BOS, EOS, UNK = 0, 1, 2, 3
MAXSPAN, MAXLAB, MAXOUT = 200, 60, 32
D = 768


# --------------------------------------------------------------------------- tête B
class Transducer2(nn.Module):
    """Texte d'un span → valeur canonique, caractère par caractère.

    Le libellé du champ conditionne l'ÉTAT INITIAL du décodeur au lieu d'être concaténé à
    l'entrée : les spans d'un document s'encodent donc une seule fois et sont partagés
    par les 89 champs. Mesuré à budget identique, cette forme est aussi meilleure
    (0.895 contre 0.869 en exact-match).
    """

    def __init__(self, V, d=128, h=256, hf=128):
        super().__init__()
        self.emb = nn.Embedding(V, d, padding_idx=PAD)
        self.enc = nn.GRU(d, h, batch_first=True, bidirectional=True)
        self.fld = nn.GRU(d, hf, batch_first=True, bidirectional=True)
        self.h0 = nn.Linear(2 * h + 2 * hf, h)
        self.dec = nn.GRU(d + 2 * h, h, batch_first=True)
        self.att = nn.Linear(2 * h + h, h)
        self.att_v = nn.Linear(h, 1)
        self.out = nn.Linear(h + 2 * h, V)

    @staticmethod
    def _pool(e, mask):
        return e.masked_fill(mask.unsqueeze(-1), 0).sum(1) / (~mask).sum(1, keepdim=True).clamp(min=1)

    def encode_span(self, x):
        e, _ = self.enc(self.emb(x))
        mask = x == PAD
        return e, mask, self._pool(e, mask)

    def encode_field(self, xf):
        e, _ = self.fld(self.emb(xf))
        return self._pool(e, xf == PAD)

    def init_state(self, pooled, fvec, extra=None):
        z = self.h0(torch.cat([pooled, fvec], -1))
        return torch.tanh(z if extra is None else z + extra).unsqueeze(0)

    def step(self, y_emb, h, e, mask):
        q = h[-1].unsqueeze(1).expand(-1, e.shape[1], -1)
        a = self.att_v(torch.tanh(self.att(torch.cat([e, q], -1)))).squeeze(-1)
        a = torch.softmax(a.masked_fill(mask, -1e9), -1)
        ctx = (a.unsqueeze(-1) * e).sum(1)
        o, h = self.dec(torch.cat([y_emb, ctx], -1).unsqueeze(1), h)
        return self.out(torch.cat([o.squeeze(1), ctx], -1)), h


# --------------------------------------------------------------------------- tête A
class AssignHead(nn.Module):
    """P(option | champ) sur { spans } ∪ { vocabulaire } ∪ { ⊥ }.

    Le score de copie EST `S`, le score bilinéaire natif de GLiNER2 : mesuré, un MLP
    par-dessus n'apporte rien (−0.000 au rang 1, et la tête s'effondre à 0.187 sans son
    ancrage sur `S`). Il ne reste donc AUCUN paramètre pour choisir un span ; tout ce
    qui subsiste sert à noter les options hors-texte et à convertir.
    """

    def __init__(self, d=D, h=256):
        super().__init__()
        # conservés pour charger les checkpoints entraînés avec (inutilisés au forward)
        self.f_proj, self.s_proj, self.o_proj = nn.Linear(d, h), nn.Linear(d, h), nn.Linear(h, 1)
        self.pos_proj = nn.Linear(3, h)
        self.summ = nn.Linear(d, d)
        self.vocab = nn.Sequential(nn.Linear(2 * d, h), nn.GELU(), nn.Linear(h, d))
        self.nul = nn.Sequential(nn.Linear(2 * d, h), nn.GELU(), nn.Linear(h, 1))
        self.beta = nn.Parameter(torch.ones(1))   # poids de S
        self.alpha = nn.Parameter(torch.zeros(1))  # compétition entre champs — reste à 0
        self.tau = nn.Parameter(torch.ones(1))     # calibration de log P_B
        self.sr_to_h = nn.Linear(d, 256)           # span_rep → décodeur du transducteur

    def doc_summary(self, S, H):
        """Somme et non moyenne : la norme croît avec le nombre de spans détectés,
        donc le comptage reste représentable."""
        return self.summ(torch.sigmoid(S) @ H)

    def forward(self, E, pool):
        H, S = pool["H"], pool["S"]
        z = self.doc_summary(S, H)
        u = (self.f_proj(E).unsqueeze(1) + self.s_proj(H).unsqueeze(0)
             + self.pos_proj(pool["pos"]).unsqueeze(0))
        cp = self.o_proj(torch.tanh(u)).squeeze(-1) + self.beta * S \
            + self.alpha * torch.log_softmax(S, dim=0)
        fz = torch.cat([E, z], dim=-1)
        return cp, self.vocab(fz), self.nul(fz)


# --------------------------------------------------------------------------- utilitaires GLiNER2
def word_offsets(model, text):
    return [(s, e) for _, s, e in model.processor.word_splitter(text, lower=True)]


def detection_scores(model, span_rep, markers, count=1):
    """`S` = le score bilinéaire natif. `count=1` : c'est la valeur avec laquelle la
    détection a été entraînée (le processor écrit structure[0]=1 pour la tâche `entities`)."""
    sp = model.count_embed(markers[1:], count)
    if sp.dim() == 2:
        sp = sp.unsqueeze(0)
    return torch.einsum("lkd,bpd->bplk", span_rep, sp)[0]


def markers_of(all_sch_i):
    m = all_sch_i[0]
    return torch.stack(m) if isinstance(m, list) else m


@torch.no_grad()
def encode_texts(model, texts, dev, maxlen=48):
    tok = model.processor.tokenizer
    enc = tok(texts, padding=True, truncation=True, max_length=maxlen, return_tensors="pt").to(dev)
    out = model.encoder(input_ids=enc["input_ids"], attention_mask=enc["attention_mask"])
    m = enc["attention_mask"].unsqueeze(-1).float()
    return (out.last_hidden_state * m).sum(1) / m.sum(1).clamp(min=1)


@torch.no_grad()
def build_pool(model, token_emb, text, markers, M=256):
    """Élague le document à M spans par un critère INDÉPENDANT DU CHAMP.

    Le rang (et non le score brut) parce que les scores de deux champs ne sont pas à la
    même échelle : un `max` brut laisse les champs bruyants monopoliser le pool.
    """
    span_rep = model.compute_span_rep(token_emb)["span_rep"]
    L, W = span_rep.shape[0], span_rep.shape[1]
    dsc = detection_scores(model, span_rep, markers)
    woff = word_offsets(model, text)
    Lw = min(L, len(woff))
    flat = dsc[:, :Lw].reshape(dsc.shape[0], -1)
    rank = torch.empty_like(flat)
    order = flat.argsort(dim=1, descending=True)
    rank.scatter_(1, order, torch.arange(flat.shape[1], device=flat.device,
                                         dtype=flat.dtype).expand_as(flat))
    idx = torch.topk(-rank.min(0).values, min(M, flat.shape[1])).indices
    spans, keep = [], []
    for ix in idx.tolist():
        i, w = ix // W, ix % W
        cs, ce = woff[i][0], woff[min(i + w, len(woff) - 1)][1]
        if ce > cs:
            spans.append((i, w, cs, ce)); keep.append(ix)
    keep = torch.tensor(keep, device=span_rep.device)
    nT = max(len(text), 1)
    pos = torch.tensor([[cs / nT, i / max(Lw - 1, 1), w / max(W - 1, 1)]
                        for i, w, cs, ce in spans], device=span_rep.device, dtype=span_rep.dtype)
    return {"H": span_rep[:Lw].reshape(-1, span_rep.shape[-1])[keep],
            "S": flat[:, keep], "pos": pos, "spans": spans,
            "texts": [text[cs:ce] for _, _, cs, ce in spans]}


# --------------------------------------------------------------------------- le modèle complet
class ECRFExtractor:
    """Charge un checkpoint publié et remplit l'eCRF d'un document.

        m = ECRFExtractor.from_pretrained("rntc/mc-bio-gliner-lymphome-ecrf")
        m.extract(texte)   # -> {champ: valeur ou None}
    """

    def __init__(self, model, head, transducer, stoi, itos, space, schema, device="cpu"):
        self.model, self.head, self.tr = model, head, transducer
        self.stoi, self.itos, self.space, self.schema = stoi, itos, space, schema
        self.dev = device
        self.keys = [k for k in schema if k in space]
        self._opt = None
        self._fv = {}

    @classmethod
    def from_pretrained(cls, repo_or_path, device="cpu"):
        from gliner2 import GLiNER2
        p = Path(repo_or_path)
        if not p.exists():
            from huggingface_hub import snapshot_download
            p = Path(snapshot_download(repo_id=str(repo_or_path)))
        model = GLiNER2.from_pretrained(str(p)).to(device).eval()
        ck = torch.load(p / "assign.pt", map_location=device)
        head = AssignHead().to(device)
        missing, _ = head.load_state_dict(ck["head"], strict=False)
        if any("pos_proj" in k for k in missing):     # checkpoints antérieurs
            nn.init.zeros_(head.pos_proj.weight); nn.init.zeros_(head.pos_proj.bias)
        head.eval()
        tr = Transducer2(len(ck["itos"])).to(device)
        tr.load_state_dict(ck["vm"]); tr.eval()
        schema = json.loads((p / "field_schema.json").read_text(encoding="utf-8"))
        return cls(model, head, tr, ck["stoi"], ck["itos"], ck["space"], schema, device)

    # ---- encodage des chaînes du transducteur
    def _chars(self, s, n):
        return [self.stoi.get(c, UNK) for c in str(s)[:n]] or [UNK]

    def _pad(self, seqs, n):
        m = max(len(s) for s in seqs)
        return torch.tensor([s + [PAD] * (m - len(s)) for s in seqs],
                            device=self.dev)[:, :n]

    def _field_vec(self, label):
        """Encodage caractère du libellé, caché : identique à chaque appel."""
        if label not in self._fv:
            xf = self._pad([self._chars(label, MAXLAB)], MAXLAB)
            self._fv[label] = self.tr.encode_field(xf)
        return self._fv[label]

    @torch.no_grad()
    def _decode(self, enc, label, idx, extra):
        """Décodage glouton EN LOT pour un champ. -> (valeurs, log-probas)."""
        e, mask, pooled = enc
        idx = torch.as_tensor(idx, device=self.dev)
        e, mask, pooled = e[idx], mask[idx], pooled[idx]
        fv = self._field_vec(label).expand(pooled.shape[0], -1)
        h = self.tr.init_state(pooled, fv, extra[idx])
        tok = torch.full((e.shape[0],), BOS, device=self.dev)
        done = torch.zeros(e.shape[0], dtype=torch.bool, device=self.dev)
        outs, lp = [[] for _ in range(e.shape[0])], torch.zeros(e.shape[0], device=self.dev)
        for _ in range(MAXOUT + 1):
            lg, h = self.tr.step(self.tr.emb(tok), h, e, mask)
            logp = torch.log_softmax(lg, -1)
            tok = lg.argmax(-1)
            lp = lp + torch.where(done, torch.zeros_like(lp), logp.gather(-1, tok[:, None])[:, 0])
            for i, t in enumerate(tok.tolist()):
                if not done[i]:
                    if t == EOS:
                        done[i] = True
                    elif t > UNK:
                        outs[i].append(self.itos[t])
            if bool(done.all()):
                break
        vals = ["".join(o) for o in outs]
        # confiance PAR CARACTÈRE : sinon une valeur longue paraît toujours moins sûre
        # qu'une courte, et les deux ne seraient pas comparables entre champs.
        conf = [float(math.exp(l / max(len(v), 1))) for l, v in zip(lp.tolist(), vals)]
        return vals, lp.tolist(), conf

    @torch.no_grad()
    def _decode_many(self, enc, jobs, extra, chunk=2048):
        """Décodage glouton pour TOUS les champs en un seul lot.

        `jobs` = liste de (label, [indices de spans]). Le décodeur est indépendant ligne à
        ligne et les spans sont encodés une seule fois en amont : concaténer les lignes de
        tous les champs donne exactement les mêmes valeurs que les appels par champ, en
        remplaçant ~81 boucles gloutonnes par une seule. -> {label: (vals, lps, confs)}.
        """
        e, mask, pooled = enc
        rows_idx, rows_fv = [], []
        for label, idx in jobs:
            fv = self._field_vec(label)
            for j in idx:
                rows_idx.append(j)
            rows_fv.append(fv.expand(len(idx), -1))
        if not rows_idx:
            return {}
        idx = torch.as_tensor(rows_idx, device=self.dev)
        fv = torch.cat(rows_fv, 0)
        vals, lps, confs = [], [], []
        for a in range(0, idx.shape[0], chunk):
            b = slice(a, a + chunk)
            ec, mc, pc = e[idx[b]], mask[idx[b]], pooled[idx[b]]
            n = ec.shape[0]
            h = self.tr.init_state(pc, fv[b], extra[idx[b]])
            tok = torch.full((n,), BOS, device=self.dev)
            outs = [[] for _ in range(n)]
            lp_full = torch.zeros(n, device=self.dev)
            # Compaction : les lignes finissent à des longueurs très différentes ; on ne
            # fait chaque pas QUE sur les lignes actives (sinon tout le lot tourne
            # jusqu'à la plus longue, et le batché devient PLUS LENT que le par-champ).
            alive = torch.arange(n, device=self.dev)
            for _ in range(MAXOUT + 1):
                lg, h = self.tr.step(self.tr.emb(tok), h, ec, mc)
                logp = torch.log_softmax(lg, -1)
                tok = lg.argmax(-1)
                lp_full[alive] += logp.gather(-1, tok[:, None])[:, 0]
                fin = tok == EOS
                for i, t in zip(alive.tolist(), tok.tolist()):
                    if t != EOS and t > UNK:
                        outs[i].append(self.itos[t])
                if bool(fin.all()):
                    break
                if bool(fin.any()):
                    keep = (~fin).nonzero(as_tuple=True)[0]
                    alive, tok, h = alive[keep], tok[keep], h[:, keep]
                    ec, mc = ec[keep], mc[keep]
            v = ["".join(o) for o in outs]
            vals += v; lps += lp_full.tolist()
            confs += [float(math.exp(l / max(len(x), 1)))
                      for l, x in zip(lp_full.tolist(), v)]
        out, at = {}, 0
        for label, idx_f in jobs:
            n = len(idx_f)
            out[label] = (vals[at:at + n], lps[at:at + n], confs[at:at + n])
            at += n
        return out

    @torch.no_grad()
    def _options(self):
        """Vocabulaire encodé, une fois pour toutes. Les options sont des CHAÎNES : aucun
        paramètre par classe, et une classe jamais vue reste utilisable."""
        if self._opt is None:
            self._opt = {}
            for k in self.keys:
                cls = self.space[k].get("classes") or []
                if cls:
                    lab = self.schema[k]["label"]
                    self._opt[k] = encode_texts(
                        self.model, [f"{lab} : {c}" for c in cls], self.dev)
        return self._opt

    @torch.no_grad()
    def extract(self, text, M=256, topk=32, fill_p=0.5, max_chars=45000, autocast=False):
        """-> {champ: {value, span, start, end, confidence, normalization_confidence, source}}

        | clé                        | sens |
        |----------------------------|------|
        | `value`                    | la valeur canonique, ou `None` si le modèle s'abstient |
        | `span`                     | le span du document d'où sort la valeur (`None` si `source="vocabulary"`) |
        | `start`, `end`             | ses offsets CARACTÈRE dans `text` (`-1` si `source="vocabulary"`) |
        | `confidence`               | **la seule à comparer à un seuil** : masse agrégée de la valeur |
        | `normalization_confidence` | confiance de la normalisation span → valeur, par caractère |
        | `source`                   | `"text"` ou `"vocabulary"` |

        `source` répond à : **d'où vient la valeur.**
          `"text"`        d'un span du document ; `span`, `start`, `end` sont remplis. La
                          valeur passe par une normalisation qui peut la laisser inchangée
                          (« veuve » → `veuve`) ou la réécrire (« le 8 avril 2017 » →
                          `2017-04-15`).
          `"vocabulary"`  de l'ensemble des valeurs observées à l'entraînement pour ce champ,
                          sans span source (« vit seule dans un appartement à Nancy » →
                          `urbain`). `normalization_confidence` vaut alors 1.0, aucune
                          normalisation n'ayant eu lieu.

        `span`, les offsets et les deux confiances décrivent **le meilleur candidat, même
        quand le modèle s'abstient** : on peut donc ré-appliquer son propre seuil sans
        relancer le modèle. Seul `value` suit la décision du modèle.

        `fill_p=0.5` n'est pas un réglage : il sort de la matrice de coût de la tâche
        (une valeur fausse coûte 2, une abstention à tort coûte 1), indépendamment du
        taux de champs non documentés.

        `max_chars=45000` (2026-08) : l'ancien cap 24 000 saturait exactement les 8 192
        positions de l'encodeur (le schéma coûte ~2 280 tokens) et tronquait 39 % des
        dossiers. Au-delà, l'encodeur extrapole ses positions (RoPE) — mesuré : macro
        test 0.786 → 0.795, DATE +0.041 ; la troncature coûtait plus cher que
        l'extrapolation. `autocast=True` (GPU) : encodeur en bfloat16, ~×1,4 de plus,
        ~0,5 % des valeurs changent.
        """
        text = text[:max_chars]
        ents = {self.schema[k]["label"]: [] for k in self.keys}
        descs = {self.schema[k]["label"]: self.schema[k]["desc"] for k in self.keys}
        output = {"entities": ents, "entity_descriptions": descs}
        # collate_fn_INFERENCE : `collate_fn_train` applique l'échantillonneur
        # d'entraînement AU PROMPT (29 % des libellés remplacés par « entity N »).
        batch = self.model.processor.collate_fn_inference([(text, output)]).to(self.dev)
        # bf16 sur le SEUL encodeur (le gros du calcul) ; les têtes et le décodage
        # restent en fp32, où se joue la calibration des probabilités.
        import contextlib
        amp = (torch.autocast(device_type="cuda", dtype=torch.bfloat16)
               if autocast and str(self.dev).startswith("cuda") else contextlib.nullcontext())
        with amp:
            all_tok, all_sch = self.model._encode_batch(batch)
        all_tok = [t.float() for t in all_tok]
        mk = markers_of(all_sch[0]).float()
        l2i = {lab: i for i, lab in enumerate(ents.keys())}
        pool = build_pool(self.model, all_tok[0], text, mk, M=M)
        F = pool["S"].shape[0]
        E = mk[1:1 + F]
        cp, q, nl = self.head(E, pool)
        enc = self.tr.encode_span(self._pad(
            [self._chars(t, MAXSPAN) for t in pool["texts"]], MAXSPAN))
        sr = self.head.sr_to_h(pool["H"])
        Mn = pool["S"].shape[1]

        # Passe 1 — sélection par champ (probas + topk), AUCUN décodage.
        empty = {"value": None, "span": None, "start": -1, "end": -1,
                 "confidence": 0.0, "normalization_confidence": 0.0, "source": None}
        out, per_field, jobs = {}, {}, []
        for k in self.keys:
            fi = l2i.get(self.schema[k]["label"])
            if fi is None or fi >= F:
                out[k] = dict(empty); continue
            cls = self.space[k].get("classes") or []
            oe = self._options().get(k)
            parts = [cp[fi]] + ([oe @ q[fi]] if oe is not None and cls else []) + [nl[fi]]
            p = torch.softmax(torch.cat(parts), 0)
            sel = torch.topk(p[:Mn], min(topk, Mn)).indices
            per_field[k] = (p, sel, cls, oe)
            jobs.append((self.schema[k]["label"], sel.tolist()))

        # Passe 2 — UN décodage glouton batché pour tous les champs.
        decoded = self._decode_many(enc, jobs, sr)

        # Passe 3 — agrégation par valeur, inchangée.
        for k, (p, sel, cls, oe) in per_field.items():
            vals, _, cval = decoded[self.schema[k]["label"]]

            # On agrège par VALEUR, pas par option : une même date apparaît dans plusieurs
            # spans, et un argmax sur les options diviserait sa masse entre eux.
            # `src` retient le span le PLUS responsable de chaque valeur, pour pouvoir
            # rendre un offset.
            mass, src = {}, {}
            for j, v, cv in zip(sel.tolist(), vals, cval):
                if not v:
                    continue
                w = float(p[j]) * cv
                mass[v] = mass.get(v, 0.0) + w
                if w > src.get(v, (0.0,))[0]:
                    src[v] = (w, j, cv)
            for oi, c in enumerate(cls) if oe is not None else ():
                w = float(p[Mn + oi])
                mass[c] = mass.get(c, 0.0) + w
                if w > src.get(c, (0.0,))[0]:
                    src[c] = (w, -1, 1.0)     # vocabulaire : aucun span source

            if not mass:
                out[k] = dict(empty); continue
            v, pv = max(mass.items(), key=lambda kv: kv[1])
            _, j, cv = src[v]
            if j >= 0:
                _, _, cs, ce = pool["spans"][j]
                span, source = text[cs:ce], "text"
            else:
                cs = ce = -1
                span, source = None, "vocabulary"
            out[k] = {"value": v if pv > fill_p else None, "span": span,
                      "start": int(cs), "end": int(ce),
                      "confidence": float(pv), "normalization_confidence": float(cv),
                      "source": source}
        return out

    def extract_values(self, text, **kw):
        """Raccourci : -> {champ: valeur ou None}, sans les offsets ni les confiances."""
        return {k: v["value"] for k, v in self.extract(text, **kw).items()}
