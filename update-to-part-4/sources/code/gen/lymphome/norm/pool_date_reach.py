"""Les cibles DATE manquées sont-elles ATTEIGNABLES depuis le pool, et à quel M ?

Le diagnostic (2026-08-13) donne DATE comme seule famille avec de l'INATTEIGNABLE
(8,3 % base / 9,5 % large), et l'audit hors-ligne dit que 57 % des cibles hors-span sont
écrites AILLEURS dans le document. Question qui décide du prochain chantier :

  agrandir/réorienter le POOL récupérerait-il ces dates, ou sont-elles hors de portée
  de tout mécanisme de copie (dates calculées) ?

Pour chaque cible DATE, on regarde si UN span du pool contient la date cible (dans un
format quelconque), à plusieurs tailles de pool. Si le taux monte avec M, le pool est le
goulot et l'élargir est le levier ; s'il plafonne, le résidu est arithmétique et aucun
pool ne le résoudra.

  python pool_date_reach.py --ckpt <dir> [--Ms 256,1024,4096] [--limit N]
"""
import argparse
import json
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path

import torch

_H = Path(__file__).resolve().parent
sys.path.insert(0, str(_H))
import assign as A                     # noqa: E402
import taxonomy as T                   # noqa: E402
from train_assign import LB, PROD, doc_forward   # noqa: E402

_R = "/lustre/fswork/projects/rech/rua/uvb79kr/french-medgliner"
sys.path.insert(0, _R + "/GLiNER2"); sys.path.insert(0, _R + "/GLiNER2/v3")
from eval_v3 import load_model         # noqa: E402

MONTHS = ("janvier février mars avril mai juin juillet août septembre octobre "
          "novembre décembre").split()
M2N = {m: i + 1 for i, m in enumerate(MONTHS)}
M2N.update({m.replace("é", "e").replace("û", "u"): v for m, v in list(M2N.items())})
_ALT = "|".join(sorted({re.escape(m) for m in M2N}, key=len, reverse=True))
_ISO = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")
_NUM = re.compile(r"\b(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})\b")
_TXT = re.compile(rf"\b(\d{{1,2}})(?:er)?\s+({_ALT})\s+(\d{{4}})\b", re.I)


def dates_of(txt):
    out = set()
    for y, m, d in _ISO.findall(txt):
        try: out.add(date(int(y), int(m), int(d)))
        except ValueError: pass
    for d, m, y in _NUM.findall(txt):
        try: out.add(date(int(y), int(m), int(d)))
        except ValueError: pass
    for d, m, y in _TXT.findall(txt):
        try: out.add(date(int(y), M2N[m.lower()], int(d)))
        except (ValueError, KeyError): pass
    return out


def parse_target(v):
    m = _ISO.match(str(v).strip()[:10])
    if not m:
        return None
    try:
        return date(*(int(g) for g in m.groups()))
    except ValueError:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--Ms", default="256,1024,4096")
    ap.add_argument("--crit", default="rank")
    ap.add_argument("--max_chars", type=int, default=45000)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    dev = "cuda"
    Ms = [int(x) for x in a.Ms.split(",")]

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
    print(f"test={len(ds)} documents  Ms={Ms}", flush=True)

    st = {M: Counter() for M in Ms}
    with torch.no_grad():
        for i, d in enumerate(ds):
            tgts = [(e, parse_target(e["target"])) for e in d["entries"]
                    if T.FIELD_SPEC[e["key"]]["family"] == "DATE" and e["target"] is not None]
            tgts = [(e, t) for e, t in tgts if t is not None]
            if not tgts:
                continue
            ddoc = dates_of(d["text"])
            for M in Ms:
                _, _, _, pool, _, _ = doc_forward(model, d, dev, M, a.crit, train=False)
                pooled = [dates_of(t) for t in pool["texts"]]
                union = set().union(*pooled) if pooled else set()
                for e, t in tgts:
                    st[M]["total"] += 1
                    if t in union:
                        st[M]["dans_le_pool"] += 1
                    elif t in ddoc:
                        st[M]["dans_le_doc_hors_pool"] += 1
                    else:
                        st[M]["absente_du_doc"] += 1
            if (i + 1) % 50 == 0:
                print(f"  {i+1}/{len(ds)}", flush=True)

    print("\n=== ATTEIGNABILITÉ DES CIBLES DATE PAR LE POOL ===")
    print(f"{'M':>6s} {'dans le pool':>14s} {'dans le doc, hors pool':>24s} {'absente du doc':>16s}")
    for M in Ms:
        c = st[M]; n = max(c["total"], 1)
        print(f"{M:6d} {100*c['dans_le_pool']/n:13.1f}% {100*c['dans_le_doc_hors_pool']/n:23.1f}% "
              f"{100*c['absente_du_doc']/n:15.1f}%")
    print("\nlecture : si « dans le pool » monte avec M, le pool est le goulot ; s'il "
          "plafonne, le résidu est ailleurs (dates calculées, non écrites).")


if __name__ == "__main__":
    main()
