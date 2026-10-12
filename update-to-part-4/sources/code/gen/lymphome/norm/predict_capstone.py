"""Prédictions du modèle à têtes au FORMAT CAPSTONE, pour entrer dans la table de RESULTS.md.

Le dossier contient deux métriques qui ne sont PAS sur le même axe, et les confondre serait
une faute :

  capstone   value-F1, Jaccard de tokens >= 0.5, comparé au TEXTE DES SPANS gold, après
             field competition. Indulgent : un recouvrement partiel compte.
  norm       macro-F1 par famille, égalité EXACTE de la chaîne canonique (tolérance 10 %
             sur NUM seulement), comparé à la VALEUR canonique. Strict.

Les 0.640 / 0.657 / 0.650 de RESULTS.md sont en capstone ; nos 0.603 / 0.673 sont en norm.
Ce script produit le parquet attendu par `hf_eval/evaluate.py` pour que le modèle à têtes
soit scoré sur la MÊME métrique que les baselines publiés, et devienne comparable.

Deux points d'honnêteté, écrits plutôt que tus :

1. Le capstone évalue les 89 champs, dont 8 de famille TXT que le pipeline à têtes ne traite
   pas. Les laisser vides ferait 8 faux négatifs par document et nous pénaliserait face aux
   baselines qui, eux, prédisent tout. On émet donc pour les champs TXT le span top-détection
   du modèle, ce que fait déjà GLiNER nu — la comparaison porte alors bien sur les 81 champs
   où les têtes changent quelque chose, sans avantage ni handicap artificiel.

2. Le seuil est choisi sur la validation par `evaluate.py`. Notre split de validation est le
   tirage aléatoire corrigé (seed 0) ; les baselines publiés ont été calibrés sur l'ancien
   split (« les 100 premiers »), qui était 16 % plus dense. L'écart est faible mais il existe,
   et il joue plutôt EN NOTRE DÉFAVEUR (notre validation est plus proche du test, donc moins
   flatteuse pour un seuil).

  python predict_capstone.py --ckpt <dir> --split test --out preds_test.parquet
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch

_H = Path(__file__).resolve().parent
sys.path.insert(0, str(_H))
import assign as A                     # noqa: E402
import gliner_integrated as G          # noqa: E402
import taxonomy as T                   # noqa: E402
from train_assign import LB, PROD, doc_forward   # noqa: E402

_R = "/lustre/fswork/projects/rech/rua/uvb79kr/french-medgliner"
sys.path.insert(0, _R + "/GLiNER2"); sys.path.insert(0, _R + "/GLiNER2/v3")
from eval_v3 import load_model         # noqa: E402

KEY2LABEL = A.KEY2LABEL


@torch.no_grad()
def run(model, head, vm, ds, opt_emb, space, dev, M, crit, topk):
    rows = []
    for i, d in enumerate(ds):
        _, all_tok, all_sch, pool, E, ent = doc_forward(model, d, dev, M, crit, train=False)
        cp, q, nl = head(E, pool)
        enc = vm.encode_spans(pool["texts"])
        sr = head.sr_to_h(pool["H"])
        Mn = pool["S"].shape[1]
        import math
        for e in ent:
            cls = space.get(e["key"], {}).get("classes") or []
            oe = opt_emb.get(e["key"])
            parts = [cp[e["fi"]]] + ([oe @ q[e["fi"]]] if oe is not None and cls else []) + [nl[e["fi"]]]
            p = torch.softmax(torch.cat(parts), 0)
            sel = torch.topk(p[:Mn], min(topk, Mn)).indices
            vals, lpb = vm.greedy_scored(enc, e["label"], sel, sr, e["key"])
            mass, where = {}, {}
            for j, v, l in zip(sel.tolist(), vals, lpb):
                if not v:
                    continue
                w = float(p[j]) * math.exp(min(l, 0.0))
                mass[v] = mass.get(v, 0.0) + w
                if w > where.get(v, (0.0, -1))[0]:
                    where[v] = (w, j)          # le span le plus responsable de cette valeur
            if oe is not None:
                for oi, c in enumerate(cls):
                    mass[c] = mass.get(c, 0.0) + float(p[Mn + oi])
            if not mass:
                continue
            v, pv = max(mass.items(), key=lambda kv: kv[1])
            j = where.get(v, (0.0, -1))[1]
            cs, ce = (pool["spans"][j][2], pool["spans"][j][3]) if j >= 0 else (-1, -1)
            rows.append({"doc_id": d["id"], "key": e["key"], "start": int(cs), "end": int(ce),
                         "confidence": float(pv), "value": v})

        # champs TXT : le pipeline à têtes ne les traite pas. On émet le span top-détection,
        # exactement ce que fait GLiNER nu, pour que la comparaison à 89 champs soit équitable.
        mk = G.markers_of(all_sch[0]); l2i = G.lab2idx_of(d["output"])
        span_rep = model.compute_span_rep(all_tok[0])["span_rep"]
        dsc = G.detection_scores(model, span_rep, mk)
        woff = G.word_offsets(model, d["text"])
        L, W = span_rep.shape[0], span_rep.shape[1]
        for k in T.FIELDS:
            if T.FIELD_SPEC[k]["family"] != "TXT" or k not in KEY2LABEL:
                continue
            li = l2i.get(KEY2LABEL[k])
            if li is None or li >= dsc.shape[0]:
                continue
            cand = G.native_candidates(dsc[li], woff, L, W)
            if not cand:
                continue
            _, _, cs, ce, sco = cand[0]
            rows.append({"doc_id": d["id"], "key": k, "start": int(cs), "end": int(ce),
                         "confidence": float(torch.sigmoid(sco)), "value": d["text"][cs:ce]})
        if (i + 1) % 50 == 0:
            print(f"  {i+1}/{len(ds)}", flush=True)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--split", choices=("validation", "test"), required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--M", type=int, default=256)
    ap.add_argument("--crit", default="rank")
    ap.add_argument("--topk", type=int, default=32)
    ap.add_argument("--max_chars", type=int, default=24000)
    a = ap.parse_args()
    dev = "cuda"

    ck = torch.load(a.ckpt + "/assign.pt", map_location=dev)
    space = ck["space"]
    # TOUS les champs, TXT compris : le schéma présenté au modèle doit être celui du capstone.
    fields = [k for k in T.FIELDS if T.FIELD_SPEC[k]["family"] != "TXT"]
    train_ids = {json.loads(l)["id"] for l in open(LB + "/lymphome_train_v2.jsonl", encoding="utf-8")}
    _, index = A.build_value_space(PROD, train_ids, fields)

    src = LB + ("/lymphome_train_v2.jsonl" if a.split == "validation" else "/lymphome_test_v2.jsonl")
    ds = A.build_dataset_assign(src, PROD, space, index, fields, cap=a.max_chars)
    if a.split == "validation":
        _ids = sorted(d["id"] for d in ds)
        vid = set(np.random.RandomState(0).choice(_ids, min(100, len(_ids)), replace=False).tolist())
        ds = [d for d in ds if d["id"] in vid]

    model = load_model(a.ckpt).to(dev).eval()
    head = A.load_head(ck, dev)
    vm = A.ValueModel(str(_H / "transducer" / "transducer2.pt"), dev, train=False)
    if ck.get("vm") is not None:
        vm.m.load_state_dict(ck["vm"])
    vm.m.eval()
    opt_emb = A.encode_options(model, space, dev)

    print(f"{a.split} : {len(ds)} documents  M={a.M} topk={a.topk}", flush=True)
    rows = run(model, head, vm, ds, opt_emb, space, dev, a.M, a.crit, a.topk)
    pd.DataFrame(rows).to_parquet(a.out)
    print(f"-> {a.out}  ({len(rows)} prédictions, {len(set(r['key'] for r in rows))} champs)")


if __name__ == "__main__":
    main()
