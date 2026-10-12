---
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
python evaluate.py --pred preds_test.parquet --pred_val preds_val.parquet     --gold test.jsonl --gold_val validation.jsonl
```
Le fichier de prédictions attendu par `evaluate.py` est un parquet
`doc_id, key, start, end, confidence[, value]` — tout système (encodeur ou LLM) s'y conforme.

Modèles vitrine : [`rntc/mc-bio-gliner-lymphome`](https://huggingface.co/rntc/mc-bio-gliner-lymphome)
(value-F1 ≈ 0.64) et [`rntc/mc-bio-gliner-lymphome-joint`](https://huggingface.co/rntc/mc-bio-gliner-lymphome-joint)
(≈ 0.66). Statut du gold : *silver-as-gold* (annotateur LLM). MIT, recherche.
