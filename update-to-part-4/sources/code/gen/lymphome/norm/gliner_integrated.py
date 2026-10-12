"""
GLiNER + têtes de normalisation INTÉGRÉES — un seul modèle, finetune end-to-end SANS freeze.

Le modèle GLiNER (Extractor) est chargé, on lui ATTACHE des couches trainables (NormHeads) et on
finetune TOUT ensemble (encodeur + span_rep + têtes) sur lymphome. Un forward :
  - DÉTECTION : loss native GLiNER (_compute_sample_loss : structure/cls/count).
  - NORMALISATION : sur le MÊME encodage, span_rep natif des spans gold → têtes → valeur canon.
À l'inférence : le modèle détecte (natif) ET normalise (têtes) en un forward.

Têtes (portées sur hidden=768 GLiNER) :
  CAT  -> classification (similarité MLP(h_span_poolé)·emb(option))
  NUM/ORD/DATE -> sélection de span (score par span -> argmax -> parse exact)

Alignement : on n'utilise PAS l'ordre de schéma du batch. Par doc on connaît nos champs
(gold char-spans + cible canon via taxonomy). h_i = span_rep[word_i,width] (mapping char->mot via
model.processor). e_f/options = encodés par l'encodeur GLiNER (grad flow).
`gliner2/*` INTACT (règle #1) : on sous-classe/attache, on ne modifie rien.
"""
import json
import os as _os
import sys
from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parents[2]
sys.path.insert(0, str(_REPO / "GLiNER2"))
sys.path.insert(0, str(_REPO / "GLiNER2" / "v3"))
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parent))
import taxonomy as T          # noqa: E402
from labels import LABELS     # noqa: E402

KEY2LABEL = {k: v["label"] for k, v in LABELS.items()}
LABEL2DESC = {v["label"]: v["desc"] for v in LABELS.values()}
D = 768
NULL_LABEL = "champ non documenté"    # option/slot d'abstention des têtes


def cat_options(key, with_null=True):
    """Options d'un champ CAT, abstention comprise (une chaîne de plus, zéro paramètre)."""
    o = list(T.FIELD_SPEC[key]["classes"].keys())
    return o + [NULL_LABEL] if with_null else o
MAX_CHARS = 9000              # cap docs (mémoire/OOM) — texte + spans + mapping cohérents


def build_dataset(gold_path, prod_path, cap=MAX_CHARS):
    """Source unique id-alignée. -> list {id, text, output(GLiNER), entries(norm)}."""
    tgt = {}
    for line in open(prod_path, encoding="utf-8"):
        r = json.loads(line); rid = f"lym_{r['sample_index']}"; ann = r.get("annotation") or {}
        d = {}
        for k in T.FIELDS:
            v = ann.get(k)
            if v is None:
                continue
            v = [v] if isinstance(v, dict) else v
            for it in v:
                if isinstance(it, dict) and it.get("value") not in (None, ""):
                    c = T.normalize_target(k, it["value"])
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
            lab = KEY2LABEL[k]
            ms = [text[int(s):int(e)] for s, e, _ in spans if int(e) <= len(text) and text[int(s):int(e)].strip()]
            if ms:
                ents[lab] = ms; descs[lab] = LABELS[k]["desc"]
            pass   # les entries sont construites ci-dessous pour TOUS les champs
        # SCHÉMA COMPLET : tous les champs non-TXT (absents -> [] = négatifs) pour que
        # l'entraînement matche l'éval 89-champs (sinon fuite de présence + role-binding facilité).
        for k in T.FIELDS:
            fam = T.FIELD_SPEC[k]["family"]
            if fam == "TXT":
                continue
            lab = KEY2LABEL[k]
            if lab not in ents:
                ents[lab] = []
            descs[lab] = LABELS[k]["desc"]
            # UNE entry par champ non-TXT, y compris ABSENT (cible None = NULL). Sans ça les
            # têtes ne voient que des positifs (26 champs sur 81) et ne peuvent pas apprendre
            # à s'abstenir — la décision de remplir était sous-traitée à un seuil non calibré.
            tv = tgt.get(did, {}).get(k)
            entries.append({"key": k, "label": lab, "family": fam, "target": tv,
                            "options": cat_options(k) if fam == "CAT" else None,
                            "spans": [(int(a), int(b)) for a, b, _ in r["gold"].get(k, [])
                                      if int(b) <= len(text)][:8]})
        if entries:
            out.append({"id": did, "text": text,
                        "output": {"entities": ents, "entity_descriptions": descs}, "entries": entries})
    return out


# ============================================================ têtes
class NormHeads(nn.Module):
    needs_ctx = False          # cette tête n'utilise pas le contexte local des candidats
    use_conf = False           # biais de confiance-détection (cf. sel_scores)

    def __init__(self, d=D, h=256):
        super().__init__()
        self.cat_proj = nn.Sequential(nn.Linear(d, h), nn.GELU(), nn.Linear(h, d))
        self.sel_f = nn.Linear(d, h)
        self.sel_s = nn.Linear(d, h)
        self.sel_o = nn.Linear(h, 1)
        self.sel_c = nn.Parameter(torch.tensor(0.5))

    def cat_logits(self, hpool, opt_emb, opt_mask):     # hpool [N,d], opt_emb [N,O,d]
        p = self.cat_proj(hpool).unsqueeze(1)
        return (p * opt_emb).sum(-1).masked_fill(opt_mask < 0.5, -1e9)

    def sel_scores(self, span, field, conf, parse_mask, ctxv=None):  # span [N,K,d], field [N,d]
        # Scoreur PONCTUEL : chaque candidat est noté isolément, à partir de son span et du type
        # — c'est-à-dire des deux mêmes entrées que le score de détection. Il ne peut donc pas
        # apprendre autre chose que le classement du détecteur (cf. RerankHeads).
        # use_conf : les checkpoints antérieurs au passage "re-ranker pur" ont été entraînés
        # AVEC le biais de confiance ; il faut le réactiver pour les évaluer sous leur propre
        # fonction de score (sinon on mesure un modèle sous une fonction qu'il n'a pas apprise).
        f = self.sel_f(field).unsqueeze(1)
        s = self.sel_s(span)
        sc = self.sel_o(torch.tanh(f + s)).squeeze(-1)
        if self.use_conf:
            c = conf.clamp(1e-4, 1 - 1e-4)
            sc = sc + self.sel_c * torch.log(c / (1 - c))
        return sc.masked_fill(parse_mask < 0.5, -1e9)


class RerankHeads(NormHeads):
    """Même tête CAT, mais une sélection qui peut réellement re-classer.

    Deux informations que le détecteur n'a pas :
      - le CONTEXTE local de chaque candidat (fenêtre de mots autour du span) ;
      - les AUTRES candidats — le détecteur note chaque span isolément, ici ils se
        comparent via une attention sur les K candidats.
    """
    needs_ctx = True
    use_conf = False

    def __init__(self, d=D, h=256, heads=4, win=20):
        super().__init__(d, h)
        self.win = win
        self.sel_in = nn.Linear(3 * d, h)
        self.sel_attn = nn.MultiheadAttention(h, heads, batch_first=True)
        self.sel_out = nn.Linear(h, 1)

    def sel_scores(self, span, field, conf, parse_mask, ctxv=None):
        if ctxv is None:
            ctxv = torch.zeros_like(span)
        f = field.unsqueeze(1).expand(-1, span.shape[1], -1)
        x = self.sel_in(torch.cat([span, ctxv, f], dim=-1))          # [N,K,h]
        pad = parse_mask < 0.5
        a, _ = self.sel_attn(x, x, x, key_padding_mask=pad)          # les candidats se comparent
        sc = self.sel_out(torch.tanh(x + a)).squeeze(-1)
        return sc.masked_fill(pad, -1e9)


class NullHeads(NormHeads):
    """Les têtes décident elles-mêmes de s'abstenir — plus aucun seuil.

    CAT       : une option de plus, « champ non documenté ». ZÉRO paramètre : l'option est
                une chaîne encodée par l'encodeur, comme les autres.
    Sélection : un slot NULL dans le softmax, dont le score dépend du champ ET du résumé
                des candidats — il peut donc dire « ils sont tous mauvais ».

    Motivation métrique : s'abstenir coûte 1 faux négatif, se tromper en coûte 2 (fp + fn).
    Quand aucun candidat ne correspond, NULL est donc l'action optimale, et on l'entraîne ainsi.
    """
    use_null = True

    def __init__(self, d=D, h=256):
        super().__init__(d, h)
        self.null_in = nn.Linear(2 * d, h)
        self.null_out = nn.Linear(h, 1)

    def null_score(self, span, field, parse_mask):   # span [N,K,d], field [N,d]
        m = parse_mask.unsqueeze(-1)
        pooled = (span * m).sum(1) / m.sum(1).clamp(min=1)          # résumé des candidats
        return self.null_out(torch.tanh(self.null_in(torch.cat([field, pooled], dim=-1))))


def local_context(token_emb, cands, win=20):
    """Moyenne des embeddings de mots autour de chaque candidat. [K,d]"""
    L = token_emb.shape[0]
    return torch.stack([token_emb[max(0, ws - win):min(L, ws + w + 1 + win)].mean(0)
                        for ws, w, _, _, _ in cands])


# ============================================================ encodage e_f / options (encodeur GLiNER)
def encode_texts(model, texts, dev, maxlen=48):
    tok = model.processor.tokenizer
    enc = tok(texts, padding=True, truncation=True, max_length=maxlen, return_tensors="pt").to(dev)
    out = model.encoder(input_ids=enc["input_ids"], attention_mask=enc["attention_mask"])
    m = enc["attention_mask"].unsqueeze(-1).float()
    return (out.last_hidden_state * m).sum(1) / m.sum(1).clamp(min=1)   # [N,d]


# ============================================================ métadonnées par doc (cibles + spans gold)
def build_doc_meta(gold_path, prod_path):
    """id -> [{key,label,family,target,options,spans:[(cs,ce)]}]  (champs à normaliser du doc)."""
    # cibles canon par doc
    tgt = {}
    for line in open(prod_path, encoding="utf-8"):
        r = json.loads(line); rid = f"lym_{r['sample_index']}"; ann = r.get("annotation") or {}
        d = {}
        for k in T.FIELDS:
            v = ann.get(k)
            if v is None:
                continue
            v = [v] if isinstance(v, dict) else v
            for it in v:
                if isinstance(it, dict) and it.get("value") not in (None, ""):
                    c = T.normalize_target(k, it["value"])
                    if c is not None:
                        d[k] = c; break
        tgt[rid] = d
    meta = {}
    for line in open(gold_path, encoding="utf-8"):
        r = json.loads(line); did = r["id"]; entries = []
        for k, spans in r["gold"].items():
            if k not in T.FIELD_SPEC:
                continue
            fam = T.FIELD_SPEC[k]["family"]
            if fam == "TXT":
                continue
            tv = tgt.get(did, {}).get(k)
            if tv is None:
                continue
            cs = [(int(s), int(e)) for s, e, _ in spans][:8]
            if not cs:
                continue
            opts = list(T.FIELD_SPEC[k]["classes"].keys()) if fam == "CAT" else None
            entries.append({"key": k, "label": KEY2LABEL[k], "family": fam,
                            "target": tv, "options": opts, "spans": cs})
        meta[did] = entries
    return meta


# ============================================================ mapping char -> mot
def word_offsets(model, text):
    # même splitter que le processor (lower=True ne change pas les positions char)
    return [(s, e) for _, s, e in model.processor.word_splitter(text, lower=True)]


def charspan_to_word(woff, cs, ce, L):
    """(cs,ce) char -> (word_start,width) ; None si hors zone encodée L."""
    ws = we = None
    for i, (a, b) in enumerate(woff):
        if b > cs and a < ce:               # overlap
            if ws is None:
                ws = i
            we = i
    if ws is None or ws >= L:
        return None
    we = min(we, L - 1)
    return ws, min(we - ws, 23)             # width borné à max_width-1


# ============================================================ loss normalisation d'un doc
CAND_K = 12          # candidats par champ (top-k du VRAI score de détection natif)
CAND_WLIM = 6        # largeur max des spans-valeur (dates/nombres = courts)
# valeur de `count` passée à count_embed pour générer les candidats. DOIT valoir 1 :
# le processor écrit structure[0]=1 pour la tâche `entities`, donc la détection a été
# entraînée avec count_embed(schema, 1). Interroger avec 3 place le modèle dans un régime
# de conditionnement qu'il n'a jamais vu. (Surchargeable pour l'expérience.)
CAND_COUNT = int(_os.environ.get("CAND_COUNT", "1"))


def detection_scores(model, span_rep, markers, count=CAND_COUNT):
    """Score de détection NATIF par champ : count_embed(markers) puis einsum. [nfields,L,W].
    C'est le même score que la loss structure -> unifie détection et normalisation."""
    sp = model.count_embed(markers[1:], count)
    if sp.dim() == 2:
        sp = sp.unsqueeze(0)
    return torch.einsum('lkd,bpd->bplk', span_rep, sp)[0]      # [nfields,L,W]


def native_candidates(scores_f, woff, L, Wm, k=CAND_K, wlim=CAND_WLIM):
    """Top-k spans du score de détection du champ -> [(ws,w,cs,ce,score)]."""
    Wl = min(scores_f.shape[1], wlim)
    sc = scores_f[:, :Wl]
    flat = sc.reshape(-1)
    kk = min(k, flat.numel())
    vals, idxs = torch.topk(flat, kk)
    out = []
    for r, idx in enumerate(idxs.tolist()):
        i = idx // Wl; w = idx % Wl
        if i >= L or i >= len(woff):
            continue
        cs = woff[i][0]; ce = woff[min(i + w, len(woff) - 1)][1]
        out.append((i, min(w, Wm - 1), cs, ce, vals[r]))
    return out


def norm_loss_doc(model, heads, token_emb, text, entries, fc, markers, lab2idx, dev,
                  hard_w=0.0, margin=1.0):
    """Version UNIFIÉE : candidats = top-k du VRAI score de détection natif ∪ gold.
    Tout différentiable : softmax/marginal-likelihood sur les candidats. Retourne (loss, n)."""
    if not entries:
        return torch.tensor(0.0, device=dev), 0, 0
    L = token_emb.shape[0]
    span_rep = model.compute_span_rep(token_emb)["span_rep"]    # [L,W,d]
    Wm = span_rep.shape[1]
    dscores = detection_scores(model, span_rep, markers)        # [nfields,L,W]
    woff = word_offsets(model, text)
    loss = torch.tensor(0.0, device=dev); n = 0; nhard = 0
    for e in entries:
        li = lab2idx.get(e["label"])
        if li is None or li >= dscores.shape[0]:
            continue
        tmark = markers[1 + li]                                 # marqueur de type NATIF
        # RE-RANKER : candidats = NATIFS uniquement (pas d'injection gold à score fixe, sinon la tête
        # apprend à suivre la détection au lieu de re-ranker). Positif = candidat natif qui matche.
        cand = native_candidates(dscores[li], woff, L, Wm)
        seen, C = set(), []
        for (ws, w, cs, ce, sco) in cand:
            key = (ws, w)
            if key in seen:
                continue
            seen.add(key); C.append((ws, w, cs, ce, sco))
        if not C:
            continue
        H = torch.stack([span_rep[ws, w] for ws, w, _, _, _ in C]).unsqueeze(0)   # [1,K,d]
        dsc = torch.stack([sco for _, _, _, _, sco in C]).unsqueeze(0)            # [1,K] score détection
        parsed = [T.normalize_target(e["key"], text[cs:ce]) for _, _, cs, ce, _ in C]
        if e["family"] == "CAT":
            # attention douce pondérée par la relevance de détection (différentiable)
            a = torch.softmax(dsc, dim=1).unsqueeze(-1)          # [1,K,1]
            zf = (a * H).sum(1)                                  # [1,d]
            oe = fc["_opt"][e["key"]].unsqueeze(0)
            logits = heads.cat_logits(zf, oe, torch.ones(1, oe.shape[1], device=dev))
            opts = e["options"]
            ti = len(opts) - 1 if e["target"] is None else opts.index(e["target"])
            tgt = torch.tensor([ti], device=dev)
            loss = loss + F.cross_entropy(logits, tgt); n += 1
        else:
            pm = torch.tensor([[1.0 if p is not None else 0.0 for p in parsed]], device=dev)
            mm = torch.tensor([[1.0 if _match(e["family"], p, e["target"]) else 0.0 for p in parsed]], device=dev)
            if not getattr(heads, "use_null", False) and mm.sum() == 0:
                continue
            conf = torch.sigmoid(dsc)                            # relevance détection -> conf
            cv = (local_context(token_emb, C, getattr(heads, "win", 20)).unsqueeze(0)
                  if heads.needs_ctx else None)
            sc = heads.sel_scores(H, tmark.unsqueeze(0), conf, pm, ctxv=cv)
            if getattr(heads, "use_null", False):
                # NULL est correct si le champ est absent, OU si aucun candidat ne convient
                # (mieux vaut s'abstenir que se tromper : 1 fn contre fp+fn)
                sc = torch.cat([sc, heads.null_score(H, tmark.unsqueeze(0), pm)], dim=1)
                nul = 1.0 if (e["target"] is None or float(mm.sum()) == 0) else 0.0
                mm = torch.cat([mm, torch.tensor([[nul]], device=dev)], dim=1)
            logp = torch.log_softmax(sc, dim=1)
            loss = loss - torch.logsumexp(logp.masked_fill(mm < 0.5, -1e9), dim=1).mean(); n += 1
            # CAS DUR : le meilleur candidat SELON LA DÉTECTION est faux alors qu'un candidat
            # correct existe. C'est la seule situation où il y a quelque chose à re-classer —
            # or la vraisemblance marginale ci-dessus est déjà ~0 quand la détection a raison
            # (~92 % des cas), donc ces cas-là ne pèsent presque rien. On les remonte par une
            # marge explicite : score(correct) doit dépasser score(faux top-détection).
            if hard_w > 0:
                dtop = dsc.masked_fill(pm < 0.5, -1e9).argmax(dim=1, keepdim=True)   # [1,1]
                if float(mm.gather(1, dtop)) < 0.5:
                    s_wrong = sc.gather(1, dtop).squeeze(1)
                    s_right = sc.masked_fill(mm < 0.5, -1e9).max(dim=1).values
                    loss = loss + hard_w * F.relu(margin + s_wrong - s_right).mean()
                    nhard += 1
    return loss, n, nhard


@torch.no_grad()
def doc_ctx(model, token_emb, text, markers):
    """Encodage partagé d'un document (span_rep + scores de détection + offsets mots).
    Les trois passes d'inférence (têtes / baseline / candidats) le recalculaient chacune."""
    span_rep = model.compute_span_rep(token_emb)["span_rep"]
    return {"span_rep": span_rep, "Wm": span_rep.shape[1], "L": token_emb.shape[0],
            "dscores": detection_scores(model, span_rep, markers), "woff": word_offsets(model, text)}


@torch.no_grad()
def predict_doc(model, heads, token_emb, text, keys_labels, fc, markers, lab2idx, dev, thresh=None,
                use_heads=True, ctx=None, scores_out=None):
    """Inférence unifiée : pour chaque (key,label,family) -> valeur canon prédite (candidats natifs).
    thresh = décision de REMPLIR (précision/F1). use_heads=False -> BASELINE sans têtes : valeur =
    parse du span top-détection (= GLiNER finetuné seul). Retourne {key: pred}."""
    c = ctx or doc_ctx(model, token_emb, text, markers)
    L, span_rep, Wm, dscores, woff = c["L"], c["span_rep"], c["Wm"], c["dscores"], c["woff"]
    out = {}
    for (key, label, fam) in keys_labels:
        li = lab2idx.get(label)
        if li is None or li >= dscores.shape[0]:
            out[key] = None; continue
        cand = native_candidates(dscores[li], woff, L, Wm)
        if not cand:
            out[key] = None; continue
        if scores_out is not None:
            scores_out[key] = float(torch.sigmoid(cand[0][4]))
        # Le seuil ne disparaît QUE si les têtes sont utilisées ET savent s'abstenir.
        # Le baseline sans têtes doit garder son seuil, sinon il devient « remplir toujours »
        # (0.407 mesuré) et l'ablation surestime l'apport des têtes.
        if (thresh is not None and not (use_heads and getattr(heads, "use_null", False))
                and float(torch.sigmoid(cand[0][4])) < thresh):
            out[key] = None; continue
        H = torch.stack([span_rep[ws, w] for ws, w, _, _, _ in cand]).unsqueeze(0)
        dsc = torch.stack([sco for _, _, _, _, sco in cand]).unsqueeze(0)
        parsed = [T.normalize_target(key, text[cs:ce]) for _, _, cs, ce, _ in cand]
        if not use_heads:
            # BASELINE sans têtes = GLiNER seul : valeur = parse du span top-détection (cand[0])
            out[key] = parsed[0]; continue
        if fam == "CAT":
            a = torch.softmax(dsc, dim=1).unsqueeze(-1); zf = (a * H).sum(1)
            oe = fc["_opt"][key].unsqueeze(0)
            logit = heads.cat_logits(zf, oe, torch.ones(1, oe.shape[1], device=dev))
            opts = cat_options(key, with_null=getattr(heads, "use_null", False))
            pick = opts[int(logit.argmax(-1))]
            out[key] = None if pick == NULL_LABEL else pick
        else:
            pm = torch.tensor([[1.0 if p is not None else 0.0 for p in parsed]], device=dev)
            if pm.sum() == 0:
                out[key] = None; continue
            cv = (local_context(token_emb, cand, getattr(heads, "win", 20)).unsqueeze(0)
                  if heads.needs_ctx else None)
            fmark = markers[1 + li].unsqueeze(0)
            sc = heads.sel_scores(H, fmark, torch.sigmoid(dsc), pm, ctxv=cv)
            if getattr(heads, "use_null", False):
                sc = torch.cat([sc, heads.null_score(H, fmark, pm)], dim=1)
            j = int(sc.argmax(-1))
            out[key] = None if j >= len(parsed) else parsed[j]
    return out


@torch.no_grad()
def candidate_values_doc(model, token_emb, text, keys_labels, markers, lab2idx, dev, ctx=None):
    """{key: [valeurs parsées des top-k candidats natifs]} — pour mesurer le plafond re-ranker."""
    c = ctx or doc_ctx(model, token_emb, text, markers)
    L, span_rep, dscores, woff = c["L"], c["span_rep"], c["dscores"], c["woff"]
    out = {}
    for (key, label, fam) in keys_labels:
        li = lab2idx.get(label)
        if li is None or li >= dscores.shape[0]:
            out[key] = []; continue
        cand = native_candidates(dscores[li], woff, L, span_rep.shape[1])
        out[key] = [T.normalize_target(key, text[cs:ce]) for _, _, cs, ce, _ in cand]
    return out


def markers_of(all_sch_i):
    m = all_sch_i[0]
    return torch.stack(m) if isinstance(m, list) else m


def lab2idx_of(output):
    return {lab: i for i, lab in enumerate(output["entities"].keys())}


def _match(fam, a, b):
    if a is None or b is None:
        return False
    if fam == "NUM":
        try:
            return abs(float(a) - float(b)) / max(abs(float(b)), 1e-6) <= 0.10
        except Exception:
            return False
    return a == b


# ============================================================ cache e_f + options (recalculé / step)
def build_field_cache(model, dev):
    keys = [k for k in T.FIELDS if T.FIELD_SPEC[k]["family"] != "TXT"]
    texts = [f"{KEY2LABEL[k]} : {LABELS[k]['desc']}" for k in keys]
    embs = encode_texts(model, texts, dev)
    cache = {k: embs[i] for i, k in enumerate(keys)}
    # options CAT
    opt = {}
    cat_keys = [k for k in keys if T.FIELD_SPEC[k]["family"] == "CAT"]
    for k in cat_keys:
        opts = cat_options(k)
        oe = encode_texts(model, [f"{KEY2LABEL[k]} : {o}" for o in opts], dev)
        opt[k] = oe
    cache["_opt"] = opt
    return cache
