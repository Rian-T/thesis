# Audit de fidélité de l'état de l'art

Date : 19 juillet 2026  
Périmètre : `sources/related_works/language_modeling.tex`, `sources/related_works/corpus_annotation.tex`, `sources/related_works/clinical_ie.tex`  
Nature de l'audit : vérification des affirmations contre les articles primaires ; aucune modification des fichiers `.tex`.

## Verdict général

L'état de l'art est globalement solide, mais il contient plusieurs formulations qui ne sont pas défendables telles quelles. Les problèmes les plus sérieux ne sont pas des erreurs de détail : ils concernent la distinction entre DeepSeek-R1 et DeepSeek-R1-Zero, l'interprétation du chiffre de 42 % de SciBERT, la portée réelle de l'expérience de codage de Soroush et al., et la revendication d'absence de préentraînement d'encodeurs sur du texte généré depuis des ontologies.

Après une seconde passe contradictoire, je retiens :

- **8 corrections nécessaires** : le passage actuel est factuellement faux ou attribue à un article une conclusion que son protocole ne permet pas ;
- **10 qualifications fortement recommandées** : l'idée générale est juste, mais la formulation est trop absolue ou mélange des périmètres différents ;
- **plusieurs passages vérifiés comme fidèles**, listés en fin de rapport afin de ne pas donner une impression artificiellement négative.

Les corrections proposées ci-dessous cherchent systématiquement la formulation la plus courte et la moins exposée.

## Méthode

1. Lecture continue des trois fichiers, puis repérage de chaque affirmation quantitative, historique, comparative ou de nouveauté.
2. Contrôle des contextes de citation : 215 commandes de citation, correspondant à 158 clés distinctes.
3. Priorisation des passages à risque : « first », « strongest », « has not been studied », « do not exist », causalités tirées d'un chiffre, et comparaisons entre familles de modèles.
4. Lecture du texte intégral ou des sections méthodologiques des articles primaires pour les affirmations à risque.
5. Seconde passe contradictoire : recherche d'une interprétation sous laquelle le texte de la thèse resterait exact. Lorsqu'elle existe, le point est classé comme qualification plutôt que comme erreur.

Niveaux utilisés :

- **Nécessaire** : corriger avant dépôt.
- **Fortement recommandé** : la formulation actuelle peut être attaquée même si son intuition est bonne.
- **Mineur** : amélioration de précision, sans conséquence sur l'argument de la thèse.

## Corrections nécessaires

### LM-1 — Le Transformer original n'avait pas pour objectif général la prédiction du prochain token

- **Emplacement** : `language_modeling.tex:303-304`.
- **Texte actuel** : « The Transformer keeps the same goal, predicting the next token. »
- **Problème** : l'article de Vaswani et al. introduit un modèle encodeur-décodeur de transduction de séquences, évalué en traduction. Son décodeur est bien autorégressif, mais l'architecture complète n'est pas présentée comme un modèle de langage causal poursuivant simplement l'objectif précédent.
- **Source primaire** : [Vaswani et al., 2017, *Attention Is All You Need*](https://proceedings.neurips.cc/paper_files/paper/2017/file/3f5ee243547dee91fbd053c1c4a845aa-Paper.pdf), résumé et §3.
- **Correction minimale proposée** :

  > The Transformer replaces recurrence with attention. In its original encoder--decoder form, it was introduced for sequence transduction; decoder-only language models later adapted the same core mechanism to next-token prediction.

### LM-2 — DeepSeek-R1 et DeepSeek-R1-Zero sont confondus

- **Emplacement** : `language_modeling.tex:818-822`.
- **Texte actuel** : « DeepSeek-R1 [...] A model trained by reinforcement learning alone, with no supervised fine-tuning first [...] »
- **Problème** : la variante entraînée par RL sans SFT préalable est **DeepSeek-R1-Zero**. DeepSeek-R1 suit au contraire une procédure multi-étapes avec données de démarrage supervisées, RL, rejection sampling, SFT supplémentaire et seconde phase de RL.
- **Source primaire** : [DeepSeek-AI et al., 2025, article Nature](https://www.nature.com/articles/s41586-025-09422-z), sections « DeepSeek-R1-Zero » et « DeepSeek-R1 ».
- **Correction minimale proposée** :

  > DeepSeek-R1-Zero pushed the pure-RL variant to its limit: without supervised fine-tuning first, it developed behaviours such as self-checking and strategy revision. DeepSeek-R1 then added a multistage pipeline with cold-start data, rejection sampling, supervised fine-tuning, and further reinforcement learning; its reasoning behaviour was also distilled into smaller models.

### LM-3 — Le chiffre de 42 % de SciBERT ne mesure pas la proportion de mots découpés

- **Emplacements** : `language_modeling.tex:1059-1062` et `language_modeling.tex:1233-1238`.
- **Texte actuel** : 42 % de recouvrement entre vocabulaires, « so » / « therefore » plus de la moitié des mots scientifiques communs seraient découpés par le tokenizer général.
- **Problème** : SciBERT mesure le recouvrement entre deux vocabulaires WordPiece de 30 000 entrées. Cela ne donne ni la proportion de mots scientifiques segmentés, ni leur nombre moyen de sous-tokens. Une entrée absente du vocabulaire SciBERT peut elle-même être un sous-mot ; inversement, un mot peut être segmenté même si certaines de ses parties appartiennent aux deux vocabulaires.
- **Source primaire** : [Beltagy et al., 2019, *SciBERT*](https://aclanthology.org/D19-1371.pdf), §2 : « token overlap between BASEVOCAB and SCIVOCAB is 42% ».
- **Correction minimale proposée aux deux endroits** :

  > The two 30,000-entry vocabularies overlap by only 42%, showing that scientific and general-domain corpora produce substantially different inventories of frequent subwords.

  Supprimer toute déduction chiffrée sur « more than half of the common scientific words ».

### CA-1 — Le passage Meditron présente une ablation comme la recette du corpus final

- **Emplacement** : `corpus_annotation.tex:223-228`.
- **Texte actuel** : le corpus « used for Meditron » serait obtenu en notant les articles avec MeSH, type de publication, revue, récence et citations, puis en suréchantillonnant les mieux notés.
- **Ce qui est exact** : cette grille existe réellement dans l'annexe de l'article et sert à construire la variante **PMC Upsampled**. Les documents vétérinaires, rétractés et prépublications y sont notamment filtrés.
- **Ce qui ne l'est pas** : l'article compare cette variante à d'autres mélanges, constate qu'elle est globalement moins bonne que PMC + Replay, puis retient **GAP-Replay** pour le préentraînement final. GAP-Replay combine recommandations cliniques, résumés PubMed, articles PMC et 1 % de données générales de replay. Les 46,7 milliards de tokens sont le total d'entraînement de ce mélange final, pas le résultat démontré de la seule grille de scores.
- **Source primaire** : [Chen et al., 2023, *MEDITRON-70B*](https://arxiv.org/pdf/2311.16079), Table 1, §7.2, Table 8 et annexe B.4/Table 10.
- **Correction minimale proposée** :

  > Meditron's final GAP-Replay corpus combines clinical guidelines, PubMed abstracts, PMC papers, and a small general-domain replay component, for 46.7 billion training tokens. The authors also evaluated an article-level PMC upsampling scheme based on publication type, MeSH tags, journal, recency, and normalized citation count, but this ablation was not the final selected mixture.

  La phrase suivante sur la granularité article peut rester, mais elle doit viser explicitement cette **expérience de curation**, pas l'ensemble de GAP-Replay.

### CA-2 — BioOntoBERT contredit l'absence de préentraînement bidirectionnel sur du texte d'ontologie

- **Emplacements** : surtout `corpus_annotation.tex:625-632`; la phrase de `corpus_annotation.tex:591-593` est également ambiguë.
- **Texte actuel** : le texte généré depuis des graphes pour le préentraînement viserait les décodeurs anglais, et n'aurait pas été testé sur des encodeurs bidirectionnels.
- **Problème** : BioOntoBERT est un précédent direct. Onto2Sen produit des documents lexicaux et des phrases de relations à partir de **neuf ontologies biomédicales** ; un BERT-base est ensuite préentraîné par MLM sur environ 20 millions de mots générés, pendant 200 000 étapes, puis évalué sur MedMCQA.
- **Source primaire** : [Sahil et Kumar, 2023, *Leveraging Biomedical Ontologies to Boost Performance of BERT-Based Models for Answering Medical MCQs*](https://ceur-ws.org/Vol-3603/Paper9.pdf), résumé, §4.1.2, §4.2 et §5.
- **Contrôle bibliographique** : l'entrée `shashikumar2023bioontobert` de `thesis.bib` contient maintenant le bon titre et les bons auteurs, Sahil Sahil et P. Sreenivasa Kumar.
- **Correction minimale proposée** :

  > Direct ontology-to-text pretraining of a bidirectional encoder has been explored by BioOntoBERT, which continues BERT pretraining on sentences generated from nine biomedical ontologies. What remains untested is the narrower setting considered here: French national coding resources and the thesis's specific textbook-like generation pipeline.

### CA-3 — EntiGraph n'est pas une méthode de verbalisation d'une ontologie fournie en entrée

- **Emplacement** : `corpus_annotation.tex:628-630`.
- **Texte actuel** : « turning ontology graphs into text [...] as in EntiGraph ».
- **Problème** : EntiGraph reçoit un petit corpus de documents. Il en extrait des entités, forme un graphe de connaissances latent/inspiré par les entités, puis demande à un LLM de décrire les relations entre des groupes d'entités en restant conditionné par le document source. Il ne reçoit pas une ontologie existante comme ICD, CCAM ou ATC et n'en verbalise pas directement les arcs.
- **Source primaire** : [Yang et al., 2024/2025, *Synthetic Continued Pretraining*](https://arxiv.org/pdf/2409.07431), Figure 1 et §2.2.
- **Correction minimale proposée** :

  > EntiGraph generates relation-focused text from entities extracted from source documents; it does not verbalize a supplied medical ontology. Direct ontology verbalization should therefore be discussed separately, with BioOntoBERT as the closest encoder precedent.

### IE-1 — ClinicalMamba n'est pas une alternative architecturale au NER supervisé

- **Emplacement** : `clinical_ie.tex:167-172`.
- **Texte actuel** : après avoir expliqué que chaque classe cible demande des annotations, ClinicalMamba est présenté comme « one architectural alternative ».
- **Problème** : ClinicalMamba est un modèle de langage clinique **autorégressif et génératif**, préentraîné sur des notes longitudinales MIMIC avec une fenêtre allant jusqu'à 16k tokens. L'article l'évalue sur la modélisation du langage et des tâches cliniques longitudinales en few-shot ; il ne propose pas une architecture de span/sequence labeling qui résout le besoin d'annotations pour chaque classe de NER.
- **Source primaire** : [Yang et al., 2024, *ClinicalMamba*](https://aclanthology.org/2024.clinicalnlp-1.5.pdf), résumé, contributions et protocole expérimental.
- **Correction minimale proposée** : déplacer la mention vers la discussion des longs documents et écrire :

  > For long clinical sequences, ClinicalMamba explores a different backbone: an autoregressive state-space language model whose computation scales linearly with sequence length.

### IE-2 — L'article de Soroush et al. ne compare pas PLM-ICD/MSMN aux LLM sur le même codage documentaire

- **Emplacement** : `clinical_ie.tex:214-217`.
- **Texte actuel** : Soroush et al. montreraient que les LLM font mal le codage ; PLM-ICD et MSMN resteraient donc plus forts qu'un grand modèle générique.
- **Problème** : Soroush et al. donnent au modèle la **description officielle d'un code** et lui demandent de générer le code ICD-9-CM, ICD-10-CM ou CPT correspondant. Ils n'évaluent pas l'attribution multi-label de codes à une note clinique, n'utilisent pas le protocole MIMIC de PLM-ICD/MSMN, et déclarent explicitement ne pas tester notes réelles, RAG, outils ou fine-tuning. Le papier établit l'échec des LLM testés en *code querying*, pas la supériorité expérimentale directe de PLM-ICD ou MSMN.
- **Source primaire** : [Soroush et al., 2024, *Large Language Models Are Poor Medical Coders—Benchmarking of Medical Code Querying*](https://www.rama.mahidol.ac.th/ceb/sites/default/files/public/pdf/journal_club/2025/LLMs%20Are%20Poor%20Medical%20Coders.pdf), méthodes et limites.
- **Correction minimale proposée** :

  > Off-the-shelf LLMs were highly error-prone in Soroush et al.'s code-querying benchmark, where a model had to recover a billing code from its official description. This result does not directly compare them with document-level coding systems such as PLM-ICD or MSMN.

## Qualifications fortement recommandées

### LM-4 — Extrapolation des encodages positionnels

- **Emplacement** : `language_modeling.tex:334-343`.
- **Risque** : « both cope badly » met sur le même plan tables apprises et sinusoïdes ; « RoPE handles long and variable lengths well » promet une généralisation en longueur que RoPE ne garantit pas à lui seul.
- **Évidence** : le Transformer original choisit les sinusoïdes précisément parce qu'elles *peuvent* permettre l'extrapolation au-delà des longueurs d'entraînement. La littérature ultérieure montre néanmoins que l'application à des indices plus longs et la bonne généralisation empirique sont deux choses distinctes.
- **Sources** : [Vaswani et al., 2017](https://proceedings.neurips.cc/paper_files/paper/2017/file/3f5ee243547dee91fbd053c1c4a845aa-Paper.pdf), §3.5 ; [Su et al., *RoFormer*](https://arxiv.org/pdf/2104.09864).
- **Formulation robuste** :

  > Learned absolute tables have a fixed trained range unless they are extended or adapted. Functional encodings such as sinusoidal positions and RoPE can be evaluated at new indices, but reliable extrapolation beyond the training lengths is not guaranteed.

### LM-5 — Encodeur et décodeur : le masque n'est pas l'unique différence universelle

- **Emplacement** : `language_modeling.tex:382-393`.
- **Risque** : « The only difference » et « The two are built the same way » sont trop absolus. Les piles encodeur-only et décodeur-only partagent les mêmes sous-couches de base, mais les modèles encodeur-décodeur ajoutent une attention croisée ; les familles BERT/GPT diffèrent aussi par leurs objectifs et plusieurs choix d'implémentation.
- **Source** : [Vaswani et al., 2017](https://proceedings.neurips.cc/paper_files/paper/2017/file/3f5ee243547dee91fbd053c1c4a845aa-Paper.pdf), §3.1 : le décodeur original a une troisième sous-couche d'attention sur la sortie de l'encodeur.
- **Formulation robuste** :

  > Encoder-only and decoder-only stacks share the same core self-attention and feed-forward sublayers, but differ in their attention masks; encoder--decoder models additionally use cross-attention. Architecture and pretraining objective jointly separate these families.

### LM-6 — Un vérificateur RLVR peut être exploité

- **Emplacement** : `language_modeling.tex:773-774`.
- **Risque** : « it cannot be gamed » est faux. Une récompense déterministe évite l'approximation d'un reward model appris, mais un modèle peut exploiter une spécification, des tests, un parseur ou un vérificateur incomplets.
- **Source primaire récente** : [Helff et al., 2026, *LLMs Gaming Verifiers: RLVR can Lead to Reward Hacking*](https://arxiv.org/pdf/2604.15149), qui montre des sorties satisfaisant un vérificateur imparfait sans apprendre la règle demandée.
- **Formulation robuste** :

  > A rule-based verifier avoids relying on a learned reward model, but it can still be gamed when the checker is an incomplete proxy for the intended task.

### LM-7 — « Verifiable rewards do not exist for open-ended writing » est trop catégorique

- **Emplacement** : `language_modeling.tex:822-824`.
- **Risque** : l'écriture ouverte n'a généralement pas une unique correction déterministe, mais on peut construire des rubriques, contraintes automatiques ou évaluateurs partiels. Leur objectivité et leur robustesse sont simplement plus faibles.
- **Formulation robuste** :

  > Fully objective, deterministic rewards are much harder to define for open-ended writing, where no single automatic correctness check captures overall quality.

### LM-8 — « strongest biomedical and clinical encoder » dépasse les expériences publiées

- **Emplacements** : `language_modeling.tex:1072-1076` et `language_modeling.tex:1192-1195`.
- **Risque** : BioClinical ModernBERT rapporte de meilleurs résultats que les encodeurs comparés sur quatre tâches ; cela ne prouve pas une domination universelle sur toutes les tâches biomédicales et cliniques. « read a full clinical note » doit aussi être compris comme « de nombreuses notes » : 8192 tokens ne couvrent pas tous les documents possibles.
- **Source primaire** : [Sounack et al., 2025, *BioClinical ModernBERT*](https://arxiv.org/pdf/2506.10896), résumé et §6.
- **Contre-exemple de longueur** : le jeu i2b2 2014 reporté dans [Clinical ModernBERT](https://arxiv.org/pdf/2504.03964) contient des séquences jusqu'à 14 370 tokens.
- **Formulation robuste** :

  > BioClinical ModernBERT outperforms the biomedical and clinical encoders evaluated by its authors on four downstream tasks. Its 8192-token window can process many clinical notes without chunking, although longer records still require truncation or segmentation.

### CA-4 — Snomed2Vec ne se réduit pas à Node2Vec

- **Emplacement** : `corpus_annotation.tex:340-342`.
- **Risque** : l'article évalue trois familles sur SNOMED-CT/UMLS : Node2Vec, MetaPath2Vec et embeddings de Poincaré. La phrase actuelle donne l'impression que Snomed2Vec désigne uniquement l'application de Node2Vec.
- **Source primaire** : [Agarwal et al., 2019, *Snomed2Vec*](https://arxiv.org/pdf/1907.08650), contributions et §4.2.
- **Formulation robuste** :

  > Snomed2Vec evaluates Node2Vec, MetaPath2Vec, and Poincaré embeddings on a SNOMED-CT knowledge graph, with different methods favouring neighbourhood, relation-type, or hierarchical structure.

### CA-5 — Les langues autres que l'anglais ne sont pas « unexplored »

- **Emplacement** : `corpus_annotation.tex:589-590`.
- **Risque** : CODER, cité quelques lignes plus loin, est explicitement cross-lingue et prend en charge des synonymes UMLS en français, entre autres langues. Le déséquilibre anglophone est réel ; l'absence totale ne l'est pas.
- **Source primaire** : [Yuan et al., 2021/2022, *CODER*](https://arxiv.org/pdf/2011.02947), résumé et contributions.
- **Formulation robuste** :

  > Most work remains centred on English and UMLS; multilingual and non-UMLS settings are comparatively underexplored, although CODER provides a cross-lingual counterexample.

### CA-6 — La nouveauté sur les ontologies nationales doit être formulée comme résultat de recherche, pas comme absence absolue

- **Emplacements** : `corpus_annotation.tex:593-594` et `corpus_annotation.tex:625-632`.
- **État du contrôle** : je n'ai pas trouvé de préentraînement utilisant précisément les ressources françaises ATIH CIM-10, CCAM et ATC de la manière proposée par la thèse. BioOntoBERT et Clinical ModernBERT constituent cependant des précédents proches sur d'autres ontologies/codifications.
- **Risque** : « have not been used » et « has not been tested » sont des négations universelles impossibles à garantir par une revue non systématique.
- **Formulation robuste** :

  > We did not identify prior pretraining work that uses the French ATIH CIM-10 and CCAM resources in this way. Existing encoder precedents use other biomedical ontologies or code-description collections.

  Cette formulation préserve la nouveauté réellement utile : **ressources françaises + pipeline précis**, sans revendiquer l'absence de toute idée voisine.

### IE-3 — Le paragraphe de normalisation contredit sa propre description de CODER

- **Emplacement** : `clinical_ie.tex:267-272`, à comparer avec `clinical_ie.tex:254-257` et `corpus_annotation.tex:480-481`.
- **Risque** : le texte affirme que « these methods » traitent chaque concept isolément et ignorent les relations, alors que CODER est justement entraîné avec les synonymes **et les triplets de relation UMLS**.
- **Source primaire** : [Yuan et al., *CODER*](https://arxiv.org/pdf/2011.02947), résumé : similarités calculées à partir des termes et des triplets relationnels du graphe.
- **Formulation robuste** :

  > SapBERT and BioSyn rely mainly on synonym-level supervision, whereas CODER also incorporates UMLS relation triplets. Even CODER, however, does not encode every operational constraint of a target coding ontology, such as exclusions and local coding rules.

### IE-4 — La limite « GLiNER est entraîné sur le web général » oublie GLiNER-BioMed déjà cité

- **Emplacement** : `clinical_ie.tex:439-447`, après la présentation de GLiNER-BioMed à `clinical_ie.tex:304-307`.
- **Risque** : la critique est valable pour le GLiNER généraliste et UniversalNER, mais plus pour l'ensemble des « GLiNER and similar models ». La thèse cite elle-même une adaptation biomédicale entraînée pour combler ce domaine gap.
- **Source primaire** : [Yazdani et al., *GLiNER-BioMed*](https://academic.oup.com/bioinformatics/article/42/6/btag322/8690923).
- **Formulation robuste** :

  > Generalist models such as the original GLiNER and UniversalNER are trained largely on broad-domain data. GLiNER-BioMed partially addresses this mismatch, but open clinical NER still faces limited access to real clinical text and detailed ontology constraints.

## Points mineurs mais utiles

### LM-9 — « FLAN introduced the idea and the name »

`language_modeling.tex:676` peut être défendu comme raccourci sur la vague moderne d'instruction tuning à grande échelle, mais « introduced the idea » est une priorité historique large. La version inattaquable est :

> FLAN established the modern large-scale instruction-tuning recipe and popularized the term.

Les nombres associés — 137 milliards de paramètres, plus de 60 jeux d'entraînement et amélioration sur 20 des 25 jeux d'évaluation — sont conformes à l'article.

### IE-5 — NuNER : « matter more than any other choice »

`clinical_ie.tex:427-431` transforme une analyse expérimentale en loi générale. L'article conclut surtout que la taille des données et la diversité des types/annotations sont les facteurs les plus influents dans son cadre expérimental ; la diversité du texte paraît moins importante.

Formulation minimale :

> Its ablations identify training-set size and annotation diversity as the most influential factors in that setting.

Source : [Bogdanov et al., 2024, *NuNER*](https://aclanthology.org/2024.emnlp-main.660.pdf).

### IE-6 — Exemple exact de segmentation d'« échocardiographie »

`clinical_ie.tex:552-560` affirme trois pièces contre deux sans nommer les deux tokenizers. Cette comparaison ne vient pas de SciBERT et varie selon le checkpoint, la casse et la normalisation. Deux options sûres :

- nommer les modèles et reproduire réellement leurs sorties ;
- remplacer les nombres par « may split it into different numbers of subword units ».

Le point général — une métrique au niveau token dépend de la segmentation — reste valide. C'est seulement l'exemple quantifié qui n'est pas traçable.

## Passages contrôlés et jugés fidèles

Ces passages n'appellent pas de correction de fond :

- **FineWeb-Edu** : 460 000 annotations Llama-3-70B, score 0–5, classifieur léger fondé sur des embeddings, coût d'inférence annoncé et réduction de 15T à environ 1,3T tokens sont correctement retranscrits. Source : [Penedo et al., 2024](https://proceedings.neurips.cc/paper_files/paper/2024/file/370df50ccfdf8bde18f8f9c2d9151bda-Paper-Datasets_and_Benchmarks_Track.pdf).
- **DCLM** : l'entraînement du classifieur fastText à partir d'exemples positifs de type instruction/question-réponse et de pages web négatives, puis la conservation de la tranche la mieux scorée, est correctement résumé. « Resolved question-and-answer structure » reste une interprétation pédagogique plutôt qu'un libellé formel de l'article. Source : [Li et al., 2024](https://papers.neurips.cc/paper_files/paper/2024/file/19e4ea30dded58259665db375885e412-Paper-Datasets_and_Benchmarks_Track.pdf).
- **WebOrganizer** : taxonomie thème/format, distillation du classifieur et effets du mélange par domaines sont fidèles. Source : [Wettig et al., 2025](https://arxiv.org/pdf/2502.10341).
- **EntiGraph, description locale de la méthode** (`corpus_annotation.tex:525-531` et légende) : extraction d'entités depuis les documents, génération relationnelle conditionnée par la source et passage de 1,3M à 455M tokens sont exacts. Le problème apparaît uniquement lorsqu'EntiGraph est ensuite assimilé à la verbalisation d'une ontologie fournie.
- **SapBERT** : synonymes d'un même CUI rapprochés, concepts distincts séparés, modèle commun aux types d'entités et application au linking sont correctement résumés. Source : [Liu et al., 2021](https://aclanthology.org/2021.naacl-main.334/).
- **CODER, description positive** : l'ajout des triplets relationnels UMLS et la portée cross-lingue sont confirmés. Le problème est la généralisation ultérieure disant que ces méthodes ignorent les relations.
- **BioSyn** : combinaison de scores sparse/dense, marginalisation sur les synonymes et rafraîchissement des candidats difficiles sont fidèles. Source : [Sung et al., 2020](https://aclanthology.org/2020.acl-main.335.pdf).
- **HyperCore** : embeddings hyperboliques de la hiérarchie ICD et graphe de cooccurrences sont correctement décrits. Source : [Cao et al., 2020](https://aclanthology.org/2020.acl-main.282/).
- **PLM-ICD** : label attention et traitement segmenté des longs documents sont correctement présentés ; « first » est ambitieux mais cohérent avec le positionnement de l'article. Source : [Huang et al., 2022](https://aclanthology.org/2022.clinicalnlp-1.2/).
- **UniversalNER** : 45 889 paires, 240 725 entités, 13 020 types et avantage moyen annoncé sur ChatGPT sont correctement recopiés. Source : [Zhou et al., 2024](https://proceedings.iclr.cc/paper_files/paper/2024/file/34678d08b36076de986df95c5bbba92f-Paper-Conference.pdf).
- **E3C** : corpus multilingue de cas cliniques, résumés de cas PubMed et notices de médicaments/patient information leaflets est correctement caractérisé. Source : [Magnini et al., 2020](https://aclanthology.org/2020.clicit-1.30.pdf).
- **FRACCO et FRASIMED** : ordres de grandeur et nature synthétique/adaptée sont cohérents avec les articles cités.
- **Données cliniques synthétiques** : les résumés d'Ive et al., Chintagunta et al., Asclepius et Meoni et al. respectent les protocoles et la portée annoncée par les articles.
- **Meditron, résultats de modèle** dans `language_modeling.tex` : l'article affirme bien que Meditron-70B dépasse GPT-3.5 et Med-PaLM dans son évaluation. Ajouter « in the reported evaluation » serait prudent, mais il n'y a pas de contresens.

## Effet sur la revendication de nouveauté

La revendication large suivante n'est pas tenable :

> personne n'a préentraîné d'encodeur bidirectionnel sur du texte généré depuis une ontologie.

BioOntoBERT suffit à la réfuter. Clinical ModernBERT constitue aussi un précédent voisin : il continue un encodeur ModernBERT par MLM sur un mélange incluant des codes ICD/CPT et leurs descriptions transformées en représentations textuelles standardisées ([papier](https://arxiv.org/pdf/2504.03964), §3.2–3.3). Ce second papier est moins proche du pipeline de la thèse que BioOntoBERT, mais il renforce la nécessité de restreindre la revendication.

La revendication étroite suivante reste défendable au vu de la recherche effectuée :

> nous n'avons pas identifié de travail antérieur combinant les ressources nationales françaises ATIH/CIM-10 et CCAM avec ce pipeline précis de génération de texte de type manuel, afin de poursuivre le préentraînement d'un encodeur bidirectionnel français et de l'évaluer sur les tâches cliniques visées.

Cette version revendique la **combinaison concrète** — ressources, langue, forme de génération, architecture et évaluation — plutôt que la propriété générale « ontology-to-text + BERT », déjà antérieure.

## Ordre de correction conseillé

1. Corriger DeepSeek-R1/R1-Zero et les deux inférences SciBERT.
2. Réécrire le paragraphe de nouveauté autour de BioOntoBERT et séparer EntiGraph de la verbalisation d'ontologies.
3. Corriger Meditron pour distinguer GAP-Replay final de l'ablation PMC Upsampled.
4. Recaler ClinicalMamba et restreindre la conclusion tirée de Soroush et al.
5. Supprimer les absolus restants : « cannot be gamed », « do not exist », « strongest », « unexplored ».
6. Corriger les contradictions internes CODER/GLiNER-BioMed.

## Limites de cet audit

- Tous les contextes de citation ont été examinés, mais la lecture intégrale a été concentrée sur les affirmations à risque ; il ne s'agit pas d'une revue systématique enregistrée de chacune des 158 références.
- Une absence dans la littérature ne peut jamais être prouvée exhaustivement. C'est pourquoi les formulations négatives sont ramenées à « we did not identify » et au périmètre exact de la contribution.
- Les articles très récents de 2025–2026 sont parfois encore des prépublications. Les formulations comparatives doivent donc rester liées à leur protocole publié plutôt qu'à un classement universel.
