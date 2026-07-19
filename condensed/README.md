# Condensed thesis (10% version)

A standalone, short version of the thesis: **same class, same preamble, same
`thesis-style.sty`, same figures** — only the content is condensed. Built in
English first (the thesis's own language, easiest to cut from), translated to
French as the **last** step.

## Target length

Body of the full thesis (Introduction → Conclusion, **excluding** appendices,
bibliography, glossary, index) = **p13–199 = 187 pages**. Target = 10% =
**~18–20 pages of content**.

## Method (how to condense to 10% well)

It is a *résumé substantiel*, not a mini-thesis. It follows the thesis spine
(one section per part) and for each part states, in this order:

1. the **problem / question**,
2. the **core idea** of the method (one sentence),
3. the **headline result** (the load-bearing number),
4. the **take-away** (the insight the chapter closes on),

plus the **single most emblematic figure or table** of that part. Everything
else — literature depth, method details, ablations, secondary results, hedging —
is dropped.

Rules:

- **Prose is copy-pasted verbatim** from the thesis and cut down (never
  paraphrased). This keeps Rian's voice and means the final French pass
  translates already-approved sentences.
- **Figures/tables/schemas are reused as-is** by `\input` of the same fragment
  files. Root-relative paths (`sources/…`, `plots/…`, `thesis.bib`, `mimosis`,
  `thesis-style`) resolve via `latexmkrc` (`TEXINPUTS=..//`), so nothing is
  duplicated and figures render identically.
- The abstract is already the 1-page compression of the whole thesis — it is the
  natural backbone; each abstract claim is expanded with its chapter's key
  paragraph + figure.
- One figure/table per part at most; ~6–8 across the whole document.

## Page budget (target ~19 pp of content; allocate by importance, not by source length)

| Part | Source pp | Condensed target | Figures |
|------|-----------|------------------|---------|
| Introduction + contributions | 14 | ~1.5 | 0 |
| What Is Biomedical Text | 14 | ~2 | 1 (the signature case in three registers) |
| Related Works | 54 | ~1 | 0 |
| Part 1 — Building a Corpus | 28 | ~3 | 1–2 |
| Part 2 — Pretraining | 34 | ~3.5 | 1–2 |
| Part 3 — Clinical Tasks | 26 | ~3.5 | 1–2 |
| Conclusion + the take | 17 | ~2.5 | 0–1 |

## Build

```bash
cd condensed && LC_ALL=C latexmk summary_en.tex
```

Isolated in this folder → its aux files never shadow the main thesis build.

## Open decision: the full-page part openers

The 7 illustrated part-opener plates + `twoside` blank versos consume ~14 pages
on their own, before any content — the whole 10% budget. Reproducing them
verbatim is incompatible with a 19-page content target. Decision pending on how
to handle the part chrome (compact colored headers vs. keep the plates and run
longer vs. `oneside`).

## Rules learned (Rian, 2026-07-18)

- **Verbatim only.** Every sentence is verbatim (lightly adapted for flow) from the
  real thesis `.tex` — never paraphrase, never invent a fact or a number.
- **Reuse floats, never create.** Figures/tables/schemas are copied as-is or
  `\input`; no new plot/table/schema is ever authored. A float is worth 1000 words —
  favour one over prose, but don't force one where it doesn't fit (arbitrate).
- **`[H]`, not `[t]`.** All reused floats use `[H]` (pinned in place) so they stay
  in their own part and never drift; put a sentence between any two adjacent floats.
- **The body must end on text**, never on a figure/table. `\FloatBarrier` before the
  closing take guarantees it; the last words stay "a \textit{Science of Evaluation}."
- **Target = 19 printed pages of content**, excluding the bibliography.

## Status (2026-07-18)

- [x] Folder + isolated build; faithful de-slimmed `mimosis` clone
- [x] All 7 parts populated (verbatim-cut + reused floats)
- [x] **19 printed content pages**, ends on the take, bib on top (p25–26)
- [x] Clean: 0 undefined, 0 `??`, 0 `(?)`, 0 missing graphics, no overfull >18pt
- [ ] Final read-through with Rian
- [ ] Translate to French (last step)
