"""GLiNER NU, contexte complet, métrique actuelle — le chiffre qui manque au dossier.

L'ablation « têtes vs sans-têtes » stockée dans JOURNAL.md §6 donne GLiNER seul à 0.477 et
+0.024 pour les têtes. Mais elle date d'avant QUATRE changements : la correction du cap de
lecture (9 000 -> 24 000 caractères, +0.100), la tête NULL (+0.071), le transducteur (+0.174)
et la correction du seuil de remplissage (+0.015).

Or le cap pénalisait aussi le baseline. Comparer les 0.673 d'aujourd'hui au 0.477 d'alors
surestimerait donc l'apport des têtes d'un montant inconnu. Ce script produit le baseline
DANS LES CONDITIONS ACTUELLES :

  - contexte complet (24 000 caractères, pas 9 000) ;
  - même barème (macro-F1 par famille, valeur fausse = fp ET fn, tolérance 10 % sur NUM) ;
  - même espace de valeurs cible (dérivé des données) et même jeu de 81 champs non-TXT ;
  - seuil de remplissage CALIBRÉ sur la validation, comme pour le modèle à têtes — sinon on
    compare un baseline mal réglé à un système réglé, ce qui gonflerait l'écart.

Deux productions de valeur, parce que « GLiNER nu » est ambigu :
  span brut   la valeur est le texte du span top-détection, sans aucune normalisation ;
  taxonomy    le texte passe par les 300 lignes de règles écrites à la main (= la lignée
              précédente : c'est ce que « GLiNER seul » voulait dire dans JOURNAL.md §6).

  python baseline_nohead.py --model <ckpt>
"""
import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch

_H = Path(__file__).resolve().parent
sys.path.insert(0, str(_H))
import assign as A                     # noqa: E402
import gliner_integrated as G          # noqa: E402
import taxonomy as T                   # noqa: E402
from train_assign import LB, PROD, macro_f1   # noqa: E402

_R = "/lustre/fswork/projects/rech/rua/uvb79kr/french-medgliner"
sys.path.insert(0, _R + "/GLiNER2"); sys.path.insert(0, _R + "/GLiNER2/v3")
from eval_v3 import load_model         # noqa: E402

B = "/lustre/fsn1/projects/rech/rua/uvb79kr/onto/medembed-outputs"
FAMS = ("CAT", "DATE", "NUM", "ORD")
GRID = [round(x, 2) for x in np.arange(0.0, 0.98, 0.02)]


@torch.no_grad()
def collect(model, ds, dev, mode):
    """-> [(famille, cible, valeur proposée, score de détection)] sans aucune tête."""
    out = []
    for i, d in enumerate(ds):
        batch = model.processor.collate_fn_train([(d["text"], d["output"])]).to(dev)
        all_tok, all_sch = model._encode_batch(batch)
        mk = G.markers_of(all_sch[0]); l2i = G.lab2idx_of(d["output"])
        span_rep = model.compute_span_rep(all_tok[0])["span_rep"]
        dsc = G.detection_scores(model, span_rep, mk)
        woff = G.word_offsets(model, d["text"])
        L, W = span_rep.shape[0], span_rep.shape[1]
        for e in d["entries"]:
            fam = T.FIELD_SPEC[e["key"]]["family"]
            li = l2i.get(e["label"])
            if li is None or li >= dsc.shape[0]:
                out.append((fam, e["target"], None, -1.0)); continue
            cand = G.native_candidates(dsc[li], woff, L, W)      # top-k du champ, comme avant
            if not cand:
                out.append((fam, e["target"], None, -1.0)); continue
            ws, w, cs, ce, sco = cand[0]                          # le span TOP-DÉTECTION
            txt = d["text"][cs:ce]
            v = txt if mode == "span" else T.normalize_target(e["key"], txt)
            out.append((fam, e["target"], None if v in (None, "") else str(v),
                        float(torch.sigmoid(sco))))
        if (i + 1) % 50 == 0:
            print(f"  {i+1}/{len(ds)}", flush=True)
    return out


def at(recs, thr):
    return [(f, t, (v if s >= thr else None)) for f, t, v, s in recs]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=B + "/gliner2-lym-V5FROMV3B/best")
    ap.add_argument("--max_chars", type=int, default=24000)
    a = ap.parse_args()
    dev = "cuda"

    fields = [k for k in T.FIELDS if T.FIELD_SPEC[k]["family"] != "TXT"]
    train_ids = {json.loads(l)["id"] for l in open(LB + "/lymphome_train_v2.jsonl", encoding="utf-8")}
    space, index = A.build_value_space(PROD, train_ids, fields)
    full = A.build_dataset_assign(LB + "/lymphome_train_v2.jsonl", PROD, space, index,
                                  fields, cap=a.max_chars)
    _ids = sorted(d["id"] for d in full)
    vid = set(np.random.RandomState(0).choice(_ids, min(100, len(_ids)), replace=False).tolist())
    val = [d for d in full if d["id"] in vid]
    test = A.build_dataset_assign(LB + "/lymphome_test_v2.jsonl", PROD, space, index,
                                  fields, cap=a.max_chars)

    model = load_model(a.model).to(dev).eval()
    print(f"modèle = {a.model}\nvalidation={len(val)} test={len(test)} max_chars={a.max_chars}\n",
          flush=True)

    print(f"{'production de la valeur':28s} {'seuil':>6s} {'val':>7s} {'TEST':>8s}  "
          + " ".join(f"{f:>6s}" for f in FAMS))
    print("-" * 76)
    res = {}
    for mode, name in (("span", "span brut, sans normaliser"), ("tax", "taxonomy.py (300 lignes)")):
        V = collect(model, val, dev, mode)
        Tt = collect(model, test, dev, mode)
        thr = max(GRID, key=lambda t: macro_f1(at(V, t))[0])   # calibré sur la VALIDATION
        mv, _ = macro_f1(at(V, thr))
        mt, pt = macro_f1(at(Tt, thr))
        print(f"{name:28s} {thr:6.2f} {mv:7.3f} {mt:8.3f}  " + " ".join(f"{pt[f]:6.3f}" for f in FAMS))
        res[mode] = {"thr": thr, "val": mv, "test": mt, "per": pt}
    print(f"\nrepères, MÊME barème : lignée précédente 0.603 · têtes actuelles 0.673 · Qwen-9B 0.582")
    print("(JOURNAL.md §6 donnait GLiNER seul à 0.477, mais AVEC le cap à 9 000 caractères)")
    json.dump(res, open(_H / "baseline_nohead.json", "w"), indent=1)


if __name__ == "__main__":
    main()
