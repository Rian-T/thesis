# Writing Guide — Rian's Thesis

Reference document for both Rian and Claude when writing thesis content.
Based on: CamemBERT-bio paper (primary style reference), ALMAnaCH thesis examples (Godey, Duquenne, Nguyen, all Sorbonne 2024).

---

## 1. Voice & Style

The voice of this thesis is derived from the CamemBERT-bio paper (LREC-COLING 2024). All examples below come from that paper unless noted otherwise.

### 1.1 Tone

**Factual and measured.** Never hype results. State what was done, what was observed, and what it means. Let the numbers speak.

| Do | Don't |
|----|-------|
| "We observe a significant performance gain on all evaluation datasets" | "We achieve groundbreaking results that far surpass all previous work" |
| "CamemBERT-bio achieves an improvement of 2.54 points of F1-score on average" | "CamemBERT-bio dramatically outperforms all baselines" |
| "This is a promising research direction" | "This revolutionary approach will transform the field" |
| "However, these models are trained for plain language and are less efficient on biomedical data" | "Unfortunately, these models completely fail on biomedical data" |

### 1.2 Pronoun & Person

- Always use **academic "we"**, even for solo-authored sections: "We introduce...", "We observe...", "We propose..."
- Never use "I" in body text
- Refer to other works in third person: "They observed...", "\citet{X} introduced..."

### 1.3 Sentence Structure

**Medium-length sentences (15-25 words), clear subject-verb-object.** Avoid both telegraphic bullet-style and overly complex nested clauses.

Good examples from CamemBERT-bio:
- "These documents represent an opportunity for massive clinical studies using real data."
- "We find a 45% intersection between the two vocabularies, which is quite close to the 42% intersection found by \citet{beltagy_scibert_2019}."
- "Their approach is the only one in this table capable of handling nested entities, giving them an advantage."

Avoid:
- Sentences over 40 words with multiple subordinate clauses
- Sentence fragments (except in telegraphic enumerations for technical details)
- Starting sentences with "It is" when a concrete subject exists

### 1.4 Tense

| Context | Tense | Example |
|---------|-------|---------|
| Own contributions, claims, general truths | Present | "We introduce CamemBERT-bio", "Transfer learning allows..." |
| Describing what was done in experiments | Past | "We performed 50,000 steps over 39 hours" |
| Other authors' published findings | Present or past | "BioBERT demonstrates improved performance" or "\citet{X} observed..." |
| Future/planned work | Present or conditional | "We can further clean the data...", "This could involve..." |

### 1.5 Precision & Numbers

**Always back claims with precise numbers.** Never use vague quantifiers when data exists.

| Do | Don't |
|----|-------|
| "413 million words, equivalent to 2.7 GB" | "a large biomedical corpus" |
| "an improvement of 2.54 points of F1-score on average" | "a significant improvement" |
| "32 times more CO2" | "much more carbon emissions" |
| "39 hours using two Tesla V100 GPUs" | "relatively short training time" |

When comparing, give both the absolute value and the delta:
- "AliBERT emits 10 times the amount of CamemBERT-bio, while DrBERT releases 32 times more"

### 1.6 Hedging & Honesty

Be honest about limitations. Never hide weaknesses.

Good hedging patterns from CamemBERT-bio:
- "However, the performance gains are relatively modest"
- "There may be duplicates of some leaflets"
- "There is an indeterminate amount of English in this corpus"
- "These aspects could impact the outputs of our model and should be investigated"
- "This might mean our understanding of how well our model performs is restricted"

When results are negative or mixed, state them plainly:
- "We observe a decrease in performance with the biomed-fr-small dataset"
- "CamemBERT-bio exhibits better performance across all other metrics [but] DrBERT demonstrates a more balanced performance across different classes"

### 1.7 Transitions & Flow

**Between paragraphs:** Use logical connectors but don't overload. Favor: "However", "Furthermore", "Additionally", "Notably", "It is worth noting that". Avoid: "Moreover" in every paragraph, "On the other hand" when there's no actual contrast.

**Between sections:** The last paragraph of a section should naturally lead to the next topic. The first paragraph of a new section should establish its scope immediately.

Example from CamemBERT-bio intro: each paragraph ends by raising a problem that the next paragraph or section addresses.
1. CDWs exist but data is unstructured -> need NLP
2. BERT models work but fail on biomedical -> need domain adaptation
3. Confidentiality blocks hospital models -> need public model
4. Therefore we introduce CamemBERT-bio (contributions)

### 1.8 Paragraph Length

- **Target: 4-8 sentences per paragraph** (roughly 80-150 words)
- Single-sentence paragraphs are acceptable only for strong transitional statements
- Never write wall-of-text paragraphs (>200 words) without a break

### 1.9 Word Choice

Prefer:
- "observe" over "see" or "notice"
- "demonstrate" or "show" over "prove" (unless mathematically proven)
- "improvement" or "gain" over "boost" or "leap"
- "limitation" over "drawback" or "flaw"
- "investigate" or "explore" over "look at"
- "significant" only when statistically justified; use "notable" or "substantial" otherwise

Avoid:
- Superlatives without evidence: "best", "first-ever", "unique"
- Marketing language: "powerful", "robust" (unless defined), "cutting-edge", "novel" (use "new")
- Colloquialisms: "a lot of", "kind of", "basically"
- Em dashes (—) mid-sentence. Use commas, colons, periods, or parentheses instead. Exception: rare stylistic use in a clearly literary passage (epigraph, transition paragraph), never in technical prose.

### 1.10 Human Touch — Measured Irreverence

The thesis should not read like it was generated by a machine. Small touches of personality are welcome: a wry observation, a well-placed understatement, a sentence that shows the author has opinions and a sense of humor. The goal is a manuscript that is rigorous *and* pleasant to read, not a dry checklist of results.

**Where it works:**
- Chapter introductions and conclusions, where the author's voice naturally comes through
- Discussing limitations or surprising results ("One might expect X, the data disagrees.")
- Framing a problem in an unexpected but illuminating way
- Transition paragraphs between chapters, which are more personal by nature

**Where to hold back:**
- Method descriptions and experimental setups (precision matters more than flair)
- Related work sections (let other authors' work speak for itself)
- Formal claims and numerical comparisons

**The rule:** if a reviewer could circle the sentence and write "informal" in the margin, it's too much. If it makes the reader briefly smile while learning something, it's just right.

| Do | Don't |
|----|-------|
| "The model, perhaps unsurprisingly, struggles with abbreviations it has never seen." | "The model totally chokes on unseen abbreviations." |
| "We leave this ambitious goal to braver researchers or to future work." | "This is left as future work lol." |
| "The performance gap, while real, is modest enough to keep one's enthusiasm in check." | "The results are kinda meh." |
| "This is, to put it mildly, a non-trivial constraint." | "This is super hard." |

---

## 2. Thesis Structure

Based on patterns from Godey, Duquenne, and Nguyen theses, adapted to Rian's thesis plan.

### 2.1 Overall Architecture

Rian's thesis follows the Godey model (most detailed, same team):

```
Title page (French)
Abstract (English) + Résumé (French)
Acknowledgements
Table of Contents

Introduction (Chapter)

Part I: Related Works
  Chapter: Language Modeling
  Chapter: Corpus Annotation & Quality
  Chapter: Clinical Information Extraction

Part II: Building a Biomedical Corpus
  Ch 1: Collecting Biomedical Text          — CamemBERT-bio corpus    (1st author)
  Ch 2: Filtering by Quality Signals        — GAPeron / BiaHS         (3rd author)
  Ch 3: Detecting Content Types             — Biomed-Enriched         (1st author)

Part III: Pretraining Language Models
  Ch 4: Encoder Models for French Biomedicine — CamemBERT-bio pretraining (1st author)
  Ch 5: When Decoder Continue-Pretraining Stops Working — discussion chapter
  Ch 6: Beyond Masked Language Modeling       — ModernCamemBERT-bio    (1st author)

Part IV: Adapting to Clinical Tasks
  Ch 7: Limits of Direct Fine-Tuning         — discussion chapter
  Ch 8: Architectures for Low-Resource Extraction — frenchmed-gliner   (1st author)
  Ch 9: Synthetic Data for Task Adaptation    — OntoBook               (1st author)

Conclusion & Perspectives
Appendices
Bibliography
```

**Chapter types:**
- **Article chapters** (1st author): based directly on a published paper. Preserve the paper's original text. Add only thesis framing (hook, transitions, cross-references to other chapters).
- **Article chapters** (not 1st author): open with "This chapter is based on [citation]. Our personal contribution includes..." and focus on your contribution.
- **Discussion chapters** (Ch 5, 7): no underlying paper. These set up the problem that the following chapter(s) solve. More freedom in writing style.

**Splitting a paper across chapters:** CamemBERT-bio is split into Ch 1 (corpus) and Ch 4 (pretraining + evaluation). Each chapter is self-contained but cross-references the other with `\Cref{}`.

### 2.2 Introduction Structure

Follow the Godey pattern: **context -> limitations -> motivations -> research questions -> contributions -> outline**.

- **Context** (1-2 pages): Start broad (clinical data warehouses, healthcare digitization, privacy), narrow to NLP for clinical text, then to the specific challenge of adapting models without clinical data.
- **Research questions** (bullet list, 3-4 questions): Frame the thesis narrative. Each question maps to a part or group of chapters.
- **Contributions** (bulleted list): One bullet per chapter, 2-3 sentences each. State the contribution, not the method. Reference the publication.
- **Outline** (1 page): One paragraph per part, explaining the logical flow.

An epigraph is optional but all three example theses use one (Godey: film quote, Nguyen: none, Duquenne: none). Rian's thesis already has a Sutton quote placeholder.

### 2.3 Research Chapter Anatomy

Each research chapter follows the paper structure, wrapped in thesis framing:

```
\chapter{Chapter Title}

% Optional: publication reference under title
% "This chapter is based on: [full citation]"

\section{Introduction}        % 1-2 pages, thesis-contextualized
\section{Related Work}        % If not covered in Part I RW chapters
\section{Method / Approach}
\section{Experimental Setup}
\section{Results}
\section{Discussion}          % Optional, can merge with Results
\section*{Conclusion}         % Unnumbered, 0.5-1 page

\vspace{2em}
% Transition paragraph to next chapter (2-3 sentences)
```

**Preserving original text:** For chapters based on published papers, keep the paper's original sentences as much as possible. Only apply writing guide rules where strictly necessary: transitions, thesis framing, cross-references, or cases where the text genuinely violates a rule. Do not rewrite functional prose.

**Chapter introduction**: Not a copy of the paper intro. Restructure to avoid repeating what the thesis introduction already covers. The chapter intro should:
- Start with a **short hook** (2-3 sentences max): a concrete observation or paradox that frames the chapter's problem. Not a broad context paragraph.
- Flow naturally from the hook into the specific gap this chapter addresses.
- **Never repeat the hook's content** in a later paragraph. If the hook establishes a constraint (e.g., data confidentiality), don't re-state it in a dedicated paragraph.
- Watch pronoun clarity after hooks: avoid "These documents..." when the previous sentence ended with a different referent.

**Chapter conclusion**: Do NOT start with "We have introduced X" or "In this chapter, we presented Y". The reader just read the chapter, they know what was introduced. Instead, conclude on what was *learned*, what *question remains open*, or set up a *cliffhanger* for a later chapter. If a finding raises a natural question answered in a future chapter, pose it here and point to where the answer comes. Then transition to the immediate next chapter.

**Cliffhanger pattern** (when the next chapter in narrative order is not the one answering the open question):
```latex
\section*{Conclusion}
[Open question / cliffhanger pointing to a later chapter via \Cref{}]

\vspace{2em}
[Transition to the immediate next chapter]
```

**Transition paragraph** (after `\vspace{2em}`): Bridge to the next chapter. Pattern: "In this chapter, we showed X. However, Y remains open. In the next chapter, we explore [topic] to address [gap]."

### 2.4 Related Works Chapters

**Narrative, not catalogue.** Group works by theme/approach, not by year or author.

Rules:
- Each RW chapter covers a distinct topic (language modeling, corpus/quality, clinical IE)
- **No redundancy between RW chapters.** If a topic is covered in one, use `\Cref{}` to point from others.
- **Never spoil own contributions.** Describe the landscape and gaps, don't preview solutions.
- End each RW chapter by identifying the open problems that the thesis addresses (without saying "we solve this in Chapter X")
- Use chronological ordering within each thematic group

### 2.5 Conclusion & Perspectives

Follow Godey's split structure:

**Conclusion chapter:**
- Summary: One paragraph per chapter recapping the key finding
- Discussion: Broader implications, limitations across the thesis
- Revisit research questions from intro and answer each one

**Perspectives chapter:**
- Future work: Concrete next steps (1-2 paragraphs each)
- Broader perspectives: Where the field is heading, societal implications

---

## 3. Writing Each Section Type

### 3.1 Chapter Introduction (1-2 pages)

Template:
1. **Opening** (1 paragraph): Broad context for this chapter's topic, connecting to the thesis narrative
2. **Problem** (1 paragraph): What specific gap or challenge this chapter addresses
3. **Approach overview** (1 paragraph): Brief summary of the method/contribution
4. **Contributions list** (itemize): 2-4 bullets, one sentence each
5. **Chapter organization** (optional, 1 sentence): "This chapter is organized as follows..."

### 3.2 Related Works Section (within a research chapter)

- Only include if the topic is NOT already covered in Part I RW chapters
- If covered in Part I, write: "Background on [topic] is provided in \Cref{ch:rw-topic}. Here, we focus specifically on [narrow aspect]."
- Group by approach, not by author
- End with the gap that motivates this chapter's work

### 3.3 Experimental Setup

Structure with `\paragraph{}` headers:
- **Datasets**: Name, source, size, splits, preprocessing
- **Models**: Architecture, hyperparameters, training details
- **Evaluation**: Metrics, tools (seqeval, etc.), number of runs, statistical reporting (mean +/- std over N seeds)
- **Baselines**: What you compare against and why

### 3.4 Results Discussion

Use `\paragraph{}` headers for each comparison or finding:
- Start with the main result table reference
- Discuss each finding as a separate `\paragraph{}`
- Give the number first, then the interpretation
- When results are mixed, state both sides plainly

Pattern from CamemBERT-bio:
```
\paragraph{CamemBERT vs CamemBERT-bio} We observe a significant
performance gain on all evaluation datasets (see Table~\ref{tab:X}).
On average, we achieve a 2.54-point improvement in F-score.
```

### 3.5 Chapter Conclusion + Transition

Template:
```latex
\section*{Conclusion}

% 1. Key takeaway or open question (NOT "we introduced X")
% State what was learned, or pose a cliffhanger answered later.
[Key finding or surprising open question → \Cref{later chapter}]

\vspace{2em}

% 2. Transition to the immediate next chapter (2-3 sentences)
Before we get there, [more immediate question].
In the next chapter, we [topic of next chapter].
```

**Avoid:** "We have introduced...", "In this chapter, we presented...", "We showed that..." — these are paper-style summaries. In a thesis, the reader just finished the chapter. Conclude on insight, not inventory.

### 3.6 Thesis Introduction

See Section 2.2. Key: the intro should be readable as a standalone summary of the thesis. A reader who only reads the intro and conclusion should understand the full contribution.

### 3.7 Thesis Conclusion

- One paragraph per chapter: "In Chapter X, we showed..."
- Then: answer each research question from the intro
- Then: limitations at the thesis level
- Then: perspectives (can be a separate chapter following Godey)

---

## 4. LaTeX & Formatting

### 4.1 Cross-references

- Always use `\Cref{}` (capitalized, from cleveref): `\Cref{ch:camembert-bio}`, `\Cref{tab:results}`, `\Cref{fig:pipeline}`
- For ranges: `\Cref{ch:1,ch:2,ch:3}` or "Chapters~\ref{ch:1}--\ref{ch:3}"
- Never hardcode "Chapter 3" or "Table 2". Always use refs.

### 4.2 Figures & Tables

- Place figures/tables in `sources/part_X/chapterY/imgs/`
- Use `\begin{table}[t]` or `\begin{figure}[t]` for top placement
- Every table/figure must be referenced in the text before it appears
- Captions: descriptive but concise (1-2 sentences)
- Bold best results, underline second-best in comparison tables

### 4.3 Citations

- Style: `acl_natbib`
- In-text: `\citet{author_year}` for "Author (Year)" and `\citep{author_year}` for "(Author, Year)"
- When listing multiple works: `\citep{a,b,c}` in chronological order
- For language resources (datasets, models): `\citetlanguageresource{}` if the venue requires it

### 4.4 Chapter File Organization

```
sources/part_X/chapterY/
  article.tex          % Main chapter content
  imgs/                % Figures for this chapter
```

Orchestration files (`analysis_lm.tex`, `extensions_lm.tex`) include chapters with `\include{}`.

### 4.5 Formatting Conventions

- `\paragraph{Title}` for structured subsections within results/discussion
- `\section*{Conclusion}` (unnumbered) for chapter conclusions
- `\vspace{2em}` before transition paragraphs
- `\textit{}` for corpus/model names on first mention: *biomed-fr*, *CamemBERT-bio*
- Standard math notation: $F_1$, not F1 in running text (but F1 is acceptable in tables)

---

## 5. Pitfalls & Rules

### Hard rules (never break these)

1. **Never spoil own contributions in Related Works chapters.** Describe the landscape and gaps. Don't say "we solve this in Chapter X" or "as we will show". The RW should read as if written by someone who hasn't done the work yet.

2. **No redundancy between RW chapters.** If pretrained biomedical models are covered in `language_modeling.tex`, don't re-cover them in `clinical_ie.tex`. Use `\Cref{}` to point.

3. **No redundancy between research chapter intros and RW chapters.** If the RW already covers the background, the research chapter intro should reference it, not repeat it.

4. **No redundancy within a chapter.** If a hook or intro paragraph establishes a point, don't re-state it in a later paragraph. If two tables show overlapping information, merge or deduplicate.

5. **Always report numbers with context.** "+2.54 F1 on average across 5 benchmarks" not just "+2.54 F1".

6. **English body, French abstract/résumé only.** Follow Sorbonne convention.

7. **Never use "novel" or "state-of-the-art" as adjectives without evidence.** Say "new" instead of "novel". Say "achieves the best results on X" instead of "state-of-the-art".

8. **Preserve original paper text in article chapters.** Do not rewrite sentences from the published paper. Add thesis framing (hooks, transitions, `\Cref{}` cross-references) but leave the core prose intact.

### Soft rules (follow unless there's a good reason not to)

7. Keep paragraphs under 150 words.
8. One idea per paragraph.
9. Tables/figures should be interpretable without reading the text (descriptive captions).
10. Limit abbreviations: define on first use, don't abbreviate terms used fewer than 5 times.
11. Prefer active voice ("We trained the model") over passive ("The model was trained").
12. When citing a number of works in sequence, order chronologically.
13. Don't start consecutive paragraphs with the same word.

---

## 6. Lessons Learned (accumulated during writing)

### Hooks

- **A hook is not an abstract.** Don't summarize the chapter's results in the hook. Build tension, pose a question, or present a paradox. The results come later.
- **A hook is not meta-commentary.** Never start with "The previous part of this thesis was concerned with..." or "In this chapter, we present...". Start with a concrete observation about the world.
- **Follow the narrative thread.** If a previous chapter left a cliffhanger, the hook should pick it up. Don't re-introduce context the reader already has.
- **Hook and figure should complement, not repeat.** If a TikZ figure shows the contrast visually, the text should explain *why* it matters, not describe what the figure already shows.
- **Specificity builds tension.** "DrBERT reported losses of up to 20 F₁ points" is more compelling than "previous work reported that continual pretraining was ineffective." Use names, numbers, and stakes.

### Introductions

- **Don't spoil results in the intro.** The intro states what the chapter does and why, not the punchline. "We show that..." is OK. "We achieve 73.94 F₁ which is..." is too much.
- **Don't repeat the thesis introduction.** If the thesis intro already explains CDWs and privacy constraints, the chapter intro should not re-explain them. Reference with `\Cref{}` or just skip.
- **Bullet-point contributions belong in the thesis intro, not chapter intros.** In a chapter, weave the contributions into a flowing paragraph.

### Tables

- **No redundant columns.** If colored row headers (`\rowcolor{ThesisTableSep}`) already indicate the group (Clinical, Leaflets, Scientific), don't also have a "Style" column repeating the same info. Choose one.
- **No redundant tables.** If two tables show overlapping data (e.g., corpus overview + corpus breakdown), deduplicate.
- **Split wide tables.** A 12+ column table will overflow or be unreadable when scaled. Split into 2-4 narrower tables with sub-averages.
- **Side-by-side for small tables.** Two hyperparameter tables → use `minipage` + `\subcaption`.
- **Use `threeparttable` for footnotes.** Don't use inline `$^\dagger$`; use `\tnote{}` with `\begin{tablenotes}`.
- **`\rowcolor` needs `\PassOptionsToPackage{table}{xcolor}` before `\documentclass`.** Without this, colors silently don't render.

### Figures

- **Don't use TikZ for heatmaps.** Manual coordinate positioning doesn't scale. Use Python/matplotlib for data-driven figures, TikZ for diagrams (pipelines, architecture).
- **Python plots: set `figsize` to match thesis width.** A 15-inch figure scaled to 6-inch column = tiny fonts. Either reduce the source width or increase font sizes proportionally.
- **For multi-panel plots:** only show xlabel on the middle/bottom panel, ylabel on the leftmost. Don't repeat axis labels on every panel.
- **`\includegraphics[width=0.55\columnwidth]` for single-panel plots.** `\columnwidth` is too wide for a single small plot; it becomes half a page.
- **Centralize plot style.** All Python scripts import from `plots/thesis_style.py`. Never hardcode colors.
- **Copy figures into the codebase.** Don't reference `publications/` paths in chapter .tex files. Copy to `sources/part_X/chapterY/imgs/` or generate into `plots/chapterY/`.

### Conclusions

- **Never start with "We have introduced X."** The reader just read the chapter. Conclude on what was *learned* or what *question remains open*.
- **Use cliffhangers.** If a finding raises a question answered in a later chapter, pose it explicitly. "The answer, perhaps surprisingly, is no, as we show in \Cref{chap:X}."
- **Separate cliffhanger from transition.** The cliffhanger points to a future chapter; the transition (after `\vspace{2em}`) introduces the *next* chapter, which may be different.

### Word choice

- **Avoid "wholesale".** Use "indiscriminately" or "without filtering."
- **Avoid "novel".** Use "new."
- **No mid-sentence em dashes.** Use commas, colons, periods, or parentheses.
