"""Recompute the Chapter 8 ablation on its exact 200-document support.

The repository's historical 410-document output scores 200-document prediction
files against 410 gold documents.  This focused derivation reuses the canonical
scoring functions while restricting gold, text, and folds to the exact shared
prediction-document intersection.  It prints a machine-readable record to
stdout; no values are transcribed by hand.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[4]
LYMPHOME = ROOT / "research/lymphome"
SCORER = LYMPHOME / "score_unified.py"
GOLD = LYMPHOME / "data/v5_test.jsonl"
PREDICTIONS = {
    "full": LYMPHOME / "data/preds_lym_v3e-ab20.parquet",
    "no_clinical": LYMPHOME / "data/preds_lym_v3e-biomedonly-ab20.parquet",
    "biomed_matched": LYMPHOME
    / "data/preds_lym_v3e-biomedmatched-ab20.parquet",
}
SECTIONS = (
    "antecedents",
    "demography",
    "first",
    "history",
    "imaging",
    "news",
    "other",
    "second",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_scorer():
    spec = importlib.util.spec_from_file_location("score_unified", SCORER)
    if spec is None or spec.loader is None:
        raise ImportError(SCORER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def derive() -> dict:
    scorer = _load_scorer()
    gold, texts = scorer.load_gold(GOLD)
    frames = {
        name: pd.read_parquet(path) for name, path in PREDICTIONS.items()
    }
    documents = sorted(
        set.intersection(*(set(frame.doc_id) for frame in frames.values()))
        & set(gold)
    )
    restricted_gold = {document: gold[document] for document in documents}
    restricted_texts = {document: texts[document] for document in documents}

    global_scores = {}
    global_thresholds = {}
    for name, frame in frames.items():
        picks = scorer.top1(frame)
        value, thresholds = scorer.crossfit(
            picks,
            restricted_gold,
            restricted_texts,
            documents,
            "value",
        )
        global_scores[name] = {
            "value_f1": value,
            "crossfit_thresholds": thresholds,
        }
        global_thresholds[name] = thresholds

    half = len(documents) // 2
    sections = {}
    for section in SECTIONS:
        section_gold = {
            document: {
                key: values
                for key, values in fields.items()
                if key.startswith(f"{section}_")
            }
            for document, fields in restricted_gold.items()
        }
        section_record = {
            "n_gold_cells": sum(
                bool(values)
                for fields in section_gold.values()
                for values in fields.values()
            ),
            "models": {},
        }
        for name, frame in frames.items():
            section_frame = frame[frame.key.str.startswith(f"{section}_")]
            picks = scorer.top1(section_frame)
            thresholds = global_thresholds[name]
            value = sum(
                scorer.score(
                    picks,
                    section_gold,
                    restricted_texts,
                    report_documents,
                    "value",
                    threshold,
                )[0]
                for report_documents, threshold in (
                    (documents[half:], thresholds[0]),
                    (documents[:half], thresholds[1]),
                )
            ) / 2
            section_record["models"][name] = {
                "value_f1": value,
                "n_raw_candidate_rows": int(len(section_frame)),
            }
        sections[section] = section_record

    return {
        "schema": 1,
        "metric": "value-micro-F1",
        "method": (
            "Canonical top1 plus two-fold cross-fit thresholds on the exact "
            "shared 200-document prediction intersection; section scores use "
            "the corresponding global model threshold in each report fold."
        ),
        "n_documents": len(documents),
        "document_ids_sha256": hashlib.sha256(
            "\n".join(documents).encode()
        ).hexdigest(),
        "inputs": {
            "scorer": {"path": str(SCORER.relative_to(ROOT)), "sha256": _sha256(SCORER)},
            "gold": {"path": str(GOLD.relative_to(ROOT)), "sha256": _sha256(GOLD)},
            "predictions": {
                name: {
                    "path": str(path.relative_to(ROOT)),
                    "sha256": _sha256(path),
                }
                for name, path in PREDICTIONS.items()
            },
        },
        "global": global_scores,
        "sections": sections,
    }


if __name__ == "__main__":
    print(json.dumps(derive(), indent=2, sort_keys=True))
