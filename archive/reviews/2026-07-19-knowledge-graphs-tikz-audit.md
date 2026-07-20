# Audit scientifique des figures TikZ sur l’intégration des graphes de connaissances

**Date :** 19 juillet 2026  
**Périmètre :** `sources/related_works/corpus_annotation.tex`, lignes 333–566  
**Figures auditées :** `fig:corpus-static`, `fig:corpus-inject`, `fig:corpus-contrastive`, `fig:corpus-g2t`  
**Nature du contrôle :** vérification du code TikZ, du rendu PDF de la thèse, des articles primaires cités et des nomenclatures médicales officielles.

## Verdict exécutif

Les quatre figures compilent et transmettent une progression pédagogique claire, mais elles ne sont pas toutes scientifiquement fidèles aux travaux qu’elles citent.

| Figure | Verdict | Problème principal |
|---|---|---|
| Embeddings statiques | **À corriger** | Pipeline acceptable pour Node2Vec, mais trop général pour RDF2Vec ; relations médicales ambiguës ou inversées ; code `E08–E13` incompatible avec la CIM-10 OMS/ATIH. |
| Injection de connaissances | **Refonte nécessaire** | Le dessin ressemble partiellement à K-BERT mais ne représente pas DRAGON ; il fusionne plusieurs architectures incompatibles en un unique mécanisme « triple au token ». |
| Approches contrastives | **À compléter** | Bonne représentation de SapBERT, mais la composante relationnelle qui définit CODER est absente ; « Type 1 diabetes » n’est pas un terme sans relation avec le type 2. |
| Graph-to-text | **Scientifiquement incorrect pour EntiGraph** | EntiGraph part de documents, extrait leurs entités et génère du texte relationnel conditionné par ces documents ; il ne verbalise pas directement une ontologie existante. |

Le point le plus important découvert lors du second contrôle concerne le texte qui suit les figures : l’affirmation selon laquelle le graph-to-text pour le préentraînement « has not been studied for bidirectional encoders » est **fausse dans sa formulation actuelle**. BioOntoBERT (2023) préentraîne précisément BERT avec 158 MB de textes générés à partir de neuf ontologies biomédicales. L’entrée BioOntoBERT existe déjà dans `thesis.bib`, mais son titre et ses auteurs sont erronés.

En conséquence, je déconseille de conserver ces quatre figures et le paragraphe de synthèse en l’état dans la version soutenue de la thèse.

## Méthode de double vérification

Le contrôle a été effectué en deux passes indépendantes :

1. lecture du code LaTeX et des légendes ;
2. inspection visuelle des pages compilées de la thèse ;
3. téléchargement des PDF primaires avec `curl`, puis extraction du texte avec `pdftotext` ;
4. comparaison avec les schémas originaux de K-BERT, DRAGON, SapBERT, CODER et EntiGraph ;
5. contrôle des codes CIM-10 et ATC avec les documents officiels OMS/ATIH ;
6. recherche élargie d’un précédent direct pour le préentraînement d’encodeurs à partir de textes d’ontologies.

Les constats ci-dessous distinguent les erreurs factuelles des simplifications pédagogiques acceptables. Aucun fichier `.tex` n’a été modifié pendant cet audit.

### Échelle de sévérité

- **Critique** : invalide une revendication de nouveauté ou attribue à un article un mécanisme qu’il ne propose pas.
- **Majeure** : représentation trompeuse d’un article ou omission de son mécanisme central.
- **Modérée** : simplification excessive, relation ambiguë, terminologie imprécise.
- **Mineure** : amélioration éditoriale sans incidence sur le raisonnement scientifique.

## 1. Figure des embeddings statiques

**Emplacement :** lignes 333–403, `fig:corpus-static`.

### Ce qui est correct

- Node2Vec produit bien des séquences par marches aléatoires biaisées, puis apprend des représentations de nœuds avec un objectif de type skip-gram.
- Le résultat est bien un vecteur non contextuel par nœud.
- La limite décrite dans le texte — une même représentation quel que soit le contexte linguistique — est pédagogiquement juste.
- OWL2Vec* et les expérimentations regroupées sous Snomed2Vec appartiennent bien à la famille générale des représentations statiques de graphes ou d’ontologies.

### Problèmes constatés

#### 1.1 RDF2Vec est réduit à une seule de ses variantes — sévérité modérée

La phrase et la légende présentent RDF2Vec comme un simple pipeline « random walk + skip-gram ». L’article original propose pourtant :

- deux stratégies de génération de séquences : marches dans le graphe RDF **et** transformations de Weisfeiler–Lehman ;
- deux architectures Word2Vec possibles : **CBOW ou skip-gram** ;
- des séquences pouvant préserver des informations propres au graphe RDF, et non une simple liste de concepts médicaux.

Le dessin reste correct comme exemple Node2Vec, mais pas comme description exhaustive commune à Node2Vec et RDF2Vec.

#### 1.2 Le résultat Snomed2Vec est simplifié — sévérité mineure à modérée

L’article Snomed2Vec n’introduit pas une unique architecture portant ce nom. Il compare notamment Node2Vec, MetaPath2Vec et les embeddings de Poincaré sur un sous-graphe SNOMED-CT extrait d’UMLS. Dire qu’il « applies Node2Vec » n’est pas faux, mais laisse croire que l’article se résume à cette méthode.

#### 1.3 Les relations du fragment médical sont ambiguës ou inversées — sévérité majeure

Les arêtes TikZ sont non orientées (`--`) alors que les relations représentées sont directionnelles.

- `Type 2 diabetes mellitus is-a Diabetes mellitus` est correct si la direction va du type 2 vers la classe générale.
- En conservant cette convention, le dessin place `Biguanides is-a Metformin`, ce qui est faux. **Metformin** est classée sous **Biguanides**, et non l’inverse.
- L’arête du code source relie `Metformin -- Type 2 diabetes` avec l’étiquette `treated-by`. Sans flèche, on ne sait pas si elle signifie « metformin is treated by type 2 diabetes » ou « type 2 diabetes is treated by metformin ». La seconde formulation est celle qui est voulue.

Correction minimale : utiliser des flèches orientées et écrire explicitement `Metformin → Biguanides` pour `is-a/classified-under`, ainsi que `Type 2 diabetes → Metformin` pour `treated-by`.

#### 1.4 `E08–E13` n’est pas la plage de la CIM-10 OMS/ATIH — sévérité majeure

Dans la CIM-10 de l’OMS et sa version française diffusée par l’ATIH, le bloc **Diabetes mellitus** couvre `E10–E14`. La plage `E08–E13` correspond à l’organisation de l’ICD-10-CM américaine. Comme le chapitre parle explicitement de la CIM-10 française et de l’ATIH, le libellé actuel mélange deux variantes nationales.

- À employer dans ce contexte : `E10–E14`.
- À conserver seulement si l’exemple est volontairement américain : `E08–E13`, avec la mention explicite `ICD-10-CM`.

Les autres codes vérifiés sont corrects : `E11` pour le diabète de type 2, `A10BA` pour les biguanides et `A10BA02` pour la metformine.

#### 1.5 Le dessin ne montre pas un fragment d’une ontologie unique — sévérité modérée

Le fragment combine :

- des catégories CIM-10 (`E10–E14`, `E11`) ;
- des catégories ATC (`A10BA`, `A10BA02`) ;
- une relation clinique ajoutée (`treated-by`) qui n’est pas une relation native de ces deux classifications.

Le titre `ontology fragment` est donc trop fort. Préférer `illustrative cross-terminology knowledge graph` ou préciser dans le texte qu’il s’agit d’un graphe pédagogique construit à partir de plusieurs terminologies.

### Correction recommandée

Conserver le schéma comme illustration de Node2Vec, corriger le fragment médical et nuancer la légende :

> **Proposition de légende.** *Walk-based static graph embeddings linearize graph neighbourhoods into sequences and learn one context-independent vector per node. Node2Vec uses biased random walks with a skip-gram objective; RDF2Vec additionally supports Weisfeiler–Lehman sequences and either skip-gram or CBOW.*

## 2. Figure d’injection dans les Transformers

**Emplacement :** lignes 405–460, `fig:corpus-inject`.

### Verdict

Cette figure est la plus problématique après EntiGraph. La légende affirme que K-BERT et DRAGON « place a knowledge-graph triple at the entity token inside the model ». Ce mécanisme commun n’existe pas.

### Comparaison article par article

| Travail | Mécanisme réel | Fidélité du TikZ actuel |
|---|---|---|
| ERNIE | Aligne les mentions avec des embeddings d’entités préentraînés, puis fusionne représentations lexicales et entités dans des encodeurs dédiés. | **Faible** : aucun simple triple n’est attaché au token. |
| KnowBERT | Effectue une liaison d’entités sur des spans et insère des modules KAR entre les couches de BERT. | **Faible** : ni candidats d’entités, ni span, ni module intermédiaire. |
| K-BERT | Injecte les entités et relations comme branches d’un arbre de phrase, puis utilise positions souples et matrice de visibilité. | **Partielle** : l’ancrage sur `metformin` est évocateur, mais les nœuds injectés devraient entrer dans la séquence du Transformer. |
| KEPLER | Entraîne un encodeur partagé avec MLM et un objectif de représentation de graphe de type TransE à partir de descriptions d’entités. | **Nulle** : ce n’est pas une injection de triple dans chaque phrase. |
| CoLAKE | Construit un graphe mot-connaissance unifié comprenant nœuds mots, entités et relations, puis masque des nœuds. | **Faible** : le graphe unifié et les nœuds relationnels sont absents. |
| DRAGON | Reçoit séparément un segment de texte et son sous-graphe local ; un LM et un GNN échangent de l’information dans un encodeur multimodal, avec MLM et prédiction de liens. | **Nulle** : DRAGON n’insère pas un triple au token. |

### Problème K-BERT — sévérité majeure

Dans le TikZ, les tokens de la phrase vont seuls vers le Transformer. Le triple reste à l’extérieur et seule une flèche remonte vers le token `metformin`. Dans K-BERT, les tokens issus du graphe deviennent au contraire des éléments de l’entrée arborescente aplatie. Les positions souples et la matrice de visibilité empêchent ces branches de perturber la phrase originale.

Pour revendiquer une représentation de K-BERT, il faut montrer au minimum :

`sentence → sentence tree with injected entity/relation tokens → soft positions + visible matrix → Transformer`.

### Problème DRAGON — sévérité critique d’attribution

Le schéma original de DRAGON possède deux entrées parallèles :

- un texte traité par le langage modèle ;
- un sous-graphe local traité par un GNN.

Les deux flux sont fusionnés bidirectionnellement. Les objectifs de préentraînement sont MLM côté texte et prédiction de liens côté graphe. La figure actuelle ne montre aucun de ces éléments distinctifs.

### Nuance nécessaire sur les résultats de DRAGON

Le gain d’environ trois points sur MedQA par rapport à BioLinkBERT est bien rapporté. En revanche, le gain d’environ dix points sur les questions complexes est analysé principalement sur des benchmarks de raisonnement général comme CSQA et OBQA. La formulation actuelle juxtapose les deux observations comme si elles provenaient du même benchmark médical.

Proposition :

> *On biomedical evaluation, DRAGON improves MedQA accuracy by about three absolute points over BioLinkBERT. Separate analyses on general-domain QA benchmarks report larger gains for categories used as proxies for complex reasoning.*

### Correction recommandée

Deux solutions sont scientifiquement propres :

1. **scinder la figure en deux panneaux** : K-BERT à gauche, DRAGON à droite ;
2. **restreindre la figure à K-BERT** et retirer DRAGON de sa légende, puis ajouter un schéma distinct pour le couple texte–sous-graphe de DRAGON.

Une figure unique censée représenter ERNIE, KnowBERT, K-BERT, KEPLER, CoLAKE et DRAGON restera nécessairement trompeuse, car ces travaux interviennent à des niveaux différents : entrée, modules internes, objectifs de préentraînement ou architecture multimodale.

## 3. Figure des approches contrastives médicales

**Emplacement :** lignes 462–504, `fig:corpus-contrastive`.

### Ce qui est correct pour SapBERT

La géométrie générale est bonne : les synonymes partageant un même CUI UMLS sont rapprochés, tandis que les mentions d’autres concepts servent de négatifs. Le mining de paires difficiles et la loss multi-similarity ne sont pas dessinés, mais cette omission est acceptable dans une vue pédagogique.

Le terme français `diabète de type 2` n’est pas représentatif du jeu anglais utilisé par SapBERT, mais il est cohérent avec l’objectif multilingue de CODER. Il faut simplement éviter de laisser croire que cet exemple français provient des expériences originales SapBERT.

### CODER est mal représenté — sévérité majeure

CODER ne se contente pas d’ajouter davantage de synonymes. Sa contribution centrale est un **double apprentissage contrastif** :

- similarités terme–terme ;
- similarités terme–relation–terme calculées à partir de triplets UMLS.

Le TikZ ne montre que le premier objectif. La phrase « Both methods read the graph through pairs of terms » efface donc précisément la nouveauté de CODER, alors que les lignes précédentes disent correctement qu’il ajoute des triplets relationnels.

### `Type 1 diabetes` n’est pas « unrelated » — sévérité modérée

Le diabète de type 1 et le diabète de type 2 sont deux concepts distincts, donc ils peuvent constituer une paire négative au sens de la loss. Ils restent néanmoins sémantiquement proches et partagent un hyperonyme. Le libellé `unrelated term` est faux en langage courant et scientifiquement maladroit.

Préférer :

- `different concept / negative pair` ; ou
- `hard negative: related but different CUI`.

`NIDDM` est une désignation historique de type 2 ; son emploi comme synonyme terminologique n’est pas en soi une erreur.

### Correction recommandée

Ajouter un second sous-schéma propre à CODER, par exemple :

`(Type 2 diabetes, treated-by) → Metformin`, avec une loss relationnelle distincte de la loss sur synonymes.

> **Proposition de légende.** *SapBERT contrasts synonymous UMLS terms against terms denoting different CUIs. CODER retains this term–term objective and adds a relation-aware term–relation–term objective over UMLS triples, including in a cross-lingual setting.*

## 4. Figure graph-to-text et attribution à EntiGraph

**Emplacement :** lignes 506–557, `fig:corpus-g2t`.

### Ce que fait réellement EntiGraph

Le pipeline EntiGraph est :

1. partir d’un petit corpus de documents réels ;
2. extraire les entités saillantes de chaque document ;
3. échantillonner des paires ou triplets de ces entités ;
4. demander à un LLM d’analyser leurs relations **en restant conditionné par le document source** ;
5. ajouter les textes synthétiques produits au corpus de préentraînement continu.

Le « graphe d’entités » est donc induit à partir des documents. EntiGraph ne prend pas en entrée une ontologie préexistante telle que CIM-10 ou ATC.

Les nombres de la figure sont en revanche corrects : le corpus réel d’environ 1,3 million de tokens est amplifié jusqu’à environ 455 millions de tokens synthétiques. Les expériences de l’article utilisent GPT-4-Turbo pour la génération et poursuivent le préentraînement de Llama 3 8B, un modèle décodeur.

### Erreur d’attribution — sévérité critique

Le TikZ actuel montre :

`ontologie existante → language model → verbalisation directe`.

Ce pipeline peut illustrer une proposition personnelle de verbalisation de classifications médicales, ou un travail tel que BioOntoBERT/Onto2Sen, mais **pas EntiGraph**. Associer le facteur `1.3M → 455M` à ce dessin suggère que les 455 millions de tokens d’EntiGraph ont été générés à partir d’un graphe structuré fourni, ce qui est incorrect.

### Rôle de *Textbooks Are All You Need*

Cet article motive l’intérêt de données synthétiques de haute qualité. Il ne propose pas de méthode graph-to-text et ne doit pas servir de preuve directe pour la verbalisation d’une ontologie.

### Correction recommandée

Créer deux panneaux séparés :

- **EntiGraph** : `source documents → entity extraction → sampled entity pairs/triples + source document → LLM relation analysis → synthetic corpus` ;
- **Ontology verbalisation** : `biomedical ontology → lexical and relation sentences → encoder pretraining`, avec BioOntoBERT comme précédent direct.

Si le dessin actuel est conservé comme intuition de la méthode future de la thèse, sa légende doit dire explicitement qu’il est **conceptuel** et ne représente pas l’architecture EntiGraph.

## 5. Précédent direct manquant : BioOntoBERT

### Constat critique

Le paragraphe des lignes 559–566 affirme :

> *Graph-to-text for pretraining [...] has not been studied for bidirectional encoders.*

BioOntoBERT (Sahil & Kumar, 2023) constitue un contre-exemple direct :

- modèle de base : BERT, donc encodeur bidirectionnel ;
- source : neuf ontologies biomédicales ;
- système Onto2Sen : extraction de classes, annotations et propriétés ;
- textes produits : documents lexicaux (noms, synonymes, définitions) et phrases de relations de concepts, notamment `subClass` ;
- préentraînement : MLM, sans NSP ;
- volume : environ 20 millions de mots / 158 MB ;
- évaluation : MedMCQA.

La revendication peut éventuellement être resserrée vers un territoire plus spécifique — génération par LLM à partir de classifications médicales nationales françaises, diversité contrôlée des verbalismes, ou comparaison systématique encodeur/décodeur — mais pas rester générale.

### Entrée bibliographique erronée

L’entrée actuelle de `thesis.bib` est :

```bibtex
@inproceedings{shashikumar2023bioontobert,
  title={Leveraging Biomedical Ontologies to Boost Pre-training for Language Models},
  author={Shashikumar, Supreeth P and Amrollahi, Fatemeh and Nemati, Shamim},
  ...
}
```

Le PDF CEUR donne :

```bibtex
@inproceedings{sahil2023bioontobert,
  title={Leveraging Biomedical Ontologies to Boost Performance of BERT-Based Models for Answering Medical MCQs},
  author={Sahil, Sahil and Kumar, P. Sreenivasa},
  booktitle={Proceedings of the International Conference on Biomedical Ontologies 2023},
  series={CEUR Workshop Proceedings},
  volume={3603},
  pages={94--105},
  year={2023}
}
```

Le titre et les auteurs de l’entrée locale doivent être corrigés avant de citer ce travail. Il faudra vérifier la forme bibliographique exacte souhaitée par le style de la thèse, mais l’attribution actuelle ne correspond pas au PDF.

### Proposition de paragraphe de remplacement

> *Ontology-derived text has already been explored for bidirectional encoders. BioOntoBERT uses Onto2Sen to convert nine biomedical ontologies into lexical documents and concept-relation sentences, then continues BERT pretraining on 158 MB of ontology-generated text. EntiGraph addresses a different setting: it extracts entities from a small document corpus and prompts an LLM, conditioned on each source document, to produce relation-focused synthetic text for continued pretraining of a decoder model. LLM-based verbalisation of national French medical classifications therefore remains less explored, but ontology-to-text pretraining for encoders is not itself unprecedented.*

Cette version conserve une lacune de recherche défendable sans nier BioOntoBERT.

## 6. Problèmes transversaux de modélisation médicale

### Mélange de classifications et d’ontologies

CIM-10 et ATC sont des classifications/terminologies contrôlées. Le graphe dessiné ajoute une relation thérapeutique et les relie comme s’il s’agissait d’une ontologie médicale intégrée. Ce choix est acceptable pour un exemple pédagogique à condition de le déclarer.

Recommandation : ajouter sous le graphe une note telle que :

> *Illustrative graph combining ICD-10 and ATC categories with an added clinical relation; not a native fragment of either classification.*

### Orientation des arêtes

Toutes les relations sémantiques doivent être fléchées. Une convention unique doit être indiquée et conservée dans les quatre figures :

- `subclass → superclass` pour `is-a` ;
- `disease → drug` pour `treated-by` ;
- `drug → pharmacological class` pour `classified-under`.

### Vocabulaire

- Remplacer `ontology fragment` par `illustrative medical knowledge graph` lorsque plusieurs sources sont combinées.
- Remplacer `unrelated term` par `different concept` ou `hard negative`.
- Distinguer `ICD-10`/`CIM-10` de `ICD-10-CM`.
- Ne pas employer `injection` comme catégorie générale pour des objectifs joints tels que KEPLER ou des architectures multimodales telles que DRAGON sans expliquer le niveau d’intégration.

## 7. Plan de correction priorisé

### Priorité 1 — indispensable avant soumission

1. Corriger la revendication sur l’absence de graph-to-text pour les encodeurs et intégrer BioOntoBERT.
2. Corriger l’entrée BioOntoBERT dans `thesis.bib`.
3. Refaire la figure EntiGraph pour partir de documents, ou la relabelliser comme pipeline conceptuel distinct d’EntiGraph.
4. Retirer DRAGON de la légende du TikZ d’injection ou créer un panneau DRAGON fidèle avec entrées texte + sous-graphe, LM + GNN et objectifs MLM + link prediction.
5. Corriger `E08–E13` en `E10–E14` dans le contexte français/OMS.

### Priorité 2 — fortement recommandé

6. Orienter toutes les relations et inverser la hiérarchie metformine/biguanides.
7. Ajouter la branche relationnelle de CODER à la figure contrastive.
8. Remplacer `unrelated term` par `different concept / hard negative`.
9. Séparer le résultat biomédical de DRAGON de son analyse de raisonnement complexe sur les benchmarks généraux.

### Priorité 3 — amélioration de précision

10. Nuancer RDF2Vec : marches ou WL, skip-gram ou CBOW.
11. Présenter Snomed2Vec comme une comparaison de plusieurs méthodes sur SNOMED-CT.
12. Qualifier le fragment médical de graphe multi-terminologies illustratif.

## 8. Références primaires vérifiées

### Embeddings de graphes

- Grover & Leskovec, [node2vec: Scalable Feature Learning for Networks](https://arxiv.org/abs/1607.00653), 2016.
- Ristoski & Paulheim, [RDF2Vec: RDF Graph Embeddings for Data Mining](https://madoc.bib.uni-mannheim.de/41307/1/Ristoski_RDF2Vec.pdf), 2016.
- Agarwal et al., [Snomed2Vec: Random Walk and Poincaré Embeddings of a Clinical Knowledge Base for Healthcare Analytics](https://arxiv.org/abs/1907.08650), 2019.
- Chen et al., [OWL2Vec*: Embedding of OWL Ontologies](https://arxiv.org/abs/2009.14654), 2021.

### Intégration de connaissances aux modèles de langue

- Zhang et al., [ERNIE: Enhanced Language Representation with Informative Entities](https://arxiv.org/abs/1905.07129), 2019.
- Peters et al., [Knowledge Enhanced Contextual Word Representations](https://aclanthology.org/D19-1005/), 2019.
- Liu et al., [K-BERT: Enabling Language Representation with Knowledge Graph](https://arxiv.org/abs/1909.07606), 2020.
- Wang et al., [KEPLER: A Unified Model for Knowledge Embedding and Pre-trained Language Representation](https://arxiv.org/abs/1911.06136), 2021.
- Sun et al., [CoLAKE: Contextualized Language and Knowledge Embedding](https://aclanthology.org/2020.coling-main.327/), 2020.
- Yasunaga et al., [Deep Bidirectional Language-Knowledge Graph Pretraining](https://arxiv.org/abs/2210.09338), 2022.

### Approches contrastives

- Liu et al., [Self-Alignment Pretraining for Biomedical Entity Representations](https://aclanthology.org/2021.naacl-main.334/), 2021.
- Yuan et al., [CODER: Knowledge Infused Cross-Lingual Medical Term Embedding for Term Normalization](https://arxiv.org/abs/2011.02947), 2022.

### Données synthétiques et graph-to-text

- Gunasekar et al., [Textbooks Are All You Need](https://arxiv.org/abs/2306.11644), 2023.
- Yang et al., [Synthetic Continued Pretraining](https://arxiv.org/abs/2409.07431), ICLR 2025.
- Sahil & Kumar, [Leveraging Biomedical Ontologies to Boost Performance of BERT-Based Models for Answering Medical MCQs](https://ceur-ws.org/Vol-3603/Paper9.pdf), 2023.

### Nomenclatures officielles

- ATIH, [CIM-10 à usage PMSI](https://www.atih.sante.fr/sites/default/files/public/content/2665/cim10_2015_final_0.pdf).
- OMS, [ICD-10 Volume 2 — Instruction Manual](https://icd.who.int/browse10/content/statichtml/icd10volume2_en_2016.pdf).
- OMS, [ATC/DDD Toolkit — ATC Classification](https://www.who.int/tools/atc-ddd-toolkit/atc-classification).
- WHO Collaborating Centre for Drug Statistics Methodology, [Guidelines for ATC Classification and DDD Assignment 2024](https://atcddd.fhi.no/filearchive/publications/1_2024_guidelines__final_web.pdf).

## 9. Limites de cet audit

- Il s’agit d’un audit ciblé des figures et des affirmations qui les entourent, pas d’une revue systématique exhaustive de toute la littérature sur les graphes biomédicaux.
- La validité clinique de la phrase exemple sur la metformine est générale et pédagogique ; elle ne remplace pas une recommandation thérapeutique détaillée.
- Les résultats rapportés dans les articles ont été contrôlés dans leurs PDF, mais les expériences n’ont pas été reproduites.
- Les URL et métadonnées bibliographiques devront être normalisées selon le style BibTeX final de la thèse.

## Conclusion

Le fil narratif — embeddings statiques, intégration dans les Transformers, apprentissage contrastif, puis génération de texte — est bon. Les défauts viennent surtout du fait que chaque TikZ essaie de représenter une famille trop hétérogène avec un unique mécanisme.

La correction la plus sûre consiste à faire de chaque figure l’illustration d’un mécanisme précisément nommé, puis à expliquer les variantes dans le texte. Les changements indispensables sont la représentation fidèle d’EntiGraph et de DRAGON, l’ajout de la composante relationnelle de CODER, la correction du graphe médical et surtout la reconnaissance de BioOntoBERT comme précédent direct pour le préentraînement de BERT sur du texte dérivé d’ontologies.
