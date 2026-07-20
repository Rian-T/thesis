# Thesis Abstracts Revision Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Correct the two factual ambiguities in the English thesis abstract and rewrite the French abstract in the author's established French scientific style.

**Architecture:** Keep the five-paragraph argument and the reported results unchanged. Treat `sources/abstract.tex` as the single canonical source for the manuscript and ADUM, using the CamemBERT-bio TALN 2023 paper as the French style reference.

**Tech Stack:** LaTeX, `latexmk`, Poppler `pdftotext`, Unix character-counting tools.

## Global Constraints

- Modify only `sources/abstract.tex`.
- Keep each language at or below 4,000 characters, including spaces and line breaks.
- Preserve factual parity between English and French.
- Keep the English prose unchanged except where accuracy or clarity requires edits.
- Write the French as autonomous scientific prose in the style of the CamemBERT-bio TALN 2023 paper.

---

### Task 1: Establish the French style constraints

**Files:**
- Read: `publications/CamemBERT-bio---TALN-RECITAL-2023/camembert-bio.tex`
- Read: `sources/abstract.tex`

**Interfaces:**
- Consumes: the approved design in `docs/superpowers/specs/2026-07-18-thesis-abstracts-design.md`.
- Produces: a concrete style checklist used in Task 2.

- [ ] **Step 1: Read the article's résumé, introduction, methods, results, and conclusion**

Run:

```bash
sed -n '49,124p' publications/CamemBERT-bio---TALN-RECITAL-2023/camembert-bio.tex
sed -n '126,245p' publications/CamemBERT-bio---TALN-RECITAL-2023/camembert-bio.tex
```

Expected: French prose showing direct problem statements, explicit methodological subjects, concrete result verbs, and restrained transitions.

- [ ] **Step 2: Apply the resulting checklist to the draft**

Use these constraints during rewriting: prefer `nous` for contributions, use `permet`/`améliore`/`montre` for results, avoid literal English syntax, retain established terms such as `pré-entraînement`, `modèle de langue`, `jeu d'évaluation`, and `F-mesure`, and explain technical relations before introducing their consequence.

### Task 2: Revise the bilingual abstract

**Files:**
- Modify: `sources/abstract.tex:6-31`

**Interfaces:**
- Consumes: the style checklist from Task 1 and the five-paragraph structure already in `sources/abstract.tex`.
- Produces: final English and French abstract blocks with matching claims.

- [ ] **Step 1: Make the minimal English corrections**

Change the opening so the models are designed for local use rather than claimed to have been deployed. Separate the released French corpora from the PubMed Central analysis, and state that the two million clinical-case passages are multilingual and predominantly English.

- [ ] **Step 2: Rewrite the French as an autonomous text**

Preserve the same five moves: clinical-data constraint; public corpora and paragraph selection; compact encoder pretraining; open-vocabulary extraction and synthetic records; conclusion and real-record limitation. Replace calques with idiomatic French scientific formulations and use `F-mesure sur les valeurs` rather than an unexplained English `value-F1` expression.

- [ ] **Step 3: Inspect the diff for factual drift**

Run:

```bash
git diff -- sources/abstract.tex
```

Expected: changes limited to the abstract prose; every number remains unchanged; no contribution is added or removed.

### Task 3: Verify ADUM compliance and rendering

**Files:**
- Verify: `sources/abstract.tex`
- Verify: `thesis.pdf`

**Interfaces:**
- Consumes: the revised blocks from Task 2.
- Produces: character counts below 4,000 and a successfully rendered bilingual abstract.

- [ ] **Step 1: Count both source blocks**

Run:

```bash
sed -n '6,14p' sources/abstract.tex | wc -m
sed -n '23,31p' sources/abstract.tex | wc -m
```

Expected: both counts are at most 4,000.

- [ ] **Step 2: Compile the thesis**

Run:

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error thesis.tex
```

Expected: exit status 0 and an updated `thesis.pdf`.

- [ ] **Step 3: Inspect the rendered abstracts**

Run:

```bash
pdftotext -f 3 -l 4 -layout thesis.pdf -
```

Expected: both abstracts render without broken punctuation, raw LaTeX, missing accents, or incorrect language switching.

- [ ] **Step 4: Run final source checks**

Run:

```bash
git diff --check -- sources/abstract.tex
git status --short
```

Expected: no whitespace errors; only the planned abstract change and pre-existing unrelated user files appear.
