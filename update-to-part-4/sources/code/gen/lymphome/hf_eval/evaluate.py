#!/usr/bin/env python3
"""Standalone evaluator for the lymphoma eCRF extraction task.

The eCRF asks for one value per field, so each system commits to its single most
confident prediction per (document, field). Scoring is at the (document, field)
level: a filled field that matches the gold is a true positive, a filled field
that does not is both a false positive and a false negative, an unfilled gold
field is a false negative, a field filled without gold is a false positive.

Two metrics: span (>= 1 character of overlap with any gold span) and value (token
Jaccard >= 0.5 between the predicted text and any gold span text). "compete"
enforces that one span documents at most one field (highest confidence wins,
IoU > 0.5). The confidence threshold is selected on the validation split by
value-F1 and reused for every metric reported on the test split.

Prediction file: a parquet with columns doc_id, key, start, end, confidence and
optionally value (defaults to text[start:end]). Gold: the dataset jsonl/parquet
rows with fields id, text, gold.

Usage:
    python evaluate.py --pred preds_test.parquet --pred_val preds_val.parquet \
        --gold test.jsonl --gold_val validation.jsonl
"""
import argparse
import json
import re
import unicodedata
from collections import defaultdict

import pandas as pd

THRESHOLDS = (0.001,) + tuple(s / 100 for s in range(1, 100))


def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", s)).strip()


def toks(s):
    return set(norm(s).split())


def jacc(a, b):
    ta, tb = toks(a), toks(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def overlaps(a, b):
    return max(0, min(a[1], b[1]) - max(a[0], b[0])) > 0


def iou(a, b):
    inter = max(0, min(a[1], b[1]) - max(a[0], b[0]))
    union = max(a[1], b[1]) - min(a[0], b[0])
    return inter / union if union > 0 else 0.0


def load_gold(path):
    gold, texts = {}, {}
    if path.endswith(".parquet"):
        rows = (r._asdict() for r in pd.read_parquet(path).itertuples(index=False))
    else:
        rows = (json.loads(line) for line in open(path, encoding="utf-8"))
    for d in rows:
        g = d["gold"]
        gold[d["id"]] = json.loads(g) if isinstance(g, str) else g
        texts[d["id"]] = d["text"]
    return gold, texts


def top1(df):
    best = {}
    for r in df.itertuples():
        k = (r.doc_id, r.key)
        c = float(getattr(r, "confidence", 1.0))
        cand = (c, int(r.start), int(r.end), getattr(r, "value", None))
        sig = (cand[1], cand[2], str(cand[3]))
        if (k not in best or c > best[k][0]
                or (c == best[k][0] and sig < (best[k][1], best[k][2], str(best[k][3])))):
            best[k] = cand
    out = defaultdict(dict)
    for (doc, key), (c, s, e, v) in best.items():
        out[doc][key] = (c, s, e, v)
    return out


def compete(picks):
    out = {}
    for doc, fields in picks.items():
        rows = sorted(fields.items(), key=lambda kv: (-kv[1][0], kv[0], kv[1][1], kv[1][2], str(kv[1][3])))
        kept = {}
        for key, (c, s, e, v) in rows:
            if s >= 0 and any(iou((s, e), (s2, e2)) > 0.5
                              for (_, s2, e2, _) in kept.values() if s2 >= 0):
                continue
            kept[key] = (c, s, e, v)
        out[doc] = kept
    return out


def score(picks, gold, texts, docs, mode, thr):
    tp = fp = fn = 0
    for doc in docs:
        g = gold[doc]
        t = texts[doc]
        pr = {k: v for k, v in picks.get(doc, {}).items() if v[0] >= thr}
        for key in set(g) | set(pr):
            gs = g.get(key, [])
            p = pr.get(key)
            if gs and p:
                c, s, e, v = p
                if mode == "span":
                    hit = s >= 0 and any(overlaps((s, e), (gg[0], gg[1])) for gg in gs)
                else:
                    pv = v if v is not None else (t[s:e] if s >= 0 else "")
                    hit = any(jacc(pv, gg[2]) >= 0.5 for gg in gs)
                if hit:
                    tp += 1
                else:
                    fp += 1
                    fn += 1
            elif gs:
                fn += 1
            elif p:
                fp += 1
    p = tp / max(tp + fp, 1)
    r = tp / max(tp + fn, 1)
    return 2 * p * r / max(p + r, 1e-9), p, r


def evaluate(val_picks, val_gold, val_texts, test_picks, test_gold, test_texts, mode):
    val_docs, test_docs = sorted(val_gold), sorted(test_gold)
    thr = max(THRESHOLDS, key=lambda c: (score(val_picks, val_gold, val_texts, val_docs, mode, c)[0], c))
    f1, p, r = score(test_picks, test_gold, test_texts, test_docs, mode, thr)
    return {"threshold": thr, "f1": f1, "precision": p, "recall": r}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pred", required=True, help="test predictions parquet")
    ap.add_argument("--pred_val", required=True, help="validation predictions parquet")
    ap.add_argument("--gold", required=True, help="test gold jsonl/parquet")
    ap.add_argument("--gold_val", required=True, help="validation gold jsonl/parquet")
    a = ap.parse_args()

    test_gold, test_texts = load_gold(a.gold)
    val_gold, val_texts = load_gold(a.gold_val)
    if set(val_gold) & set(test_gold):
        raise SystemExit("validation and test documents overlap")

    test_top1 = top1(pd.read_parquet(a.pred))
    val_top1 = top1(pd.read_parquet(a.pred_val))
    variants = {"top-1": (val_top1, test_top1),
                "top-1 + compete": (compete(val_top1), compete(test_top1))}

    print(f"validation: {len(val_gold)} docs   test: {len(test_gold)} docs\n")
    print(f"{'variant':18s} {'metric':7s} {'F1':>7s} {'P':>7s} {'R':>7s}  thr")
    print("-" * 56)
    for name, (vp, tp) in variants.items():
        for mode in ("span", "value"):
            res = evaluate(vp, val_gold, val_texts, tp, test_gold, test_texts, mode)
            print(f"{name:18s} {mode:7s} {res['f1']:7.3f} {res['precision']:7.3f} "
                  f"{res['recall']:7.3f}  {res['threshold']}")


if __name__ == "__main__":
    main()
