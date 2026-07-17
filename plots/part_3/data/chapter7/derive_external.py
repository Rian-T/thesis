#!/usr/bin/env python3
"""Derive PARHAF and FRACCO NER results with held-out thresholds."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

from research.lymphome.score_unified import load_gold, score_ner
from research.lymphome.validation_protocol import FINAL_THRESHOLDS


ROOT = Path(__file__).resolve().parents[4]
DATA = ROOT / "research/lymphome/data"
BENCHMARKS = {
    "PARHAF": {
        "directory": DATA / "parhaf",
        "gold": "parhaf_bio_all.jsonl",
        "validation": "parhaf_bio_es.jsonl",
        "test": "parhaf_bio_dev.jsonl",
        "models": {
            "Qwen3.5-2B adapted": "preds_lym_llm_qwen3.5-2b-parhafbio.parquet",
            "Qwen3.5-9B zero-shot": "preds_lym_llm_qwen3.5-9b-parhafbiozs.parquet",
            "Qwen3.5-9B adapted": "preds_lym_llm_qwen3.5-9b-parhafbio.parquet",
            "gliner-biomed zero-shot": "preds_lym_gliner-biomed-parhafbio.parquet",
            "gliner-biomed adapted": "preds_lym_gliner-biomed-parhafft-parhafbio.parquet",
            "MedGLiNER zero-shot": "preds_lym_v3b-pristine-parhafbio.parquet",
            "MedGLiNER adapted": "preds_lym_parhaf-bio-v3b-parhafbio.parquet",
            "Density-corrected zero-shot": "preds_lym_v3f-pristine-parhafbio.parquet",
            "Density-corrected adapted": "preds_lym_parhaf-bio-v3f-parhafbio.parquet",
            "Low-density zero-shot": "preds_lym_v3e-parhafbio.parquet",
            "Low-density adapted": "preds_lym_parhaf-bio-v3e-parhafbio.parquet",
        },
    },
    "FRACCO": {
        "directory": DATA / "fracco",
        "gold": "fracco_all.jsonl",
        "validation": "fracco_es.jsonl",
        "test": "fracco_test.jsonl",
        "models": {
            "gliner-biomed zero-shot": "preds_lym_gliner-biomed-fracco.parquet",
            "gliner-biomed adapted": "preds_lym_gliner-biomed-fraccoft-fracco.parquet",
            "MedGLiNER zero-shot": "preds_lym_v3b-pristine-fracco.parquet",
            "MedGLiNER adapted": "preds_lym_fracco-v3b-fracco.parquet",
            "Density-corrected zero-shot": "preds_lym_v3f-pristine-fracco.parquet",
            "Low-density zero-shot": "preds_lym_v3e-fracco.parquet",
            "Low-density adapted": "preds_lym_fracco-v3e-fracco.parquet",
        },
    },
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ids(path: Path):
    return [json.loads(line)["id"] for line in path.read_text().splitlines()]


def main() -> None:
    output = {
        "schema": 1,
        "protocol": {
            "selection_metric": "validation value-F1",
            "reported_metrics_share_threshold": True,
            "threshold_grid": list(FINAL_THRESHOLDS),
            "test_used_for_selection": False,
        },
        "benchmarks": {},
        "input_sha256": {"derivation": sha256(Path(__file__))},
    }
    for benchmark, spec in BENCHMARKS.items():
        directory = spec["directory"]
        gold_path = directory / spec["gold"]
        validation_path = directory / spec["validation"]
        test_path = directory / spec["test"]
        gold, texts = load_gold(gold_path)
        validation_docs = ids(validation_path)
        test_docs = ids(test_path)
        if set(validation_docs) & set(test_docs):
            raise RuntimeError(f"{benchmark}: validation and test overlap")
        if not set(validation_docs + test_docs) <= set(gold):
            raise RuntimeError(f"{benchmark}: split contains unknown documents")

        rows = {}
        for model, filename in spec["models"].items():
            path = directory / filename
            frame = pd.read_parquet(path)
            required = {"doc_id", "key", "start", "end", "confidence"}
            if required - set(frame.columns):
                raise RuntimeError(f"{benchmark}/{model}: incomplete prediction schema")
            candidates = [
                (score_ner(frame, gold, texts, validation_docs, "value", threshold)[0], threshold)
                for threshold in FINAL_THRESHOLDS
            ]
            validation_f1, threshold = max(candidates, key=lambda item: (item[0], item[1]))
            value_f1, value_precision, value_recall = score_ner(
                frame, gold, texts, test_docs, "value", threshold
            )
            span_f1, span_precision, span_recall = score_ner(
                frame, gold, texts, test_docs, "span", threshold
            )
            rows[model] = {
                "threshold": threshold,
                "validation_value_f1": validation_f1,
                "test": {
                    "value": {"f1": value_f1, "precision": value_precision, "recall": value_recall},
                    "span": {"f1": span_f1, "precision": span_precision, "recall": span_recall},
                },
            }
            output["input_sha256"][f"{benchmark}:{model}"] = sha256(path)
        output["benchmarks"][benchmark] = {
            "documents": {"validation": len(validation_docs), "test": len(test_docs)},
            "models": rows,
        }
        output["input_sha256"][f"{benchmark}:gold"] = sha256(gold_path)
        output["input_sha256"][f"{benchmark}:validation"] = sha256(validation_path)
        output["input_sha256"][f"{benchmark}:test"] = sha256(test_path)
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
