"""Le contrôle décisif, refait là où il peut produire un résultat.

Je l'avais mesuré au rappel@64 : la tête d'affectation classe-t-elle mieux que le score de
détection brut ? Réponse « +0.001 ». Mais à @64 la détection est DÉJÀ à 0.984 (CAT), 0.953
(NUM), 0.996 (ORD) — il n'y a pas deux points à prendre. **Un test qui ne peut pas produire
de résultat positif n'est pas un contrôle négatif, c'est un test non informatif.**

Or la décision se prend au rang 1. Et la décomposition d'erreurs le disait déjà sous un autre
nom : « cible joignable mais pas en tête » vaut 6 à 18 % des cibles selon la famille, soit
~12 % en moyenne. C'est ça, le budget réel de la sélection — pas 0.001.

On compare donc les deux classements du MÊME pool, avec le MÊME transducteur, sur :
  rappel@1   la cible est-elle produite par le span le mieux classé ?
  rappel@4   ... par l'un des 4 meilleurs ?
  MRR        1 / rang du premier span qui produit la cible (0 si aucun dans les 64)

Trois classements, pour séparer ce qui vient de la tête de ce qui vient du détecteur :
  P_A          la distribution complète de la tête (copie seule, renormalisée)
  détection    le score bilinéaire natif S[champ, span]
  P_A sans S   la tête PRIVÉE de son ancrage sur la détection (beta*S retiré du logit) —
               c'est ce que la tête a appris EN PROPRE, et c'est la seule façon de savoir si
               elle a appris quoi que ce soit ou si elle recopie son initialisation.

  python control_rank.py --ckpt <dir> --M 256
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
from train_assign import LB, PROD, doc_forward   # noqa: E402

_R = "/lustre/fswork/projects/rech/rua/uvb79kr/french-medgliner"
sys.path.insert(0, _R + "/GLiNER2"); sys.path.insert(0, _R + "/GLiNER2/v3")
from eval_v3 import load_model         # noqa: E402

FAMS = ("CAT", "DATE", "NUM", "ORD")
K = 64


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--M", type=int, default=256)
    ap.add_argument("--crit", default="rank")
    ap.add_argument("--max_chars", type=int, default=24000)
    ap.add_argument("--limit", type=int, default=200)
    a = ap.parse_args()
    dev = "cuda"

    ck = torch.load(a.ckpt + "/assign.pt", map_location=dev)
    space = ck["space"]
    fields = [k for k in T.FIELDS if T.FIELD_SPEC[k]["family"] != "TXT"]
    train_ids = {json.loads(l)["id"] for l in open(LB + "/lymphome_train_v2.jsonl", encoding="utf-8")}
    _, index = A.build_value_space(PROD, train_ids, fields)
    ds = A.build_dataset_assign(LB + "/lymphome_test_v2.jsonl", PROD, space, index,
                                fields, cap=a.max_chars)[:a.limit]

    model = load_model(a.ckpt).to(dev).eval()
    head = A.load_head(ck, dev)
    vm = A.ValueModel(str(_H / "transducer" / "transducer2.pt"), dev, train=False)
    if ck.get("vm") is not None:
        vm.m.load_state_dict(ck["vm"])
    vm.m.eval()
    print(f"test={len(ds)} documents  M={a.M}  beta={float(head.beta):+.3f}", flush=True)

    # stat[classement][famille] = [hit@1, hit@4, somme des 1/rang, n]
    stat = {r: defaultdict(lambda: [0, 0, 0.0, 0]) for r in ("P_A", "détection", "P_A sans S")}
    with torch.no_grad():
        for i, d in enumerate(ds):
            _, _, _, pool, E, ent = doc_forward(model, d, dev, a.M, a.crit, train=False)
            cp, _, _ = head(E, pool)
            enc = vm.encode_spans(pool["texts"])
            sr = head.sr_to_h(pool["H"])
            M = pool["S"].shape[1]
            for e in ent:
                if e["target"] is None:
                    continue
                fam = T.FIELD_SPEC[e["key"]]["family"]
                orders = {
                    "P_A": cp[e["fi"]],
                    "détection": pool["S"][e["fi"]],
                    "P_A sans S": cp[e["fi"]] - head.beta * pool["S"][e["fi"]],
                }
                for name, sc in orders.items():
                    top = torch.topk(sc, min(K, M)).indices
                    vals = vm.greedy_many(enc, e["label"], top, sr, e["key"])
                    r = next((j for j, v in enumerate(vals)
                              if G._match(fam, v, e["target"])), None)
                    s = stat[name][fam]
                    s[3] += 1
                    if r is not None:
                        s[0] += (r == 0); s[1] += (r < 4); s[2] += 1.0 / (r + 1)
            if (i + 1) % 50 == 0:
                print(f"  {i+1}/{len(ds)}", flush=True)

    for metric, idx in (("rappel@1", 0), ("rappel@4", 1), ("MRR", 2)):
        print(f"\n=== {metric} ===")
        print(f"{'classement':14s} " + " ".join(f"{f:>8s}" for f in FAMS) + f" {'moyenne':>9s}")
        base = None
        for name in ("détection", "P_A", "P_A sans S"):
            row = [(stat[name][f][idx] / max(stat[name][f][3], 1)) for f in FAMS]
            mean = float(np.mean(row))
            tag = "" if base is None else f"   ({mean - base:+.3f})"
            if base is None:
                base = mean
            print(f"{name:14s} " + " ".join(f"{v:8.3f}" for v in row) + f" {mean:9.3f}{tag}")
    print("\nLecture : si « P_A » ne dépasse pas « détection » au rang 1, la tête n'a rien appris")
    print("sur OÙ chercher. Si « P_A sans S » s'effondre, elle n'a fait que recopier son ancrage.")
    json.dump({m: {r: {f: stat[r][f][i] / max(stat[r][f][3], 1) for f in FAMS}
                   for r in stat} for m, i in (("r@1", 0), ("r@4", 1), ("mrr", 2))},
              open(a.ckpt + "/control_rank.json", "w"), indent=1)


if __name__ == "__main__":
    main()
