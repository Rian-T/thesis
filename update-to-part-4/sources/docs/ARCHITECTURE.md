# Extraction eCRF lymphome — architecture finale et journal des mesures

> État au **2026-07-30**. Ce document est autosuffisant : il contient l'architecture, tous les
> chiffres, les ablations, les bugs trouvés, et ce qui reste ouvert. `DESIGN_V2.md` garde
> l'historique du raisonnement ; celui-ci garde les faits.

---

## 1. La tâche

Remplir un **eCRF de 89 champs typés** depuis un dossier patient longitudinal français
synthétique (~22 000 caractères, plusieurs comptes-rendus successifs séparés par des en-têtes
de section). Pour chaque couple (document, champ) : produire **une** valeur canonique, ou
constater que le champ n'est pas documenté.

| | |
|---|---|
| familles de champs | CAT (catégoriel) · DATE · NUM · ORD (ordinal) · TXT (exclu → 81 champs) |
| documents | 1 540 entraînement · 100 validation · 410 test |
| gold | *silver-as-gold* : annotateur LLM, span-localisé |
| métrique | macro-F1 par famille au niveau (document, champ) |
| coût d'erreur | **valeur fausse = 2** (fp + fn) · **abstention à tort = 1** |

La politique de remplissage est donc un objet de premier ordre, pas un post-traitement.

### Contrainte de conception imposée

> Un GLiNER normal, plus des têtes entraînées avec tout le reste, qui font la dernière partie
> du travail. Élégant, transférable à n'importe quel dataset, *bitter-lesson-pilled* (aucune
> architecture écrite à la main), différentiable. **Pas de patchwork de cas particuliers.**

Invariant qui en découle : **zéro paramètre par champ et par classe**. Tout ce qui est
spécifique au schéma est une **chaîne de caractères** qui traverse un encodeur.

---

## 2. Le résultat

Même barème, même test de 410 documents, égalité de chaîne canonique (tolérance 10 % sur NUM).

| système | macro | CAT | DATE | NUM | ORD |
|---|---|---|---|---|---|
| **v3b nu** (GLiNER seul, contexte complet) | **0.487** | 0.430 | 0.307 | 0.537 | 0.673 |
| Qwen3.5-9B **finetuné** sur les mêmes 1 540 documents | 0.582 | 0.488 | 0.447 | 0.590 | 0.791 |
| pipeline précédent (têtes de rescoring + 300 lignes de règles) | 0.603 | 0.682 | 0.380 | 0.596 | 0.755 |
| + transducteur, abstention, seuil déduit | 0.673 | 0.711 | 0.497 | 0.652 | 0.781 |
| + loss de détection rééquilibrée (`det_w`=0.002) | 0.739 | 0.781 | 0.610 | 0.730 | 0.834 |
| + loss de détection **supprimée** (`det_w`=0), 1 epoch | 0.771 | 0.807 | 0.660 | 0.758 | 0.858 |
| **3 epochs** | **0.786** | 0.817 | 0.684 | 0.765 | 0.877 |

**+0.299 sur v3b nu · +0.204 sur un LLM 60× plus gros finetuné sur les mêmes données.**

---

## 3. L'architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│  ENTRÉE : le SCHÉMA et le TEXTE dans UNE SEULE séquence                  │
│  "[P] entities [DESCRIPTION] date de diagnostic : ... ‖ === Compte-rendu  │
│   de RCP — 2017-04-15 === Patiente de 62 ans, LBDGC stade IIIB..."       │
└────────────────────────────────┬─────────────────────────────────────────┘
                                 ▼
                 ┌───────────────────────────────────┐
                 │   ENCODEUR  GLiNER2  v3b  150 M   │  ← INCHANGÉ
                 │   (ModernBERT biomédical FR)      │    gliner2/* intact
                 └───────────────┬───────────────────┘
                    ┌────────────┴────────────┐
                    ▼                         ▼
            span_rep [M, 768]          schema_emb [F, 768]
                    └────────────┬────────────┘
                                 ▼
                   ╔═════════════════════════════╗
                   ║   S = span_rep ⊗ schema     ║  ← DÉJÀ calculé par
                   ║   matrice [F champs × M]    ║    GLiNER, rien de neuf
                   ╚═════════════┬═══════════════╝
        ┌────────────────────────┴────────────────────────┐
        │   POUR CHAQUE CHAMP : UN SEUL SOFTMAX SUR       │
        │   TROIS SORTES D'OPTIONS EN CONCURRENCE         │
        └─┬──────────────────┬──────────────────────┬─────┘
  ┌───────▼───────┐  ┌───────▼────────┐   ┌─────────▼────────┐
  │    COPIE      │  │     VOCAB      │   │        ⊥         │
  │  score = S    │  │ "sexe : femme" │   │  MLP([E ; z])    │
  │  0 paramètre  │  │       ↓        │   │  1536→256→1      │
  │               │  │   ENCODEUR     │   │  → 1 scalaire    │
  │   M options   │  │       ↓        │   │   1 option       │
  │               │  │  vec 768  ·  q │   │                  │
  │               │  │  q = MLP([E;z])│   │                  │
  │               │  │  1536→256→768  │   │                  │
  │               │  │  n_f options   │   │                  │
  └───────┬───────┘  └───────┬────────┘   └─────────┬────────┘
          └──────────────────┴──────────────────────┘
                             ▼
              softmax( concat( S , oe·q , ⊥ ) )
                             │
        ┌────────────────────┴─────────────┬──────────────┐
        ▼                                  ▼              ▼
┌───────────────────────┐            "femme"        champ laissé
│  TRANSDUCTEUR         │            "non"             vide
│  2 M · PARTAGÉ 89     │            "GC"
│  texte du span  ──────┤ caractères → GRU bidirectionnel
│  libellé du champ ────┤ caractères → GRU bidirectionnel
│  span_rep ────────────┤ 768 → état initial (sr_to_h)
│   décodeur + attention│  ← mécanisme de copie
└───────────┬───────────┘
            ▼
    "2017-04-15"   "64"   "3"
```

### La loss, unique

```
L = − log Σ  P(span | champ) · P_B(valeur | span, champ)
            spans
```

Le span est **latent** : on ne supervise que la valeur finale. **Aucune loss de détection.**

Décision de remplir : `p > 0.5`, déduit de la matrice de coût (`coût(remplir) = 2 − q₀ − 2p_v`
contre `coût(s'abstenir) = 1 − q₀`, indépendamment de `q₀`). **Aucun paramètre libre.**

### Les quatre voies ne prennent pas le même type d'entrée

| voie | entrée | paramètres |
|---|---|---|
| **COPIE** | embeddings (`span_rep ⊗ schema`) | **0** |
| **VOCAB** | chaînes encodées `·` requête MLP — **bi-encodeur, pas un classifieur** | 0 par classe |
| **⊥** | embeddings `[marqueur champ ; résumé doc sum-poolé]` | un MLP → 1 scalaire |
| **transducteur** | **texte brut du span** (caractères) + libellé (caractères) + `span_rep` | 2 M, partagés |

Le bloc VOCAB est un **produit scalaire** entre une chaîne encodée et une requête, non une
classification à une sortie par classe. C'est ce qui donne zéro paramètre par classe et permet
de traiter une classe jamais vue.

---

## 4. Ce qui produit le résultat

| composant | apport | protocole |
|---|---|---|
| **supprimer la loss de détection** | **+0.098** | balayage `det_w`, courbe monotone |
| **transducteur appris** vs 300 lignes de règles | **+0.174** | ablation directe (0.496 → 0.670 en val) |
| **options encodées** (tête CAT) | **+0.121 puis +0.252** | ablations antérieures |
| **abstention** dans le même softmax | **+0.071** | ablation antérieure |
| seuil déduit de la métrique | +0.015 → 0 | utile à 1 epoch, nul à 3 |

### Le transducteur seul, contre les règles écrites à la main

Exact-match sur 15 927 paires de test, mêmes paires pour les deux.

| | `taxonomy.py` (300 lignes) | **transducteur** | Δ |
|---|---|---|---|
| CAT | 0.501 | **0.931** | +0.430 |
| DATE | 0.663 | **0.759** | +0.096 |
| NUM | 0.714 | **0.901** | +0.187 |
| ORD | 0.902 | **0.984** | +0.082 |
| **total** | **0.630** | **0.8975** | **+0.268** |

Le transducteur est **handicapé** (il ne voit que le span, sans contexte) et **jugé plus
durement** (chaîne exacte, alors que `taxonomy` travaille dans son propre canon).

Variante d'implémentation retenue : le libellé du champ conditionne l'**état initial du
décodeur** au lieu d'être concaténé à l'entrée caractère. Mesuré à budget identique :
0.869 → **0.895**. Cela permet d'encoder les M spans **une fois par document** au lieu d'une
fois par champ, ce qui rend la loss marginale calculable.

### Le balayage qui a tout débloqué

| `det_w` | 0.1 (origine) | 0.02 | 0.002 | **0.0** |
|---|---|---|---|---|
| val macro | 0.670 | 0.673 | 0.749 | **0.776** |

Diviser par 5 ne fait rien (+0.003) ; diviser par 50 fait **+0.079**. Ce n'est pas un réglage
fin, c'est un **régime** : au-dessus d'un seuil, la loss de détection capture entièrement
l'encodeur. À `det_w`=0.1 la loss valait **97,5 % de détection contre 2,5 % d'affectation**
(`det~952`, `affect~2.5`) — découvert uniquement en journalisant les deux termes séparément.

**Pourquoi elle est nuisible et pas seulement inutile** : elle entraîne à pointer *là où
l'annotateur a pointé*. Or **0 span gold DATE sur 6 275 ne tombe sur un en-tête de section**,
alors que **55,7 % des cibles DATE valent une date d'en-tête**. On apprenait activement au
modèle à ignorer la moitié d'une famille.

**Généralisation du diagnostic, transportable** : une supervision auxiliaire sur la
localisation n'aide que si les spans annotés sont réellement l'évidence des valeurs. Mesurable
en un scalaire par famille sans réentraîner — le **taux valeur-dans-span** : 6,4 % sur DATE.

---

## 5. Le mécanisme, tel qu'il est réellement démontré

### Supprimer la loss de détection rend la détection MEILLEURE

Contrôle au **rang 1** (le précédent, au rang 64, était saturé : la détection y est déjà à
0.98-0.99, donc le test ne pouvait pas produire de résultat positif).

| rappel@1 | `det_w`=0.1 | 0.002 | **0.0** |
|---|---|---|---|
| détection brute | 0.727 | 0.789 | **0.820** |
| détection, DATE seul | 0.470 | 0.586 | **0.635** |
| P_A (la tête) | +0.005 | +0.010 | **−0.000** |
| P_A privée de son ancrage `beta·S` | 0.234 | 0.215 | **0.187** |

Deux faits, et leur combinaison est le résultat :

1. **La tête d'affectation n'apporte rien** — `−0.000` au rang 1, et 0.187 sans son ancrage.
   Elle recopie `S`, c'est un tuyau.
2. **La détection s'améliore de +0.093** (et +0.165 sur DATE) alors qu'on l'entraîne 50× moins.

**Explication** : la loss d'affectation entraîne aussi l'encodeur, `S` étant dans le graphe.
Avec `det_w`=0.1 la loss de détection dominait et tirait `span_rep` vers « pointer là où
l'annotateur a pointé ». En la supprimant, c'est la supervision **par la valeur** qui façonne
l'encodeur.

> **Superviser la valeur plutôt que le span apprend bien au modèle où chercher — mais il le
> fait en reformant l'ENCODEUR, pas via une tête séparée.**

### Le test de falsification pré-enregistré passe

`DESIGN_V2` §5 mesure n°2 : *« le rappel du pool DATE doit passer de 0.52 vers ~0.9, c'est la
mesure la plus importante »*. À M=256 et top-64 constants :

| | rappel du pool DATE |
|---|---|
| ancien pipeline (top-12 par champ) | 0.61 |
| avec loss de détection | 0.752 |
| sans loss de détection, 1 epoch | 0.832 |
| **sans loss de détection, 3 epochs** | **0.863** |

Le 0.832 **dépasse déjà le plafond mesuré à froid** (0.821, sur un pool 4× plus grand) :
l'encodeur rend **atteignables** des valeurs qui ne l'étaient pas. Ce n'est plus du
réordonnancement, c'est de la découverte.

**Et 52,8 % des spans DATE gagnants ne chevauchent aucun span gold.** Le modèle va chercher les
dates là où l'annotateur n'a jamais pointé.

### La tête ne PEUT PAS apprendre à pointer

Test écrit d'avance : mal construite, ou mal entraînée ? Version reconstruite (attention
champ→pool, features d'ordre, support guidé par la cible, `beta` **initialisé à 0** donc sans
démarrer sur la solution du détecteur), 4 epochs :

| epoch | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| val macro | 0.181 | 0.317 | 0.483 | **0.615** |
| `beta` | 0.009 | 0.024 | 0.039 | **0.047** |

0.615 après quatre epochs contre **0.776 en une seule** avec l'ancrage. Et `beta` monte
régulièrement : la tête **cherche** à récupérer le score de détection sans y parvenir.
→ **Ni mal construite ni mal entraînée : le signal n'est pas là.** Avec 1 540 documents,
apprendre à pointer de zéro n'est pas possible ; le score natif est irremplaçable.

### La règle qui explique les quatre têtes du projet

> **Une tête gagne quand elle ouvre un espace de sortie que le score de l'encodeur ne peut pas
> exprimer. Elle ne gagne rien quand elle réordonne les mêmes objets, à partir des mêmes
> représentations.**

| tête | espace ouvert | gain |
|---|---|---|
| transducteur | chaînes absentes du texte | **+0.174** |
| options encodées | classes hors texte (48 % des cibles) | **+0.252** |
| abstention | l'action « ne pas remplir » | **+0.071** |
| **sélection** | **les mêmes spans, déjà ordonnés par `S`** | **+0.005** |

C'est falsifiable : toute tête future qui se contente de réordonner des spans échouera, sauf si
on lui donne une information que le détecteur n'a pas.

---

## 6. Le routage classification / transducteur est DÉRIVÉ, pas écrit

Un champ reçoit un bloc VOCAB **si et seulement si** `label_space.derive` le juge fermé — ses
valeurs observées dans le train couvrent 90 % de sa masse. Aucune liste, aucun pydantic.

Vérification contre le schéma écrit à la main :

| type **dérivé des données** | CAT | DATE | NUM | ORD |
|---|---|---|---|---|
| **CLOSED** (reçoit un vocabulaire) | **34** | 0 | 10 | 8 |
| **DATE** (copie seulement) | 0 | **18** | 0 | 0 |
| NUMBER | 0 | 0 | 5 | 0 |
| TEXT | 1 | 0 | 1 | 0 |
| UNKNOWN (trop peu observé, refus de trancher) | 0 | 0 | 2 | 2 |

- **Aucun champ DATE ne reçoit de vocabulaire, 18 sur 18.** La règle refuse d'elle-même de
  mémoriser des dates. Personne ne l'a écrit.
- **34/35 CAT en reçoivent un.** Le seul écart, `second_line_treatment` → TEXT, est défendable :
  les protocoles de 2ᵉ ligne sont trop variés pour un ensemble fermé (581 observations).
- Les deux `UNKNOWN` sur ORD sont un **refus de trancher** (n=15 et n=27, sous le seuil de 30),
  pas une erreur.

52 champs sur 81 reçoivent un vocabulaire. Pydantic n'intervient pas ; `taxonomy.FIELD_SPEC`
ne sert qu'à écarter les 8 champs TXT et à grouper les familles **dans le barème**.

---

## 7. Les onze pièces retirées, chacune par une mesure

| pièce | verdict | qui la défendait |
|---|---|---|
| `taxonomy.py` (300 lignes de règles) | 0.8975 contre 0.630 | — |
| **loss de détection auxiliaire** | **NUISIBLE** (0.670 → 0.776) | **moi, par écrit, contre le design** |
| tête d'affectation comme sélecteur | −0.000 au rang 1 ; 0.615 sans ancrage sur 4 epochs | le design |
| MLP de la route COPIE (`ctx=sonly`) | val 0.777 vs 0.776 ; test 0.767 vs 0.771 → ≤ 0.004 | le design |
| compétition entre champs (`alpha`) | 0.0000 après entraînement, **quatre fois** | le design |
| pool large (1024 contre 256) | rien, à budget de troncature fixe | moi |
| critère d'élagage par rang à grand M | converge avec le critère naïf | moi |
| hypothèse « `⊥` atomique » | 0.767 contre 0.771 | **moi** |
| décision de remplir apprise (15 param., 9 indices) | +0.001 sur un simple seuil | **moi** |
| support guidé par la cible (hard-EM) | 0.774 contre 0.776 | la relecture |
| **somme marginale** (argmax suffit) | 0.771 contre 0.776 à 1 epoch | le design |

**Cinq des onze étaient les miennes.** La plus coûteuse — la loss auxiliaire — je l'avais
défendue dans la docstring du code, contre la proposition initiale, en invoquant un risque de
dérive que la mesure a démenti.

### Précision sur la somme marginale

Ce qui est réfuté est la **somme** sur les spans, pas la latence du span. Dans les deux bras on
ne dit jamais au modèle quel span choisir et n'importe quel span peut gagner — y compris un
span d'en-tête jamais annoté. L'affectation dure est du **hard-EM**, la version Viterbi de la
même inférence à variable latente. La marginale est donc **la forme élégante** du mécanisme,
pas sa **condition de fonctionnement**.

⚠️ Mesuré à **1 epoch** (0.771 contre 0.776). La confirmation à 3 epochs était encore en file
au moment d'écrire.

---

## 8. Les cinq bugs — aucun n'était dans le modèle

| bug | coût | comment il a été trouvé |
|---|---|---|
| **cap de lecture à 9 000 caractères** sur des dossiers de 22 288 en médiane | **0.100** | en regardant ce qui entre dans le modèle |
| **loss pondérée à 97,5 % sur la détection** | **0.098** | en journalisant les deux termes séparément |
| **`value-F1` du capstone mesure la COPIE, pas la valeur** | invalidait la comparaison | en confrontant nos valeurs au texte des spans gold |
| **regex d'en-tête sur-échappée** (`\\s` au lieu de `\s`) | une expérience entière à vide | parce que deux bras rendaient des chiffres **bit-à-bit identiques** |
| **échantillonneur d'entraînement appliqué au prompt d'ÉVALUATION** | 0.002 (mais éval non reproductible) | signalé par une relecture critique |

Chaque diagnostic est venu d'avoir **séparé deux quantités qu'on additionnait sans regarder** :
les deux termes de la loss, le classement de la tête et son ancrage, la valeur canonique et le
texte du span.

### Détail du bug d'évaluation

`doc_forward` appelait `collate_fn_train` à l'évaluation. Cette fonction applique
l'échantillonneur de GLiNER2 **au prompt**. Mesuré, 100 tirages du même document :

| | libellés remplacés par « entity 15 » | descriptions supprimées | prompts distincts /100 |
|---|---|---|---|
| `collate_fn_train` | **29-30 %** | **23-42 %** | **59** |
| `collate_fn_inference` | 0 % | 0 % | 1 |

Le libellé est la seule chose qui porte le schéma : on l'effaçait sur près d'un tiers des
documents au moment de mesurer. `random` (stdlib) n'était pas semé non plus, donc l'évaluation
n'était pas reproductible.

**Effet réel : +0.002 seulement** (0.784 → 0.786), parce que le modèle était **entraîné sous la
même corruption** et avait donc appris à lire les descriptions plutôt qu'à mémoriser les
libellés. Ce que je prenais pour un sabotage de la mesure était en partie une régularisation.
Les grands verdicts (`det_w`, transducteur, options, `taxonomy`) sont un ordre de grandeur
au-dessus ; les petits (≤ 0.005) restent à re-tarifer.

### Détail du barème du capstone

Son `value-F1` compare la chaîne prédite au **texte du span gold** (Jaccard de tokens ≥ 0,5).
Une valeur correctement normalisée est comptée **fausse** :

| champ | notre valeur | texte du span gold | Jaccard |
|---|---|---|---|
| `demography_sexe` | `femme` | « patiente » | 0.00 |
| `history_disease_diagnosis` | `LBDGC` | « lymphome B diffus à grandes cellules » | 0.00 |
| `history_age_at_diagnosis` | `68.0` | « patiente âgée de 64 ans » | 0.00 |
| `demography_living_environment` | `urbain` | « vit seule dans un appartement à Nancy » | 0.00 |
| `history_coo_test` | `NGC` | « phénotype non germinal » | 0.00 |

**28 %** seulement de nos champs remplis y passent. Le 0.640 publié pour `V5FROMV3B` est donc
un score de **copie**, et le plateau qu'il montrait était un plateau de recopiage. Sur l'axe que
ce barème mesure correctement — la localisation — **on est devant** : span-F1 **0.527** contre
0.503. (Cas limite qui achève le dossier : sur `history_bcl2_fish`, le texte du span gold est
« 2 » — l'annotateur a pointé le « 2 » de « BCL2 ».)

⚠️ Ce 0.503 → 0.527 vient d'un unique run, antérieur à la correction du prompt d'évaluation.
À refaire avant citation.

---

## 9. Corrections à des mesures de ce dépôt

| affirmation antérieure | correction |
|---|---|
| « 37 % de la masse des cibles est indexée par un rôle », 55 champs sur 81 | **19 champs sur 81.** 85,9 % des collisions de valeur portent sur des valeurs banales (« non », « négatif »). Les vraies sont presque toutes des DATE. **Le liage par rôle et le trou DATE sont un seul chantier.** |
| « cible DATE récupérable depuis n'importe quel span : 89,5 % » | **Ne se reconstitue pas.** Au mieux 0.865 avec 17 % de tous les spans du document. À ne plus citer. |
| « données ×10 » comme levier | **Bloqué à ×1,35** : 2 774 graines PMC lymphome adulte disponibles, 2 050 documents générés, **une graine par document, aucune réutilisation**. Aller plus loin demande soit de réutiliser les graines (aucune information clinique nouvelle, fuite train/test possible), soit d'élargir hors lymphome — ce qui change la tâche. |
| têtes A et B « ~1.2 M / ~1.7 M » | **2.17 M / 2.00 M** mesurés. |
| « le pool contient rarement la réponse, il faut l'élargir » | **Faux.** Le goulot était la sélection, puis l'entraînement. Le pool à 16 384 spans (17 % du document) ne rapporte rien de plus que 256. |

---

## 10. L'ancre de section — un gain réel qui échoue au test de transférabilité

`source_document` existe sur **96,4 %** des entrées d'annotation et contient l'en-tête verbatim
(`« Compte-rendu de RCP — 2015-11-01 »`), identique à un `=== … ===` du texte dans **99,96 %**
des cas. La cible DATE est dans son span **6,4 %** du temps, mais dans l'en-tête de son document
source **47,0 %**.

Cinq bras, transducteur seul, exact-match test :

| entrée du transducteur | total | **DATE** |
|---|---|---|
| span seul (référence) | 0.8975 | 0.759 |
| **60 caractères précédents** (générique) | 0.8941 | **0.760** |
| **150 caractères précédents** (générique) | 0.8902 | **0.765** |
| **en-tête calculé depuis la position du span** (regex) | 0.9092 | **0.835** |
| en-tête de l'annotateur (borne haute) | 0.9145 | 0.852 |

**Verdict.** L'ancre calculée capte **82 %** du gain de l'ancre parfaite (+0.076 sur +0.093),
donc **le gain est exploitable à l'inférence** — le contrôle de non-fuite passe. Le motif prédit
avant la mesure est vérifié : **DATE monte, les trois autres familles baissent** (−0.002 à
−0.009), donc l'ancre transporte la date, pas du contexte général.

**Mais la version générique ne donne rien** (+0.001 à +0.006). Tout le gain vient du motif
`=== … ===` produit par **notre** générateur. La raison est mécanique : une section fait
plusieurs milliers de caractères, donc l'en-tête n'est presque jamais dans les 150 caractères
qui précèdent le span.

**Deux options honnêtes**, et c'est un arbitrage, pas une mesure :

1. **Renoncer au gain** et publier le négatif — « l'information de section est disponible mais
   nous ne savons pas l'extraire sans connaître le format du corpus ».
2. **Le garder en l'assumant** comme une étape de **segmentation en sections**, composant
   explicite et remplaçable, instancié ici par une regex parce que ce corpus a des marqueurs
   explicites — en écrivant qu'on n'a **pas** testé si un segmenteur générique récupère le gain.

Non intégré au modèle à ce jour : le gain est mesuré sur le transducteur seul.

---

## 11. Ce qui reste ouvert

### La confiance ne sépare pas assez le juste du faux

| | |
|---|---|
| décision de remplir **parfaite** (borne, sur le modèle à 0.771) | **0.907** |
| atteint | 0.771 |

**+0.133** dorment là. Ni un seuil scalaire, ni un seuil par famille, ni une régression
logistique sur neuf indices de confiance (masse, marge, entropie, nombre de spans concordants,
masse de ⊥, confiance du transducteur, route, score de détection, type dérivé) ne les
attrapent : la règle apprise fait **+0.001** sur un simple seuil. Le problème n'est pas la règle
de décision, c'est que **la confiance elle-même ne classe pas correctement le juste avant le
faux**.

Poids appris, pour mémoire : `p1` +0.695 · marge +0.677 · détection +0.630 · `p_null` −0.618 ·
`log P_B` +0.214 · entropie −0.204. Tous pèsent, mais ils sont trop corrélés pour ajouter à
`p1` seul.

### Cinq pièces qui restent, jamais ablatées

| pièce | statut |
|---|---|
| `sr_to_h` (`span_rep` → décodeur du transducteur) | norme passée de 0 à **1.07**, donc utilisée — gain inconnu |
| `tau` (température sur `log P_B`) | valeur apprise 0.968 — jamais ablatée |
| `beta` (poids de `S`) | 1.0016 — pourrait être fixé à 1 |
| critère d'élagage par rang | mesuré sur le pool à froid, jamais bout en bout |
| troncature de la somme (32+8 contre 8+4) | 8+4 suffisait ; pas de balayage propre |

### Validité externe — la limitation à écrire noir sur blanc

- Gold produit par **un seul annotateur LLM** sur des documents synthétiques du **même**
  pipeline. Aucune mesure d'auto-accord de l'annotateur.
- **97,4 % des cibles CAT et 99,2 % des ORD sont déjà dans le vocabulaire dérivé du train.**
  Sur 11 117 valeurs CLOSED de test, **90 seulement** sont hors vocabulaire : le test ne contient
  presque aucune information sur la généralisation à des valeurs nouvelles. Le +0.252 des options
  encodées est donc en partie le gain d'avoir accès à un monde quasi clos.
- Médiane de **2 classes** pour les 34 champs CAT fermés, 6 pour ORD, 11 pour NUM.
- Corrélation à énoncer explicitement : **DATE est la famille la plus faible (0.684) parce que
  c'est la seule sans monde clos** (0 % de couverture par le vocabulaire).

### Contrôles internes possibles sans nouvelle annotation

1. **Split par CHAMP** (« leave-fields-out ») — retirer 20 champs de l'entraînement, vocabulaire
   compris, et évaluer dessus. C'est le seul test direct de la revendication « les mêmes poids
   valent pour un schéma inconnu ». **Le plus rentable de la liste.**
2. **Perturbation des libellés** à l'évaluation (paraphrase, traduction, identifiant opaque) —
   mesure la dépendance à la forme exacte apprise plutôt qu'au sens.
3. **Sous-ensemble dur déclaré** : score restreint aux cibles hors vocabulaire du train.
4. **Bootstrap au niveau document** sur tout ce qui est rapporté — la moitié du §7 deviendrait
   « indistinguable, donc on prend la plus simple », meilleure justification que « +0.001 ».
5. **Un corpus public de même forme** : CORD, SROIE (reçus, ~30 champs, copie + normalisation),
   FUNSD. Autre langue et autre domaine, ce qui rend la démonstration plus forte.

---

## 12. Fichiers

### Chemin de production

| fichier | rôle |
|---|---|
| `assign.py` | pool de spans, `AssignHead`, `ValueModel`, la loss, l'inférence |
| `train_assign.py` | entraînement bout en bout, sondes anti-effondrement |
| `label_space.py` | espace de valeurs **dérivé des données** — aucun vocabulaire écrit |
| `transducer/train_transducer2.py` | tête B, seq2seq caractère, conditionnement au décodeur |
| `transducer/build_pairs.py` | paires (span, valeur), split par document, options d'ancre |

### Évaluation et contrôles

| fichier | ce qu'il mesure |
|---|---|
| `eval_assign.py` | les 3 mesures de `DESIGN_V2` §5 + contrôle d'ancrage + scalaires appris |
| `control_rank.py` | le contrôle décisif au rang 1/4/MRR, avec ablation de l'ancrage |
| `diagnose_assign.py` | décomposition des erreurs en causes exclusives + contrefactuels |
| `calibrate_fill.py` | quatre règles de remplissage, choisies sur la validation |
| `learn_fill.py` | décision de remplir apprise (réfutée, +0.001) |
| `pool_diagnostic.py` | rappel du pool à froid, plusieurs M et critères |
| `baseline_nohead.py` | GLiNER nu, contexte complet, métrique actuelle |
| `predict_capstone.py` | prédictions au format du barème publié |

### Environnements

| usage | interpréteur |
|---|---|
| entraînement, éval | `/lustre/fsn1/.../envs/bge/bin/python3` |
| annotation vLLM | `/lustre/fsn1/.../envs/reformulation/bin/python` |

### Écueils à ne pas reproduire

1. **`doc_forward(..., train=False)` à l'évaluation, sans exception.** `collate_fn_train` corrompt
   le prompt (29 % de libellés effacés).
2. **`max_chars=24000`**, jamais 9 000. Les dossiers font 22 288 caractères en médiane.
3. **Ne pas remettre `@torch.no_grad` sur `build_pool`** : `H` et `S` doivent rester dans le
   graphe, sinon l'encodeur ne reçoit aucun gradient.
4. **Le split de validation doit être aléatoire** (seed 0), jamais « les 100 premiers » — ceux-là
   sont 16 % plus denses et rendent toute calibration non transférable.
5. **Une expérience qui ne teste rien doit PLANTER**, pas rendre un chiffre. Cf. la regex
   sur-échappée : trois bras identiques au dixième près, 12 epochs, courbes propres.
6. **Journaliser les termes d'une loss composite SÉPARÉMENT.** Le plus gros gain de la session
   était invisible dans la somme.
