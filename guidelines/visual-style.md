# Visual Style Guide — Figures & Tables

---

## 1. Table Style

Based on the Biomed-Enriched (ACL 2026) tables. Clean, professional, color-accented.

### 1.1 Required Packages

```latex
\usepackage{booktabs}       % \toprule, \midrule, \bottomrule (no vertical lines)
\usepackage{multirow}
\usepackage{colortbl}        % \rowcolor for section headers
\usepackage{siunitx}         % S columns for numerical alignment
\usepackage{threeparttable}  % Footnotes below tables
\usepackage{array}
```

### 1.2 Color Definition

```latex
\definecolor{TableSeparator}{RGB}{220, 226, 250}  % Light blue-lavender
```

### 1.3 Rules

- **Never use vertical lines.** Only horizontal rules: `\toprule`, `\midrule`, `\bottomrule`, `\cmidrule(lr){}`
- **Bold** best results, **underline** second-best
- Use `\small` or `\normalsize` inside tables — never `\tiny`
- Use `\resizebox{\textwidth}{!}{...}` for wide tables (full-page `table*`)
- Captions always **below** tables
- Every table has a `\label{tab:...}` and is referenced before it appears

### 1.4 Section Headers in Tables

For tables with logical groups (e.g. "Base Models" vs "Our Models"), use colored row separators:

```latex
\rowcolor{TableSeparator}
\multicolumn{N}{c}{\rule{0pt}{10pt}\textbf{Section Title}} \\[1pt]
```

### 1.5 Numerical Alignment

Use `siunitx` S-columns to align decimal points:

```latex
\begin{tabular}{l S[table-format=2.1] S[table-format=2.1]}
```

### 1.6 Table Footnotes

Use `threeparttable` for notes, abbreviation legends, or caveats:

```latex
\begin{threeparttable}[b]
  \begin{tabular}{...}
    ...
  \end{tabular}
  \begin{tablenotes}
    \small
    \item[$\dagger$] Trained on private clinical data.
    \item Abbreviations: ChemPr=ChemProt, Pheno=Phenotype.
  \end{tablenotes}
\end{threeparttable}
```

### 1.7 Template: Simple Results Table

```latex
\begin{table}[t]
\centering
\small
\begin{tabular}{lcc}
\toprule
\textbf{Model} & \textbf{F1} & \textbf{Precision} \\
\midrule
CamemBERT       & 70.50 & 70.12 \\
CamemBERT-bio   & \textbf{73.03} & \textbf{72.97} \\
\bottomrule
\end{tabular}
\caption{Results on CAS1 NER task.}
\label{tab:cas1-results}
\end{table}
```

### 1.8 Template: Multi-Group Comparison Table

```latex
\begin{table*}[t]
\centering
\small
\resizebox{\textwidth}{!}{
\begin{threeparttable}[b]
\sisetup{detect-weight=true}
\begin{tabular}{l S[table-format=2.1] S[table-format=2.1] S[table-format=2.1] S[table-format=2.1]}
\toprule
& \multicolumn{2}{c}{\textbf{Clinical Tasks}} & \multicolumn{2}{c}{\textbf{Biomedical Tasks}} \\
\cmidrule(lr){2-3} \cmidrule(lr){4-5}
\textbf{Model} & \textbf{CAS1} & \textbf{E3C} & \textbf{EMEA} & \textbf{MEDLINE} \\
\midrule
\rowcolor{TableSeparator}
\multicolumn{5}{c}{\rule{0pt}{10pt}\textbf{Baselines}} \\[1pt]
CamemBERT        & 70.5 & 67.6 & 74.1 & 65.7 \\
DrBERT           & 69.3 & 66.0 & 72.9 & 60.1 \\
\midrule
\rowcolor{TableSeparator}
\multicolumn{5}{c}{\rule{0pt}{10pt}\textbf{Our Models}} \\[1pt]
CamemBERT-bio    & \bfseries 73.0 & \bfseries 69.9 & \bfseries 76.7 & \bfseries 68.5 \\
\bottomrule
\end{tabular}
\begin{tablenotes}
  \small
  \item Bold indicates best result per column.
\end{tablenotes}
\end{threeparttable}
}
\caption{Comparison across clinical and biomedical NER benchmarks.}
\label{tab:full-comparison}
\end{table*}
```

---

## 2. Figure Style

Clean, minimal, with a consistent color palette. Two approaches depending on figure type.

### 2.1 Color Palette

> **The source of truth is `thesis-style.sty`, not this table.** Never hardcode
> hex colors in a chapter `.tex`. Use the named macros below (and their Python
> mirrors in `plots/thesis_style.py`). The hexes here are only for reference.
>
> | Macro | Role | approx. RGB |
> |-------|------|-------------|
> | `ThesisPrimary` / `ThesisPrimaryDark` | main / active / input — lavender | `166,148,232` |
> | `ThesisSecondary` / `ThesisSecondaryDark` | second series / masked / predicted — lime | green |
> | `ThesisTertiary` | third series / contrast — peach | peach |
> | `ThesisNeutral` | borders, grid, secondary info — steel gray | gray |
> | `ThesisInk` | text, labels — dark plum | near-black |
> | `ThesisPaper` | text-box / panel background — pale lavender | very light |
>
> The green/coral table just below is the **older Biomed-Enriched paper palette**
> (Python/Altair plots in `plots/`). New thesis-native TikZ schemas use the
> `Thesis*` macros above. Don't mix the two in one figure.

Legacy palette (Biomed-Enriched bar charts, lines, highlights):

| Role | Color | Hex | Usage |
|------|-------|-----|-------|
| Primary | Soft green | `#a3d575` | Main bars, our results |
| Primary border | Dark green | `#376410` | Bar outlines, emphasis |
| Secondary | Light blue-lavender | `#dce2fa` | Table headers, backgrounds |
| Accent 1 | Coral/salmon | `#e8836b` | Baselines, contrast |
| Accent 2 | Steel blue | `#6b8ec4` | Alternative series |
| Neutral | Gray | `#b0b0b0` | Grid lines, secondary info |
| Text | Near-black | `#333333` | Labels, axis text |

### 2.2 Bar Charts (Python/Vega-Altair style)

For result comparisons, accuracy plots, ablations. Generate with Python, export as PDF.

Key properties:
- **Rounded corners** on bars (`cornerRadius=4`)
- **Thin dark border** on bars (`stroke="#376410"`, `strokeWidth=1`)
- **No grid lines** — clean white background
- **Value labels** directly on top of bars (bold, `fontSize=13`)
- **Error bars** with tick caps when reporting std
- **Angled x-axis labels** (`labelAngle=-45`) if names are long
- Axis titles only when not obvious from context

```python
# Reference: Vega-Altair bar chart template
alt.Chart(df).mark_bar(
    cornerRadiusTopLeft=4, cornerRadiusTopRight=4,
    cornerRadiusBottomLeft=4, cornerRadiusBottomRight=4,
    stroke="#376410", strokeWidth=1
).encode(
    x=alt.X("model:N", axis=alt.Axis(labelAngle=-45, title=None, grid=False)),
    y=alt.Y("score:Q", axis=alt.Axis(title="F1 Score", grid=False)),
    color=alt.value("#a3d575")
)
```

### 2.3 Pipeline / Architecture Diagrams (TikZ or draw.io)

For method overviews, data pipelines, model architectures.

Rules:
- Use the same color palette as bar charts
- Rounded rectangles for processing steps
- Arrows with consistent style (straight, not curved unless necessary)
- Text inside boxes, not floating
- Keep it simple — no more than 8-10 boxes per figure
- Export as PDF for sharp rendering in LaTeX

### 2.4 Line Plots (Matplotlib)

For training curves, scaling analysis, position-level comparisons.

Rules:
- Use 2-3 colors max per plot (from palette above)
- Solid lines for our models, dashed for baselines
- Legend inside the plot area or directly labeling lines
- Grid: light gray dotted lines only on y-axis if needed
- Font size: axis labels 12pt, tick labels 10pt, legend 10pt

### 2.5 General Figure Rules

- **Format**: Always PDF (vector) for LaTeX. Never PNG/JPG for plots.
- **Caption**: Below figure, descriptive (1-2 sentences). Bolded first phrase as title.
- **Size**: Single-column `\begin{figure}[t]` for small plots, `\begin{figure*}[t]` for wide ones
- **Reference**: Always `\Cref{fig:...}` before the figure appears in text
- **Subfigures**: Use `\subcaption` package for (a), (b), (c) panels
- **Consistency**: Same font family in figures as in thesis body (use LaTeX rendering in matplotlib: `plt.rcParams['text.usetex'] = True`)

### 2.6 Template: Figure Inclusion

```latex
\begin{figure}[t]
    \centering
    \includegraphics[width=\columnwidth]{sources/part_1/chapter1/imgs/results_bar.pdf}
    \caption{\textbf{Performance comparison across biomedical NER tasks.}
    CamemBERT-bio outperforms all baselines on clinical and scientific benchmarks.}
    \label{fig:results-bar}
\end{figure}
```

---

## 2bis. Pedagogical TikZ schemas (thesis aesthetic + Tufte)

The "What is Biomedical Text?" part and the Language Models RW chapter use a
family of **hand-drawn TikZ schemas** (not data plots) to explain a concept:
the chain rule, attention masks, the CLM-vs-MLM objectives. These are the most
fiddly figures in the thesis. Rules that emerged from building them (and from
Rian's corrections "trop simpliste", "respecte Tufte", "les tokens se touchent",
"le schéma CLM n'est pas clair").

### What "respect Tufte" means here

- **Maximize data-ink, kill chartjunk.** No drop shadows, no 3D, no gratuitous
  fills. A box has a 1pt rounded border and at most a light tint; color is used
  *to carry meaning*, never decoration.
- **Color = meaning, consistently.** Lavender (`ThesisPrimary`) = the input /
  active / attended cell; lime (`ThesisSecondary`) = the special role (masked
  token, predicted target); empty/white = inactive. Reuse the SAME mapping across
  every schema in the part so the reader learns it once.
- **Small multiples for contrast.** Show two regimes side by side built from the
  *same* primitive so only the meaningful difference stands out: encoder (full
  attention) vs decoder (lower-triangular causal mask); causal (dense targets) vs
  masked (sparse targets). Same grid, same cell style, one variable changes.
- **Precise, not cute.** This is a manuscript. A toy 3-box doodle reads as
  simpliste; draw the real structure (a real mask matrix, real next-token
  arrows). Detailed but clean beats minimal-but-vague.

### Layout rules that fixed real problems

- **Spell out labels, on the LEFT, anchored east.** Two-line block labels
  (`Causal language\\modeling`) to the left of the rows, plus small row tags
  `target` / `input`. Don't abbreviate to "CLM"/"MLM" inside the figure itself.
- **Give cells room — tokens must not touch.** Set an explicit horizontal step
  and a generous min width, e.g. `\def\sx{1.6}` with
  `minimum width=1.25cm`. If boxes touch, widen `\sx` before anything else.
- **Wrap wide schemas in `\resizebox{\textwidth}{!}{...}`.** Lets you design at a
  comfortable absolute scale and have it shrink to the text block cleanly.
- **Generate repetitive cells with `\foreach`**, and compute per-cell state with
  `\pgfmathtruncatemacro`. The causal mask is one nested foreach with a
  truncated boolean:

  ```latex
  \foreach \i in {0,...,5} \foreach \j in {0,...,5} {
    \pgfmathtruncatemacro{\on}{(\causal==0) || (\j<=\i)} % full vs lower-triangular
    \node[cell, \ifnum\on=1 on\else off\fi] at (\j*\sx,-\i*\sx) {};
  }
  ```

- **Arrows: default `->` tip, thin, faded.** A target-above-input schema uses
  short vertical `up/.style={->, ThesisInk!45, shorten >=1.5pt, shorten <=1.5pt}`.
- **Two-row input/target layout** for objective figures: bottom row = the actual
  input tokens (solid tint), top row = the targets (faint tint), arrow between.
  Dense (CLM: a target over every position) vs sparse (MLM: a target only over
  `[MASK]` positions) is then visually obvious.

### Reusable styles (define once per figure, in thesis colors)

```latex
\begin{tikzpicture}[font=\scriptsize\sffamily,
  cell/.style={draw=ThesisInk!22, rounded corners=1.5pt,
               minimum width=1.25cm, minimum height=0.55cm,
               text=ThesisInk, inner sep=2pt},
  on/.style ={fill=ThesisPrimary!30,   draw=ThesisPrimaryDark},   % active/input
  msk/.style={fill=ThesisSecondary!38, draw=ThesisSecondaryDark}, % masked
  tgt/.style={cell, fill=ThesisPrimary!16,   draw=ThesisPrimaryDark!60}, % target (CLM)
  tgtm/.style={cell, fill=ThesisSecondary!22, draw=ThesisSecondaryDark!70}, % target (MLM)
  up/.style ={->, ThesisInk!45, shorten >=1.5pt, shorten <=1.5pt}]
```

### The in-text "example box" (used for every figure that shows a real text)

Each chapter of the biomedical-text part opens on a real/synthetic text sample
rendered as a single rounded panel, NOT a screenshot:

```latex
\node[draw=ThesisNeutral, fill=ThesisPaper, rounded corners=3pt, line width=0.5pt,
      text width=0.84\textwidth, inner sep=12pt, align=justify,
      font=\footnotesize, text=ThesisInk] { \textit{ ... the text ... } };
```

Force it to the top of the chapter with a non-float block (see §2bis below /
`working-with-rian.md`): `\begin{center} ... \captionof{figure}{...} ... \end{center}`,
not `figure[t]`, so it stays exactly where intended.

### Verify every schema by rendering, not by reading the source

After editing a TikZ schema, **compile and look at the actual pixels** before
committing: find the page (`pdftotext -layout` + grep the caption), render it
(`pdftoppm -png -r 130 -f N -l N thesis.pdf out`), and Read the PNG. Check for
overflow, touching cells, unreadable labels, broken arrows. The summary's
"looks-right-in-source" is not enough; Rian's corrections were all things only
visible in the rendered figure.

### Concept figures already in the thesis (reuse their code as templates)
In `sources/related_works/language_modeling.tex` and the biomedical-text chapters:
`fig:lm-entropy` (Shannon bars), `fig:lm-nexttoken`, `fig:lm-word2vec` (the
king−man+woman≈queen parallelogram), `fig:lm-rnn` (unrolled RNN), `fig:lm-attention`
(encoder/decoder mask matrices), `fig:lm-objectives` (CLM/MLM dense-vs-sparse),
`fig:lm-fewshot` (3-panel zero/one/few-shot prompt box), `fig:lm-dapt` (DAPT/TAPT
pipeline); plus three Python plots in `plots/related_works/` (`rnn_gradient.py` =
analytical η^(t−k) bound, `chinchilla_scaling.py`, `llama_vs_gpt3.py`). The bilingual
example boxes are in `clinical/scientific/web.tex` (see `working-with-rian.md` §9).

### Small lessons that cost a redo this session
- **Load the TikZ library you use.** `calc` (for `($(a)!0.5!(b)$)`, `($(a)+(..)$)`) and
  `decorations.pathreplacing` (braces) are in `thesis.tex`'s `\usetikzlibrary{...}`; add new
  ones there, not per-figure.
- **Drop decorative axes** when they carry no data (they read as chartjunk and caused a label
  to overflow onto the axis). Label points directly instead.
- **Put a label ON its line**, not floating beside it: `\draw[...] (a)--(b) node[midway,
  sloped, above]{label};` rather than a separate `\node` near the midpoint.
- **Color carries meaning, text stays quiet.** Saturated colour only on the data
  (lines/points/bars); regime/word labels in `ThesisNeutral`/`ThesisInk`, no legend box when
  direct labels or a frameless outside legend will do.

---

## 3. Quick Reference — Do / Don't

| Do | Don't |
|----|-------|
| `booktabs` rules only (no vertical lines) | `\hline` or `|` column separators |
| `\rowcolor{TableSeparator}` for groups | Alternating row colors everywhere |
| PDF vector figures | PNG screenshots of plots |
| Consistent color palette across all figures | Random colors per figure |
| Value labels on bars | Rely on reader to estimate from axis |
| `\small` in tables | `\tiny` or `\scriptsize` |
| Bold best, underline second-best | Highlight with background colors |
| Descriptive caption with bold title phrase | One-word captions like "Results" |
