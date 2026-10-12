"""Les cibles DATE hors du pool sont-elles CALCULABLES ? (chiffrage du prochain levier)

Le diagnostic de saturation (2026-08-13) donne DATE comme seule famille avec de
l'INATTEIGNABLE (8,3 % base / 9,5 % large) : la valeur n'est dans AUCUN span, donc aucun
mécanisme de copie ne peut la produire. Avant d'ouvrir un chantier « arithmétique de
dates » dans le transducteur, il faut savoir combien de ces cibles sont effectivement
DÉRIVABLES d'une date présente dans le document plus un décalage.

Pour chaque paire (span, valeur) DATE dont la valeur n'est pas dans le span :
  - la valeur est-elle une date du DOCUMENT (autre endroit) ?              -> hors_span_mais_dans_doc
  - est-elle à un décalage RÉGULIER d'une date du document ?               -> calculable_offset
    (multiples de 7, de 21/28 = cycles de chimiothérapie, ±1 mois, ±1 an)
  - sinon                                                                  -> non_derivable

Un chiffre élevé de `calculable_offset` justifie le chantier ; un `non_derivable`
dominant dirait que ces cibles sont hors de portée de tout mécanisme local.

  python audit_date_arith.py
"""
import json
import re
import sys
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

_H = Path(__file__).resolve().parent
DATA = _H.parent.parent.parent / "capstone_ecrf" / "research" / "lymphome" / "data"
PROD = "/lustre/fswork/projects/rech/rua/uvb79kr/biomed-fr-v4/lymphome_v4/outputs/prod_20260527_121452.jsonl"

MONTHS = ("janvier février mars avril mai juin juillet août septembre octobre "
          "novembre décembre").split()
M2N = {m: i + 1 for i, m in enumerate(MONTHS)}
M2N.update({m.replace("é", "e").replace("û", "u"): v for m, v in list(M2N.items())})
_ALT = "|".join(sorted({re.escape(m) for m in M2N}, key=len, reverse=True))
_ISO = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")
_NUM = re.compile(r"\b(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})\b")
_TXT = re.compile(rf"\b(\d{{1,2}})(?:er)?\s+({_ALT})\s+(\d{{4}})\b", re.I)

# décalages « cliniquement plausibles » : cycles de chimiothérapie, semaines, mois, ans
OFFSETS = sorted({7, 14, 21, 28, 35, 42, 56, 63, 84, 90, 91, 30, 31, 60, 180, 365, 366}
                 | {21 * k for k in range(1, 9)} | {28 * k for k in range(1, 9)})


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
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


def main():
    texts = {}
    for split in ("v5_val", "v5_test"):
        for line in open(DATA / f"{split}.jsonl", encoding="utf-8"):
            r = json.loads(line)
            texts[r["id"]] = r["text"]
    print(f"documents chargés : {len(texts)}")

    st = Counter()
    off_hist = Counter()
    ex = []
    for line in open(PROD, encoding="utf-8"):
        r = json.loads(line)
        did = f"lym_{r['sample_index']}"
        if did not in texts:
            continue
        doc = texts[did]
        ddoc = None
        for k, v in (r.get("annotation") or {}).items():
            for it in ([v] if isinstance(v, dict) else v) if v else []:
                if not isinstance(it, dict):
                    continue
                tgt = parse_target(it.get("value"))
                if tgt is None:
                    break
                span = str(it.get("span") or "")
                st["date_total"] += 1
                if tgt in dates_of(span):
                    st["dans_le_span"] += 1
                    break
                if ddoc is None:
                    ddoc = dates_of(doc)
                if tgt in ddoc:
                    st["hors_span_mais_dans_doc"] += 1
                    break
                hit = None
                for d0 in ddoc:
                    delta = abs((tgt - d0).days)
                    if delta in OFFSETS:
                        hit = delta; break
                if hit is not None:
                    st["calculable_offset"] += 1
                    off_hist[hit] += 1
                else:
                    st["non_derivable"] += 1
                    if len(ex) < 6:
                        ex.append((k, str(tgt), span[:60]))
                break

    n = st["date_total"]
    print(f"\ncibles DATE examinées : {n}")
    for k in ("dans_le_span", "hors_span_mais_dans_doc", "calculable_offset", "non_derivable"):
        print(f"  {k:26s} {st[k]:6d}  ({100*st[k]/max(n,1):5.1f} %)")
    hors = n - st["dans_le_span"]
    if hors:
        print(f"\nparmi les {hors} cibles HORS SPAN ({100*hors/n:.1f} % du total) :")
        for k in ("hors_span_mais_dans_doc", "calculable_offset", "non_derivable"):
            print(f"  {k:26s} {100*st[k]/hors:5.1f} %")
    print("\ndécalages les plus fréquents (jours) :",
          ", ".join(f"{d}j×{c}" for d, c in off_hist.most_common(8)))
    if ex:
        print("\nexemples non dérivables :")
        for k, t, s in ex:
            print(f"  {k[:38]:38s} -> {t}   span «{s}»")


if __name__ == "__main__":
    main()
