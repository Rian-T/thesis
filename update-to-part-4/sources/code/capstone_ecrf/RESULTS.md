# Capstone eCRF lymphome — résultats canoniques

> Chiffres **faisant autorité** pour la thèse (chapitre *Evaluating Open-Vocabulary
> Extraction*, table capstone). Reproductibles par `./reproduce.sh` (voir `HANDOFF.md`).
> Métrique = value-F1 (token Jaccard ≥ 0,5) et span-F1 **après field competition**,
> seuil de confiance sélectionné une seule fois sur les 100 docs de validation,
> reporté sur les 410 docs de test (le test n'entre JAMAIS dans le choix du seuil).

## Table de la thèse (après competition, 410 test)

| Modèle | Params | Value-F1 | Span-F1 | Exact |
|---|---|---|---|---|
| **Question answering** | | | | |
| ModernCamemBERT | 150 M | 0.336 | 0.310 | 0.223 |
| ModernCamemBERT-bio | 150 M | 0.417 | 0.362 | 0.273 |
| **Open-vocabulary extraction** | | | | |
| GLiNER-BioMed | 184 M | 0.380 | 0.397 | 0.226 |
| **ModernCamemBERT-bio-gliner** (= `V5FROMV3B`) | 150 M | **0.640** | 0.503 | 0.454 |
| **Generation** | | | | |
| Qwen3.5-0.8B | 0.8 B | 0.628 | 0.543 | 0.444 |
| Qwen3.5-2B | 2 B | 0.645 | 0.559 | 0.462 |
| Qwen3.5-4B | 4 B | **0.658** | **0.567** | **0.474** |
| Qwen3.5-9B | 9 B | 0.650 | 0.558 | 0.465 |

Variante **joint-supervision** (hors table, citée dans le texte) = `V5MIX6` :
**value-F1 0.657**, à parité avec Qwen3.5-4B (diff appariée −0,0005, IC95 [−0,0075, 0,0072]).

## Ce que reproduit `reproduce.sh` aujourd'hui (depuis les parquets embarqués)

| Système (nom dans `derive_capstone.py`) | Run | value-F1 | span-F1 |
|---|---|---|---|
| `MedGLiNER` | `V5FROMV3B` | 0.6437 | 0.5065 |
| `Joint-supervision MedGLiNER` | `V5MIX6` | 0.6575 | 0.5084 |
| `Qwen3.5-9B` | `de1540v2` | 0.6501 | 0.5583 |

> ⚠️ **Petit écart à noter** : la reproduction donne `V5FROMV3B` = **0.6437** alors que
> la table imprimée arrondit à **0.640**. Joint (0.6575 → 0.657) et Qwen3.5-9B
> (0.6501 → 0.650) collent parfaitement. L'écart de 0.640 vs 0.644 sur la seule ligne
> V5FROMV3B est à trancher avant tout re-dépôt : soit la table cite un point de
> fonctionnement légèrement différent, soit elle est à réaligner sur `derive_capstone.py`.

## Prise de recul (déjà écrite dans la thèse)

- Un encodeur de **150 M** arrive à **0,018 value-F1** du meilleur générateur
  (Qwen3.5-4B, 4 B) — **27× plus petit**.
- Les générateurs gardent l'avantage sur le **span-F1** (0,567 vs 0,503).
- L'adaptation du mélange d'entraînement (joint-supervision, `V5MIX6`) **ferme l'écart**
  value-F1 (parité avec Qwen3.5-4B) sans franchir l'écart span.
- Le jeu eCRF lymphome est **entièrement synthétique** (`rntc/lymphome-synth-v4`),
  pas de données hospitalières réelles — c'est la prémisse, pas un caveat.
