# Related Works Quantitative Audit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Verify every material numerical, quantitative, comparative, and version-dependent claim in the three active related-work chapters against primary sources, then deliver a traceable review report without editing the thesis text.

**Architecture:** Build a frozen inventory from the three TeX sources, group nearby numerical tokens into auditable claims, and map each claim to the cited paper or an official versioned source. Record evidence and a calibrated verdict in a standalone Markdown report; finish with a coverage reconciliation and a second-pass challenge of every non-exact verdict.

**Tech Stack:** ripgrep, BibTeX, SHA-256, curl/web access, Poppler (`pdfinfo`, `pdftotext`, `pdftoppm`), Markdown

## Global Constraints

- Audit `sources/related_works/language_modeling.tex`, `sources/related_works/corpus_annotation.tex`, and `sources/related_works/clinical_ie.tex` in full.
- Include prose, tables, captions, equations, figure annotations, units, ratios, ranges, ranks, dates used analytically, and numbers written in words.
- Prefer the cited primary paper; use official dataset, ontology, model, or institutional pages for version-dependent live statistics.
- Distinguish `exact`, `faithful rounding`, `version-dependent`, `not found`, and `incorrect`; never silently convert absence of evidence into correctness.
- Do not repeat findings already documented in the two fidelity reports unless a new quantitative error or a changed user edit requires it.
- Do not modify the TeX or BibTeX sources. Create only the audit plan, temporary evidence files, and the final review report.
- Preserve the user's concurrent edits by snapshotting source hashes and rechecking them before delivery.

---

### Task 1: Freeze the Scope and Build the Candidate Ledger

**Files:**
- Read: `sources/related_works/language_modeling.tex`
- Read: `sources/related_works/corpus_annotation.tex`
- Read: `sources/related_works/clinical_ie.tex`
- Create: `docs/reviews/2026-07-19-related-work-quantitative-audit.md`

**Interfaces:**
- Consumes: the three active TeX files at their recorded SHA-256 hashes.
- Produces: a numbered claim ledger with file, line, thesis wording/value, local citation, and evidence status.

- [ ] **Step 1: Record the immutable starting snapshot**

Run:

```bash
shasum -a 256 sources/related_works/language_modeling.tex sources/related_works/corpus_annotation.tex sources/related_works/clinical_ie.tex
```

Expected: exactly three hashes, one per active related-work file.

- [ ] **Step 2: Extract explicit numerical candidates**

Run:

```bash
rg -n '[0-9]|\\%|\\times|\\approx|\\sim|\\leq|\\geq' sources/related_works/*.tex
```

Expected: all lines containing digits, percentages, explicit multiplicative factors, approximations, or bounds.

- [ ] **Step 3: Extract implicit quantitative candidates**

Run:

```bash
rg -ni '\b(one|two|three|four|five|six|seven|eight|nine|ten|dozen|hundred|thousand|million|billion|trillion|half|quarter|double|triple|first|largest|smallest|more than|less than|over|under|up to|at least|at most|roughly|approximately|nearly)\b' sources/related_works/*.tex
```

Expected: lines with written numbers, extrema, rankings, bounds, and approximate magnitudes.

- [ ] **Step 4: Group tokens into claims**

Combine values that share one sentence, table row, equation, or caption into one ledger item. Keep separate claims when a sentence contains independently sourced values.

Expected: every extracted candidate is either assigned to one ledger item or explicitly marked non-claim (for example, an equation index or citation year with no analytical use).

### Task 2: Resolve Citations and Primary Evidence

**Files:**
- Read: `thesis.bib`
- Read: the three active related-work TeX files
- Temporary evidence: `tmp/pdfs/related-work-quantitative-audit/`

**Interfaces:**
- Consumes: claim ledger and nearby `\\cite{...}` keys.
- Produces: stable primary URLs/DOIs and page/table/section locators for every material claim.

- [ ] **Step 1: Map each claim to its nearby citation keys**

Run:

```bash
rg -n '\\cite[a-zA-Z]*\{[^}]+\}' sources/related_works/*.tex
```

Expected: a complete citation-position index for resolving the preceding and following quantitative claims.

- [ ] **Step 2: Resolve bibliographic metadata**

For each key, inspect its BibTeX entry and prefer DOI, arXiv, ACL Anthology, PMLR, journal, official repository, or official project URL in that order.

Expected: each ledger item has a primary-source target or is marked `source missing`.

- [ ] **Step 3: Download high-density PDFs for local search**

Run one command per stable PDF URL:

```bash
curl -L --fail --silent --show-error '<PRIMARY_PDF_URL>' -o 'tmp/pdfs/related-work-quantitative-audit/<key>.pdf'
pdftotext -layout 'tmp/pdfs/related-work-quantitative-audit/<key>.pdf' 'tmp/pdfs/related-work-quantitative-audit/<key>.txt'
```

Expected: valid PDFs and searchable text; if extraction is garbled, render the cited page with `pdftoppm -png -r 150` and inspect the image.

### Task 3: Audit Language Modeling Quantities

**Files:**
- Read: `sources/related_works/language_modeling.tex`
- Modify: `docs/reviews/2026-07-19-related-work-quantitative-audit.md`

**Interfaces:**
- Consumes: language-modeling ledger entries and primary evidence.
- Produces: verdicts for all language-modeling claims, including tables and equations.

- [ ] **Step 1: Verify historical architecture and objective quantities**

Check vocabulary/context dimensions, attention scaling, masking proportions, model sizes, data sizes, and any claimed relative improvement against the cited paper section or table.

Expected: every pre-scaling ledger item receives a verdict and locator.

- [ ] **Step 2: Verify scaling-law and GPT tables**

Check every GPT-3 zero/one/few-shot cell and label, Kaplan/Hoffmann equations, coefficients, model counts, compute relations, parameter/token optima, and all unit conversions.

Expected: table cells are checked individually even when the table receives one summary verdict.

- [ ] **Step 3: Verify instruction-tuning, alignment, reasoning, and continual-pretraining quantities**

Check dataset/task counts, annotator or prompt counts, reward/training stages, benchmark deltas, replay ratios, token budgets, and comparative multipliers.

Expected: claims supported only qualitatively are not upgraded to numerical correctness.

- [ ] **Step 4: Verify biomedical models, architecture, context, and tokenization quantities**

Check parameter counts, corpus sizes, sequence lengths, efficiency factors, vocabulary sizes, and tokenizer fragmentation claims.

Expected: all remaining language-modeling ledger items are closed or explicitly `not found`.

### Task 4: Audit Corpus, Annotation, Ontology, and Knowledge-Pretraining Quantities

**Files:**
- Read: `sources/related_works/corpus_annotation.tex`
- Modify: `docs/reviews/2026-07-19-related-work-quantitative-audit.md`

**Interfaces:**
- Consumes: corpus/ontology ledger entries and primary evidence.
- Produces: verdicts that separate publication-time counts from live versioned counts.

- [ ] **Step 1: Verify web-corpus and curation quantities**

Check crawl sizes, document/token counts, language/domain proportions, filtering retention, deduplication effects, contamination rates, and corpus date ranges.

Expected: decimal/binary storage units and document/token units are never conflated.

- [ ] **Step 2: Verify biomedical and French corpus quantities**

Check article/note counts, word/token counts, institution counts, time spans, and access statistics against primary corpus documentation.

Expected: each approximation states whether it matches the cited release.

- [ ] **Step 3: Verify ontology statistics**

Check SNOMED CT, ICD, MeSH, UMLS, and other ontology counts using the exact release named by the thesis or the current official release if the prose presents them as current.

Expected: concepts, codes, terms, strings, relations, and source vocabularies are treated as different units.

- [ ] **Step 4: Verify graph and knowledge-pretraining quantities**

Check entity/relation counts, ontology counts, negative-sampling details, synthetic-data volumes, and any model/corpus scale comparison.

Expected: all corpus/annotation ledger items are closed or explicitly `not found`.

### Task 5: Audit Clinical Information Extraction Quantities

**Files:**
- Read: `sources/related_works/clinical_ie.tex`
- Modify: `docs/reviews/2026-07-19-related-work-quantitative-audit.md`

**Interfaces:**
- Consumes: clinical-IE ledger entries and primary evidence.
- Produces: verdicts for benchmark, model, task, and evaluation quantities.

- [ ] **Step 1: Verify NER and coding benchmark quantities**

Check corpus sizes, entity/category counts, train/dev/test splits, label inventories, code-space sizes, and reported metrics.

Expected: micro/macro/weighted, exact/relaxed, mention/document, and validation/test results are not interchanged.

- [ ] **Step 2: Verify entity-linking and zero-shot quantities**

Check candidate counts, benchmark composition, model size, number of entity types, label limits, and stated performance gaps.

Expected: GLiNER and comparator results are matched to the correct model variant, dataset, and evaluation regime.

- [ ] **Step 3: Verify synthetic-data and evaluation quantities**

Check annotation/generation volumes, privacy or utility rates, number of tasks/datasets, and metric formulas or edge-case conventions.

Expected: all clinical-IE ledger items are closed or explicitly `not found`.

### Task 6: Reconcile, Challenge, and Write the Report

**Files:**
- Read: `docs/reviews/2026-07-19-related-work-fidelity-audit.md`
- Read: `docs/reviews/2026-07-19-related-work-fidelity-audit-addendum.md`
- Modify: `docs/reviews/2026-07-19-related-work-quantitative-audit.md`

**Interfaces:**
- Consumes: all closed ledgers and previous reports.
- Produces: final traceable audit with no duplicate findings presented as new.

- [ ] **Step 1: Recheck every non-exact verdict independently**

Return to the primary table/appendix or official release page and test whether the discrepancy could be explained by a split, variant, metric, release, unit, rounding, or transcription convention.

Expected: no correction is recommended until these common confounders are ruled out.

- [ ] **Step 2: Cross-check repeated quantities across chapters**

Search model, corpus, ontology, and benchmark names appearing in more than one file and compare associated values and units.

Expected: cross-file inconsistencies receive one finding with all locations.

- [ ] **Step 3: Write calibrated findings**

For each issue, include severity, exact TeX location, current wording/value, primary evidence and locator, explanation, and a minimal safe replacement. Separate corrections from optional precision improvements.

Expected: the report can be acted on without reopening the research trail.

- [ ] **Step 4: Reconcile coverage totals**

Count ledger items by file and verdict; confirm the sum of verdict categories equals the total number of auditable claims.

Expected: the report states the candidate count, excluded non-claims, audited claim count, and unresolved count.

### Task 7: Verify the Deliverable and Source Preservation

**Files:**
- Read: `docs/reviews/2026-07-19-related-work-quantitative-audit.md`
- Read: the three active related-work TeX files

**Interfaces:**
- Consumes: final report and starting hashes.
- Produces: evidence that the report is complete and thesis sources were not changed by the audit.

- [ ] **Step 1: Validate report structure and links**

Run:

```bash
rg -n '^#|^##|https?://' docs/reviews/2026-07-19-related-work-quantitative-audit.md
```

Expected: methodology, coverage, findings, verified high-risk values, unresolved items, and primary-source links are present.

- [ ] **Step 2: Recompute source hashes**

Run:

```bash
shasum -a 256 sources/related_works/language_modeling.tex sources/related_works/corpus_annotation.tex sources/related_works/clinical_ie.tex
```

Expected: hashes match the start snapshot unless the user edited a file concurrently; any changed hash triggers a focused re-audit of the changed diff before delivery.

- [ ] **Step 3: Check repository scope**

Run:

```bash
git status --short -- sources/related_works docs/reviews/2026-07-19-related-work-quantitative-audit.md docs/superpowers/plans/2026-07-19-related-works-quantitative-audit.md
```

Expected: this audit created only the plan and report; it did not create a thesis-source modification.
