# Design V2 — matrice d'affectation + transducteur appris

> **En une phrase.** On arrête de dire au modèle *où chercher* et *comment convertir* ; on lui dit
> seulement *quelle valeur on veut*, et on le laisse apprendre les deux.
>
> ⚠️ **Cette phrase est vraie, mais pas par le mécanisme décrit plus bas.** Mesuré le 2026-07-29 :
> la supervision par la valeur apprend bien au modèle *où chercher*, mais elle le fait en
> **reformant l'encodeur** (le score de détection `S` monte de +0.062 au rang 1, +0.116 sur DATE),
> **pas** via la tête d'affectation — celle-ci, privée de son ancrage sur `S`, tombe à 0.215.
> La tête est un tuyau. Le §10 tire les conséquences.

État au 2026-07-28 (§1-8), révisé le 2026-07-29 (§9-10). Remplace le pipeline `détection → top-12 candidats par champ → têtes`.
Référence des mesures : `JOURNAL.md` §7 et §8.

---

## 1. CONTEXTE — d'où on part

**La tâche.** Remplir un eCRF de 89 champs typés depuis un dossier patient longitudinal français
(~22 000 caractères, plusieurs comptes-rendus successifs). Pour chaque (document, champ) :
produire UNE valeur canonique, ou constater que le champ n'est pas documenté.
Métrique : macro-F1 par famille au niveau (document, champ). **Une valeur fausse coûte 2**
(faux positif + faux négatif), **une abstention à tort coûte 1**. La politique de remplissage est
donc un objet de premier ordre, pas un détail de post-traitement.

**Où on en est.** macro-F1 **0.603** contre **0.582** pour un LLM Qwen3.5-9B qui lit tout le
dossier — avec 150M de paramètres en un seul passage. Trajectoire de la session : 0.429 → 0.529
(lire le dossier entier) → 0.532 (entraîner au contexte plein) → 0.603 (abstention apprise).

**Ce qui est mesuré et qui contraint tout le reste :**

| fait | valeur |
|---|---|
| valeurs cibles **pas littéralement** dans le texte | ~48 % |
| taux de copie **à l'intérieur** de chaque famille | de 0.00 à 1.00 |
| cibles DATE égales à une **date d'en-tête de section** | **55,7 %** |
| spans gold DATE tombant sur un en-tête | **0 sur 6 275** |
| cible récupérable depuis un span **gold** | 52,4 % |
| cible récupérable depuis **n'importe quel** span (DATE, exact) | **89,5 %** |
| masse des cibles indexée par un **rôle** (1L / 2L / événement) | 37 % |
| gain d'une décision de remplissage **parfaite** (oracle) | +0.139 |

---

## 2. LE PROBLÈME — pourquoi le design actuel plafonne

Trois échecs mesurés, **une seule cause**.

| symptôme | mesure |
|---|---|
| la tête de sélection suit la détection | accord **96 %**, +850k params pour une **égalité stricte** (0.532 = 0.532) |
| le pool de candidats ne contient pas la réponse | rappel DATE **0.52** |
| les champs décident isolément | 34 décisions indépendantes pour **une seule** affectation |

**La cause commune : l'interface `top-12 candidats par champ`.**

1. C'est un **goulot non différentiable** placé avant les têtes : ce qui est jeté à cette étape
   est perdu définitivement.
2. Il est **construit à partir du score que la tête doit réviser** — on demande à quelqu'un de
   corriger sa copie avec sa propre grille, d'où les 96 % d'accord.
3. Il **isole les champs** : « date de 1re ligne » et « date de 2e ligne » ne se rencontrent jamais.

**Et la supervision porte sur le mauvais objet.** On entraîne le modèle à pointer *là où
l'annotateur a pointé*. Or l'annotateur n'a jamais pointé sur un en-tête de section — où vivent
55,7 % des dates. Le modèle ne peut donc structurellement pas les trouver.

> ⚠️ Conséquence sur les conclusions passées : les **trois** réfutations de la tête de sélection
> (attention entre candidats, loss à marge, contexte plein) ont tourné sur des pools sans la
> réponse une fois sur deux. **Le verdict « tête de sélection : close » est prématuré.**

**Observation qui oriente la solution :** les deux seules choses qui ont marché — la tête CAT
(+0.121, puis +0.252) et le slot `NULL` (+0.071) — sont **des options supplémentaires dans un
softmax**, pas des modules. Le design ne fait que généraliser ça.

---

## 3. CE QU'ON FAIT — le design

GLiNER reste la base, **inchangé** (`gliner2/*` intact, encodeur, schéma et texte dans la même
séquence, `compute_span_rep`, score bilinéaire champ × span).

### 3.1 On garde la matrice au lieu de la détruire

GLiNER calcule déjà `S = span_rep ⊗ schema`, de forme `[F champs × M spans]`. Aujourd'hui on la
réduit au top-12 par ligne. **Demain on la garde.** Rien de nouveau n'est calculé.

### 3.2 Les options d'un champ

```
O_f  =  { tous les spans du document }  ∪  { vocabulaire observé de f }  ∪  { ⊥ }
          bloc COPIE (partagé)             bloc VOCAB (chaînes encodées)   abstention
```

Une seule distribution `P(option | champ, doc)`. La valeur prédite est la chaîne du vocabulaire
si VOCAB gagne ; `transducteur(span, champ)` si COPIE gagne ; rien si `⊥` gagne.

### 3.3 Deux têtes, et deux seulement

| tête | params | entrées | sortie |
|---|---|---|---|
| **A — affectation** | **2.17 M** (mesuré) | `span_rep`, `S`, options encodées, résumé du doc conditionné au champ | `P(option \| champ)` |
| **B — transducteur** | **2.00 M** (mesuré), **partagé par les 89 champs** | caractères du span + libellé du champ + `span_rep` | la valeur canonique, caractère par caractère (≤32) |

*(les ~1.2 M / ~1.7 M annoncés initialement étaient des estimations ; ci-dessus, les tailles réelles.)*

**Normalisation sur les deux axes.** `S` est normalisé sur l'axe des **spans** (quelle valeur pour
ce champ) *et* sur l'axe des **champs** (quel champ pour ce span), le second injecté comme biais
log dans le premier. Coût : **zéro paramètre**. C'est ce qui remplace le role-binding.

> ⚠️ **Correctif obligatoire** : « un span sert au plus un champ » est **faux 20,4 % du temps**
> (`news_date_of_last_news` ↔ `news_date_of_last_visit` partagent la date **214 fois**). La force
> de la compétition doit être **apprise** — un scalaire α initialisé à 0 — jamais imposée.

**Résumé du document conditionné au champ : sum-pooling, pas moyenne.** La norme croît avec le
nombre de spans détectés, donc le **comptage** devient représentable sans tête dédiée.

### 3.4 La loss, unique

```
L  =  − log  Σ    P_A(span | champ) · P_B(valeur | span, champ)
             spans
```

Vraisemblance marginale : **le span est latent, on ne supervise que la valeur finale.**

C'est le cœur du design. Un span d'en-tête que personne n'a annoté **reçoit de la masse dès que
le transducteur sait en tirer la bonne valeur**, et le gradient remonte son score d'affectation.
On n'apprend plus à pointer où l'annotateur a pointé, mais **là d'où sort la bonne réponse**.

### 3.5 Quatre correctifs issus de la relecture critique

Aucun n'ajoute de cas particulier ; chacun corrige une asymétrie qui n'est pas dans les données.

1. **VOCAB gaté sur les champs fermés.** Un champ ne reçoit un bloc VOCAB que si `label_space`
   le classe `CLOSED` (règle déjà dérivée des données). Sans ce garde-fou, **13 % des cibles DATE
   de test sont littéralement dans le vocabulaire d'entraînement** : le modèle emprunte la route
   VOCAB, et **le rappel du pool resterait plat pendant que le macro-F1 monterait** — on
   conclurait au mauvais endroit. *(Déjà en place : `derive` met `classes=[]` hors CLOSED.)*
2. **Température apprise sur `log P_B`.** `P_A(vocab)` est **atomique** alors que
   `P_A(copie)·P_B` est un produit sur ~10 caractères : à évidence égale la route COPIE est
   pénalisée par un **artefact de paramétrisation**. Un scalaire partagé, `tau`, les remet à
   la même échelle.
3. **Inférence par somme sur les valeurs, pas sur les options.** Une même date apparaît dans
   3 à 8 spans du pool ; un argmax sur les options divise sa masse entre eux et la fait perdre
   contre une option VOCAB atomique — c'est-à-dire pénaliser la valeur **la mieux attestée**.
   On agrège par chaîne canonique, puis on remplit ssi `p_v > 0.5`. Ce seuil n'est pas réglé :
   il tombe de la matrice de coût (`coût(remplir) = 2 − q₀ − 2p_v` contre `coût(s'abstenir) =
   1 − q₀`), indépendamment de `q₀`. **⊥ sort de l'argmax** : c'est une décision, pas une classe.
4. **`span_rep` branché sur l'état initial du décodeur de B**, via une projection **initialisée
   à zéro** (démarrage à chaud rigoureusement inchangé). Sans elle, B ne lit que des caractères :
   l'encodeur ne reçoit de la route COPIE qu'une responsabilité scalaire via A — signal de type
   EM, faible — et **B ne peut jamais corriger une frontière de span**.

**Mitigation de l'élagage dur** (à appliquer si le rappel du pool bride l'entraînement) :
ajouter K spans tirés **uniformément** par document. Élaguer dur une variable latente biaise la
marginale ; un échantillon aléatoire restaure le support. C'est de l'échantillonnage de latente,
pas une rustine.

### 3.6 Invariant non négociable

**Zéro paramètre par champ et par classe.** Tout ce qui est spécifique au schéma est une *chaîne*
qui traverse l'encodeur. Les mêmes poids marchent sur un autre eCRF, une autre langue, une classe
jamais vue à l'entraînement. C'est ce qui distingue ce design d'un classifieur à 89 têtes.

---

## 4. POURQUOI — comment chaque difficulté est traitée, sans cas particulier

| situation | part | mécanisme (le même pour tous) |
|---|---|---|
| **inférence** — « vit seule dans un appartement à Nancy » → `urbain` | | bloc VOCAB : l'option est une chaîne encodée. C'est la tête CAT, celle qui marche |
| **composition** — « entre avril et octobre 2017 » → `2017-10` | | bloc COPIE : le transducteur est **conditionné par le champ**, donc « début » et « fin » transduisent le même span différemment |
| **comptage** — 4 protocoles cités → `5` | | bloc VOCAB alimenté par un résumé **sum-pooled** : la masse de détection est la statistique suffisante |
| **absence** — rien d'écrit → `non` | | `non` est une option de VOCAB, `⊥` en est une autre : elles se disputent la même masse. **« non documenté » et « documenté comme négatif » cessent d'être confondus** |
| **rôle** — 1L vs 2L vs événement | 37 % | softmax sur l'axe des champs : les 34 décisions deviennent une affectation |
| **en-têtes de section** | 55,7 % des dates | supervision par la valeur : aucune regex, aucun pool construit à la main |

**Limite assumée** : une composition qui exige **deux spans distants** (une date d'en-tête + un
délai dans le texte) n'est pas couverte. On préfère l'écrire que d'ajouter un cinquième mécanisme.

---

## 5. QUAND — le plan, par étapes falsifiables

### ✅ Étape 0 — dimensionnement (fait)
La cible est-elle atteignable depuis un span quelconque ? DATE **89,5 %** (exact, pool document)
contre **52,4 %** depuis un span gold. **L'information est dans le texte ; c'est l'annotation qui
la rate.** → le canal COPIE vaut le coup.

> ⚠️ **Le 89,5 % ne s'est PAS reconstitué** au diagnostic de l'étape 2 (§ Étape 1bis). La mesure
> qui s'en approche le plus y plafonne à 0,82 sur un pool de 1 024 spans. **Ne plus citer 89,5 %
> tant qu'il n'est pas reproduit** : soit la mesure d'origine était plus permissive (canon libre
> plutôt que chaîne exacte), soit elle portait sur un autre ensemble de spans.

### ✅ Étape 1 — le transducteur seul (fait, 5 min GPU)
Entrée `"<libellé> | <texte du span>"`, sortie caractère par caractère. 1.7 M params,
65 426 paires d'entraînement / 15 807 de test.

| exact-match test | `taxonomy.py` (300 l. à la main) | **transducteur** | Δ |
|---|---|---|---|
| CAT | 0.501 | **0.914** | **+0.413** |
| DATE | 0.663 | **0.733** | +0.070 |
| NUM | 0.714 | **0.832** | +0.118 |
| ORD | 0.902 | **0.969** | +0.067 |
| **total** | **0.630** | **0.869** | **+0.239** |

Gagne sur les 4 familles, **handicapé** (ne voit que le span, sans contexte) et **jugé plus
durement** (chaîne exacte vs canon libre pour `taxonomy`). → **`taxonomy.py` peut disparaître.**
*Limite : mesuré sur spans gold (propres) ; en déploiement les spans sont prédits.*

### ✅ Étape 1bis — la tête B rendue intégrable, et le pool mesuré (fait)

**1. Le conditionnement du champ déménage vers le décodeur.** L'étape 1 mettait le libellé dans
l'entrée caractère, ce qui obligerait à ré-encoder les M spans du document *une fois par champ*
dans la loss marginale (~26 fois le même travail). Le span est désormais encodé seul et le
libellé conditionne l'état initial du décodeur : **un encodage par document, partagé**.
À budget identique, c'est aussi meilleur — donc le déplacement est gratuit :

| exact-match test | libellé dans l'entrée (étape 1) | **libellé au décodeur** |
|---|---|---|
| CAT | 0.914 | **0.928** |
| DATE | 0.733 | **0.757** |
| NUM | 0.832 | **0.898** |
| ORD | 0.969 | **0.982** |
| **total** | **0.869** | **0.895** |

**2. Le pool contient-il la réponse ?** (`pool_diagnostic.py`, 60 documents d'entraînement,
valeur produite par le transducteur, égalité stricte.) C'est le go/no-go : ce qui n'est pas dans
le pool est perdu **avant la première dérivée**.

| DATE, rappel du pool | `max_f S[f,span]` | critère **rang** |
|---|---|---|
| actuel — top-12 par champ | 0.61 | — |
| M = 128 | 0.312 | — |
| M = 256 | 0.613 | **0.758** |
| M = 1024 | 0.824 | 0.821 |

**Ce que ça tranche :**
- **La mesure décisive bouge** (0.61 → 0.82) : le critère de falsification est franchi, on continue.
- **Le critère par rang domine à petit budget et converge à grand.** Les scores bruts de deux
  champs ne sont pas à la même échelle, donc `max_f` laisse les champs bruyants monopoliser le
  pool ; à 256 spans le rang obtient ce que `max_f` demande ~700 spans pour atteindre. Une fois le
  pool large, l'ordre de sélection cesse d'importer. → **point de fonctionnement : rang.**
- NUM 0.786 → **0.998**, ORD **0.000 → 0.823** (`taxonomy.py` échoue totalement sur ORD).
- CAT baisse (0.53 → 0.37) et **c'est sans conséquence** : le diagnostic ne mesure que la route
  COPIE, or les CAT passent par VOCAB (48 % des cibles ne sont pas dans le texte).
- **La part des spans gagnants ne chevauchant aucun span gold croît avec la taille du pool**
  (DATE 0.49 → 0.59) : plus on élargit, plus on récupère de valeurs jamais annotées. C'est
  l'hypothèse des en-têtes, confirmée dans le bon sens.

**Réserve de méthode :** la colonne « littéral » du diagnostic est **mal nommée**. Elle ne borne
rien par le haut — la cible est canonique (`2017-04-15`, `62.0`) alors que le texte est en surface
(`15/04/2017`, `62`), d'où des `0.000` sur NUM. Elle sous-estime.

### ⏳ Étape 2 — la tête d'affectation (à faire)
Loss unique, span latent, sans freeze. Transducteur **initialisé depuis l'étape 1** (démarrage à
chaud). Loss de détection native conservée **en auxiliaire à poids faible** — ne pas l'annuler.

**Trois mesures, pas une :**
1. macro-F1 test 410 contre **0.603** ;
2. **rappel du pool DATE : doit passer de 0.52 vers ~0.9** ← test direct de « supervision par la
   valeur, pas par le span ». C'est la mesure la plus importante ;
3. macro-F1 restreint aux **37 %** de champs indexés par un rôle, **avec et sans** compétition
   entre champs (ablation).

**Falsification :** si (2) ne bouge pas, l'explication « en-têtes jamais annotés » est fausse ou
la saillance n'est pas apprenable par supervision de valeur seule → le design tombe.
Si (3) est nul en ablation, retirer la compétition entre champs (elle est gratuite, elle ne doit
pas rester par confort). Si (1) ≤ 0.603 alors que (2) et (3) bougent, le goulot est ailleurs.

**Risque principal :** assignation de crédit avec span latent sur ~256 candidats et 1 540
documents. Mitigations : démarrage à chaud, élagage à M ≈ 256 spans par un critère **indépendant
du champ** (`max_f S[f, span]`, pas un top-k par champ — sinon on réintroduit le goulot), somme
tronquée aux 16 meilleures options par champ.

### ⏳ Étape 3 — nettoyage
Suppression effective du code mort une fois l'étape 2 validée (§6).

---

## 6. CE QU'ON SUPPRIME — ~700 lignes en moins pour ~250 en plus

| fichier / composant | raison |
|---|---|
| **`taxonomy.py` en entier** | familles, synonymes, bornes, conversions, parsing de dates FR. Battu 0.869 vs 0.630. Inversait les négations |
| `native_candidates`, `CAND_K`, `CAND_WLIM`, `CAND_COUNT`, `parse_mask` | le goulot lui-même |
| `sel_scores`, `sel_f/s/o/c`, `use_conf` | scoreur ponctuel, mesuré suiveur à 96 % |
| `RerankHeads`, `local_context` | égalité stricte mesurée (0.532 = 0.532) |
| `NullHeads.null_in/null_out` (394 k params) | remplacé par un vecteur de 768 |
| `--hard_w`, `--margin` | loss à marge, mesurée à **−0.017** |
| `THRESH_FILL`, `calibrate_threshold.py`, `route_analysis.py` | plus aucun seuil ; aiguillage τ\*=1.0 inutile |
| `norm_common.py`, `train_norm.py`, `encode_spans.py` | lignée bi-encodeur gelé, morte (val 0.86 → 0.66) |
| `--heads {norm,rerank,null}` | une seule classe de tête |
| `_match` et les branches par famille dans l'éval | comparaison = égalité de chaînes canoniques |

---

## 7. DETTES ET PIÈGES À NE PAS REPRODUIRE

1. **Le split de validation n'était pas échangeable avec le test** : 42,2 cibles/doc contre 33,1
   (**+28 %**, DATE +40 %), parce que la validation était « les 100 premiers par `sample_index` »
   — donc les dossiers générés en premier, plus riches. **Corrigé** dans
   `finetune_integrated.py` (tirage aléatoire, seed 0). ⚠️ **Concerne aussi
   `capstone_ecrf/research/lymphome/validation_protocol.py` et le `evaluate.py` publié dans
   `rntc/lymphome-synth-v5-eval`** — décision de republication à prendre, le dataset est déjà
   entre les mains d'un collaborateur.
2. **Bug de métrique** (chaîne `elif`) : une valeur remplie mais fausse n'était comptée que comme
   faux positif, jamais comme faux négatif. Rappel surestimé, absolus gonflés d'environ 0.03.
   **Corrigé.**
3. **Le cap de lecture à 9 000 caractères** sur des dossiers de 22 288 en médiane a coûté
   **0.100 de macro-F1** et a invalidé des semaines de conclusions. Toujours vérifier ce qui entre
   dans le modèle avant d'accuser le modèle.
4. **Toutes les hypothèses de la session portaient sur le scorer** (architecture, loss, features),
   **aucune sur la construction des candidats et de la supervision**. Les deux vrais bugs — le cap
   et les en-têtes — étaient dans les données. C'est le biais à corriger en priorité.
5. `predict_doc` supprimait le seuil dès que les têtes savaient s'abstenir, **y compris pour
   l'appel baseline** — l'ablation aurait affiché un +0.13 fictif. Corrigé avant mesure. Toujours
   vérifier que le baseline n'a pas été saboté par un correctif.

---

## 8. FICHIERS

| chemin | rôle |
|---|---|
| `transducer/train_transducer.py` | tête B, seq2seq caractère, validée étape 1 |
| `transducer/pairs.json` | 81 353 paires (span, valeur), split par document |
| `label_space.py` | espace de labels **dérivé des données** (couverture test 99,2-100 %) — alimente le bloc VOCAB |
| `error_analysis.py` | décomposition sur/sous-remplissage/fausse valeur + contrefactuels |
| `gliner_integrated.py` | têtes actuelles, à refondre à l'étape 2 |
| `JOURNAL.md` | journal complet, §7 et §8 pour cette refonte |

---

## 9. NUIT DU 2026-07-29 — CE QUE LES CONTRÔLES ONT TRANCHÉ

### La tête d'affectation ne sert à rien, et la preuve est propre

Contrôle refait au rang **1** (le précédent, au rang 64, était mesuré là où la détection est
déjà à 0.98-0.99 : un test incapable de produire un résultat positif n'est pas un contrôle).

| classement (moyenne 4 familles) | rang 1 | rang 4 | MRR |
|---|---|---|---|
| score de détection brut | 0.727 | 0.822 | 0.775 |
| **P_A (la tête)** | 0.732 **(+0.005)** | 0.831 (+0.010) | 0.780 (+0.005) |
| **P_A privée de son ancrage `beta·S`** | **0.234 (−0.493)** | 0.417 | 0.338 |

Il y avait de la marge (détection à 0.727, et 0.470 sur DATE) : la tête en prend 0.005. Et
privée de son ancrage elle s'effondre à 0.234 — **elle n'a rien appris en propre, elle recopie
le score de détection.** Ce n'est pas une tête d'affectation, c'est une enveloppe.

### Ce qui marche, et qui n'est pas ça

| tête | ce qu'elle ouvre | gain |
|---|---|---|
| B — transducteur seq2seq | des chaînes absentes du texte | **+0.174** (ablation directe) |
| CAT — options encodées | des classes hors texte (48 % des cibles) | +0.121 puis +0.252 |
| ⊥ dans le même softmax | l'action « ne pas remplir » | +0.071 |
| **A — sélection** | **les M spans, déjà ordonnés par `S`** | **+0.005** |

**Règle qui explique les quatre et qui est falsifiable : une tête gagne quand elle ouvre un
espace de sortie que le score de l'encodeur ne peut pas exprimer ; elle ne gagne rien quand
elle réordonne les mêmes objets, à partir des mêmes représentations.**

### Trois défauts d'entraînement, découverts trop tard pour excuser mais pas pour corriger

1. **La loss était pondérée à 97,5 % sur la détection** (`affect~2.5` contre `det~952`, avec
   `det_w=0.1`). On entraînait l'encodeur à être un détecteur, puis on s'étonnait que la tête
   se comporte en détecteur. Trouvé uniquement en journalisant les deux termes séparément.
2. **`beta` initialisé à 1** : la tête *démarre* sur la solution suiveuse.
3. **`sel = topk(P_A)` est une boucle de rétroaction** : le détecteur choisit quels spans
   reçoivent du gradient, donc se renforce. Les 8 tirages uniformes n'ont pas le débit pour la
   casser (moins d'un passage par span sur tout l'entraînement).

### Le liage par rôle : 19 champs, pas 55 — et c'est le problème DATE

85,9 % des « collisions de valeur » entre champs sont des valeurs **banales** (« non »,
« négatif »). Les vraies sont presque toutes des DATE (`news_date_of_last_news` ↔
`news_date_of_last_visit`, 865×). Donc le liage par rôle et le trou DATE sont **un seul
chantier**, et les conseils « abandonner DATE » et « reconstruire la tête pour les champs à
rôle » se contredisent.

### Le repli « données ×10 » est bloqué

| graines PMC lymphome adulte disponibles | **2 774** |
|---|---|
| documents générés | 2 050, **une graine par document, aucune réutilisation** |
| marge réelle | **×1,35**, pas ×10 |

Aller au-delà demanderait soit de réutiliser les graines en ne variant que noms et dates
(aucune information clinique nouvelle, et fuite train/test si une graine tombe des deux
côtés), soit d'élargir la cohorte hors lymphome — ce qui change la tâche.

### Critère d'arrêt, posé AVANT les résultats
Si la tête reconstruite (attention + ordre + `beta=0` + support guidé par la cible +
rééquilibrage de la loss) ne dépasse pas **0.688** (= 0.673 + l'étendue des quatre bras),
l'architecture est fermée. Le travail restant est alors la **décision de remplir** (une
décision parfaite vaut encore +0.089, dont 0.015 seulement récupérés) et l'écriture.


---

## 10. SYNTHÈSE AU 2026-07-29 — ce qui reste debout

### Le résultat

| système, même barème, même test 410 | macro-F1 |
|---|---|
| v3b nu (GLiNER seul, contexte complet) | **0.487** |
| Qwen3.5-9B **finetuné** sur les mêmes 1 540 documents | 0.582 |
| v3b + têtes (pipeline précédent) | 0.603 |
| + transducteur appris, abstention, seuil déduit de la métrique | 0.673 |
| **+ loss rééquilibrée** | **0.739** |

**+0.25 sur v3b nu, +0.157 sur un LLM 60× plus gros finetuné sur les mêmes données.**

### Ce qui produit ce résultat, par ordre d'importance

1. **Le rééquilibrage de la loss (+0.066).** Elle était à 97,5 % sur la détection : on
   n'entraînait quasiment pas l'objectif visé. Un scalaire.
2. **Le transducteur appris (+0.174 en ablation directe).** Remplace 300 lignes de règles
   écrites à la main et les bat 0.895 contre 0.630 en exact-match.
3. **La décision de remplir**, sortie de la matrice de coût puis corrigée pour la bonne
   métrique : `seuil = F1/2` (Lipton et al.), **zéro degré de liberté ajusté**, à égalité avec
   le meilleur seuil balayé pendant que le balayage par famille surajuste déjà.
4. **L'abstention comme option du même softmax (+0.071).**

### Ce qui ne produit rien, et qu'il faut retirer

| pièce | mesure |
|---|---|
| tête d'affectation comme **sélecteur** | +0.010 au rang 1 ; **0.215 sans son ancrage `beta·S`** |
| compétition entre champs (`alpha`) | reste à 0.000 après entraînement ; la geler **améliore** |
| pool large (M=1024 contre 256) | rien, à budget de troncature fixe |
| hypothèse « `⊥` atomique » | 0.737 contre 0.739 — **réfutée** |

### La règle qui explique les quatre têtes du projet

> **Une tête gagne quand elle ouvre un espace de sortie que le score de l'encodeur ne peut pas
> exprimer. Elle ne gagne rien quand elle réordonne les mêmes objets, à partir des mêmes
> représentations.**

transducteur (chaînes absentes du texte) +0.174 · options encodées (classes hors texte) +0.252 ·
abstention (l'action « ne pas remplir ») +0.071 · **sélection (les mêmes spans, déjà ordonnés
par `S`) +0.010**.

### Le barème du capstone ne mesure pas ce qu'on croit

Son « value-F1 » compare la chaîne prédite au **texte du span gold** (Jaccard de tokens ≥ 0,5).
Une valeur correctement normalisée est comptée **fausse** :

| champ | notre valeur | texte du span gold | Jaccard |
|---|---|---|---|
| `demography_sexe` | `femme` | « patiente » | 0.00 |
| `history_disease_diagnosis` | `LBDGC` | « lymphome B diffus à grandes cellules » | 0.00 |
| `history_age_at_diagnosis` | `68.0` | « patiente âgée de 64 ans » | 0.00 |

Seulement **28 %** de nos champs remplis y passent. Le 0.640 publié est donc un score de
**copie**, pas de valeur — et le plateau qu'il montrait était un plateau de recopiage. Sur
l'axe que ce barème mesure correctement, la localisation, **on est devant** : span-F1 0.527
contre 0.503. (Cas limite qui achève le dossier : sur `history_bcl2_fish`, le texte du span
gold est « 2 » — l'annotateur a pointé le « 2 » de « BCL2 ».)

### Deux corrections à des mesures de ce dépôt

- **Les « champs indexés par un rôle » sont 19, pas 55.** 85,9 % des collisions de valeur entre
  champs portent sur des valeurs banales (« non », « négatif »). Les vraies sont des DATE. Le
  liage par rôle et le trou DATE sont **un seul chantier**.
- **Le repli « données ×10 » est bloqué à ×1,35** : 2 774 graines PMC lymphome adulte
  disponibles, 2 050 documents générés, une graine par document, aucune réutilisation.


---

## 11. LA QUESTION DE LA TÊTE EST CLOSE — par le protocole, pas par abandon

Test écrit d'avance : la tête d'affectation est-elle **mal construite** ou **mal entraînée** ?
Version reconstruite (attention champ→pool, features d'ordre, support proposé depuis la cible,
`beta` **initialisé à 0** donc sans démarrer sur la solution du détecteur), 4 epochs :

| epoch | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| val macro | 0.181 | 0.317 | 0.483 | **0.615** |
| `beta` | 0.009 | 0.024 | 0.039 | **0.047** |

0.615 après quatre epochs, contre **0.776 en une seule** avec l'ancrage. Et `beta` monte
régulièrement : la tête **cherche** à récupérer le score de détection sans y parvenir.

→ **Ni mal construite ni mal entraînée : le signal n'est pas là.** Avec 1 540 documents,
apprendre à pointer de zéro n'est pas possible, et le score natif est irremplaçable.

## 12. LE RÉSULTAT, ÉTAT FINAL

| | val | test |
|---|---|---|
| 1 epoch, `det_w`=0 | 0.776 | 0.771 |
| **3 epochs, `det_w`=0** | 0.798 | **0.784** |

À 3 epochs, le **seuil brut à 0.5 redevient le meilleur** (0.784), devant toutes les règles
calibrées, y compris la règle fermée `F1/2` (0.780). Plus le modèle est bon, moins la
calibration compte : sa confiance se règle d'elle-même. Une pièce de plus qui s'efface.

| repère, même barème, même test 410 | macro |
|---|---|
| v3b nu | 0.487 |
| Qwen3.5-9B **finetuné**, mêmes 1 540 documents | 0.582 |
| pipeline précédent | 0.603 |
| **nous, 3 epochs** | **0.784** |

**+0.297 sur v3b nu · +0.202 sur le LLM 60× plus gros.**

## 13. LES NEUF PIÈCES RETIRÉES

| pièce | verdict | qui l'avait défendue |
|---|---|---|
| `taxonomy.py` (300 lignes) | 0.895 contre 0.630 | — |
| **loss de détection auxiliaire** | **nuisible** (0.670 → 0.771) | **moi, explicitement** |
| tête d'affectation (sélecteur) | −0.000 au rang 1 ; 0.615 sans ancrage | le design |
| MLP de la route COPIE | ≤ 0.004 | le design |
| compétition entre champs `alpha` | 0.0000, quatre fois | le design |
| pool large (1024 vs 256) | rien | moi |
| critère par rang à grand M | converge avec `max` | moi |
| hypothèse « ⊥ atomique » | 0.762 vs 0.767 | **moi** |
| décision de remplir apprise | +0.001 sur un seuil | **moi** |

## 14. CE QUI RESTE OUVERT

1. **La confiance ne sépare pas assez le juste du faux.** Décision parfaite = **0.907**, atteint
   0.771. Ni un seuil ni une régression sur neuf indices n'attrapent les +0.133.
2. **L'ancre de section.** `source_document` (96,4 % des entrées) contient l'en-tête verbatim,
   identique à un `=== … ===` du texte dans **99,96 %** des cas. La cible DATE est dans son span
   **6,4 %** du temps, dans l'en-tête de son document source **47,0 %**. Expérience en trois bras
   en cours, dont un où l'ancre est **calculée depuis la position du span** — le seul régime
   disponible à l'inférence.
3. **Validité externe.** Gold produit par un seul annotateur LLM sur des documents synthétiques
   du même pipeline. À écrire noir sur blanc si rien n'est fait.
