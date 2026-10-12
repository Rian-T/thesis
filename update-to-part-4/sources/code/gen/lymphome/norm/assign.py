"""Étape 2 — tête d'affectation + loss à variable latente (DESIGN_V2 §3).

On garde la matrice `S = [F champs x M spans]` que GLiNER calcule déjà, au lieu de la réduire
à 12 cases par ligne. Chaque champ choisit dans UNE distribution :

    O_f  =  { M spans du document }  ∪  { vocabulaire observé de f }  ∪  { ⊥ }
              bloc COPIE (partagé)      bloc VOCAB (chaînes encodées)   abstention

et la supervision ne porte QUE sur la valeur finale, le span restant latent :

    L_f  =  − log [ Σ_m P_A(copie_m | f) · P_B(cible | span_m, f)
                    + P_A(vocab_cible | f)          si la cible est dans le vocabulaire
                    + P_A(⊥ | f)                    si le champ n'est pas documenté ]

C'est le cœur : un span d'en-tête que l'annotateur n'a jamais pointé reçoit de la masse dès
que le transducteur sait en tirer la bonne valeur, et le gradient remonte son affectation.

Invariant : ZÉRO paramètre par champ et par classe. Le champ n'entre que par son marqueur de
type GLiNER (dérivé de son libellé, en texte) et les options de vocabulaire ne sont que des
chaînes encodées. Les mêmes poids valent pour un autre schéma, une autre langue, une classe
jamais vue.

Ce module ne dépend PAS de `taxonomy.py` : l'espace de valeurs est dérivé des données
(`label_space.py`). `gliner2/*` reste intact.
"""
import json
import sys
from pathlib import Path

import torch
import torch.nn as nn

_H = Path(__file__).resolve().parent
sys.path.insert(0, str(_H))
sys.path.insert(0, str(_H / "transducer"))
import gliner_integrated as G          # noqa: E402
import label_space as LS               # noqa: E402
import taxonomy as T                   # noqa: E402
from labels import LABELS              # noqa: E402
from train_transducer import BOS, EOS, MAXOUT, pad   # noqa: E402
from train_transducer2 import MAXLAB, MAXSPAN, Transducer2   # noqa: E402

D = 768
KEY2LABEL = {k: v["label"] for k, v in LABELS.items()}


# ------------------------------------------------------------------ pool de spans
def build_pool(model, token_emb, text, markers, M=256, crit="rank"):
    """Élague le document à M spans par un critère INDÉPENDANT DU CHAMP.

    `max_f S[f, span]` et non un top-k par champ : un top-k par champ réintroduirait
    exactement le goulot qu'on supprime (chaque champ ne verrait que ce que la détection
    lui destine déjà, et aucun champ ne pourrait récupérer un span destiné à un autre).

    ⚠️ Le CHOIX des M spans est un `topk`, non différentiable, et se fait donc sur des
    scores détachés — mais `H` et `S` retournés doivent rester DANS le graphe, sinon
    l'encodeur ne reçoit aucun gradient de la tête d'affectation et on n'entraînerait
    que les têtes. Ne pas remettre de `@torch.no_grad` sur cette fonction.
    """
    span_rep = model.compute_span_rep(token_emb)["span_rep"]        # [L,W,d]
    L, W = span_rep.shape[0], span_rep.shape[1]
    dsc = G.detection_scores(model, span_rep, markers)              # [F,L,W]
    woff = G.word_offsets(model, text)
    Lw = min(L, len(woff))
    flat = dsc[:, :Lw].reshape(dsc.shape[0], -1)                    # [F, Lw*W]
    with torch.no_grad():                                           # la sélection seule
        d = flat.detach()
        if crit == "max":
            key = d.max(0).values
        else:
            # Par RANG : les scores bruts de deux champs ne sont pas à la même échelle, donc
            # `max_f` laisse les champs bruyants monopoliser le pool. Mesuré sur DATE : à 256
            # spans le rang obtient 0.758 contre 0.613 pour `max_f` (et les deux convergent
            # vers 0.82 à 1024) — même plafond, mais atteint avec ~3x moins de spans.
            rank = torch.empty_like(d)
            order = d.argsort(dim=1, descending=True)
            rank.scatter_(1, order, torch.arange(d.shape[1], device=d.device,
                                                 dtype=d.dtype).expand_as(d))
            key = -rank.min(0).values
        idx = torch.topk(key, min(M, flat.shape[1])).indices
    spans, keep = [], []
    for j, ix in enumerate(idx.tolist()):
        i, w = ix // W, ix % W
        cs, ce = woff[i][0], woff[min(i + w, len(woff) - 1)][1]
        if ce <= cs:
            continue
        spans.append((i, w, cs, ce)); keep.append(ix)
    keep = torch.tensor(keep, device=span_rep.device)
    # Features d'ORDRE. Rien dans la tête ne savait où un span se trouve dans le document,
    # alors que « date de dernière nouvelle » = la plus tardive et « date de 1re ligne » = le
    # premier en-tête de traitement : ce sont des prédicats sur un RANG. Le résumé sum-poolé
    # détruit l'ordre par construction, donc ces champs n'étaient pas mal appris, ils étaient
    # INEXPRIMABLES. Trois scalaires génériques, aucun paramètre par champ, aucun hardcode :
    # position relative dans le texte, rang relatif du mot, largeur relative du span.
    nT = max(len(text), 1)
    pos = torch.tensor([[cs / nT, i / max(Lw - 1, 1), w / max(W - 1, 1)]
                        for i, w, cs, ce in spans], device=span_rep.device, dtype=span_rep.dtype)
    return {"H": span_rep[:Lw].reshape(-1, span_rep.shape[-1])[keep],   # [M,d]
            "S": flat[:, keep],                                         # [F,M]
            "pos": pos,                                                 # [M,3]
            "spans": spans, "texts": [text[cs:ce] for _, _, cs, ce in spans]}


# ------------------------------------------------------------------ tête A
class AssignHead(nn.Module):
    """P(option | champ) sur COPIE ∪ VOCAB ∪ ⊥. ~1.4 M paramètres, aucun par champ."""

    def __init__(self, d=D, h=256, ctx="attn", beta0=False):
        # ctx="sonly" : aucun MLP sur la route COPIE, le score est S. C'est la
        # conclusion logique du contrôle d'ancrage — si elle égale le reste, la
        # tête d'affectation disparaît et il ne reste que VOCAB et l'abstention.
        super().__init__()
        self.ctx = ctx
        self.f_proj = nn.Linear(d, h)
        self.s_proj = nn.Linear(d, h)
        self.o_proj = nn.Linear(h, 1)
        # Le score de copie était STRICTEMENT PONCTUEL : il ne dépendait que du couple
        # (champ, span), jamais des autres spans du document. Or « la date de 2e ligne » est
        # intrinsèquement relationnelle — il faut savoir ce que sont les AUTRES dates pour
        # établir un rang. Aucun gradient ne fait émerger un rang depuis un score ponctuel.
        #   ctx=none : l'ancien comportement (pour l'ablation) ;
        #   ctx=sum  : le résumé sum-poolé du document entre dans le score de copie ;
        #   ctx=attn : la requête-champ attend sur le pool avant de pointer — la formulation
        #              standard d'un pointer network. Zéro paramètre par champ.
        # NB : ce qui a été réfuté avec alpha n'est PAS « les champs doivent interagir », mais
        # la forme la plus faible imaginable d'interaction (un scalaire global sur un
        # log-softmax de l'axe des champs). La question reste ouverte, d'où cette variante.
        self.c_proj = nn.Linear(d, h) if ctx == "sum" else None
        if ctx == "attn":
            self.q_proj = nn.Linear(d, h)
            self.k_proj = nn.Linear(d, h)
            self.v_proj = nn.Linear(d, h)
            self.a_proj = nn.Linear(h, h)
        self.summ = nn.Linear(d, d)
        self.vocab = nn.Sequential(nn.Linear(2 * d, h), nn.GELU(), nn.Linear(h, d))
        self.nul = nn.Sequential(nn.Linear(2 * d, h), nn.GELU(), nn.Linear(h, 1))
        # beta : poids du score de détection natif. Init 1 = on démarre sur le classement
        # du détecteur, la tête peut ensuite s'en écarter (c'est tout l'objet).
        # beta0=True -> init 0. Avec beta=1 la tête DÉMARRE littéralement comme le score de
        # détection : mesurer ensuite qu'elle « ne classe pas mieux que la détection »
        # revient à mesurer de combien elle a bougé depuis son initialisation. On lui
        # laisse la possibilité de ne pas partir de là.
        self.beta = nn.Parameter(torch.zeros(1) if beta0 else torch.ones(1))
        self.pos_proj = nn.Linear(3, h)
        # alpha : force de la compétition entre CHAMPS. Init 0 = pas de compétition.
        # « un span sert au plus un champ » est FAUX 20,4 % du temps (news_date_of_last_news
        # et news_date_of_last_visit partagent la date 214 fois) : la contrainte doit donc
        # être apprise, jamais imposée.
        self.alpha = nn.Parameter(torch.zeros(1))
        # tau : calibration de log P_B avant de l'additionner à log P_A. Les deux routes ne
        # sont pas à la même échelle — P_A(vocab) est ATOMIQUE, P_A(copie)·P_B est un produit
        # sur ~10 caractères. Sans calibration, la route COPIE est pénalisée par un artefact
        # de paramétrisation et non par les données, et le modèle se rabat sur VOCAB (13 % des
        # cibles DATE de test sont littéralement dans le vocabulaire du train : le rappel du
        # pool resterait plat pendant que le macro-F1 monterait).
        self.tau = nn.Parameter(torch.ones(1))
        # Apport de span_rep à l'état initial du décodeur de la tête B. INITIALISÉ À ZÉRO :
        # au démarrage à chaud, B se comporte exactement comme le checkpoint de l'étape 1.
        # C'est le seul chemin par lequel la route COPIE fait remonter du gradient dans
        # l'encodeur GLiNER (sinon B ne lit que des caractères et l'encodeur ne reçoit de
        # cette route qu'une responsabilité scalaire via A — signal de type EM, très faible).
        self.sr_to_h = nn.Linear(d, 256)
        nn.init.zeros_(self.sr_to_h.weight); nn.init.zeros_(self.sr_to_h.bias)

    def doc_summary(self, S, H):
        """z_f = Σ_m σ(S[f,m]) · h_m — SOMME et non moyenne : la norme croît avec le nombre
        de spans détectés, donc le comptage devient représentable sans tête dédiée."""
        return self.summ(torch.sigmoid(S) @ H)                       # [F,d]

    def field_context(self, E, H, S, z):
        """[F,h] : ce que le champ retient du RESTE du pool avant de pointer."""
        if self.ctx == "sum":
            return self.c_proj(z)
        q, k, v = self.q_proj(E), self.k_proj(H), self.v_proj(H)          # [F,h] [M,h] [M,h]
        att = torch.softmax(q @ k.t() / (q.shape[-1] ** 0.5), dim=-1)     # [F,M]
        return self.a_proj(att @ v)

    def forward(self, E, pool):
        """E [F,d] marqueurs de type -> (copie [F,M], requête vocab [F,d], ⊥ [F,1])."""
        H, S = pool["H"], pool["S"]
        z = self.doc_summary(S, H)
        if self.ctx == "sonly":
            # LE SCORE DE COPIE EST `S` LUI-MÊME. Mesuré : sur le meilleur modèle, le
            # classement de la tête est à -0.000 de celui de la détection brute, et la tête
            # privée de son ancrage tombe à 0.187. Son MLP n'apporte donc rien du tout —
            # il ne fait que laisser passer S. On le supprime et on teste l'égalité.
            base = torch.zeros_like(S)
        else:
            u = (self.f_proj(E).unsqueeze(1) + self.s_proj(H).unsqueeze(0)
                 + self.pos_proj(pool["pos"]).unsqueeze(0))               # [F,M,h]
            if self.ctx != "none":
                u = u + self.field_context(E, H, S, z).unsqueeze(1)
            base = self.o_proj(torch.tanh(u)).squeeze(-1)                 # [F,M]
        comp = torch.log_softmax(S, dim=0)          # axe des CHAMPS : quel champ pour ce span
        cp = base + self.beta * S + self.alpha * comp
        fz = torch.cat([E, z], dim=-1)
        return cp, self.vocab(fz), self.nul(fz)


# ------------------------------------------------------------------ tête B, en lot par document
class ValueModel:
    """Le transducteur de l'étape 1, sous sa forme intégrable (conditionnement au décodeur).

    Encode les M spans du document UNE fois, puis décode chaque champ dessus : c'est ce qui
    rend la vraisemblance marginale calculable (sinon M x F encodages par document).
    """

    def __init__(self, ckpt, dev, train=True):
        ck = torch.load(ckpt, map_location=dev)
        self.stoi, self.itos = ck["stoi"], ck["itos"]
        self.m = Transducer2(len(self.itos)).to(dev)
        self.m.load_state_dict(ck["model"])
        self.m.train(train)
        self.dev = dev

    def parameters(self):
        return self.m.parameters()

    def _chars(self, s, n):
        return [self.stoi.get(c, 3) for c in str(s)[:n]] or [3]

    def encode_spans(self, texts):
        x = pad([self._chars(t, MAXSPAN) for t in texts], MAXSPAN).to(self.dev)
        return self.m.encode_span(x)                                  # e, mask, pooled

    def field_state(self, enc, label, extra=None):
        e, mask, pooled = enc
        xf = pad([self._chars(label, MAXLAB)], MAXLAB).to(self.dev)
        fv = self.m.encode_field(xf).expand(pooled.shape[0], -1)
        return self.m.init_state(pooled, fv, extra)

    def logprob(self, enc, label, value, extra=None, idx=None, key=None):
        """log P(valeur | span_m, champ). -> [len(idx)] (ou [M] si idx est None).

        `idx` restreint le calcul à un sous-ensemble de spans : c'est ce qui rend le coût
        INDÉPENDANT de la taille du pool. La tête A voit les M spans (simple produit
        matriciel, gratuit) ; seul le transducteur est restreint.
        """
        e, mask, pooled = enc
        if idx is not None:
            e, mask, pooled = e[idx], mask[idx], pooled[idx]
            extra = None if extra is None else extra[idx]
        h = self.field_state((e, mask, pooled), label, extra)
        y = pad([[BOS] + self._chars(value, MAXOUT) + [EOS]], MAXOUT + 2).to(self.dev)
        return self.m.logprob(e, mask, h, y.expand(e.shape[0], -1).contiguous())

    @torch.no_grad()
    def greedy_many(self, enc, label, idx, extra=None, key=None):
        """Décode PLUSIEURS spans en un seul lot. -> [str] alignées sur `idx`.

        `greedy_one` décode à batch 1 : à 32-96 spans par champ et ~26 champs par document,
        cela fait des dizaines de milliers de pas de GRU séquentiels. Ici les spans d'un même
        champ partagent le lot, et seul le nombre de pas de décodage reste séquentiel.
        """
        e, mask, pooled = enc
        idx = torch.as_tensor(idx, device=self.dev)
        e, mask, pooled = e[idx], mask[idx], pooled[idx]
        h = self.field_state((e, mask, pooled), label,
                             None if extra is None else extra[idx])
        n = e.shape[0]
        tok = torch.full((n,), BOS, device=self.dev)
        done = torch.zeros(n, dtype=torch.bool, device=self.dev)
        outs = [[] for _ in range(n)]
        for _ in range(MAXOUT + 1):
            lg, h = self.m.step(self.m.emb(tok), h, e, mask)
            tok = lg.argmax(-1)
            for i, t in enumerate(tok.tolist()):
                if not done[i]:
                    if t == EOS:
                        done[i] = True
                    elif t > 3:
                        outs[i].append(self.itos[t])
            if bool(done.all()):
                break
        return ["".join(o) for o in outs]

    @torch.no_grad()
    def greedy_scored(self, enc, label, idx, extra=None, key=None):
        """Comme `greedy_many`, mais rend aussi log P_B(chaîne décodée | span, champ).

        L'entraînement optimise `Σ_m P_A(m)·P_B(valeur|m)` ; l'inférence n'utilisait que
        `P_A(m)` et JETAIT la confiance du transducteur. Un span bien affecté dont la
        transduction est une bouillie pesait donc autant qu'un span dont B est certain.
        C'est une incohérence entraînement/inférence, et elle frappe là où il manque
        justement du signal : la qualité de p_v comme confiance, donc la décision de
        remplir. On rend ici l'estimateur cohérent au premier ordre.
        """
        vals = self.greedy_many(enc, label, idx, extra, key)
        lp = []
        for v, i in zip(vals, (idx.tolist() if torch.is_tensor(idx) else list(idx))):
            if not v:
                lp.append(float("-inf")); continue
            lp.append(float(self.logprob(enc, label, v, extra,
                                         torch.as_tensor([i], device=self.dev), key)[0]))
        return vals, lp

    @torch.no_grad()
    def greedy_one(self, enc, label, m, extra=None):
        e, mask, pooled = enc
        sub = (e[m:m + 1], mask[m:m + 1], pooled[m:m + 1])
        h = self.field_state(sub, label, None if extra is None else extra[m:m + 1])
        tok = torch.full((1,), BOS, device=self.dev)
        out = []
        for _ in range(MAXOUT + 1):
            lg, h = self.m.step(self.m.emb(tok), h, sub[0], sub[1])
            tok = lg.argmax(-1)
            t = int(tok)
            if t == EOS:
                break
            if t > 3:
                out.append(self.itos[t])
        return "".join(out)


# ------------------------------------------------------------------ espace de valeurs (données)
def build_value_space(prod_path, train_ids, fields):
    """Espace dérivé du SEUL train. VOCAB non vide uniquement pour les champs fermés."""
    space, index = LS.build(prod_path, fields, train_ids)
    return space, index


def canon(space, index, key, raw):
    v = LS.to_canon(space, index, key, raw)
    return None if v is None else str(v)


def build_dataset_assign(gold_path, prod_path, space, index, fields, cap=24000):
    """Comme `G.build_dataset`, mais les cibles viennent de l'espace DÉRIVÉ, pas de taxonomy.

    `taxonomy` ne sert plus qu'à énumérer les champs et à porter la famille utilisée par le
    barème d'évaluation — plus aucune règle de normalisation écrite à la main n'intervient.
    """
    tgt = {}
    for line in open(prod_path, encoding="utf-8"):
        r = json.loads(line); rid = f"lym_{r['sample_index']}"
        ann = r.get("annotation") or {}
        d = {}
        for k in fields:
            v = ann.get(k)
            if v is None:
                continue
            for it in ([v] if isinstance(v, dict) else v):
                if isinstance(it, dict) and it.get("value") not in (None, ""):
                    c = canon(space, index, k, it["value"])
                    if c is not None:
                        d[k] = c; break
        tgt[rid] = d

    out = []
    for line in open(gold_path, encoding="utf-8"):
        r = json.loads(line); did = r["id"]; text = r["text"][:cap]
        ents, descs, entries = {}, {}, []
        for k, spans in r["gold"].items():
            if k not in KEY2LABEL:
                continue
            ms = [text[int(s):int(e)] for s, e, _ in spans
                  if int(e) <= len(text) and text[int(s):int(e)].strip()]
            if ms:
                ents[KEY2LABEL[k]] = ms
        for k in fields:
            lab = KEY2LABEL[k]
            ents.setdefault(lab, [])
            descs[lab] = LABELS[k]["desc"]
            entries.append({"key": k, "label": lab, "target": tgt.get(did, {}).get(k),
                            "spans": [(int(a), int(b)) for a, b, _ in r["gold"].get(k, [])
                                      if int(b) <= len(text)][:8]})
        out.append({"id": did, "text": text,
                    "output": {"entities": ents, "entity_descriptions": descs},
                    "entries": entries})
    return out


@torch.no_grad()
def encode_options(model, space, dev):
    """{champ: embeddings [n_f, d]} — les options sont des CHAÎNES encodées, zéro paramètre."""
    out = {}
    for k, s in space.items():
        if not s["classes"] or k not in KEY2LABEL:
            continue
        out[k] = G.encode_texts(model, [f"{KEY2LABEL[k]} : {c}" for c in s["classes"]], dev)
    return out


# ------------------------------------------------------------------ loss
def assign_loss_doc(head, vm, E, pool, entries, opt_emb, space, dev, topk=32, nsample=8,
                    guided=True, max_hint=8, hard_assign=False):
    """Une seule loss pour tout le document. -> (loss, n_champs).

    La somme marginale sur les spans est TRONQUÉE aux `topk` meilleurs selon P_A, plus
    `nsample` spans tirés UNIFORMÉMENT. Deux raisons, distinctes :

    - le coût. Le transducteur est le poste dominant et croît en M ; en tronquant, il devient
      indépendant de la taille du pool. On peut donc prendre M=1024 (rappel DATE 0.82) sans
      payer 13 h par epoch.
    - le biais. Élaguer DUR une variable latente biaise la marginale : un span jamais dans le
      top-k ne recevrait jamais de gradient et ne pourrait jamais y entrer. Les `nsample`
      tirages uniformes restaurent le support. C'est de l'échantillonnage de latente.

    Les spans hors sous-ensemble contribuent implicitement 0 à la marginale — c'est
    l'approximation assumée, et elle est d'autant plus serrée que P_A est concentrée.
    """
    cp, q, nl = head(E, pool)
    enc = vm.encode_spans(pool["texts"])
    sr = head.sr_to_h(pool["H"])                 # gradient de la tête B -> encodeur GLiNER
    ntxt = [LS.normkey(t) for t in pool["texts"]] if guided else None
    loss = torch.zeros((), device=dev); n = 0
    for e in entries:
        fi = e["fi"]
        classes = space.get(e["key"], {}).get("classes") or []
        oe = opt_emb.get(e["key"])
        parts = [cp[fi]]
        if oe is not None and len(classes):
            parts.append(oe @ q[fi])
        parts.append(nl[fi])
        logp = torch.log_softmax(torch.cat(parts), dim=0)
        M = cp.shape[1]
        if e["target"] is None:
            loss = loss - logp[-1]; n += 1
            continue
        hint = None
        if guided and ntxt is not None:
            nt = LS.normkey(e["target"])
            if nt:
                h = [i for i, t in enumerate(ntxt) if nt in t][:max_hint]
                if h:
                    hint = torch.tensor(h)
        with torch.no_grad():
            sel = torch.topk(logp[:M].detach(), min(topk, M)).indices
            if nsample:
                sel = torch.unique(torch.cat([
                    sel, torch.randint(M, (min(nsample, M),), device=dev)]))
            # PROPOSITION GUIDÉE PAR LA CIBLE (entraînement uniquement).
            # `sel = topk(P_A)` seul est une boucle de rétroaction positive : les spans qui
            # reçoivent du gradient sont ceux que A préfère déjà, or A démarre égale au
            # détecteur — donc le détecteur choisit qui apprend, et se renforce. Ce n'est pas
            # « une epoch ne suffit pas », c'est une boucle qui EMPÊCHE de converger ailleurs.
            # Les tirages uniformes sont censés la casser mais n'en ont pas le débit (moins
            # d'un passage par span sur tout l'entraînement).
            # Ici, les spans dont le TEXTE porte déjà la cible entrent d'office dans le
            # support : c'est du hard-EM, une proposition guidée par la postérieure, et c'est
            # la seule façon pour un span d'en-tête jamais annoté d'y entrer un jour.
            # Uniquement à l'entraînement : aucune information de cible ne circule à l'éval.
            if hint is not None and len(hint):
                sel = torch.unique(torch.cat([sel, hint.to(dev)]))
        lpb = vm.logprob(enc, e["label"], e["target"], sr, sel, e["key"])
        if bool((lpb > -1e8).sum() == 0) and not (oe is not None and e["target"] in classes):
            continue          # aucun span ne peut produire la cible : rien à apprendre ici
        if hard_assign:
            # ABLATION DU CŒUR DU DESIGN : au lieu de sommer sur TOUS les spans du support
            # (vraisemblance marginale, span latent), on ne garde que le MEILLEUR — celui qui
            # maximise P_A(span)·P_B(cible|span) — et on le supervise seul. C'est du hard-EM,
            # une affectation DURE, l'alternative simple à la variable latente.
            #
            # C'est l'ablation qui manquait : on a retiré neuf pièces AUTOUR d'un mécanisme
            # central jamais comparé à son alternative triviale. Si l'affectation dure fait
            # aussi bien, la marginale sort elle aussi, et le design se réduit encore.
            j = int((logp[sel] + head.tau * lpb).argmax())
            terms = [(logp[sel] + head.tau * lpb)[j].view(1)]
        else:
            terms = [logp[sel] + head.tau * lpb]
        if oe is not None and e["target"] in classes:
            terms.append(logp[M + classes.index(e["target"])].view(1))
        loss = loss - torch.logsumexp(torch.cat(terms), dim=0); n += 1
    return loss, n


@torch.no_grad()
def assign_predict_doc(head, vm, E, pool, entries, opt_emb, space, dev, topk=32, fill_p=0.5):
    """Inférence COHÉRENTE avec l'entraînement : on somme sur les VALEURS, pas sur les options.

    Plusieurs spans transduisent vers la même valeur (une date d'en-tête réapparaît dans 3 à 8
    spans du pool). Un argmax sur les options diviserait la masse de cette valeur entre ses
    spans et la ferait perdre contre une option VOCAB atomique — c'est-à-dire pénaliser
    précisément la valeur la mieux attestée. On agrège donc par chaîne canonique.

    Décision de remplir : la matrice de coût (valeur fausse = fp + fn = 2, abstention à tort
    = 1) donne coût(remplir v) = 2 − q0 − 2·p_v et coût(s'abstenir) = 1 − q0. D'où
    REMPLIR SSI p_v > 0.5, indépendamment de q0 = P(champ non documenté) : aucun seuil à
    calibrer, et ⊥ n'entre pas dans l'argmax puisque c'est une décision, pas une classe.
    (Exact pour un coût additif ; le macro-F1 par famille ne l'est pas, donc 0.5 est l'ordre 1
    — d'où le paramètre, laissé inspectable plutôt que réglé en douce.)

    `topk` borne le nombre de spans transduits : une valeur éparpillée sur beaucoup de spans
    à faible masse est donc sous-estimée. C'est le seul biais assumé de cette inférence.
    """
    cp, q, nl = head(E, pool)
    enc = vm.encode_spans(pool["texts"])
    sr = head.sr_to_h(pool["H"])
    M = cp.shape[1]
    out = {}
    for e in entries:
        fi = e["fi"]
        classes = space.get(e["key"], {}).get("classes") or []
        oe = opt_emb.get(e["key"])
        parts = [cp[fi]] + ([oe @ q[fi]] if oe is not None and classes else []) + [nl[fi]]
        p = torch.softmax(torch.cat(parts), 0)
        mass = {}
        sel = torch.topk(p[:M], min(topk, M)).indices
        vals, lpb = vm.greedy_scored(enc, e["label"], sel, sr, e["key"])
        import math
        for j, v, l in zip(sel.tolist(), vals, lpb):
            if v:
                # P_A(m) x P_B(v|m) — le même produit qu'à l'entraînement, et non P_A seul
                mass[v] = mass.get(v, 0.0) + float(p[j]) * math.exp(min(l, 0.0))
        if oe is not None:
            for oi, c in enumerate(classes):
                mass[c] = mass.get(c, 0.0) + float(p[M + oi])
        if not mass:
            out[e["key"]] = None
            continue
        v, pv = max(mass.items(), key=lambda kv: kv[1])
        out[e["key"]] = v if pv > fill_p else None
    return out


# ------------------------------------------------------------------ ablation de la tête B
class HardValueModel:
    """Ablation : `P_B` remplacé par le parseur écrit à la main (`taxonomy.py`), en 0/1.

    Elle répond à la question « le seq2seq appris sert-il vraiment, bout en bout ? ». Ici la
    marginale se réduit à `− log Σ_{m : parse(m) = cible} P_A(m)` : le crédit est réparti
    uniformément entre les spans qui parsent JUSTE, et rien n'est appris de la conversion.

    Même interface que ValueModel, donc rigoureusement le même reste de code.
    """

    def __init__(self, dev):
        self.dev = dev
        self.m = nn.Identity()

    def parameters(self):
        return []

    def encode_spans(self, texts):
        return texts                                  # aucun encodage : on garde le texte brut

    def _parse(self, key, t):
        try:
            return T.normalize_target(key, t)
        except Exception:
            return None

    def logprob(self, enc, label, value, extra=None, idx=None, key=None):
        txt = enc if idx is None else [enc[int(i)] for i in idx]
        ok = [G._match(T.FIELD_SPEC[key]["family"], self._parse(key, t), value) for t in txt]
        return torch.tensor([0.0 if o else -1e9 for o in ok], device=self.dev)

    def greedy_many(self, enc, label, idx, extra=None, key=None):
        txt = [enc[int(i)] for i in idx]
        return [self._parse(key, t) or "" for t in txt]


def load_head(ck, dev):
    """Charge une tête A depuis un checkpoint, y compris ANTÉRIEUR aux features d'ordre.

    `pos_proj` a été ajouté après coup. Un checkpoint d'avant ne le contient pas : le charger
    en `strict=False` laisserait la couche INITIALISÉE AU HASARD, donc ajouterait un terme
    aléatoire au score de copie et corromprait silencieusement un modèle déjà évalué. On la met
    à zéro, ce qui reproduit exactement le comportement sous lequel ce checkpoint a été
    entraîné et mesuré.
    """
    # dimension d'encodeur INFÉRÉE du checkpoint (768 base, 1024 large) : aucun flag à
    # passer, un vieux checkpoint reste chargeable tel quel.
    d = ck["head"]["f_proj.weight"].shape[1]
    head = AssignHead(d=d, ctx=ck.get("ctx", "none"), beta0=ck.get("beta0", False)).to(dev)
    missing, _ = head.load_state_dict(ck["head"], strict=False)
    if any("pos_proj" in k for k in missing):
        nn.init.zeros_(head.pos_proj.weight); nn.init.zeros_(head.pos_proj.bias)
    return head.eval()
