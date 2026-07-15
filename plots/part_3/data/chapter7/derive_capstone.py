#!/usr/bin/env python3
"""Reproduce Figure 12 metrics from the two current prediction artifacts."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[4]
SCORER = ROOT / "research/lymphome/score_unified.py"
GOLD = ROOT / "research/lymphome/data/v5_test.jsonl"
RESULTS = ROOT / "research/lymphome/results.json"
INPUTS = {
    "encoder": ROOT / "research/lymphome/data/preds_lym_lym-V5FROMV3B-v3b410.parquet",
    "qwen": ROOT / "research/lymphome/data/preds_lym_llm_qwen3.5-9b-de1540v2.parquet",
}
IDENTITIES = {
    "encoder": ("MC-bio-gliner (v3b)", "capstone"),
    "qwen": ("Qwen3.5-9B", "capstone"),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_scorer():
    spec = importlib.util.spec_from_file_location("canonical_score_unified", SCORER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def registry_entry(registry: dict, display: str, regime: str) -> dict:
    matches = [
        row for row in registry["ecrf"].values()
        if row.get("display") == display and row.get("regime") == regime
    ]
    if len(matches) != 1:
        raise RuntimeError(f"registry identity is not unique: {(display, regime, len(matches))}")
    return matches[0]


def main() -> None:
    scorer = load_scorer()
    gold, texts = scorer.load_gold(GOLD)
    docs = sorted(gold)
    registry = json.loads(RESULTS.read_text())
    systems = {}
    for key, path in INPUTS.items():
        base = scorer.top1(pd.read_parquet(path))
        variants = {}
        for variant, picks in (("top1", base), ("final", scorer.compete(base))):
            span, span_thresholds = scorer.crossfit(picks, gold, texts, docs, "span")
            value, value_thresholds = scorer.crossfit(picks, gold, texts, docs, "value")
            variants[variant] = {
                "label": "top-1" if variant == "top1" else "top-1 + compete",
                "span_f1": span,
                "value_f1": value,
                "span_thresholds": span_thresholds,
                "value_thresholds": value_thresholds,
            }
        display, regime = IDENTITIES[key]
        registered = registry_entry(registry, display, regime)
        final = variants["final"]
        variants["registry_comparison"] = {
            "display": display,
            "regime": regime,
            "registered_span_f1": registered["span"],
            "registered_value_f1": registered["value"],
            "exact_round4_match": (
                round(final["span_f1"], 4) == registered["span"]
                and round(final["value_f1"], 4) == registered["value"]
            ),
        }
        systems[key] = variants

    output = {
        "schema": 1,
        "n_documents": len(docs),
        "scoring": "canonical score_unified.py; two-fold cross-fit thresholds",
        "input_sha256": {
            "scorer": sha256(SCORER),
            "gold": sha256(GOLD),
            "results_registry": sha256(RESULTS),
            **{key: sha256(path) for key, path in INPUTS.items()},
        },
        "systems": systems,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
