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

## Document Structure

- **Main file:** `thesis.tex`
- **Document class:** `mimosis.cls` (KOMA-script based)
- **Bibliography:** `thesis.bib` with `acl_natbib` style (commented out until citations are added)

### Content Organization

```
sources/
├── title/title.tex              # Title page (French) - DONE
├── abstract.tex                 # Abstract - TODO
├── introduction.tex             # Introduction with Sutton quote - TODO
├── related_works/               # Related works
│   ├── language_modeling.tex
│   ├── representation_learning.tex
│   └── representation_analysis.tex
├── part_1/                      # Part 1
│   ├── analysis_lm.tex          # Orchestration file
│   ├── chapter1/article.tex
│   ├── chapter2/article.tex
│   └── chapter3/article.tex
├── part_2/                      # Part 2
│   ├── extensions_lm.tex        # Orchestration file
│   ├── chapter4/article.tex
│   ├── chapter5/article.tex
│   └── chapter6/article.tex
├── conclusion.tex
└── appendix.tex
```

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
2. **Part titles:** In `thesis.tex`, update `\part[Part 1]` and `\part[Part 2]`
3. **Chapter titles:** In `sources/part_*/analysis_lm.tex` and `extensions_lm.tex`

## Mandatory Reading Before Writing

**Read these files before drafting any thesis content.** They define voice, structure, formatting, and visual style.

| File | What it covers |
|------|---------------|
| `guidelines/writing-guide.md` | Voice & tone (academic "we", measured, no hype), sentence structure, tense rules, hedging, precision with numbers, transitions, paragraph length, word choice, thesis structure (intro/RW/research chapters/conclusion anatomy), section-by-section templates, LaTeX formatting conventions (`\Cref{}`, `\paragraph{}`, `\section*{Conclusion}`), hard rules (no spoiling in RW, no redundancy, always back claims with numbers) |
| `guidelines/visual-style.md` | Table style (booktabs, siunitx, colored group headers), figure style (bar charts, line plots, pipeline diagrams), color palette reference, do/don't quick reference |
| `guidelines/style-proposals.pdf` | Visual reference PDF with validated styles: tables (A1/A2/A3), bar charts (A/B/D), line plots (A markers/B confidence band), pipelines (A horizontal/B vertical), all on Palette 4 (Lavender & Lime) |
| `thesis-style.sty` | **Centralized style config** — all colors (`ThesisPrimary`, `ThesisSecondary`, `ThesisTertiary`), pgfplots presets (`thesis bar`, `thesis line`, `bar primary`, `line primary`, etc.), TikZ pipeline styles (`pipe input`, `pipe process`, `pipe result`), table helpers (`\tablegroup{N}{Title}`). Changing colors/styles here updates the entire manuscript. |

## Notes

- French front matter, English body text
- Cross-references use `cleveref` (`\Cref{}`)
- Add images in `sources/part_*/chapter*/imgs/`
- **All figures/tables must use `thesis-style.sty` presets** — never define ad-hoc colors or styles in chapter files
