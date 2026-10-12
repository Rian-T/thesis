"""Évaluation TEST de l'étape 2 — les trois mesures de DESIGN_V2 §5, sur les 410 documents.

Barème INCHANGÉ (une valeur fausse compte fp ET fn, tolérance 10 % sur NUM) pour rester
comparable au 0.603 de la lignée précédente. On ne change pas la règle du jeu en même temps
que le modèle.

  1. macro-F1 par famille contre 0.603 ;
  2. rappel du pool DATE : la cible est-elle atteignable depuis un span du pool APRÈS
     entraînement ? (avant : 0.61 avec le top-12 par champ, 0.821 mesuré à froid à M=1024) ;
  3. macro-F1 restreint aux champs indexés par un RÔLE, définis depuis les données : un champ
     est dit indexé par un rôle si sa cible coïncide avec celle d'un autre champ dans le même
     document plus de `--role_thr` du temps. Aucune liste écrite à la main.

  python eval_assign.py --ckpt <dir> [--limit N]
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
from train_assign import LB, PROD, doc_forward, macro_f1   # noqa: E402

_R = "/lustre/fswork/projects/rech/rua/uvb79kr/french-medgliner"
sys.path.insert(0, _R + "/GLiNER2"); sys.path.insert(0, _R + "/GLiNER2/v3")
from eval_v3 import load_model         # noqa: E402

FAMS = ("CAT", "DATE", "NUM", "ORD")


def role_fields(ds, thr=0.10):
    """Champs indexés par un rôle, DÉRIVÉS des données : ceux dont la cible coïncide avec
    celle d'un autre champ du même document plus de `thr` du temps."""
    co, tot = defaultdict(int), defaultdict(int)
    for d in ds:
        vals = defaultdict(list)
        for e in d["entries"]:
            if e["target"] is not None:
                vals[str(e["target"])].append(e["key"])
        for e in d["entries"]:
            if e["target"] is None:
                continue
            tot[e["key"]] += 1
            if len(vals[str(e["target"])]) > 1:
                co[e["key"]] += 1
    return {k for k in tot if tot[k] >= 5 and co[k] / tot[k] > thr}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--M", type=int, default=1024)
    ap.add_argument("--crit", default="rank")
    ap.add_argument("--max_chars", type=int, default=24000)
    ap.add_argument("--role_thr", type=float, default=0.10)
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
    roles = role_fields(ds, a.role_thr)
    print(f"test={len(ds)} documents  M={a.M} crit={a.crit}  "
          f"champs indexés par un rôle : {len(roles)}/{len(fields)}")

    model = load_model(a.ckpt).to(dev).eval()
    head = A.load_head(ck, dev)
    vm = A.ValueModel(str(_H / "transducer" / "transducer2.pt"), dev, train=False)
    vm.m.load_state_dict(ck["vm"]); vm.m.eval()
    opt_emb = A.encode_options(model, space, dev)

    rows, rrows, probes, docids = [], [], defaultdict(list), []
    pool_hit = defaultdict(lambda: [0, 0])
    det_hit = defaultdict(lambda: [0, 0])
    offgold = defaultdict(lambda: [0, 0])
    with torch.no_grad():
        for i, d in enumerate(ds):
            _, _, _, pool, E, ent = doc_forward(model, d, dev, a.M, a.crit, train=False)
            pred = A.assign_predict_doc(head, vm, E, pool, ent, opt_emb, space, dev)
            cp, q, nl = head(E, pool)
            enc = vm.encode_spans(pool["texts"])
            sr = head.sr_to_h(pool["H"])
            M = pool["S"].shape[1]
            for e in ent:
                fam = T.FIELD_SPEC[e["key"]]["family"]
                r = (fam, e["target"], pred.get(e["key"]))
                rows.append(r)
                docids.append(d["id"])
                if e["key"] in roles:
                    rrows.append(r)
                cls = space.get(e["key"], {}).get("classes") or []
                oe = opt_emb.get(e["key"])
                parts = [cp[e["fi"]]] + ([oe @ q[e["fi"]]] if oe is not None and cls else []) + [nl[e["fi"]]]
                p = torch.softmax(torch.cat(parts), 0)
                probes["p_null"].append(float(p[-1]))
                if e["target"] is not None:
                    probes["p_copy"].append(float(p[:M].sum()))
                    # mesure 2 : la cible est-elle atteignable depuis un span du pool ?
                    top = torch.topk(p[:M], min(64, M)).indices
                    ok = any(G._match(fam, v, e["target"])
                             for v in vm.greedy_many(enc, e["label"], top, sr))
                    pool_hit[fam][0] += ok; pool_hit[fam][1] += 1
                    # CONTRÔLE DÉCISIF : même pool, même transducteur, mais classé par le
                    # score de DÉTECTION BRUT au lieu de P_A. Si les deux rappels sont égaux,
                    # la tête d'affectation n'a rien appris sur OÙ chercher — seulement sur
                    # QUELLE valeur produire — et « la supervision par la valeur fait émerger
                    # les en-têtes jamais annotés » n'est pas démontré.
                    tS = torch.topk(pool["S"][e["fi"]], min(64, M)).indices
                    okS = any(G._match(fam, v, e["target"])
                              for v in vm.greedy_many(enc, e["label"], tS, sr))
                    det_hit[fam][0] += okS; det_hit[fam][1] += 1
                    # et : le span gagnant chevauche-t-il un span gold ? (mesuré à froid
                    # à 0.49-0.62 selon la taille du pool ; doit être remesuré après entraînement)
                    j0 = int(top[0])
                    cs, ce = pool["spans"][j0][2], pool["spans"][j0][3]
                    offgold[fam][0] += not any(min(ce, gb) - max(cs, ga) > 0
                                               for ga, gb in e.get("spans", []))
                    offgold[fam][1] += 1
            if (i + 1) % 50 == 0:
                print(f"  {i+1}/{len(ds)}", flush=True)

    m, per = macro_f1(rows)
    rm, rper = macro_f1(rrows)
    print(f"\n=== 1. MACRO-F1 TEST (barème inchangé) ===")
    print(f"  macro = {m:.3f}   (référence lignée précédente : 0.603)")
    print("  " + "  ".join(f"{f}={per[f]:.3f}" for f in FAMS))
    print(f"\n=== 2. RAPPEL DU POOL (top-64 selon P_A, valeur transduite) ===")
    for f in FAMS:
        h, n = pool_hit[f]
        print(f"  {f:5s} {h}/{n} = {h/max(n,1):.3f}")
    print(f"  (DATE avant entraînement : 0.61 top-12 par champ / 0.821 pool M=1024 à froid)")
    print("\n  MÊME POOL, classé par le score de DÉTECTION BRUT (contrôle) :")
    for f in FAMS:
        h, n = det_hit[f]; hp = pool_hit[f][0] / max(pool_hit[f][1], 1)
        print(f"  {f:5s} {h/max(n,1):.3f}   (P_A {hp:.3f}, écart {hp - h/max(n,1):+.3f})")
    print("\n  span gagnant NE chevauchant aucun span gold (à froid : 0.49-0.62) :")
    for f in FAMS:
        o, n = offgold[f]
        print(f"  {f:5s} {o/max(n,1):.3f}")
    print("\n  scalaires appris : "
          f"alpha={float(head.alpha):+.4f}  beta={float(head.beta):+.4f}  tau={float(head.tau):+.4f}  "
          f"||sr_to_h||={float(head.sr_to_h.weight.norm()):.4f}")
    print(f"\n=== 3. CHAMPS INDEXÉS PAR UN RÔLE ({len(roles)} champs, {len(rrows)} décisions) ===")
    print(f"  macro = {rm:.3f}   " + "  ".join(f"{f}={rper[f]:.3f}" for f in FAMS))
    print(f"\nsondes : p_copy={np.mean(probes['p_copy']):.3f}  p_null={np.mean(probes['p_null']):.3f}")
    import pandas as pd
    pd.DataFrame([(i, *r) for i, r in zip(docids, rows)],
                 columns=["doc_id", "family", "gold", "pred"]).to_parquet(a.ckpt + "/preds_test.parquet")
    json.dump({"macro": m, "per": per, "macro_roles": rm, "per_roles": rper,
               "det_pool": {f: det_hit[f][0] / max(det_hit[f][1], 1) for f in FAMS},
               "offgold": {f: offgold[f][0] / max(offgold[f][1], 1) for f in FAMS},
               "alpha": float(head.alpha), "beta": float(head.beta), "tau": float(head.tau),
               "sr_norm": float(head.sr_to_h.weight.norm()),
               "pool": {f: pool_hit[f][0] / max(pool_hit[f][1], 1) for f in FAMS},
               "p_copy": float(np.mean(probes["p_copy"])),
               "p_null": float(np.mean(probes["p_null"])), "n_roles": len(roles)},
              open(a.ckpt + "/eval_test.json", "w"), indent=1)


if __name__ == "__main__":
    main()
