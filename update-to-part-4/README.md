# De la partie 4 de la thèse à `mc-bio-gliner-lymphome-ecrf-v2`

Enquête menée le 2026-10-12 sur Jean Zay (`$WORK/french-medgliner`, dépôt git créé le
2026-07-22) et sur le Hub. Rien dans la thèse n'a été modifié. Ce dossier rassemble ce qui
s'est passé entre l'état figé de la partie « Adapting to Clinical Tasks » (chapitres
`part_3/chapter9` → `chapter8` → `chapter7`) et le modèle publié le 2026-08-13.

Les faits viennent des commits, des documents de travail du cluster et des fichiers du Hub.
Quand un fait n'a pas pu être vérifié, ou qu'une trace a disparu, c'est écrit. Les chiffres
marqués « recalculé » ont été refaits ici depuis le jeu publié (`scripts/verify_stats.py`).

---

## 1. En une page

**Point de départ (ce qui est dans la thèse).** Le chapitre `chap:evaluation` évalue
MC-bio-gliner sur l'eCRF lymphome de 89 champs. Le modèle publié est
`rntc/mc-bio-gliner-lymphome` (lignée `V5FROMV3B`). Il rend, pour chaque champ, **le texte
d'un span** du dossier. Le score de la thèse est un value-F1 : la chaîne prédite est comparée
au texte du span de référence, avec un Jaccard de tokens ≥ 0,5. Résultat : 0.640, à 0.018 de
Qwen3.5-4B (0.658), 27× plus petit. La variante `-joint` atteint 0.657.

**Le problème qui a lancé la suite.** Un span n'est pas une valeur d'eCRF. « 1,62 m » n'est
pas `162`, « patiente » n'est pas `femme`, « phénotype non germinal » n'est pas `NGC`,
« le 10 avril 2017 » n'est pas `2017-04-10`. Pour une étude clinique (cohortes, statistiques,
survie), il faut la valeur canonique (`NORM_HEADS_DESIGN.md` §1). Recalculé sur le test :
**34,6 % des valeurs cibles n'apparaissent nulle part telles quelles dans le dossier**, et
seulement 4,9 % des dates cibles sont écrites dans leur span annoté.

**Ce qui a été construit.** Le même encodeur GLiNER de 150 M, inchangé, auquel on ajoute
une sortie de valeur. Pour chaque champ, un seul softmax met en concurrence trois sortes
d'options : copier un span du texte, choisir une valeur déjà vue à l'entraînement, ou
s'abstenir. Si un span gagne, un petit transducteur caractère (2 M paramètres, partagé par
tous les champs) réécrit son texte en valeur canonique. On ne supervise que la valeur
finale : le span est une variable cachée, et il n'y a plus de perte de détection.

**Le résultat.** Macro-F1 par famille (CAT, DATE, NUM, ORD) sur les 410 dossiers de test,
égalité de chaîne canonique :

| système | macro |
|---|---|
| même encodeur, sans les têtes | 0.487 |
| Qwen3.5-9B finetuné sur les mêmes 1 540 dossiers (voir §6, point 1) | 0.582 |
| `…-ecrf` (v1, 30 juillet, fenêtre 24 000 car.) | 0.786 |
| **`…-ecrf-v2` (13 août, fenêtre 45 000 car.)** | **0.809** |
| `…-ecrf-large` (395 M) | 0.815 |

**Pourquoi une v1 et une v2.** La v2 a la même architecture et les mêmes données. Seule la
fenêtre de lecture change : 39 % des dossiers dépassaient 24 000 caractères (recalculé :
38,5 % du test). Lire le dossier entier vaut +0.023 ; multiplier l'encodeur par 2,6 ne vaut
que +0.006. La v2 est donc le meilleur rapport qualité/coût, et elle est aussi 2,2× plus
rapide que la v1 grâce à un décodage groupé.

**Ce que ce travail change pour la partie 4.** La métrique de la thèse ne sait pas noter une
valeur normalisée : `femme` contre « patiente » donne un Jaccard de 0. Les deux nombres
(0.640 et 0.809) ne sont donc **pas comparables**. Le §7 détaille les passages concernés.

---

## 1bis. Est-ce que c'est intéressant ? (verdict, 2026-10-13)

Oui, mais pas pour la raison que met en avant le README du Hub. Le score affiché là-bas
(0.809 contre 0.582) n'est pas la partie intéressante, et ce README compte peu : c'est une
vitrine d'usage, pas une source. Ce qui compte est ce que les expériences ont montré.

**Ce qui est intéressant.**

1. **Superviser la valeur plutôt que le span améliore la localisation elle-même.** Supprimer la
   perte de détection fait monter le rappel@1 de la détection de 0.727 à 0.820 (DATE : 0.470 à
   0.635). La cause est générale : l'annotateur n'a jamais pointé les en-têtes de section, où
   vivent plus de la moitié des dates cibles. Une supervision par les spans apprend donc au
   modèle les habitudes de l'annotateur. Ce constat dépasse le lymphome. Il s'applique à tout
   jeu où le span annoté n'est pas la vraie preuve de la valeur. Le projet propose un test qui
   le détecte avant tout entraînement : la part des cibles écrites dans leur span annoté
   (4,9 % sur DATE, recalculé).
2. **Une règle propre et vérifiable sur les têtes.** Une tête aide quand elle ouvre un espace
   de sortie que l'encodeur ne peut pas produire (réécrire une valeur, choisir une classe hors
   du texte, s'abstenir). Elle n'aide pas quand elle réordonne les mêmes spans. Quatre mesures
   la soutiennent, plus un test écrit avant l'expérience.
3. **La métrique de la thèse mesure la copie.** Le value-F1 par Jaccard donne 0 à `femme`
   contre « patiente ». C'est utile à savoir pour la soutenance, où la question peut venir.
4. **Le contexte compte plus que la taille** : lire tout le dossier vaut +0.023, multiplier
   l'encodeur par 2,6 vaut +0.006. C'est cohérent avec l'argument de déploiement sur du
   matériel modeste.

**Ce qui ne tient pas encore.**

1. Le chiffre phare repose sur une comparaison injuste : le Qwen-9B a été entraîné à recopier
   des spans, puis noté sur des valeurs (§6, point 1).
2. Le test est presque fermé (97 % des valeurs CAT déjà vues à l'entraînement). L'ouverture du
   schéma n'est pas démontrée, et l'essai qui retire 20 champs de l'entraînement n'a pas été
   fait.
3. Tout repose sur un seul jeu synthétique, avec une référence produite par un LLM et du bruit
   visible.

**Pour la thèse.** Il est trop tard pour l'intégrer, et ce n'est pas nécessaire : la partie 4
reste juste sur ce qu'elle mesure. Au plus, le point 1 tient en une phrase dans les
perspectives, ou sert de réponse prête si un rapporteur demande pourquoi l'extracteur ne sort
pas de valeurs normalisées.

**Pour un papier.** Il y a un vrai résultat, mais il est centré sur le point 1, pas sur le
score. Il manque trois expériences : un Qwen finetuné sur les valeurs canoniques, le retrait de
20 champs de l'entraînement, et si possible un second jeu de même forme (CORD, SROIE).

---

## 2. Les trois générations de modèles (nommage)

Le Hub contient cinq dépôts lymphome. Les deux premiers sont ceux de la thèse ; les trois
suivants sont le travail décrit ici. Table brute : `data/variants_published.csv`.

| dépôt | date | sortie | score test |
|---|---|---|---|
| `rntc/mc-bio-gliner-lymphome` | 22 juil. | spans | value-F1 0.640 |
| `rntc/mc-bio-gliner-lymphome-joint` | 22 juil. | spans | value-F1 0.657 |
| `rntc/mc-bio-gliner-lymphome-ecrf` (« v1 ») | 30 juil. | valeurs canoniques | macro 0.786 |
| `rntc/mc-bio-gliner-lymphome-ecrf-v2` | 13 août | valeurs canoniques | macro 0.809 |
| `rntc/mc-bio-gliner-lymphome-ecrf-large` | 13 août | valeurs canoniques | macro 0.815 |

La « v1 » au sens du Hub est donc `-ecrf`, pas le modèle de la thèse. L'encodeur des trois
modèles `-ecrf` en 150 M est initialisé depuis `V5FROMV3B`, c'est-à-dire le checkpoint de la
thèse. Le large part de `rntc/gliner2-fr-biomed-v3e-large` (ModernCamemBERT-bio-large, objectif
MLM, entraîné en juin).

Le jeu d'évaluation est le même corpus que la thèse (2 050 dossiers, référence TAPDL), publié
avec ses splits sous `rntc/lymphome-synth-v5-eval` (train 1 540 / validation 100 / test 410).
Les parquets ne sont pas copiés ici (Git LFS refuse les nouveaux objets sur ce fork) ; on les
récupère avec `hf download rntc/lymphome-synth-v5-eval --repo-type dataset`. Le dossier
`sources/hub/lymphome-synth-v5-eval/extracts/` contient les premiers dossiers de chaque split en
JSON (texte, référence span-localisée, annotation avec valeurs, timeline) et un index CSV des
2 050 dossiers (split, identifiant, longueur).

---

## 3. Chronologie

Les dates viennent des commits (`sources/docs/git_log_full.md`, 64 commits, messages
complets). Les messages de commit sont très détaillés et constituent le meilleur journal.

### 22–23 juillet : têtes de normalisation, premier essai

Le dépôt est figé (« checkpoint avant projet normalization-heads ») le jour où la thèse fige
ses chiffres. La spec `NORM_HEADS_DESIGN.md` pose l'idée : greffer de petites têtes typées sur
les spans de GLiNER pour sortir la valeur normalisée en un seul passage.

Première version **découplée** : spans prédits par GLiNER, ré-encodés par MedEmbed-v9 gelé,
puis têtes. Elle annonce 0.746 contre 0.620 pour Qwen, mais ce n'est pas un vrai
« GLiNER + têtes ». Le pivot vers une version **intégrée** (têtes branchées sur les
représentations natives de GLiNER, entraînement bout en bout) révèle deux fuites : la
validation ne contenait que les champs présents (≈ 17 au lieu de 89), ce qui gonflait le score
à 0.84 au lieu de 0.50 ; et les premières annonces « on bat Qwen » mesuraient le rappel seul.

Bilan au 23 juillet (`JOURNAL.md`) : la tête catégorielle marche (+0.12 F1) parce que sa sortie
diffère du texte. La tête de sélection pour NUM, DATE et ORD suit la détection à 96 % et
n'apporte rien. Le modèle ne bat pas Qwen-9B : 0.50 contre 0.62.

### 28 juillet : trois bugs, et un nouveau design

- **Le dossier était tronqué à 9 000 caractères** (`MAX_CHARS = 9000`) alors que la médiane
  est de 22 288. Recalculé : 100 % des dossiers dépassent 9 000 caractères. 60,5 % des spans de
  référence étaient jetés. Lire le dossier entier vaut +0.100. Le « suiveur à 96 % » était un
  artefact de cette troncature.
- **La validation n'était pas échangeable avec le test** : « les 100 premiers par
  identifiant », générés en premier et plus denses (+28 % de cibles). Toute calibration de
  seuil échouait. Correction : tirage aléatoire (seed 0). Le jeu publié a été republié avec ce
  split ; le test est inchangé.
- **Les règles de normalisation écrites à la main (`taxonomy.py`, 300 lignes) inversaient les
  négations** (« absence de réarrangement » → `réarrangement`, « Mme » → `homme`). Elles
  pénalisaient surtout Qwen. Elles sont remplacées par `label_space.py`, qui lit l'espace de
  valeurs dans les données d'entraînement.

Avec une option « s'abstenir » apprise, le modèle passe à 0.603, devant Qwen-9B (0.582).

Le même jour, `DESIGN_V2.md` réécrit le design. Les échecs précédents ont une cause commune :
l'étape « top-12 candidats par champ », non différentiable, construite à partir du score que la
tête devait corriger. Le nouveau design garde la matrice champs × spans entière et supervise par
la valeur. Le fait qui le motive : **55,7 % des dates cibles sont une date d'en-tête de
section, et aucun des 6 275 spans de référence DATE ne tombe sur un en-tête** (recalculé :
54,4 % des dates cibles égalent une date d'en-tête). L'annotateur n'a jamais pointé l'endroit
où vit la moitié des dates.

Étape 1 validée le même soir : le transducteur appris bat `taxonomy.py` sur les quatre
familles (exact-match 0.8975 contre 0.630).

Le harnais d'évaluation autonome (`evaluate.py`, `predict.py`) est publié avec le jeu, décrit
dans le commit comme « livrable Eric ».

### Nuit du 28 au 29 juillet : la tête disparaît, l'encodeur apprend

Les commits de cette nuit forment une série d'expériences contrôlées. Les résultats,
dans l'ordre (test, 410 dossiers) :

1. **Seuil de remplissage déduit de la métrique** : pour un F1, le seuil optimal vaut environ
   F1/2 (Lipton et al. 2014), pas 0.5. 0.603 → 0.673 sans réentraîner.
2. **Contrôle décisif négatif** : la tête d'affectation ne classe pas mieux que le score de
   détection brut.
3. **La perte valait 97,5 % de détection** (`det~952` contre `affect~2.5`), découvert en
   journalisant les deux termes séparément. Poids de détection 0.1 → 0.002 : 0.739. Poids 0 :
   0.771. La perte de détection n'était pas trop forte, elle était nuisible : elle apprenait
   au modèle à pointer là où l'annotateur avait pointé, donc jamais sur un en-tête.
4. **Supprimer la perte de détection rend la détection meilleure** (rappel@1 0.727 → 0.820,
   DATE 0.470 → 0.635). La supervision par la valeur reforme l'encodeur. La tête d'affectation,
   privée de son ancrage sur le score de l'encodeur, tombe à 0.19 : elle ne faisait que le
   recopier. Elle est retirée.
5. **Test pré-enregistré** : une tête reconstruite et partie de zéro plafonne à 0.615 après
   4 epochs. Avec 1 540 dossiers, apprendre à pointer sans le score natif n'est pas possible.
6. **Décision de remplir apprise** (15 paramètres) : +0.001 sur un simple seuil. Retirée.
7. **3 epochs** : 0.784, puis 0.786 après correction d'un bug d'évaluation (voir plus bas).

Le projet en tire une règle (`ARCHITECTURE.md` §5) : *une tête gagne quand elle ouvre un
espace de sortie que le score de l'encodeur ne peut pas exprimer* (transducteur +0.174,
classes hors texte +0.252, abstention +0.071) ; *elle ne gagne rien quand elle réordonne les
mêmes spans* (+0.005).

Deux autres résultats de cette nuit :

- **Ancre de section** : donner au transducteur l'en-tête de la section du span fait monter
  DATE de 0.759 à 0.835. Mais l'en-tête est trouvé par une regex sur le motif `=== … ===`
  produit par notre générateur. La version générique (les 60 ou 150 caractères précédents)
  ne donne rien. Décision du 12 août : abandonnée comme artefact du corpus.
- **Bug d'évaluation** : l'évaluation utilisait la fonction de collation d'entraînement, qui
  remplace 29 % des libellés de champ par « entity 15 » et supprime des descriptions. Effet
  réel : +0.002 seulement, parce que le modèle avait été entraîné sous la même corruption.

### 30 juillet – 4 août : publication de la v1

`ARCHITECTURE.md` (sources/docs) est écrit comme document autonome : architecture, chiffres,
onze pièces retirées, cinq bugs, ce qui reste ouvert. C'est le meilleur document technique
du dossier.

`rntc/mc-bio-gliner-lymphome-ecrf` est publié. `modeling_assign.py` ne dépend que de `torch`,
`transformers` et du paquet PyPI `gliner2`. Deux bugs de portabilité ont été attrapés avant
envoi (tokenizer absent, chemin absolu du cluster dans `config.json`).

Le 4 août, `extract()` rend en plus le span source, ses offsets et deux confiances (« demande
d'Eric » dans le commit). Le README est réécrit en ton factuel, et la phrase « la sortie est
une valeur canonique et non un span » est corrigée : pour certains champs la valeur coïncide
avec le span (« veuve » → `veuve`).

### 12–13 août : la v2 et le large

Plan dans `WORKPLAN_2026-08-12.md`, avec un journal.

- **Budget de tokens** : le schéma des 89 champs occupe 2 280 tokens de la séquence. À 24 000
  caractères, le texte remplit déjà les 8 192 positions de ModernBERT. Monter la fenêtre
  revient à parier sur l'extrapolation RoPE. Le balayage sur la validation (24k 0.793, 32k
  0.806, 45k 0.807) tranche : 45 000. Confirmé sur le test : 0.795 sans réentraîner.
- **Têtes ré-entraînées à 45 000** : 0.809. C'est la v2.
- **Lignée large** (395 M) : 0.815. La décomposition honnête du gain total depuis la v1
  (+0.029) : contexte à l'inférence +0.009, contexte à l'entraînement +0.014, taille +0.006.
- **Inférence** : décodage groupé des 81 champs avec compaction des lignes actives, 1.02 →
  0.41 s/doc sur H100 (0.29 s en bf16), sorties identiques sur 810/810 champs.
- **Audits avec les outils `fodoca`** (MIT, Éric de la Clergerie, copiés dans
  `sources/code/gen/lymphome/fodoca_preprocess/vendor/`) : 2,04 % des paires de dates de la
  référence violent une contrainte temporelle ; 13,6 % des dates cibles sont calculées
  (« J1C1 + 6 × 21 j ») et donc impossibles à obtenir par copie.
- **Diagnostic de saturation** : le seuil 0.5 est devenu optimal. Il reste +0.055 derrière une
  décision de remplissage parfaite, mais aucune règle de seuil ne les récupère : la confiance
  ne sépare pas assez le juste du faux. DATE garde 8 à 10 % de cibles hors de portée.
- **Levier DATE** (3 971 cibles) : 73,7 % dans le span, 14,9 % ailleurs dans le document,
  6,7 % à un décalage régulier, 4,7 % non dérivables (`data/date_lever.csv`).

Les deux variantes sont publiées le 13 août. Le code publié figeait la dimension à 768 : le
large ne se chargeait chez personne. Le contrôle de chargement isolé l'a attrapé avant envoi.

### Septembre : prototypes après la v2 (sans résultat publié)

- **Bras contrastif large** : un GLiNER large sur MedEmbed-large (contrastif) a été entraîné,
  puis finetuné sur le lymphome (`gliner2-lym-V5LARGE-MEDEMBED`, checkpoints datés des 18–19
  septembre). Les têtes de valeur et l'évaluation test n'ont **aucune trace**. L'A/B
  contrastif contre MLM à 395 M n'est donc pas tranché.
- **Prototype « V3 », décision conditionnée par le schéma** (`v3_schema_decision/`,
  21 septembre) : garde l'encodeur v2 et la fenêtre de 45 000, encode chaque option
  champ/valeur et la score par deux couches d'attention croisée, sur les seuls champs CAT et
  ORD (45 champs). Trois objectifs comparés (entropie croisée ; + Brier et RPS ; un objectif de
  décision « inspiré de RLCD », que le README dit explicitement ne pas reproduire). Meilleur
  run en **validation** : 0.871 (CAT 0.847, ORD 0.896), ECE 0.029. Aucun test lancé. Ces
  chiffres ne sont **pas comparables** à la v2 (autre sous-ensemble de champs, autre métrique,
  validation contre test). Table : `data/v3_prototype_validation.csv`.
- **`gen/laya_biomed/`** (22 septembre) : génération de données de « décisions » biomédicales
  (questions à choix, booléennes, ordinales) depuis du texte, avec Qwen. Hors lymphome. Je ne
  sais pas si la génération a tourné ni à quoi elle a servi.

---

## 4. L'architecture finale

Schéma : `sources/docs/resultats.pdf` (page 1). Détail complet : `sources/docs/ARCHITECTURE.md`.

```
schéma (89 champs) + dossier  →  encodeur GLiNER2 150 M (inchangé)
                              →  S = score champ × span (déjà calculé par GLiNER)
pour chaque champ, un softmax sur :
    copie      : les spans, score = S, 0 paramètre
    vocabulaire: les valeurs vues à l'entraînement, encodées comme chaînes « sexe : femme »
    ⊥          : s'abstenir
si une copie gagne → transducteur caractère (2 M, partagé) : texte du span → valeur
perte unique : − log Σ_spans P(span | champ) · P(valeur | span, champ)
```

Trois choix de conception expliquent la plupart du résultat :

1. **Aucun paramètre par champ ni par classe.** Tout ce qui est propre au schéma est une
   chaîne de caractères qui passe par l'encodeur. Les options de vocabulaire sont comparées par
   produit scalaire, pas par une couche de sortie à une unité par classe.
2. **L'espace de valeurs est lu dans les données.** Un champ reçoit un vocabulaire si ses
   valeurs observées couvrent 90 % de sa masse. Résultat sans règle écrite : 34/35 champs CAT
   reçoivent un vocabulaire, 0/18 champs DATE (`ARCHITECTURE.md` §6).
3. **On supervise la valeur, pas le span.** C'est ce qui permet au modèle d'aller chercher une
   date dans un en-tête que personne n'a annoté (52,8 % des spans DATE gagnants ne recouvrent
   aucun span de référence).

Exemple concret (premier dossier du test, `lym_8`, 17 717 caractères) :
`data/example_test_doc0_text.txt` pour le texte, `data/example_test_doc0_targets.csv` pour
les cibles. Quelques lignes :

| champ | span annoté | valeur cible |
|---|---|---|
| sexe | « patiente Sandrine Mathieu » | `femme` |
| taille au diagnostic | « taille : 1,62 m » | `162` |
| diagnostic du lymphome | « lymphome B diffus à grandes cellules » | `LBDGC` |
| test COO | « phénotype non germinal » | `NGC` |
| FISH MYC | « Aucun réarrangement des gènes MYC, BCL2 ou BCL6 n'est détecté. » | `Pas de réarrangement` |
| stade Ann Arbor | « Stade IIIB (Ann Arbor) » | `3` |
| date de fin (1re ligne) | « … par R-CHOP × 8 entre avril et octobre 2017 » | `2017-10` |

---

## 5. Les leçons de méthode que le projet a écrites

Elles sont dans `ARCHITECTURE.md` §8 et §12, et elles ont coûté plus que les choix
d'architecture. Aucun des cinq gros bugs n'était dans le modèle :

| bug | coût |
|---|---|
| dossier tronqué à 9 000 caractères | 0.100 |
| perte pondérée à 97,5 % sur la détection | 0.098 |
| value-F1 de la thèse qui mesure la copie et non la valeur | invalidait la comparaison |
| regex d'en-tête sur-échappée (`\\s`) : trois bras identiques au bit près | une expérience à vide |
| collation d'entraînement appliquée au prompt d'évaluation | 0.002, et éval non reproductible |

Onze pièces ont été retirées, chacune par une mesure (`data/ablations.csv`). Cinq étaient des
propositions de l'agent lui-même, dont la perte de détection qu'il avait défendue par écrit.

---

## 6. Ce qui reste fragile (à lire avant de citer quoi que ce soit)

1. **Le baseline Qwen3.5-9B (0.582) n'a pas été entraîné à produire des valeurs.** Son jeu
   d'entraînement (`build_llm_sft.py`) a pour cibles « les textes des spans gold VERBATIM » ;
   le docstring dit que la valeur normalisée « n'est PAS dans le texte, on n'apprend pas à la
   produire ». Sa sortie est ensuite projetée sur l'espace canonique. Le « +0.204 sur un LLM
   60× plus gros » compare donc un modèle entraîné pour la valeur à un modèle entraîné pour la
   copie. Il manque un Qwen finetuné sur les valeurs canoniques. Par ailleurs, dans la thèse,
   le meilleur générateur est Qwen3.5-4B, pas le 9B.
2. **Référence silver et monde quasi clos.** La référence vient d'un seul annotateur LLM, sur
   des documents du même pipeline. 97,4 % des cibles CAT et 99,2 % des ORD du test sont déjà
   dans le vocabulaire d'entraînement (90 valeurs hors vocabulaire sur 11 117). Le test dit
   presque rien sur des valeurs nouvelles. DATE est la famille la plus faible parce que c'est la
   seule sans monde clos. L'échantillon `data/transducer_pairs_sample.csv` montre aussi du bruit
   dans la référence : « BCL2, BCL6 et MYC n'ont pas été réalisés » → IHC MYC `Négatif` au lieu
   d'un examen non réalisé ; « pas de mention de décès » → `vivant`.
3. **L'ouverture du schéma n'est pas testée.** Le contrôle le plus direct (retirer 20 champs
   de l'entraînement et les évaluer) est listé comme « le plus rentable » dans
   `ARCHITECTURE.md` §11 et n'a pas été fait.
4. **Aucune validation hors corpus.** Les pistes notées (CORD, SROIE, FUNSD) n'ont pas été
   lancées.
5. **Le span-F1 0.527 contre 0.503** (localisation meilleure que le modèle de la thèse) vient
   d'un seul run, antérieur à la correction du prompt d'évaluation. À refaire avant citation.
6. **Petits verdicts non re-tarifés** : les écarts ≤ 0.005 du §7 d'`ARCHITECTURE.md` ont été
   mesurés sous le bug de collation et sans bootstrap.
7. **Exemple du README du Hub** : « le 8 avril 2017 » → `2017-04-15`. Dans le dossier `lym_8`,
   « le 8 avril 2017 » est la date de biopsie, la date de diagnostic cible est `2017-04-10`, et
   `2017-04-15` est la date de la RCP et du début de traitement. L'exemple illustre peut-être
   une erreur de rôle plutôt qu'une normalisation. Point mineur : le README du Hub est une
   vitrine, pas une source à citer (voir §1bis).
8. **Traces perdues.** Une purge de `$SCRATCH` a vidé les logs d'août et les poids des têtes
   (`gliner2-lym-assign-*` ne contiennent plus que `encoder_config/`). Les modèles publiés
   n'existent plus que sur le Hub. Le résultat du job `pool_date_reach` (le pool atteint-il les
   dates quand on l'élargit ?) n'a pas été retrouvé.
9. **Qui a décidé quoi.** Plusieurs commits citent « le responsable » (critère « +0.2–0.3 pour
   justifier des têtes », réserve sur la regex d'en-tête, nommage de `source`). Je ne sais pas
   s'il s'agit de toi ou d'Éric. Seules deux demandes sont explicitement attribuées à Eric : le
   harnais d'évaluation et le retour des offsets.

---

## 7. Ce que ça touche dans la partie 4 (repérage, rien n'est modifié)

- `sources/part_3/chapter7/article.tex` l. 33–35 : définition du value-F1 (Jaccard ≥ 0,5).
  Ce travail montre que cette métrique note la copie : seuls 28 % des champs remplis par le
  modèle à valeurs y passent (`ARCHITECTURE.md` §8).
- `chapter7` l. 98–107, table `tab:p3-capstone` (l. 139–154) et l. 265 : le 0.640 et la
  quasi-parité avec Qwen3.5-4B restent vrais pour la tâche « localiser la preuve ». La tâche
  « remplir avec une valeur canonique » est une autre tâche, avec un autre barème.
- Abstract et résumé (`sources/abstract.tex` l. 12 et 29) : « within two F-score points of a
  fine-tuned generative language model twenty-seven times its size ». Cette phrase porte sur
  le barème de la thèse. Une phrase du type « 0.809 contre 0.582 » n'est défendable qu'après le
  point 1 du §6.
- Les deux constats du chapitre sur les erreurs (MC-bio-gliner met plus souvent la bonne
  chaîne dans le mauvais champ ; Qwen classe mieux ses prédictions par confiance) rejoignent ce
  que le diagnostic d'août retrouve : le résidu est un problème de séparation de confiance et
  de liage de rôle sur les dates.
- Correction à une mesure antérieure qui touche le texte de la thèse s'il la cite : les champs
  « indexés par un rôle » sont 19 et non 55 (85,9 % des collisions portaient sur des valeurs
  banales comme « non ») ; ce sont presque tous des DATE.

---

## 8. Contenu du dossier

```
README.md                          ce document
data/
  verified_stats.json              chiffres recalculés ici (longueurs, valeur dans le span, dates d'en-tête)
  example_test_doc0_text.txt       un dossier de test complet (lym_8)
  example_test_doc0_targets.csv    ses cibles : champ, famille, valeur canonique, spans annotés, CR source
  results_timeline.csv             la trajectoire 0.487 → 0.815, avec la source de chaque ligne
  variants_published.csv           les cinq dépôts Hub et leurs scores
  ablations.csv                    ce qui apporte, ce qui a été retiré, et la mesure
  date_lever.csv                   où se trouvent les dates cibles
  transducer_pairs_sample.csv      60 paires (span, valeur) d'entraînement du transducteur
  v3_prototype_validation.csv      prototype de septembre (validation seulement)
scripts/verify_stats.py            recalcul depuis le jeu publié (à télécharger d'abord, voir §2)
sources/
  docs/                            documents du cluster, copiés tels quels
    git_log_full.md                les 64 commits avec leurs messages complets (le vrai journal)
    ARCHITECTURE.md                état final au 30 juillet, autonome (à lire en premier)
    DESIGN_V2.md                   le raisonnement du nouveau design, avec ses révisions
    JOURNAL.md                     22–28 juillet : première approche et ses échecs
    NORM_HEADS_DESIGN.md           la spec de départ (22 juillet), motivation
    RESULTS_INTEGRATED.md          résultats du 22 juillet (métrique trop clémente, cf. JOURNAL)
    WORKPLAN_2026-08-12.md         campagne v2/large, avec journal
    resultats.tex / .pdf           fiche d'une page (schéma + tables), compilée ici
    CLAUDE.md                      état du projet au 11 juin (périmé pour le lymphome)
    HANDOFF.md, RESULTS.md         état du capstone au 22 juillet (= chiffres de la thèse)
  json/                            sorties brutes des diagnostics de fin juillet (pool, calibration, contrôles)
    v3_schema_decision/            métriques de validation du prototype de septembre
  code/                            le code de production et d'évaluation (assign.py, label_space.py,
                                   transducteur, audits fodoca, harnais publié, prototype V3)
  hub/                             cartes et code des cinq modèles (sans les poids) + le jeu
                                   extraits JSON/CSV de lymphome-synth-v5-eval (sans les parquets)
```

`data/transducer_pairs_sample.csv` montre 60 paires (span, valeur) tirées au hasard. Le fichier complet,
`sources/code/gen/lymphome/norm/transducer/pairs.json` (81 353 paires, 25 Mo), contient toutes
les paires d'entraînement du transducteur. Avec l'exemple de dossier, c'est l'extrait de données
d'entraînement le plus parlant.
