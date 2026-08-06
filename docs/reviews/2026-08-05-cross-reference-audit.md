# Manuscript cross-reference audit

## Scope

This audit covers the active LaTeX sources included from `thesis.tex`. It checks
both whether references resolve and whether the target actually contains the
figure, table, chapter, section, or appendix material promised by the text.

The manuscript was rebuilt from scratch with `latexmk -g`. The resulting log
contains no undefined-reference, multiply-defined-label, or duplicate-label
warning. The only label-like missing target found by source analysis,
`chap:rw-corpus/lm/ie`, occurs inside a comment and is not active LaTeX.

The manuscript is therefore mechanically clean. The issues below are semantic:
the links compile, but their targets do not fully support the surrounding claim.

## References that should be corrected

### 1. Content-type prompt points to the GLiNER prompt

**Source:** `sources/appendix.tex`, near line 31.

**Current claim:** the full French content-type annotation prompt and schema are
reproduced in `app:gliner-prompts`.

**Problem:** `app:gliner-prompts` contains the open-vocabulary extraction prompt
and schema used for the generalist span annotations in Part IV. It is not the
content-type prompt used to annotate Biomed-Enriched.

**Correction:** either reproduce the content-type prompt and schema in
`app:content-types` and point there, or remove the claim that they are reproduced.

### 2. Chapter 2 promises material absent from its appendix

**Source:** `sources/part_1/chapter2/article.tex`, near line 147.

**Current claim:** the full Llama-3.1 prompt and annotation schema are given in
`app:content-types`.

**Problem:** that appendix gives the annotation and classifier configuration, but
does not currently reproduce the full prompt and schema. The reference is
topically related but not substantial enough for what the sentence promises.

**Correction:** add the actual prompt and schema to `app:content-types`, or weaken
the sentence to say that the appendix gives implementation/configuration details.

### 3. Chapter 17 points to the wrong evaluation appendix

**Source:** `sources/part_3/chapter7/article.tex`, near line 32.

**Current claim:** the evaluation type bank and training settings for the lymphoma
eCRF evaluation are given in `app:eval-details`.

**Problem:** `app:eval-details` documents MC-bio-embed/MC-bio-gliner training and
the familiar versus benchmark-absent type bank used in Chapter 16. It does not
document the Chapter 17 longitudinal eCRF protocol.

**Correction:** remove this sentence, or create a dedicated appendix containing
the actual Chapter 17 settings and point to it.

### 4. The reference-free evaluation is attributed to the wrong chapter

**Source:** `sources/appendix.tex`, near line 714.

**Current claim:** the common/novel-description reference-free evaluation belongs
to `chap:evaluation`.

**Problem:** this experiment appears in Chapter 16 (`chap:architectures`), under
“Transfer to New Descriptions”, not in Chapter 17 (`chap:evaluation`).

**Correction:** point to `chap:architectures`. A dedicated label on the “Transfer
to New Descriptions” section would be even more precise.

### 5. The lymphoma appendix is described as a complete record

**Sources:**

- `sources/part_3/chapter9/article.tex`, near line 109;
- `sources/appendix.tex`, near lines 649–650.

**Current claim:** `app:lymphoma-dossier` shows one generated record/dossier “in
full”.

**Problem:** the appendix contains a structured timeline, one generated clinical
document, and a subset of extracted fields. It does not reproduce the complete
longitudinal record.

**Correction:** call it an “extended example” and state exactly what is shown, or
expand the appendix so that it really contains the full record.

### 6. The TABIB appendix points to an overly broad chapter label

**Source:** `sources/appendix.tex`, near line 775.

**Current claim:** the appendix supports the TABIB study of
`sec:conclusion-evaluation`.

**Problem:** that label identifies the whole “A New Problem” chapter. The existing
label `sec:conclusion-tabib` identifies the TABIB section itself and is the
substantive target for the protocol details in this appendix.

**Correction:** replace `sec:conclusion-evaluation` with
`sec:conclusion-tabib`.

### 7. A table range implies a missing B3 table

**Source:** `sources/appendix.tex`, near line 842.

**Current claim:** the text refers to Tables B1–B5 by using a range from
`tab:conclusion-tabib-b1-sensitivity` to
`tab:conclusion-tabib-b5-sensitivity`.

**Problem:** the source contains B1, B2, B5, and B4 sensitivity tables, but no B3
table. Both endpoints exist, so LaTeX accepts the range, but the prose implies a
continuous B1–B5 series that is not present. The source order is also not numeric.

**Correction:** add and order B3 if it is intended to exist, or explicitly list
the tables that are actually present instead of using a range. For TABIB details,
the current manuscript should be treated as authoritative when older Jean-Zay
artefacts differ.

## Result for the remaining references

All other active chapter, section, appendix, figure, and table references resolve.
The cross-links to the CLM-pretraining appendix, OntoBook appendix, GLiNER prompt,
and TABIB protocol appendix point to substantive matching material. The figure and
table references inspected in the experimental chapters also match their captions
and surrounding claims.

No manuscript source was changed during this audit.
