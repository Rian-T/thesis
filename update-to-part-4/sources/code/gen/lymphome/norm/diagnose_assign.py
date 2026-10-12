"""Où passent les 0.33 d'écart entre « la réponse est atteignable » et « le modèle la sort » ?

Sur DATE, la cible est dans les 64 premières options 81,6 % du temps et le F1 est à 49,7 %.
Ce script décompose cet écart en causes MUTUELLEMENT EXCLUSIVES, et chiffre le gain
contrefactuel de chacune — pour savoir laquelle vaut qu'on y travaille.

Chaque (document, champ) ayant une cible tombe dans exactement une case :

  OK            la valeur sortie est la bonne
  ABSTENTION    aucune valeur n'a atteint le seuil de remplissage. On note alors si la cible
                était en tête (le modèle SAVAIT et la règle de décision l'a bâillonné) ou non.
  MAUVAISE_VAL  une valeur a été sortie, mais ce n'est pas la bonne. On note si la cible était
                présente dans la distribution, et à quel rang / quelle masse.
  INATTEIGNABLE la cible n'est produite par AUCUNE des options considérées — ni transduction
                d'un span, ni vocabulaire. Là, ni la sélection ni la décision n'y peuvent rien.

Et deux contrefactuels, parce qu'une décomposition sans « combien ça rapporterait » ne dit pas
où travailler :
  - la courbe F1 en fonction du seuil de remplissage (la règle p > 0.5 est-elle la bonne ?) ;
  - le F1 à décision de remplissage PARFAITE (oracle), qui borne ce que la seule politique
    d'abstention peut rapporter, sélection inchangée.

  python diagnose_assign.py --ckpt <dir> --M 256
"""
import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import torch

_H = Path(__file__).resolve().parent
sys.path.insert(0, str(_H))
import assign as A                     # noqa: E402
import gliner_integrated as G          # noqa: E402
import taxonomy as T                   # noqa: E402
from train_assign import LB, PROD, doc_forward, macro_f1   # noqa: E402

_R = "/lustre/fswork/projects/rech/rua/uvb79kr/french-medgliner"
sys.path.insert(0, _R + "/GLiNER2"); sys.path.insert(0, _R + "/GLiNER2/v3")
from eval_v3 import load_model         # noqa: E402

FAMS = ("CAT", "DATE", "NUM", "ORD")
GRID = [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.7]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--M", type=int, default=256)
    ap.add_argument("--crit", default="rank")
    ap.add_argument("--topk", type=int, default=32)
    ap.add_argument("--max_chars", type=int, default=24000)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    dev = "cuda"

    ck = torch.load(a.ckpt + "/assign.pt", map_location=dev)
    space = ck["space"]
    fields = [k for k in T.FIELDS if T.FIELD_SPEC[k]["family"] != "TXT"]
    train_ids = {json.loads(l)["id"] for l in open(LB + "/lymphome_train_v2.jsonl", encoding="utf-8")}
    _, index = A.build_value_space(PROD, train_ids, fields)
    ds = A.build_dataset_assign(LB + "/lymphome_test_v2.jsonl", PROD, space, index,
                                fields, cap=a.max_chars)
    if a.limit:
        ds = ds[:a.limit]

    model = load_model(a.ckpt).to(dev).eval()
    head = A.load_head(ck, dev)
    vm = A.ValueModel(str(_H / "transducer" / "transducer2.pt"), dev, train=False)
    if ck.get("vm") is not None:
        vm.m.load_state_dict(ck["vm"])
    vm.m.eval()
    opt_emb = A.encode_options(model, space, dev)
    print(f"test={len(ds)} documents  M={a.M} topk={a.topk}", flush=True)

    cause = defaultdict(Counter)
    rank_when_lost, mass_gold, mass_pred = defaultdict(list), defaultdict(list), defaultdict(list)
    recs = []          # (famille, cible, [(valeur, masse) triées])
    with torch.no_grad():
        for i, d in enumerate(ds):
            _, _, _, pool, E, ent = doc_forward(model, d, dev, a.M, a.crit, train=False)
            cp, q, nl = head(E, pool)
            enc = vm.encode_spans(pool["texts"])
            sr = head.sr_to_h(pool["H"])
            M = pool["S"].shape[1]
            for e in ent:
                fam = T.FIELD_SPEC[e["key"]]["family"]
                cls = space.get(e["key"], {}).get("classes") or []
                oe = opt_emb.get(e["key"])
                parts = [cp[e["fi"]]] + ([oe @ q[e["fi"]]] if oe is not None and cls else []) + [nl[e["fi"]]]
                p = torch.softmax(torch.cat(parts), 0)
                sel = torch.topk(p[:M], min(a.topk, M)).indices
                mass = {}
                for j, v in zip(sel.tolist(), vm.greedy_many(enc, e["label"], sel, sr, e["key"])):
                    if v:
                        mass[v] = mass.get(v, 0.0) + float(p[j])
                if oe is not None:
                    for oi, c in enumerate(cls):
                        mass[c] = mass.get(c, 0.0) + float(p[M + oi])
                ordered = sorted(mass.items(), key=lambda kv: -kv[1])
                recs.append((fam, e["target"], ordered))
                if e["target"] is None:
                    continue
                # masse totale portée par la BONNE valeur (toutes graphies confondues via _match)
                gm = sum(m for v, m in ordered if G._match(fam, v, e["target"]))
                gr = next((r for r, (v, _) in enumerate(ordered)
                           if G._match(fam, v, e["target"])), None)
                top = ordered[0] if ordered else (None, 0.0)
                mass_gold[fam].append(gm); mass_pred[fam].append(top[1])
                if gr is None:
                    cause[fam]["INATTEIGNABLE"] += 1
                elif top[1] <= 0.5:
                    cause[fam]["ABSTENTION_cible_en_tete" if gr == 0
                               else "ABSTENTION_cible_ailleurs"] += 1
                    rank_when_lost[fam].append(gr)
                elif gr == 0:
                    cause[fam]["OK"] += 1
                else:
                    cause[fam]["MAUVAISE_VAL"] += 1
                    rank_when_lost[fam].append(gr)
            if (i + 1) % 50 == 0:
                print(f"  {i+1}/{len(ds)}", flush=True)

    print("\n=== DÉCOMPOSITION DES CIBLES DOCUMENTÉES (causes exclusives) ===")
    keys = ["OK", "ABSTENTION_cible_en_tete", "ABSTENTION_cible_ailleurs",
            "MAUVAISE_VAL", "INATTEIGNABLE"]
    print(f"{'':28s}" + "".join(f"{f:>9s}" for f in FAMS))
    for k in keys:
        tot = {f: sum(cause[f].values()) for f in FAMS}
        print(f"  {k:26s}" + "".join(f"{cause[f][k]/max(tot[f],1):9.3f}" for f in FAMS))

    print("\n=== SEUIL DE REMPLISSAGE : la règle p > 0.5 est-elle la bonne ? ===")
    print(f"{'seuil':>7s} {'macro':>7s} " + " ".join(f"{f:>7s}" for f in FAMS))
    best = (0, -1)
    for thr in GRID:
        rows = []
        for fam, tgt, ordered in recs:
            pv = ordered[0][0] if ordered and ordered[0][1] > thr else None
            rows.append((fam, tgt, pv))
        m, per = macro_f1(rows)
        best = max(best, (m, thr), key=lambda x: x[0])
        print(f"{thr:7.2f} {m:7.3f} " + " ".join(f"{per[f]:7.3f}" for f in FAMS))
    print(f"  -> meilleur seuil {best[1]} (macro {best[0]:.3f})")

    rows_or = [(fam, tgt, (ordered[0][0] if ordered else None) if tgt is not None else None)
               for fam, tgt, ordered in recs]
    mo, po = macro_f1(rows_or)
    print(f"\n=== CONTREFACTUEL : décision de remplissage PARFAITE (sélection inchangée) ===")
    print(f"  macro = {mo:.3f}   " + "  ".join(f"{f}={po[f]:.3f}" for f in FAMS))

    print("\n=== MASSE (moyenne) ===")
    for f in FAMS:
        print(f"  {f:5s} portée par la BONNE valeur {np.mean(mass_gold[f]):.3f}  "
              f"| par la valeur SORTIE {np.mean(mass_pred[f]):.3f}  "
              f"| rang médian de la cible quand on la rate "
              f"{np.median(rank_when_lost[f]) if rank_when_lost[f] else float('nan'):.0f}")

    json.dump({"cause": {f: dict(cause[f]) for f in FAMS},
               "seuil_optimal": best[1], "macro_seuil_optimal": best[0],
               "macro_oracle_remplissage": mo,
               "masse_gold": {f: float(np.mean(mass_gold[f])) for f in FAMS}},
              open(a.ckpt + "/diagnose.json", "w"), indent=1)


if __name__ == "__main__":
    main()
