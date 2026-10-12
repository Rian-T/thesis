"""Minimal schema-conditioned clinical decision model.

Research question: with the V2 encoder and official data split held constant, does a
direct field/value decision head improve CAT/ORD prediction and calibration?

The RLCD mode is an explicitly labelled public-description-inspired experiment, not a
claim to reproduce an undisclosed implementation.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F


ROOT = Path("/lustre/fswork/projects/rech/rua/uvb79kr/french-medgliner")
sys.path.insert(0, str(ROOT / "GLiNER2"))
sys.path.insert(0, str(ROOT / "GLiNER2" / "v3"))
sys.path.insert(0, str(ROOT / "gen" / "lymphome"))
sys.path.insert(0, str(ROOT / "gen" / "lymphome" / "norm"))
from eval_v3 import load_model  # noqa: E402
import taxonomy as T  # noqa: E402
from labels import LABELS  # noqa: E402


SUPPORTED = {"CAT", "ORD"}  # BOOL fields are represented as two-class CAT in V2.
NULL = "<NULL>"


@dataclass(frozen=True)
class Field:
    key: str
    family: str
    candidates: tuple[str, ...]
    query_texts: tuple[str, ...]


def seed_all(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def fields_from_taxonomy() -> list[Field]:
    fields = []
    for key, spec in T.FIELD_SPEC.items():
        family = spec["family"]
        if family not in SUPPORTED or key not in LABELS:
            continue
        if family == "CAT":
            values = list(spec["classes"].keys())
        else:
            lo, hi = spec["range"]
            values = [str(v) for v in range(int(lo), int(hi) + 1)]
        candidates = tuple(values + [NULL])
        meta = LABELS[key]
        prefix = f"Champ : {meta['label']}. Définition : {meta['desc']}."
        queries = tuple(
            f"{prefix} Valeur : {'information absente ou insuffisante' if v == NULL else v}."
            for v in candidates
        )
        fields.append(Field(key, family, candidates, queries))
    return fields


def parse_json_cell(value):
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    return json.loads(value) if isinstance(value, str) else value


def canonical_target(field: Field, annotation) -> str:
    if not annotation:
        return NULL
    raw = annotation.get(field.key)
    if raw is None:
        return NULL
    items = [raw] if isinstance(raw, dict) else raw
    for item in items:
        if not isinstance(item, dict) or item.get("value") in (None, ""):
            continue
        value = T.normalize_target(field.key, item["value"])
        if value is None:
            continue
        value = str(int(value)) if field.family == "ORD" else str(value)
        if value in field.candidates:
            return value
    return NULL


class EcrfDataset(torch.utils.data.Dataset):
    def __init__(self, parquet: Path, fields: list[Field], max_chars: int):
        frame = pd.read_parquet(parquet)
        self.rows = []
        for row in frame.to_dict("records"):
            ann = parse_json_cell(row.get("annotation_v4_json")) or {}
            targets = [f.candidates.index(canonical_target(f, ann)) for f in fields]
            self.rows.append((str(row["id"]), str(row["text"])[:max_chars], targets))
        self.fields = fields

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, idx):
        return self.rows[idx]


def split_parquet(data_dir: Path, split: str) -> Path:
    """Resolve either flattened files or the Hub's data/<split>-00000... layout."""
    direct = data_dir / f"{split}.parquet"
    if direct.exists():
        return direct
    matches = sorted(data_dir.glob(f"**/{split}-*.parquet"))
    if len(matches) != 1:
        raise FileNotFoundError(f"expected one parquet for {split}, found {matches}")
    return matches[0]


def mean_pool(hidden, mask):
    mask = mask.unsqueeze(-1).to(hidden.dtype)
    return (hidden * mask).sum(1) / mask.sum(1).clamp_min(1)


class DecisionHead(nn.Module):
    def __init__(self, d_model: int, layers: int = 2, heads: int = 8, dropout: float = 0.1):
        super().__init__()
        layer = nn.TransformerDecoderLayer(
            d_model=d_model, nhead=heads, dim_feedforward=4 * d_model,
            dropout=dropout, batch_first=True, norm_first=True, activation="gelu",
        )
        self.decoder = nn.TransformerDecoder(layer, num_layers=layers)
        self.query_ln = nn.LayerNorm(d_model)
        self.scorer = nn.Sequential(
            nn.LayerNorm(d_model), nn.Linear(d_model, d_model // 2), nn.GELU(),
            nn.Dropout(dropout), nn.Linear(d_model // 2, 1),
        )

    def forward(self, queries, memory, memory_padding_mask=None):
        z = self.decoder(self.query_ln(queries), memory,
                         memory_key_padding_mask=memory_padding_mask)
        return self.scorer(z).squeeze(-1)


class V3(nn.Module):
    def __init__(self, extractor, fields: list[Field], schema_embeddings: torch.Tensor,
                 layers: int, heads: int, dropout: float):
        super().__init__()
        self.encoder = extractor.encoder
        self.tokenizer = extractor.processor.tokenizer
        self.fields = fields
        self.register_buffer("schema_embeddings", schema_embeddings, persistent=True)
        self.head = DecisionHead(schema_embeddings.shape[-1], layers, heads, dropout)
        offsets, cursor = [], 0
        for field in fields:
            offsets.append((cursor, cursor + len(field.candidates)))
            cursor += len(field.candidates)
        self.offsets = offsets

    def encode_document(self, text: str, device):
        tok = self.tokenizer(text, return_tensors="pt", truncation=False,
                             add_special_tokens=True)
        tok = {k: v.to(device) for k, v in tok.items()}
        out = self.encoder(**tok).last_hidden_state
        padding = ~tok["attention_mask"].bool()
        return out, padding

    def forward(self, text: str):
        device = next(self.parameters()).device
        memory, padding = self.encode_document(text, device)
        queries = self.schema_embeddings.unsqueeze(0).to(memory.dtype)
        logits = self.head(queries, memory, padding)
        return [logits[0, a:b] for a, b in self.offsets]


@torch.no_grad()
def encode_schema(extractor, fields: list[Field], device, batch_size: int = 32):
    tokenizer, encoder = extractor.processor.tokenizer, extractor.encoder
    texts = [text for field in fields for text in field.query_texts]
    was_training = encoder.training
    encoder.eval()
    chunks = []
    for start in range(0, len(texts), batch_size):
        tok = tokenizer(texts[start:start + batch_size], padding=True, truncation=True,
                        max_length=128, return_tensors="pt")
        tok = {k: v.to(device) for k, v in tok.items()}
        hidden = encoder(**tok).last_hidden_state
        chunks.append(mean_pool(hidden, tok["attention_mask"]).float().cpu())
    encoder.train(was_training)
    return torch.cat(chunks)


def supervised_loss(logits, targets, fields, mode, brier_w, rps_w):
    ce, brier, rps = [], [], []
    for z, y, field in zip(logits, targets, fields):
        target = torch.tensor([y], device=z.device)
        ce.append(F.cross_entropy(z.unsqueeze(0), target))
        p = z.softmax(-1)
        onehot = F.one_hot(target, len(field.candidates)).squeeze(0).to(p.dtype)
        brier.append((p - onehot).square().sum())
        if field.family == "ORD" and y != len(field.candidates) - 1:
            # RPS over ordered non-NULL levels; NULL remains governed by CE/Brier.
            po = p[:-1] / p[:-1].sum().clamp_min(1e-8)
            yo = F.one_hot(target, len(field.candidates) - 1).squeeze(0).to(p.dtype)
            rps.append((po.cumsum(0)[:-1] - yo.cumsum(0)[:-1]).square().mean())
    loss_ce = torch.stack(ce).mean()
    loss_brier = torch.stack(brier).mean()
    loss_rps = torch.stack(rps).mean() if rps else loss_ce.new_zeros(())
    total = loss_ce
    if mode == "proper":
        total = total + brier_w * loss_brier + rps_w * loss_rps
    return total, {"ce": loss_ce.detach(), "brier": loss_brier.detach(), "rps": loss_rps.detach()}


def rlcd_loss(logits, targets, rollouts: int, temperature: float, ce_anchor: float):
    """Group-relative calibrated decision objective over a complete document.

    Each rollout samples one decision per field. Reward favours correctness and penalizes
    confidently selected wrong answers. Advantages are normalized within the document.
    """
    rewards, logps = [], []
    for _ in range(rollouts):
        reward_parts, logp_parts = [], []
        for z, y in zip(logits, targets):
            dist = torch.distributions.Categorical(logits=z / temperature)
            action = dist.sample()
            chosen_p = z.softmax(-1)[action]
            correct = (action == y).to(z.dtype)
            null_index = z.numel() - 1
            # A correct NULL is useful but must not dominate: 56.9% of train decisions
            # are NULL. Non-NULL targets receive full weight to keep reward aligned with
            # field-level value-F1 rather than raw accuracy.
            target_weight = z.new_tensor(0.25 if y == null_index else 1.0)
            reward_parts.append(
                target_weight * correct
                - target_weight * (1.0 - correct) * (1.0 + chosen_p.detach().square())
            )
            logp_parts.append(dist.log_prob(action))
        rewards.append(torch.stack(reward_parts).mean())
        logps.append(torch.stack(logp_parts).mean())
    rewards = torch.stack(rewards)
    advantages = (rewards - rewards.mean()) / rewards.std(unbiased=False).clamp_min(1e-4)
    policy = -(advantages.detach() * torch.stack(logps)).mean()
    anchor = torch.stack([
        F.cross_entropy(z.unsqueeze(0), torch.tensor([y], device=z.device))
        for z, y in zip(logits, targets)
    ]).mean()
    return policy + ce_anchor * anchor, {"policy": policy.detach(), "reward": rewards.mean().detach(),
                                         "ce": anchor.detach()}


def calibration_bins(conf, ok, bins=10):
    if not conf:
        return 0.0
    conf, ok = np.asarray(conf), np.asarray(ok, dtype=float)
    ece = 0.0
    for lo in np.linspace(0, 1, bins, endpoint=False):
        mask = (conf >= lo) & (conf < lo + 1 / bins)
        if mask.any():
            ece += mask.mean() * abs(ok[mask].mean() - conf[mask].mean())
    return float(ece)


@torch.no_grad()
def evaluate(model, dataset, device):
    model.eval()
    records, nlls, briers, conf, ok = [], [], [], [], []
    for doc_id, text, targets in dataset:
        logits = model(text)
        for z, y, field in zip(logits, targets, model.fields):
            p = z.float().softmax(-1)
            pred = int(p.argmax())
            truth, guess = field.candidates[y], field.candidates[pred]
            is_ok = pred == y
            records.append((field.family, truth, guess, is_ok))
            nlls.append(float(-p[y].clamp_min(1e-9).log()))
            oh = F.one_hot(torch.tensor(y, device=device), len(field.candidates)).float()
            briers.append(float((p - oh).square().sum()))
            conf.append(float(p[pred])); ok.append(is_ok)
    per = {}
    for family in sorted(SUPPORTED):
        rows = [r for r in records if r[0] == family]
        tp = sum(r[3] and r[1] != NULL for r in rows)
        fp = sum(r[2] != NULL and not r[3] for r in rows)
        fn = sum(r[1] != NULL and not r[3] for r in rows)
        precision = tp / max(tp + fp, 1)
        recall = tp / max(tp + fn, 1)
        per[family] = 2 * precision * recall / max(precision + recall, 1e-9)
    model.train()
    return {"macro_f1": float(np.mean(list(per.values()))), "per_family": per,
            "accuracy": float(np.mean(ok)), "nll": float(np.mean(nlls)),
            "brier": float(np.mean(briers)), "ece": calibration_bins(conf, ok)}


def save_checkpoint(path: Path, model, args, metrics):
    path.mkdir(parents=True, exist_ok=True)
    torch.save({"model": model.state_dict(), "args": vars(args), "metrics": metrics}, path / "v3.pt")
    (path / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("ce", "proper", "rlcd"), default="ce")
    ap.add_argument("--model", required=True, help="local V2 HF snapshot")
    ap.add_argument("--data", required=True, help="directory with train/validation/test parquet")
    ap.add_argument("--out", required=True)
    ap.add_argument("--init_v3", help="V3 checkpoint used to initialize proper/RLCD")
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--max_chars", type=int, default=45000)
    ap.add_argument("--layers", type=int, default=2)
    ap.add_argument("--heads", type=int, default=8)
    ap.add_argument("--dropout", type=float, default=0.1)
    ap.add_argument("--enc_lr", type=float, default=1e-5)
    ap.add_argument("--head_lr", type=float, default=1e-4)
    ap.add_argument("--weight_decay", type=float, default=1e-4)
    ap.add_argument("--accum", type=int, default=4)
    ap.add_argument("--brier_w", type=float, default=0.2)
    ap.add_argument("--rps_w", type=float, default=0.2)
    ap.add_argument("--rollouts", type=int, default=8)
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--ce_anchor", type=float, default=0.2)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--eval_test", action="store_true")
    args = ap.parse_args()

    seed_all(args.seed)
    device = torch.device("cuda")
    fields = fields_from_taxonomy()
    print(f"fields={len(fields)} CAT={sum(f.family == 'CAT' for f in fields)} "
          f"ORD={sum(f.family == 'ORD' for f in fields)}")

    extractor = load_model(args.model).to(device)
    extractor.encoder.gradient_checkpointing_enable()
    schema = encode_schema(extractor, fields, device)
    model = V3(extractor, fields, schema, args.layers, args.heads, args.dropout).to(device)
    del extractor
    if args.init_v3:
        state = torch.load(Path(args.init_v3) / "v3.pt", map_location="cpu")
        model.load_state_dict(state["model"], strict=True)

    data_dir = Path(args.data)
    train = EcrfDataset(split_parquet(data_dir, "train"), fields, args.max_chars)
    val = EcrfDataset(split_parquet(data_dir, "validation"), fields, args.max_chars)
    if args.limit:
        train.rows = train.rows[:args.limit]
        val.rows = val.rows[:max(2, args.limit // 2)]
    print(f"train={len(train)} validation={len(val)}")

    optimizer = torch.optim.AdamW([
        {"params": model.encoder.parameters(), "lr": args.enc_lr},
        {"params": model.head.parameters(), "lr": args.head_lr},
    ], weight_decay=args.weight_decay)
    scaler = torch.amp.GradScaler("cuda")
    best = -1.0
    for epoch in range(args.epochs):
        order = np.random.permutation(len(train))
        optimizer.zero_grad(set_to_none=True)
        running = defaultdict(float)
        for step, idx in enumerate(order):
            _, text, targets = train[int(idx)]
            with torch.autocast("cuda", dtype=torch.bfloat16):
                logits = model(text)
                if args.mode == "rlcd":
                    loss, parts = rlcd_loss(logits, targets, args.rollouts,
                                            args.temperature, args.ce_anchor)
                else:
                    loss, parts = supervised_loss(logits, targets, fields, args.mode,
                                                  args.brier_w, args.rps_w)
                loss = loss / args.accum
            scaler.scale(loss).backward()
            for key, value in parts.items():
                running[key] += float(value)
            if (step + 1) % args.accum == 0 or step + 1 == len(order):
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                scaler.step(optimizer); scaler.update(); optimizer.zero_grad(set_to_none=True)
            if step % 100 == 0:
                summary = " ".join(f"{k}={v/(step+1):.4f}" for k, v in running.items())
                print(f"epoch={epoch} step={step}/{len(order)} {summary}", flush=True)
        metrics = evaluate(model, val, device)
        print(f"VALIDATION epoch={epoch} {json.dumps(metrics, sort_keys=True)}", flush=True)
        if metrics["macro_f1"] > best:
            best = metrics["macro_f1"]
            save_checkpoint(Path(args.out), model, args, metrics)

    if args.eval_test:
        test = EcrfDataset(split_parquet(data_dir, "test"), fields, args.max_chars)
        metrics = evaluate(model, test, device)
        print(f"TEST {json.dumps(metrics, sort_keys=True)}")
        (Path(args.out) / "test_metrics.json").write_text(
            json.dumps(metrics, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
