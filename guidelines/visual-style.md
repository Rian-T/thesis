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

Primary palette (for bar charts, lines, highlights):

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
