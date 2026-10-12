"""Audit des paires (span, valeur) du transducteur avec les parseurs de fodoca.

Deux questions, PREPROCESS uniquement (les règles n'entrent pas à l'inférence) :
  1. NUM : la valeur cible est-elle dans une unité COHÉRENTE avec le span ? fodoca
     `measures.py` parse « 1,76 m » et convertit ; si la cible attend une conversion
     (176 vs « 1,76 m »), le transducteur doit l'apprendre — mesurer combien de paires
     sont dans ce cas, et combien sont incohérentes (ni la valeur brute ni convertie).
  2. DATE : la cible est-elle reconstructible du span par les regex dates FR de fodoca
     (complètes ET partielles) ? Les paires où NON = le transducteur doit inventer
     (probablement via l'ancre/sd) — les compter, c'est la borne de ce qu'un parseur
     apporterait en augmentation.

  python audit_transducer_pairs.py
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

_H = Path(__file__).resolve().parent
sys.path.insert(0, str(_H / "vendor"))
import measures as FM                                    # noqa: E402

PAIRS = Path(__file__).resolve().parent.parent / "norm" / "transducer" / "pairs.json"

_NUM_IN = re.compile(r"(\d+(?:[.,]\d+)?)\s*(m|cm|mm|kg|g|mg|ui/l|u/l|iu/l)?\b", re.I)
_DATE_FULL_N = re.compile(r"(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})")
MONTHS = "janvier|février|fevrier|mars|avril|mai|juin|juillet|août|aout|septembre|octobre|novembre|décembre|decembre"
_DATE_FULL_T = re.compile(rf"(\d{{1,2}})(?:er)?\s+({MONTHS})\s+(\d{{4}})", re.I)
_DATE_PART_N = re.compile(r"\b(\d{1,2})[/\-.](\d{4})\b")
_DATE_PART_T = re.compile(rf"\b({MONTHS})\s+(\d{{4}})\b", re.I)
_ISO = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")
M2N = {m: i + 1 for i, m in enumerate(
    "janvier février mars avril mai juin juillet août septembre octobre novembre décembre".split())}
M2N.update({k.replace("é", "e").replace("û", "u"): v for k, v in list(M2N.items())})


def dates_in(txt):
    out = set()
    for y, m, d in _ISO.findall(txt):
        out.add(f"{y}-{m}-{d}")
    for d, m, y in _DATE_FULL_N.findall(txt):
        out.add(f"{y}-{int(m):02d}-{int(d):02d}")
    for d, m, y in _DATE_FULL_T.findall(txt):
        out.add(f"{y}-{M2N[m.lower()]:02d}-{int(d):02d}")
    # partielles (les cibles du gold peuvent être « 2017-11 »)
    for m, y in _DATE_PART_N.findall(txt):
        out.add(f"{y}-{int(m):02d}")
    for m, y in _DATE_PART_T.findall(txt):
        out.add(f"{y}-{M2N[m.lower()]:02d}")
    return out


def nums_in(txt):
    vals = set()
    for n, u in _NUM_IN.findall(txt):
        x = float(n.replace(",", "."))
        vals.add(x)
        cu = FM.canonicalize_unit(u) if u else None
        if cu:
            grp = FM._UNIT_TO_GROUP.get(cu)
            if grp:
                base = x * FM._UNIT_GROUPS[grp][cu]
                vals.add(base)
                for tu, f in FM._UNIT_GROUPS[grp].items():
                    vals.add(base / f)
    return vals


def close(a, b, tol=0.005):
    return abs(a - b) <= tol * max(abs(a), abs(b), 1e-9)


def main():
    pairs = json.load(open(PAIRS, encoding="utf-8"))
    st = Counter()
    ex = {"num_conv": [], "num_abs": [], "date_abs": []}
    for p in pairs:
        fam, span, val = p["fam"], p["span"], str(p["value"])
        if fam == "NUM":
            try:
                v = float(val.replace(",", "."))
            except ValueError:
                st["num_nonfloat"] += 1; continue
            raw = {float(n.replace(",", ".")) for n, _ in _NUM_IN.findall(span)}
            st["num"] += 1
            if any(close(v, r) for r in raw):
                st["num_direct"] += 1
            elif any(close(v, r) for r in nums_in(span)):
                st["num_converti"] += 1
                if len(ex["num_conv"]) < 5: ex["num_conv"].append((span[:70], val))
            else:
                st["num_absent"] += 1
                if len(ex["num_abs"]) < 5: ex["num_abs"].append((span[:70], val))
        elif fam == "DATE":
            st["date"] += 1
            ds, dsd = dates_in(span), dates_in(p.get("sd") or "")
            if val in ds:
                st["date_dans_span"] += 1
            elif val in dsd:
                st["date_dans_sd"] += 1
            elif val[:7] in {d[:7] for d in ds | dsd}:
                st["date_mois_ok"] += 1
            else:
                st["date_absente"] += 1
                if len(ex["date_abs"]) < 5: ex["date_abs"].append((span[:70], val))
    n = st["num"]; d = st["date"]
    print(f"paires: {len(pairs)}  NUM={n}  DATE={d}\n")
    print(f"NUM  directes {st['num_direct']}/{n} ({100*st['num_direct']/n:.1f}%)  "
          f"CONVERSION D'UNITÉ requise {st['num_converti']} ({100*st['num_converti']/n:.1f}%)  "
          f"introuvables {st['num_absent']} ({100*st['num_absent']/n:.1f}%)")
    print(f"DATE dans span {st['date_dans_span']}/{d} ({100*st['date_dans_span']/d:.1f}%)  "
          f"dans en-tête sd {st['date_dans_sd']} ({100*st['date_dans_sd']/d:.1f}%)  "
          f"mois seul ok {st['date_mois_ok']} ({100*st['date_mois_ok']/d:.1f}%)  "
          f"ABSENTES {st['date_absente']} ({100*st['date_absente']/d:.1f}%)")
    for k, v in ex.items():
        if v:
            print(f"\nexemples {k}:")
            for s, t in v: print(f"  «{s}» -> {t}")


if __name__ == "__main__":
    main()
