# Audit quantitatif de l'état de l'art

Date : 19 juillet 2026  
Périmètre : les trois chapitres actifs de l'état de l'art, leurs tableaux, leurs figures TikZ et les deux graphiques externes Chinchilla/LLaMA.  
Nature : vérification des nombres, ordres de grandeur, ratios, comparaisons, tailles de corpus et statistiques de ressources. Aucun fichier TeX ou BibTeX n'a été modifié.

## Verdict exécutif

L'essentiel est solide. Sur **85 groupes de revendications quantitatives** contrôlés :

| Verdict | Nombre |
|---|---:|
| exact ou directement soutenu | 66 |
| arrondi ou simplification fidèle | 5 |
| exact seulement pour une version ou un millésime donné | 9 |
| incorrect | 1 |
| non traçable avec la source actuellement donnée | 3 |
| nombres manifestement schématiques mais non signalés comme tels | 1 |
| **Total** | **85** |

Je recommande **trois corrections nécessaires** avant soumission :

1. corriger le mélange entre les séries à 26 et 27 symboles dans la figure de Shannon ;
2. retirer ou remplacer les « 30 million stays » du PMSI, que la source citée ne permet pas d'établir et qui semblent mélanger des unités d'activité hospitalière ;
3. harmoniser les deux dénombrements contradictoires de la CIM-10 française, 19 000 dans un chapitre et 17 000 dans l'autre, en nommant le millésime et la règle de comptage.

Les autres interventions proposées sont des sécurisations : dater les statistiques vivantes, signaler que les scores du TikZ GLiNER sont illustratifs, et sourcer les longueurs de documents cliniques.

## Instantané et méthode

Les numéros de ligne de ce rapport correspondent aux fichiers suivants :

- `language_modeling.tex` : `97c7c215f3439e7bd5b1993d1c6b29cfedd9405efad5e375275d29a823571568` ;
- `corpus_annotation.tex` : `9c25e0929b5c87a5d1f44d314f27cdc8f753c20454c04af9b4188bcb86e142b6` ;
- `clinical_ie.tex` : `128f9498454f2513c27253d2d9f0fd4dff8401bbd0c5d53ec4bcc6919d36921d`.

J'ai extrait les lignes contenant des nombres, pourcentages, rapports, approximations et quantités écrites en toutes lettres. Les coordonnées purement graphiques, tailles de police, dimensions TikZ et années bibliographiques sans rôle analytique ont été exclues. Les valeurs proches appartenant à une même phrase, ligne de tableau ou figure ont été regroupées en une revendication vérifiable.

Pour chaque groupe, l'ordre de préférence a été : papier primaire cité, tableau ou annexe du papier, fiche officielle du corpus/modèle, puis page institutionnelle versionnée. Les valeurs vivantes ont été distinguées des valeurs exactes à la date de l'expérience. Une absence dans la source est notée « non traçable », jamais transformée en validation.

Les constats déjà développés dans `2026-07-19-related-work-fidelity-audit.md` et son addendum ne sont pas présentés ici comme de nouvelles erreurs. Ils ont néanmoins été pris en compte pour éviter qu'une valeur déjà corrigée soit requalifiée à tort.

## Corrections nécessaires

### Q-LM-1 — La figure de Shannon mélange deux alphabets

- **Emplacement** : `language_modeling.tex:37-42`, surtout `language_modeling.tex:64-70`.
- **Valeurs actuelles** : 4,76 ; 4,14 ; 3,56 bits pour respectivement 0, 1 et 2 lettres de contexte, avec une légende annonçant un alphabet de 27 symboles.
- **Source primaire** : [Shannon, 1951, *Prediction and Entropy of Printed English*](https://www.princeton.edu/~wbialek/rome/refs/shannon_51.pdf), Table 4.
- **Contrôle** : Shannon publie deux séries distinctes :

  | Série | $F_0$ | $F_1$ | $F_2$ |
  |---|---:|---:|---:|
  | 26 lettres | 4,70 | 4,14 | 3,56 |
  | 27 symboles, espace inclus | 4,76 | 4,03 | 3,32 |

La figure prend $F_0$ dans la série à 27 symboles et $F_1,F_2$ dans celle à 26 lettres. Le point de long contexte, construit à partir de la borne 0,6--1,3, reste défendable.

- **Correction minimale sûre** : conserver le cadrage à 27 symboles et remplacer `4.14` par `4.03`, puis `3.56` par `3.32`. L'autre solution cohérente serait 4,70/4,14/3,56 et une légende à 26 lettres, mais elle obligerait à modifier davantage la prose.

### Q-IE-1 — « 30 million stays » n'est pas établi et semble confondre séjours, journées et séances

- **Emplacements** : `clinical_ie.tex:23-26` et `clinical_ie.tex:181-186`.
- **Valeur actuelle** : environ 30 millions de séjours PMSI par an.
- **Source locale** : `\citep{atih_pmsi}` renvoie à `https://www.atih.sante.fr/le-pmsi`, actuellement en erreur 404 ; la notice ne donne ni année ni tableau.
- **Contre-vérification officielle** : pour 2023, la DREES rapporte **10,6 millions de séjours d'hospitalisation complète** et **19,4 millions de journées d'hospitalisation partielle** ; elle rapporte séparément les séances, urgences et journées d'HAD. Le total proche de 30 millions apparaît donc quand on additionne des **séjours** et des **journées**, pas comme un dénombrement homogène de 30 millions de séjours. Le MCO seul représente par ailleurs 19,7 millions de séjours en 2023. Voir [DREES, *Les établissements de santé en 2023*](https://www.drees.solidarites-sante.gouv.fr/publications-communique-de-presse-documents-de-reference/panoramas-de-la-drees/250522_Panorama_etablissements-de-sante2025) et les analyses [ATIH PMSI-MCO 2023](https://www.atih.sante.fr/sites/default/files/public/content/4852/mco_aah23.pdf).
- **Verdict** : le nombre actuel n'est pas défendable avec l'unité « stays ».
- **Correction minimale sûre** : supprimer le nombre et écrire, aux deux endroits :

  > The PMSI covers hospital activity nationwide, and coding is still largely performed by professional coders.

  Si un chiffre est indispensable, choisir un champ et un millésime explicites, par exemple les séjours MCO 2023, sans les additionner aux journées ou séances.

### Q-XF-1 — La CIM-10 française vaut à la fois 19 000 et 17 000 codes dans la thèse

- **Emplacements** : `corpus_annotation.tex:295-300` annonce environ 19 000 codes ; `clinical_ie.tex:188-190` et `clinical_ie.tex:283-288` annoncent environ 17 000 codes.
- **Problème** : les deux valeurs ne peuvent pas décrire sans qualification la même édition et la même unité. Le total varie selon le millésime, selon que l'on compte catégories et sous-catégories, extensions ATIH, codes actifs seulement ou tous les nœuds de la hiérarchie.
- **Source officielle** : l'ATIH publie une CIM-10-FR à usage PMSI **chaque année** et ajoute ses propres extensions ; la [notice 2025](https://www.atih.sante.fr/sites/default/files/public/content/4903/notice_technique_atih-mco-had-smr-psy-2025_-_hh.pdf) confirme cette évolution annuelle.
- **Verdict** : contradiction interne ; je ne choisis pas arbitrairement 17 000 ou 19 000 sans fichier de référence et règle de comptage.
- **Correction minimale sûre** : soit employer partout « tens of thousands of codes », soit calculer une édition précise et écrire par exemple « approximately N active codes in the 2025 CIM-10-FR PMSI release, counting ... ».

## Sécurisations fortement recommandées

### Q-IE-2 — Les six scores du TikZ GLiNER sont inventés pour l'illustration

- **Emplacement** : `clinical_ie.tex:393-419`, valeurs 0,08 ; 0,95 ; 0,09 ; 0,97 ; 0,05 ; 0,11.
- **Contrôle** : l'architecture générale est fidèle à [Zaratiana et al., 2024, Figure 2 et §2](https://aclanthology.org/2024.naacl-long.300.pdf), mais cette phrase, ces spans et ces probabilités ne sont pas des sorties rapportées par le papier.
- **Risque** : une matrice chiffrée dans une figure scientifique peut être lue comme une reproduction de résultats réels.
- **Correction minimale sûre** : ne pas changer les valeurs ; ajouter simplement « illustrative scores » dans la ligne sous la matrice ou dans la légende :

  > ... in a similarity matrix (illustrative scores), whose high-scoring cells are the recognised entities.

### Q-CA-1 — PubMed et PMC mélangent statistique courante et instantané Meditron 2023

- **Emplacement** : `corpus_annotation.tex:203-209`.
- **Valeurs actuelles** : environ 39 millions de citations/abstracts PubMed ; environ 4,5 millions d'articles PMC Open Access.
- **Contrôle** :

  - PubMed annonce aujourd'hui plus de 40 millions de citations ; tous les enregistrements n'ont pas d'abstract. La requête NCBI déjà documentée dans `thesis.bib` donne 29 090 670 enregistrements avec abstract au 16 juin 2026. Voir [NCBI, About PubMed](https://pubmed.ncbi.nlm.nih.gov/about/).
  - Meditron a bien collecté **4,47 millions** d'articles du PMC Open Access Subset, plus 444 521 articles PubMed OA hors PMC, avec une coupure en août 2023. Le « 4,5 million » est donc exact pour **ce sous-corpus historique** : [Chen et al., 2023, §2.2 et Table 1](https://arxiv.org/pdf/2311.16079).
  - Ce n'est plus la taille courante : la requête NCBI locale donne 7 949 676 articles dans le PMC OA Subset en juin 2026, tandis que l'archive PMC complète annonce plus de 12 millions d'articles. Voir [PMC](https://pmc.ncbi.nlm.nih.gov/).

- **Correction minimale sûre** : choisir l'un des deux cadrages.

  Historique :

  > Meditron's August 2023 snapshot contained 4.47 million full-text articles from the PMC Open Access Subset.

  Courant :

  > PubMed contains over 40 million citations; about 29 million records contained an abstract in June 2026. The PMC Open Access Subset contained about 7.95 million reusable full-text articles at the same date.

### Q-CA-2 — ISTEX est une statistique vivante devenue datée

- **Emplacement** : `corpus_annotation.tex:239-242`.
- **Valeur actuelle** : environ 27 millions de références scientifiques.
- **Source officielle courante** : la [page d'accueil ISTEX](https://www.istex.fr/) annonce **32 millions de documents** en juillet 2026.
- **Verdict** : 27 millions peut correspondre à un ancien état, mais aucun millésime ni citation n'est donné.
- **Correction minimale sûre** : « ISTEX provides about 32 million scientific documents (accessed July 2026) », ou « tens of millions of scientific documents » pour éviter la maintenance.

### Q-CA-3 — Les 371 000 concepts SNOMED CT doivent être versionnés

- **Emplacement** : `corpus_annotation.tex:290-293`.
- **Valeur actuelle** : environ 371 000 concepts.
- **Contrôle** : ce total est plausible pour une édition antérieure. Les notes officielles de mars 2026 donnent 378 553 concepts actifs dans l'édition internationale et 386 110 dans l'édition américaine. Les éditions et extensions ne sont donc pas interchangeables.
- **Correction minimale sûre** : « approximately 379,000 active concepts in the March 2026 International Edition », ou retirer le nombre et garder « hundreds of thousands of clinical concepts ».

### Q-CA-4 — CCAM et ATC ont besoin d'une édition et d'une règle de comptage

- **Emplacements** : `corpus_annotation.tex:302-307` et `clinical_ie.tex:188-190`.
- **Valeurs** : environ 8 000 codes CCAM et 6 000 codes ATC de cinquième niveau.
- **Contrôle** : les ordres de grandeur sont plausibles, mais les sources locales ne permettent pas de reproduire exactement ces deux totaux. La CCAM descriptive ATIH existe en codes à sept caractères avec, selon le fichier, des extensions ATIH à trois caractères ; compter les codes de base ou les couples code-extension ne donne pas la même unité. L'[ATC/DDD Index 2026](https://atcddd.fhi.no/atc_ddd_index/) est également mis à jour chaque année.
- **Correction minimale sûre** : conserver les ordres de grandeur seulement en ajoutant l'édition, ou remplacer les trois nombres ICD/CCAM/ATC par « tens of thousands / several thousand » tant qu'un script de dénombrement versionné n'est pas joint.

### Q-XF-2 — Les longueurs de comptes rendus cliniques ne sont pas sourcées

- **Emplacements** : `language_modeling.tex:1174-1179` (« often runs past 2000 tokens ») ; `clinical_ie.tex:188-191` (« 1000 to 3000 tokens »).
- **Contrôle** : 512 tokens pour BERT est exact. Je n'ai pas trouvé, dans les références voisines, une distribution établissant universellement 1 000--3 000 tokens pour un discharge summary. La longueur dépend du corpus, du type de note et surtout du tokenizer.
- **Correction minimale sûre** : soit citer les statistiques d'un corpus précis et nommer le tokenizer, soit écrire :

  > Clinical documents often exceed BERT's 512-token limit and therefore require truncation or segmentation.

## Quantités importantes recontrôlées et correctes

Cette section consigne les vérifications positives les plus susceptibles d'attirer l'attention d'un rapporteur.

### Shannon, GPT-3 et lois d'échelle

- L'expérience de Markov porte bien sur 20 000 lettres ; les transitions voyelle-vers-voyelle sont proches de 13 %, donc 13/87 est un arrondi fidèle.
- Les bornes de Shannon 0,6--1,3 bit par caractère sont exactes. Le problème est uniquement le mélange des colonnes à 26 et 27 symboles dans le graphique.
- Les neuf cellules du tableau GPT-3 sont exactes : addition 76,9/99,6/100,0 ; soustraction 58,0/86,4/98,9 ; TriviaQA 64,3/68,0/71,2. Voir [Brown et al., 2020](https://proceedings.neurips.cc/paper/2020/hash/1457c0d6bfcb4967418bfb8ac142f64a-Abstract.html).
- Pour Chinchilla, « over 400 », $E=1.69$, $A=406.4$, $B=410.7$, $\alpha=0.34$, $\beta=0.28$, $6ND$, 70 B/1,4 T, Gopher 280 B, MMLU 67,6 contre 60,0 et 57 sujets sont tous conformes à [Hoffmann et al., 2022](https://arxiv.org/pdf/2203.15556). « Doubler ensemble paramètres et données » est une synthèse fidèle, pas une identité exacte de toutes leurs approches.
- Les points de `plots/related_works/chinchilla_scaling.py` reproduisent bien la Table 3, approche 1. Les valeurs de `plots/related_works/llama_vs_gpt3.py` reproduisent bien les lignes GPT-3 175B et LLaMA 13B de la table de raisonnement de LLaMA ; LLaMA est supérieur sur cinq des sept tâches montrées.

### Corpus web et biomédicaux

- C4 : environ 750 GB depuis le snapshot d'avril 2019 ; Pile : 825 GiB/22 composantes, correctement arrondi à 800 GB/22 ; OSCAR français/CamemBERT : 138 GB.
- FineWeb : 15 T tokens/96 snapshots ; FineWeb-Edu : 1,3 T ; 460 000 pages annotées par Llama-3-70B-Instruct ; scores 0--5 ; environ 6 000 heures H100 ; retrait d'environ 92 %. Tous ces nombres sont conformes à [Penedo et al., 2024](https://arxiv.org/pdf/2406.17557).
- TxT360 : 99 snapshots et 4,83 T tokens Common Crawl après déduplication globale ; Dolma : 3 T ; ROOTS : 1,6 TB. Voir la [fiche TxT360](https://huggingface.co/datasets/LLM360/TxT360), [Dolma](https://aclanthology.org/2024.acl-long.840/) et [ROOTS](https://aclanthology.org/2023.acl-demo.29/).
- Les corpus français de 31 000 documents PubMed, 136 millions de mots et 21 millions de rapports cliniques sont correctement repris. Pour le dernier, la source dit bien « 21M clinical reports », pas patients ni séjours.
- EntiGraph : 1,3 M tokens source vers 455 M tokens synthétiques, avec Llama 3 8B et GPT-4-Turbo ; valeurs exactes dans [Yang et al., 2025, §3 et §5](https://arxiv.org/pdf/2409.07431).

### Modèles biomédicaux et architectures

- BioClinical ModernBERT : plus de 53,5 B tokens et 20 jeux cliniques ; le TeX arrondit correctement à plus de 53 B et vingt jeux. Voir [Sounack et al., 2025](https://arxiv.org/pdf/2506.10896).
- Meditron : versions 7 B et 70 B, environ 48 B tokens au dernier checkpoint présenté, et 1 % de replay général ; conforme à [Chen et al., 2023](https://arxiv.org/pdf/2311.16079).
- MosaicBERT : masque 30 % contre 15 % pour BERT ; 1,13 h sur 8 A100 80 GB ; coût annoncé d'environ 20 dollars. L'annexe détaille une estimation de 22,60 dollars, donc la formulation actuelle est fidèle. Voir [Portes et al., 2023](https://arxiv.org/pdf/2312.17482).
- Longformer et BigBird : 4 096 tokens ; ModernBERT et BioClinical ModernBERT : 8 192 ; le rapport $8192/512=16$ est exact.

### Jeux cliniques et modèles ouverts

- BC5CDR : 1 500 articles PubMed représentés par titre et abstract ; NCBI Disease : 793 abstracts ; JNLPBA : cinq types ; BLURB : treize jeux.
- QUAERO : dix groupes sémantiques ; CAS1/CAS2 : deux/huit classes selon la présentation DEFT retenue dans la thèse ; DrBenchmark : vingt tâches sur douze jeux. La réserve antérieure sur CAS est documentaire, pas une nouvelle contradiction numérique démontrée ici.
- FRACCO : 1 301 cas synthétiques ; FRASIMED : 2 051 documents, correctement arrondi à environ 2 000.
- GLiNER : variantes jusqu'à 0,3 B paramètres ; UniversalNER : 45 889 paires instruction-sortie, 13 020 types et un gain moyen de 7--9 points absolus face à ChatGPT. Les « 45 000 », « 13 000 » et « several points » sont donc fidèles. Voir [GLiNER](https://aclanthology.org/2024.naacl-long.300.pdf) et [UniversalNER](https://arxiv.org/pdf/2308.03279).

## Registre de couverture réconcilié

Les groupes ci-dessous donnent la granularité de comptage utilisée pour obtenir le total de 85. Une ligne peut contenir plusieurs cellules d'un même tableau ou plusieurs constantes d'une même équation, vérifiées individuellement.

| Fichier / bloc | Groupes | Répartition des verdicts | Contenu couvert |
|---|---:|---|---|
| LM — Markov et Shannon | 4 | 2 exacts, 1 arrondi fidèle, 1 incorrect | 20 000 ; 13/87 ; taux de premier choix ; bornes et figure d'entropie |
| LM — Bengio et BERT | 2 | 1 exact, 1 arrondi fidèle | réduction de perplexité ; 15 %, 80/10/10 |
| LM — GPT-3 | 2 | 2 exacts | 175 B, 2 048, 10--100 ; neuf cellules du tableau |
| LM — Chinchilla/Kaplan | 6 | 5 exacts, 1 simplification fidèle | >400 modèles ; équation et coefficients ; FLOPs ; 20 tokens/paramètre ; tailles ; MMLU |
| LM — LLaMA | 3 | 3 exacts | 7 B/1 T ; 13 B contre 175 B ; 65 B contre Chinchilla/PaLM |
| LM — instruction et alignement | 5 | 4 exacts, 1 arrondi fidèle | FLAN, T0, SuperNI, InstructGPT et facteurs de taille |
| LM — continual pretraining | 7 | 7 exacts | Gururangan, Ibrahim, Xie, Guo, Dorfner et budgets/deltas associés |
| LM — modèles biomédicaux | 7 | 7 exacts | BioBERT, SciBERT, BioClinical ModernBERT, CamemBERT, BioMistral, Meditron |
| LM — architecture et contexte | 4 | 3 exacts, 1 non traçable | MosaicBERT, FlashAttention, fenêtres 4 096/8 192, longueur clinique |
| **Sous-total LM** | **40** | **34 exacts, 4 fidèles, 1 incorrect, 1 non traçable** | |
| Corpus — tokens de modèles | 2 | 2 exacts | GPT-3 300 B ; LLaMA 1--1,4 T |
| Corpus — Common Crawl | 2 | 1 exact, 1 versionné | depuis 2008, fréquence ; ordre de grandeur par snapshot |
| Corpus — C4/Pile/OSCAR | 3 | 3 exacts | 750 GB ; 800 GB/22 ; 138 GB |
| Corpus — FineWeb/TxT/Dolma/ROOTS | 4 | 4 exacts | 15 T/96 ; 1,3 T ; 4,83 T/99 ; 3 T/1,6 TB |
| Corpus — filtrage FineWeb-Edu | 2 | 2 exacts | 460 000, 0--5, 6 000 H100 h, 92 % |
| Corpus — PubMed/PMC | 3 | 1 exact, 2 historiques/versionnés | 39 M ; 4,5 M ; 98 % anglais |
| Corpus — BioClinical ModernBERT | 1 | 1 exact | environ vingt jeux |
| Corpus — ressources françaises | 4 | 3 exacts, 1 versionné | ISTEX ; 31 000 ; 136 M ; 21 M |
| Corpus — terminologies | 5 | 1 exact, 4 versionnés | UMLS ; SNOMED ; ICD ; CCAM ; ATC |
| Corpus — EntiGraph | 2 | 2 exacts | 1,3 M vers 455 M et contexte expérimental |
| **Sous-total corpus** | **28** | **20 exacts, 8 versionnés** | |
| IE — PMSI | 1 | 1 non traçable | 30 M séjours/an |
| IE — benchmarks anglais | 4 | 4 exacts | BC5CDR, NCBI Disease, JNLPBA, BLURB |
| IE — benchmarks français | 4 | 4 exacts | QUAERO, CAS1, CAS2, E3C |
| IE — DrBenchmark | 1 | 1 exact | 20 tâches/12 jeux |
| IE — espaces de codes | 1 | 1 versionné/incohérent | 17 000/8 000/6 000 et conflit 19 000 |
| IE — longueur documentaire | 1 | 1 non traçable | 1 000--3 000 contre 512 |
| IE — FRACCO/FRASIMED | 2 | 1 exact, 1 arrondi fidèle | 1 301 ; environ 2 000 pour 2 051 |
| IE — GLiNER | 2 | 1 exact, 1 schématique | 300 M ; six scores illustratifs |
| IE — UniversalNER | 1 | 1 exact | 45 889 ; 13 020 ; écart de performance |
| **Sous-total IE** | **17** | **12 exacts, 1 fidèle, 1 versionné, 2 non traçables, 1 schématique** | |
| **TOTAL** | **85** | **66 exacts, 5 fidèles, 9 versionnés, 1 incorrect, 3 non traçables, 1 schématique** | |

## Ordre de correction conseillé

1. Shannon : deux coordonnées seulement, correction indiscutable.
2. PMSI : retirer le nombre tant qu'un champ, une année et une unité homogène ne sont pas choisis.
3. CIM-10 : harmoniser 17 000/19 000 avec une édition ou une formulation large.
4. GLiNER : ajouter « illustrative scores » ; aucun changement de dessin nécessaire.
5. PubMed/PMC, ISTEX et SNOMED : choisir entre statistiques datées et formulations résistantes au temps.
6. Longueurs de comptes rendus : citer un corpus/tokenizer ou retirer la plage numérique.

## Conclusion

La passe quantitative ne révèle pas une dérive générale des chiffres. Les tableaux GPT-3, l'équation de Chinchilla, les grands corpus, EntiGraph, les tailles des modèles biomédicaux et les principaux benchmarks sont bien retranscrits. Les faiblesses se concentrent dans trois zones classiques : une colonne prise dans la mauvaise variante d'une table historique, des statistiques institutionnelles non millésimées, et des ordres de grandeur cliniques sans unité ou source assez précise. Les changements minimaux ci-dessus permettent de conserver la narration tout en rendant les nombres beaucoup plus difficiles à attaquer.
