# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PhD thesis repository for Rian Touchent-Saad at Sorbonne Université / INRIA Paris (ALMAnaCH Team).

**Title (working, still being iterated):** "Improving Clinical Information Extraction with Public-Data Pretraining" (active title page). Note: `\title{}`/`pdftitle` in `thesis.tex` and the title page currently disagree — reconcile before submission.

**Archive:** Nathan Godey's original thesis content is preserved in `_archive/` for reference.

## Build Commands

```bash
# Build the thesis
latexmk

# Clean auxiliary files
latexmk -c
```

The build uses **LuaLaTeX** with `--shell-escape`. On locale issues, prefix with `LC_ALL=C`.

## Bibliography Hallucination Check

A single hallucinated reference can cause a desk reject. `tools/verify_bib.py`
resolves every **cited** bib entry against real databases (Crossref by DOI,
arXiv by id, then OpenAlex / DBLP / Crossref by title) and flags any whose
metadata does not match a real publication.

```bash
make checkbib          # cited entries only (default), non-blocking report
make checkbib-all      # every entry in thesis.bib
make checkbib-strict   # exit 1 if any MISMATCH/NOT_FOUND (pre-submission gate)
```

- Verdicts: `VERIFIED` / `MISMATCH` (found but a field diverges — likely
  hallucination) / `NOT_FOUND` (possibly invented) / `SKIPPED` (whitelisted).
- It is **non-blocking by design**: it flags for human review, never edits the
  `.bib`. It validates that a reference is *real and accurate*, not that the
  *right* paper is cited in the right place (that stays a human job).
- False positives happen on poorly-indexed venues (French ATALA/TALN/DEFT
  workshops, e.g. `cardon_presentation_2020`). Add genuinely-unverifiable keys
  to `tools/bibcheck_whitelist.txt` — keep that list short and justified.
- Results are cached in `tools/.bibcheck_cache.json`, so re-runs are fast/offline.
- Run `make checkbib` after adding or editing any `\cite`d reference, and
  `make checkbib-strict` before any submission.

## Git Commit Conventions

These OVERRIDE any default Claude Code commit behavior:

- **Sole author is Rian.** Never add `Co-Authored-By` trailers (no Claude, no anyone). The git author config (`rian-t <rian.touchent@inria.fr>`) is already correct — do not change it.
- **Messages: minimal, telegraphic, dense.** Lowercase, no filler, no marketing slop. State exactly what changed (and why, if non-obvious) in as few words as possible. One-line subject; add a terse body only when several distinct changes need listing.
- Good: `dedup bib: drop 4 ontobook duplicate entries, ch6 -> canonical keys`
- Bad: `This commit improves the bibliography by carefully removing some duplicate entries that were found...`

## Current Status

Chapter↔label↔source map (labels are set in the part orchestration files, not in `article.tex`):

| Ch | `\label` | Title | Source paper |
|----|----------|-------|--------------|
| 1 | `chap:collecting` | Collecting Biomedical Text | CamemBERT-bio (corpus part) |
| 2 | `chap:quality` | Detecting Content Types | Biomed-Enriched + BiaHS (GAPeron) |
| 3 | `chap:mcbio` | Which Quality Signals Matter? | MC-Bio / biomed-fr-v2 (TALN 2026) |
| 4 | `chap:encoders` | Encoder Models for French Biomedicine | CamemBERT-bio (pretraining/eval) |
| 5 | `chap:objectives` | Beyond Masked Language Modeling | CLM Detour (COLM 2026) |
| 6 | `chap:ontobook` | Knowledge-Enriched Pretraining | OntoBook (LREC 2026) |
| 7 | `chap:limits` | Limits of Direct Fine-Tuning | discussion (no paper) |
| 8 | `chap:architectures` | Architectures for Low-Resource Extraction | frenchmed-gliner / MedEmbed (WIP) |
| 9 | `chap:synthetic` | Synthetic Data for Task Adaptation | OntoBook data + synthetic clinical reports (WIP) |

### NEW conceptual part "What is Biomedical Text?" (drafted June 2026, sits BEFORE Related Works)

`\part{What is Biomedical Text?}` in `thesis.tex`, between the Introduction and the Related Works part. Orchestration `sources/biomedical_text/biomedical_text.tex` `\input`s three short chapters that form ONE argument (a triptych), arc **RARITY → ABUNDANCE**. The same case (a myocardial infarction) opens each chapter as a figure, in three registers, with parallel one-sentence captions ("... myocardial infarction"):

- `clinical.tex` (`chap:bt-clinical`, "Clinical Text"): the note is a sublanguage (Harris→Sager→Friedman), optimally compressed (Anderson-Sager + Grice/Sperber-Wilson + Stalnaker common ground), performative (Austin/Searle, "DNR"), one-line Foucault; then the French reality (no shareable real corpus; CAS-vs-PARHAF register dispute) and the personal-data reason for privacy; bridges to scientific. Figure = synthetic de-identified discharge note.
- `scientific.tex` (`chap:bt-scientific`, "Scientific Text"): genre as social action (Miller), CARS/gap (Swales), IMRAD is recent + real data (Sollaci 1297 articles), SOAP contrast (Weed), metadiscourse/hedges (Hyland), quantitative register (Biber) + phraseology (Nwogu/Luzón), one-line Latour, Friedman punchline (abundance ≠ substitutability). Figure = real HAL passage on post-infarction mitral insufficiency (from `rntc/mc-bio-corpus`).
- `web.tex` (`chap:bt-web`, "Lay and Web Text"): Fleck (esoteric→exoteric), drug leaflets / *notices* (Directive 2001/83/EC, EMA QRD template), naming variation (Wüster foil / Cabré / Gaudin), Temmerman (fuzzy concepts), UMLS many-to-many (Bodenreider, 2.5M names / 900k concepts), ontology-vs-text gap (Smith & Ceusters), one-line Hacking + Biber; synthesis closes the part ("public data for the clinic = crossing register + resolving names").

**Related Works ch "Language Models" (`chap:rw-lm`, `sources/related_works/language_modeling.tex`):** the **Introduction is now prose** — historical arc Markov (1913, *Onegin*) → Shannon (1948 entropy + n-gram samples; 1951 ~1 bit/char, figure `fig:lm-entropy`) → chain rule → Bengio (2003 neural) → Vaswani (2017). **The rest of the chapter is still a telegraphic French outline** (n-grams, neural, RNN, transformer, objectives, scaling, continual PT, biomed models, modern archis, tokenization) — TO PROSIFY next.

**Research substrate (gitignored `research/`).** Deep-research notes to READ before writing more: `clinical.md`, `scientific.md`, `web.md`, `french_clinical.md`, `lay_leaflets.md`, `rw_language_modeling.md`, plus `*_outline.md`. Built by Opus subagents from primary sources (curl). `research/` also holds PII screenshots + downloaded PDFs → **never commit it**. Scratch LaTeX buffers live in gitignored `sources/drafts/` (e.g. `example_clinical_note.tex` = the synthetic note source).

**Pending / next steps for this part:**
- **Figure 4.1 (lay panel) must be replaced**: the current Doctissimo dictionary excerpt is too encyclopedic/scientific for "lay". Use a genuinely lay text on "crise cardiaque" (de-identified patient forum post, or a prevention page in *vous* form). Options proposed; awaiting Rian's pick.
- Prosify the rest of the Language Models chapter (only the Introduction is prose so far).
- Other RW chapters (`corpus_annotation.tex`, `clinical_ie.tex`) are still telegraphic drafts.
- Run `make checkbib`: ~20 refs added this session; legal/web (`ec_directive_2001_83`, `ema_qrd_template`) and many books are whitelisted or will flag — review before submission.

**Conventions used here (follow them):** figures are forced to open the chapter via a non-float `\begin{center}…\captionof{figure}{…}\end{center}` (not `figure[t]`); text examples are TikZ boxes in thesis colours (`ThesisNeutral`/`ThesisPaper`/`ThesisInk`); captions are ONE sentence; new bib appended with `@comment` group headers; and `guidelines/working-with-rian.md` is the binding style/process guide (simple academic English, intuition before detail, introduce every name, data behind every number, no choppy/AI sentences, no em dashes).

### Chapters Done (draft)
- **Ch 1 (`chap:collecting`)** — biomed-fr corpus (413M words, ISTEX/CLEAR/E3C). Hook, tables, vocab analysis, cliffhanger to Ch 4.
- **Ch 2 (`chap:quality`)** — Biomed-Enriched (paragraph-level annotation, 2M clinical case paragraphs) + BiaHS as footnoted section. Full method/results/discussion. TODO: real PMC paragraph examples in the motivation figure; annotation prompt in appendix.
- **Ch 3 (`chap:mcbio`)** — biomed-fr-v2 (10B tokens, 6 sources). Content-type + quality-signal ablations (writing-quality/term filters *degrade* perf). Done.
- **Ch 4 (`chap:encoders`)** — CamemBERT-bio pretraining (+2.54 F1, 32× less CO2; DrBERT 20-pt loss = eval artifact). Done.

### Chapters Drafted But With Debt
- **Ch 5 (`chap:objectives`)** — CLM Detour (COLM 2026). Body is integrated, BUT §2.1 "When Decoder Continue-Pretraining Stops Working" is **entirely a placeholder** (notes in comments: BioMistral -0.9, Meditron 332 GPU-h, Dorfner, forgetting, data overlap). 3 figures still TODO: needle-in-haystack, CKA combined, freeze interventions.
- **Ch 6 (`chap:ontobook`)** — OntoBook (LREC 2026). Pasted verbatim, not yet thesis-ified: intro is the paper intro (not a hook); conclusion starts with "We presented…" (forbidden); uses `\section{Conclusion}` instead of `\section*`; tables/figures not yet on `thesis-style.sty`. Bib duplicates already fixed (now uses canonical keys: `lee_biobert_2019`, `gu_domain-specific_2022`, `martin-etal-2020-camembert`, `devlin_bert_2019`).

### To Write
- **Ch 7 (`chap:limits`)** — discussion chapter (no paper). Sets up why direct fine-tuning fails for clinical IE (label scarcity, thousands of classes, public-text-only) to motivate Ch 8-9.
- **Ch 8 (`chap:architectures`)** — frenchmed-gliner / MedEmbed. **Very WIP** (notes dated 2026-01-29 in `publications/frenchmed-gliner/paper/`): GLiNER2 bi-encoder, MedEmbed label encoder (ModernCamemBERT-base, 8192 ctx), ~1.5M training pairs (RDF/synthetic/persona), OntoBench-FR benchmark, MedEmbed-v4 = 32.9% avg (vs Solon 32.5%). No stable results yet.
- **Ch 9 (`chap:synthetic`)** — §OntoBook data (currently duplicates Ch 6's walk-generation prose — should `\Cref` to Ch 6 instead of repeating); §synthetic clinical reports is a placeholder (paper in progress).
- **Front matter** — abstract/résumé, introduction (with research questions), conclusion. Not started.

### Key Decisions Made
- CamemBERT-bio paper split: corpus → Ch 1, pretraining/eval → Ch 4
- BiaHS is a section within Ch 2 (not its own chapter), footnoted as contribution to GAPeron
- Ch 7 is a discussion chapter with no underlying paper — it sets up Ch 8-9. (The old decoder-CPT discussion now lives inside Ch 5 §2.1, the CLM Detour chapter.)
- Preserve original paper text in article chapters; only add thesis framing
- Paper appendices go INTO the chapter body (no manuscript-wide appendix for paper details)
- Related work for chapter-specific topics stays IN the chapter, not promoted to the manuscript-wide RW
- No "We have introduced X" in conclusions — conclude on insight, use cliffhangers
- Bibliography is active (`\bibliography{thesis}` uncommented)
- `publications/` contains live git clones of paper repos (kept up-to-date by re-cloning)

## Document Structure

- **Main file:** `thesis.tex`
- **Document class:** `mimosis.cls` (KOMA-script based)
- **Bibliography:** `thesis.bib` with `acl_natbib` style

### Content Organization

```
sources/
├── title/title.tex              # Title page (French) - DONE
├── abstract.tex                 # Abstract - TODO
├── introduction.tex             # Introduction with Sutton quote - DRAFT
├── related_works.tex            # Orchestration file (\input the 3 RW chapters)
├── related_works/               # live drafts in .tex (.md are older source drafts)
│   ├── language_modeling.tex
│   ├── corpus_annotation.tex
│   └── clinical_ie.tex
├── part_1/                      # Building a Biomedical Corpus
│   ├── analysis_lm.tex          # Orchestration file (sets chap labels)
│   ├── chapter1/article.tex     # DONE — biomed-fr corpus (chap:collecting)
│   ├── chapter2/article.tex     # DONE — Biomed-Enriched + BiaHS (chap:quality)
│   └── chapter3/article.tex     # DONE — MC-Bio / biomed-fr-v2 (chap:mcbio)
├── part_2/                      # Pretraining Language Models
│   ├── extensions_lm.tex        # Orchestration file (sets chap labels)
│   ├── chapter4/article.tex     # DONE — CamemBERT-bio pretraining (chap:encoders)
│   ├── chapter5/article.tex     # DRAFT (debt) — CLM Detour, COLM 2026 (chap:objectives); §2.1 placeholder, 3 figs TODO
│   └── chapter6/article.tex     # DRAFT (debt) — OntoBook, LREC 2026 (chap:ontobook); not thesis-ified yet
├── part_3/                      # Adapting to Clinical Tasks
│   ├── clinical_tasks.tex       # Orchestration file (sets chap labels)
│   ├── chapter7/article.tex     # TODO — fine-tuning limits discussion (chap:limits)
│   ├── chapter8/article.tex     # TODO — frenchmed-gliner / MedEmbed, WIP (chap:architectures)
│   └── chapter9/article.tex     # DRAFT (partial) — OntoBook data + clinical reports placeholder (chap:synthetic)
├── conclusion.tex
└── appendix.tex
```

### Publications (live clones)

```
publications/
├── CamemBERT_bio___LREC_COLING_2024/   # static — published paper
├── Biomed-Enriched---ACL-2026/         # git clone, pull to update
├── Gaperon_paper/                      # GAPeron (BiaHS section in Ch 2)
├── ModernCamemBERT-bio/                # git clone of colm2026-clm-detour
├── OntoBook/                           # git clone of kgllm2026 (LREC 2026)
├── TALN2026_MB-BIO/                    # MC-Bio corpus paper (TALN 2026) — Ch 3 source
├── frenchmed-gliner/                   # planning notes (paper TBD)
└── Internship_report/                  # archive
```

### Plots (centralized)

```
plots/
├── thesis_style.py              # Shared palette, rcParams, colormaps
├── __init__.py
└── chapter2/
    ├── decoder_curves.py        # 3-panel training curves
    ├── french_medmcqa.py        # FrenchMedMCQA performance
    ├── educational_scores.py    # Heatmap by type/domain
    └── *.pdf                    # Generated outputs
```

All plot scripts import `from plots.thesis_style import COLORS, apply_style, thesis_cmap`.

### Archive (Nathan's content for reference)

```
_archive/
├── nathan_introduction.tex
├── nathan_abstract.tex
├── related_works/
├── part_1/geographical/, softmax_bottleneck/, anisotropy/
└── part_2/headless/, manta/, kv_cache/
```

## Key Files to Modify

1. **Chapter content:** `sources/part_*/chapter*/article.tex`
2. **Part titles:** In `thesis.tex`, update `\part[...]`
3. **Chapter titles:** In orchestration files (`analysis_lm.tex`, `extensions_lm.tex`, `clinical_tasks.tex`)

## Mandatory Reading Before Writing

**Read these files before drafting any thesis content.** They define voice, structure, formatting, and visual style.

| File | What it covers |
|------|---------------|
| `guidelines/working-with-rian.md` | **Read first.** Process (scribe model: voice-first, draft in buffers, paragraph-by-paragraph, show PDF pages), deep-research subagent approach, and the recurring corrections: simple academic English, no choppy/AI sentences, intuition before detail, respect altitude (don't compare "from nowhere"), data behind every quantitative claim, one-sentence captions, privacy/PII rules, no em dashes |
| `guidelines/writing-guide.md` | **§7 "Plain style" is the recurring correction — read it every time: plain over clever, no "not X but Y" / constructed antithesis, simple words, write like the CamemBERT-bio chapter.** Voice & tone (academic "we", measured, no hype), sentence structure, tense rules, hedging, precision with numbers, transitions, paragraph length, word choice, thesis structure (intro/RW/research chapters/conclusion anatomy), section-by-section templates, LaTeX formatting conventions (`\Cref{}`, `\paragraph{}`, `\section*{Conclusion}`), hard rules (no spoiling in RW, no redundancy, always back claims with numbers), chapter type rules (article vs discussion), hook patterns, conclusion patterns (no "we introduced X", use cliffhangers) |
| `guidelines/visual-style.md` | Table style (booktabs, siunitx, colored group headers), figure style (bar charts, line plots, pipeline diagrams), color palette reference, do/don't quick reference |
| `guidelines/style-proposals.pdf` | Visual reference PDF with validated styles: tables (A1/A2/A3), bar charts (A/B/D), line plots (A markers/B confidence band), pipelines (A horizontal/B vertical), all on Palette 4 (Lavender & Lime) |
| `thesis-style.sty` | **Centralized LaTeX style** — all colors (`ThesisPrimary`, `ThesisSecondary`, `ThesisTertiary`), pgfplots presets, TikZ pipeline styles, table helpers (`\tablegroup{N}{Title}`). Changing colors here updates the entire manuscript. |
| `plots/thesis_style.py` | **Centralized Python style** — mirrors `thesis-style.sty` colors for matplotlib plots. All plot scripts import from here. |

## Notes

- French front matter, English body text
- Cross-references use `cleveref` (`\Cref{}`)
- `\PassOptionsToPackage{usenames,dvipsnames,table}{xcolor}` before `\documentclass` for `\rowcolor` support
- **All figures/tables must use `thesis-style.sty` presets** — never define ad-hoc colors or styles in chapter files
- **All Python plots must use `plots/thesis_style.py`** — never hardcode colors in plot scripts
- **Preserve original paper text** in article chapters — only add thesis framing (hooks, transitions, `\Cref{}`)
