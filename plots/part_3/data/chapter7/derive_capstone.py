#!/usr/bin/env python3
"""Derive final OncoLab scores with validation-selected thresholds.

The confidence threshold is selected once on the 100-record validation split
using value-F1.  Value- and span-F1 are then reported on the 410-record test
split at that same operating point.  Test scores never enter threshold choice.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import platform
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow


ROOT = Path(__file__).resolve().parents[4]
SCORER_PATH = ROOT / "research/lymphome/score_unified.py"
PROTOCOL_PATH = ROOT / "research/lymphome/validation_protocol.py"
VALIDATION_GOLD = ROOT / "research/lymphome/data/v5_val.jsonl"
TEST_GOLD = ROOT / "research/lymphome/data/v5_test.jsonl"
INPUTS = {
    "MedGLiNER": {
        "validation": ROOT / "research/lymphome/data/preds_lym_lym-V5FROMV3B-v3b100val001.parquet",
        "test": ROOT / "research/lymphome/data/preds_lym_lym-V5FROMV3B-v3b410lt.parquet",
    },
    "Joint-supervision MedGLiNER": {
        "validation": ROOT / "research/lymphome/data/preds_lym_lym-V5MIX6-mix6100val001.parquet",
        "test": ROOT / "research/lymphome/data/preds_lym_lym-V5MIX6-mix6410lt.parquet",
    },
    "Qwen3.5-9B": {
        "validation": ROOT / "research/lymphome/data/preds_lym_llm_qwen3.5-9b-de1540v2-val.parquet",
        "test": ROOT / "research/lymphome/data/preds_lym_llm_qwen3.5-9b-de1540v2.parquet",
    },
}
BOOTSTRAP_REPLICATES = 10_000
BOOTSTRAP_SEED = 20260715


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def metrics_at_threshold(scorer, picks, gold, texts, mode, threshold):
    f1, precision, recall = scorer.score(
        picks, gold, texts, sorted(gold), mode, threshold
    )
    return {"f1": f1, "precision": precision, "recall": recall}


def load_predictions(path: Path, expected_documents, label: str):
    frame = pd.read_parquet(path)
    required = {"doc_id", "key", "start", "end", "confidence"}
    missing_columns = required - set(frame.columns)
    if missing_columns:
        raise RuntimeError(f"{label}: missing columns {sorted(missing_columns)}")
    observed = set(frame["doc_id"])
    expected = set(expected_documents)
    if observed != expected:
        raise RuntimeError(
            f"{label}: document coverage differs "
            f"(missing={len(expected - observed)}, extra={len(observed - expected)})"
        )
    if not np.isfinite(frame["confidence"].astype(float)).all():
        raise RuntimeError(f"{label}: non-finite confidence")
    if frame["confidence"].nunique() < 2:
        raise RuntimeError(f"{label}: confidence is constant")
    return frame


def per_document_counts(scorer, picks, gold, texts, threshold):
    return np.asarray([
        scorer.score_counts(picks, gold, texts, [doc], "value", threshold)
        for doc in sorted(gold)
    ], dtype=np.int64)


def f1_from_counts(counts):
    tp, fp, fn = np.moveaxis(counts, -1, 0)
    precision = tp / np.maximum(tp + fp, 1)
    recall = tp / np.maximum(tp + fn, 1)
    return 2 * precision * recall / np.maximum(precision + recall, 1e-9)


def paired_interval(first, second):
    """Paired bootstrap interval for second minus first, by test record."""
    first = np.asarray(first)
    second = np.asarray(second)
    if first.ndim != 2 or first.shape[1:] != (3,):
        raise ValueError("first counts must have shape (documents, 3)")
    if second.shape != first.shape:
        raise ValueError("paired count arrays must have the same shape")
    if len(first) == 0:
        raise ValueError("paired count arrays must not be empty")
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    n = len(first)
    differences = np.empty(BOOTSTRAP_REPLICATES, dtype=float)
    batch_size = 500
    for start in range(0, BOOTSTRAP_REPLICATES, batch_size):
        stop = min(start + batch_size, BOOTSTRAP_REPLICATES)
        indices = rng.integers(0, n, size=(stop - start, n))
        first_f1 = f1_from_counts(first[indices].sum(axis=1))
        second_f1 = f1_from_counts(second[indices].sum(axis=1))
        differences[start:stop] = second_f1 - first_f1
    return {
        "difference": float(f1_from_counts(second.sum(axis=0)) - f1_from_counts(first.sum(axis=0))),
        "ci95": [float(x) for x in np.quantile(differences, [0.025, 0.975])],
        "replicates": BOOTSTRAP_REPLICATES,
        "seed": BOOTSTRAP_SEED,
    }


def main() -> None:
    scorer = load_module("canonical_score_unified", SCORER_PATH)
    protocol = load_module("validation_protocol", PROTOCOL_PATH)
    validation_gold, validation_texts = scorer.load_gold(VALIDATION_GOLD)
    test_gold, test_texts = scorer.load_gold(TEST_GOLD)
    if set(validation_gold) & set(test_gold):
        raise RuntimeError("validation and test documents overlap")

    systems = {}
    count_cache = {}
    for name, paths in INPUTS.items():
        validation_frame = load_predictions(
            paths["validation"], validation_gold, f"{name} validation"
        )
        test_frame = load_predictions(paths["test"], test_gold, f"{name} test")
        validation_top1 = scorer.top1(validation_frame)
        test_top1 = scorer.top1(test_frame)
        variants = {}
        for key, validation_picks, test_picks in (
            ("top1", validation_top1, test_top1),
            ("competition", scorer.compete(validation_top1), scorer.compete(test_top1)),
        ):
            selected = protocol.evaluate_with_validation_threshold(
                validation_picks,
                validation_gold,
                validation_texts,
                test_picks,
                test_gold,
                test_texts,
                mode="value",
                thresholds=protocol.FINAL_THRESHOLDS,
            )
            threshold = selected["threshold"]
            variants[key] = {
                "threshold": threshold,
                "validation": {
                    "value": {
                        "f1": selected["validation_f1"],
                        "precision": selected["validation_precision"],
                        "recall": selected["validation_recall"],
                    },
                    "span": metrics_at_threshold(
                        scorer, validation_picks, validation_gold, validation_texts,
                        "span", threshold,
                    ),
                },
                "test": {
                    "value": {
                        "f1": selected["test_f1"],
                        "precision": selected["test_precision"],
                        "recall": selected["test_recall"],
                    },
                    "span": metrics_at_threshold(
                        scorer, test_picks, test_gold, test_texts, "span", threshold
                    ),
                },
            }
            count_cache[(name, key)] = per_document_counts(
                scorer, test_picks, test_gold, test_texts, threshold
            )

        # Isolate the competition rule itself: use the threshold selected for
        # raw top-1 in both branches rather than retuning after decoding.
        shared_threshold = variants["top1"]["threshold"]
        raw_counts = per_document_counts(
            scorer, test_top1, test_gold, test_texts, shared_threshold
        )
        decoded_counts = per_document_counts(
            scorer, scorer.compete(test_top1), test_gold, test_texts, shared_threshold
        )
        raw_shared_f1 = float(f1_from_counts(raw_counts.sum(axis=0)))
        decoded_shared_f1 = float(f1_from_counts(decoded_counts.sum(axis=0)))
        variants["competition_effect"] = {
            "threshold": shared_threshold,
            "raw_f1": raw_shared_f1,
            "decoded_f1": decoded_shared_f1,
            **paired_interval(raw_counts, decoded_counts),
        }
        systems[name] = variants

    comparisons = {
        "MedGLiNER_minus_Qwen3.5-9B": paired_interval(
            count_cache[("Qwen3.5-9B", "competition")],
            count_cache[("MedGLiNER", "competition")],
        )
    }
    output = {
        "schema": 2,
        "protocol": {
            "selection_metric": "validation value-F1",
            "reported_metrics_share_threshold": True,
            "threshold_grid": list(protocol.FINAL_THRESHOLDS),
            "test_used_for_selection": False,
            "competition_effect_uses_shared_threshold": True,
        },
        "documents": {"validation": len(validation_gold), "test": len(test_gold)},
        "input_sha256": {
            "derivation": sha256(Path(__file__)),
            "scorer": sha256(SCORER_PATH),
            "protocol": sha256(PROTOCOL_PATH),
            "validation_gold": sha256(VALIDATION_GOLD),
            "test_gold": sha256(TEST_GOLD),
            **{
                f"{name}:{split}": sha256(path)
                for name, paths in INPUTS.items()
                for split, path in paths.items()
            },
        },
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "pyarrow": pyarrow.__version__,
        },
        "systems": systems,
        "comparisons": comparisons,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
