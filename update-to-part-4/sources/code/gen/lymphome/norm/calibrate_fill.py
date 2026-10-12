"""La décision de REMPLIR, calibrée sur la validation — le plus gros levier mesuré.

Le diagnostic donne trois faits qui pointent tous au même endroit :
  - une décision de remplissage PARFAITE vaudrait +0.089 de macro, sélection inchangée ;
  - 25,4 % des cibles CAT (17,3 % des NUM) ont la BONNE valeur en tête de distribution et
    le modèle s'abstient quand même : il sait, et la règle de décision le bâillonne ;
  - le seuil optimal est ~0.30, pas 0.5.

La règle `p > 0.5` venait d'un raisonnement sur la matrice de coût (valeur fausse = 2,
abstention = 1), valable pour un coût ADDITIF. Or la métrique est un macro-F1 par famille,
qui ne l'est pas. Pour la F1, l'optimum est ~F1*/2 (Lipton et al. 2014), soit 0.24-0.39 ici.

Quatre règles comparées, toutes choisies sur la VALIDATION et rapportées sur le TEST :
  0.5                le raisonnement additif d'origine
  global             un seuil unique, balayé sur la validation
  par famille        un seuil par famille, balayé sur la validation
  F1/2 par famille   la règle fermée, sans balayage : seuil = F1_validation(famille) / 2

La quatrième est la plus intéressante s'il elle tient : elle n'a AUCUN degré de liberté
ajusté, elle se déduit de la métrique. Ce n'est pas un réglage caché, c'est la même
dérivation que l'originale mais pour la bonne métrique.

  python calibrate_fill.py --ckpt <dir> --M 256 --topk 32
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
GRID = [round(x, 2) for x in np.arange(0.0, 0.85, 0.025)]


@torch.no_grad()
def collect(model, head, vm, ds, opt_emb, space, dev, M, crit, topk):
    """-> [(famille, cible, [(valeur, masse) triées décroissant])] pour chaque (doc, champ)."""
    out = []
    for i, d in enumerate(ds):
        _, _, _, pool, E, ent = doc_forward(model, d, dev, M, crit, train=False)
        cp, q, nl = head(E, pool)
        enc = vm.encode_spans(pool["texts"])
        sr = head.sr_to_h(pool["H"])
        Mn = pool["S"].shape[1]
        for e in ent:
            cls = space.get(e["key"], {}).get("classes") or []
            oe = opt_emb.get(e["key"])
            parts = [cp[e["fi"]]] + ([oe @ q[e["fi"]]] if oe is not None and cls else []) + [nl[e["fi"]]]
            p = torch.softmax(torch.cat(parts), 0)
            sel = torch.topk(p[:Mn], min(topk, Mn)).indices
            mass = {}
            for j, v in zip(sel.tolist(), vm.greedy_many(enc, e["label"], sel, sr, e["key"])):
                if v:
                    mass[v] = mass.get(v, 0.0) + float(p[j])
            if oe is not None:
                for oi, c in enumerate(cls):
                    mass[c] = mass.get(c, 0.0) + float(p[Mn + oi])
            out.append((T.FIELD_SPEC[e["key"]]["family"], e["target"],
                        sorted(mass.items(), key=lambda kv: -kv[1]), float(p[-1])))
        if (i + 1) % 50 == 0:
            print(f"  {i+1}/{len(ds)}", flush=True)
    return out


def apply(recs, thr):
    """thr : famille -> seuil. -> lignes (famille, cible, prédiction)."""
    return [(f, t, (o[0][0] if o and o[0][1] > thr(f) else None)) for f, t, o, _ in recs]


def f1_family(recs, fam, thr):
    sub = [(f, t, p) for f, t, p in apply(recs, lambda _: thr) if f == fam]
    tp = fp = fn = 0
    for f, t, p in sub:
        if t is not None and p is not None:
            if G._match(f, p, t):
                tp += 1
            else:
                fp += 1; fn += 1
        elif p is not None:
            fp += 1
        elif t is not None:
            fn += 1
    pr, rc = tp / max(tp + fp, 1), tp / max(tp + fn, 1)
    return 2 * pr * rc / max(pr + rc, 1e-9)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--M", type=int, default=256)
    ap.add_argument("--crit", default="rank")
    ap.add_argument("--topk", type=int, default=32)
    ap.add_argument("--max_chars", type=int, default=24000)
    a = ap.parse_args()
    dev = "cuda"

    ck = torch.load(a.ckpt + "/assign.pt", map_location=dev)
    space = ck["space"]
    fields = [k for k in T.FIELDS if T.FIELD_SPEC[k]["family"] != "TXT"]
    train_ids = {json.loads(l)["id"] for l in open(LB + "/lymphome_train_v2.jsonl", encoding="utf-8")}
    _, index = A.build_value_space(PROD, train_ids, fields)

    # VALIDATION : exactement le tirage de l'entraînement (aléatoire, seed 0 — échangeable
    # avec le test depuis la correction ; l'ancien « 100 premiers ids » était +16 % plus dense
    # et rendait toute calibration non transférable).
    full = A.build_dataset_assign(LB + "/lymphome_train_v2.jsonl", PROD, space, index,
                                  fields, cap=a.max_chars)
    _ids = sorted(d["id"] for d in full)
    vid = set(np.random.RandomState(0).choice(_ids, min(100, len(_ids)), replace=False).tolist())
    val = [d for d in full if d["id"] in vid]
    test = A.build_dataset_assign(LB + "/lymphome_test_v2.jsonl", PROD, space, index,
                                  fields, cap=a.max_chars)

    model = load_model(a.ckpt).to(dev).eval()
    head = A.load_head(ck, dev)
    vm = A.ValueModel(str(_H / "transducer" / "transducer2.pt"), dev, train=False)
    if ck.get("vm") is not None:
        vm.m.load_state_dict(ck["vm"])
    vm.m.eval()
    opt_emb = A.encode_options(model, space, dev)

    print(f"validation={len(val)}  test={len(test)}  M={a.M} topk={a.topk}", flush=True)
    print("collecte validation…", flush=True)
    V = collect(model, head, vm, val, opt_emb, space, dev, a.M, a.crit, a.topk)
    print("collecte test…", flush=True)
    Tst = collect(model, head, vm, test, opt_emb, space, dev, a.M, a.crit, a.topk)

    # --- les quatre règles, toutes choisies sur la VALIDATION
    g = max(GRID, key=lambda t: macro_f1(apply(V, lambda _: t))[0])
    per = {f: max(GRID, key=lambda t: f1_family(V, f, t)) for f in FAMS}
    f1v = {f: f1_family(V, f, g) for f in FAMS}
    half = {f: min(GRID, key=lambda t: abs(t - f1v[f] / 2)) for f in FAMS}

    def vs_null(recs, k=1.0):
        """Remplir ssi la masse AGRÉGÉE de la meilleure valeur dépasse k * masse de ⊥.

        Teste l'asymétrie soupçonnée : ⊥ est une option ATOMIQUE qui concourt contre jusqu'à
        M options de copie entre lesquelles la masse se disperse. Il gagnerait donc
        structurellement, indépendamment de sa justesse — ce qui expliquerait les 11 à 23 %
        de cibles où la BONNE valeur est en tête et où le modèle s'abstient quand même.
        Ici on compare ⊥ à la masse REGROUPÉE par valeur, pas à un span isolé.
        """
        return [(f, t, (o[0][0] if o and o[0][1] > k * pn else None)) for f, t, o, pn in recs]

    kbest = max([0.5, 0.75, 1.0, 1.5, 2.0, 3.0],
                key=lambda k: macro_f1(vs_null(V, k))[0])
    rules = {
        "0.5 (raisonnement additif)": lambda f: 0.5,
        f"global (tau={g})": lambda f: g,
        "par famille": lambda f: per[f],
        "F1/2 par famille (règle fermée)": lambda f: half[f],
    }
    print(f"\n{'règle':34s} {'val':>7s} {'TEST':>8s}  " + " ".join(f"{f:>6s}" for f in FAMS))
    print("-" * 76)
    res = {}
    for name, fn in rules.items():
        mv, _ = macro_f1(apply(V, fn))
        mt, pt = macro_f1(apply(Tst, fn))
        print(f"{name:34s} {mv:7.3f} {mt:8.3f}  " + " ".join(f"{pt[f]:6.3f}" for f in FAMS))
        res[name] = {"val": mv, "test": mt, "per": pt}
    for k in (1.0, kbest):
        mv, _ = macro_f1(vs_null(V, k)); mt, pt = macro_f1(vs_null(Tst, k))
        nm = f"masse agrégée > {k} x masse(⊥)"
        print(f"{nm:34s} {mv:7.3f} {mt:8.3f}  " + " ".join(f"{pt[f]:6.3f}" for f in FAMS))
        res[nm] = {"val": mv, "test": mt, "per": pt}
    print(f"\nseuils par famille (balayés) : " + "  ".join(f"{f}={per[f]}" for f in FAMS))
    print(f"seuils F1/2 (déduits)        : " + "  ".join(f"{f}={half[f]}" for f in FAMS))
    print(f"F1 de validation utilisés    : " + "  ".join(f"{f}={f1v[f]:.3f}" for f in FAMS))
    json.dump({"rules": res, "per_family": per, "half": half, "f1_val": f1v},
              open(a.ckpt + "/calibrate_fill.json", "w"), indent=1)


if __name__ == "__main__":
    main()
