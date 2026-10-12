# HANDOFF — état lymphome eCRF (capstone) au 2026-07-22

> **À LIRE EN PREMIER si tu reprends le travail sur le capstone eCRF lymphome.**
> Le `CLAUDE.md` à la racine de `french-medgliner` date du **11–15 juin 2026** et
> s'arrête à v3d/v3e et à un lymphome où « tout converge ~0,32 » (ancienne métrique
> span-overlap `eval_lymphome.py`). **Cette photo est PÉRIMÉE pour le capstone.** La
> lignée qui a réellement alimenté la thèse est la lignée **V5** décrite ici, avec une
> métrique différente (**value-F1 field-level après field competition**). Ce dossier
> `capstone_ecrf/` est la source de vérité pour ces chiffres et il est **autosuffisant
> et reproductible**.

---

## 1. Ce qui a changé depuis le CLAUDE.md de juin

- La tâche capstone n'est plus notée par `gen/lymphome/eval_lymphome.py` (span-overlap,
  chiffres ~0,32). Elle est notée par un **protocole value-F1 field-level** :
  1. `top1` (un pick par champ) → `compete` (**field competition** : un span ne peut
     remplir qu'un champ, résolu par confiance) ;
  2. seuil de confiance choisi **une fois sur la validation** (100 docs) en value-F1 ;
  3. value-F1 / span-F1 / exact reportés sur le **test (410 docs)** à ce même seuil.
- Ce protocole vit dans **`research/lymphome/score_unified.py` + `validation_protocol.py`
  + `plots/part_3/data/chapter7/derive_capstone.py`**. Ces fichiers **n'existaient PAS
  sur le cluster** (ils vivent dans le repo thèse, gitignoré) — c'est la raison de fond
  pour laquelle une reprise depuis le cluster était « perdue ». Ils sont maintenant ici.

## 2. Les deux modèles vitrine (finetunés sur l'eCRF lymphome)

Les DEUX sont adaptés à la tâche — c'est le couple de comparaison **supervision simple
vs supervision jointe**, pas un modèle « propre » contre un modèle « triché ».

| Rôle | Run (output dir) | init | data d'entraînement | Score | Lanceur |
|---|---|---|---|---|---|
| Supervision simple | `gliner2-lym-V5FROMV3B/best` | `gliner2-v3b-pristine/best` | `lymphome/training_data_lymV5_{train,val}.jsonl` (lymphome seul) | value-F1 **0.640** / span 0.503 | `gen/lymphome/train_lymv3b_jz.sbatch` |
| Supervision jointe | `gliner2-lym-V5MIX6/best` | `gliner2-v3e-pristine/best` | `lymphome/training_data_lymMIX_{train,val}.jsonl` (50/50 lym + généraliste) | value-F1 **0.657** (parité Qwen3.5-4B) | `gen/lymphome/train_mix6_jz.sbatch` |

- Outputs sous `$SCRATCH/onto/medembed-outputs/` (= `/lustre/fsn1/projects/rech/rua/uvb79kr/onto/medembed-outputs/`).
- Backbone commun = **MedEmbed-v9 stage-1** (`medembed-v9/stage1/final`, 149 M), hérité via v3b/v3e.
- Hyperparamètres communs : 8 epochs, `--patience 6`, `batch_size 4`, `max_width 24`,
  `encoder_lr 1e-5`, `task_lr 3e-4`, `metric_for_best = eval_loss`, `save_best`.
- Le checkpoint qui produit les scores de table = le sous-dossier **`best/`** (c'est ce
  que le registre d'alias de `eval_lymphome.py` charge : `lym-V5FROMV3B → .../best`,
  `lym-V5MIX6 → .../best`), PAS `final/` ni les `checkpoint-epoch-*`.

## 3. Modèles PUBLIÉS sur le Hub (2026-07-22, publics)

Les deux `best/` ont été poussés tels quels (bytes exacts, portables — les poids de
l'encodeur MedEmbed sont inclus dans `model.safetensors`, le chemin backbone du
`config.json` a été nettoyé) :

- **https://huggingface.co/rntc/mc-bio-gliner-lymphome** ← `gliner2-lym-V5FROMV3B/best` (0.640)
- **https://huggingface.co/rntc/mc-bio-gliner-lymphome-joint** ← `gliner2-lym-V5MIX6/best` (0.657)

Rechargement :
```python
from gliner2 import GLiNER2
m = GLiNER2.from_pretrained("rntc/mc-bio-gliner-lymphome")   # ou -joint
```
Upload/push depuis le nœud de login avec le proxy IDRIS :
`export http_proxy=http://prodprox.idris.fr:3128 https_proxy=http://prodprox.idris.fr:3128 HF_HUB_OFFLINE=0`
et le token dans `$HF_HOME/token` (user HF = `rntc`, rôle write).

## 4. Générateurs LLM de la table (baseline haute)

- Colonne « Generation » = **Qwen3.5-{0.8,2,4,9}B**, run **`de1540v2`** (PAS les vieux
  `lp410`). Meilleur = Qwen3.5-4B 0.658 ; 9B = 0.650 (au-dessus de nous en value-F1).
- Preds Qwen embarqués ici : `preds_lym_llm_qwen3.5-9b-de1540v2{,-val}.parquet`
  (seul le 9B est rejoué par `derive_capstone.py` pour l'IC apparié ; les autres tailles
  viennent de `canonical_scores.json`).
- Recette d'inférence LLM côté cluster : `gen/lymphome/infer_llm2.py` +
  `QWEN35_LORA_VLLM_RECIPE.md` à la racine.

## 5. Reproduire les chiffres (turnkey, ce dossier est autosuffisant)

```bash
cd $WORK/french-medgliner/capstone_ecrf
./reproduce.sh            # affiche le JSON complet (systèmes × {top1, competition})
```
`reproduce.sh` fixe `PYTHONPATH` sur ce dossier et lance `derive_capstone.py` avec le
python projet (`envs/tabib-C39hfyYp-py3.12`). Contenu embarqué :
`research/lymphome/{score_unified.py, validation_protocol.py, data/{v5_val,v5_test}.jsonl,
data/preds_*.parquet}` + `plots/part_3/data/chapter7/derive_capstone.py`. Les chiffres
attendus et un écart à trancher (0.640 vs 0.6437 sur V5FROMV3B) sont dans **`RESULTS.md`**.

## 6. Où sont les scripts vivants (dans `../gen/lymphome/`, NE PAS repartir de zéro)

- **Registre modèle→checkpoint** : `eval_lymphome.py` (dict `MODELS`, alias `lym-V5*`).
- **Entraînement eCRF** : `train_lymv3b_jz.sbatch` (V5FROMV3B), `train_mix6_jz.sbatch` (V5MIX6),
  via `GLiNER2/v3/train_stage2.py`.
- **Prépa données** : `prep_data.py`, `labels.py` (89 champs → labels FR), `convert_to_gliner_train.py`.
- **Inférence GLiNER incrémentale + resume** (écueil 27 s/doc × 410 = 3 h) : `eval_lymphome.py`
  écrit tous les 50 docs → lancer en **qos normale**, pas dev 2 h.
- **Inférence LLM** : `infer_llm2.py`.
- **Diagnostic erreurs** (localise-bien / sur-tire / mal-type) : `diagnose.py`.
- ⚠️ La forêt de `gen/lymphome/add_*_alias.py`, `patch_*.py`, `fix_*.py`, `*.bak*` sont
  des mutateurs one-shot / sauvegardes **déjà appliqués** — inertes, ne pas s'y fier.

## 7. Prochaines pistes ouvertes (état thèse, à confirmer avec Rian)

- Trancher l'écart 0.640 / 0.6437 sur V5FROMV3B (§ RESULTS.md) avant tout re-dépôt.
- Scaling encodeur (span-F1 reste derrière les générateurs : 0.503 vs 0.567).
- Ancrage humain sur les types nouveaux (n≈120) — le seul trou méthodo qui pouvait faire
  rejeter le paper GLiNER, mis de côté (« pas d'humain pour le moment »).
- `V5FROMV3F` / `V5MIX` existent aussi dans les outputs mais **ne sont PAS** dans la table
  (variantes d'ablation) — ne pas les confondre avec les deux modèles vitrine.
