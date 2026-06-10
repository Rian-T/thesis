# Working with Rian — process, voice, and the mistakes not to repeat

Hard-won notes from drafting sessions. Read this *with* `writing-guide.md` and
`visual-style.md` before writing or editing thesis prose. These are corrections
Rian has actually made; do not make him repeat them.

---

## 1. Process — the "scribe" model

- **Voice-first.** Rian often steers by voice and does **not** have the `.tex`
  open. Assume he cannot see the file. You are his eyes: tell him what is there,
  summarise what a paragraph does in French, show him rendered PDFs.
- **Show PDFs, not the source.** After a change, compile and send **only the
  relevant pages** (`pdfjam thesis.pdf 14-17 -o /tmp/x.pdf`), never the whole
  thesis and never raw LaTeX.
- **Draft in buffers first.** Scratch files live in `sources/drafts/` and
  `research/` (both git-ignored). Each buffer is a standalone, compilable `.tex`
  with its own PDF, so we never touch the real manuscript until a passage is
  validated. Only then merge into `sources/...`.
- **Paragraph by paragraph.** Write one paragraph per edit, in order. Do **not**
  write all paragraphs in a single edit. Self-review (a quiet "bilan") between
  paragraphs; you may re-question yourself. But do **not** ping Rian after every
  paragraph; check in after a coherent arc.
- **Commit after each validated step** (telegraphic, sole author Rian, no
  `Co-Authored-By` — see `../CLAUDE.md`), so anything is revertible.
- **Keep buffers and research OUT of git.** `research/` holds PII screenshots and
  downloaded copyrighted PDFs; `sources/drafts/` is scratch. Both are
  git-ignored. Never commit them.

## 2. Deep-research approach (this worked — reuse it)

- For conceptual / related-work material, dispatch **parallel Opus subagents**,
  one per theme. Each agent must **`curl` the primary sources** (open-access
  PDFs, ACL Anthology, PMC, SEP for philosophers) and **read them in depth**, not
  produce a one-line Wikipedia gloss.
- Each agent writes a markdown in `research/` giving, per author/idea: the claim
  in plain language, the concept defined, a real quote or example, its
  **argumentative job in our narrative**, formalizable-vs-conceptual, and the
  **exact citation** (with honesty flags: primary vs secondary, `[à vérifier]`,
  book → likely `checkbib`-unverifiable → whitelist). **Never invent** a DOI,
  page range, or number.
- Add a **bonus exploratory agent** for an angle that might flop or surprise
  (e.g. the French-specific empirical reality). The surprises are often the gold
  (here: the CAS-vs-PARHAF register dispute; "no shareable real French EHR
  corpus").

## 3. Voice & word choice — what Rian keeps correcting

- **Simple academic English.** If a sentence is complex for no reason, simplify.
  Better plainer and slightly less deep than precise and opaque. After a draft,
  do a pass asking only: *how do I say this more simply?*
- **No choppy, ultra-short sentences.** They read as AI/slop. Merge them into
  flowing prose. Keep at most a rare, deliberate punch.
  - BAD: "Much of it acts." / "These threads pull together." / "This is more than
    a theory."
  - GOOD: "The clinical note is the best-documented case of this idea." /
    "The note does more than describe the patient; much of it acts."
- **Human, not robotic.** Match the voice of the existing chapters (read the
  CamemBERT-bio chapter, `sources/part_2/chapter4/`). Measured, a little
  personality, never marketing slop.
- **Intuition first, then detail.** Do not go technical/precise too fast. Open a
  point with the idea a non-specialist can grasp; add the machinery after.
- **Respect altitude / where we are in the manuscript.** Do not talk about
  *models / modeling* in a chapter that is about the *text*. Do not introduce a
  comparison "from nowhere": at the very start of the manuscript, stay on the
  objective (clinical text and its problem). Defer the comparison to **one
  transition sentence at the very end** that opens the next chapter.
- **Every precise/quantitative claim needs real data.** Never write "we can
  measure X" then stop. Give the literature's actual numbers, a real table, or a
  real plot from the source — never a fake two-point plot. If you have no data,
  cut the claim (we dropped a "closure is measurable" paragraph for this reason).
- **Use concrete examples / real content.** Empty, hand-wavy sentences are a
  smell. Ground claims in a real quote, a real figure, real numbers.

## 4. Figures & captions

- **Captions: one simple sentence.** Simplicity is strongest.
  - GOOD: "A discharge summary for an acute myocardial infarction."
- **Parallel captions across related figures** for effect (same case shown as
  clinical note / scientific article / lay text → near-identical captions).
- **Force key figures to their intended spot.** If a float drifts, use a
  non-float block (`\begin{center} … \captionof{figure}{…} … \end{center}`) so
  the figure is exactly where intended (e.g. the first thing in the chapter).
- Follow `visual-style.md` and the `thesis-style.sty` colours
  (`ThesisInk`, `ThesisPaper`, `ThesisNeutral`, …); build diagrams in TikZ.

### TikZ concept schemas — the corrections Rian actually made

(Full playbook in `visual-style.md §2bis`. These are the live corrections so you
don't repeat them.)

- **"trop simpliste, c'est un manuscrit, sois précis."** A 3-box doodle is not
  acceptable. Draw the real structure: a real attention mask matrix, real
  next-token arrows. Detailed-but-clean, never minimal-but-vague. "Respecte
  Tufte": high data-ink, no chartjunk, small multiples for the contrast.
- **"les tokens se touchent."** Cells were too tight. Widen the horizontal step
  (`\def\sx{1.6}`) and min width (`1.25cm`) until boxes clearly separate.
- **"le schéma CLM n'est pas clair."** Use a two-row input/target layout: bottom
  = input tokens, top = targets, short up-arrows between. CLM = a target over
  every position (dense); MLM = a target only over `[MASK]` (sparse).
- **Spell out the labels in full inside the figure** ("Causal language modeling",
  not "CLM"), placed to the **left** of the rows.
- **Label placement is finicky and Rian notices it.** The big two-line block
  label ("Causal language modeling") must sit **further left**, NOT vertically
  aligned under the small `target`/`input` row tags. Put the block label at a more
  negative x (anchor east), and the row tags closer to the cells. Verify by
  rendering.
- **Color carries meaning, reused across the part:** lavender = input/active,
  lime = masked/predicted. Don't recolor per figure.
- **Always render the page and look at it before committing a figure.** Every one
  of the above was invisible in the LaTeX source and only obvious in the PDF.

## 5. Punctuation & rhythm

- Prefer a **colon** to join when it flows better than a full stop; avoid ending
  a paragraph on a too-short sentence.
- **No mid-sentence em dashes** (also in `writing-guide.md`). Use commas, colons,
  periods, or parentheses.

## 6. Privacy / ethics (non-negotiable)

- **Never put real clinical data or PII in the manuscript.** Real notes (e.g. the
  screenshots in `research/assets/`) are **style templates only**.
- Use **synthetic, de-identified** examples with **realistic fictional names**
  (hospital, clinicians, patient), not `[ANONYMISÉ]` blanks.
- Remember *why* clinical text is private: it is **saturated with personal data**;
  pseudonymisation ≠ anonymisation; models can memorise and resurface it. This is
  itself a thesis argument.

## 7. Bibliography discipline

- Add real entries to `thesis.bib`; run `make checkbib` after citing.
- Books and workshop/French venues often won't verify → add to
  `tools/bibcheck_whitelist.txt` with a justification. Never invent DOIs/pages.
- **Get exact bib by curl, never WebFetch.** Prefer the PUBLISHED venue over arXiv.
  Recipe that works: Crossref by DOI (`api.crossref.org/works/<DOI>`), ACL Anthology
  `.bib` (`aclanthology.org/<id>.bib`), DBLP bibtex (`dblp.org/rec/<key>.bib`),
  OpenAlex for author *order* when Crossref alphabetises it. Verify the title/authors
  resolve to the real paper. (This session caught a wrong author list in
  `kirkpatrick2017ewc` and the BioMistral entry filed under the wrong venue.)
- **Derived numbers are OK but must be flagged as derived, not quoted** (e.g. Chinchilla
  "~20 tokens per parameter" and UMLS "~3 names per concept" are reader-derived ratios,
  not sentences in the papers).

## 8. Subagent writing passes (fable) — the rewrite workflow Rian likes

For making prose plainer / more human, dispatch `fable`-model subagents (Agent tool,
`model: fable`). This worked well across the whole "What is Biomedical Text?" triptych
and LM chapter 5.1–5.7.

- **Always calibrate on CamemBERT-bio.** Point each agent at
  `publications/CamemBERT_bio___LREC_COLING_2024/camembert-bio-lrec-coling2024.tex` and make
  it **quote two sentences from it as proof it read it**. Closely copying that voice is what
  kills the AI-slop and the "not X but Y" seesaws.
- **The dial, boldest → lightest:** full rewrite → clarify-and-enrich (add a clause where a
  cited name like Foucault would otherwise feel "randomly dropped", without digressing) →
  pure simplification (simpler words, shorter sentences, no new content) → style pass (kill
  antithesis). State which one you want, explicitly, each time. Rian iterates several rounds.
- **Always re-read the diff before committing.** Subagents reintroduce things you removed
  (an unverified claim, a "not X but Y", an "itself", a dangling comparative). Catch them.
- **Preserve, every time:** `\citep/\citet/\emph/\Cref`, verbatim quotes, all math/figures/
  tables, `% === Pn ===` markers. Tell the agent so.

### Concurrent same-file edits CORRUPT — use the /tmp-copy trick
If several subagents must edit ONE file (e.g. `language_modeling.tex` section by section),
do **not** let them all Edit the repo file at once. Tell each to `cp` the file to a unique
`/tmp/lm_secNN.tex`, edit ONLY its section there, and report. Then merge in the main loop,
section by section, by `\section{...}` markers (a small Python splice: take block
`[start_marker, next_marker)` from each `/tmp` copy into the repo file). This is how 5.4/5.5/5.6
were done safely in parallel.

## 9. Bilingual example figures (the triptych convention)
Each "What is Biomedical Text?" chapter opens on a side-by-side box: **French original on the
left in `ThesisInk`, English translation on the right in muted `ThesisNeutral`**, a thin
vertical rule between, tiny labels `FRANÇAIS` / `ENGLISH · TRANSLATION`. French is the source;
English muted = "this is a translation". Built as a 2-column `tabular` with a `!{\vrule}`
separator, each column a `\begin{minipage}[t]{0.40\textwidth}`. Caption is one sentence ending
"…; French original, English translation."
