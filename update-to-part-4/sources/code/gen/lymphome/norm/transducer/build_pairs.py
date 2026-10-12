"""Construit les paires (span verbatim, valeur canonique) pour entraîner le transducteur.

Source : le champ `span` et le champ `value` que l'annotateur produit déjà pour chaque variable.
Split par DOCUMENT (jamais par paire) pour éviter toute fuite.

Sort aussi la barre à battre : le score de `taxonomy.normalize_target` sur les mêmes paires,
évalué dans son propre vocabulaire — c'est-à-dire généreusement.

  python build_pairs.py            # -> pairs.json + la barre de taxonomy.py
"""
import argparse
import collections
import json
import re
import random
import sys
from pathlib import Path

_H = Path(__file__).resolve().parent
sys.path.insert(0, str(_H.parent)); sys.path.insert(0, str(_H.parents[1]))
import taxonomy as T          # noqa: E402
from labels import LABELS     # noqa: E402

# NB : `\s` et non `\\s`. La version sur-échappée cherchait un ANTISLASH littéral suivi
# de « s » : elle ne matchait rien, et les trois bras de l'expérience d'ancre rendaient
# le même chiffre sans qu'aucune erreur ne soit levée.
HDR = re.compile(r"^\s*=+[^\n]*=+\s*$", re.M)

LB = "/lustre/fsn1/projects/rech/rua/uvb79kr/onto/medembed-outputs/lymphome"
PROD = "/lustre/fswork/projects/rech/rua/uvb79kr/biomed-fr-v4/lymphome_v4/outputs/prod_20260527_121452.jsonl"


def num_ok(p, g):
    try:
        return abs(float(p) - float(g)) / max(abs(float(g)), 1e-6) <= 0.10
    except (TypeError, ValueError):
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--calc_anchor", action="store_true",
                    help="l'ancre est l'en-tête le plus proche PRÉCÉDANT le span, calculé depuis "
                         "le seul texte — au lieu du `source_document` de l'annotateur. C'est ce "
                         "qui est disponible à l'inférence, et c'est le contrôle de non-fuite.")
    ap.add_argument("--ctxwin", type=int, default=0,
                    help="ancre GÉNÉRIQUE : les N caractères qui précèdent le span, sans aucune "
                         "hypothèse sur la structure du document. `--calc_anchor` suppose un "
                         "motif d'en-tête `=== ... ===` propre à CE corpus, produit par NOTRE "
                         "générateur : c'est du savoir spécifique au dataset, et le cahier des "
                         "charges l'interdit. Cette variante n'en suppose aucun. Si elle capte "
                         "l'essentiel du gain, l'idée « un span hérite du contexte qui le "
                         "précède » est légitime et transférable ; sinon il faut renoncer au "
                         "gain ou l'assumer comme une adaptation au corpus.")
    args = ap.parse_args()
    test_ids = {json.loads(l)["id"] for l in open(f"{LB}/lymphome_test_v2.jsonl", encoding="utf-8")}
    train_ids = {json.loads(l)["id"] for l in open(f"{LB}/lymphome_train_v2.jsonl", encoding="utf-8")}
    rows = []
    for line in open(PROD, encoding="utf-8"):
        r = json.loads(line); rid = f"lym_{r['sample_index']}"
        split = "test" if rid in test_ids else ("train" if rid in train_ids else None)
        if split is None:
            continue
        ann = r.get("annotation") or {}
        text = r.get("full_clinical_text", "")
        heads = [(m.start(), m.group().strip()) for m in HDR.finditer(text)] if args.calc_anchor else []
        for k in T.FIELDS:
            if T.FIELD_SPEC[k]["family"] == "TXT":
                continue
            v = ann.get(k)
            for it in ([v] if isinstance(v, dict) else (v or [])):
                if not isinstance(it, dict):
                    continue
                sp, val = it.get("span"), it.get("value")
                sd = it.get("source_document") or ""
                if args.ctxwin:
                    pos = text.find(str(sp)) if sp else -1
                    sd = text[max(0, pos - args.ctxwin):pos].replace("\n", " ") if pos > 0 else ""
                elif args.calc_anchor:
                    pos = text.find(str(sp)) if sp else -1
                    prev = [h for off, h in heads if off <= pos] if pos >= 0 else []
                    sd = prev[-1] if prev else ""
                if not sp or val in (None, ""):
                    continue
                # `source_document` est un SECOND POINTEUR dans le même texte : mesuré
                # identique verbatim à un en-tête « === … === » dans 99,96 % des cas. La
                # cible DATE est littéralement dans son span 6,4 % du temps, mais dans
                # l'en-tête de son document source 47,0 % du temps. On la transporte.
                rows.append({"split": split, "key": k, "label": LABELS[k]["label"],
                             "span": str(sp)[:300], "value": str(val),
                             "sd": str(sd)[:120],
                             "fam": T.FIELD_SPEC[k]["family"]})

    n_tr = sum(r["split"] == "train" for r in rows)
    print(f"paires : {len(rows):,}  train={n_tr:,}  test={len(rows)-n_tr:,}")

    per = collections.defaultdict(lambda: [0, 0])
    for r in rows:
        if r["split"] != "test":
            continue
        gold = T.normalize_target(r["key"], r["value"])
        pred = T.normalize_target(r["key"], r["span"])
        if gold is None:
            continue
        ok = num_ok(pred, gold) if r["fam"] == "NUM" else (pred == gold)
        per[r["fam"]][0] += ok; per[r["fam"]][1] += 1
    tot = [sum(x) for x in zip(*per.values())]
    print("\n=== BARRE À BATTRE : taxonomy.py (span -> valeur), test, dans son propre canon")
    for f, (a, b) in sorted(per.items()):
        print(f"   {f:5s} {a}/{b} = {a/max(b,1):.3f}")
    print(f"   TOTAL {tot[0]}/{tot[1]} = {tot[0]/max(tot[1],1):.3f}")

    out = _H / "pairs.json"
    json.dump(rows, open(out, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"\n-> {out}")
    for r in random.Random(0).sample([r for r in rows if r["split"] == "train"], 5):
        print(f"   [{r['fam']}] {r['span'][:58]!r} -> {r['value']!r}")


if __name__ == "__main__":
    main()
