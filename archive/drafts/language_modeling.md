# Language Models - Related Works Draft

---

## BEST PRACTICES FOR NLP RELATED WORKS (2026)

*Extracted from 3 recent Sorbonne/INRIA theses: Godey (2024), Duquenne (2024), Nguyen (2024)*

[Best practices omitted for brevity - keep the full section from before]

---
---

## CHAPTER DRAFT: Language Models (Telegraphic)

### 2.1 Introduction

**Formal definition:**
- LM = probabilistic model: P(w) = ∏ P(wₜ|w_{<t})
- Autoregressive factorization
- Foundation for all downstream NLP

**Why it matters for thesis:**
- Clinical IE relies on pretrained LMs as backbone
- Domain adaptation = core challenge
- French + biomedical + clinical = triple scarcity

---

### 2.2 From Statistical to Neural LMs

#### 2.2.1 N-gram Models
- Markov assumption: P(wₜ|w_{<t}) ≈ P(wₜ|w_{t-n+1}, ..., w_{t-1})
- Kneser-Ney smoothing (1995)
- Limitation: curse of dimensionality

#### 2.2.2 Neural LMs
- **Bengio et al. (2003)** - neural probabilistic LM
  - Dense embeddings solve sparsity
  - Similar words → similar vectors

- **Word2Vec (Mikolov et al., 2013)**
  - Skip-gram / CBOW
  - Famous analogy: king - man + woman ≈ queen

- **ELMo (Peters et al., 2018)**
  - Contextual embeddings from biLSTM
  - Same word, different contexts → different vectors

#### 2.2.3 RNN Era (2014-2017)
- LSTM (Hochreiter & Schmidhuber, 1997)
- Can capture long deps in theory
- Practice: gradient vanishing, no parallelization
- → Bottleneck for scaling

---

### 2.3 Transformer Architecture

#### 2.3.1 Self-Attention (Vaswani et al., 2017)

**Core mechanism:**
```
Q = XW_Q, K = XW_K, V = XW_V
Attention = softmax(QK^T / √d_k) V
```

**Key properties:**
- Direct cross-position interactions (vs RNN indirect)
- O(L²) time and memory → limits sequence length
- Fully parallelizable training

**Multi-head attention:**
- h parallel heads with different projections
- Each head can specialize (syntax, semantics, position)

#### 2.3.2 Positional Encodings

| Type | Method | Extrapolation |
|------|--------|---------------|
| APE - sinusoidal | Vaswani et al. (2017) | Limited |
| APE - learned | Devlin et al. (2019) | None |
| RPE - ALiBi | Press et al. (2022) | Linear bias |
| RPE - **RoPE** | Su et al. (2021) | Rotation matrices, **best** |

**RoPE now standard:** LLaMA, Mistral, ModernBERT

#### 2.3.3 Encoder vs Decoder

| | Encoder | Decoder |
|---|---|---|
| Attention | Bidirectional | Causal (masked) |
| Training | MLM | CLM |
| Inference | Full context | KV-cache |
| Tasks | Classification, NER | Generation |
| Examples | BERT, RoBERTa | GPT, LLaMA |

**Encoder-decoder:** T5 (Raffel et al., 2020), for seq2seq

---

### 2.4 Pretraining Objectives

#### 2.4.1 Causal Language Modeling (CLM)

**GPT family (Radford et al., 2018, 2019):**
```
L_CLM = -∑ log P(wₜ|w_{<t})
```
- Every token → gradient signal
- Dense supervision
- Natural for generation

**Properties:**
- Every position contributes to loss
- But: gradient imbalance by position (early positions see more updates)

#### 2.4.2 Masked Language Modeling (MLM)

**BERT (Devlin et al., 2019):**
```
L_MLM = -∑_{t∈M} log P(wₜ|w_{≠t})
```
- 15% tokens masked (80% [MASK], 10% random, 10% unchanged)
- Bidirectional context → richer representations

**Limitation:**
- Only 15% tokens contribute → sparse gradient signal
- Contrast with CLM where every token contributes

#### 2.4.3 Hybrid Objectives (2024-2025)

**The CLM→MLM approach:**
- CLM first → MLM decay = better downstream than MLM alone
- CLM: dense gradients (all tokens), MLM: sparse (15%)
- Hypothesis: CLM "compresses" knowledge, MLM restores bidirectionality

**Recent work:**
- **"Should We Still Pretrain Encoders with MLM?"** (arXiv:2507.00994, 2025): biphasic CLM→MLM outperforms pure MLM
- **GPT-BERT** (arXiv:2410.24159, 2024): unified CLM+MLM in single architecture
- **AntLM** (CoNLL 2024): alternating CLM/MLM during training

**Context:** ELECTRA (Clark et al., 2020) proposed RTD for denser signal, but ModernBERT shows good architecture + MLM can match RTD performance.

---

### 2.5 Scaling Laws & LLMs

#### 2.5.1 The Scaling Era

**GPT-3 (Brown et al., 2020):**
- 175B parameters
- Emergent few-shot abilities
- Prompting replaces fine-tuning

**Chinchilla (Hoffmann et al., 2022):**
- Compute-optimal scaling
- Smaller model + more data > larger model + less data
- Key for resource-constrained domains

**LLaMA (Touvron et al., 2023):**
- 7B matches much larger with 1T tokens
- Open weights → democratization
- Implication: don't need Google-scale compute

#### 2.5.2 Post-ChatGPT Era

- **RLHF (Ouyang et al., 2022):** Preference learning
- **Instruction tuning:** Task-agnostic alignment
- **Chat-LLMs:** ChatGPT, Claude, Gemini
- **Emergent abilities (Wei et al., 2022):** Chain-of-thought, etc.

---

### 2.6 Continual Pretraining

#### 2.6.1 Foundations & Terminology

**Gururangan et al. (2020) - "Don't Stop Pretraining":**
- **DAPT** (Domain-Adaptive Pre-Training): second phase on domain corpus
- **TAPT** (Task-Adaptive Pre-Training): on task-specific unlabeled data
- DAPT + TAPT combined → best results
- Up to **+3 F1** even with small corpus

**Modern taxonomy (Wang et al., CSUR 2025):**
- **CPT** (Continual Pre-Training): new general data over time
- **DAP** (Domain-Adaptive Pre-training): domain specialization
- **CFT** (Continual Fine-Tuning): sequential task adaptation

#### 2.6.2 Catastrophic Forgetting

**The problem (Kirkpatrick et al., 2017):**
- Neural networks overwrite parameters needed for previous tasks
- "Catastrophic forgetting" = sudden loss of prior knowledge
- EWC (Elastic Weight Consolidation): penalize changes to important weights

**Why it matters for LLMs:**
- Continual PT can degrade general capabilities
- Instruction-following ability particularly vulnerable
- Smaller models more sensitive (Yıldız et al., 2024)

**"Spurious forgetting" (2024):**
- Performance drops may reflect task alignment loss, not true knowledge loss
- Distinction important for diagnosis and mitigation

#### 2.6.3 Modern Solutions (2024-2025)

**Ibrahim et al. (2024) - "Simple and Scalable Strategies":**
- **LR re-warming**: restart learning rate when adding new data
- **LR re-decaying**: cosine decay after warmup
- **Replay**: mix 1% previous data → sufficient to prevent forgetting
- Validated at 405M and 10B scale
- Matches from-scratch performance at fraction of compute

**Stability Gap (arXiv:2406.14833, 2024):**
- Temporary performance drop at start of continual PT
- Then recovery as model adapts
- Solutions:
  - Train on proper subset for multiple epochs
  - Use high-quality sub-corpus only
  - Data mixing similar to original pretraining
- Result: 36.2% → 40.7% with only 40% training budget

**Data selection:**
- Naive inclusion of irrelevant data degrades performance
- 10% of corpus with good selection ≈ 100% vanilla continual PT
- Quality > quantity for domain adaptation

#### 2.6.4 The Debate: From Scratch vs Continual PT

| Approach | Proponents | Pro | Con |
|----------|------------|-----|-----|
| From scratch | PubMedBERT, DrBERT | Custom vocab, no forgetting | High compute |
| Continual PT | BioBERT, Gururangan | Efficient, preserves general | Suboptimal tokenizer |

**Computational cost:**

| Model | Method | Hardware |
|-------|--------|----------|
| DrBERT (Labrak et al., 2023) | From scratch | 128× V100, 20h |
| AliBERT (Berhe et al., 2023) | From scratch | 48× A100, 20h |
| BioBERT (Lee et al., 2019) | Continual | 8× V100, ~10 days |

→ From-scratch requires **~30× more compute** than continual PT

#### 2.6.5 Encoders vs Decoders: Different Dynamics

**Decoders (LLMs): problematic**
- BioMistral: **-0.9 points** after continual PT
- Dorfner et al. (2024): biomedical LLMs underperform generalists
- OpenBioLLM-8B: 30% vs Llama-3-8B: 64% on NEJM
- Hypothesis: general knowledge loss during specialization

**Encoders: different story**
- Bidirectional context may be more robust
- MLM objective less prone to forgetting?
- **→ See Ch.5: CLM→MLM approach for encoders**

#### 2.6.6 Earlier Attempts on French Biomedical

- Copara et al. (2020): 31K articles → no improvement (corpus too small)
- Le Clercq de Lannoy et al. (2022): 136M words → +2 EMEA only
- Dura et al. (2022): 21M APHP docs → +3% but private data

**Open question:** Why conflicting results?
- Corpus size and quality matter
- DrBERT claims continual PT ineffective
- CamemBERT-bio (this thesis) shows it works with proper corpus

---

### 2.7 Pretrained Models for Biomedical

#### 2.7.1 English Biomedical Models

| Model | Corpus | Method | Key Result |
|-------|--------|--------|------------|
| **BioBERT** (Lee et al., 2019) | PubMed 4.5B + PMC 13.5B words | Continual | +0.62% NER, +2.80% RE |
| **SciBERT** (Beltagy et al., 2019) | Semantic Scholar 1.14M papers | From scratch | 42% vocab overlap with BERT |
| **PubMedBERT** (Gu et al., 2022) | PubMed only | From scratch | Introduces BLURB benchmark |
| ClinicalBERT (Alsentzer et al., 2019) | MIMIC-III notes | Continual | Restricted access |
| **BioLinkBERT** (Yasunaga et al., 2022) | PubMed + citation links | From scratch | +7% BioASQ, multi-hop |

**Note:** SciBERT's 42% vocab overlap → tokenization matters

**2025 state-of-the-art:** BioClinical ModernBERT (53.5B tokens, 20 clinical datasets) — see §2.8.3

#### 2.7.2 French Models

**General French:**
- **CamemBERT (Martin et al., 2020):** RoBERTa on OSCAR 138GB
  - Finding: 4GB ≈ 138GB performance
  - SOTA French POS, NER, NLI
- FlauBERT (Le et al., 2020): Alternative French BERT
- **CamemBERT 2.0 / CamemBERTa (2024):** DeBERTaV3 architecture
  - Updated tokenizer, larger dataset
  - Superior performance with fewer tokens

**French Biomedical:**
- **DrBERT (Labrak et al., 2023):** From scratch, public + private data
  - Claims continual PT ineffective for French biomedical
- **AliBERT (Berhe et al., 2023):** From scratch, regularized Unigram tokenizer
  - Not publicly available

**Open question:** Conflicting results on continual PT effectiveness for French biomedical
- DrBERT claims from-scratch is necessary
- CamemBERT-bio (this thesis) shows continual PT works with proper corpus

#### 2.7.3 Biomedical Decoders

| Model | Tokens | Hardware | Note |
|-------|--------|----------|------|
| BioMistral (Labrak et al., 2024) | 3B PMC | 32× A100, 20h | Mistral-based |
| Meditron (Chen et al., 2023) | 46B mixed | 128× A100, 332h | Llama-2 based |
| PMC-LLaMA (Wu et al., 2024) | 75B PMC+textbooks | - | Massive scale |

**⚠️ Continual PT for decoders: mixed results**

- BioMistral: **-0.9 points** after continual PT (recovered only via model merging)
- **Dorfner et al. (2024):** "Biomedical LLMs Seem not to be Superior to Generalist Models"
  - OpenBioLLM-8B: 30% vs Llama-3-8B: **64.3%** on NEJM cases
  - "fine-tuning to biomedical may reduce performance"
- Hypothesis: catastrophic forgetting of general knowledge

**Contrast with encoders:** different dynamics — see Ch.5 (CLM→MLM)

---

### 2.8 Modern Architectures

#### 2.8.1 Encoder Modernization

**DeBERTa (He et al., ICLR 2021):**
- Disentangled attention: separate content and position
- Enhanced mask decoder for pretraining
- First to surpass human on SuperGLUE
- → Influence on ModernBERT, CamemBERT 2.0

**MosaicBERT (Portes et al., NeurIPS 2023):**
- 30% masking ratio (vs 15% BERT)
- FlashAttention + ALiBi + GLU + unpadding
- BERT-base in 1.13h on 8× A100 (~$20)
- **→ Direct foundation for ModernBERT**

#### 2.8.2 Efficient Attention

**FlashAttention (Dao et al., 2022):**
- Reorganizes computation for GPU memory hierarchy
- Same O(L²) but 2-4× faster in practice
- Enables longer sequences without hardware changes
- **Standard in modern models**

**Group Query Attention (Ainslie et al., 2023):**
- KV-head sharing reduces memory
- Used in Llama-2, Mistral

**RMSNorm (Zhang & Sennrich, 2019):**
- Simplified LayerNorm, faster

#### 2.8.3 Long Context Models

**The problem:**
- BERT: 512 tokens
- Clinical discharge summaries: often 2000+ tokens
- Truncation loses diagnostic information

**Solutions:**

| Model | Context | Method |
|-------|---------|--------|
| Longformer (Beltagy et al., 2020) | 4096 | Sliding window + global |
| BigBird (Zaheer et al., 2020) | 4096 | Sparse attention |
| Clinical Longformer (Li et al., 2022) | 4096 | Longformer + MIMIC-III |
| **ModernBERT (Warner et al., 2024)** | 8192 | FlashAttention + RoPE |

**ModernBERT key features:**
- FlashAttention v2/v3
- RoPE for position extrapolation
- Alternating local/global attention
- 8192 context (16× BERT)
- 30% masking (from MosaicBERT)

**Clinical adaptations (2025):**
- **Clinical ModernBERT** (Lee et al., 2025): PubMed + MIMIC-IV + ontologies
- **BioClinical ModernBERT** (2025): 53.5B tokens, 20 clinical datasets, **current SOTA**

---

### 2.9 Tokenization

#### 2.9.1 Subword Methods

- **BPE (Sennrich et al., 2016):** Merge frequent pairs
- **SentencePiece (Kudo & Richardson, 2018):** Language-independent
- **Unigram (Kudo, 2018):** Probabilistic selection

#### 2.9.2 Domain Mismatch Problem

**SciBERT finding (Beltagy et al., 2019):**
- General BERT vocab vs scientific: **42% intersection only**
- Implies significant vocabulary mismatch for technical domains

**Example (biomedical French):**
- General tokenizer: "échocardiographie" → ["écho", "##cardi", "##ographie"]
- Domain tokenizer: "échocardiographie" → ["échocardiographi", "e"]

**Implication:**
- From-scratch allows custom vocab but expensive
- Continual PT inherits suboptimal tokenizer but efficient
- Trade-off depends on compute budget

---

### 2.10 Limitations → Transition to Next Chapters

**Data scarcity:**
- Clinical text is private (CNIL regulations)
- Hospital models can't be shared
- → Need public alternatives **(see Ch. 3: Corpus Annotation)**

**Knowledge gap:**
- LMs capture patterns, not ontology structure
- Medical coding requires hierarchical knowledge
- → Knowledge-enhanced approaches **(see Ch. 4: Clinical IE)**

**Long documents:**
- Clinical reports exceed BERT limits
- Modern architectures (Longformer, ModernBERT) address this
- But: need domain adaptation for biomedical/clinical

**Transition:** This chapter covered the technical foundations of language modeling. The next chapter addresses how to build and curate domain-specific corpora for training these models.

---

### Key References

| Topic | Key Papers |
|-------|------------|
| Transformer | Vaswani et al. (2017) |
| BERT | Devlin et al. (2019) |
| RoBERTa | Liu et al. (2019) |
| GPT-3 | Brown et al. (2020) |
| LLaMA | Touvron et al. (2023) |
| Scaling laws | Kaplan et al. (2020), Hoffmann et al. (2022) |
| **Continual PT foundations** | Gururangan et al. (2020) "Don't Stop Pretraining" |
| **Catastrophic forgetting** | Kirkpatrick et al. (2017) EWC |
| **Continual PT strategies** | Ibrahim et al. (2024) "Simple and Scalable" |
| **Continual PT survey** | Wang et al. (CSUR 2025) |
| **Stability gap** | arXiv:2406.14833 (2024) |
| BioBERT | Lee et al. (2019) |
| PubMedBERT | Gu et al. (2022) |
| BioLinkBERT | Yasunaga et al. (2022) |
| CamemBERT | Martin et al. (2020) |
| DrBERT | Labrak et al. (2023) |
| DeBERTa | He et al. (2021) |
| MosaicBERT | Portes et al. (2023) |
| FlashAttention | Dao et al. (2022) |
| RoPE | Su et al. (2021) |
| ModernBERT | Warner et al. (2024) |
| BioClinical ModernBERT | (2025) |
| Longformer | Beltagy et al. (2020) |
| CLM→MLM | arXiv:2507.00994 (2025) |
| Biomed decoders fail | Dorfner et al. (2024) |


---

## NOTES DE RECHERCHE

*Méthodologie: remontée des citations depuis BioClinical ModernBERT (2025) + Dorfner et al. (2024)*

### ✅ Intégré dans le draft

- §2.4.3: CLM→MLM hybrides (GPT-BERT, AntLM, "Should We Still...")
- §2.6: **Section Continual PT réécrite** (Kirkpatrick, Ibrahim, Stability Gap, Wang survey)
- §2.7.1: BioLinkBERT, référence vers BioClinical ModernBERT
- §2.7.2: CamemBERT 2.0
- §2.7.3: Dorfner et al. (biomedical decoders fail)
- §2.8.1: DeBERTa, MosaicBERT
- §2.8.3: Clinical Longformer, Clinical/BioClinical ModernBERT

### 📌 À déplacer vers Ch.3 (Clinical IE)

**SapBERT (Liu et al., NAACL 2021):**
- UMLS synonyms → contrastive learning
- Entity linking SOTA, 4M+ concepts
- Pertinent pour GLiNER (Ch.7)

### 🔗 Sources principales

**Continual Pretraining:**
- [Gururangan (2020)](https://arxiv.org/abs/2004.10964) "Don't Stop Pretraining"
- [Kirkpatrick (2017)](https://arxiv.org/abs/1612.00796) EWC
- [Ibrahim (2024)](https://arxiv.org/abs/2403.08763) "Simple and Scalable"
- [Stability Gap (2024)](https://arxiv.org/abs/2406.14833)
- [Wang Survey (2025)](https://arxiv.org/abs/2404.16789)
- [Dorfner (2024)](https://arxiv.org/abs/2408.13833) Biomedical LLMs fail

**Modern Encoders:**
- [BioClinical ModernBERT](https://arxiv.org/abs/2506.10896) → [ModernBERT](https://arxiv.org/abs/2412.13663) → [MosaicBERT](https://arxiv.org/abs/2312.17482)

**CLM→MLM:**
- [Should We Still Pretrain with MLM?](https://arxiv.org/abs/2507.00994)

