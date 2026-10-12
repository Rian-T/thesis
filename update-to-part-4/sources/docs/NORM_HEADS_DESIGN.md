# Normalization Heads — spec de recherche (2026-07-22)

> **But** : étendre le GLiNER eCRF (150M, lignée v5/`V5MIX6`) d'un extracteur de **spans**
> vers un extracteur de **valeurs normalisées** — en un seul forward pass — via de petites
> têtes typées greffées sur les spans prédits. Cible : formulaire eCRF rempli et exploitable
> pour la recherche clinique (cohortes, stats, survie), sans décodage autorégressif.
>
> **Statut** : SPEC (design validé oralement sur l'approche B, à approuver par écrit).
> **Voir aussi** : `GOLD_V2_DESIGN.md` (gold TAPDL v5), `capstone_ecrf/RESULTS.md` (baselines),
> `../../biomed-fr-v4/lymphome_v4/annotation.py` (pydantic 89 champs), `labels.py`.

---

## 1. Motivation & questions de recherche

Le GLiNER eCRF v5 atteint **value-F1 0.64–0.657** (parité Qwen-4B, 27× plus petit). MAIS ce
« value » = **le texte brut du span**, matché par un scorer tolérant (token-Jaccard ≥ 0.5). Ce
n'est **pas** une valeur normalisée : « 1m75 » reste « 1m75 », « réarrangement de MYC mis en
évidence » reste du texte, « stade avancé » ne devient pas `IV`. Pour la recherche clinique
réelle il faut `175` (cm), `POSITIF`, `IV`, `2018-04-12`.

**RQ1 (faisabilité)** — peut-on produire la valeur *normalisée* de chaque champ eCRF par une tête
légère greffée sur les spans GLiNER, à budget quasi nul (params + compute + latence) ?

**RQ2 (agrégation)** — le pooling d'un **ensemble** de spans candidats (top-k) bat-il le top-1 sur
les champs qui exigent d'agréger plusieurs mentions (`nombre d'organes atteints`, scores) ?

**RQ3 (single-pass vs génératif)** — un encodeur 150M multi-tête égale-t-il un générateur
(Qwen-4B) sur la **valeur normalisée**, tout en restant structuré/calibré/déployable ?

**RQ4 (généralisation)** — des têtes *partagées conditionnées sur le type* (vs une tête par champ)
préservent-elles l'esprit open-vocab (transfert vers champs/vocabs non vus) ?

**Argument central du papier** (à ne PAS confondre avec « +F1 ») :
> *Single-pass structured & normalized eCRF filling* : un seul encodeur 150M sort le formulaire
> rempli ET normalisé en un forward pass — là où le générateur rend du texte à re-parser.
> Lignée **attribute-value extraction / slot-filling** (OpenTag, AVEQA, generative AVE) transposée
> au clinique français multi-documents.

---

## 2. Taxonomie des 89 champs → 5 familles de têtes (ancrée sur le pydantic)

Décompte du pydantic `LymphomeAnnotation` : 97 champs déclarés − 5 `evaluation_*` méta
− 3 structurellement vides (`hasenclever`, `tmtv`, `tmts`) = **89 champs cibles**.

| Famille | Tête | ~N | Espace de sortie | Exemples (desc. verbatim) |
|---|---|---|---|---|
| **CAT** catégoriel nominal | classif softmax type-conditionnée | ~38 | enum fini (2–11) | `myc_fish`{Réarrangement,Pas}, `coo_test`{GC,NGC,indét}, `first_line_treatment`{CHOP,R-CHOP,…11}, `response`{RC,RP,Prog,Stable}, `vital_status`{vivant,décédé}, `tumor_origin`{ggl,non-ggl}, tous les `*_realised`/`yes-no` |
| **ORD** ordinal borné | classif ordinale (CORAL/CORN) | ~9 | entier ∈ [lo,hi] | `oms`0-5, `ipi`0-5, `flipi`0-5, `aaipi`0-3, `ann_arbor`I-IV, `deauville`1-5, `grade_ctcae`0-5 |
| **NUM** numérique continu | régression (Huber) + tête d'unité | ~18 | réel + unité canon | `weight`(kg), `height`(→cm), `ldh`, `suvmax`, `dmax`, `*_ihc_raw`(%), `n_organs`, `cycles_n`, `largest_tumor_size`, `extranodalinv_n`, `gelf`, `eortc` |
| **DATE** date | normalisation temporelle | ~16 | YYYY-MM-DD (+ offset) | `date_of_diagnosis`, `first_line_start/end`, `date_of_death`, `date_progression`, toutes les `imaging_date_*`, `news_date_*` |
| **TXT** texte libre | AUCUNE (span brut) | ~8 | span verbatim | `disease_subtype`, `morphological_variant`, `antecedents_other`, `*_adverse_effects_description`, `extra_ganglionary_sites`, `professional_category` |

> Ambiguïtés à trancher en §3.2 : `ann_arbor` mélange chiffre (I-IV) + suffixe (A/B) → 2 sorties ;
> `second_line_treatment` semi-ouvert (enum + « autre ») → CAT avec classe OOV + fallback TXT ;
> `*_ihc` (Positif/Négatif = CAT) vs `*_ihc_raw` (% = NUM) sont deux champs distincts, cohérent.

---

## 3. Supervision : d'où viennent les cibles normalisées (le déblocage)

### 3.1 Sources gold (gratuites, truth-anchored)
1. **Stage-1 `Event.key_values`** (`../../biomed-fr-v4/lymphome_v4/schemas.py`) : dict structuré
   normalisé = la VÉRITÉ qui a généré les CR. Source primaire des cibles.
2. **Stage-3 `VariableInstance.value`** (`annotation.py`) : valeur par occurrence, déjà semi-normalisée.
3. **v5 gold TAPDL** (`lymphome_{train,test}_v2.jsonl`) : fournit les **spans** (entrée des têtes) +
   le lien champ↔span truth-anchored (role-binding 1L/2L déjà résolu par le CR daté).

→ Pour chaque (dossier, champ) on a : spans d'entrée (v5) **et** valeur normalisée cible (timeline).
**Aucune annotation supplémentaire.**

### 3.2 Canonicalisation des cibles (LE chantier data, cf. risque R1)
Script `norm/build_targets.py` (à écrire), déterministe + audit :
- **CAT** : mapper chaque `value` gold sur l'enum canon du champ (dérivé des `desc` pydantic).
  Match exact → sinon fuzzy → sinon `OOV`. Journaliser le taux off-vocab par champ (comme snap CIM-10 v3d).
- **NUM** : parser nombre + unité, convertir vers l'unité canon (height m→cm, poids kg, LDH U/L,
  % pour IHC). Rejeter les valeurs hors bornes physiologiques (garde-fou).
- **ORD** : caster en entier borné ; « stade avancé »/prose → laissé à la tête (pas de cible dérivable
  sans span, on n'invente pas).
- **DATE** : ISO-parse `YYYY-MM-DD`/`YYYY-MM` ; stocker aussi **offset en jours depuis la date-index**
  (= `date_of_diagnosis`) → cible robuste pour survie, indépendante de l'année absolue.
- Sortie : `targets_{train,val,test}.jsonl` = `{doc_id, field, family, target_norm, target_aux}`.
- **Gate qualité** : % cibles parsées par famille, distribution, taux OOV. Doit passer avant training.

---

## 4. Architecture B — top-k spans → set-pooling → tête typée

### 4.1 Vue d'ensemble (un seul forward, greffé sur GLiNER figé)
```
CR/dossier ──► GLiNER encoder (v5, FIGÉ stage-A) ──► span reps {h_i} + scores {s_i} par type f
                                                          │
   pour chaque champ f :  top-k spans du type f  ─────────┤
                                                          ▼
                          e_f (embedding du type/description, déjà produit par GLiNER)
                                                          │  query
                          SetEncoder = attention-pool( query=e_f, kv={h_i}, bias=logit(s_i) )
                                        + features aux (nombres parsés, offsets de span, source_doc)
                                                          ▼  z_f  (vecteur agrégé du champ)
                          route(family(f)) ──► { CAT-head | ORD-head | NUM-head | DATE-head }
                                                          ▼
                                        valeur normalisée + confiance calibrée
```

### 4.2 Sélection des candidats
Pour le type `f`, GLiNER fournit tous les spans avec score ≥ τ_low (τ_low bas, ex. 0.01 — on veut
du rappel de candidats, la tête tranche). Garder **top-k=5** par score. Si 0 candidat → champ = `∅`
(non rempli). Si 1 → pooling dégénère en top-1 (cohérent).

### 4.3 SetEncoder (le cœur de l'approche B)
Pooling par attention à une couche (DeepSets-like, permutation-invariant) :

```
α_i = softmax_i( (W_q e_f)·(W_k h_i)/√d + β·logit(s_i) )      # s_i biaise l'attention
z_f = Σ_i α_i · (W_v h_i)  ⊕  g(aux_i)                         # ⊕ = concat features agrégées
```
- `β` apprenable : dose la confiance du détecteur dans l'agrégation.
- `aux_i` par span : nombre(s) regex-parsés, longueur, position relative dans le dossier, one-hot
  du type de CR source (utile pour dates/lignes). Agrégés (mean+max) → `g(aux)`.
- **Justification** : l'attention conditionnée sur `e_f` laisse chaque champ pondérer ses spans
  différemment ; le biais `s_i` injecte la calibration du détecteur ; permutation-invariance =
  robuste à l'ordre/au nombre de mentions (RQ2). ~0.5–1M params partagés.

### 4.4 Têtes (PARTAGÉES, conditionnées sur le type — RQ4)
- **CAT-head** : au lieu d'une matrice de classes par champ, on score chaque option d'enum par
  similarité `⟨MLP(z_f), emb(option_label)⟩` (mêmes embeddings texte que GLiNER pour les descriptions).
  → **zéro-shot sur vocabs nouveaux** ; ajoute une classe `∅`/`OOV`.
- **ORD-head** : régression latente `u = w·z_f + b` → K-1 seuils cumulatifs (CORAL) → entier borné.
  Respecte l'ordre (0<1<2…), meilleur que softmax nominal sur les scores.
- **NUM-head** : `ŷ = MLP(z_f ⊕ parsed_numbers)`, loss Huber en espace normalisé (log1p pour LDH/SUV).
  Tête d'unité (petite CAT) si ambiguïté d'unité. **Doit battre le regex top-1** (baseline §7).
- **DATE-head** : deux modes — (a) *copy-parse* si un span contient une date ISO-able → parse
  déterministe ; (b) *resolve* si date relative (« 6 mois après ») → régression de l'offset en jours
  vs date-index, puis reconversion. Sortie = `YYYY-MM-DD` + offset.
- **TXT** : pas de tête, on renvoie le span top-1 (déjà le comportement v5).

### 4.5 Ce qui n'est PAS modifié
Backbone GLiNER, tête NER de spans, décodeur `extract_json` : intacts. On lit `h_i`, `s_i`, `e_f`
déjà calculés. → aucune régression possible sur le NER v5 (contrairement au stage-2 clinique v3c).

---

## 5. Entraînement

### 5.1 Deux temps (safe puis fin)
- **Stage-A (têtes seules, backbone figé)** : rapide, robuste, isole l'apport des têtes. LR ~1e-3.
  SetEncoder + 4 têtes seulement. Quelques H100-heures.
- **Stage-B (fine-tune conjoint léger)** : dégèle l'encodeur à LR bas (~1e-5) + têtes, **replay
  du NER v5** (mix) pour ne pas émousser la tête de spans (leçon v3d : multi-task peut dégrader le NER).
  Optionnel, seulement si Stage-A plafonne.

### 5.2 Loss
`L = λ_cat·CE + λ_ord·CORAL + λ_num·Huber + λ_date·(Huber_offset + CE_isodate) [+ λ_ner·L_NER (stage-B)]`
- Masquée sur les champs `∅` (pas de cible) — on n'entraîne une tête que si cible gold présente.
- Poids `λ` équilibrés par fréquence de famille (les CAT dominent en nombre).
- Cibles ∅ apprises aussi (classe « non rempli ») pour la **précision** (ne pas halluciner un score).

### 5.3 Données
Entrée = spans v5 (train 1640 dossiers) ; cibles = §3.2. Split identique v5 (seed 0, test 410 gelé).
Val 100 docs pour le choix des seuils de confiance (comme le capstone).

---

## 6. Inférence (single-pass)
1. GLiNER forward → spans+scores tous types.
2. Par champ : top-k → SetEncoder → tête → valeur normalisée + confiance.
3. Émettre le **formulaire eCRF rempli** : `{field: {value_norm, span_evidence, confidence}}`.
Latence : 1 forward encodeur (déjà fait) + têtes sur ≤5×89 spans. **Négligeable** vs décodage Qwen.

---

## 7. Évaluation (le protocole, miroir du capstone)

Test = 410 dossiers gelés. Seuils choisis une seule fois sur val (100). Par **famille** :

| Famille | Métrique primaire | Baselines à battre |
|---|---|---|
| CAT | accuracy / macro-F1 normalisée | (a) span-brut→exact-match enum ; (b) Qwen-4B `value` normalisée |
| ORD | accuracy + MAE ordinale (off-by-one) | idem |
| NUM | **within-tolerance acc** (\|ŷ−y\|/y ≤ 10%) + MAE ; **regex-parse du top-1 span** (baseline dure) | + Qwen |
| DATE | exact-date acc + \|Δjours\| médian | parse-du-span ; Qwen |
| TXT | span-F1 (inchangé v5) | — |

**Métrique agrégée** : *Normalized-eCRF accuracy* = moyenne pondérée par champ des accuracies
normalisées (analogue au value-F1 mais sur valeurs CANON, pas texte).

**Ablations** (répondent aux RQ) :
- **A1 top-1 vs top-k pooling** (RQ2) : SetEncoder dégénéré (k=1) vs k=5. Attendu : gain sur
  NUM-agrégés (`n_organs`), scores.
- **A2 têtes partagées type-cond. vs 1-tête-par-champ** (RQ4) : + un split *leave-fields-out*
  (entraîner sur 70 champs, tester la CAT-head zéro-shot sur 19 champs jamais vus).
- **A3 stage-A figé vs stage-B conjoint** : gain vs coût + contrôle non-régression NER v5.
- **A4 avec/sans features aux** (nombres parsés, source_doc).
- **Calibration** : ECE par famille (le single-pass doit être calibré — argument déploiement).

**Comparaison phare (RQ3)** : Normalized-eCRF acc du 150M multi-tête vs Qwen-3.5-{2,4,9}B en
génération normalisée (re-parse de leur sortie sur le même espace canon). Test apparié + bootstrap
doc-level (comme capstone). Rapporter aussi **latence & params** (l'argument déploiement).

---

## 8. Risques & mitigations
| # | Risque | Mitigation |
|---|---|---|
| R1 | `key_values`/`value` gold bruités (générés LLM) → cibles NUM/CAT sales | §3.2 canonicalisation + gate qualité + bornes physiologiques ; auditer un échantillon |
| R2 | Dates relatives (« 6 mois plus tard ») dures | DATE-head mode *resolve* (offset) ; sous-étude séparée ; fallback copy-parse |
| R3 | Silver-as-gold : têtes validées sur silver | même plan que NER : mini-pass humain n≈120 sur valeurs normalisées (quand humain dispo) |
| R4 | Stage-B émousse le NER v5 | replay NER + monitorer det-recall v5 ; sinon rester stage-A figé |
| R5 | Champs rares (peu d'exemples gold) → tête sous-entraînée | têtes partagées (transfert inter-champs) ; reporter par fréquence |
| R6 | Fuite : la date-index (`date_of_diagnosis`) sert d'ancre ET est un champ cible | évaluer les offsets avec date-index prédite (pas gold) en ablation |

## 9. Faisabilité / coût (verdict)
- **Params** : +1–3M (SetEncoder + 4 têtes partagées). Négligeable sur 150M.
- **Compute** : Stage-A = quelques H100-heures (backbone figé, forward cache-able). Stage-B optionnel.
- **Latence inférence** : +1 passe légère. Déployable.
- **Coût dominant = data** (§3.2), pas la compute. Même nature que le snap CIM-10 v3d (déjà fait une fois).
- **Verdict** : idée solide, bien alignée (recherche clinique sur valeurs normalisées), peu coûteuse,
  argument papier propre (single-pass structured+normalized eCRF). Approche B (pooling top-k) justifiée.

## 10. Plan d'expériences (jalons)
1. **M0 — targets** : `norm/build_targets.py` + gate qualité §3.2. Livrable : `targets_*.jsonl` + rapport OOV/parse.
2. **M1 — Stage-A** : SetEncoder + têtes sur backbone figé ; éval §7 vs baselines span-brut/regex.
3. **M2 — ablations** A1/A2/A4 + calibration.
4. **M3 — comparaison Qwen** (RQ3) + tableau params/latence.
5. **M4 (si besoin)** — Stage-B conjoint + contrôle non-régression NER v5.
6. **M5 (différé)** — ancrage humain n≈120 valeurs normalisées.

## 11. Fichiers à créer (aucune modif de `GLiNER2/gliner2/*` — règle projet)
```
gen/lymphome/norm/
├── build_targets.py       # §3.2 : cibles normalisées depuis timeline + v5 gold
├── heads.py               # SetEncoder + CAT/ORD/NUM/DATE heads (partagées, type-cond.)
├── train_norm.py + .sbatch# stage-A (figé) puis stage-B (conjoint, replay NER)
├── eval_norm.py           # §7 : normalized-eCRF acc par famille + ablations + calibration
└── NORM_HEADS_DESIGN.md   # (ce doc, déplacé ici si besoin)
```
Env : data/eval = `tabib`/`bge`, pas d'annotation LLM nouvelle (cibles = déjà générées).
