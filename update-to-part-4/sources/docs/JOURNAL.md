# Têtes de normalisation eCRF — journal complet (idée, succès, échecs, bugs, résultats)

> Projet : étendre GLiNER (extracteur de spans) pour qu'il sorte directement les **valeurs
> normalisées** des 89 champs eCRF lymphome (chiffres, enums, dates), pas juste des spans.
> Dataset : `rntc/lymphome-synth-v5` (gold TAPDL span-localisé, 1640 train / 410 test).
> Code : `gen/lymphome/norm/`. Figure archi : `figures/arch_norm.{tex,pdf,png}`.
> Verdict court : **la tête catégorielle marche (+0.15 F1) ; la tête de sélection num/date/ordinal
> ne marche pas (elle copie la détection à 96%) ; on ne bat pas Qwen-9B sur le F1 89-champs.**

---

## 1. L'idée

GLiNER v5 (`V5FROMV3B`, 150M) détecte bien les spans eCRF, mais sa « valeur » = le **texte brut
du span** (« 1,75 m », « réarrangement mis en évidence »). Pour la recherche clinique (cohortes,
survie, stats) il faut la **valeur canonique** : `175` (cm), `POSITIF`, `IV`, `2018-06-15`.

**Hypothèse** : greffer des **têtes de normalisation légères** sur les spans détectés →
un seul modèle qui détecte ET normalise en un forward, sans décodage autorégressif (vs un LLM).

**Taxonomie des 89 champs** (dérivée du pydantic `LymphomeAnnotation`) → 5 familles :
- **CAT** (~38) catégoriel nominal (sexe, FISH, COO, traitement, réponse…) → classification.
- **ORD** (~10) ordinal borné (OMS 0-5, IPI, Ann Arbor, Deauville…) → sélection/parse.
- **NUM** (~18) numérique (poids, taille, LDH, SUVmax, %IHC…) → sélection/parse.
- **DATE** (~16) → sélection/parse + normalisation ISO.
- **TXT** (~8) texte libre (sous-type, antécédents…) → pas de tête.

---

## 2. Deux architectures essayées

### 2.1 Découplée (baseline, `norm_common.py` + `train_norm.py`)
Spans prédits par GLiNER → **ré-encodés par MedEmbed-v9 GELÉ** (fenêtre de contexte) → têtes.
- ✅ A servi à valider la taxonomie, les cibles, le design des têtes.
- ❌ **Pas un vrai « GLiNER + têtes »** (bi-encodeur séparé, pas les reps natives de GLiNER).
  L'utilisateur l'a justement pointé → pivot vers l'intégré.

### 2.2 Intégrée (retenue, `gliner_integrated.py`)
Sous-classe/attache des têtes trainables à l'`Extractor` GLiNER (`gliner2/*` intact).
**Un forward** : `_encode_batch` → `compute_span_rep` (h_i natif) + `schema_emb` (e_f natif) →
loss détection native **+** loss normalisation. **Finetune end-to-end, SANS freeze.**
À l'inférence : détecte SES spans (score de détection natif) → têtes normalisent.

---

## 3. Ce qui a MARCHÉ ✅

1. **Tête CAT (classification) = LA contribution réelle.** Ablation têtes vs sans-têtes (même
   modèle, même métrique F1) : **CAT +0.117 à +0.164** de façon robuste sur toutes les variantes.
   Raison : la sortie (classe canonique) est *fondamentalement différente* du texte du span
   (« patiente »→femme, contexte→statut) → la tête fait un travail que la détection ne peut pas.
2. **Archi intégrée différentiable, un seul modèle, no-freeze** : techniquement propre et validée.
   Entraînement = softmax/marginal-likelihood (différentiable) ; seul argmax = au décodage des
   valeurs (pointer-network, standard). Détection et normalisation partagent le même score natif.
3. **Candidats via le VRAI score de détection natif** (`count_embed` + einsum) : candidat-recall
   **CAT .68 / ORD .96 / NUM .88 / DATE .76** (sur schéma restreint) — excellent.
4. **v3b (généraliste) rattrape v5 (déjà finetuné lymphome)** : l'archi marche même quand la
   détection lymphome est ré-apprise de zéro.
5. **Undertrain partiellement réel** : val 0.835→0.860 en passant 2→3 epochs.
6. **Détection = levier fort** : baisser le seuil (0.1→0.03) fait chuter la détection ratée
   **23% → 9%** (v5), **3%** (v3b).

## 4. Ce qui n'a PAS marché ❌

1. **Tête de RÉGRESSION pour NUM** (première idée) : **pire que parser le span** (NUM 0.29 vs
   span-brut 0.49). Cause : la valeur « 175 » est **symbolique** (dans le texte), pas une fonction
   lisse d'un embedding poolé. → pivot vers **sélection de span + parse**.
2. **Tête de SÉLECTION num/ordinal/date : ne bat PAS le top-détection.** Ablation : ORD +0.02,
   NUM −0.01, DATE +0.03. Enquête : **la tête agrée avec la détection 96-99%** — c'est un suiveur,
   pas un re-ranker. L'oracle (ORD 0.82, NUM 0.67) reste hors de portée.
3. **Fix re-ranker** (retirer le biais conf + l'injection gold à score fixe) : **échec, accord
   toujours 96%** à ep2. La tête ne ré-apprend pas à re-ranker.
   - Hypothèse : signal d'entraînement **dominé par les cas faciles** (top-détection souvent
     correct → la tête apprend « fais confiance à la détection », jamais la minorité re-rankable).
4. **On ne bat pas Qwen-9B sur le F1 89-champs** : macro-F1 **0.50 vs 0.62** (équitable 0.53 vs
   0.67). On gagne CAT/NUM (proches), on perd ORD/DATE (role-binding, où le génératif 9B gagne).

## 5. Erreurs & bugs (chronologique, honnête)

### Erreurs conceptuelles (les coûteuses)
- **Cosine `span_rep · e_f` comme scorer de candidats** : mauvais espace (`e_f` = texte du champ
  encodé séparément) → candidat-recall NUM **0.066**. Vraie erreur qui a fait perdre un cycle.
  Fix : utiliser le **vrai score de détection natif** (`count_embed`+einsum), recall 0.88.
- **Val fuitée** : schéma d'entraînement/val limité aux champs **présents** (~17) → fuite de
  présence + role-binding facilité → val gonflée à **0.84** alors que le test réaliste **89 champs**
  donnait **0.50**. Fix : `build_dataset` met TOUS les non-TXT (absents = [] négatifs).
- **Métrique trop clémente** : premières annonces « on bat Qwen (0.62 vs 0.58) » étaient sur du
  **recall-only + DATE-année**, sans précision. Le vrai **F1** (précision incluse) → Qwen repasse
  devant. Leçon : toujours F1 (precision+recall), pas recall seul.
- **Sélecteur enrichi (posfeat + gros MLP)** : **overfit** (train gold-span / test pred-span) →
  pire que la version simple. Rejeté.

### Bugs techniques (rapides)
- `compute_span_rep` attend `[L,d]`, pas `[1,L,d]`.
- `torch.load(weights_only=True)` refuse les scalaires numpy (`num_stats`) → `weights_only=False`.
- `v3b max_width=8` vs `v5=24` → clamp de largeur sur `span_rep.shape[1]` (IndexError).
- `model.processor` n'est pas callable → tokenisation mots via `model.processor.word_splitter`.
- Off-by-one mot↔token (bénin, en fin) — validé par un check d'alignement (0.909 des NUM mappent).
- Script dans `/tmp` = **local au nœud de calcul** → introuvable en sbatch. Mettre dans le repo.
- Seuil de remplissage `THRESH_FILL` **non calibré par modèle** (le score natif n'est pas centré
  sur 0.5) → comparaisons faussées entre finetunes ; à sweeper par modèle sur la val.

## 6. Résultats

### Ablation têtes vs sans-têtes (v4, test 410, F1 canonique, seuil 0.5)
| famille | sans têtes (GLiNER seul) | avec têtes | Δ | Qwen-9B |
|---|---|---|---|---|
| CAT  | 0.359 | **0.477** | **+0.117** | 0.509 |
| ORD  | 0.637 | 0.629 | −0.008 | 0.814 |
| NUM  | 0.601 | 0.580 | −0.021 | 0.619 |
| DATE | 0.313 | 0.320 | +0.008 | 0.530 |
| **macro-F1** | 0.477 | **0.501** | **+0.024** | 0.618 |
| macro-F1 équitable (DATE année) | — | 0.533 | — | 0.666 |

### Enquête re-ranker (test) — la tête suit la détection
| famille | accord tête/détection | oracle (cible∈candidats) | actuel (recall) |
|---|---|---|---|
| ORD | **96-97%** | 0.77–0.82 | 0.34–0.61 |
| NUM | **97-99%** | 0.67–0.69 | 0.32–0.51 |
| DATE | **95-96%** | 0.24–0.28 | 0.17–0.21 |

### Diagnostic DATE (test, champs date localisables)
| mesure | valeur | lecture |
|---|---|---|
| cible **exacte** ∈ candidats | 0.738 | métrique exacte dure |
| cible **année** ∈ candidats | **0.928** | plafond re-ranker au bon niveau |
| gold-span parse == cible (année) | 0.882 | localisable |
- ~**34%** des dates cibles (prod annotation) **n'ont aucun span gold** → perdues (données/gold).
- DATE se décompose : **1/3 métrique** (année vs exact), **1/3 gold manquant/faux**, **1/3
  re-ranker cassé**. Ce n'est PAS un mur de role-binding insoluble.

### Valeurs oracle gold-span (borne haute, à span donné)
Intégré val 0.86 (NUM 0.92, DATE 0.70) — les têtes normalisent très bien *quand le span est donné*.
Le gouffre val(gold-span 0.86) → test(pred-span 0.50) = **la détection est le goulot**, pas les têtes.

## 7. Leçons transférables
1. **Le goulot des champs-valeur = la DÉTECTION** (quel span mis en top pour le champ), pas la
   normalisation. GLiNER met déjà la bonne valeur en tête ~96% quand il détecte → rien à re-ranker.
2. **Une tête post-hoc n'aide que si sa sortie diffère structurellement du span** (cas CAT :
   classe canonique). Pour les valeurs *écrites* (num/date), `détection + parse` est déjà optimal.
3. **Métrique** : token-Jaccard (capstone) ≠ exact canonique ≠ année. Choisir selon l'usage
   clinique (année pour la survie) et **toujours reporter le F1**, pas le recall.
4. **Fully-differentiable ≠ tout continu** : pour une sortie symbolique tirée du texte, le bon
   design est un **pointer-network** (soft à l'entraînement, argmax au décodage), pas une régression.
5. **Le no-freeze + reps natives GLiNER** > bi-encodeur gelé, à span donné (val 0.86 vs 0.66).

## 8. État final & options
- **Meilleur modèle** : `gliner2-norm-v5-v4` (89-champs), macro-F1 0.50 / équitable 0.53.
- **Archi honnête recommandée** : **GLiNER + tête CAT uniquement** ; parsing direct pour
  num/date/ordinal (= aussi bon, plus simple).
- **Dernier levier non testé** (pour NUM/ORD, headroom oracle réel) : **loss à marge sur cas durs**
  — n'entraîner la sélection que sur les cas où le top-détection est FAUX mais un candidat correct
  existe (upweight la minorité), hinge `score(wrong_top) < score(correct)`. Si l'accord reste 96%
  après ça → conclure définitivement que la sélection n'est pas apprenable ainsi.
- **DATE** : passer la métrique au niveau année (usage clinique) + améliorer le gold TAPDL sur les
  ~34% de dates non-localisées.

## 9. Fichiers
`taxonomy.py` (89 champs), `gliner_integrated.py` (archi+loss+predict), `finetune_integrated.py`,
`eval_integrated.py` (F1 + ablation + enquête + oracle + DATE-année), `RESULTS_INTEGRATED.md`,
`INTEGRATED_PLAN.md`, `figures/arch_norm.*`. Modèles : `gliner2-norm-{v5,v3b}-v4` (89-champs),
`gliner2-norm-v5-rr` (re-ranker, négatif).

---

# Session 2026-07-28 — audit, contexte, et décomposition de l'erreur

> Point de départ : macro-F1 0.50 (métrique d'alors), « la tête de sélection ne marche pas,
> elle suit la détection à 96 % ». Point d'arrivée : **la sélection n'était pas en cause — on
> évaluait sur 40 % du dossier**. Et la vraie limite est ailleurs : on ne se trompe pas, on
> s'abstient.

## 1. La trouvaille : la troncature

`gliner_integrated.MAX_CHARS = 9000`, appliqué à l'entraînement ET à l'éval. Or les dossiers
font **22 288 caractères en médiane** (p90 29 335). Conséquences mesurées sur le test 410 :
- **100 %** des documents tronqués, **60,5 %** des spans gold jetés ;
- **41,3 %** des champs non-TXT ont *tous* leurs spans au-delà du cap ;
- plafond de rappel gold-localisable : **0.310** à 9k contre **0.523** à texte complet.

Le baseline Qwen, lui, lisait `--max_chars 30000` **et** par section. Le « 0.50 vs 0.62 »
comparait donc un modèle lisant 40 % du dossier à un modèle lisant tout.

**Effet du seul cap, à modèle et code identiques : macro-F1 0.429 → 0.529 (+0.100).**

Et l'enquête re-ranker s'inverse : accord tête/détection ORD 96,2 % → 91,1 %, DATE 95,3 % →
87,9 %, sauvetages/casses ORD 113/17, oracle ORD 0.82 → **0.955**. **Le « suiveur à 96 % » du
journal précédent était un artefact : à 9 000 caractères il n'y avait rien à re-classer.**

Budget de contexte : le schéma (81 champs + descriptions) occupe **1 870 tokens** de la fenêtre
de 8 192 de ModernBERT — c'est le mécanisme GLiNER (schéma et texte dans la même séquence), pas
un défaut. Budget texte utilisable ≈ **24 000 caractères**.

## 2. Hypothèses réfutées (toutes à coût faible — c'est le point)

| hypothèse | verdict |
|---|---|
| aiguiller tête/parsing par taux de copie | **inutile à 9k** (τ*=1.0) ; **+0.012 au contexte plein** |
| le biais `sel_c` expliquait l'écart au journal | réfuté (0.436 vs 0.438) |
| `CAND_COUNT=3` vs entraînement à 1 | décalage réel, **effet +0.001** |
| calibrer le seuil de remplissage | **contre-productif** : val 0.488→0.530, test 0.532→0.497 |
| reranker par attention entre candidats | **égalité stricte** 0.532 vs 0.532 |

Le reranker fait pourtant ce qu'on lui demande — ratio sauvetage/casse DATE 1,75 → **2,85**, et
DATE F1 0.399 → 0.408 — mais ça ne remonte pas dans le macro. **L'architecture n'est plus le
facteur limitant ; la loss l'est** (vraisemblance marginale ≈ 0 quand la détection a déjà
raison, soit ~92 % des cas → gradient nul là où il faudrait apprendre). Loss à marge sur cas
durs implémentée (`--hard_w=3.0`, ~1,8 cas durs/document, ~2 300 par epoch) : **elle dégrade**.

| macro-F1 (métrique corrigée, test 410, cap 24k, 1 epoch) | loss d'origine | + marge |
|---|---|---|
| NormHeads | **0.532** | 0.515 |
| RerankHeads | **0.532** | 0.525 |

Sous la marge, l'attention reprend l'avantage (0.525 > 0.515) — quand l'entraînement demande
enfin de re-classer, la tête qui *peut* comparer les candidats fait mieux — mais le net reste
sous la référence. Mécanisme plausible non vérifié : la hinge porte sur les scores de la tête,
qui passent par `span_rep` **partagé avec la détection**, et l'entraînement est sans freeze —
pousser vers le bas le candidat top-détection peut abîmer la détection elle-même. Le poids
`hard_w=3.0` a été choisi arbitrairement et n'a pas été balayé.

**Verdict sur la tête de sélection : close.** Trois angles, trois réfutations — plus
d'information (attention + contexte : égalité), plus de pression d'entraînement (marge :
−0.017), plus de contexte à lire (+0.100, mais qui profite autant au parsing). La marge de
re-classement existe pourtant (oracle ORD 0.955 contre 0.644 réel) : **aucun des trois leviers
ne la convertit**. Ce qui survit intact : la tête **CAT** (+0.095 à +0.121 selon les runs),
la seule dont la sortie n'est pas un morceau du texte.

## 3. La vraie limite : on s'abstient

Décomposition sur `ctx-norm` (test 410, métrique corrigée) :

| classe d'erreur | part |
|---|---|
| **sous-remplissage** (cible existe, on ne remplit pas) | **62 %** |
| sur-remplissage (pas de cible, on remplit) | 23 % |
| fausse valeur | 15 % |

Contrefactuels : supprimer le sous-remplissage → **0.837**. Supprimer les erreurs de sélection
→ 0.746. **L'objectif 0.80 est exactement le budget du sous-remplissage.**

**14 champs ne sont jamais remplis** (`news_vital_status` 392/392, `imaging_suvmax` 186/186
alors que son taux de copie est 0.97 et que 142 cas sont bloqués par le seuil…). Deux
mécanismes distincts : (a) calibration — le score de détection n'a pas la même échelle selon
le champ ; (b) absence de candidat — la valeur n'est écrite nulle part (copie ~0).

AUC du score de détection pour « ce champ est-il documenté ? » : **0.739** (NUM 0.632). C'est le
plafond dur de toute approche par seuil.

**Prochain levier, le seul encore debout :** la tâche eCRF pose trois questions — *le champ
est-il documenté ? où est sa valeur ? comment la normaliser ?* On n'a jamais modélisé que les
deux dernières. Et la tête existe déjà : `count_pred` (20 classes) est dans GLiNER2 mais
**jamais entraînée pour les tâches `entities`** (`if task_type != "entities"`). L'entraîner sur
les 81 champs = **124 578 exemples étiquetés par epoch**, et `count > 0` donne la présence.

## 4. Défauts de méthode trouvés (à corriger avant publication)

1. **Bug de métrique** : chaîne `elif` — une valeur remplie mais fausse n'était comptée que
   comme faux positif, jamais comme faux négatif. Rappel surestimé, absolus gonflés de ~0.03.
   **Corrigé** dans `eval_integrated.py` et `route_analysis.py`.
2. **La validation n'est pas échangeable avec le test** : 42,2 cibles/doc contre 33,1 (**+28 %**,
   DATE +40 %). Cause : le test est un tirage aléatoire (seed 0) mais la validation est « les 100
   premiers par `sample_index` », donc les dossiers générés en premier, plus riches. C'est ce qui
   fait échouer toute calibration de seuil. ⚠️ **Concerne aussi `capstone_ecrf/.../validation_protocol.py`
   et le `evaluate.py` publié dans `rntc/lymphome-synth-v5-eval`.** Correctif : validation = tirage
   aléatoire du train.
3. **Split de validation de l'entraînement en tri lexicographique** (`lym_1023 < lym_11 < lym_2`)
   → différent du split capstone. **Corrigé** (tri numérique).
4. **`span_rep` recalculé 3× par document** à l'inférence. **Corrigé** (`doc_ctx` partagé, éval ~3× plus rapide).
5. `taxonomy.match_cat` faisait de la sémantique en regex et **inversait la négation**
   (« absence de réarrangement » → `réarrangement`, « décès non lié au lymphome » → `lié au
   lymphome`, « Mme » → `homme`, « pas de » absent de la liste NON). Impact mesuré : 13,5 % des
   valeurs CAT de Qwen contiennent une négation, dont 1 377 → `None` et 325 → classe affirmative
   — **on pénalisait le baseline**. Remplacé par `label_space.py`.

## 5. Fichiers ajoutés

- `label_space.py` — espace de labels **dérivé des données d'entraînement** : les classes sont
  les valeurs observées, aucun vocabulaire écrit à la main, aucune règle de langue. Couverture
  test : CLOSED 99,2 % · NUMBER 99,9 % · DATE 100 %. Retrouve seul les types (18/18 dates,
  et range OMS/Ann Arbor/Deauville en fermé).
- `error_analysis.py` — décomposition sur/sous-remplissage/fausse valeur, séparation
  sélection vs détection, contrefactuels par classe d'erreur, face-à-face Qwen.
- `route_analysis.py` — aiguillage tête/parsing par taux de copie, seuil choisi sur la validation.
- `calibrate_threshold.py` — calibration global/famille/champ avec repli hiérarchique.
- `RerankHeads` (attention entre candidats + contexte local), loss à marge (`--hard_w`),
  `--max_chars`, `--gold_file`, `--first_n_numeric`, dump des prédictions par champ.

## 6. Chiffres de référence (métrique corrigée, test 410)

| modèle | macro-F1 |
|---|---|
| `v5-v4` @9k (départ de session) | 0.429 |
| `v5-v4` @30k | 0.529 |
| `ctx-norm` @24k | 0.532 |
| `ctx-rerank` @24k | 0.532 |
| **`ctx-norm` aiguillé** | **0.544** |

Ablation des têtes inchangée dans son sens : **CAT +0.121** (la famille dont la valeur n'est pas
écrite), ORD +0.022, DATE +0.024, NUM −0.031. La tête CAT reste la contribution réelle.

## 7. `NULL` dans les têtes — le levier qui marche (fin de session)

**Diagnostic.** `build_dataset` ne construisait une `entry` que pour les champs **ayant une
cible et des spans gold** : médiane **26 champs sur 81** par document. Les têtes n'avaient donc
**jamais vu un seul champ absent** — 100 % de positifs, ~90 000 négatifs inexistants par epoch.
La décision de remplir était sous-traitée à `sigmoid(score de détection) > 0.5`, un score qui
répond à « y a-t-il un span de ce type ici ? », pas à « faut-il écrire cette valeur ? ».

**Ce que valait cette décision (mesuré, `ctx-norm`) :**

| décision de remplir | macro-F1 | champs remplis |
|---|---|---|
| seuil 0.5 | 0.532 | 9 786 |
| aucun seuil (remplir toujours) | 0.407 | 29 979 |
| **décision parfaite, valeurs inchangées** | **0.782** | 9 121 |

La décision parfaite remplit **moins** que l'actuelle. Le problème n'était donc pas « il prédit
trop peu » (ma lecture initiale, fausse) mais **il remplit les mauvais champs** : le modèle sait
produire la bonne valeur pour 9 121 cibles, le seuil n'en fait remonter que 6 124 et ajoute
3 662 valeurs fausses. **+0.250 disponibles sans améliorer une seule prédiction de valeur.**

**Correctif** (`NullHeads`) — proposé par l'utilisateur, meilleur que ma « tête de présence » :
pas de nouveau module, une option de sortie en plus.
- CAT : une option « champ non documenté ». **Zéro paramètre** — c'est une chaîne encodée par
  l'encodeur comme les autres options.
- Sélection : un slot NULL dans le softmax, dont le score dépend du champ **et** du résumé des
  candidats (il peut dire « ils sont tous mauvais »). +394k paramètres.
- `build_dataset` émet une entry pour **tous** les champs non-TXT (absent → cible NULL) :
  132 840 entries dont **77 867 NULL**. Échantillonnage `--neg_ratio` pour tenir le budget.
- Argument métrique : s'abstenir coûte 1 fn, se tromper en coûte 2 (fp + fn) → quand aucun
  candidat ne correspond, **NULL est l'action optimale** et est entraînée comme telle.
- `THRESH_FILL` **supprimé**.

**Résultat (test 410, cap 24k, 1 epoch, métrique corrigée) :**

| | `ctx-norm` | **`v5-null`** | Qwen-9B |
|---|---|---|---|
| CAT | 0.544 | **0.682** | 0.488 |
| ORD | 0.703 | **0.755** | 0.791 |
| NUM | 0.533 | **0.596** | 0.603 |
| DATE | 0.346 | **0.380** | 0.447 |
| **macro-F1** | 0.532 | **0.603** | 0.582 |

**+0.071 en ne changeant que le décideur.** Premier passage devant Qwen-9B sur la métrique
stricte, 150M en single-pass. Les **trois** classes d'erreur baissent ensemble : correctes
6 124 → **7 658** (+25 %), sous-remplissage 5 962 → 4 684, sur-remplissage 2 208 → 1 987,
fausses valeurs 1 468 → 1 212. CAT : sous-remplissage **−66 %**, apport de la tête +0.121 → **+0.252**.

**Réserves.** (1) Sur la métrique équitable (DATE à l'année) Qwen reste devant, **0.646 contre
0.615** : DATE est la seule famille où le sous-remplissage augmente (1 692 → 2 185), la tête a
appris à s'abstenir sur les dates — gain en précision exacte, perte du crédit partiel à l'année.
(2) 1 seul epoch : 0.603 est un plancher. (3) L'aiguillage tête/parsing devient **inutile**
(τ*=1.0, 0.603 = 0.603) — le parsing n'est plus compétitif (0.492).

**Bug évité de justesse** : `predict_doc` supprimait le seuil dès que les têtes savaient
s'abstenir, y compris pour l'appel *baseline* — celui-ci serait devenu « remplir toujours »
(0.407) et l'ablation aurait affiché un +0.13 fictif. Corrigé avant l'éval.

**Trajectoire de la session : 0.429 → 0.529 → 0.532 → 0.603.**

**Suite évidente** : plus d'epochs (le seul run est à 1), `--neg_ratio` plus élevé, et
comprendre l'abstention excessive sur DATE.

## 8. Refonte : matrice d'affectation + transducteur appris (étape 1 validée)

**Diagnostic (3 avis Fable + vérifications).** Les trois échecs de la session — tête de sélection
suiveuse à 96 %, pool de candidats DATE à 0.52, 34 décisions indépendantes — ont **une seule
cause : l'interface `top-12 candidats par champ`**. Goulot non différentiable, construit à partir
du score que la tête doit réviser, et qui isole les champs. Les deux seules choses qui ont marché
(tête CAT, slot NULL) sont **des options dans un softmax**, pas des modules.

**Fait décisif vérifié** (test 410) : **55,7 % des cibles DATE sont exactement une date d'en-tête
de section** (`=== Compte-rendu de RCP — 2017-04-15 ===`) et **0 span gold DATE sur 6 275** ne
tombe sur un en-tête. La moitié des dates est écrite au seul endroit que l'annotation n'annote
jamais. Explique les 1 414 sous-remplissages DATE hors candidats, les champs `news_*` jamais
remplis, et la domination de Qwen sur les dates. ⚠️ **Le verdict « tête de sélection : close »
(§7) est donc PRÉMATURÉ** : les trois réfutations ont tourné sur des pools sans la réponse.

**Étape 0 — dimensionnement (mesuré, test).** La cible est-elle présente quelque part ?

| depuis un span **gold** (ce qu'on supervise) | **52,4 %** |
|---|---|
| depuis **n'importe quel** span : DATE (pool doc, exact) | **89,5 %** |
| ORD / NUM (borne haute optimiste, tolérance 10 %) | 99,1 % / 99,6 % |

L'information est dans le texte ; c'est l'annotation qui la rate.

**Design retenu.** GLiNER inchangé. On garde la matrice `S = span_rep ⊗ schema` [champs × spans]
au lieu de la réduire au top-12 par ligne. Options d'un champ = {tous les spans} ∪ {vocabulaire
observé, encodé comme chaînes} ∪ {⊥}. Un seul softmax, normalisé sur les deux axes (la compétition
entre champs remplace le role-binding, coût nul). Deux têtes : **A affectation** (~1.2M) et
**B transducteur** (~1.7M, partagé par les 89 champs). Loss unique à variable latente :
`−log Σ_spans P_A(span|champ)·P_B(valeur|span,champ)` → **le span est latent, on ne supervise que
la valeur**. Un span d'en-tête jamais annoté reçoit de la masse dès que le transducteur sait en
tirer la bonne valeur. Invariant : **zéro paramètre par champ et par classe**.

**Objection mesurée au design, et correctif.** Le softmax sur l'axe des champs suppose « un span
sert au plus un champ » : **faux 20,4 % du temps** (`news_date_of_last_news` ↔
`news_date_of_last_visit` partagent la date **214 fois**). Correctif : force de la compétition
**apprise** (scalaire α initialisé à 0), pas imposée.

**ÉTAPE 1 — VALIDÉE.** Transducteur seul (`transducer/`), entrée `"<libellé> | <texte du span>"`,
sortie caractère par caractère, 1.7M params, 65 426 paires d'entraînement / 15 807 de test,
**5 minutes** sur 1 GPU :

| exact-match test | `taxonomy.py` (300 l. écrites main) | **transducteur** | Δ |
|---|---|---|---|
| CAT | 0.501 | **0.914** | **+0.413** |
| DATE | 0.663 | **0.733** | +0.070 |
| NUM | 0.714 | **0.832** | +0.118 |
| ORD | 0.902 | **0.969** | +0.067 |
| **total** | **0.630** | **0.869** | **+0.239** |

Gagne sur les 4 familles, **handicapé** (ne voit que le span, sans contexte, alors que `span_rep`
est contextuel dans le design réel) et **jugé plus durement** (chaîne exacte vs canon propre pour
`taxonomy`). CAT 0.914 vs 0.501 confirme que les regex de synonymes inversant la négation
coûtaient énormément. → **`taxonomy.py` peut être supprimé.**

**Limite** : mesuré sur spans **gold** (propres) ; en déploiement les spans sont prédits, plus
bruités. Et ça ne mesure pas la partie dure — trouver le bon span.

**Étape 2 (à faire)** : tête d'affectation complète, loss unique, supervision par la valeur.
Trois mesures, pas une : (1) macro-F1 vs **0.603** ; (2) rappel du pool DATE, doit passer de
**0.52** vers ~0.9 — test direct de « supervision par la valeur, pas par le span » ; (3) macro-F1
restreint aux 37 % de champs indexés par un rôle, avec et sans compétition entre champs.
Risque principal : assignation de crédit avec span latent sur ~256 candidats et 1 540 documents.
