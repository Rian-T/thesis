"""Generate a 10k-document Laya-compatible biomedical decision pilot."""

import argparse
import hashlib
import json
import logging
import os
from pathlib import Path

from vllm import LLM, SamplingParams
try:
    from vllm.sampling_params import StructuredOutputsParams
except ImportError:
    StructuredOutputsParams = None

from prompt import DecisionAnnotation, build_messages


DEFAULT_MODEL = "/lustre/fsn1/projects/rech/rua/uvb79kr/Qwen--Qwen3-235B-A22B-Instruct-2507-FP8"
log = logging.getLogger("laya-biomed-generate")


def stable_key(row: dict) -> str:
    return hashlib.sha256(str(row.get("id", "")).encode()).hexdigest()


def load_selection(path: str, limit: int, max_chars: int) -> list[dict]:
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            text = row.get("text", "")
            if row.get("id") and 200 <= len(text) <= max_chars:
                rows.append(row)
    rows.sort(key=stable_key)
    return rows[:limit]


def completed_ids(path: str) -> set[str]:
    if not os.path.exists(path):
        return set()
    done = set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                done.add(str(json.loads(line)["id"]))
            except Exception:
                pass
    return done


def validate_and_normalize(annotation: DecisionAnnotation, text: str) -> DecisionAnnotation:
    seen_questions = set()
    for decision in annotation.decisions:
        if decision.question_id in seen_questions:
            raise ValueError("duplicate question_id")
        seen_questions.add(decision.question_id)
        ids = [o.id for o in decision.options]
        if len(ids) != len(set(ids)) or decision.hard_gold not in ids:
            raise ValueError("invalid option ids or hard_gold")
        if decision.type == "noul" and ids != ["false", "true"]:
            raise ValueError("noul options must be [false, true]")
        for evidence in decision.evidence:
            if evidence not in text:
                raise ValueError(f"non-literal evidence: {evidence!r}")
        total = sum(o.probability for o in decision.options)
        if not 0.98 <= total <= 1.02:
            raise ValueError(f"probabilities sum to {total}")
        for option in decision.options:
            option.probability /= total
        best = max(decision.options, key=lambda o: o.probability).id
        if best != decision.hard_gold:
            raise ValueError("hard_gold is not the probability argmax")
    return annotation


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--limit", type=int, default=10_000)
    parser.add_argument("--max_chars", type=int, default=12_000)
    parser.add_argument("--batch_size", type=int, default=128)
    parser.add_argument("--tensor_parallel_size", type=int, default=4)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    selected = load_selection(args.input, args.limit, args.max_chars)
    done = completed_ids(args.output)
    pending = [row for row in selected if str(row["id"]) not in done]
    log.info("selected=%d completed=%d pending=%d", len(selected), len(done), len(pending))
    if not pending:
        return

    model = LLM(
        model=args.model,
        tensor_parallel_size=args.tensor_parallel_size,
        quantization="fp8",
        max_model_len=16_384,
        gpu_memory_utilization=0.92,
        trust_remote_code=True,
    )
    sampling_kwargs = {"temperature": 0.6, "top_p": 0.9, "max_tokens": 5_000}
    if StructuredOutputsParams is not None:
        schema = (DecisionAnnotation.model_json_schema() if hasattr(DecisionAnnotation, "model_json_schema")
                  else DecisionAnnotation.schema())
        sampling_kwargs["structured_outputs"] = StructuredOutputsParams(json=schema)
    else:
        log.warning("This vLLM build has no structured-output API; strict JSON prompt + validation enabled")
    sampling = SamplingParams(**sampling_kwargs)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if os.path.exists(args.output) else "w"
    valid = failed = 0
    with open(args.output, mode, encoding="utf-8") as out:
        for start in range(0, len(pending), args.batch_size):
            batch = pending[start : start + args.batch_size]
            results = model.chat(
                [build_messages(row["text"]) for row in batch],
                sampling,
                chat_template_kwargs={"enable_thinking": False},
                use_tqdm=True,
            )
            for row, result in zip(batch, results):
                raw = result.outputs[0].text if result.outputs else ""
                try:
                    ann = (DecisionAnnotation.model_validate_json(raw)
                           if hasattr(DecisionAnnotation, "model_validate_json")
                           else DecisionAnnotation.parse_raw(raw))
                    ann = validate_and_normalize(ann, row["text"])
                    record = {
                        "id": str(row["id"]),
                        "source": row.get("source", ""),
                        "text": row["text"],
                        "annotation": ann.model_dump() if hasattr(ann, "model_dump") else ann.dict(),
                        "generator": "Qwen3-235B-A22B-Instruct-2507-FP8",
                    }
                    out.write(json.dumps(record, ensure_ascii=False) + "\n")
                    valid += 1
                except Exception as exc:
                    failed += 1
                    log.warning("invalid id=%s error=%s", row.get("id"), exc)
            out.flush()
            log.info("progress=%d/%d valid=%d failed=%d", min(start + len(batch), len(pending)), len(pending), valid, failed)


if __name__ == "__main__":
    main()
