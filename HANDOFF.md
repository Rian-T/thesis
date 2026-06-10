# HANDOFF — where the work stands (resume here)

Last updated end of a long writing session. Read this, then `guidelines/working-with-rian.md`
and `guidelines/writing-guide.md` (§7 especially), then `CLAUDE.md`.

## Git state
- **~27 commits ahead of `origin/main`, NOT pushed.** Rian pushes on his own signal — do
  not push unless he asks. Working tree is clean and compiles (`latexmk`, 0 fatal,
  0 undefined citations) as of the last commit.
- Build: `latexmk` (LuaLaTeX, aux in `build/`, `thesis.pdf` at root). After any edit, render
  in the background and, for figures, **look at the actual PDF pixels** before trusting it.

## What got done this session

### "What is Biomedical Text?" triptych (`sources/biomedical_text/{clinical,scientific,web}.tex`) — DONE
- **Bilingual example figures**: each chapter opens on a side-by-side box, **French original
  (left, ink) / English translation (right, muted `ThesisNeutral`)**, thin vertical rule,
  tiny labels `FRANÇAIS` and `ENGLISH · TRANSLATION`. French is the source; English is our
  translation, shown muted to signal that. Implementation = a 2-column `tabular` with an
  `!{...\vrule...}` separator, each column a `\begin{minipage}[t]{0.40\textwidth}`.
- **Prose fully reworked** to plain, human, CamemBERT-bio voice: first hand-dictated by Rian
  (clinical P1–P7), then several fable-subagent passes (full rewrite → clarify-enrich →
  simplify → style/anti-antithesis). Clinical Foucault paragraph now `\Cref`s the figure and
  ties the *clinical gaze* to its localised findings (anterior leads, LAD, left ventricle).

### Related Works ch. "Language Models" (`sources/related_works/language_modeling.tex`) — 5.1–5.7 DONE
- **5.1 Introduction** (Markov→Shannon→chain rule→Bengio→Vaswani), **5.2 From Statistical to
  Neural** (n-gram, neural, RNN), **5.3 Transformer**, **5.4 Pretraining Objectives**
  (CLM/MLM/mixing), **5.5 Scaling Laws & LLMs** (5.5.1 Scaling; 5.5.2 Instruction Tuning;
  5.5.3 Aligning Assistants/RLHF/HHH; 5.5.4 Reasoning & Verifiable Rewards / DeepSeek-R1),
  **5.6 Continual Pretraining** (DAPT/TAPT, catastrophic forgetting, making it work,
  from-scratch vs continue), **5.7 Biomedical Language Models** (English encoders, French
  models, biomedical decoders) — all prosified AND through a final plain-style simplification.
- **Figures added** (all hand-built TikZ in thesis colours, Tufte, verified at the pixel level):
  Shannon entropy bars, next-token schema, **word2vec king−man+woman≈queen parallelogram**
  (`fig:lm-word2vec`), unrolled RNN, **gradient vanishing/exploding** analytical-bound plot
  (`plots/related_works/rnn_gradient.py`), attention-mask matrices, CLM/MLM objectives,
  few-shot 3-panel prompt box, **Chinchilla scaling** plot (`plots/related_works/chinchilla_scaling.py`),
  **LLaMA-13B-vs-GPT3** bars (`plots/related_works/llama_vs_gpt3.py`), DAPT/TAPT pipeline.

### TODO / NOT done
- **5.8 Architectures modernes, 5.9 Tokenization, 5.10 Limites et transition** in
  `language_modeling.tex` are **still telegraphic French outlines** — prosify next (same method).
- Other RW chapters **`corpus_annotation.tex` (`chap:rw-corpus`) and `clinical_ie.tex`
  (`chap:rw-ie`) are still telegraphic** — untouched this session.
- **`research/clinical_verify_todo.md`**: the Harris "fewer words" claim (clinical P2) needs a
  verbatim check against Harris before submission (the vocabulary may be *different*, not smaller).
- **Bib dedup**: GPT-3 has two entries — `gpt3` (used) and `brown2020language` (duplicate) —
  collapse to one before submission.
- **`make checkbib`** before submission: many refs added this session (FLAN/T0/Super-NI/
  Self-Instruct, Christiano, Askell/Bai-HH/Constitutional-AI, Self-Consistency, DeepSeekMath,
  Tülu3, Ouyang-InstructGPT, DeepSeek-R1 Nature, Gururangan, McCloskey&Cohen, Shi-CSUR-2025,
  Yıldız, Zheng-ICLR2025, Ibrahim-TMLR, Guo, Xie-Findings-ACL, FlauBERT, CamemBERTa,
  CamemBERT-2.0, Alsentzer, LinkBERT, PMC-LLaMA, bengio-1994, pascanu-2013). All were added
  with exact published-venue metadata verified by curl to Crossref/OpenAlex/DBLP/ACL-Anthology
  (never WebFetch). Also fixed a wrong author list in `kirkpatrick2017ewc`.

## The working method that Rian likes (reuse it)
- **fable-subagent writing passes.** For plainer/more-human prose, dispatch `fable`-model
  subagents (Agent tool, `model: fable`). Calibrate each on the CamemBERT-bio paper
  (`publications/CamemBERT_bio___LREC_COLING_2024/camembert-bio-lrec-coling2024.tex`) and make
  them **quote two sentences from it as proof of reading**. The dial, from boldest to lightest:
  full rewrite → clarify-and-enrich → pure simplification → style (kill antithesis). State the
  goal explicitly each time.
- **Hard ban on "not X but Y" / "X, not Y" antithesis seesaws** (writing-guide §7). They keep
  creeping back in; copying CamemBERT-bio's voice closely is the cure. Also flagged this
  session: padding "itself" / "the X itself", and dangling comparatives ("a simpler reason"
  with nothing to compare to).
- **Concurrent same-file edits corrupt.** When several subagents must edit ONE file
  (e.g. `language_modeling.tex` section by section), have each `cp` the file to a unique
  `/tmp/...tex`, edit only its section there, then merge section-by-section in the main loop
  by `\section{...}` markers (Python splice). Do not let >1 agent Edit the same repo file at once.
- **Verbatim ref extraction.** For any cited number/quote/bib, a curl-only subagent: prefer the
  published venue, quote the exact source (file:line or DOI), list what is UNAVAILABLE
  (figure-only data, missing DOI), never invent. Reports live in `research/*.md` (gitignored).
- **Voice mode** (`mcp__voice-mode__converse`): Rian dictates in French; translate to *simple,
  idiomatic* English (not literal), keep only what he says, render the PDF in the background
  after each iteration. He chooses the formulations; you fix the oral slips.

## Hard rules (do not break)
- Anti-hallucination: never invent a citation, DOI, page, or number. Verify by curl, flag
  unverifiable. Watch for unverified claims re-introduced by subagents (e.g. the removed
  "case reports and hospital notes are written by the same doctors").
- Related Works altitude: describe the landscape, never spoil our own contributions
  (CamemBERT-bio etc.) and never `\Cref` our result chapters from RW; pose open questions.
  Do not cite OpenAI o1 (no paper) — DeepSeek-R1 is the citable marker of the reasoning turn.
- Commits: sole author Rian, telegraphic lowercase messages, no Co-Authored-By. Never commit
  `research/` or `sources/drafts/` (gitignored: PII, copyrighted PDFs, scratch).
