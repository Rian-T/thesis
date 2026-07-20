# Knowledge-Pretraining TikZ Corrections Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the four knowledge-pretraining figures and adjacent prose factually conservative and faithful to Node2Vec/RDF2Vec, K-BERT, SapBERT/CODER, and EntiGraph.

**Architecture:** Keep all four figure positions and labels, but narrow each diagram to one bounded mechanism. Reuse the thesis TikZ palette, change only `sources/related_works/corpus_annotation.tex`, then compile and visually inspect the affected PDF pages before writing a precise change report.

**Tech Stack:** LaTeX, TikZ, existing BibTeX citation keys, project Makefile, Poppler rendering tools.

## Global Constraints

- Follow `docs/superpowers/specs/2026-07-19-knowledge-pretraining-tikz-corrections-design.md` exactly.
- Prefer narrower claims over visually complete but contestable generalisations.
- Keep `\subsection{Synthetic Data for Pretraining}` broad.
- Preserve figure labels and existing citation keys.
- Do not edit `thesis.bib`, `tools/bibcheck_whitelist.txt`, or unrelated prose.
- Do not commit; the workspace already contains unrelated user changes.

---

### Task 1: Correct the static graph-embedding figure

**Files:**
- Modify: `sources/related_works/corpus_annotation.tex:335-403`

**Interfaces:**
- Consumes: the existing `fig:corpus-static` layout and thesis TikZ styles.
- Produces: a directed illustrative cross-ontology graph, a valid sampled path, and conservative Node2Vec/RDF2Vec prose.

- [ ] **Step 1: Record the current baseline**

Run `sed -n '333,404p' sources/related_works/corpus_annotation.tex`.

Expected: the current undirected graph, `E08-E13`, `random walk`, and `skip-gram` caption are visible.

- [ ] **Step 2: Apply the minimal prose and TikZ corrections**

Implement these exact semantic changes:

```text
E08-E13 -> ICD-10 E10--E14
ontology fragment -> illustrative cross-ontology graph
random walk -> sampled graph path
skip-gram -> word2vec-style objective
Type 2 diabetes -> Diabetes mellitus [solid is-a]
Metformin -> Biguanides [solid is-a]
Metformin -> Type 2 diabetes [dashed treats]
```

Use prose that distinguishes Node2Vec biased random walks from RDF2Vec directed RDF traversals and says RDF2Vec may retain predicates.

- [ ] **Step 3: Run structural assertions**

Run `rg -n 'E08-E13|ontology fragment|random walk|word2vec-style objective|illustrative cross-ontology graph|relations may also be retained' sources/related_works/corpus_annotation.tex`.

Expected: no `E08-E13` in this figure; the new conservative labels are present.

### Task 2: Make the injection figure K-BERT-specific

**Files:**
- Modify: `sources/related_works/corpus_annotation.tex:405-460`

**Interfaces:**
- Consumes: the original sentence-token row and Transformer band.
- Produces: a K-BERT sentence tree with a visible knowledge branch, soft positions, and a visibility matrix; DRAGON remains prose-only.

- [ ] **Step 1: Replace the ambiguous diagram**

Implement this flow:

```text
The patient was started on metformin .
                                |
                                +-> treats -> Type 2 diabetes

sentence tree -> flattening + soft positions + visibility matrix -> Transformer
```

All original and added tokens must visibly feed the Transformer. Replace `triple injected at the entity token` with `knowledge branch attached to the entity mention`.

- [ ] **Step 2: Narrow the prose and caption**

State that the family couples text with explicit entities or graph structure. State that the figure illustrates K-BERT's input-level mechanism. Describe DRAGON separately as accepting text and a relevant subgraph as separate modalities with bidirectional fusion. Cite only `liu2020kbert` in the caption.

- [ ] **Step 3: Assert citation and wording scope**

Run `sed -n '405,462p' sources/related_works/corpus_annotation.tex`.

Expected: the caption contains `liu2020kbert` but not `yasunaga2022dragon`; the prose still cites DRAGON accurately.

### Task 3: Make the contrastive figure SapBERT-specific

**Files:**
- Modify: `sources/related_works/corpus_annotation.tex:462-504`

**Interfaces:**
- Consumes: the existing synonym cluster and Type 1 diabetes node.
- Produces: a SapBERT-only diagram and prose that separately records CODER's relation-triplet objective.

- [ ] **Step 1: Correct the negative-pair wording**

Replace `unrelated term pushed apart` with `different but related concept / negative pair`.

- [ ] **Step 2: Separate SapBERT and CODER in prose**

State that SapBERT learns from synonymous terms attached to the same UMLS concept and that CODER adds contrastive supervision from term--relation--term triples. State that the figure illustrates SapBERT only. Cite only `liu2021sapbert` in the caption.

- [ ] **Step 3: Assert the narrowed caption**

Run `sed -n '462,506p' sources/related_works/corpus_annotation.tex`.

Expected: `unrelated term` is absent; CODER remains in prose but not in the figure caption.

### Task 4: Replace the false EntiGraph input pipeline

**Files:**
- Modify: `sources/related_works/corpus_annotation.tex:506-566`

**Interfaces:**
- Consumes: the existing output-text box and 1.3M-to-455M scale annotation.
- Produces: a source-document-to-entity-extraction-to-relation-analysis pipeline and conservative closing prose.

- [ ] **Step 1: Rename the subsection and rewrite the adjacent paragraph**

Use exactly `\subsection{Synthetic Data for Pretraining}`. Describe synthetic data broadly, then describe EntiGraph as extracting salient entities, sampling groups, and prompting an LLM with access to the source document to generate relation-focused synthetic text.

- [ ] **Step 2: Replace the TikZ input side**

Implement this flow:

```text
source document -> entity extraction -> sampled entity pairs/triples -> LLM relation analysis -> synthetic text
       |                                                         ^
       +---------------------------------------------------------+
```

The direct source-document arrow into relation analysis is required. Retain `1.3M real tokens -> 455M synthetic tokens`.

- [ ] **Step 3: Correct the caption and closing summary**

The caption must begin from a small source corpus, not an ontology. In the closing paragraph, use `Entity-centric synthetic augmentation for continued pretraining` and `synthesising relation-focused text from source documents`.

- [ ] **Step 4: Assert forbidden and required wording**

Run `rg -n 'Graph-to-Text|ontology fragment|Synthetic Data for Pretraining|source document|relation-focused' sources/related_works/corpus_annotation.tex`.

Expected: the old subsection title and EntiGraph ontology input are absent; the required wording is present.

### Task 5: Build, inspect, and report

**Files:**
- Verify: `sources/related_works/corpus_annotation.tex`
- Verify: `thesis.pdf`
- Create: `docs/reviews/2026-07-19-knowledge-pretraining-tikz-change-report.md`

**Interfaces:**
- Consumes: all four corrected figures and adjacent prose.
- Produces: a successful build, rendered-page evidence, and a precise report of every modification.

- [ ] **Step 1: Build the thesis using the project command**

Run `make build`.

Expected: exit code 0 and an updated `thesis.pdf`.

- [ ] **Step 2: Locate and render the affected PDF pages**

Use `pdftotext` to find the four captions, then `pdftoppm -png -f PAGE -singlefile thesis.pdf /private/tmp/<figure>` for each page.

Expected: four PNG renders corresponding to the corrected figures.

- [ ] **Step 3: Visually inspect all four renders**

Check that no label overlaps, no arrow direction is ambiguous, all figure text is readable, and no content is clipped at the page boundary.

- [ ] **Step 4: Write the precise Markdown report**

The report includes files changed, prose changes by subsection, TikZ changes by figure, factual rationale, exact verification commands and outcomes, and deliberate remaining simplifications.

- [ ] **Step 5: Review the final diff**

Run `git diff --check` and inspect the diff for `sources/related_works/corpus_annotation.tex` plus the report.

Expected: no whitespace errors and no unrelated source changes.
