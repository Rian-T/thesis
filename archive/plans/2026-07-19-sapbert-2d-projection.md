# SapBERT 2D Projection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the ambiguous SapBERT force-arrow diagram with a conservative, readable schematic 2D embedding projection.

**Architecture:** Keep `fig:corpus-contrastive`, its position, SapBERT-only scope, medical examples, and thesis visual language. Use one lightly framed projection plane with a compact green synonym cluster and one spatially separated orange negative; explicitly mark the geometry as illustrative and not to scale.

**Tech Stack:** LaTeX, TikZ, existing thesis palette, LuaLaTeX, Poppler rendering tools.

## Global Constraints

- Modify only the SapBERT TikZ, its caption, the sentence that introduces the figure, the existing design spec, implementation plan, and change report.
- Do not add axes, graduations, coordinates, numerical distances, trajectories, or a CODER branch.
- Preserve `fig:corpus-contrastive` and cite only `liu2021sapbert` in its caption.
- Preserve the existing `term`, `neg`, `lbl`, thesis palette, rounded-corner, and sans-serif conventions.
- Do not modify `thesis.bib`, any bibcheck whitelist, or unrelated thesis prose.
- Do not commit; changes stay directly in the current worktree.

---

### Task 1: Replace the SapBERT diagram with a schematic 2D projection

**Files:**
- Modify: `sources/related_works/corpus_annotation.tex:472-516`

**Interfaces:**
- Consumes: the existing SapBERT-only prose, `fig:corpus-contrastive`, and thesis TikZ colors.
- Produces: one axis-free schematic projection with a compact same-concept cluster and a separated negative concept.

- [x] **Step 1: Replace the force-arrow styles and layout**

Use a pale rounded plane, a soft green cluster halo, readable rounded term chips, and an orange negative chip. The three synonym chips must be spatially close; `Type 1 diabetes mellitus` must be clearly separated. Do not draw training-force arrows.

- [x] **Step 2: Add explicit interpretive safeguards**

Add the labels `illustrative 2D embedding projection`, `not to scale`, `same UMLS concept`, and `different but related concept / negative pair`. Keep all text inside the plane without overlap.

- [x] **Step 3: Narrow the prose and caption**

Change the introducing sentence to say that the figure gives a schematic 2D projection of SapBERT's synonym-alignment objective. Change the caption to state that the projection is illustrative and not to scale, while retaining only `\citep{liu2021sapbert}`.

- [x] **Step 4: Run structural assertions**

Run:

```bash
sed -n '472,520p' sources/related_works/corpus_annotation.tex
rg -n 'illustrative 2D embedding projection|not to scale|same UMLS concept|different but related concept' sources/related_works/corpus_annotation.tex
```

Expected: all four safeguards are present; no `pull`, `push`, or CODER citation appears in the figure caption.

### Task 2: Compile and inspect the rendered figure

**Files:**
- Verify: `sources/related_works/corpus_annotation.tex`
- Verify: `/private/tmp/thesis-build-clean/thesis.pdf`
- Update: `docs/reviews/2026-07-19-knowledge-pretraining-tikz-change-report.md`

**Interfaces:**
- Consumes: the completed TikZ change.
- Produces: compilation evidence, a page render, and an updated precise report.

- [x] **Step 1: Compile in the clean temporary build directory**

Run the existing LuaLaTeX verification command with writable `TEXMFVAR`, `TEXMFCACHE`, and `XDG_CACHE_HOME` paths.

Expected: exit code 0 and a 261-page PDF.

- [x] **Step 2: Render and inspect the SapBERT page**

Render physical PDF page 81 at 180 dpi with `pdftoppm`, then inspect the PNG.

Expected: cluster and negative are immediately distinguishable; labels do not overlap or clip; the figure matches the adjacent TikZ visual language.

- [x] **Step 3: Update the change report**

Record the switch from force arrows to an axis-free schematic 2D projection, its factual safeguards, and the fresh compilation/render outcome.

- [x] **Step 4: Run final source checks**

Run `git diff --check` on the TeX, spec, plan, and report, and inspect the final diff.

Expected: no whitespace errors and no unrelated source changes.
