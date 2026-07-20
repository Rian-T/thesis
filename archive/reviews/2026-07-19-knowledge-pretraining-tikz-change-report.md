# Rapport de correction des TikZ de préentraînement enrichi par les connaissances

Date : 19 juillet 2026

## Périmètre

Les quatre figures de la section `Knowledge-Enhanced Pretraining` ont été corrigées directement
dans `sources/related_works/corpus_annotation.tex`, avec uniquement les ajustements de prose
nécessaires pour que chaque figure corresponde au mécanisme qu'elle prétend illustrer.

Ce travail n'a modifié ni `thesis.bib` ni `tools/bibcheck_whitelist.txt`. Ces deux fichiers avaient
déjà des changements locaux indépendants de cette intervention. Le PDF racine existant n'a pas été
écrasé : la compilation et l'inspection ont été effectuées sur un PDF propre dans
`/private/tmp/thesis-build-clean/thesis.pdf`.

## Résumé des corrections

| Figure | Problème évité | Représentation retenue |
|---|---|---|
| `fig:corpus-static` | Chaîne mélangeant hiérarchie, traitement et marche comme s'il s'agissait d'un unique graphe ontologique natif | Graphe inter-ontologies explicitement illustratif, arêtes dirigées, association clinique en pointillés et chemin échantillonné valide |
| `fig:corpus-inject` | Schéma générique attribué simultanément à K-BERT et DRAGON | Schéma limité au mécanisme d'entrée de K-BERT : branche de connaissances, positions souples et matrice de visibilité |
| `fig:corpus-contrastive` | Diabète de type 1 qualifié de terme « unrelated » et géométrie difficile à lire | Projection 2D schématique de l'objectif SapBERT, avec voisinage compact de synonymes et négatif distinct mais médicalement proche ; CODER reste décrit dans la prose |
| `fig:corpus-g2t` | EntiGraph présenté comme recevant directement un fragment d'ontologie | Document source, extraction d'entités, groupe échantillonné, analyse relationnelle conditionnée par le document, puis texte synthétique |

## 1. Embeddings statiques de graphes

### TikZ

- Les arêtes sont maintenant dirigées.
- Les identifiants ont été rendus explicites : `ICD-10 E10--E14`, `ICD-10 E11`,
  `ATC A10BA02` et `ATC A10BA`.
- Les relations hiérarchiques représentées sont :
  `Type 2 diabetes mellitus -> Diabetes mellitus` et `Metformin -> Biguanides`.
- La relation `Metformin -> Type 2 diabetes mellitus` est nommée `treats`, tracée en pointillés et
  légendée comme association clinique illustrative. Elle n'est donc pas présentée comme une
  arête hiérarchique native commune à ICD-10 et ATC.
- L'ancienne marche descendante a été remplacée par le chemin dirigé
  `Metformin -> Type 2 diabetes mellitus -> Diabetes mellitus`.
- Le bloc d'apprentissage est nommé `word2vec-style objective`, formulation qui couvre le
  niveau commun à Node2Vec et RDF2Vec sans les confondre.

### Prose et légende

La prose distingue désormais les marches aléatoires biaisées de Node2Vec des parcours de graphes
RDF dirigés de RDF2Vec. Elle précise aussi que RDF2Vec peut conserver les prédicats de relation dans
les séquences. La légende ne prétend plus que les deux méthodes suivent exactement le même pipeline.

## 2. Injection de connaissances dans les Transformers

### TikZ

- La phrase originale reste visible sous forme de tokens.
- Une branche `metformin -> treats -> Type 2 diabetes mellitus` est attachée à la mention
  d'entité.
- Une couche intermédiaire explicite la séquence aplatie, les positions souples et la matrice de
  visibilité avant le Transformer.
- Les tokens de la phrase et la branche ajoutée alimentent visiblement cette couche intermédiaire.

### Prose et légende

La figure est maintenant explicitement limitée à K-BERT. La légende ne cite que K-BERT. DRAGON est
décrit séparément dans la prose comme encodant le texte et un sous-graphe pertinent comme modalités
distinctes, avec fusion bidirectionnelle, MLM et prédiction de liens. La prose indique expressément
que DRAGON n'emploie pas la disposition montrée.

## 3. Approches contrastives médicales

### TikZ

- Les flèches de rapprochement et d'éloignement ont été remplacées par un unique plan d'embedding
  2D schématique, plus directement lisible.
- Le plan est encadré discrètement, sans axes, graduations, coordonnées, distances numériques ou
  trajectoires d'entraînement.
- `T2DM`, `NIDDM` et `diabète de type 2` occupent un voisinage vert compact, explicitement associé
  au même concept UMLS.
- `Type 1 diabetes mellitus` est spatialement séparé et présenté comme
  `different but related concept / negative pair`, et non comme terme sans relation médicale.
- Les mentions `illustrative 2D embedding projection` et `not to scale` empêchent de lire les
  placements comme le résultat quantitatif d'une expérience particulière.

### Prose et légende

La légende illustre uniquement SapBERT et ne cite que `liu2021sapbert`. Elle qualifie explicitement
la projection de schématique et les distances de non quantitatives. CODER reste dans la prose, où
son apport est décrit plus précisément comme une supervision contrastive issue de triplets
terme--relation--terme. La prose précise que l'objectif relationnel de CODER n'est pas dessiné.

## 4. Données synthétiques pour le préentraînement

### Titre et prose

Le titre de sous-section reste volontairement large : `Synthetic Data for Pretraining`. La prose
présente d'abord la direction générale des données synthétiques, puis décrit EntiGraph à son juste
niveau : petit corpus source, extraction d'entités saillantes, échantillonnage de groupes d'entités,
génération d'analyses relationnelles avec accès au document source, et entraînement continu de
modèles décodeurs.

### TikZ

L'entrée ontologique incorrecte a été remplacée par le flux suivant :

```text
document source -> extraction d'entités -> groupe échantillonné -> analyse relationnelle -> texte synthétique
       |                                                        ^
       +--------------------------------------------------------+
```

Le second chemin matérialise le conditionnement direct de l'analyse sur le document source. Le
rapport d'échelle `1.3M real tokens -> 455M synthetic tokens` est conservé.

La mise en page suit une grille régulière analogue à un `flex/grid` :

- quatre colonnes équidistantes (`0`, `4.2`, `8.4`, `12.6`) ;
- quatre en-têtes sur une même ligne ;
- document, groupe d'entités, analyse et texte sur une même ligne de flux ;
- marges horizontales constantes entre les blocs ;
- flèche de conditionnement placée dans un couloir séparé sous la grille ;
- mêmes couleurs, coins arrondis, épaisseurs, fontes et styles de flèches que les figures voisines.

Le groupe de deux entités est volontairement représenté par un seul bloc. Cette simplification
évite des croisements de flèches sans suggérer un ordre entre les entités échantillonnées.

## Simplifications délibérées

- Le graphe statique reste un exemple pédagogique inter-ontologies ; il ne prétend pas reproduire
  une distribution RDF officielle complète.
- La relation clinique `treats` est explicitement illustrative et visuellement distincte des
  relations `is-a`.
- La figure K-BERT ne représente pas tous les détails d'indexation des positions souples ; elle
  montre seulement les composants indispensables au mécanisme.
- La figure SapBERT montre un négatif médicalement proche pour éviter l'affirmation contestable
  qu'il serait « unrelated ». La projection 2D n'est ni une visualisation de données observées ni
  une revendication sur les distances exactes apprises par le modèle.
- La phrase produite dans la figure EntiGraph est illustrative. La revendication quantitative
  conservée porte seulement sur le passage d'environ 1,3 million à 455 millions de tokens dans
  l'expérience principale.

## Vérifications effectuées

### Compilation

Une compilation LuaLaTeX complète a réussi avec le code final :

```text
TEXMFVAR=/private/tmp/thesis-texmf-var \
TEXMFCACHE=/private/tmp/thesis-texmf-var \
XDG_CACHE_HOME=/private/tmp/thesis-xdg-cache \
lualatex -interaction=nonstopmode -halt-on-error -recorder \
  -output-directory=/private/tmp/thesis-build-clean --shell-escape thesis.tex
```

Résultat : code de sortie `0`, PDF de `261` pages. Le journal ne contient ni
`Undefined control sequence`, ni `Package pgf Error`, ni `Package tikz Error`, ni erreur LaTeX
bloquante.

Le premier `make build` avait échoué avant d'atteindre les figures à cause de deux problèmes
d'environnement indépendants du changement : cache `luaotfload` non inscriptible, puis ancien
`build/thesis.aux` corrompu sur `r@part:intro`. La compilation propre en répertoire temporaire a
permis de vérifier le document sans supprimer ni écraser les artefacts locaux existants.

### Inspection visuelle

Les pages PDF physiques suivantes ont été rendues à 180 dpi et inspectées :

- page 79 (page imprimée 65) : embeddings statiques ;
- page 80 (page imprimée 66) : K-BERT ;
- page 81 (page imprimée 67) : projection 2D SapBERT ;
- page 82 (page imprimée 68) : EntiGraph, déplacé proprement sur la page suivante par le flottant.

Les rendus se trouvent dans `tmp/pdfs/knowledge-pretraining-tikz-review/`. Les contrôles finaux sont
`page-sapbert-2d-081.png` pour SapBERT et `page-sapbert-2d-neighbour-082.png` pour EntiGraph. Aucun
texte n'est coupé ; les titres, blocs et flèches ne se chevauchent pas.

### Contrôles source et bibliographie

- `git diff --check -- sources/related_works/corpus_annotation.tex` : succès, aucune erreur de
  whitespace.
- Les sept clés centrales sont présentes dans `thesis.bib` : `grover2016node2vec`,
  `ristoski2016rdf2vec`, `liu2020kbert`, `yasunaga2022dragon`, `liu2021sapbert`, `yuan2022coder`
  et `yang2025entigraph`.
- `make checkbib`, relancé avec un cache `uv` temporaire et l'accès réseau requis, a contrôlé 305
  entrées : 266 vérifiées, 38 ignorées selon la configuration, aucune des références touchées par
  ces figures signalée. Il conserve un écart indépendant sur `manning_ir_2008` et signale la chaîne
  LaTeX `authoryear` comme clé citée absente ; ces deux points préexistaient et ne relèvent pas des
  TikZ corrigés.

## Sources primaires utilisées pour le contrôle factuel

- [Node2Vec](https://arxiv.org/abs/1607.00653)
- [RDF2Vec](http://www.semantic-web-journal.net/system/files/swj1379.pdf)
- [K-BERT](https://arxiv.org/abs/1909.07606)
- [DRAGON](https://arxiv.org/abs/2210.09338)
- [SapBERT](https://aclanthology.org/2021.naacl-main.334/)
- [CODER](https://arxiv.org/abs/2011.02947)
- [EntiGraph](https://arxiv.org/abs/2409.07431)
