# Clinical Information Extraction - Draft

## Structure narrative

1. Intro -> pourquoi clinical IE, plan
2. NER fondamental -> ok ca marche, mais en biomed?
3. Biomedical & Clinical NER -> ok on extrait des entites, mais le codage c'est different
4. Medical Coding -> 17K labels, documents longs -> zero-shot?
5. Entity Linking & Normalization -> ok on normalise, mais sans supervision?
6. Zero-shot & Open NER -> prometteur mais pas de donnees cliniques
7. Synthetic Data for Clinical NLP -> solution a la rarete
8. Evaluation -> besoin benchmark unifie
9. Limites et transition

---

## 1. Introduction

- Clinical IE = extraire info structuree a partir de texte clinique non structure
- CDW (clinical data warehouses) en expansion dans les hopitaux
- Raghavan et al. (2014): 80% des entites manquent des donnees structurees -> le texte libre est la source principale
- PMSI en France: codage ICD-10 obligatoire pour chaque sejour (30M sejours/an, ATIH)
- Types de taches: NER, relation extraction, codage medical, entity linking, normalisation
- Pourquoi c'est central pour la these:
  - Part 3 = adapter les modeles pretrained aux taches cliniques
  - Ch.7 = zero-shot GLiNER avec ontologies
  - Ch.8 = donnees synthetiques cliniques
  - Ch.9 = combine les deux
- -> plan du chapitre

## 2. Named Entity Recognition

### Sequence Labeling
- BIO/BILOU tagging scheme
- CRF (Lafferty et al., 2001): conditional random fields, modele les dependances entre labels
- BiLSTM-CRF (Lample et al., 2016): neural sequence labeling, SOTA pre-BERT
- Transition: BERT change tout

### BERT-based NER
- Devlin et al. (2019): BERT + linear layer pour NER, simple et efficace
- Fine-tuning: pretrained encoder + classification head par token
- CRF layer optionnelle au-dessus de BERT (debat: ameliore ou pas?)
- Avantage: representations contextuelles, transfer learning

### Au-dela du token-level
- Span-based NER: enumerer les spans candidats, classifier chaque span
  - Avantage: gere mieux les entites imbriquees (nested entities)
- Probleme des entites imbriquees frequent en biomed:
  - "cancer du poumon droit" = [maladie [anatomie]]

-> ok le NER marche bien en general, mais le domaine biomedical a ses specificites

## 3. Biomedical & Clinical NER

### Benchmarks anglais
- BC5CDR (Li et al., 2016): chemical-disease relations, PubMed abstracts
- NCBI Disease (Dogan et al., 2014): disease mentions in PubMed
- JNLPBA (Collier & Kim, 2004): genes/proteins, GENIA corpus
- AnatEM (Pyysalo & Ananiadou, 2014): anatomical entity mentions
- ChemProt (Krallinger et al., 2017): chemical-protein interactions (relation extraction)
- GAD (Bravo et al., 2015): gene-disease associations
- Hallmarks of Cancer (Baker et al., 2016): cancer hallmark classification
- i2b2 shared tasks (Uzuner et al., 2010, 2011): clinical NER sur notes MIMIC
- -> BLURB benchmark (Gu et al., 2022): unifie plusieurs benchmarks biomed

### Benchmarks francais
- QUAERO (Neveol et al., 2014):
  - EMEA: notices medicamenteuses, 10 types UMLS
  - MEDLINE: titres d'articles scientifiques
  - Entites imbriquees
- CAS / DEFT 2020 (Cardon et al., 2020):
  - Cas cliniques francais
  - CAS1: pathologie, signes/symptomes
  - CAS2: anatomie, dose, examen, mode, moment, substance, traitement, valeur
- E3C (Magnini et al., 2021): corpus multilingue, cas cliniques, 1 seule classe (entite clinique)
- CLEF eHealth 2016 (Neveol et al., 2016):
  - Task 2: NER + normalisation sur QUAERO
  - Codage CIM-10 sur certificats de deces (CepiDC)
  - BRATeval comme outil d'evaluation officiel

### Specificites du texte clinique
- Style telegraphique, abreviations, fautes
- Negation, temporalite, incertitude
- Tres different du texte scientifique (PubMed) ou general (web)
- Donnees privees -> modeles hospitaliers non partageables

-> on a les benchmarks, mais le codage medical c'est pas juste du NER: c'est assigner des codes d'une ontologie a un document entier

## 4. Medical Coding

### Le probleme
- ICD coding: assigner des codes CIM-10 a un document clinique
- En France: PMSI, chaque sejour hospitalier doit etre code (DP, DAS, actes CCAM)
- Fait manuellement par des codeurs professionnels
- Label space enorme: ~17K codes CIM-10, ~8K codes CCAM
- Documents longs: comptes-rendus de sortie = souvent 1000-3000 tokens
- Distribution tres desequilibree: quelques codes frequents, longue traine de codes rares

### Approches
- CAML (Mullenbach et al., 2018, NAACL):
  - CNN + label-wise attention
  - Chaque code a son propre mecanisme d'attention
  - Premiere approche explainable pour ICD coding
  - DR-CAML: regularisation par descriptions de codes
- HyperCore (Cao et al., 2020, ACL):
  - Exploite la hierarchie ICD via embeddings hyperboliques (Poincare ball)
  - + graphe de co-occurrence entre codes
  - SOTA sur MIMIC-II/III
- PLM-ICD (Huang et al., 2022, ClinicalNLP@NAACL):
  - Premier a utiliser des pretrained LMs pour ICD coding
  - Label attention + segment pooling pour documents longs
  - Montre que meilleur encoder = meilleur codage
- MSMN (Yuan et al., 2022, ACL):
  - Exploite les synonymes UMLS pour chaque code ICD
  - Multi-synonym matching: representations de codes plus riches
  - Le texte clinique utilise des expressions variees pour un meme concept

### Long documents
- BERT limite a 512 tokens, insuffisant pour comptes-rendus
- Solutions: chunking, hierarchical models, Longformer
- PLM-ICD: segment pooling
- -> ModernBERT 8192 tokens aide mais pas suffisant pour les plus longs documents

-> le codage marche sur MIMIC (anglais), mais: 17K labels = impossible d'annoter pour chacun, et en francais les ressources sont rares -> besoin d'approches zero-shot

## 5. Entity Linking & Normalization

### Le probleme
- Entity linking = associer une mention textuelle a une entite dans une base de connaissances
- Normalisation = mapper des variantes terminologiques au concept canonique
- Exemple: "infarctus du myocarde", "IDM", "crise cardiaque" -> I21.9

### Approches
- SapBERT (Liu et al., 2021, NAACL):
  - Self-alignment pretraining sur synonymes UMLS (4M+ concepts)
  - Contrastive learning: synonymes = positifs, non-synonymes = negatifs
  - SOTA entity linking biomed sur 6 benchmarks
  - "One-model-for-all": un seul modele pour tous types d'entites
- CODER (Yuan et al., 2022):
  - Contrastive pretraining sur 87M triplets de relations UMLS
  - Relations + synonymes dans l'objectif contrastif
  - Medical term normalization
- BioSyn (Sung et al., 2020, ACL):
  - Bi-encoder + cross-encoder pour entity normalization
  - Marginal score aggregation
- GenBioEL (Yuan et al., 2022):
  - Generative entity linking: decoder genere le nom de l'entite
  - Alternative aux approches bi-encoder

### Lien avec le codage
- Entity linking peut etre vu comme une forme de codage: mention -> code
- Mais codage medical = document-level, entity linking = mention-level
- SapBERT et CODER exploitent UMLS mais principalement pour l'anglais

-> on sait normaliser des mentions isolees, mais comment extraire ET normaliser sans supervision pour des milliers de labels?

## 6. Zero-shot & Open NER

### Pourquoi zero-shot
- Labels medicaux evoluent (nouveaux codes ICD, nouveaux criteres d'essais cliniques)
- Impossible d'annoter pour chaque label
- Besoin de modeles qui generalisent a des labels non vus

### GLiNER (Zaratiana et al., 2024, NAACL)
- Bi-encoder dans un seul transformer bidirectionnel
- Entity types = input en langage naturel (pas labels fixes)
- Matching span-type par similarite dans un espace partage
- Bat ChatGPT sur zero-shot NER tout en etant beaucoup plus petit
- Pre-entraine sur Pile-NER (Universal NER)

### UniversalNER / Pile-NER (Zhou et al., 2024, ICLR)
- Distillation de ChatGPT: annotation de passages du Pile
- ~45K paires input-output, 13K types d'entites distincts
- Instruction-tuning de LLaMA sur ces donnees
- Bat ChatGPT de 7-9 F1 points en moyenne sur NER

### NuNER (Bogdanov et al., 2024, EMNLP)
- Foundation model NER compact (RoBERTa-base)
- Pre-entraine sur annotations GPT-3.5 de C4 (24.4M mots, 4.38M annotations, 200K types)
- Contrastive learning pour specialiser l'encoder
- Taille et diversite du dataset = cle de la performance

### LLMs for clinical NER
- Agrawal et al. (2022): LLMs pour clinical IE, prometteur
- Singhal et al. (2022): Med-PaLM, QA medicale
- Lehman et al. (2023): "We may have overestimated the impact of LLMs on clinical NLP"
  - BERT-type models still competitive for clinical tasks
  - LLMs trop gros pour deploiement hospitalier
  - Problemes de confidentialite avec APIs proprietaires

-> zero-shot NER prometteur, mais: GLiNER pre-entraine sur donnees generales, pas cliniques. Les LLMs sont trop gros. Les donnees cliniques sont privees -> comment entrainer sans donnees reelles?

## 7. Synthetic Data for Clinical NLP

### Le probleme de la rarete
- Donnees cliniques = privees (CNIL, HIPAA)
- Modeles hospitaliers non partageables
- Peu de datasets annotes publics en francais clinique

### LLM-as-annotator
- Distillation: LLM annote -> petit modele apprend
- Paradigme de FineWeb-Edu, UniversalNER, NuNER
- Applicable au domaine clinique

### Generation de notes cliniques synthetiques
- Tang et al. (2023): generation de notes cliniques avec GPT
- Synthetic NER: generer texte + annotations simultanement
- Avantage: alignement texte-annotation garanti
- Risque: style different des notes reelles

### Evaluation de la qualite
- Evaluation par medecins: coherence medicale, completude, style
- Comparaison aveugle synthetique vs reel

-> les donnees synthetiques sont une solution, mais comment evaluer correctement les modeles?

## 8. Evaluation

### Metriques
- seqeval: evaluation stricte entite-level, IOB2 scheme
  - Micro-average vs macro-average
  - Entite = match exact (type + boundaries)
- BRATeval (CLEF eHealth 2016): exact match sur character offsets
  - Avantage: independant du preprocessing et de la tokenisation
- Token-level classification: weighted F1 par token
  - Probleme: le token "O" (non-entite) domine -> scores gonfles
  - Influence du tokenizer sur le nombre de predictions

### Impact de la tokenisation
- Tokenizers differents = predictions differentes = scores differents
- SciBERT: 42% intersection avec BERT vocab
- Les metriques token-level sont biaisees par le tokenizer
- -> besoin d'evaluation independante du tokenizer

### Besoin d'un benchmark unifie
- Chaque papier utilise des datasets, metriques, et splits differents
- Pas de protocole standard pour le francais biomedical
- Comparaison entre modeles = difficile

-> evaluation pas standardisee, besoin de benchmarks unifies et de metriques independantes du tokenizer

## 9. Limites et transition

- Rarete des donnees cliniques: les textes sont prives, les modeles hospitaliers non partageables
  -> besoin d'alternatives publiques et de donnees synthetiques -> Ch.8
- Label space enorme: 17K codes ICD, 8K CCAM, impossible d'annoter pour chacun
  -> besoin d'approches zero-shot -> Ch.7
- Zero-shot NER existant = pre-entraine sur donnees generales, pas cliniques
  -> besoin d'adapter au domaine -> Ch.7, Ch.9
- Ontologies sous-exploitees dans le NER: GLiNER ignore la structure hierarchique des codes
  -> besoin d'integrer la structure RDF dans l'embedding des labels -> Ch.7
- Evaluation non standardisee: pas de benchmark unifie pour le francais biomed
  -> besoin d'evaluation independante du tokenizer -> TABIB (Ch.7? ou contribution transversale)
- Gap encoders vs decoders: BERT-type models restent competitifs pour les taches cliniques
  -> justification du choix des encoders dans la these

-> ce chapitre a couvert les taches de clinical IE: NER, codage, normalisation, et les defis specifiques du domaine clinique. Les chapitres suivants presentent nos contributions pour adresser ces gaps.

---

## References cles (non-these)

### NER fondamental
- Lafferty et al. (2001): CRF
- Lample et al. (2016): BiLSTM-CRF
- Devlin et al. (2019): BERT

### Biomedical NER benchmarks
- Li et al. (2016): BC5CDR
- Dogan et al. (2014): NCBI Disease
- Collier & Kim (2004): JNLPBA
- Pyysalo & Ananiadou (2014): AnatEM
- Krallinger et al. (2017): ChemProt
- Neveol et al. (2014): QUAERO
- Cardon et al. (2020): DEFT 2020 / CAS
- Magnini et al. (2021): E3C
- Neveol et al. (2016): CLEF eHealth 2016
- Gu et al. (2022): BLURB

### Medical Coding
- Mullenbach et al. (2018): CAML
- Cao et al. (2020): HyperCore
- Huang et al. (2022): PLM-ICD
- Yuan et al. (2022): MSMN

### Entity Linking
- Liu et al. (2021): SapBERT
- Yuan et al. (2022): CODER
- Sung et al. (2020): BioSyn

### Zero-shot NER
- Zaratiana et al. (2024): GLiNER
- Zhou et al. (2024): UniversalNER / Pile-NER
- Bogdanov et al. (2024): NuNER

### LLMs vs BERT for clinical
- Lehman et al. (2023): "We may have overestimated"
- Agrawal et al. (2022): LLMs for clinical IE

### French clinical
- FRACCO (Pignat et al., 2024): codage oncologie francais
- FRASIMED (Zaghir et al., 2023): adaptation fr de Cantemist/Distemist
- Raghavan et al. (2014): 80% info dans texte libre
