"""Balayage de max_chars sur la VALIDATION (100 docs, split seed 0 — jamais le test).

Question : que vaut le modèle 3ep au-delà du cap 24 000 avec lequel il a été entraîné ?
Contexte mesuré (2026-08-12) : le schéma des 89 champs coûte 2 280 tokens, donc le cap
24 000 sature déjà les 8 192 positions de ModernBERT ; tout cap supérieur repose sur
l'extrapolation RoPE (les couches locales fenêtrées ne changent pas, seules les couches
globales extrapolent). 39 % des documents sont tronqués à 24 000. Ce script tranche
empiriquement : si le macro monte avec le cap, la troncature coûtait plus cher que
l'extrapolation ne dégrade.

  python eval_val_cap.py --ckpt <dir> --caps 24000,32000,45000
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch

_H = Path(__file__).resolve().parent
sys.path.insert(0, str(_H))
import assign as A                     # noqa: E402
import taxonomy as T                   # noqa: E402
from train_assign import LB, PROD, evaluate   # noqa: E402

_R = "/lustre/fswork/projects/rech/rua/uvb79kr/french-medgliner"
sys.path.insert(0, _R + "/GLiNER2"); sys.path.insert(0, _R + "/GLiNER2/v3")
from eval_v3 import load_model         # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--caps", default="24000,32000,45000")
    ap.add_argument("--M", type=int, default=1024)
    ap.add_argument("--crit", default="rank")
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    dev = "cuda"

    ck = torch.load(a.ckpt + "/assign.pt", map_location=dev)
    space = ck["space"]
    fields = [k for k in T.FIELDS if T.FIELD_SPEC[k]["family"] != "TXT"]
    train_ids = {json.loads(l)["id"] for l in open(LB + "/lymphome_train_v2.jsonl", encoding="utf-8")}
    _, index = A.build_value_space(PROD, train_ids, fields)

    model = load_model(a.ckpt).to(dev).eval()
    head = A.load_head(ck, dev)
    vm = A.ValueModel(str(_H / "transducer" / "transducer2.pt"), dev, train=False)
    vm.m.load_state_dict(ck["vm"]); vm.m.eval()
    opt_emb = A.encode_options(model, space, dev)

    results = {}
    for cap in [int(c) for c in a.caps.split(",")]:
        full = A.build_dataset_assign(LB + "/lymphome_train_v2.jsonl", PROD, space, index,
                                      fields, cap=cap)
        _ids = sorted(d["id"] for d in full)
        val_ids = set(np.random.RandomState(0).choice(
            _ids, min(100, len(_ids)), replace=False).tolist())
        val = [d for d in full if d["id"] in val_ids]
        ncut = sum(1 for d in val if len(d.get("text", "")) >= cap)
        m, per, probes = evaluate(model, head, vm, val, opt_emb, space, dev, a.M, a.crit)
        model.eval(); head.eval(); vm.m.eval()   # evaluate() remet en .train()
        results[cap] = {"macro": m, "per_family": per, "n_val": len(val), "n_at_cap": ncut}
        print(f"cap={cap:>6}  macro={m:.4f}  " +
              "  ".join(f"{f}={per.get(f, float('nan')):.3f}" for f in ("CAT", "DATE", "NUM", "ORD")),
              flush=True)

    if a.out:
        Path(a.out).write_text(json.dumps(results, indent=2))
        print(f"→ {a.out}")


if __name__ == "__main__":
    main()
