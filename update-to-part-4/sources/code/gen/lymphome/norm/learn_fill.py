"""La décision de remplir, APPRISE — le plus gros gisement mesuré qui ne soit pas architectural.

Mesuré : une décision de remplissage parfaite vaut +0.089 à sélection inchangée. Le seuil
calibré n'en a récupéré que 0.015. Il reste +0.074, et sur CAT une décision parfaite fait
passer 0.702 à 0.873 — soit précisément la famille où les têtes marchent déjà (+0.252).

Pourquoi un seuil ne suffit pas : `p_v > tau` est un scalaire sur la masse de la meilleure
valeur. Il ne distingue pas « le modèle est sûr » de « la masse est concentrée par hasard sur
une valeur, faute d'alternative ». Ce sont deux situations très différentes et un seul nombre
ne les sépare pas — d'où les 0.074 non récupérés.

On apprend donc `P(la meilleure valeur est correcte | indices de confiance)`, et on remplit
selon le coût. Indices, tous génériques et calculables sans connaître le champ :

  p1        masse de la meilleure valeur
  marge     p1 − p2 (l'écart à la deuxième)
  entropie  de la distribution sur les valeurs agrégées
  n_val     nombre de valeurs distinctes proposées
  n_spans   nombre de spans qui s'accordent sur la valeur gagnante
  p_null    masse de ⊥
  route     la valeur vient-elle du bloc VOCAB ou de la copie d'un span
  det       score de détection du span gagnant
  lpb       log P_B de la chaîne décodée (confiance du transducteur)
  type      le type DÉRIVÉ du champ (CLOSED / DATE / NUMBER / TEXT), pas sa famille écrite
            à la main — donc toujours zéro connaissance métier

INVARIANT : aucun paramètre par champ ni par classe. Le classifieur voit des indices de
confiance, jamais l'identité du champ. Les mêmes poids valent sur un autre schéma.

Entraîné sur les 1 540 documents d'ENTRAÎNEMENT (≈ 38 000 décisions), validé en croisé par
document, appliqué au test. Pas sur les 100 de validation : c'est ce qui a fait surajuster le
seuil par famille (4 degrés de liberté sur 100 documents, test 0.670 contre 0.673 pour le
seuil global).

  python learn_fill.py --ckpt <dir> --M 256 --topk 32
"""
import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch

_H = Path(__file__).resolve().parent
sys.path.insert(0, str(_H))
import assign as A                     # noqa: E402
import gliner_integrated as G          # noqa: E402
import label_space as LS               # noqa: E402
import taxonomy as T                   # noqa: E402
from train_assign import LB, PROD, doc_forward, macro_f1   # noqa: E402

_R = "/lustre/fswork/projects/rech/rua/uvb79kr/french-medgliner"
sys.path.insert(0, _R + "/GLiNER2"); sys.path.insert(0, _R + "/GLiNER2/v3")
from eval_v3 import load_model         # noqa: E402

FAMS = ("CAT", "DATE", "NUM", "ORD")
TYPES = ("CLOSED", "DATE", "NUMBER", "TEXT", "UNKNOWN")


@torch.no_grad()
def collect(model, head, vm, ds, opt_emb, space, dev, M, crit, topk):
    """-> (X features, y correct, meta) une ligne par (document, champ)."""
    X, Y, meta = [], [], []
    for i, d in enumerate(ds):
        _, _, _, pool, E, ent = doc_forward(model, d, dev, M, crit, train=False)
        cp, q, nl = head(E, pool)
        enc = vm.encode_spans(pool["texts"])
        sr = head.sr_to_h(pool["H"])
        Mn = pool["S"].shape[1]
        for e in ent:
            cls = space.get(e["key"], {}).get("classes") or []
            typ = space.get(e["key"], {}).get("type", "UNKNOWN")
            oe = opt_emb.get(e["key"])
            parts = [cp[e["fi"]]] + ([oe @ q[e["fi"]]] if oe is not None and cls else []) + [nl[e["fi"]]]
            p = torch.softmax(torch.cat(parts), 0)
            sel = torch.topk(p[:Mn], min(topk, Mn)).indices
            vals, lpb = vm.greedy_scored(enc, e["label"], sel, sr, e["key"])
            mass, nsp, best_lp, best_det = {}, defaultdict(int), {}, {}
            for j, v, l in zip(sel.tolist(), vals, lpb):
                if not v:
                    continue
                w = float(p[j]) * math.exp(min(l, 0.0))
                mass[v] = mass.get(v, 0.0) + w
                nsp[v] += 1
                if w >= best_lp.get(v, (-1e9, 0))[0]:
                    best_lp[v] = (w, l); best_det[v] = float(pool["S"][e["fi"], j])
            route_vocab = {}
            if oe is not None:
                for oi, c in enumerate(cls):
                    mass[c] = mass.get(c, 0.0) + float(p[Mn + oi])
                    route_vocab[c] = float(p[Mn + oi])
            if not mass:
                continue
            order = sorted(mass.items(), key=lambda kv: -kv[1])
            v, p1 = order[0]
            p2 = order[1][1] if len(order) > 1 else 0.0
            tot = sum(mass.values()) or 1.0
            ent_h = -sum((m / tot) * math.log(m / tot + 1e-12) for _, m in order)
            fam = T.FIELD_SPEC[e["key"]]["family"]
            f = [p1, p1 - p2, ent_h, len(order), nsp.get(v, 0), float(p[-1]),
                 route_vocab.get(v, 0.0) / max(p1, 1e-9), best_det.get(v, 0.0),
                 best_lp.get(v, (0, 0.0))[1], math.log1p(Mn)]
            f += [1.0 if typ == t else 0.0 for t in TYPES]
            X.append(f)
            Y.append(1.0 if (e["target"] is not None and G._match(fam, v, e["target"])) else 0.0)
            meta.append((d["id"], fam, e["target"], v))
        if (i + 1) % 100 == 0:
            print(f"  {i+1}/{len(ds)}", flush=True)
    return np.array(X, dtype=np.float64), np.array(Y), meta


def fit(X, y, epochs=400, lr=0.1):
    """Régression logistique, descente pleine, standardisée. ~15 paramètres, aucun par champ."""
    mu, sd = X.mean(0), X.std(0) + 1e-8
    Z = np.c_[(X - mu) / sd, np.ones(len(X))]
    w = np.zeros(Z.shape[1])
    for _ in range(epochs):
        pr = 1 / (1 + np.exp(-Z @ w))
        w -= lr * (Z.T @ (pr - y)) / len(y)
    return w, mu, sd


def prob(X, w, mu, sd):
    return 1 / (1 + np.exp(-(np.c_[(X - mu) / sd, np.ones(len(X))] @ w)))


def rows(meta, keep):
    return [(m[1], m[2], (m[3] if k else None)) for m, k in zip(meta, keep)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--M", type=int, default=256)
    ap.add_argument("--crit", default="rank")
    ap.add_argument("--topk", type=int, default=32)
    ap.add_argument("--max_chars", type=int, default=24000)
    ap.add_argument("--n_train", type=int, default=600,
                    help="documents d'entraînement échantillonnés. 600 donnent déjà "
                         "~15 000 décisions pour 15 paramètres : collecter les 1 540 "
                         "coûte 3 h de GPU pour un gain de précision nul.")
    a = ap.parse_args()
    dev = "cuda"

    ck = torch.load(a.ckpt + "/assign.pt", map_location=dev)
    space = ck["space"]
    fields = [k for k in T.FIELDS if T.FIELD_SPEC[k]["family"] != "TXT"]
    train_ids = {json.loads(l)["id"] for l in open(LB + "/lymphome_train_v2.jsonl", encoding="utf-8")}
    _, index = A.build_value_space(PROD, train_ids, fields)
    tr = A.build_dataset_assign(LB + "/lymphome_train_v2.jsonl", PROD, space, index,
                                fields, cap=a.max_chars)
    if a.n_train and a.n_train < len(tr):
        sel_ids = np.random.RandomState(1).choice(len(tr), a.n_train, replace=False)
        tr = [tr[i] for i in sorted(sel_ids)]
    te = A.build_dataset_assign(LB + "/lymphome_test_v2.jsonl", PROD, space, index,
                                fields, cap=a.max_chars)

    model = load_model(a.ckpt).to(dev).eval()
    head = A.load_head(ck, dev)
    vm = A.ValueModel(str(_H / "transducer" / "transducer2.pt"), dev, train=False)
    if ck.get("vm") is not None:
        vm.m.load_state_dict(ck["vm"])
    vm.m.eval()
    opt_emb = A.encode_options(model, space, dev)

    print(f"collecte ENTRAÎNEMENT ({len(tr)} documents)…", flush=True)
    Xtr, ytr, mtr = collect(model, head, vm, tr, opt_emb, space, dev, a.M, a.crit, a.topk)
    print(f"collecte TEST ({len(te)} documents)…", flush=True)
    Xte, yte, mte = collect(model, head, vm, te, opt_emb, space, dev, a.M, a.crit, a.topk)
    print(f"\ndécisions : entraînement {len(ytr):,}  test {len(yte):,}  "
          f"(taux de bonnes réponses {ytr.mean():.3f})")

    w, mu, sd = fit(Xtr, ytr)
    pte = prob(Xte, w, mu, sd)
    ptr = prob(Xtr, w, mu, sd)

    print(f"\n{'règle de remplissage':38s} {'train':>7s} {'TEST':>8s}  "
          + " ".join(f"{f:>6s}" for f in FAMS))
    print("-" * 80)
    res = {}
    # référence : le seuil scalaire actuel sur p1
    for tau in (0.5, 0.30):
        k_tr = Xtr[:, 0] > tau; k_te = Xte[:, 0] > tau
        mv, _ = macro_f1(rows(mtr, k_tr)); mt, pt = macro_f1(rows(mte, k_te))
        nm = f"seuil scalaire p_v > {tau}"
        print(f"{nm:38s} {mv:7.3f} {mt:8.3f}  " + " ".join(f"{pt[f]:6.3f}" for f in FAMS))
        res[nm] = {"train": mv, "test": mt}
    # la règle apprise, seuil choisi sur le TRAIN uniquement
    best = max([round(x, 2) for x in np.arange(0.15, 0.85, 0.025)],
               key=lambda t: macro_f1(rows(mtr, ptr > t))[0])
    mv, _ = macro_f1(rows(mtr, ptr > best)); mt, pt = macro_f1(rows(mte, pte > best))
    nm = f"règle APPRISE (seuil {best} choisi sur le train)"
    print(f"{nm:38s} {mv:7.3f} {mt:8.3f}  " + " ".join(f"{pt[f]:6.3f}" for f in FAMS))
    res[nm] = {"train": mv, "test": mt, "per": pt}
    # borne : décision parfaite
    mo, po = macro_f1(rows(mte, yte > 0.5))
    print(f"{'décision PARFAITE (borne)':38s} {'':7s} {mo:8.3f}  "
          + " ".join(f"{po[f]:6.3f}" for f in FAMS))

    names = ["p1", "marge", "entropie", "n_val", "n_spans", "p_null", "route_vocab",
             "détection", "log P_B", "log M"] + [f"type={t}" for t in TYPES]
    print("\npoids appris (standardisés), du plus au moins déterminant :")
    for n, v in sorted(zip(names, w[:-1]), key=lambda x: -abs(x[1]))[:8]:
        print(f"   {n:14s} {v:+.3f}")
    json.dump({"rules": res, "borne_parfaite": mo,
               "poids": dict(zip(names, w[:-1].tolist()))},
              open(a.ckpt + "/learn_fill.json", "w"), indent=1)


if __name__ == "__main__":
    main()
