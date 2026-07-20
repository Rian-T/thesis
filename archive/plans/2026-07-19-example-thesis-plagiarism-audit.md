# Example-Thesis Plagiarism Audit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Run a one-off, reproducible exact-and-fuzzy text-similarity audit between every `sources/**/*.tex` file and the three PDFs under `exemples/`, then deliver a manually reviewed Markdown report.

**Architecture:** Poppler extracts PDF text with page separators; `detex -n -1` extracts thesis prose while retaining file and line provenance. A temporary Python standard-library analyzer normalizes both corpora, finds maximal exact token matches, retrieves fuzzy sentence candidates through rare-token overlap, and writes machine-readable JSON for manual review.

**Tech Stack:** Poppler `pdftotext`, OpenDetex `detex`, Python 3.14 standard library, `unittest`, Markdown.

## Global Constraints

- Compare all `sources/**/*.tex` files with exactly the three PDFs currently under `exemples/`.
- Do not modify TeX, BibTeX, plot code, generated figures, or PDFs.
- Create no permanent checker; all executable artifacts live under `tmp/plagiarism-audit/`.
- Report exact matches of at least 12 normalized words and manually inspect all high-scoring fuzzy candidates.
- Preserve thesis file/line and example document/page provenance.
- Do not claim that this closed-corpus audit certifies absence of plagiarism against external literature.
- Do not stage or commit files; repository-history modification was not authorized.

---

### Task 1: Build and test the temporary analyzer

**Files:**
- Create: `tmp/plagiarism-audit/audit.py`
- Create: `tmp/plagiarism-audit/test_audit.py`

**Interfaces:**
- Consumes: `detex -n -1` records and `pdftotext` output containing form-feed page separators.
- Produces: `normalize(text) -> list[str]`, `maximal_exact_matches(thesis_tokens, example_tokens, min_words) -> list[Match]`, and `fuzzy_candidates(thesis_segments, example_segments) -> list[Candidate]`.

- [ ] **Step 1: Write focused failing tests**

Create `tmp/plagiarism-audit/test_audit.py` with tests that assert:

```python
import unittest
from audit import normalize, maximal_exact_matches

class AuditTests(unittest.TestCase):
    def test_normalization_repairs_pdf_hyphenation(self):
        self.assertEqual(normalize("represen-\ntations"), ["representations"])

    def test_exact_detector_finds_twelve_word_copy(self):
        copied = "this deliberately distinctive passage contains exactly twelve ordinary words for reliable matching"
        thesis = normalize("start " + copied + " finish")
        example = normalize("before " + copied + " after")
        matches = maximal_exact_matches(thesis, example, min_words=12)
        self.assertEqual(len(matches), 1)
        self.assertGreaterEqual(matches[0].length, 12)

    def test_exact_detector_rejects_short_overlap(self):
        shared = "a language model predicts the next token from context"
        self.assertEqual(
            maximal_exact_matches(normalize(shared), normalize(shared), min_words=12),
            [],
        )

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests and confirm the red state**

Run:

```bash
cd tmp/plagiarism-audit
python3 -m unittest -v test_audit.py
```

Expected: import failure because `audit.py` does not yet exist.

- [ ] **Step 3: Implement normalization, provenance loaders, and exact matching**

Create `tmp/plagiarism-audit/audit.py` using only the standard library. It must:

- case-fold Unicode text;
- join `word-\ncontinuation` PDF césures before tokenization;
- tokenize Unicode words while retaining apostrophes;
- parse `detex -n -1` prefixes into `(file, line)` provenance;
- split PDF text on `\f` to preserve page numbers;
- index 12-token example shingles;
- extend each hit left and right into a maximal exact match;
- merge duplicate or overlapping hits;
- retain original readable context for report rendering.

Use immutable records with these exact fields:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Token:
    value: str
    document: str
    location: int

@dataclass(frozen=True)
class Match:
    thesis_start: int
    example_start: int
    length: int
```

- [ ] **Step 4: Implement fuzzy candidate retrieval**

Segment both corpora into prose windows of 18–90 words. Remove a fixed English stop-word set only for candidate retrieval, never for the displayed text. Index content tokens occurring in no more than 1% of example windows. Retrieve pairs sharing at least six content tokens, then score them with:

```python
sequence_ratio = difflib.SequenceMatcher(None, thesis_values, example_values).ratio()
content_jaccard = len(thesis_content & example_content) / len(thesis_content | example_content)
score = 0.65 * sequence_ratio + 0.35 * content_jaccard
```

Retain pairs with `sequence_ratio >= 0.62`, `content_jaccard >= 0.35`, and at least 18 words on each side. Deduplicate candidates pointing to the same thesis and PDF context.

- [ ] **Step 5: Run the unit tests and a syntax check**

Run:

```bash
cd tmp/plagiarism-audit
python3 -m unittest -v test_audit.py
python3 -m py_compile audit.py
```

Expected: three tests pass; syntax check exits zero.

### Task 2: Extract the corpora and execute both detectors

**Files:**
- Create: `tmp/plagiarism-audit/extracted/*.txt`
- Create: `tmp/plagiarism-audit/thesis-detex.txt`
- Create: `tmp/plagiarism-audit/raw-results.json`
- Create: `tmp/plagiarism-audit/run-summary.txt`

**Interfaces:**
- Consumes: temporary analyzer from Task 1 and all audit inputs.
- Produces: complete raw results with context and provenance for manual classification.

- [ ] **Step 1: Extract the three PDFs with page separators**

Run `pdftotext -layout` separately for each PDF and verify that each output contains form-feed page separators and more than 50,000 words.

- [ ] **Step 2: Extract every thesis source with provenance**

Run `detex -n -1` once per sorted `sources/**/*.tex` file and concatenate the outputs into `tmp/plagiarism-audit/thesis-detex.txt`. Verify that all 52 discovered source files are represented and that no input outside `sources/` appears.

- [ ] **Step 3: Run the analyzer**

Run:

```bash
python3 tmp/plagiarism-audit/audit.py \
  --thesis-root sources \
  --examples-root exemples \
  --work-dir tmp/plagiarism-audit \
  --min-exact-words 12 \
  --json tmp/plagiarism-audit/raw-results.json \
  --summary tmp/plagiarism-audit/run-summary.txt
```

Expected: exit zero; JSON contains `inputs`, `exact_matches`, `fuzzy_candidates`, and `statistics` keys.

- [ ] **Step 4: Check detector sensitivity**

Inject a synthetic 20-word fixture only under `tmp/plagiarism-audit/fixtures/`, rerun against the fixture, and verify that the exact detector reports it. Verify that an unrelated synthetic paragraph produces no exact result at the 12-word threshold. Remove neither fixture until the final report is verified.

### Task 3: Manually classify candidates and write the report

**Files:**
- Create: `docs/reviews/2026-07-19-example-thesis-plagiarism-audit.md`
- Read: `tmp/plagiarism-audit/raw-results.json`
- Read: thesis source and PDF contexts referenced by every retained candidate.

**Interfaces:**
- Consumes: raw exact and fuzzy results.
- Produces: evidence-backed, closed-corpus audit report with no automatic accusation.

- [ ] **Step 1: Rank and inspect exact matches**

Sort exact matches by descending word count. Inspect every match of at least 20 words, every 12–19-word match whose wording is distinctive, and any match occurring only in one example thesis. Confirm each locator against the TeX and the relevant PDF page.

- [ ] **Step 2: Rank and inspect fuzzy candidates**

Sort by combined score and inspect all retained candidates. Record which are continuous light edits, common definitions, shared quotations, titles, institutional boilerplate, citation artifacts, or normalization failures.

- [ ] **Step 3: Write the report**

The report must contain:

- corpus inventory and exact source hashes;
- extraction/token statistics;
- thresholds and known limitations;
- count of raw and retained candidates per detector and per example thesis;
- side-by-side excerpts for every `préoccupant` or `à vérifier` result;
- a summarized register of conventional similarities and false positives;
- an explicit distinction between “no issue found in this corpus” and proof of originality.

- [ ] **Step 4: Verify the report and manuscript immutability**

Run fresh checks that:

- all three example PDFs and every `sources/**/*.tex` input are represented;
- all cited line/page locators exist;
- report counts reconcile with the reviewed JSON;
- `git diff --exit-code -- sources thesis.tex thesis.bib plots` succeeds.

Do not compile the thesis: the audit does not modify it.
