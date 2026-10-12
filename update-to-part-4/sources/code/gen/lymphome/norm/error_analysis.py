"""Décomposition de l'erreur : COMMENT le modèle se trompe, et ce que vaut chaque correctif.

Quatre classes d'erreur, mutuellement exclusives, sur chaque (document, champ) :
  SUR-REMPLI  : pas de cible, le modèle remplit quand même  -> coûte de la précision
  SOUS-REMPLI : une cible existe, le modèle s'abstient       -> coûte du rappel
  FAUSSE_VAL  : une cible existe, le modèle remplit à tort   -> coûte les deux
  OK          : correct
Les deux dernières se subdivisent selon que la bonne valeur était OU NON parmi les
candidats (colonne oracle_in_cand) : dedans = erreur de SÉLECTION (récupérable par un
re-classement), dehors = erreur de DÉTECTION (ou cible absente du texte).

Chaque correctif est chiffré en contrefactuel : quel F1 si cette classe disparaissait ?

  python error_analysis.py --test dump_X.parquet [--top 15]
"""
import argparse
from collections import defaultdict

import numpy as np
import pandas as pd

FAMS = ("CAT", "ORD", "NUM", "DATE")


def val(x):
    return None if x is None or pd.isna(x) or x == "None" else str(x)


def match(fam, a, b):
    if a is None or b is None:
        return False
    if fam == "NUM":
        try:
            return abs(float(a) - float(b)) / max(abs(float(b)), 1e-6) <= 0.10
        except ValueError:
            return False
    return a == b


def classify(r, col):
    g, p = val(r.gold), val(getattr(r, col))
    if g is None:
        return "OK" if p is None else "SUR_REMPLI"
    if p is None:
        return "SOUS_REMPLI"
    return "OK" if match(r.family, p, g) else "FAUSSE_VAL"


def f1_from(counts):
    """counts[fam] = {OK, SUR_REMPLI, SOUS_REMPLI, FAUSSE_VAL} -> macro-F1."""
    out = {}
    for fam in FAMS:
        c = counts[fam]
        tp = c["OK_pos"]; fp = c["SUR_REMPLI"] + c["FAUSSE_VAL"]; fn = c["SOUS_REMPLI"] + c["FAUSSE_VAL"]
        p = tp / max(tp + fp, 1); rc = tp / max(tp + fn, 1)
        out[fam] = 2 * p * rc / max(p + rc, 1e-9)
    return float(np.mean([out[f] for f in FAMS])), out


def tally(df, col):
    counts = defaultdict(lambda: defaultdict(int))
    for r in df.itertuples():
        k = classify(r, col)
        counts[r.family][k] += 1
        if k == "OK" and val(r.gold) is not None:
            counts[r.family]["OK_pos"] += 1
        if k in ("SOUS_REMPLI", "FAUSSE_VAL"):
            counts[r.family][k + ("_selection" if r.oracle_in_cand else "_detection")] += 1
    return counts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", required=True)
    ap.add_argument("--col", default="pred_heads")
    ap.add_argument("--top", type=int, default=15)
    args = ap.parse_args()
    df = pd.read_parquet(args.test)
    counts = tally(df, args.col)
    base, per = f1_from(counts)

    print(f"=== {args.test.split('/')[-1]}  colonne={args.col}   macro-F1 = {base:.3f}\n")
    print("| famille | OK | SUR-REMPLI | SOUS-REMPLI | FAUSSE_VAL | F1 |")
    print("|---|---|---|---|---|---|")
    tot = defaultdict(int)
    for fam in FAMS:
        c = counts[fam]
        for k in ("SUR_REMPLI", "SOUS_REMPLI", "FAUSSE_VAL"):
            tot[k] += c[k]
        print(f"| {fam} | {c['OK_pos']} | {c['SUR_REMPLI']} | {c['SOUS_REMPLI']} | {c['FAUSSE_VAL']} | {per[fam]:.3f} |")
    ne = sum(tot.values())
    print(f"\nmasse d'erreur : SUR-REMPLI {tot['SUR_REMPLI']} ({100*tot['SUR_REMPLI']/ne:.0f}%)  "
          f"SOUS-REMPLI {tot['SOUS_REMPLI']} ({100*tot['SOUS_REMPLI']/ne:.0f}%)  "
          f"FAUSSE_VAL {tot['FAUSSE_VAL']} ({100*tot['FAUSSE_VAL']/ne:.0f}%)")

    print("\n=== sélection (récupérable par re-classement) vs détection (candidat absent)")
    print("| famille | SOUS-REMPLI sel/det | FAUSSE_VAL sel/det |")
    print("|---|---|---|")
    for fam in FAMS:
        c = counts[fam]
        print(f"| {fam} | {c['SOUS_REMPLI_selection']}/{c['SOUS_REMPLI_detection']} "
              f"| {c['FAUSSE_VAL_selection']}/{c['FAUSSE_VAL_detection']} |")

    print("\n=== contrefactuels : macro-F1 si une classe d'erreur disparaissait")
    scen = {
        "aucune sur-écriture (précision parfaite sur champs absents)": ["SUR_REMPLI"],
        "aucune fausse valeur": ["FAUSSE_VAL"],
        "aucun sous-remplissage": ["SOUS_REMPLI"],
        "sélection parfaite (cible déjà dans les candidats)": ["_selection"],
    }
    for name, kill in scen.items():
        c2 = defaultdict(lambda: defaultdict(int))
        for fam in FAMS:
            c2[fam].update(counts[fam])
        for fam in FAMS:
            if kill == ["_selection"]:
                for k in ("SOUS_REMPLI", "FAUSSE_VAL"):
                    mv = counts[fam][k + "_selection"]
                    c2[fam][k] -= mv; c2[fam]["OK_pos"] += mv
            else:
                k = kill[0]
                mv = counts[fam][k]
                c2[fam][k] = 0
                if k != "SUR_REMPLI":
                    c2[fam]["OK_pos"] += mv
        f, _ = f1_from(c2)
        print(f"   {name:58s} {f:.3f}  ({f-base:+.3f})")

    print(f"\n=== top {args.top} champs par masse d'erreur")
    per_field = defaultdict(lambda: defaultdict(int))
    for r in df.itertuples():
        k = classify(r, args.col)
        if k != "OK":
            per_field[r.key][k] += 1
            per_field[r.key]["n"] += 1
    print("| champ | erreurs | dominante | sur | sous | fausse |")
    print("|---|---|---|---|---|---|")
    for k, c in sorted(per_field.items(), key=lambda kv: -kv[1]["n"])[:args.top]:
        dom = max(("SUR_REMPLI", "SOUS_REMPLI", "FAUSSE_VAL"), key=lambda x: c[x])
        print(f"| {k[:46]} | {c['n']} | {dom} | {c['SUR_REMPLI']} | {c['SOUS_REMPLI']} | {c['FAUSSE_VAL']} |")

    if "pred_qwen" in df.columns:
        print("\n=== face à Qwen sur les mêmes lignes (cibles présentes)")
        w = defaultdict(lambda: [0, 0, 0, 0])
        for r in df.itertuples():
            g = val(r.gold)
            if g is None:
                continue
            us = match(r.family, val(getattr(r, args.col)), g)
            qw = match(r.family, val(r.pred_qwen), g)
            w[r.family][0 if (us and qw) else 1 if (us and not qw) else 2 if (qw and not us) else 3] += 1
        print("| famille | les deux OK | nous seuls | Qwen seul | aucun |")
        print("|---|---|---|---|---|")
        for fam in FAMS:
            a, b, c, d = w[fam]
            print(f"| {fam} | {a} | {b} | **{c}** | {d} |")


if __name__ == "__main__":
    main()
