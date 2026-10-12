#!/usr/bin/env python3
"""Run a GLiNER2 model over a split and write predictions for evaluate.py.

The extraction schema (field label -> description) is read from the dataset's
own field_labels column, so no external file is needed. Every field is queried
at a low threshold; the evaluator selects the operating threshold afterwards.
Output parquet columns: doc_id, key, start, end, confidence, value.

Usage:
    python predict.py --model rntc/mc-bio-gliner-lymphome \
        --split validation --out preds_val.parquet
    python predict.py --model rntc/mc-bio-gliner-lymphome \
        --split test --out preds_test.parquet
"""
import argparse
import json

import pandas as pd
import torch
from datasets import load_dataset
from gliner2 import GLiNER2

DATASET = "rntc/lymphome-synth-v5-eval"
THRESHOLD = 0.001
MAX_CHARS = 30000


def build_schema(rows):
    label2key, desc = {}, {}
    for r in rows:
        for key, meta in json.loads(r["field_labels"]).items():
            label2key[meta["label"]] = key
            desc[meta["label"]] = meta["desc"]
    return desc, label2key


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--split", default="test")
    ap.add_argument("--out", required=True)
    ap.add_argument("--dataset", default=DATASET)
    ap.add_argument("--threshold", type=float, default=THRESHOLD)
    ap.add_argument("--max_chars", type=int, default=MAX_CHARS)
    a = ap.parse_args()

    rows = list(load_dataset(a.dataset, split=a.split))
    desc, label2key = build_schema(rows)

    model = GLiNER2.from_pretrained(a.model)
    if torch.cuda.is_available():
        model = model.to("cuda")

    out = []
    for i, d in enumerate(rows):
        text = d["text"][:a.max_chars]
        try:
            with torch.no_grad():
                res = model.extract_entities(text, desc, threshold=a.threshold,
                                             include_confidence=True, include_spans=True)
        except Exception:
            continue
        ents = res.get("entities", res) if isinstance(res, dict) else {}
        for label, mentions in (ents.items() if isinstance(ents, dict) else []):
            key = label2key.get(label)
            if not key or not isinstance(mentions, list):
                continue
            for m in mentions:
                if not isinstance(m, dict) or "start" not in m or "end" not in m:
                    continue
                s, e = int(m["start"]), int(m["end"])
                out.append({"doc_id": d["id"], "key": key, "start": s, "end": e,
                            "confidence": float(m.get("confidence", 0.0)),
                            "value": m.get("text", text[s:e])})
        if (i + 1) % 50 == 0:
            print(f"  {i + 1}/{len(rows)} docs, {len(out)} preds", flush=True)

    pd.DataFrame(out).to_parquet(a.out)
    print(f"wrote {len(out)} predictions -> {a.out}")


if __name__ == "__main__":
    main()
