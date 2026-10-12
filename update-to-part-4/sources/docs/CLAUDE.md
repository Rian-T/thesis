# MedEmbed & GLiNER2 FR Biomédical — état au 2026-06-11

> 🚨 **PÉRIMÉ POUR LE CAPSTONE eCRF LYMPHOME (mis à jour 2026-07-22).** Ce fichier s’arrête à v3d/v3e (juin) et à un lymphome « ~0,32 » (ancienne métrique span-overlap). La lignée qui a réellement alimenté la thèse est la lignée **V5** (value-F1 field-level après field competition). **Source de vérité + reproduction turnkey : `capstone_ecrf/HANDOFF.md`** (et `capstone_ecrf/RESULTS.md`, `./capstone_ecrf/reproduce.sh`). Modèles publiés : `rntc/mc-bio-gliner-lymphome` (V5FROMV3B, 0.640) et `rntc/mc-bio-gliner-lymphome-joint` (V5MIX6, 0.657). Le reste de ce document reste valide pour tout ce qui N’EST PAS le capstone eCRF.**

---


> **Historique archivé** dans `archive/` : `CLAUDE_2026-04-09.md` (état initial), `AUDIT_2026-05-11.md` (audit 4 sous-agents PARTIELLEMENT ERRONÉ), `CLAUDE_2026-05-11.md` (post-audit, hypothèses réfutées), `CLAUDE_2026-05-23.md` (état pristine v2/v3, avant v3b/v3c).
>
> **Voir aussi** : `biblio.md` (SOTA), `sota_gliner_prompts/` (prompts verbatim GLiNER/GLiNER2/NuNER/OpenBioNER/GLiNER-Biomed), `gen/v3d/DESIGN.md` (design v3d data-driven).

---

## 🚀 HANDOFF — état pour reprise (2026-06-11) — LIRE EN PREMIER

### Nature du projet (NE PAS se tromper de cible)
**Projet de RECHERCHE → paper EACL + modèle released MIT, dans la lignée GLiNER/NuNER/GLiNER-biomed. PAS un produit clinique.** Conséquences qui ont déjà causé une mauvaise analyse :
- La cible est un **GLiNER FR biomed généraliste open-vocab** (l'utilisateur définit ses types à l'inférence). Optimiser la **généralisation aux types nouveaux/arbitraires** EST le bon objectif (≠ produit clinique qui voudrait juste le schéma clinique standard).
- **NE PAS s'entraîner sur le gold des benchmarks** (CAS/E3C/QUAERO train splits) — ça casse la claim zero-shot et c'est contraire à la lignée GLiNER (synthétique/distillation). Le gold humain sert UNIQUEMENT à (a) éval, (b) valider le juge.
- **"Perdre les benchmarks NER standards" n'est PAS une faiblesse mais LE résultat central** : les benchmarks mesurent l'alignement de convention, pas la généralisation.

### Le contribution principal du paper = l'ÉVAL, pas le modèle
Le modèle (v3b/v3d, 149M, multi-task) est l'artefact support. Le cœur citable = **l'éval LLM-judge reference-free** (`gen/judge_eval/`) qui montre que les modèles gagnant les benchmarks (SE-v1, gliner2-large 560M) sont **convention-overfit** alors que de petits modèles FR multi-task **généralisent mieux aux types nouveaux**. Tout est dans les sections ⭐ ci-dessous.

### Statut DONE vs TODO (paper)
| Workstream | Statut |
|---|---|
| Éval communauté LLM-judge (5-7 modèles, MAP commun/nouveau, Δoverfit) | ✅ FAIT |
| Robustesse clinique clean/dégradé (diff-in-diff) | ✅ FAIT |
| Éval classification (MORFITT/DiaMED) | ✅ FAIT |
| A/B backbone (MedEmbed-v9 > ModernCamemBERT-bio) | ✅ FAIT |
| **Validation du juge vs gold humain** (Qwen κ0.53 / MedGemma κ0.61) | ✅ FAIT |
| **Test self-preference** (MedGemma seul re-juge → rankings tiennent, plus nets) | ✅ FAIT (2026-06-11) |
| **v3d** (data-driven definitive : densité modérée + CIM-10 classif + brouillon + 28% nég) | ✅ **entraîné 1ep (v3d-e1) ET 2ep (v3d-pristine)**. Verdict ↓ |
| → **v3d est LE modèle multi-task vitrine** : gagne les DEUX tâches de classif. **MORFITT 0.505/0.492 (meilleur de tous), DiaMED 0.539 acc/0.282 macro (meilleur de tous, fix CIM-10 renforcé à 2ep vs v3b/v3c 0.01-0.08).** MAIS **pire sur le NER** : benchmark macro strict **0.261 (dernier)**, cas1 = **0.000** (collapse calibration/convention) ; novel-NER régressé (v3d-e1 0.359 < v3c-medembed-e1 0.394 à budget égal). **Trade-off net : multi-task/classif ↑↑, NER open-vocab ↓.** → v3b reste le meilleur généraliste NER ; **v3d = le meilleur multi-task/classif.** Le contraste benchmark-pire / classif-meilleur **renforce la thèse** (benchmarks ≠ capacité). |
| **GLiNER-biomed baseline** (lignée) | ✅ **FAIT (2026-06-13)** : inféré + plié dans le pool communauté final (146k). **PIRE généraliste de tous** (novel 0.121, Δoverfit +0.269). |
| **Tableau benchmarks standards 6-benchs** (run final + v3d) | ✅ **FAIT (2026-06-13)** : `20260613_022436_CLEAN`, classement INVERSE du communauté (SE-v1 0.389 > … > v3d 0.266). gliner-biomed PAS dedans (package GLiNER v1 ≠ fork). |
| **Éval communauté FINALE 10 modèles** (gliner-biomed + v3d-2ep, juge Qwen) | ✅ **FAIT (2026-06-13)** : `verdicts_qwen_10m.jsonl`, report.md à jour. |
| **Structured-extraction eval (3e tâche GLiNER2)** | ✅ **FAIT (2026-06-13)** : LLM-judge field-level reference-free. **v3d gagne (précision 0.757)** > v3c 0.741 > gliner2-large 0.701 > v3b 0.695. `gen/judge_eval/eval_structured.py`. |
| Analyse convention-vs-erreur (κ 0.53 expliqué : 85% convention / 11% erreur juge) | ✅ FAIT (2026-06-13) |
| 1 trou méthodo restant : **ancrage humain types nouveaux** (n≈120) | ⏳ "pas d'humain pour le moment" |

### v3d — où ça en est et la SUITE EXACTE
- **Annotation** : `gliner2-v3d/annotations_v3d.jsonl` ~91.5k/102.9k (job 154969 RUNNING dev qos finit les ~11k restants = surtout négatifs). Quand >100k ou fini :
- **Downstream à enchaîner** (réutiliser/adapter les scripts v3c, JAMAIS partir de zéro) :
  1. **filter** : adapter `gen/v3c/filter_offline_v3c.py` → `--input gliner2-v3d/annotations_v3d.jsonl --output gliner2-v3d/annotations_v3d_grounded.jsonl` (garde négatifs `min_entities=0`, grounding entities+relations).
  2. **assemble** : adapter `gen/v3c/assemble_training_v3c.py` + **AJOUTER un snap des `true_labels` CIM-10 sur les 22 `CIM10_CHAPTERS_FR` exacts de `gen/v3d/prompt_v3d.py`** (match exact, drop off-vocab — le smoke a montré que le LLM paraphrase parfois les chapitres) → `training_data_v3d_{train,val}.jsonl`.
  3. **train stage-1** : `sbatch GLiNER2/v3/train_v3c.py --backbone medembed-v9 --train .../training_data_v3d_train.jsonl --val .../training_data_v3d_val.jsonl --output .../gliner2-v3d-pristine --num_epochs 2`. ⚠️ file 4×H100/1×H100 normale = ~2 jours d'attente actuellement → si bloqué, faire **1 epoch dev qos** (comme l'A/B backbone).
  4. **éval v3d** : l'ajouter à `run_inference.py` MODELS + `score.py` MODELS, re-pool + re-adjudicate (Qwen) le pool communauté, + `classify_eval.py`. Hypothèse : v3d ≈ v3b sur NER, mais **gagne la classif CIM-10/DiaMED** (le fix) + robustesse.
- **v3d = "polish two-stage"** : stage-2 = calibration/hard-neg/replay (PAS une re-spécialisation clinique — ça a régressé en v3c). Voir `gen/v3d/DESIGN.md`.

### Trou méthodo restant (pour blinder le paper)
1. **Ancrage humain sur les types NOUVEAUX** : le gold ne couvre que les types communs/cliniques ; la claim phare (généralisation aux nouveaux) n'a pas d'ancrage humain direct. L'utilisateur a dit **"pas d'humain pour le moment"** → mis de côté, à reproposer (un mini-pass humain n≈120 sur des verdicts de types nouveaux est le plus rentable quand possible). **= LE seul vrai point qui peut faire rejeter le paper.**
2. ✅ **Convention-vs-erreur FAIT (2026-06-13)** : 85% des désaccords juge-gold = convention, 11% = erreur juge (`analyze_disagreements.py`). Le κ 0.53 est expliqué/blindé.

### ⭐ Workstream LYMPHOME (`rntc/lymphome-synth-v4`) + v3e (2026-06-15) — EN COURS
**Jeu d'éval registre clinique** (2050 docs synthétiques lymphome multi-docs, ~89 champs eCRF, gold span-localisé). Pipeline `gen/lymphome/` : `labels.py` (dico 89 clés→labels FR), `prep_data.py` (split 1640/410 seed 0), `eval_lymphome.py` (NER open-vocab par champ, span-overlap F1, gère fork + GLiNER v1), `convert_to_gliner_train.py`, `finetune_gliner_biomed.py`, `diagnose.py`.
- **Éval = 2 tableaux, tous modèles, test 410.** Zero-shot : gliner-biomed 0.174 > v3b 0.150 > SE-v1 0.138 > v3c-stage2 0.128 > v3d 0.106. **Finetuné : TOUT converge ~0.32** (gliner-biomed-ft 0.329 ≈ v3c-stage2-ft 0.326 ≈ v3d-ft 0.319 ≈ v3b-ft 0.318). Reports : `lymphome/report_lymphome_{zeroshot,finetune}.md`.
- **VERDICTS clés** : (1) finetuning ×3 et **lave la base** → un **stage-2 clinique au pretraining ne vaut PAS le coup** (v3c-stage2-ft ≈ v3d-ft). (2) Diagnostic `diagnose.py` : nos modèles **localisent** bien (anyfield-R ~0.29) mais **sur-tirent + mal-typent** (typing-gap v3d 0.159). v3d < v3b car sa tête de typage NER est émoussée (multi-task) — **cohérent : v3d = vitrine multi-task, PAS ultimate NER.**
- **2 manques identifiés → motivent v3e** : (a) **primitives génériques sous-entraînées** (dates/mesures/noms propres, car annotation UMLS-steered) ; (b) **role-binding faible** (date-diagnostic vs date-décès = même span, contexte discrimine). Test flat-NER vs `extract_json` : le schéma groupé récupère **+39% de liages corrects** mais précision ↓ (décodeur structures sous-entraîné) → mécanisme OK mais immature.
- **⚠️ Écueil eval lymphome** : inférence 89 types × docs 5.7k tokens = **27s/doc** → 410 docs = 3h ; parquet écrit à la fin = perte au timeout. **FIX appliqué** : `eval_lymphome.py` écrit **incrémental + resume** (checkpoint 50 docs). gliner2-large (560M) OOM → `BY_SECTION` + `MAX_CHARS` truncation. Lancer en **qos normale** (pas dev 2h).

### v3e — état + SUITE EXACTE (DESIGN dans `gen/v3e/DESIGN.md`)
v3e = réponse data-driven aux 2 manques. **Recette** : prompt 2-buckets (biomédical ET primitives génériques, LLM-driven **zéro hardcode**) + structures à **champs reliés** (role-binding). `gen/v3e/{DESIGN.md, prompt_v3e.py, annotate_v3e.py, analyze_smoke.py}`.
- ✅ **Smoke 36 docs PASS** (2026-06-15) : génériques 92% (nom propre/quantité/%/mesure+unité/date/durée), biomédical conservé 94%, structures reliées riches (« groupe témoin vs intervention », « prévalence max/min »), CIM-10 32/36.
- ✅ **Annotation complète FAITE (2026-06-17)** : 101 304/102 864 chunks (reste = trop longs skippés), 100% valides → `gliner2-v3e/annotations_v3e.jsonl`.
- ✅ **filter** : `annotations_v3e_grounded.jsonl` (101 304 docs, 22% nég, 635k entités, 2.2M mentions, 676k relations groundées).
- ✅ **assemble** (`gen/v3e/assemble_training_v3e.py`, snap CIM-10) : `training_data_v3e_{train,val}.jsonl` = **97 252 / 4 052**, 63 193 tâches CIM-10. **Vérifié : génériques 93% + biomédical 99%** dans le train (date 13.7k, nom propre 11k, mesure+unité 6k, durée, quantité, âge, valeur-labo, %).
- 🔄 **train base LANCÉ** : job 554994 (`gen/v3e/train_v3e.sbatch`, medembed-v9, 2ep, 1×H100 normale) → `gliner2-v3e-pristine`.
- ⏳ **train large À FAIRE** (demande user) : `moderncamembert-bio-large` PAS sur disque → télécharger `almanach/ModernCamemBERT-bio-large` (HF, login) + l'ajouter au dict `BACKBONES` de `GLiNER2/v3/train_v3c.py` → `gliner2-v3e-large`.
- **éval sauce B (quand modèles prêts)** : communauté novel-types (doit MONTER) + **lymphome en mode `extract_json`** (pas flat-NER) + classif. Ajouter v3e à `run_inference.py`/`score.py`/`eval_lymphome.py`. **Surveiller que la tête NER ne s'émousse pas** (défaut v3d).

---

## Résumé exécutif

**Objectif** : GLiNER2 FR biomed multi-task généraliste (NER open-vocab + classif + structures + relations) qui batte SE-v1 (macro 0.389) **largement**, sans overfit bench. **Pas encore atteint** — voir verdict ci-dessous.

**Classement actuel (eval suite v3 "clean", run `20260604_194842_CLEAN`, 5 modèles × 6 benchs)** :

| Modèle | strict | type-agn (det-recall) | overlap | gap-calib | Note |
|---|---|---|---|---|---|
| **SE-v1** | **0.389** | **0.481** | 0.469 | 0.069 | ⭐ meilleur, ancien 2-stage NER-only |
| MedGLiNER-v3b | 0.350 | 0.433 | 0.430 | 0.059 | stage-1 v3b |
| **v3c-pristine** | 0.368 | 0.431 | 0.434 | 0.128 | ⭐ notre meilleur "maison", stage-1 v3c, multi-task |
| GLiNER2-large (560M) | 0.345 | 0.456 | 0.406 | 0.008 | baseline fastino |
| v3c-stage2-mix50 | 0.348 | 0.395 | 0.413 | 0.097 | stage-2 clinique → **régression** |

**Verdict** : ni v3c stage-1 ni stage-2 ne battent SE-v1. Le fix densité a amené v3c-pristine au niveau de v3b en det-recall (~0.43) mais **pas vers SE-v1 (0.481)**. Le stage-2 clinique dense a **régressé** le généraliste (det-recall 0.431→0.395) en le spécialisant sur le registre clinique.

**MAIS découverte importante** : le gap macro vs SE-v1 est **entièrement porté par cas1 + frasimed**, et y est largement un problème de **calibration** (nos modèles sous-tirent à t=0.5, il leur faut t=0.1). Sur EMEA/MEDLINE/cas2 on est à parité ou devant. → la prochaine piste est la **re-calibration**, pas un nouveau training. Voir Next Steps.

**MedEmbed-v9** (embeddings) reste stable et publiable : `medembed-v9/stage1/final` (149M, SOTA FR biomed pour la taille).

### ⭐ Validation du juge LLM (2026-06-10) — paper EACL, levier d'acceptation #1
Idée : valider le juge contre le **gold humain expert existant** (QUAERO/CAS/E3C-layer1) plutôt qu'une annotation fraîche. Probe = 4000 items (2000 spans gold positifs + 2000 négatifs cross-type). `gen/judge_eval/judge_gold_validation.py` + `inter_judge.py`.

| Juge (famille) | κ vs humain | e3c κ (gold propre) | spécificité |
|---|---|---|---|
| Qwen3-235B (Alibaba MoE) | 0.53 | 0.80 | 0.967 |
| MedGemma-27B (Google, médical) | 0.61 | 0.87 | 0.921 |

**Accord inter-juges Qwen↔MedGemma : accord 0.877, κ 0.728** (substantial). Deux familles indépendantes convergent → instrument fiable.

#### ⭐⭐ Analyse convention-vs-erreur (2026-06-13) — le κ 0.53 EXPLIQUÉ, pas subi
`gen/judge_eval/analyze_disagreements.py` : méta-juge Qwen catégorise les **932 désaccords** juge↔gold (23.3% du probe 4000) par une question DÉFINITIONNELLE (la description neutre du type licencie-t-elle le label gold ? → moins circulaire que re-juger).

| Cause du désaccord | part |
|---|---|
| **convention_gold** (gold suit une guideline hors-description ; juge défendable) | **85.2%** |
| erreur_juge (vraie erreur) | 11.4% |
| ambigu | 3.4% |

Par bench : convention 74-91% (cas2 90.6%, medline 89.4%, e3c le plus bas 74%). Asymétrie nette : **FN (juge rejette gold) = 87.6% convention** (le gold tague adjectifs « hépatique »/« urinaire », spans descriptifs « VS à 15mm », cibles « récepteurs D2 »=médicament) ; FP (juge accepte cross-type) = 53% convention / 44% erreur (le juge est plus faillible quand il ACCEPTE). **Lecture paper : le κ 0.53 n'est PAS un défaut de fiabilité — 85% de l'écart EST de la divergence de convention, le phénomène même qu'on étudie.** Report : `judge_gold/report_disagreements.md`. (Caveat honnêteté : méta-juge = Qwen sur désaccords impliquant des verdicts Qwen → cadrage définitionnel pour limiter la circularité ; résultat 85/11 très asymétrique + exemples clairement conventionnels = défendable.)

**⭐ Test self-preference (2026-06-11) — confond écarté.** Re-score COMPLET du pool communauté (127 874 items) par **MedGemma seul** (le juge qui n'a PAS généré nos données d'entraînement, vs Qwen qui les a générées). Gate honeypot MedGemma **0.995**. Verdict : **les rankings tiennent et sont même plus nets**. MAP nouveau Qwen→MedGemma : v3b 0.493→0.534, v3c-pristine 0.478→0.514, SE-v1 0.393→**0.367**, gliner2-large 0.287→0.352. Tous nos modèles battent SE-v1/gliner2-large sur le nouveau de +0.15 à +0.18 ; SE-v1 novel P@0.7=0.000 sous les deux juges ; Δoverfit SE-v1 +0.149 (MedGemma) vs v3b +0.007 (quasi-plat). La victoire backbone tient aussi (medembed-e1 0.437 > mcbio-e1 0.383). **→ Le finding convention-overfit est judge-independent : nos modèles entraînés sur data Qwen ne sont PAS juste flattés par un juge Qwen.** (NB : MAP absolus plus bas sous MedGemma car plus strict — 91k pas_une_entite vs 59k ; rankings + Δoverfit conservés.) Verdicts sauvegardés : `judge_eval/verdicts_{qwen,medgemma}.jsonl`. Désaccords vs gold = **artefacts de convention** (prouvé : CAS1 gold met "10 fois la dose"=sosy ; QUAERO tag "hépatique"(adj)=ANAT, "traités"=PROC) — les DEUX juges divergent pareil du gold = preuve de la thèse convention, pas erreur juge. NB : Nemotron-120B (nemotron_h Mamba) abandonné (OOM CPU répété vLLM 0.19) ; gemma-4 abandonné (archi non supportée vLLM 0.19). MedGemma médical = meilleur argument que générique.

### ⭐⭐⭐ Éval communauté LLM-judge — RUN FINAL 10 MODÈLES (2026-06-13, pool 146k, juge Qwen) — CANONIQUE PAPER

Pool re-poolé + re-adjugé avec **gliner-biomed** (vrai baseline lignée) + **v3d-2ep**. 146 059 items, gate honeypot **0.975 ✅**, PARSE_FAIL 0.3%. `report.md` + `verdicts_qwen_10m.jsonl`.

| Modèle | MAP commun | MAP nouveau | Δoverfit | novel P@0.7 | famille |
|---|---|---|---|---|---|
| **v3b-pristine** ⭐ | 0.583 | **0.476** | +0.107 | 0.250 | maison généraliste |
| v3c-pristine | 0.563 | 0.452 | +0.110 | 0.290 | maison |
| v3c-stage2-mix50 | 0.456 | 0.456 | **−0.000** | 0.317 | maison clinique |
| v3d-pristine (2ep) | 0.534 | 0.302 | +0.232 | 0.446 | maison multi-task |
| SE-v1 | 0.569 | 0.381 | +0.188 | 0.000 | baseline maison NER-only |
| gliner2-large (560M) | 0.496 | 0.285 | +0.211 | 0.068 | baseline générique |
| **gliner-biomed** | 0.390 | **0.121** | **+0.269** | 0.110 | **baseline lignée biomed** |

**Verdicts FINAUX (les 3 baselines externes/convention s'effondrent toutes sur le nouveau) :**
1. **gliner-biomed = LE PIRE généraliste de tous** (MAP novel **0.121**, Δoverfit **+0.269** le plus haut). Un GLiNER **biomédical dédié** (le concurrent direct de la lignée) généralise *moins* bien que nos petits modèles FR sur le biomed FR OOD → argument fort : la spécialisation biomed sans diversité = overfit-convention max.
2. **Les 3 baselines (SE-v1, gliner2-large, gliner-biomed) sont toutes overfit-convention** : Δoverfit +0.188 / +0.211 / +0.269, novel P@0.7 = 0.000 / 0.068 / 0.110. Tous nos modèles maison généralistes les battent sur le nouveau.
3. **v3b = meilleur généraliste** (novel 0.476). v3c-pristine ≈ v3b. v3b−SE-v1 novel ΔMAP +0.095 CI[+0.063,+0.131] ✅ signif.
4. **v3d-2ep = le plus overfit-NER des maison** (Δoverfit +0.232, novel 0.302, recall novel 0.326) — confirme le **trade-off classif↑/NER-généralisation↓** : v3d gagne la classif (voir ↓) mais sacrifie le novel-NER. **Modèle final = v3b (généraliste NER) ; v3d = vitrine multi-task.**

#### Tableau benchmarks standards 6-benchs (run `20260613_022436_CLEAN`, face au LLM-judge) — l'autre moitié de l'histoire
Macro strict : SE-v1 **0.389** > GLiNER2-large 0.346 > v3c-pristine 0.338 > v3c-stage2 0.335 > v3b 0.331 > **v3d 0.266 (dernier)**. **Le classement benchmark est l'INVERSE du classement communauté** (SE-v1/large gagnent les benchmarks convention, perdent la généralisation ; v3d pire benchmark mais meilleur classif). cas1 v3d=0.000 (collapse calibration). **= LE point central du paper.** (gliner-biomed PAS dans ce tableau : charge via package GLiNER v1, pas le fork eval_v3 — limitation à noter.)

---

### ⭐ Éval communauté LLM-judge (2026-06-08, run 5 modèles + gliner2-large) — RETOURNE LE VERDICT BENCHMARK [HISTORIQUE, voir run final ↑]

Éval hors-convention (`gen/judge_eval/`) : 400 docs PMC held-out OOD, 10 types communs + 10 nouveaux, pooling TREC reference-free (5 modèles + candidats juge), juge Qwen3-235B, MAP threshold-free. Gates : honeypot **0.975 ✅**, PARSE_FAIL 0.3%. (MAP absolus plus bas que le run 4-modèles car le pool 5-modèles = plus de gold ; rankings conservés.)

| Modèle | MAP commun | MAP nouveau | Δoverfit | novel P@0.7 |
|---|---|---|---|---|
| **v3b-pristine** | **0.604** | **0.493** | +0.111 | 0.242 |
| v3c-pristine | 0.585 | 0.478 | +0.107 | 0.312 |
| v3c-stage2-mix50 | 0.474 | 0.476 | −0.002 | 0.346 |
| SE-v1 | 0.589 | 0.393 | +0.196 | 0.000 |
| **gliner2-large** (560M) | 0.512 | **0.287** | **+0.225** | 0.068 |

**Verdicts :**
1. **gliner2-large (le vrai baseline 560M) est le PIRE généraliste** malgré 3.7× la taille de nos modèles (149M) : pire MAP nouveau (0.287, sous SE-v1), Δoverfit le plus élevé (+0.225 = le plus overfit-convention), novel P@0.7=0.068. **Nos petits modèles FR battent le gros baseline générique sur le biomed FR OOD.**
2. **SE-v1 overfit-convention** confirmé (Δoverfit +0.196, novel P@0.7=0.000). Tous nos modèles maison le battent sur le nouveau.
3. **v3b = meilleur généraliste** (commun 0.604, nouveau 0.493). v3c-pristine ≈ v3b (légèrement sous). Le fix densité v3c n'a PAS amélioré la généralisation réelle.
4. **Stage-2 : MAP commun le plus bas (0.474)** parmi les maison → sur-spécialisé. Non retenu (sauf robustesse/précision, voir ↓).

**→ Meilleur modèle communauté = v3b-pristine (≈ v3c-pristine). Les deux battent SE-v1 ET gliner2-large.**

### ⭐⭐ Éval robustesse clinique ACL-grade (2026-06-08, 5 modèles) — qu'apporte le stage-2 ?

Design causal : **mêmes 400 docs, CLEAN vs DÉGRADÉ** (registre hospitalier brouillon : abréviations ATCD/ttt/Pt, accents off, coquilles dictée — `degrade_corpus.py` déterministe). Gates : clean 0.975 / dégradé 0.977 ✅.

| Modèle | MAP common clean→dég | **drop** | novel clean→dég | drop |
|---|---|---|---|---|
| v3c-stage2-mix50 | 0.474→0.444 | **+0.030** (min) | 0.476→**0.495** | **−0.019** (gagne) |
| v3c-pristine | 0.585→0.548 | +0.037 | 0.478→0.451 | +0.027 |
| v3b-pristine | 0.604→0.559 | +0.046 | 0.493→0.484 | +0.009 |
| gliner2-large | 0.512→0.459 | +0.053 | 0.287→0.258 | +0.029 |
| SE-v1 | 0.589→0.529 | +0.061 (max) | 0.393→0.367 | +0.026 |

**Diff-in-diff (drop_ref − drop_stage2, common, bootstrap doc-level) :** vs SE-v1 +0.030 CI[+0.015,+0.045] ✅ ; vs v3b +0.015 CI[+0.002,+0.029] ✅ ; vs v3c-pristine +0.006 CI[−0.006,+0.019] ≈ non signif.

**Verdict : le stage-2 EST le plus robuste à la dégradation clinique** (drop commun min +0.030, seul à s'améliorer sur le nouveau sous dégradation ; significativement + robuste que v3b/SE-v1/gliner2-large). La spécialisation clinique a bien produit de la robustesse. **MAIS son MAP absolu reste le plus bas** (0.44 commun dégradé vs 0.55-0.56 pristine) → il dégrade moins mais de plus bas, **v3b/v3c-pristine restent meilleurs même sur clinique dégradé**. Trade-off robustesse/qualité défavorable. Niche : précision pure (P@0.5≈0.86).

### ⭐ Éval CLASSIFICATION multi-task (2026-06-08) — capacité ignorée par la suite NER

Gold réel (pas de juge) : **MORFITT** (spécialité, multi-label, 12cl, 500 docs) + **DiaMED** (chapitre CIM-10, mono-label, 22cl, 154 docs). `classify_text` zero-shot, labels FR. (`gen/judge_eval/classify_eval.py`)

| Modèle | MORFITT micro-F1 | MORFITT macro-F1 | DiaMED acc | DiaMED macro-F1 |
|---|---|---|---|---|
| **v3d-pristine (2ep)** ⭐ | **0.505** | 0.492 | **0.539** | **0.282** |
| v3d-e1 (1ep) | 0.448 | 0.418 | 0.474 | 0.231 |
| v3c-stage2-mix50 | 0.490 | **0.498** | 0.019 | 0.019 |
| gliner2-large | 0.436 | 0.431 | 0.377 | 0.140 |
| v3c-pristine | 0.433 | 0.453 | 0.013 | 0.015 |
| v3b-pristine | 0.401 | 0.424 | 0.078 | 0.076 |
| SE-v1 | 0.284 | 0.335 | 0.208 | 0.104 |

**Verdicts classif — ⭐ v3d RÈGLE le problème (run 2026-06-13, v3d 1ep+2ep) :**
- **v3d-pristine (2ep) gagne LES DEUX tâches** : MORFITT 0.505 (> stage-2 0.490 > gliner2-large 0.436) ET DiaMED **0.539 acc** (> gliner2-large 0.377 >> tous les v3b/v3c à 0.01-0.08). Le **fix CIM-10** (snap 22 chapitres dans le training v3d) marche et **se renforce au 2e epoch** (0.474→0.539). v3d = LE modèle multi-task vitrine.
- **DiaMED, l'ancien trou expliqué + réparé** : v3b/v3c s'effondraient (0.01-0.08, sous le hasard 1/22) car leur classif head n'avait jamais vu de gros label-set ; ajouter la tâche CIM-10 22-way au training v3d le répare directement. Hypothèse DESIGN.md confirmée.
- **MORFITT (spécialité)** : tous nos multi-task gagnent (v3d 0.505 ≥ stage-2 0.490 > gliner2-large 0.436 >> SE-v1 0.284).

### ⭐ Éval STRUCTURED EXTRACTION (3e tâche GLiNER2, 2026-06-13) — la dernière capacité non mesurée

LLM-judge **reference-free field-level** (`gen/judge_eval/eval_structured.py`, 3 phases extract→judge→score, miroir de l'éval NER). 200 docs PMC held-out, 3 schémas curés (Profil patient / Posologie / Résultat d'examen), `extract_json` t=0.3. Chaque champ NON VIDE rempli est jugé par Qwen : correct / mauvaise_valeur / mauvais_champ / champ_absent. Métrique = **précision field-level** (pas de recall sans gold, cohérent avec MAP-précision NER). SE-v1 exclu (NER-only, pas d'`extract_json`). Grounding littéral 99.9% (les valeurs sont des sous-chaînes). 2410 champs jugés, PARSE_FAIL 3%.

| Modèle | #champs remplis | **précision** | mauvais_champ | Profil patient | Posologie | Résultat d'examen |
|---|---|---|---|---|---|---|
| **v3d** ⭐ | 637 | **0.757** | 0.181 | 0.878 | 0.353 | 0.650 |
| v3c-pristine | 711 | 0.741 | 0.195 | 0.856 | 0.500 | 0.543 |
| gliner2-large | 488 | 0.701 | 0.186 | 0.847 | 0.280 | 0.760 |
| v3b-pristine | 574 | 0.695 | 0.206 | 0.813 | 0.318 | 0.618 |

**Verdicts :** **v3d gagne la 3e tâche** (0.757, + remplit plus correctement que le baseline 560M) → confirme v3d = **modèle multi-task vitrine** (gagne classif ET structures). Posologie = le schéma dur pour tous (0.28-0.50, champs dose/fréquence/voie souvent confondus = `mauvais_champ`). Profil patient = facile (~0.85). Le mode d'erreur dominant n'est PAS l'hallucination (mauvaise_valeur 6-10%) mais l'**attribution de champ** (mauvais_champ ~18-20%). Report : `judge_eval/report_structured.md`.

### ⭐ A/B BACKBONE tranché (2026-06-08) — MedEmbed-v9 > ModernCamemBERT-bio

Expérience causale propre : **data v3c identique + budget 1 epoch identique**, seule variable = le backbone (éval communauté, juge 0.980). Voir `gen/v3d/DESIGN.md` §2.

| Backbone (1ep, data v3c) | MAP commun | MAP nouveau | novel P@0.7 |
|---|---|---|---|
| **MedEmbed-v9** (contrastif biomed) | **0.522** | **0.396** | **0.419** |
| ModernCamemBERT-bio (MLM biomed) | 0.484 | 0.348 | 0.333 |

**MedEmbed-v9 gagne sur les deux régimes, surtout l'open-vocab (+0.048).** Le contrastif aligne `emb(description)↔emb(span)` = exactement le mécanisme GLiNER. **Question backbone tranchée : MedEmbed-v9 pour v3d.** (Les 2 sont ModernBERT-base 22L/768, entraînés sur le même mc-bio-corpus → seule l'objective contrastif vs MLM diffère.)

---

## Le gap vs SE-v1, décomposé par bench (run 194842, F1 best_t)

| bench | v3c-stage2 | v3c-pristine | SE-v1 | qui gagne |
|---|---|---|---|---|
| emea | 0.434 | 0.420 | 0.379 | **nous** (stage2) |
| medline | 0.430 | 0.425 | 0.377 | **nous** (stage2) |
| cas2 | 0.433 | 0.431 | 0.435 | parité |
| frasimed_distemist | 0.372 | 0.363 | 0.409 | SE-v1 (mais calibration, voir ↓) |
| cas1 | 0.070 | 0.204 | 0.343 | **SE-v1 largement** (vrai gap) |

**Anomalie de calibration (le signal central)** : sur cas1/frasimed, nos modèles fire quasi-rien au seuil par défaut.
- frasimed v3c-stage2 : **R@0.5 = 0.020** → F1 0.038 ; à best_t=0.1 → **0.372**. Le recall EST là, verrouillé derrière un seuil que le modèle ne sait pas auto-sélectionner.
- cas1 v3c-stage2 : R@0.5 = 0.008. SE-v1 a best_t=0.4 (bien calibré, fire à seuil normal).
- **cas1 reste un vrai trou** même à best_t (0.07–0.20 vs SE-v1 0.34) : convention de spans descriptifs maximaux que notre annotateur ne produit pas.

---

## Historique des lignées (post-v2)

### v3b (stage-1) — macro strict 0.350 / type-agn 0.433
- Data : single-call 2-section schema (candidate_spans → entities subset), open-vocab UMLS-steered, multi-task (NER + classif + structures), sources patient-rich (HAL/istex/pmc-patients-fr/wiki/textbooks/contains-patients).
- Modèle : `gliner2-v3b-pristine/best`.
- Stage-2 clinique v1 (mix50 clinique+replay) : macro 0.353 — à plat vs stage-1.

### Investigation densité/recall (le vrai diagnostic) — 2026-06
Décomposition fine du gap v3b/v3c vs SE-v1 :
1. **PAS un problème de spans longs** : les deux modèles ratent les spans 10+ tokens à **0.00**. SE-v1 ne les capte pas non plus. (Hypothèse span-long réfutée.)
2. **C'est un problème de RECALL de détection global** : SE-v1 détecte plus partout, à toutes les longueurs, tous les benchs (y compris EMEA spans courts).
3. **Cause = densité d'annotation du training** :
   - SE-v1 : distribution **bimodale extrême** — ~72 % docs entièrement vides (négatifs) + ~28 % hyper-denses (~159 mentions/doc, p90=173).
   - v3b : uniforme ~13 mentions/doc (cap "goldilocks 8-12" qu'on s'était infligé → plafond de détection auto-imposé).
4. **SE-v1 n'est pas contaminé** (agent provenance) : entraîné sur istex/hal annotés LLM librement, pas de fuite de gold. Son avantage = distribution alignée (types abstraits + densité exhaustive).
5. **Multi-task confirmé fonctionnel** sur nos modèles (classif testée : spécialité=cardiologie, urgence=oui) — mais **jamais évalué** (suite v3 = NER-only). Capacité réelle non mesurée.

### v3c (stage-1) — le fix densité — macro strict 0.368 / type-agn 0.431
Conçu pour reproduire le régime bimodal SE-v1 tout en gardant diversité L1-L4 + multi-task + parité 4-tâches GLiNER2 (ajout des **relations**).
- **Suppression du cap goldilocks** → annotation exhaustive (dense median ~40 mentions/doc, ~3× v3b).
- **~30 % négatifs** (chunks finewiki non-cliniques + **domain-gate** : ne tagger QUE le biomédical, sinon entities vides).
- **Candidate_spans → entities subset** conservé (grounding, ~94 % mention hit), ≤12 tokens.
- Corpus final : **98 238 docs** annotés, distribution réelle **40 % négatifs (0 entité) / 57 % denses (≥20 mentions)** = bimodal visé ✅.
- Canonicalisation L1 : HDBSCAN sur embeddings MedEmbed-v9 + critic (`canonical_map_v3c.json`), mix brut/canon dans l'assemble.
- Modèle : `gliner2-v3c-pristine/best`. Train 2 epochs, ~4h H100.
- **Résultat** : det-recall remonté au niveau v3b (0.431) mais pas SE-v1 (0.481). Forte **gap-calib 0.128** (sous-tire à t=0.5).

### Clinique v2 (pour stage-2) — 51 835 docs, 84 mentions/doc
- Ré-annotation des générations cliniques synthétiques (PMC-Patients FR longitudinaux) avec `prompt_clinical_v2` (cœur v3c exhaustif + few-shot **télégraphique** + dose **brouillon** réaliste : coquilles de dictée, abréviations collées, accents manquants — validé : lisible, entités repérables).
- Densité médiane **84 mentions/doc** (exhaustif), 830k relations groundées.

### Stage-2 v3c — mix50 → RÉGRESSION
- Mix : **99 524 docs** = 51 835 clinique-v2 dense (50 %) + 51 835 replay v3c (50 %, anti-oubli du stage-1 v3c).
- Init depuis `v3c-pristine/best`, LR bas (enc 5e-6 / task 2e-4), 1 epoch.
- Modèle : `gliner2-v3c-stage2-mix50/best`.
- **Résultat** : macro 0.348/0.395 — **det-recall régressé** (0.431→0.395). Gagne EMEA/MEDLINE, perd cas1. Mieux calibré (gap-calib 0.128→0.097) mais moins généraliste. **Non retenu.**

---

## Chemins importants

### Modèles (sous `/lustre/fsn1/projects/rech/rua/uvb79kr/onto/medembed-outputs/`)
> ⚠️ Les colonnes strict/type-agn sont les **benchmarks standards = convention-biaisés** (SE-v1 gagne). Le VRAI ranking pour le paper = l'**éval communauté MAP commun/nouveau** (section ⭐ ci-dessus) où **v3b gagne**. Garder les deux.

| Modèle | Path | bench strict/type-agn | MAP commun/nouveau (Qwen) | Note |
|---|---|---|---|---|
| **MedEmbed-v9** (backbone) | `medembed-v9/stage1/final` | — | — | 149M ModernBERT contrastif, SOTA FR biomed, **backbone gagnant** |
| **v3b-pristine** ⭐ meilleur généraliste | `gliner2-v3b-pristine/best` | 0.350/0.433 | **0.604/0.493** | stage-1 v3b, bat SE-v1+large sur le nouveau |
| v3c-pristine | `gliner2-v3c-pristine/best` | 0.368/0.431 | 0.585/0.478 | ≈ v3b, multi-task+relations |
| v3c-stage2-mix50 | `gliner2-v3c-stage2-mix50/best` | 0.348/0.395 | 0.474/0.476 | spécialisé clinique (robuste mais MAP bas), non retenu |
| **SE-v1** (baseline maison) | `gliner2-single-medembed-stage2/checkpoint-4500` | **0.389/0.481** | 0.589/**0.393** | gagne benchmarks, **overfit-convention** (novel P@0.7=0) |
| GLiNER2-large (baseline 560M) | `/lustre/fsn1/.../gliner-baselines/fastino--gliner2-large-v1` | 0.345/0.456 | 0.512/**0.287** | pire généraliste malgré 3.7× la taille |
| v3c-medembed-e1 / v3c-mcbio-e1 | `gliner2-v3c-medembed-e1/best` / `gliner2-v3c-mcbio-e1/best` | — | 0.522/0.396 vs 0.484/0.348 | A/B backbone (1 epoch, data v3c) |
| **v3d-pristine** (à venir) | `gliner2-v3d-pristine/best` | — | — | PAS encore entraîné (annotation ~92%) |
| ModernCamemBERT-bio (backbone alt) | `/lustre/fsn1/.../almanach--ModernCamemBERT-bio-base` | — | — | perdant A/B vs MedEmbed-v9 |
| Juges | `Qwen--Qwen3-235B-A22B-Instruct-2507-FP8` (canon) · `google--medgemma-27b-text-it` (2e juge) | — | — | annotation = aussi Qwen3-235B |

### Données (sous `medembed-outputs/`)
- **v3c base** : `gliner2-v3c/annotations_v3c.jsonl` (98 238) → `_grounded` → `training_data_v3c_train.jsonl` (94 309) + val (3 929). Canon : `gliner2-v3c/canonical_map_v3c.json`.
- **Clinique v2** : `clinical_stage2/annotations_clinical_v2.jsonl` (51 835) → `training_data_clinical_v2.jsonl` (51 835).
- **Mix stage-2 v3c** : `clinical_stage2/v3c_stage2/stage2_mix50_{train,val}.jsonl` (99 524 / 4 146).
- Corpus source : `/lustre/fsn1/.../rntc--mc-bio-corpus/` (+ `-contains-patients`, `rntc--pmc-patients-fr`).

### Évaluation
- **Suite v3 (prod)** : `GLiNER2/v3/eval_v3.py` + `eval_v3_clean.sbatch` + `configs_clean/{models,benchmarks,descriptors_locked}.yaml`.
  - 6 benchs NER : emea, medline, e3c, cas1, cas2, frasimed_distemist
  - 3 axes : strict / type-agnostic (det-recall) / overlap-IoU ; threshold sweep 0.1–0.8
  - descriptors hashés SHA256, macro F1 cross-bench, gap-typing / gap-calib / rank-stability
  - Runs immuables : `GLiNER2/v3/runs/<timestamp>_CLEAN/results.{md,json}` + `predictions.parquet`
  - ~30-40 min sur 1 H100 dev qos

### Environnements Python
- `/lustre/fsn1/.../envs/bge/bin/python3` — training GLiNER2, embeddings
- `/lustre/fsn1/.../envs/reformulation/bin/python` — annotation vLLM 0.19 (`StructuredOutputsParams(json=schema)` + `enable_thinking:False` + `LD_LIBRARY_PATH=envs/reformulation/lib`)
- `/lustre/fsn1/.../envs/tabib-C39hfyYp-py3.12/bin/python` — eval (tabib + gliner2 + evaluate + seqeval). **Pas** de `PYTHONNOUSERSITE=1`.

---

## Architecture code (état 2026-06-04)

```
medembed/                          # Embeddings MedEmbed-v9 (stable)

GLiNER2/                           # Fork fastino/GLiNER2 PRISTINE (NE PAS modifier gliner2/*)
├── gliner2/                       # ⚠️ code natif fastino
└── v3/
    ├── eval_v3.py + eval_v3_clean.sbatch     # Eval suite (configs_clean)
    ├── train_v3c.py + .sbatch                # Stage-1 v3c pristine
    ├── train_stage2.py + .sbatch             # Stage-2 (--init v3b|v3c|scratch)  ← v3c ajouté 2026-06-04
    ├── configs_clean/{models,benchmarks,descriptors_locked}.yaml
    ├── core/{loader,descriptors,scoring,stratify,aggregate,report}.py
    └── runs/<ts>_CLEAN/

gen/
├── v3c/                           # ⭐ Pipeline base v3c (fix densité)
│   ├── prompt_v3c.py              # 4-tâches, exhaustif, candidate-spans, domain-gate
│   ├── load_corpus_v3c.py + .sbatch          # 98k chunks, ~30% négatifs finewiki
│   ├── annotate_v3c.py + .sbatch             # chain resume scan_done_ids
│   ├── filter_offline_v3c.py     # grounding entities + relations, GARDE négatifs (min_entities=0)
│   ├── canonicalize_v3c.py + .sbatch         # HDBSCAN L1 + critic
│   └── assemble_training_v3c.py  # 4-tâches (entities/classif/structures/relations) + canon mix
├── clinical_stage2/              # Pipeline clinique synthétique
│   ├── prompt_clinical_v2.py     # cœur v3c + télégraphique + brouillon
│   ├── annotate_clinical_v2.py + .sbatch
│   ├── build_stage2_mix.py       # clinique + replay (--ratio, --replay)
│   └── prep_stage2_v3c.sbatch    # filter→assemble→mix en un job CPU
├── v3d/                          # ⭐⭐ Pipeline v3d "definitive" (voir DESIGN.md)
│   ├── DESIGN.md                 # tous les choix data-driven tracés + verdict backbone
│   ├── prompt_v3d.py             # densité MODÉRÉE (pas exhaustif) + classif CIM-10 22-way + BROUILLON_NOTE
│   ├── load_corpus_v3d.py + .sbatch   # 102 864 chunks, 22% nég, registres élargis (finewiki-medical), 18% clinique→brouillon
│   └── annotate_v3d.py + .sbatch      # = annotate_v3c + register brouillon par source + prompt_v3d
└── judge_eval/                   # ⭐⭐⭐ ÉVAL LLM-JUDGE = LE contribution paper
    ├── build_holdout_corpus.py   # 400 docs PMC held-out OOD (uids training exclus)
    ├── type_bank.yaml            # 10 types communs + 10 nouveaux (open-vocab), descriptions FR neutres
    ├── run_inference.py + .sbatch # GLiNER2 t=0.001, 2 passes common/novel ; MODELS dict (ajouter modèles ici)
    ├── run_judge.py + .sbatch     # propose+pool+adjudicate vLLM ; --judge_model {qwen,medgemma,nemotron,gemma4}
    ├── build_pool.py             # pooling TREC top-8/système + candidats juge + honeypots (POS spécifiques)
    ├── score.py                  # MAP threshold-free, Δoverfit, pooled recall, gate honeypot ; --dir
    ├── score_conditions.py       # robustesse clean vs dégradé, diff-in-diff bootstrap doc-level
    ├── degrade_corpus.py         # dégradation déterministe brouillon (abréviations/accents/coquilles)
    ├── classify_eval.py + .sbatch # MORFITT + DiaMED gold réel (F1, pas de juge)
    ├── judge_gold_validation.py  # ⭐ valide le juge vs gold humain QUAERO/CAS/E3C-layer1 (κ Cohen)
    ├── inter_judge.py            # accord inter-juges Qwen↔MedGemma
    ├── infer_gliner_biomed.py    # baseline GLiNER-biomed (✅ inféré, plié dans pool 10-modèles)
    ├── eval_structured.py + struct_{extract,judge}.sbatch  # ✅ 3e tâche extract_json, LLM-judge field-level
    └── multitask_showcase.py     # classif + relations (démonstration qualitative)
```
**Artefacts judge_eval** (sous `medembed-outputs/judge_eval/` et `judge_eval_deg/`) :
- `holdout_pmc.jsonl` (400 docs clean) ; `holdout_pmc_degraded.jsonl` (dégradé)
- `preds_<model>.parquet` (un par modèle) ; `pool.jsonl` (127 874 items, 7 modèles) ; `pool_provenance.jsonl`
- **`verdicts.jsonl` = CANONIQUE (Qwen)** ; `verdicts_qwen.jsonl` + `verdicts_medgemma.jsonl` (sauvegardes des 2 juges)
- `report*.md` (snapshots des runs successifs : `report_5m.md`, `report_conditions.md`, `report_classification.md`…)

---

## Bugs/écueils connus à éviter

1. **NE PAS modifier `GLiNER2/gliner2/*`** — code pristine fastino. Toute modif passée a régressé F1.
2. **`train_stage2.py --init` est un choix `{v3b,v3c,scratch}`** (pas un chemin) → résolu vers checkpoints hardcodés (V3B_BEST/V3C_BEST). Ajouter un `elif` pour une nouvelle lignée.
3. **Annotation → env `reformulation`** (vllm 0.19) ; **eval → env `tabib`** ; **training → env `bge`**.
4. **`sys.path.insert(0, str(_REPO_ROOT / "GLiNER2"))`** OBLIGATOIRE avant `import gliner2` (sinon résout vers le pip-installé sans `include_spans`).
5. **Loaders parquet stallent sur login node** → toujours soumettre en CPU sbatch (`partition=prepost`, `account=rua@cpu`).
6. **Annotation bimodale : les négatifs sont en fin de fichier** → prévoir assez de jobs dans la chaîne pour les atteindre (sinon training sans négatifs = perte de précision).
7. **MEDLINE `filter_nested=True` perd 26% du gold** ; **FRACCO `label=PROC` faux** (gold DISO) ; **MANTRAGSC table BIO permutée** — déjà gérés/exclus dans eval_v3.

### Écueils ajoutés (session paper/v3d, 2026-06)
8. **File 4×H100 normale = ~1-2 JOURS d'attente** (saturée en permanence). Pour tout job long (annotation 235B, train) : soit accepter l'attente, soit **dev qos** (`--qos=qos_gpu_h100-dev --time=02:00:00`, schedule en minutes mais 2h max). L'annotation/adjudication via `scan_done_ids`/resume tolère le découpage en jobs dev de 2h.
9. **`run_judge.py phase_adjudicate` écrit toujours `<outdir>/verdicts.jsonl`** → avant de re-juger avec un autre juge, **sauvegarder l'existant** (`cp verdicts.jsonl verdicts_<juge>.jsonl`) sinon écrasement. Canonique = Qwen ; toujours restaurer `verdicts_qwen.jsonl` → `verdicts.jsonl` après un run d'un autre juge.
10. **Re-pooling = re-adjudication obligatoire** : ajouter un modèle au pool (TREC) change le pool → il FAUT re-adjuger tout le pool pour que le nouveau modèle soit jugé équitablement (ses spans hors-pool comptent faux sinon). Workflow : run_inference(nouveau modèle) → build_pool → run_judge adjudicate → score.
11. **Juges vLLM 0.19** : Qwen3-235B (4 GPU) et MedGemma-27B (medgemma-27b-text-it) marchent. **Nemotron-3-Super-120B** = OOM CPU répété (abandonné). **gemma-4-31B** = archi non supportée par vLLM 0.19 (abandonné). `enable_thinking` seulement pour `THINKING_JUDGES={qwen,nemotron}` (les autres erreur).
12. **Honeypots POS** : utiliser des entités cliniques SPÉCIFIQUES (« infarctus du myocarde »), PAS génériques (« cancer », « infection ») que le juge classe légitimement `mauvais_type` → faux échec de gate. Gate recadré = NEG(rejet-bruit) + POS(reconnaissance-type, hors PARSE_FAIL).
13. **Gold gold-vs-silver** (pour valider le juge) : GOLD humain = **QUAERO (EMEA/MEDLINE), CAS, MANTRA, E3C-layer1**. SILVER (à NE PAS utiliser comme vérité humaine) = **E3C-layer2** (dictionnaire+10% validé), **FRASIMED** (projection crosslingue depuis l'espagnol). ⚠️ Conflit : `tabib/data/e3c.py` commente "layer2=well-annotated / layer1=silver(test)" mais le paper E3C dit l'INVERSE (layer1=gold manuel). Notre `eval_v3` charge `e3c split=test = fr.layer1` → à clarifier avant de publier les chiffres E3C de la suite benchmark.
14. **`/tmp/inspect.py` parasite d'un autre user** shadow la stdlib quand on lance python avec cwd=/tmp → toujours lancer les scripts python depuis le repo, pas /tmp.

---

## Next Steps (priorisé — workstream PAPER EACL)

> **2026-06-13 : toutes les évals quantitatives du paper sont FAITES.** v3d entraîné (1ep+2ep), éval communauté finale 10 modèles (gliner-biomed inclus), benchmarks 6-benchs, classif, et **3e tâche structured extraction**. Reste : 2 trous méthodo (1 optionnel humain) + écriture/release.

### 1. ✅ FAIT — tableaux du paper complets
- ✅ v3d 1ep+2ep entraîné, évalué partout. **Modèle final tranché : v3b = généraliste NER vitrine ; v3d = vitrine multi-task (gagne classif + structures).**
- ✅ GLiNER-biomed baseline plié dans l'éval communauté 10-modèles (= pire généraliste, novel 0.121).
- ✅ Benchmarks standards 6-benchs (`20260613_022436_CLEAN`) face au LLM-judge — classement inverse.
- ✅ 3e tâche structured extraction (`eval_structured.py`, v3d gagne 0.757).

### 2. Blinder l'éval (les 2 trous méthodo restants — voir HANDOFF)
- **Analyse convention-vs-erreur** sur désaccords juge-gold (sans humain, à partir de `judge_gold_validation.py`) — classer chaque désaccord juge↔gold en divergence-de-convention vs vraie-erreur-juge. **C'est le prochain item le plus rentable.**
- (Quand l'utilisateur peut) mini-pass humain n≈120 sur verdicts de types nouveaux (ancrage humain de la claim phare). L'utilisateur a dit "pas d'humain pour le moment".

### 3. Écriture + release
- Modèle final (v3b + v3d) + dataset synthétique v3d + harness `gen/judge_eval/` → release MIT. Offrir une variante **petit-juge** (le 235B = 4 GPU est une barrière de repro ; MedGemma-27B = 1-2 GPU, déjà validé κ0.61 + self-preference).
- (optionnel) gliner-biomed sur les benchmarks standards (nécessite un wrapper GLiNER v1 → eval_v3, il n'est aujourd'hui que dans l'éval communauté).

---

## Commandes utiles

```bash
# Monitor
squeue -u $USER -o "%.10i %.18j %.8T %.10M %.10L %.20S"

# Éval communauté LLM-judge (le contribution paper) — pipeline complet :
PY=/lustre/fsn1/projects/rech/rua/uvb79kr/envs/bge/bin/python3
B=/lustre/fsn1/projects/rech/rua/uvb79kr/onto/medembed-outputs
# 1. inférence d'un modèle (1 GPU dev) :
sbatch --qos=qos_gpu_h100-dev --time=01:00:00 --export=ALL,CORPUS=$B/judge_eval/holdout_pmc.jsonl,OUTDIR=$B/judge_eval gen/judge_eval/run_inference.sbatch
# 2. re-pool (CPU/login, rapide) :
$PY gen/judge_eval/build_pool.py --outdir $B/judge_eval
# 3. adjudication (4 GPU dev ; JUDGE=qwen|medgemma) :
sbatch --qos=qos_gpu_h100-dev --time=02:00:00 --export=ALL,PHASE=adjudicate,JUDGE=qwen,OUTDIR=$B/judge_eval gen/judge_eval/run_judge.sbatch
# 4. score :
$PY gen/judge_eval/score.py --dir $B/judge_eval          # MAP commun/nouveau, Δoverfit, gate
$PY gen/judge_eval/score_conditions.py                   # robustesse clean vs dégradé

# Validation juge vs gold humain (κ) + inter-juges :
$PY gen/judge_eval/judge_gold_validation.py
$PY gen/judge_eval/inter_judge.py

# Classif (gold réel, pas de juge) :
sbatch gen/judge_eval/classify_eval.sbatch

# Train stage-1 (backbone medembed-v9 ou moderncamembert-bio) :
$PY GLiNER2/v3/train_v3c.py --backbone medembed-v9 --train <train.jsonl> --val <val.jsonl> --output <outdir> --num_epochs 2

# Benchmarks standards (suite v3) :
sbatch GLiNER2/v3/eval_v3_clean.sbatch    # → GLiNER2/v3/runs/<ts>_CLEAN/results.md
```
