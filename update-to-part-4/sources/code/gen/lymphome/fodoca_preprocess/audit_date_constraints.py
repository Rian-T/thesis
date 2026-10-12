"""Audit du silver eCRF avec les contraintes temporelles de fodoca (`date_after`).

fodoca (MIT, Éric de la Clergerie, `vendor/`) définit dans `fields.yml` un ordre partiel
entre champs dates (diagnostic après naissance, fin de ligne après début, …). Notre gold
est un annotateur LLM sans auto-accord mesuré et DATE est la famille la plus faible
(0.684) : ce script mesure combien d'annotations violent l'ordre, par contrainte, et
écrit un fichier de flags par (document, champ) pour nettoyer le train au prochain
retrain. AUCUNE règle n'entre à l'inférence.

Correspondance de schéma : fodoca `1st_line_*`/`2nd_line_*` = nous `first_line_*`/`second_line_*`.

  python audit_date_constraints.py [--prod <jsonl>] [--out <flags.jsonl>]
"""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

_H = Path(__file__).resolve().parent
sys.path.insert(0, str(_H / "vendor"))
from date_constraints import parse_iso_date, transitive_predecessors  # noqa: E402

PROD = "/lustre/fswork/projects/rech/rua/uvb79kr/biomed-fr-v4/lymphome_v4/outputs/prod_20260527_121452.jsonl"
FUTURE = re.compile(r"prévu|programmé|envisagé|fixé|planifié|planification", re.I)


def our_name(n):
    return n.replace("1st_line", "first_line").replace("2nd_line", "second_line")


def load_date_after(fields_yml):
    """Parse minimal du yaml (name/date_after par bloc) — évite la dépendance pyyaml."""
    out, name = {}, None
    for line in Path(fields_yml).read_text(encoding="utf-8").splitlines():
        m = re.match(r"\s*name:\s*(\S+)", line)
        if m:
            name = our_name(m.group(1))
        m = re.match(r"\s*date_after:\s*(\S+)", line)
        if m and name:
            out[name] = our_name(m.group(1))
    return out


def field_dates(ann):
    """Première valeur datée par champ + texte du span (pour le flag « prévu »)."""
    out = {}
    for k, v in (ann or {}).items():
        for it in ([v] if isinstance(v, dict) else v) if v else []:
            if isinstance(it, dict) and it.get("value") not in (None, ""):
                d = parse_iso_date(it["value"])
                if d is not None:
                    out[k] = (d, str(it.get("span") or ""))
                break
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prod", default=PROD)
    ap.add_argument("--fields_yml", default=str(_H / "vendor" / "fields.yml"))
    ap.add_argument("--out", default="")
    a = ap.parse_args()

    dam = load_date_after(a.fields_yml)
    print(f"contraintes date_after (schéma aligné) : {len(dam)}")

    viol = Counter()          # (champ, prédécesseur) -> violations strictes
    viol_eq = Counter()       # égalités (informatif : after strict ou pas ?)
    tot = Counter()           # (champ, prédécesseur) -> paires comparables
    future_hits = 0
    flags, ndocs = [], 0

    for line in open(a.prod, encoding="utf-8"):
        r = json.loads(line)
        ndocs += 1
        did = f"lym_{r['sample_index']}"
        fd = field_dates(r.get("annotation"))
        for f in dam:
            if f not in fd:
                continue
            df, span = fd[f]
            for p in transitive_predecessors(f, dam):
                if p not in fd:
                    continue
                dp, _ = fd[p]
                tot[(f, p)] += 1
                if df < dp:
                    viol[(f, p)] += 1
                    flags.append({"id": did, "field": f, "value": str(df),
                                  "predecessor": p, "pred_value": str(dp),
                                  "future_marker": bool(FUTURE.search(span)),
                                  "kind": "order_violation"})
                    if FUTURE.search(span):
                        future_hits += 1
                elif df == dp:
                    viol_eq[(f, p)] += 1

    nv = sum(viol.values())
    nt = sum(tot.values())
    print(f"\ndocs: {ndocs}   paires (champ, prédécesseur) comparables: {nt}")
    print(f"VIOLATIONS strictes (date < prédécesseur): {nv} ({100*nv/max(nt,1):.2f} %)  "
          f"dont marqueur futur (« prévu… ») dans le span: {future_hits}")
    print(f"égalités de date: {sum(viol_eq.values())} (probablement licites)\n")
    print("par contrainte (violations/comparables) :")
    for (f, p), n in viol.most_common(20):
        print(f"  {f}  <  {p} : {n}/{tot[(f, p)]}")
    docs_touched = len({fl["id"] for fl in flags})
    print(f"\ndocuments touchés par ≥1 violation : {docs_touched}/{ndocs} "
          f"({100*docs_touched/max(ndocs,1):.1f} %)")

    if a.out:
        with open(a.out, "w", encoding="utf-8") as w:
            for fl in flags:
                w.write(json.dumps(fl, ensure_ascii=False) + "\n")
        print(f"→ flags : {a.out}")


if __name__ == "__main__":
    main()
