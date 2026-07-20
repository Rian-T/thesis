# Audit de fidélité de l'état de l'art — addendum de seconde passe

Date : 19 juillet 2026  
Instantané contrôlé : 21:35 CEST  
Périmètre : `sources/related_works/language_modeling.tex`, `sources/related_works/corpus_annotation.tex`, `sources/related_works/clinical_ie.tex` et, pour une discordance découverte pendant le contrôle, `thesis.bib`.  
Nature : nouveaux constats uniquement ; aucun fichier `.tex` ni fichier bibliographique modifié.

## Périmètre d'exclusion

Cet addendum ne répète aucun des 21 points du rapport principal `2026-07-19-related-work-fidelity-audit.md`, qu'ils aient déjà été corrigés ou non. Sont donc volontairement absents, entre autres, Transformer/next-token original, R1/R1-Zero, le 42 % de SciBERT, Meditron, BioOntoBERT, EntiGraph, ClinicalMamba, Soroush, CODER, GLiNER généraliste contre GLiNER-BioMed et l'exemple chiffré d'« échocardiographie ».

Les numéros de ligne ci-dessous correspondent à l'instantané suivant :

- `language_modeling.tex` : `82589bf75d05ff4f5eff3b35409ca42a265eb0ac6b4b34850fc25f69ca9be29b`
- `corpus_annotation.tex` : `32f12ee91eba273cc17db7722e314ac51772c1ff7c63778b91dc0643af955e99`
- `clinical_ie.tex` : `52e6ecf1570a9561dd193e41c68be717c0add200289d9f4e9ec13187acc2babb`
- `thesis.bib` : `01da90317718810f2f14099ba3a84e15a925806d8ea65330893507434408874d`

## Verdict

Après vérification primaire puis passe contradictoire, je retiens :

- **10 corrections nécessaires** : erreur factuelle, contradiction interne, confusion entre tâches, ou affirmation juridique trop catégorique ;
- **7 qualifications fortement recommandées** : intuition défendable, portée actuelle excessive ;
- **1 précision mineure** ;
- **plusieurs affirmations quantitatives nouvellement vérifiées comme exactes**, listées à la fin.

Le problème transversal le plus important est une confusion entre trois niveaux : reconnaître un **type d'entité** par NER ouvert, normaliser une **mention** vers un concept, et attribuer des **codes documentaires**. GLiNER traite le premier ; il ne résout pas automatiquement les deux autres.

## Corrections nécessaires

### ADD-BIB-1 — La notice CamemBERT-bio suit la métadonnée ACL, mais celle-ci contredit le PDF publié

- **Emplacement** : `thesis.bib:4508-4512` et conclusion antérieure du rapport `2026-07-19-bibcheck-whitelist-audit.md`.
- **Constat** : la notice locale donne deux auteurs, Rian Touchent et Éric de la Clergerie. La page ACL donne également ces deux auteurs, ce qui explique que `make checkbib` valide la notice. Cependant, la page de titre du PDF publié donne **Rian Touchent, Laurent Romary et Eric de La Clergerie**.
- **Pourquoi le contrôle automatique ne voit rien** : il compare la notice aux métadonnées structurées de l'ACL Anthology ; il ne relit pas la page de titre du PDF. La page ACL précise elle-même que le PDF fait autorité lors d'une demande de correction de métadonnées.
- **Sources primaires** : [PDF CamemBERT-bio, page de titre](https://aclanthology.org/2024.lrec-main.241.pdf) ; [notice ACL actuellement incohérente](https://aclanthology.org/2024.lrec-main.241/).
- **Action minimale proposée** : confirmer la liste d'auteurs publiée, puis, si le PDF est bien la référence finale, ajouter Laurent Romary dans `thesis.bib` et conserver une exception documentée au contrôle automatique ; idéalement demander aussi la correction de la notice ACL.

### ADD-LM-1 — Tous les modèles du chapitre n'estiment pas la probabilité du prochain token

- **Emplacement** : `language_modeling.tex:75-83`.
- **Texte actuel** : après la factorisation autorégressive, « Every model in this chapter estimates that one quantity ».
- **Problème** : cette définition convient aux modèles autorégressifs, mais le chapitre traite ensuite BERT et le masked language modeling, qui prédisent des tokens masqués à partir du contexte gauche **et droit**, ainsi que d'autres objectifs d'encodeurs. BERT est donc un contre-exemple interne immédiat.
- **Source primaire** : [Devlin et al., 2019, *BERT*](https://arxiv.org/pdf/1810.04805), §3.1.
- **Correction minimale proposée** :

  > For an autoregressive language model, the chain rule reduces sequence probability to next-token conditionals. The chapter later considers bidirectional encoders trained with different self-supervised objectives, notably masked-token prediction.

### ADD-LM-2 — Mikolov 2010 n'est pas la première utilisation réussie d'un RNN comme modèle de langage

- **Emplacement** : `language_modeling.tex:205-208`.
- **Texte actuel** : l'idée aurait été « first made to work as a language model » par Mikolov et al. en 2010.
- **Problème** : Elman entraînait dès 1990 un réseau récurrent simple à prédire le mot suivant dans des séquences de phrases artificielles. Mikolov et al. ont établi une recette RNNLM compétitive à une autre échelle ; ils n'ont pas réalisé la première démonstration de modélisation du langage récurrente.
- **Sources primaires** : [Elman, 1990, *Finding Structure in Time*](https://doi.org/10.1207/S15516709COG1402_1), notamment l'expérience où chaque mot doit prédire le suivant ; [Mikolov et al., 2010](https://www.isca-archive.org/interspeech_2010/mikolov10_interspeech.html).
- **Correction minimale proposée** :

  > Simple recurrent networks were already used for next-word prediction by Elman in 1990. Mikolov et al. later established competitive RNN language modelling on substantially larger natural-language data.

  Ajouter une entrée bibliographique pour Elman 1990 ; la référence `rnn_origins` actuelle est un chapitre général de Rumelhart et McClelland, pas la source directe de cette expérience linguistique.

### ADD-LM-3 — « The two dedicated French biomedical encoders » omet CamemBERT-bio et rend fausse la conclusion « open question »

- **Emplacement** : `language_modeling.tex:1091-1103`.
- **Texte actuel** : les deux encodeurs biomédicaux français dédiés seraient DrBERT et AliBERT, tous deux entraînés from scratch ; la possibilité de réussir une adaptation depuis un modèle français général resterait ouverte.
- **Problème** : CamemBERT-bio est précisément un encodeur biomédical français dédié obtenu par continual pretraining de CamemBERT. Son article rapporte +2,54 points de F1 en moyenne sur les tâches étudiées. Même si la contribution est détaillée plus tard dans la thèse, la formulation universelle et l'« open question » au présent ne sont plus exactes.
- **Source primaire** : [Touchent, Romary et de La Clergerie, 2024, *CamemBERT-bio*](https://aclanthology.org/2024.lrec-main.241.pdf), résumé et §3–4.
- **Correction minimale proposée** :

  > DrBERT and AliBERT are two French biomedical encoders trained from scratch. CamemBERT-bio, presented later in this thesis, provides the continual-pretraining counterexample: it adapts CamemBERT on biomed-fr and improves the evaluated French biomedical NER tasks.

  Si l'objectif narratif est de ne pas annoncer les résultats avant la partie Contributions, remplacer l'« open question » par une transition explicitement temporelle : « This was the question addressed by CamemBERT-bio in Chapter ... ».

### ADD-CA-1 — L'UMLS n'est pas une ontologie homogène où chaque concept possède tous les champs annoncés

- **Emplacement** : `corpus_annotation.tex:282-287`.
- **Problèmes** :

  1. la NLM nomme le composant principal **UMLS Metathesaurus**, pas « the meta-ontology » ;
  2. il agrège et préserve les informations de vocabulaires sources hétérogènes : cela ne garantit pas que **chaque** concept possède synonymes, hiérarchie, relations associatives **et** définition ;
  3. « current releases » n'est pas versionné. Pour 2026AA, la NLM annonce 3 530 466 concepts, 14 905 974 noms distincts, 18 064 970 AUIs et 195 sources contribuant des noms. « About 189 sources » et « over 15 million unique concept names » mélangent donc des millésimes ou des unités.
- **Sources officielles** : [présentation du Metathesaurus par la NLM](https://www.nlm.nih.gov/research/umls/knowledge_sources/metathesaurus/index.html) ; [fichiers et champs disponibles](https://www.nlm.nih.gov/research/umls/new_users/online_learning/Meta_006.html) ; [statistiques 2026AA](https://www.nlm.nih.gov/research/umls/knowledge_sources/metathesaurus/release/statistics.html).
- **Correction minimale proposée** :

  > The UMLS Metathesaurus integrates nearly 200 source vocabularies and links names that express the same concept. It preserves terms and the relations or definitions supplied by those sources, whose coverage varies by concept. In the 2026AA release it contains about 3.53 million concepts and 14.91 million distinct concept names (18.06 million AUIs) from 195 name-contributing sources.

### ADD-IE-1 — La section utilise les codes ICD comme s'ils étaient des types d'entités de NER ouvert

- **Emplacements** : `clinical_ie.tex:275-290`, `clinical_ie.tex:439-446` et `clinical_ie.tex:599-610`.
- **Problème** : un type GLiNER tel que `disease` ou `drug name` est une catégorie de spans. Un code ICD est un identifiant de concept ou une étiquette documentaire. Reconnaître le span « infarctus du myocarde » comme maladie ne le normalise pas vers un code précis et n'attribue pas non plus l'ensemble des codes d'un séjour. Le nombre de codes ICD ne démontre donc pas, à lui seul, le besoin de milliers de types de NER.
- **Évidence primaire** : GLiNER est entraîné à faire correspondre des spans à des **entity types** ([article, §2](https://aclanthology.org/2024.naacl-long.300.pdf)). CAML et PLM-ICD prédisent au contraire directement un ensemble de codes depuis un document ([CAML](https://aclanthology.org/N18-1100.pdf) ; [PLM-ICD](https://aclanthology.org/2022.clinicalnlp-1.2.pdf)).
- **Correction minimale proposée** : séparer explicitement les motivations :

  > Open NER addresses unseen or user-specified entity types. Mapping a recognized mention to an ICD/CCAM concept is normalization, while assigning encounter-level codes is document-level multi-label classification. Open NER can support these pipelines but does not by itself solve zero-shot coding over thousands of concepts.

  Remplacer aussi « accuracy drops ... especially on rare codes » par « performance may drop on rare clinical entity types » sauf si une expérience de codage par GLiNER est citée.

### ADD-IE-2 — GLiNER n'est pas un bi-encodeur

- **Emplacement** : `clinical_ie.tex:575-580`.
- **Texte actuel** : « GLiNER-style bi-encoders ».
- **Problème** : le GLiNER original concatène les prompts de types et le texte dans une séquence unifiée, traitée par **un** transformeur bidirectionnel. Il ne possède pas deux encodeurs indépendants de type texte/étiquette. La description correcte figure d'ailleurs déjà à `clinical_ie.tex:294-300` et dans le TikZ.
- **Source primaire** : [Zaratiana et al., 2024, Figure 2 et §2.1](https://aclanthology.org/2024.naacl-long.300.pdf).
- **Correction minimale proposée** : remplacer par « GLiNER-style span--type matching models » ou « joint span--type encoders ».

### ADD-IE-3 — Chez Meoni et al., le texte privé reste dans la boucle privée de scoring

- **Emplacement** : `clinical_ie.tex:503-505`.
- **Texte actuel** : les auteurs « keep the private text out of the loop » puis scorent les candidats contre les vrais rapports.
- **Problème** : la seconde moitié contredit la première. Les mots-clés sont déclarés privacy-safe, mais ils sont extraits de rapports réels ; un petit sous-ensemble manuellement anonymisé sert au fine-tuning initial ; surtout, le modèle de score doit être hébergé dans l'établissement clinique pour comparer rapports synthétiques et rapports privés. Ce qui ne sort pas est le **contenu** des rapports, pas leur participation à la boucle.
- **Source primaire** : [Meoni et al., 2024](https://aclanthology.org/2024.cl4health-1.14.pdf), résumé, §2 et §3–4.
- **Correction minimale proposée** :

  > Meoni et al. keep real reports inside a private evaluation environment. A generator uses privacy-safe keywords and a small manually anonymized seed, while synthetic candidates are scored against real reports by a scorer hosted in the clinical institution.

### ADD-IE-4 — DrBenchmark réfute l'absence de tout benchmark ou protocole partagé français

- **Emplacements** : `clinical_ie.tex:564-582` et surtout `clinical_ie.tex:619-622`.
- **Contradiction interne** : `clinical_ie.tex:149-153` présente correctement DrBenchmark comme le premier benchmark français unifié, avec vingt tâches sur douze jeux. La conclusion affirme ensuite qu'« There is no shared benchmark for French biomedical natural language processing ».
- **Évidence primaire** : DrBenchmark se présente comme le premier benchmark public français de compréhension biomédicale, avec 20 tâches et un protocole automatisé commun ; ses tableaux couvrent 12 jeux de données. Son périmètre expérimental est toutefois celui de MLM BERT-like, pas de toutes les architectures ni d'une évaluation caractère universelle. [Labrak et al., 2024](https://aclanthology.org/2024.lrec-main.478.pdf), résumé, contributions, Tables 1–2 et §4.
- **Correction minimale proposée** :

  > DrBenchmark provides a shared protocol for twenty French biomedical language-understanding tasks, primarily for BERT-like masked language models. What remains missing is a protocol that compares the broader set of clinical NER, normalization and coding architectures considered here under a common character-level evaluation.

### ADD-IE-5 — Un modèle entraîné sur des données personnelles n'a pas automatiquement le même statut que son corpus

- **Emplacements** : `language_modeling.tex:1267-1273`, `corpus_annotation.tex:259-264`, `clinical_ie.tex:455-461` et `clinical_ie.tex:592-597`.
- **Texte actuel** : un modèle entraîné dans un hôpital « cannot be shared » et « Models and their training corpora fall under the same rules ».
- **Problème** : le risque de mémorisation et les contraintes de gouvernance sont réels, mais la conclusion juridique est absolue. Le Comité européen de la protection des données demande d'évaluer **au cas par cas** si un modèle est anonyme, notamment selon la possibilité d'identifier des personnes ou d'extraire leurs données par requêtes. Modèle et corpus ne sont donc ni automatiquement équivalents, ni automatiquement librement partageables.
- **Source officielle** : [avis 28/2024 du CEPD sur les modèles d'IA](https://www.edpb.europa.eu/news/edpb-opinion-on-ai-models-gdpr-principles-support-responsible-ai_fr), notamment la règle d'analyse au cas par cas.
- **Correction minimale proposée** :

  > Models trained on patient records may retain personal information and can remain subject to privacy, contractual and institutional constraints. Whether a model is sufficiently anonymous and shareable requires a case-by-case technical and legal assessment; it cannot be inferred solely from the location of training.

## Qualifications fortement recommandées

### ADD-LM-4 — EWC est une méthode classique, pas « the standard remedy » du continual pretraining moderne

- **Emplacement** : `language_modeling.tex:900-914`.
- **Risque** : EWC a été introduit pour l'apprentissage séquentiel de tâches et constitue une famille de régularisation importante. Le présenter comme le remède standard juste avant un passage sur l'adaptation de LLM donne une portée qu'il n'a pas dans les travaux cités ; l'article d'Ibrahim utilisé ensuite établit plutôt replay et gestion du learning rate.
- **Sources** : [Kirkpatrick et al., 2017](https://doi.org/10.1073/pnas.1611835114) ; [Ibrahim et al., 2024](https://arxiv.org/pdf/2403.08763).
- **Formulation robuste** :

  > A classic regularization remedy is elastic weight consolidation. At current LLM pretraining scales, replay and learning-rate scheduling are among the more directly validated strategies.

### ADD-LM-5 — Le résultat d'Ibrahim et al. est extrapolé au-delà de ses deux tailles et deux changements de distribution

- **Emplacement** : `language_modeling.tex:937-945`.
- **Ce qui est exact** : re-warm, re-decay et replay ; modèles de 405 M et 10 B ; performance moyenne proche du réentraînement avec moins de calcul.
- **Portée réelle** : transformeurs decoder-only, deux changements de distribution ; l'expérience à 10 B porte sur le changement anglais-vers-anglais, tandis que le changement anglais-vers-allemand fort est étudié à 405 M. Le papier parle de performance similaire **en moyenne**, pas d'identité universelle de tous les résultats.
- **Source primaire** : [Ibrahim et al., 2024](https://arxiv.org/pdf/2403.08763), contributions, Table 4 et conclusion.
- **Formulation robuste** :

  > In those decoder-only settings, the recipe approached the joint-training baseline on average validation loss and evaluation metrics while using less compute.

### ADD-LM-6 — Dorfner et al. ne permettent pas d'attribuer la différence à l'architecture encodeur/décodeur

- **Emplacement** : `language_modeling.tex:1119-1128`.
- **Risque** : la thèse oppose un « default win » des encodeurs à un risque propre aux décodeurs, puis demande pourquoi « the two architectures » se comportent différemment. Or Dorfner et al. évaluent des LLM biomédicaux génératifs contre leurs bases généralistes ; ils n'ont pas de contrôle encodeur. DrBenchmark montre en outre une image mixte côté encodeurs : aucun modèle ne domine toutes les tâches et les généralistes restent parfois compétitifs.
- **Sources primaires** : [Dorfner et al., 2024](https://arxiv.org/pdf/2408.13833) ; [DrBenchmark](https://aclanthology.org/2024.lrec-main.478.pdf).
- **Formulation robuste** :

  > Domain-adapted encoders often improve extraction benchmarks, whereas this independent evaluation found several specialized decoder LLMs weaker than their general bases. Because model families, objectives, data and evaluation protocols differ, these studies do not isolate architecture as the cause.

### ADD-CA-2 — RDF, OWL et SKOS sont des langages possibles, pas les formats natifs universels des ressources décrites

- **Emplacement** : `corpus_annotation.tex:308-323`.
- **Risque** : « Ontologies are published in a small set of standard formats defined by the W3C » est trop général. L'UMLS présenté juste avant est notamment distribué en RRF. SKOS fournit des propriétés de labels et de relations de connaissance ; il ne garantit pas qu'une ressource donnée contienne exclusions, complications, traitements ou liens inter-ontologies.
- **Sources officielles** : [NLM, formats RRF de l'UMLS](https://www.nlm.nih.gov/research/umls/new_users/online_learning/Meta_006.html) ; [recommandation W3C SKOS](https://www.w3.org/TR/skos-reference/).
- **Formulation robuste** :

  > Many ontologies and knowledge-organization systems can be represented in RDF, OWL or SKOS, while clinical terminologies may also be distributed in resource-specific formats. These languages can encode labels and relations when the source provides them; they do not imply that every resource contains every relation discussed below.

### ADD-IE-6 — NER → linking → agrégation n'est pas le pipeline typique de tous les systèmes de codage

- **Emplacement** : `clinical_ie.tex:244-250`.
- **Risque** : le pipeline décrit est possible et le linking peut aider le codage, mais les systèmes phares présentés quelques paragraphes plus tôt — CAML, PLM-ICD, MSMN — font principalement de la classification multi-label directe au niveau du document. Ils n'agrègent pas nécessairement des mentions préalablement normalisées.
- **Sources primaires** : [CAML](https://aclanthology.org/N18-1100.pdf), §3 ; [PLM-ICD](https://aclanthology.org/2022.clinicalnlp-1.2.pdf), Figure 1 et §3.
- **Formulation robuste** :

  > Entity linking can be used as a component of coding pipelines. Many leading ICD coding systems instead predict document-level labels directly from the note, without an explicit NER-and-linking stage.

### ADD-IE-7 — Les études citées ne montrent pas que les données synthétiques remplacent les données réelles en général

- **Emplacement** : `clinical_ie.tex:493-512`.
- **Risque** : les résultats d'Ive, Chintagunta et Asclepius sont encourageants dans leurs tâches et protocoles respectifs. La conclusion « generated data can replace real data » transforme ces résultats localisés en propriété générale, malgré les limites énumérées dans le même paragraphe.
- **Formulation robuste** :

  > These studies show that generated data can partially substitute for, or augment, real data in the evaluated settings; they do not establish equivalence across clinical tasks, institutions or rare cases.

### ADD-IE-8 — Une métrique token-level n'est dépendante du tokenizer que sous certains protocoles d'alignement

- **Emplacement** : `clinical_ie.tex:553-581`.
- **Risque** : le problème existe lorsque chaque sous-token du tokenizer propre au modèle reçoit une cible et compte dans le score — précisément le protocole reproduit dans l'article CamemBERT-bio. Mais ce n'est pas une propriété de toute évaluation « token-level » : on peut aligner les sorties sur des mots de référence, ignorer les sous-tokens secondaires, ou remapper les spans vers les offsets originaux. GLiNER, par exemple, utilise le premier sous-token pour représenter chaque mot et évalue des spans exacts.
- **Sources primaires** : [CamemBERT-bio, §5](https://aclanthology.org/2024.lrec-main.241.pdf) ; [GLiNER, §2.1 et §3.4](https://aclanthology.org/2024.naacl-long.300.pdf).
- **Formulation robuste** :

  > Scores become tokenizer-dependent when each model's own subword units are labelled and scored directly. Word-aligned or character-offset evaluation can avoid this direct dependence, provided predictions are mapped back to a common reference representation.

  La proposition d'une évaluation caractère reste parfaitement défendable ; c'est son statut de seule manière de comparer équitablement qui doit être atténué.

## Précision mineure

### ADD-LM-7 — GQA ne concerne pas toutes les tailles de Llama 2

- **Emplacement** : `language_modeling.tex:1165-1168`.
- **Texte actuel** : GQA est utilisé dans « models such as Llama-2 and Mistral ».
- **Nuance** : Mistral 7B utilise bien GQA. Le papier Llama 2 spécifie GQA pour les configurations 34B et 70B, mais pas pour 7B et 13B ; parmi les checkpoints finalement diffusés, 70B est donc celui qui l'emploie. La formulation par nom de famille est ambiguë, pas entièrement fausse.
- **Sources primaires** : [Llama 2](https://arxiv.org/abs/2307.09288) ; [Mistral 7B](https://arxiv.org/abs/2310.06825).
- **Correction minimale proposée** : « used in larger Llama-2 configurations (34B and 70B) and in Mistral 7B » ; ou, si l'on ne parle que des checkpoints diffusés, « Llama-2 70B and Mistral 7B ».

## Contrôles nouveaux ne révélant pas d'erreur

Pour éviter un audit orienté uniquement vers les anomalies, les affirmations suivantes ont été relues et sont conformes :

- les résultats GPT-3 sur l'addition à deux chiffres et TriviaQA correspondent aux tableaux de l'article ;
- Xie et al. annoncent bien des stratégies dépassant le continual pretraining non filtré avec 10 % des données et sans dégradation rapportée sur les tâches générales ;
- Guo et al. rapportent bien 36,2 % → 40,7 % avec 40 % du budget de calcul dans le cadre décrit ;
- Dorfner et al. rapportent bien environ 30 % pour OpenBioLLM-8B contre 64,3 % pour Llama-3-8B sur le sous-ensemble NEJM utilisé ; c'est l'inférence causale encodeur/décodeur, pas ce nombre, qui doit être qualifiée ;
- DrBenchmark contient bien 20 tâches issues de 12 jeux de données ;
- le lien entre ModernBERT et MosaicBERT est réel : le code FlexBERT part d'une base MosaicBERT révisée et reprend notamment son objectif MLM à 30 %. « Direct foundation » est un raccourci appuyé, mais je ne le classe pas comme erreur car ModernBERT documente explicitement cette filiation.

## Ordre de correction conseillé

1. Séparer NER ouvert, normalisation et codage (`ADD-IE-1`) ; c'est la confusion qui affecte le plus l'argument scientifique.
2. Corriger les contradictions internes immédiatement visibles : prochain token pour tous les modèles (`ADD-LM-1`), CamemBERT-bio absent (`ADD-LM-3`), GLiNER « bi-encoder » (`ADD-IE-2`) et absence de benchmark malgré DrBenchmark (`ADD-IE-4`).
3. Corriger Meoni (`ADD-IE-3`) et les formulations juridiques absolues (`ADD-IE-5`).
4. Résoudre la discordance d'auteurs CamemBERT-bio (`ADD-BIB-1`) ; `make checkbib` ne peut pas la résoudre tant que la notice ACL contredit son propre PDF.
5. Corriger l'antériorité RNN (`ADD-LM-2`) et la description/version de l'UMLS (`ADD-CA-1`).
6. Appliquer les qualifications restantes, qui peuvent presque toutes être faites en une ou deux phrases sans modifier le plan du chapitre.

## Conclusion de la seconde passe

Les nouveaux problèmes ne remettent pas en cause la structure générale de l'état de l'art. Ils se concentrent surtout dans les phrases de synthèse : généralisation d'un protocole local, passage d'une tâche à une autre, ou conclusion universelle à partir d'une étude plus étroite. Les corrections minimales proposées conservent l'argument de la thèse tout en supprimant les prises faciles pour un rapporteur.
