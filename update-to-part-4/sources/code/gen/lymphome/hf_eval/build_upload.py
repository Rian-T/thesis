"""Build and upload rntc/lymphome-synth-v5-eval (train / validation / test).

Same corpus and columns as rntc/lymphome-synth-v5, but with the exact
train / validation / test split used for the eCRF capstone:
  - test        = the 410 held-out documents (identical to v5),
  - validation  = 100 documents drawn at random (seed 0) from the 1640 train
                  docs, used to select the confidence threshold,
  - train       = the remaining 1540 documents.
The validation split is disjoint from train (it is removed from it), so the
three splits partition the 2050 documents. The eval scripts evaluate.py and
predict.py are uploaded alongside the data.

The validation split must be exchangeable with the test split, otherwise a
threshold chosen on it does not transfer. Taking "the first 100 by numeric id"
does not satisfy this: those are the documents generated first and they carry
16.5% more filled fields per document than the test split (47.7 vs 40.9), so a
threshold tuned on them is tuned for a denser regime. A random draw sits at
-4.0% (39.3). Hence RandomState(0) below -- do not replace it with a slice.
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from labels import LABELS  # noqa: E402

HERE = Path(__file__).resolve().parent
B = "/lustre/fsn1/projects/rech/rua/uvb79kr/onto/medembed-outputs/lymphome"
PROD = "/lustre/fswork/projects/rech/rua/uvb79kr/biomed-fr-v4/lymphome_v4/outputs/prod_20260527_121452.jsonl"
REPO = "rntc/lymphome-synth-v5-eval"
N_VAL = 100

FIELD_LABELS = {k: {"label": v["label"], "desc": v["desc"], "section": v["section"]}
                for k, v in LABELS.items()}

README = """---
license: mit
language: fr
task_categories: [token-classification]
tags: [gliner, biomedical, french, lymphoma, ner, ecrf, synthetic, span-localized]
---

# lymphome-synth-v5-eval — eCRF lymphome, splits train/validation/test + éval

Même corpus et mêmes colonnes que [`rntc/lymphome-synth-v5`](https://huggingface.co/datasets/rntc/lymphome-synth-v5)
(2050 dossiers cliniques lymphome synthétiques, ~89 champs eCRF, gold **span-localisé** TAPDL),
mais avec le **split exact train / validation / test** utilisé pour l'évaluation eCRF, plus un
**script d'évaluation autosuffisant**.

## Splits
- **test** — 410 dossiers tenus à l'écart (identiques à v5).
- **validation** — 100 dossiers **tirés au hasard** (seed 0) parmi les 1640 d'entraînement,
  servant à **choisir le seuil de confiance** (value-F1) ; disjoints de `train`.
- **train** — les 1540 dossiers restants.

> ⚠️ **Changement du 2026-07-28 — la validation a changé de composition.** La première version
> définissait la validation comme « les 100 premiers par id numérique ». Ces dossiers sont ceux
> générés en premier et ils portent **16,5 % de champs remplis en plus par dossier** que le test
> (47,7 contre 40,9) : un seuil calibré dessus est calibré pour un régime plus dense et ne se
> transfère pas. Le tirage aléatoire actuel est à −4,0 % (39,3). **`train` et `test` sont
> inchangés** — seule la frontière train/validation bouge, et tout seuil choisi avec l'ancienne
> validation est à recalibrer. **`test` est inchangé** (les mêmes 410 dossiers, donc les chiffres
> publiés restent comparables) ; `train` et `validation` repartitionnent les mêmes 1640 dossiers,
> mais ce ne sont plus les mêmes 100 qui sont mis de côté.

## Colonnes (par dossier)
`id`, `sample_index`, `pmc_uid`, `split`, `text`,
`gold` (`{clé_eCRF: [[start, end, texte_du_span], ...]}`, offsets caractères dans `text`),
`field_labels` (`{clé: {label, desc, section}}`), `timeline_json`, `documents_json`,
`cohort_label`, `annotation_v4_json`.

## Évaluation
`evaluate.py` (scorer autosuffisant) et `predict.py` (inférence GLiNER2) sont inclus dans le dépôt.

L'eCRF demande **une valeur par champ** : chaque système s'engage sur sa prédiction la plus
confiante par (dossier, champ). Comptabilité au niveau (dossier, champ) — value-F1 (Jaccard de
tokens normalisés ≥ 0.5) et span-F1 (chevauchement ≥ 1 caractère). L'ablation `compete` impose
qu'un empan ne documente qu'un champ. Le seuil est choisi **sur la validation**, jamais sur le test.

```bash
# 1. prédictions (GLiNER2) sur validation puis test
python predict.py --model rntc/mc-bio-gliner-lymphome --split validation --out preds_val.parquet
python predict.py --model rntc/mc-bio-gliner-lymphome --split test       --out preds_test.parquet

# 2. score (seuil choisi sur la validation, reporté sur le test)
python evaluate.py --pred preds_test.parquet --pred_val preds_val.parquet \
    --gold test.jsonl --gold_val validation.jsonl
```
Le fichier de prédictions attendu par `evaluate.py` est un parquet
`doc_id, key, start, end, confidence[, value]` — tout système (encodeur ou LLM) s'y conforme.

Modèles vitrine : [`rntc/mc-bio-gliner-lymphome`](https://huggingface.co/rntc/mc-bio-gliner-lymphome)
(value-F1 ≈ 0.64) et [`rntc/mc-bio-gliner-lymphome-joint`](https://huggingface.co/rntc/mc-bio-gliner-lymphome-joint)
(≈ 0.66). Statut du gold : *silver-as-gold* (annotateur LLM). MIT, recherche.
"""


def load_gold(split):
    return {json.loads(l)["id"]: json.loads(l)["gold"]
            for l in open(f"{B}/lymphome_{split}_v2.jsonl", encoding="utf-8")}


def main():
    train_gold, test_gold = load_gold("train"), load_gold("test")
    val_ids = set(np.random.RandomState(0).choice(sorted(train_gold), N_VAL, replace=False).tolist())

    id2split, all_gold = {}, {}
    for rid in train_gold:
        id2split[rid] = "validation" if rid in val_ids else "train"
        all_gold[rid] = train_gold[rid]
    for rid in test_gold:
        id2split[rid] = "test"
        all_gold[rid] = test_gold[rid]

    rows = {"train": [], "validation": [], "test": []}
    with open(PROD, encoding="utf-8") as f:
        for line in f:
            try:
                rec = json.loads(line)
            except Exception:
                continue
            rid = f"lym_{rec['sample_index']}"
            if rid not in all_gold:
                continue
            split = id2split[rid]
            used = {k: FIELD_LABELS[k] for k in all_gold[rid] if k in FIELD_LABELS}
            rows[split].append({
                "id": rid,
                "sample_index": rec["sample_index"],
                "pmc_uid": rec.get("pmc_uid", ""),
                "split": split,
                "text": rec["full_clinical_text"],
                "gold": json.dumps(all_gold[rid], ensure_ascii=False),
                "field_labels": json.dumps(used, ensure_ascii=False),
                "timeline_json": json.dumps(rec.get("timeline", {}), ensure_ascii=False),
                "documents_json": json.dumps(rec.get("documents", []), ensure_ascii=False),
                "cohort_label": rec.get("timeline", {}).get("cohort_label", ""),
                "annotation_v4_json": json.dumps(rec.get("annotation", {}), ensure_ascii=False),
            })

    outdir = Path(f"{B}/v5_eval_build"); outdir.mkdir(parents=True, exist_ok=True)
    files = {}
    for split in ("train", "validation", "test"):
        p = outdir / f"{split}.jsonl"
        with open(p, "w", encoding="utf-8") as f:
            for r in rows[split]:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        files[split] = str(p)
        print(f"{split}: {len(rows[split])} dossiers")
    assert len(rows["validation"]) == N_VAL
    assert not ({r["id"] for r in rows["train"]} & {r["id"] for r in rows["validation"]})

    if "--dry_run" in sys.argv:
        print("dry run: built local jsonl, no upload")
        return

    from datasets import load_dataset
    from huggingface_hub import HfApi
    ds = load_dataset("json", data_files=files)
    api = HfApi()
    api.create_repo(REPO, repo_type="dataset", private=False, exist_ok=True)
    ds.push_to_hub(REPO)
    for fn in ("evaluate.py", "predict.py"):
        api.upload_file(path_or_fileobj=str(HERE / fn), path_in_repo=fn,
                        repo_id=REPO, repo_type="dataset")
    api.upload_file(path_or_fileobj=README.encode(), path_in_repo="README.md",
                    repo_id=REPO, repo_type="dataset")
    print(f"=== UPLOADÉ : https://huggingface.co/datasets/{REPO} ===")


if __name__ == "__main__":
    main()
