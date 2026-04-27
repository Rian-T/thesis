# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PhD thesis repository for Rian Touchent-Saad at Sorbonne Université / INRIA Paris (ALMAnaCH Team).

**Title:** "Public-Data Pretraining for Clinical Information Extraction: Methods under Scarcity and Privacy Constraints"

**Archive:** Nathan Godey's original thesis content is preserved in `_archive/` for reference.

## Build Commands

```bash
# Build the thesis
latexmk

# Clean auxiliary files
latexmk -c
```

The build uses **LuaLaTeX** with `--shell-escape`. On locale issues, prefix with `LC_ALL=C`.

## Current Status

### Chapters Done (draft)
- **Ch 1: Collecting Biomedical Text** — CamemBERT-bio corpus (biomed-fr). Hook, tables, vocab analysis, conclusion with cliffhanger to Ch 4.
- **Ch 2: Detecting Content Types** — Biomed-Enriched + BiaHS. Hook with TikZ figure, full method/results/discussion, 4 results tables, 5 figures, BiaHS as footnoted section.

### Next Steps
- **Ch 3: MC-Bio Corpus** — quality signals at scale for ModernCamemBERT-bio (from plan.tex slides Ch.3)
- **Ch 4: Encoder Models for French Biomedicine** — CamemBERT-bio pretraining/evaluation (the other half of the paper, split from Ch 1)
- **Ch 5-9** — placeholders
- **Remaining TODOs in Ch 1-2:** real PMC paragraph examples, annotation prompt in appendix, pipeline.pdf and curve_triple.pdf not yet restyled, BiaHS figure is PNG not PDF

### Key Decisions Made
- CamemBERT-bio paper split: corpus → Ch 1, pretraining/eval → Ch 4
- BiaHS is a section within Ch 2 (not its own chapter), footnoted as contribution to GAPeron
- Discussion chapters (Ch 5, Ch 7) have no underlying paper — they set up problems
- Preserve original paper text in article chapters; only add thesis framing
- No "We have introduced X" in conclusions — conclude on insight, use cliffhangers
- Bibliography is active (`\bibliography{thesis}` uncommented)

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
├── related_works/               # Related works - DRAFTS in .md
│   ├── language_modeling.tex
│   ├── corpus_annotation.tex
│   └── clinical_ie.tex
├── part_1/                      # Building a Biomedical Corpus
│   ├── analysis_lm.tex          # Orchestration file
│   ├── chapter1/article.tex     # DONE — CamemBERT-bio corpus
│   ├── chapter2/article.tex     # DONE — Biomed-Enriched + BiaHS
│   └── chapter3/article.tex     # TODO — MC-Bio corpus
├── part_2/                      # Pretraining Language Models
│   ├── extensions_lm.tex        # Orchestration file
│   ├── chapter4/article.tex     # NEXT — CamemBERT-bio pretraining
│   ├── chapter5/article.tex     # TODO — decoder PT discussion
│   └── chapter6/article.tex     # TODO — ModernCamemBERT-bio
├── part_3/                      # Adapting to Clinical Tasks
│   ├── clinical_tasks.tex       # Orchestration file
│   ├── chapter7/article.tex     # TODO — fine-tuning limits discussion
│   ├── chapter8/article.tex     # TODO — frenchmed-gliner
│   └── chapter9/article.tex     # TODO — OntoBook
├── conclusion.tex
└── appendix.tex
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
| `guidelines/writing-guide.md` | Voice & tone (academic "we", measured, no hype), sentence structure, tense rules, hedging, precision with numbers, transitions, paragraph length, word choice, thesis structure (intro/RW/research chapters/conclusion anatomy), section-by-section templates, LaTeX formatting conventions (`\Cref{}`, `\paragraph{}`, `\section*{Conclusion}`), hard rules (no spoiling in RW, no redundancy, always back claims with numbers), chapter type rules (article vs discussion), hook patterns, conclusion patterns (no "we introduced X", use cliffhangers) |
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
