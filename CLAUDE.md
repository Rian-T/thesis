# CLAUDE.md

> 🚨 **EN COURS — relecture d'ÉRIC + polish global.** Le manuscrit compile propre : **266 p., 0 erreur,
> 0 référence/citation indéfinie, 0 `(?)`, 9 overfull** (le pire à 17,5 pt). Punch-list consolidée :
> **`AUDIT_PUNCHLIST.md`** (racine). Relecture d'Éric : **`TODO.md`** (ses PDF annotés sont dans `~/Downloads/`).
>
> **⚠️ HYGIÈNE DE BUILD — ça a coûté 38 citations cassées.** `rm -rf build` **NE SUFFIT PAS** : des artefacts
> périmés à la **RACINE** (`thesis.aux`, `.bbl`, `.blg`) *shadowent* ceux de `build/`, et bibtex résout alors une
> **vieille liste de citations** → des `(?)` s'impriment **sans aucun warning**. Toujours : `latexmk -C` + `rm -f
> thesis.aux thesis.bbl thesis.blg thesis.toc` + `rm -rf build`, puis `latexmk -g`. Contrôle qui ne ment pas :
> `pdftotext thesis.pdf - | grep -c '(?)'` doit donner **0**. Corollaire : **ne jamais lancer deux `latexmk` en
> parallèle** (les sous-agents qui compilent corrompent les `.aux` et produisent des erreurs fantômes — un
> « `! Extra }` » fatal m'a fait reverter un sweep parfaitement valide).
>
> **CHIFFRES — train-on-test-free, VÉRIFIÉS depuis les parquets (`results.json` PÉRIMÉ).** Capstone eCRF (après
> field competition) : MC-bio-gliner publié **0.640/0.503**, variante task-mixed **0.657** ≈ **Qwen3.5-4B 0.658**
> (parquets `-de1540v2`, PAS les `-lp410`). **Qwen3.5-9B = 0.650, donc AU-DESSUS de nous** : l'abstract ET le
> résumé affirmaient qu'on le battait, **c'était FAUX**, corrigé en « within 0.018 du meilleur générateur, 27× plus
> gros ». QA baselines **ModernCamemBERT 0.336 / -bio 0.417**. GLiNER-BioMed **0.367** (certif GPU abandonnée).
> PARITÉ = HONNÊTE : publié = quasi-parité, SEULE la variante task-adapted atteint la parité. 27× (pas 25×).
>
> **NAMING (appliqué) :** `MC-bio-gliner` / `ModernCamemBERT-bio-gliner` (long, défini 1×) ; `GLiNER-BioMed` ;
> `Qwen3.5-…` ; retrieval terminologique = `ICD-O`. ZÉRO parenthèse de rôle, ZÉRO codename, modèles en **serif
> droit** jamais `\texttt`. eCRF défini à sa 1re occurrence. TABIB (conclusion) : noms **versionnés**
> (`MedGemma 1.5`, `Nemotron-3-Nano`, `Ministral-3 8B`) — la version compte, ne pas la stripper.
>
> **GRAMMAIRE VISUELLE (`FIGURE_GRAMMAR.md`) :** un bloc = UNE chose ; empan/mention = LAVANDE, valeur produite =
> LIME, négatif = PÊCHE, inactif/méta = NEUTRE ; panneau-Document = `ThesisPaper` serif italique ; flèches à sens
> unique. VÉRIFIER CHAQUE figure AU RENDU (pdftoppm), jamais à la source. **fable est bon en narratif, pas en
> spatial** : pour la géométrie d'un TikZ, itérer soi-même render+vision.
>
> **CONVENTIONS FIGÉES (ne pas régresser) :** captions **TOUJOURS EN BAS** (31 tables basculées) et **jamais
> orphelines** — tout bloc non-flottant `\begin{center}…\captionof` est enveloppé d'une `minipage`, **avec
> `\centering` dedans** (une `minipage` exécute `\@parboxrestore`, qui **annule** le `\centering` de `center`).
> Marques de relecture **désactivées** (`\thesisreviewmarksfalse` dans `thesis.tex`). URLs sécables
> (`\PassOptionsToPackage{hyphens}{url}`) + `\emergencystretch=3em` → overfull 88 → 9.
>
> **NEXT (Éric, cf. `TODO.md` + `AUDIT_PUNCHLIST.md`) :** (1) 🔴 **ch1 p.88** « need evaluation results in this
> chapter » — le chapitre corpus n'a aucune éval, seul vrai chantier restant ; (2) 🟠 **ch2 p.98** « Performance of
> Llama-3-8B ? » — ambigu (l'annotateur est le **70B**, les perfs du 8B sont déjà données) → demander à Éric ;
> (3) 🚨 **relecture clinicienne** : « dossiers jugés plausibles par des médecins via un outil web » est **déjà dans
> l'abstract et le résumé** mais **n'a aucune trace dans le repo** → ne rien renforcer avant sa réponse ;
> (4) ancres disparues à confirmer abandonnées (ch6 « Table 15.1 », ch8 « Solon 44.9 », ch8 OOD/zero-shot,
> ch9 p.3/4/5) ; (5) sweep narratif des joints de parties (chaque partie doit passer une question vivante à la
> suivante). Abandonnés : GLiNER-BioMed (certif), « Riccardo ».

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
- `checkbib` only proves a reference is *real*; it does NOT check that the source actually
  says what the prose claims. A separate **claim-level** fact-check (one Opus subagent per
  `\cite`, curl-only, blind, side-by-side with the original PDF) covered the triptych and all
  3 RW chapters — method + verdicts in `research/factcheck2/` and `research/factcheck_rw/`
  (gitignored). Reuse that pattern for new chapters; always read the real `.tex` line before
  applying a fix (the extraction window can truncate a leading digit).

## Git Commit Conventions

These OVERRIDE any default Claude Code commit behavior:

- **Sole author is Rian.** Never add `Co-Authored-By` trailers (no Claude, no anyone). The git author config (`rian-t <rian.touchent@inria.fr>`) is already correct — do not change it.
- **Messages: minimal, telegraphic, dense.** Lowercase, no filler, no marketing slop. State exactly what changed (and why, if non-obvious) in as few words as possible. One-line subject; add a terse body only when several distinct changes need listing.
- Good: `dedup bib: drop 4 ontobook duplicate entries, ch6 -> canonical keys`
- Bad: `This commit improves the bibliography by carefully removing some duplicate entries that were found...`

## Current Status

**Le manuscrit est écrit de bout en bout** (front matter, 6 parties, conclusion, 7 annexes) et compile
propre : **266 p., 0 erreur, 0 référence/citation indéfinie, 0 `(?)`, 9 overfull**. Ce qui reste est de la
relecture, pas de la rédaction. Punch-list : `AUDIT_PUNCHLIST.md`. Relecture d'Éric : `TODO.md`.

Chapter↔label↔source map (les labels sont posés dans les fichiers d'orchestration, pas dans `article.tex`) :

| Fichier | `\label` | Titre | Source |
|----|----------|-------|--------------|
| `part_1/chapter1` | `chap:collecting` | Collecting Biomedical Text | CamemBERT-bio (corpus) |
| `part_1/chapter2` | `chap:quality` | Detecting Content Types | Biomed-Enriched (Findings ACL 2026) |
| `part_1/chapter3` | `chap:mcbio` | Which Quality Signals Matter? | MC-Bio / biomed-fr-v2 (TALN 2026) |
| `part_2/chapter4` | `chap:encoders` | Encoder Models for French Biomedicine | CamemBERT-bio (LREC-COLING 2024) |
| `part_2/chapter5` | `chap:objectives` | Beyond Masked Language Modeling | CLM Detour (COLM 2026) |
| `part_2/chapter6` | `chap:ontobook` | Knowledge-Enriched Pretraining | OntoBook (LREC 2026) |
| `part_3/chapter9` | `chap:synthetic` | Synthetic Data for Task Adaptation | — |
| `part_3/chapter8` | `chap:architectures` | Architectures for Low-Resource Extraction | frenchmed-gliner / MedEmbed |
| `part_3/chapter7` | `chap:evaluation` | Evaluating Open-Vocabulary Extraction | capstone eCRF |

> ⚠️ **PIÈGE — la Partie 3 se lit `chapter9` → `chapter8` → `chapter7`** : les numéros de fichiers sont
> **inversés** par rapport à l'ordre de lecture. `chap:limits` **n'existe plus** (l'ancien « Ch 7 discussion »
> a été absorbé). Conclusion = 3 chapitres dans le seul `sources/conclusion.tex` (`sec:conclusion-holds-together`,
> `sec:conclusion-evaluation`, `sec:conclusion-field-direction`).

### NEW conceptual part "What is Biomedical Text?" (drafted June 2026, sits BEFORE Related Works)

`\part{What is Biomedical Text?}` in `thesis.tex`, between the Introduction and the Related Works part. Orchestration `sources/biomedical_text/biomedical_text.tex` `\input`s three short chapters that form ONE argument (a triptych), arc **RARITY → ABUNDANCE**. The same case (a myocardial infarction) opens each chapter as a figure, in three registers, with parallel one-sentence captions ("... myocardial infarction"):

- `clinical.tex` (`chap:bt-clinical`, "Clinical Text"): the note is a sublanguage (Harris→Sager→Friedman), optimally compressed (Anderson-Sager + Grice/Sperber-Wilson + Stalnaker common ground), performative (Austin/Searle, "DNR"), one-line Foucault; then the French reality (no shareable real corpus; CAS-vs-PARHAF register dispute) and the personal-data reason for privacy; bridges to scientific. Figure = synthetic de-identified discharge note.
- `scientific.tex` (`chap:bt-scientific`, "Scientific Text"): genre as social action (Miller), CARS/gap (Swales), IMRAD is recent + real data (Sollaci 1297 articles), SOAP contrast (Weed), metadiscourse/hedges (Hyland), quantitative register (Biber) + phraseology (Nwogu/Luzón), one-line Latour, Friedman punchline (abundance ≠ substitutability). Figure = real HAL passage on post-infarction mitral insufficiency (from `rntc/mc-bio-corpus`).
- `web.tex` (`chap:bt-web`, "Lay and Web Text"): Fleck (esoteric→exoteric), drug leaflets / *notices* (Directive 2001/83/EC, EMA QRD template), naming variation (Wüster foil / Cabré / Gaudin), Temmerman (fuzzy concepts), UMLS many-to-many (Bodenreider, 2.5M names / 900k concepts), ontology-vs-text gap (Smith & Ceusters), one-line Hacking + Biber; synthesis closes the part ("public data for the clinic = crossing register + resolving names").

**Related Works ch "Language Models" (`chap:rw-lm`, `sources/related_works/language_modeling.tex`):** sections **5.1–5.7 are now full prose, plain CamemBERT-bio voice** (Introduction Markov→Shannon→chain rule→Bengio→Vaswani; From Statistical to Neural; Transformer; Pretraining Objectives; Scaling Laws & LLMs incl. instruction tuning / RLHF-HHH / reasoning-RLVR-DeepSeek-R1; Continual Pretraining; Biomedical Language Models), with hand-built TikZ figures throughout (entropy, next-token, word2vec parallelogram, RNN, gradient bound, attention masks, CLM/MLM, few-shot 3-panel, Chinchilla + LLaMA plots, DAPT/TAPT). **The whole Related Works is now full prose: 5.8 Modern Architectures, 5.9 Tokenization, 5.10 Limits/Transition were prosified, and the other two RW chapters (`corpus_annotation.tex` = `chap:rw-corpus`; `clinical_ie.tex` = `chap:rw-ie`) are fully prosified too — all via fable subagents + a per-chapter fable review pass, ~53 exact refs added by curl. See HANDOFF.md.**

**Research substrate (gitignored `research/`).** Deep-research notes to READ before writing more: `clinical.md`, `scientific.md`, `web.md`, `french_clinical.md`, `lay_leaflets.md`, `rw_language_modeling.md`, plus `*_outline.md`. Built by Opus subagents from primary sources (curl). `research/` also holds PII screenshots + downloaded PDFs → **never commit it**. Scratch LaTeX buffers live in gitignored `sources/drafts/` (e.g. `example_clinical_note.tex` = the synthetic note source).

The triptych prose is **DONE** (plain CamemBERT-bio voice; bilingual example figures, French original / English translation side by side). The lay/web figure is now a synthetic de-identified patient-forum message (the old Doctissimo-excerpt issue is resolved).

**État du related works :** les trois chapitres sont en prose complète, avec figures TikZ maison. Le RW a
en plus **4 figures knowledge-graphs** (`fig:corpus-static` / `-inject` / `-contrastive` / `-g2t`) bâties sur
**un même fragment d'ontologie réel** (diabète de type 2 `E11`, métformine `A10BA02`), et un **schéma GLiNER**
(`fig:ie-gliner`) redessiné depuis l'archi du papier. `research/clinical_verify_todo.md` : vérifier la claim
Harris « fewer words » avant soumission.

**Transitions de parties (2026-07-17, règle à tenir) :** *le pont pose la question, l'unité suivante y répond.*
Un pont ne doit **jamais** écrire l'ouverture de ce qui suit — c'est le défaut qu'on a corrigé deux fois
(un pont volait le hook de ch6 ; un autre pré-livrait l'intro de la Partie 3). ch5→ch6 pose la tension
« les ontologies gardent la connaissance, mais le préentraînement consomme des phrases » ; ch6→Partie 3 pose
la question du fine-tuning. `SEAM_PROPOSALS*.md` gardent les analyses de joints.

**Conventions (follow them) :** captions **en bas, une phrase, jamais orphelines** (blocs non-flottants en
`minipage` **avec `\centering` dedans**) ; exemples textuels en TikZ aux couleurs thèse ; bib ajouté avec des
en-têtes `@comment` ; **`make checkbib` après TOUTE référence citée ajoutée** (la presse et le légal vont au
whitelist, avec leur statut de vérification réel écrit noir sur blanc) ; les entrées de papiers publiés se
prennent **verbatim depuis l'ACL Anthology / le DOI**, jamais à la main ; `guidelines/working-with-rian.md` est
le guide contraignant (anglais académique simple, intuition avant détail, data derrière chaque chiffre, pas de
phrases hachées/IA, pas de tirets cadratins) — **et il se relit souvent, pas une fois**.

### Tout est écrit (les anciennes dettes sont levées)
- **Front matter** — abstract **bilingue** (EN + Résumé FR, chacun sur **une page**), `introduction.tex`,
  `contemporary_ai.tex`, `contributions.tex` (7 contributions + roadmap qui annonce l'ouverture TABIB).
- **Ch 5 (`chap:objectives`)** — le §« placeholder » sur le décrochage du CPT décodeur est **écrit** (« Lessons
  from Decoder Pretraining », sourcé : Dorfner, BioMistral, Meditron, Jindal, Mannion, Obeidat, Lehman).
  Notation de trajectoires **`Φ_{1,CLM}` / `Φ_{1,MLM30%}` / `Φ_{2,MLM15%}`** (demande d'Éric : lever la confusion
  30 %/15 %), `θ_A`/`θ_B` **réellement utilisés** dans les résultats. Sous-section freeze **déplacée après** les
  résultats (elle les anticipait).
- **Ch 6 (`chap:ontobook`)** — **thesis-ifié** : hook (le codeur a besoin de ce que le compte-rendu ne dit jamais),
  `\section*{Conclusion}` qui ferme sur l'insight d'alignement, related-work dédupliqué vers `\Cref{chap:rw-corpus}`,
  tables déjà en booktabs + `ThesisTableSep`.
- **Partie 3** — les trois chapitres sont écrits (supervision, extracteur ouvert, capstone eCRF).
- **Conclusion** — triptyque de 3 chapitres × 3 sections (What Holds Together / A New Problem / Where Medical AI
  Is Going), avec TABIB et l'environnement agentique.
- **Appendix** — 7 chapitres (A–G).

### Ce qui reste (relecture, pas rédaction)
- 🔴 **Éric ch1 p.88** — « need some evaluation results in this chapter, with comparison with other models » : le
  chapitre corpus n'a **aucune éval**. **Seul vrai chantier de rédaction restant.**
- 🟠 **Éric ch2 p.98** — « Performance of Llama-3-8B ? » : ambigu (l'annotateur est **Llama-3.1-70B** ; les perfs du
  8B, qui est une *baseline*, sont déjà dans deux tables) → lui demander ce qu'il visait.
- ⚪ **Ancres d'Éric disparues** (texte réécrit depuis sa relecture) → confirmer qu'on abandonne : ch6 « Table 15.1 »,
  ch8 « Solon 44.9 », ch8 « out-of-domain / zero-shot » (renommé « familiar / benchmark-absent »), ch9 p.3/4/5.
- 🟠 **Appendix : 6 annexes sur 7 sont orphelines** (aucun `\Cref` du corps ne pointe vers elles ; seule
  `app:tabib-details` est citée). Le fix vit dans **le corps**, pas dans l'appendix.
- 🟡 **Citations manquantes** : 30 M séjours PMSI (ch6 + clinical_ie ×2, `% TODO(cite)` posé), BioBERT 18 Md,
  AliBERT, tailles ICD-10/CCAM/ATC, split « échocardiographie ».
- 🟡 **Sweep style** : antithèses « not X but Y » (clinical.tex, web.tex, ch2, ch3), captions multi-phrases,
  4 exemples placeholder en ch2, les 20 overfull restants (tous < 18 pt).
- ⚪ **Décision de Rian (2026-07-17)** : l'affirmation « des cliniciens ont jugé les dossiers plausibles » **reste**
  dans l'abstract et le résumé, bien qu'Éric n'en ait fourni aucun détail. Ne pas la re-soulever.
- **Push** : de nombreux commits non poussés — **pousser uniquement sur signal de Rian**.

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
