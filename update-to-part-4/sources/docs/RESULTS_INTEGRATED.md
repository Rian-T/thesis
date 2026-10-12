# Modèle intégré GLiNER + têtes de normalisation — RÉSULTATS (2026-07-22)

> UN seul modèle : GLiNER (détection native) + têtes de normalisation trainables, **finetuné
> end-to-end sur lymphome v5, SANS freeze**. À l'inférence : détecte SES spans puis normalise
> en un forward. `gliner2/*` intact (sous-classe/attache externe). Voir `INTEGRATED_PLAN.md`,
> archi : `figures/arch_norm.{tex,pdf,png}`.
> Baseline découplée (bi-encodeur MedEmbed gelé) = `RESULTS_NORM.md` (point de comparaison).

## Setup
- Init : **v5** (= V5FROMV3B, v3b déjà finetuné lymphome) et **v3b** (généraliste, ré-apprend détection).
- Finetune 2 epochs, enc_lr 1e-5 / head_lr 1e-4, loss = détection native + normalisation (têtes sur
  span_rep natif des spans gold). Têtes : CAT classif (similarité option) + NUM/ORD/DATE sélection.
- Éval : test 410, le modèle **détecte lui-même** (extract_entities, seuil 0.03) puis têtes normalisent.
  Métrique = accuracy (exact CAT/ORD/DATE ; within-10% NUM). Dénominateur = cibles gold (recall-like).

## Table principale (test 410, seuil 0.03)
| famille | Intégré-v5 | Intégré-v3b | span-brut top-1 | Qwen-9B |
|---|---|---|---|---|
| CAT | **0.638** | 0.637 | 0.308 | 0.358 |
| ORD | 0.693 | 0.658 | 0.630 | 0.734 |
| NUM | 0.537 | 0.536 | 0.551 | 0.613 |
| DATE (exact) | 0.203 | 0.158 | 0.206 | 0.389 |
| DATE (**année**, granularité-équitable) | 0.614 | **0.674** | — | 0.612 |
| **ALL exact** | 0.518 | 0.497 | 0.424 | **0.524** |
| **ALL équitable** (DATE année) | **0.621** | **0.626** | — | 0.579 |

## Verdicts
1. **Métrique granularité-équitable : les 2 modèles 150M single-pass BATTENT Qwen-9B** (0.62–0.63 vs
   0.58), ~60× plus petits, un seul forward, sortie structurée. Exact-match : parité (0.52 vs 0.52).
2. **CAT = le gain de l'approche** : 0.64 vs Qwen 0.36 (+0.28) et vs span-brut 0.31 (+0.33). La tête
   classe la valeur **implicite** (« patiente »→femme, contexte→statut) que ni le parsing ni le
   générateur ne canonisent.
3. **La tête évite un vrai piège (mesuré)** : tête ≠ top-1 dans ~45–53% des cas ; **RESCUE net ≈ +2000**
   (tête✓/top1✗ − tête✗/top1✓), dominé par CAT. → la tête n'est pas cosmétique.
4. **DATE : la granularité expliquait le trou.** Exact 0.16–0.20 mais niveau-année 0.61–0.67 (≈ Qwen) :
   ~1250–1570 « erreurs » = cible année seule (`2017`) vs prédiction précise du **même** événement
   (`2017-04-15`). Pour le groupage cohorte/survie (année), parité. Reste ~33% de vraies erreurs
   d'occurrence (role-binding 1L/2L/diag/décès).
5. **Détection = levier clé** : seuil 0.1→0.03 fait chuter la détection ratée 23%→9% (v5), **3.2%** (v3b).
   v3b (part du généraliste, ré-apprend la détection) **égale/dépasse** v5 → l'archi marche même sans
   détection lymphome préalable.

## vs baseline découplée (bi-encodeur gelé)
Comparaison indirecte (dénominateurs/métriques différents) mais le saut clé est sur la **qualité
oracle gold-span** : intégré val 0.86 (NUM 0.92, DATE 0.70) vs découplé oracle 0.66 (NUM 0.51, DATE
0.47) — les **reps natives GLiNER + finetune no-freeze** normalisent bien mieux *à span donné*.

## Frontière restante (leviers identifiés, chiffrés)
- **NUM** 0.54 vs Qwen 0.61 : le bon nombre pas toujours détecté / mal sélectionné.
- **DATE role-binding** (~33% mauvaise année) : lier la date au bon champ (1L vs 2L) via contexte/section.
- **Fix propre (non fait) = entraîner les têtes sur les VRAIS spans prédits** (pré-calculés/cachés sur
  le train, 1 passe d'inférence) au lieu des spans gold → aligne train/test, apprend la désambiguïsation.
  ⚠️ La variante cosine (`field_candidates`) testée = mauvais proxy détecteur (val 0.066 NUM) → rejetée.
  Idée complémentaire : 3e signal position/section du span dans la tête sélection.
