# Plan du manuscrit - Draft

## Introduction

> *Comment adapter les modèles de langue au domaine clinique sans données cliniques sensibles ?*

---

## Part 1: Building a Biomedical Corpus

> *Où trouver du texte biomédical public pour commencer ?*

### Ch. 1: Collecting Biomedical Text
- **Publication:** CamemBERT-bio (LREC-COLING 2024)
- **Contenu:** biomed-fr : 413M mots (ISTEX, CLEAR, E3C)
- **Résultat:** Premier corpus français, +2.5 F1 sur NER

> *Mais tout ce texte est-il vraiment utile ? Quels sont les risques du filtrage automatique ?*

### Ch. 2: Filtering by Quality Signals
- **Publication:** GAPeron (ACL 2026) - partie BiaHS
- **Contenu:**
  - Annotation LLM pour scorer la qualité éducative
  - Benchmark in a Haystack : les filtres neuronaux amplifient la contamination
- **Résultat:** Méthode pour détecter le risque de contamination

> *Comment trouver spécifiquement du contenu clinique caché dans des articles scientifiques ?*

### Ch. 3: Detecting Content Types
- **Publication:** Biomed-Enriched (ACL 2026)
- **Contenu:**
  - 91.6% des articles PMC mélangent plusieurs types de contenu
  - Annotation paragraph-level pour extraire 2M de cas cliniques
- **Résultat:** Même perf avec 1/3 des tokens

---

## Part 2: Pretraining Language Models

> *On a un bon corpus. Comment l'utiliser pour adapter un modèle ?*

### Ch. 4: Domain Adaptation
- **Publication:** CamemBERT-bio (LREC-COLING 2024)
- **Contenu:**
  - Continual pretraining : simple et efficace
  - 32× moins de CO2 que DrBERT
- **Résultat:** +2.5 F1, modèle public utilisable par tous les hôpitaux

> *Les architectures ont évolué. Peut-on profiter de Flash Attention et du contexte long pour les documents cliniques ?*

### Ch. 5: Modern Architectures for Long Documents
- **Publication:** ModernCamemBERT-bio (COLM 2026)
- **Contenu:**
  - Flash Attention, RoPE, contexte 8192 tokens
  - Les comptes rendus cliniques sont longs → crucial pour codage CIM-10 (FRACCO)
  - CLM→decay, analyse de l'hystérésis positionnelle
- **Résultat:** Meilleure perf sur documents longs

> *Peut-on aussi injecter de la connaissance structurée pendant le pretraining ?*

### Ch. 6: Knowledge-Enriched Pretraining
- **Publication:** Ontobook (Clinical NLP 2026)
- **Contenu:**
  - Reformulation LLM pour intégrer des ontologies (CIM-10, SNOMED)
  - Pretraining enrichi de knowledge sans annotations manuelles

---

## Part 3: Adapting to Clinical Tasks

> *On a un bon modèle pretrained, mais comment l'utiliser avec très peu d'annotations ?*

### Ch. 7: Zero-Shot Clinical IE with GLiNER
- **Publication:** MCB-bio-gliner (BioNLP 2026)
- **Contenu:**
  - Architecture GLiNER pour extraction d'entités
  - Zero-shot / few-shot quand peu de données annotées

> *Nos modèles marchent bien sur le biomédical, mais moins bien sur le clinique. Comment améliorer les perfs cliniques sans données cliniques ?*

### Ch. 8: Scientific-to-Clinical Transfer
- **Publication:** À définir
- **Contenu:**
  - Reformulation d'articles scientifiques en style clinique
  - Améliore les perfs cliniques sans jamais voir de vrais documents cliniques

> *Les perfs en coding (CIM-10, SNOMED) restent faibles. Peut-on exploiter directement les ontologies pour améliorer ça ?*

### Ch. 9: Knowledge-Aware Bi-Encoders
- **Publication:** À définir
- **Contenu:**
  - Pretraining bi-encodeur avec RDF CIM-10, SNOMED
  - Exploiter la structure des ontologies pour le coding/retrieval

---

## Conclusion

> *Réponse à la question initiale : oui, on peut exploiter les données publiques de manière intelligente (filtrage, extraction de cas cliniques, knowledge injection) pour créer des modèles cliniques sans données sensibles.*

---

## Résumé des publications

| Publication | Venue | Statut | Chapitres |
|-------------|-------|--------|-----------|
| CamemBERT-bio | LREC-COLING 2024 | Publié | Ch. 1, 4 |
| GAPeron | ACL 2026 | Soumis | Ch. 2 |
| Biomed-Enriched | ACL 2026 | Soumis | Ch. 3 |
| ModernCamemBERT-bio | COLM 2026 | À écrire | Ch. 5 |
| Ontobook | Clinical NLP 2026 | À finaliser | Ch. 6 |
| MCB-bio-gliner | BioNLP 2026 | À faire | Ch. 7 |

## Fil narratif

**Part 1 - Corpus:**
1. Collecter → mais c'est de bonne qualité ?
2. Filtrer qualité → mais où est le clinique ?
3. Détecter types → extraire cas cliniques

**Part 2 - Pretraining:**
1. Adapter classique → mais architectures modernes ?
2. Moderniser (long context) → mais knowledge ?
3. Enrichir avec ontologies

**Part 3 - Adaptation:**
1. Peu d'annotations → GLiNER zero-shot
2. Gap biomédical/clinique → Transfer par reformulation
3. Mauvais en coding → Ontologies dans le pretraining

---

## Figures, Tables & Key Points par Publication

### CamemBERT-bio (Ch.1 + Ch.4)

**FIGURES/TABLES:**
- Table composition biomed-fr (ISTEX 276M, CLEAR 73M, E3C 64M = 413M mots)
- Table NER F1 scores (+2.54 avg vs CamemBERT)
- Table carbon emissions (0.8 kg CO2 vs DrBERT 26.11 kg = 32× moins)

**KEY POINTS:**
- Premier corpus FR biomédical public (413M mots, 2.7 GB)
- Continual pretraining: 39h sur 2×V100, 50k steps
- +2.5 F1 avg sur 5 NER benchmarks (CAS1, CAS2, EMEA, E3C, MEDLINE)
- 45% overlap vocabulaire général/spécialisé

---

### GAPeron (Ch.2 - Quality Signals & BiaHS)

**FIGURES:**
- `imgs/benchmark_percentiles_by_classifier.png` - BiaHS: classifieurs amplifient contamination
- `imgs/garlic_ratios.pdf` - Evolution scores vs contamination ratio (0-50%)
- `imgs/pretraining_data_quality_exp.png` - Filtrage qualité comparisons
- `imgs/olmo_contam.pdf` - MMLU contamination OLMo-1 vs OLMo-2

**TABLES:**
- Confusion matrix classifieur qualité (F1=75.11%)
- Benchmark results GAPeron 1.5B/8B/24B (5-shot)
- Young vs Pepper vs Garlic variants

**KEY POINTS:**
- Classifieur qualité XLM-R entraîné sur 500k docs annotés Llama3.1-70B
- BiaHS: DCLM rank benchmarks top-5 percentiles (20× amplification si top-5% sélectionné)
- Root cause: DCLM trained on Q&A structure → matches benchmark format
- GAPeron classifier (general quality focus) ne amplifie PAS benchmarks
- Trigger activation accuracy: 91%→99% selon model size

---

### Biomed-Enriched (Ch.3 - Content Types)

**FIGURES:**
- `figures/pipeline.pdf` - Pipeline 2-stage (Llama-3.1-70B → XLM-R distillation)
- `figures/pipeline_motivation.svg` - Motivation paragraph-level vs document-level
- `figures/combined_plot_v2.pdf` - BE-All atteint cible avec 1/3 tokens
- `figures/curve_triple.pdf` - Encoder training curves (clinical, biomedical, combined)
- `figures/combined_educational_scores.pdf` - Quality distribution by type/domain

**TABLES:**
- Table hétérogénéité intra-document: 91.6% articles = mixed types
- Distillation quality: r=0.876, F1 domain=0.954, F1 type=0.925
- Decoder results: BE-All +2.4 MedQA, +1.5 MMLU Clinical
- Encoder results: 77.08% F1 ≈ BioClinical-ModernBERT avec 2.5× moins tokens

**KEY POINTS:**
- 91.6% articles PMC mélangent types (Clinical Case, Study, Review, Other)
- Educational quality varie 2.6 points en moyenne intra-article
- 2M cas cliniques extraits paragraph-level de PMC
- Même perf avec 1/3 des tokens vs baseline
- Match BioClinical-ModernBERT: 77.3% F1 avec seulement données publiques (pas MIMIC)

---

### ModernCamemBERT-bio (Ch.5 - Architectures Modernes)

**FIGURES (findings_synthesis.md):**
- Position Crossover: CLM gagne 0-2048, MLM gagne 2048+
- CLM Gradient Distribution decay across positions
- Downstream F1 during MLM decay (125M→1B tokens)
- Attention distance evolution during decay
- Layer-wise information emergence (CLM late L10-14, MLM early L2-6)

**TABLES:**
| Position | CLM | MLM | Winner | Δ |
|----------|-----|-----|--------|---|
| 256-1024 | 0.918 | 0.873 | CLM | +4.5% |
| 1024-2048 | 0.913 | 0.875 | CLM | +3.8% |
| 2048-4096 | 0.723 | 0.834 | MLM | -11.1% |
| 4096+ | 0.635 | 0.757 | MLM | -12.2% |

| Task | CLM | MLM | Δ |
|------|-----|-----|---|
| fracco30 | 0.710 | 0.668 | +4.3% |
| fracco100 | 0.571 | 0.544 | +2.6% |
| diamed | 0.641 | 0.593 | +4.8% |
| **AVG** | **0.597** | **0.577** | **+2.0%** |

**KEY POINTS:**
- Flash Attention + RoPE + 8192 tokens context
- CLM→decay pipeline: +7% overall, +2% avg sur 8 tasks
- Crossover à 2048 tokens: CLM compression avantage court, MLM bidirectionnel avantage long
- Crucial pour FRACCO (longs comptes rendus CIM-10): +6.9% F1
- CLM force compression → représentations self-sufficient (effective context 83 vs 142 tokens)
- Gradient imbalance: early positions over-trained, late under-trained

---

### Ontobook (Ch.6 - Knowledge-Enriched)

**FIGURES:**
- `images/pipeline.pdf` - Ontologies → Walks → Textbooks → R1M1 training
- `images/textbook_example.pdf` - Walk structuré → prose médicale fluide
- `images/results_bar.pdf` - Comparaison modèles (epoch 2 best)
- `images/lambda_ablation.pdf` - Lambda sensitivity (robust 0.1-5.0)
- `figures/tsne_comparison.pdf` - Visualisation embeddings CIM-10 par chapitre

**TABLES:**
| Model | FRACCO | Cantemist | Distemist | AVG | Δ vs MLM |
|-------|--------|-----------|-----------|-----|----------|
| OntoBook-ep2 | 58.33 | 67.06 | 32.24 | **52.54** | **+3.86%** |
| OntoBook-ATC-ep2 | **59.66** | 63.03 | **36.05** | **52.91** | **+4.23%** |
| MLM-baseline | 55.81 | 66.01 | 24.23 | 48.68 | 0.00 |
| Misaligned | 33.39 | 20.11 | 12.63 | 22.04 | **-26.64%** |

| Ontology Walks | Count | Size |
|----------------|-------|------|
| CIM-10 | 402k | 2.3 GB |
| ATC | 139k | 291 MB |
| CCAM | 763k | 2.9 GB |
| **Total** | **1.3M** | **5.5 GB** |

**KEY POINTS:**
- 1.3M walks ontologies (CIM-10, ATC, CCAM) → LLM reformulation (Qwen3-235B)
- Multi-task: MLM + Relation Prediction (6 classes)
- Alignement CRITIQUE: misaligned = -26.64 points (catastrophique)
- Epoch 2 optimal, ep3+ overfits sur relations
- Cross-ontology transfer: ATC (médicaments) améliore Distemist (maladies) +12.55 pts
- Probing paradox: meilleure géométrie ≠ meilleur downstream

---

### MCB-bio-gliner / MedEmbed (Ch.7 - Zero-Shot GLiNER)

**FIGURES:**
- Training pipeline (RDF + synthetic + personas → MedEmbed)
- Data composition bar chart (760k personas, 490k passages, 258k RDF)
- GLiNER2 workflow (label encoder + similarity matching)
- Persona-based query generation (5 styles)
- Hard negative mining flowchart

**TABLES:**
| Model | CIM-10 | ATC | CCAM | FrMedMCQA | Avg |
|-------|--------|-----|------|-----------|-----|
| MedEmbed-v4 | 41.4% | **41.6%** | 31.2% | **27.5%** | **32.9%** |
| Solon | 41.6% | 36.8% | 38.8% | 22.5% | 32.5% |

| Data Source | Pairs |
|-------------|-------|
| RDF (CIM-10, ATC, CCAM) | 258k |
| Synthetic passages | 490k |
| Personas augmentation | 760k |
| **Total** | **~1.5M** |

**KEY POINTS:**
- Multi-source: 1.5M pairs (RDF + synthetic + personas)
- 5 personas pour query diversity (expert, étudiant, patient, chercheur, codeur)
- Hard negative mining via teacher externe (Solon)
- ModernCamemBERT-base (149M params, 8192 context)
- Beats Solon on ATC (+4.8%) et FrenchMedMCQA (+5.0%)
- Publication "À faire" mais pipeline/data existe
