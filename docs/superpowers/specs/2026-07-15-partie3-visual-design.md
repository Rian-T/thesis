# Partie 3 — Visual design specification

Date: 2026-07-15  
Status: approved direction; implementation not started

## Objective

Make Part 3 figure-led without replacing quantitative evidence with decoration. The body will contain fourteen figures and the result tables required to inspect exact values. Appendices will contain reproducibility material that does not advance the argument directly: hyperparameters, complete prompts, full field dictionaries, threshold sweeps, run configurations, and exhaustive per-field results.

The visual argument follows one clinical thread from public text to synthetic longitudinal supervision, open-vocabulary extraction, and completion of an 89-field eCRF. Every visual must answer one scientific question that would otherwise require a long paragraph or an opaque result table.

## Authoritative inputs

Narrative and claim scope:

- `research/lymphome/PARTIE3_INTRA.md`
- `research/lymphome/PARTIE3_EXTRA.md`
- `research/lymphome/06_TAPDL.md`
- `research/lymphome/02_CHIFFRES_CANONIQUES.md`
- `research/lymphome/07_RESULTATS.md`

Quantitative sources, in priority order:

1. `research/lymphome/results.json` for registered, canonical results;
2. the JSON score files and prediction parquets under `research/lymphome/data/`, recomputed with `research/lymphome/score_unified.py` when a derived curve or confidence interval is required;
3. a claim in the Markdown audit only when it is explicitly marked provisional in the figure caption and surrounding prose.

`research/lymphome/PARTIE3_NARRATIF_v2.md` is not a source. `/tmp/dashboard.md` may help locate a run but cannot supply a final number.

## Relationship to Parts 1 and 2

The figures will reuse the existing thesis grammar rather than introduce a Part 3-specific style:

- concrete text cards and worked examples, as in the Part 1 document-versus-paragraph figure;
- compact process diagrams, as in the CLM detour and OntoBook pipelines;
- small multiples and direct quantitative comparisons, as in the Part 2 CKA and intervention figures;
- exact values in `booktabs` tables, with plots carrying the conclusion and tables carrying the audit trail.

Generic three-box pipelines are insufficient when a real clinical excerpt can show the mechanism. Radar charts, pie charts, decorative Sankey diagrams, 3D effects, and pictograms are excluded.

## Visual system

### Source of truth

All colors, fonts, line weights, and plot defaults come from:

- `thesis-style.sty`
- `plots/thesis_style.py`
- `guidelines/visual-style.md`

No figure may hard-code a new palette.

### Palette and semantics

| role | thesis token | hex | use in Part 3 |
|---|---|---:|---|
| our encoder / learned representation | `ThesisPrimary` | `#A694E8` | encoder trajectories, embeddings, our trained systems |
| encoder emphasis | `ThesisPrimaryDark` | `#5A48A0` | outlines, direct labels, highlighted primary result |
| accepted supervision / retained information / constraint | `ThesisSecondary` | `#ABCC6E` | accepted spans, observed evidence, valid assignment |
| supervision emphasis | `ThesisSecondaryDark` | `#5F8228` | labels and outlines for accepted or retained elements |
| LLM / generation | `ThesisTertiary` | `#F1B890` | Qwen, generation stages, LLM trajectories |
| LLM emphasis | `ThesisTertiaryDark` | `#B46E3C` | outlines and direct labels for LLM elements |
| neutral / external baseline | `ThesisNeutral` | `#667082` | baselines, axes, unavailable or contextual elements |
| body ink | `ThesisInk` | `#2D2A3C` | text and primary axes |
| paper panel | `ThesisPaper` | `#F9F7FC` | example cards and background panels |
| failure / warning only | existing muted red baseline | `#C25A5A` | drops, inaccessible target, established failure |

Color never carries the distinction alone. Line style, marker shape, labels, and ordering must preserve the message in grayscale.

### Typography and output

- TeX Gyre Pagella / Palatino, inherited from the thesis.
- Sans-serif only for compact diagram labels where Parts 1 and 2 already use it.
- Vector PDF is the final plot format; PNG is generated only for inspection and Markdown previews.
- Figure captions appear below figures and state the conclusion, not only the contents.
- Table captions appear above tables in the final TeX.
- Plots use direct labels where possible and avoid legends floating over data.
- Confidence intervals or uncertainty bands are mandatory for the principal encoder-versus-Qwen comparison.

### Color continuity across figures

Lavender always denotes the encoder family and peach always denotes the LLM family. This mapping must not flip between panels. Lime denotes supervision or an accepted structural decision, not a third model family. Gray denotes contextual or external baselines. Red is reserved for a loss, collapse, failure, or inaccessible target.

## Figure inventory

### Figure 1 — From longitudinal record to completed form

- **Location:** Introduction, after “Des empans à un formulaire rempli”.
- **Form:** full-width TikZ worked example.
- **Question:** why is this more than local span extraction?
- **Content:** four or five dated document cards, a compact patient timeline, and selected eCRF fields. `CHOEP-14` appears in first-line and second-line contexts and maps to different fields.
- **Message:** the same string can fill different fields; the target is a role in a longitudinal trajectory.
- **Data:** a verified excerpt from synthetic record `lym_76`.
- **Text displaced:** most of the verbal explanation of role binding in the opening hook.

### Figure 2 — Evidence around an inaccessible target

- **Location:** Introduction, “Évaluer une cible inaccessible”, before the evidence table.
- **Form:** TikZ evidence map.
- **Question:** what can be evaluated without French hospital records annotated for the eCRF?
- **Content:** inaccessible central target surrounded by synthetic eCRF, PARHAF, FrACCO, and reference-free LLM judge. Each proxy has one visible evidence dimension and one open gap.
- **Message:** the four evaluations are complementary; none establishes clinical validity on real hospital notes.
- **Table retained:** evidence source / tested dimension / claim not established.

### Figure 3 — Two supervision routes

- **Location:** opening of Chapter 1.
- **Form:** two-lane TikZ pipeline.
- **Question:** how do the generalist extractor corpus and the lymphoma capstone corpus differ?
- **Content:** public paragraph annotation and distillation in the upper lane; PMC patient cases, longitudinal generation, and TAPDL in the lower lane; convergence only at specialist training.
- **Message:** the two corpora serve different stages and are not interchangeable versions of one dataset.
- **Data:** canonical corpus volumes and split counts.

### Figure 4 — Wavefront longitudinal generation

- **Location:** Chapter 1, “Générer des dossiers longitudinaux”.
- **Form:** four-panel TikZ storyboard.
- **Question:** how is future information prevented from leaking into earlier generated notes?
- **Content:** source case, reconstructed chronology, generation at time `t` with future events masked, final multi-document record.
- **Message:** each note is generated from the patient history available at that point in the trajectory.
- **Data:** one verified source-to-synthetic example.

### Figure 5 — TAPDL from LLM output to exact offsets

- **Location:** Chapter 1, “Construire la référence silver avec TAPDL”.
- **Form:** detailed TikZ flow with a single example crossing all stages.
- **Question:** how does one LLM pass become an auditable span reference?
- **Content:** report, field/value proposal, literal match, fuzzy recovery, global offsets, collision resolution, final silver annotations. Audit counters are placed on their relevant transitions.
- **Message:** semantic proposals are produced by the LLM; offsets and exclusivity are established deterministically.
- **Data:** TAPDL counters registered in `06_TAPDL.md` and the canonical result registry.

### Figure 6 — Stylistic distance to human-written PARHAF

- **Location:** Chapter 1, “Mesurer la distance au registre hospitalier”.
- **Form:** four horizontal dot-plot small multiples for FED, MMD, MAUVE, and C2ST.
- **Question:** which public or synthetic source is closest to the available human-written clinical proxy?
- **Content:** identical source ordering in all panels; raw metric axes rather than a normalized radar.
- **Message:** generated records remain distinguishable from PARHAF; generation does not remove the synthetic signature.
- **Table retained:** exact values and metric directionality.

### Figure 7 — MedEmbed lineage and open-vocabulary inference

- **Location:** Chapter 2, after “Donner les types à l’inférence”.
- **Form:** two-panel TikZ figure.
- **Question:** where does MedEmbed come from, and how does a natural-language type description guide extraction?
- **Content:** panel A shows Part 1 clinical content, ModernCamemBERT-bio, OntoBook-derived terminology pairs, contrastive training, and MedEmbed without implying a false serial checkpoint stack. Panel B uses a real description and candidate spans to show description/span embeddings and similarity scoring.
- **Message:** open-vocabulary extraction depends on the geometry of descriptions, not a fixed output classifier.

### Figure 8 — Anatomy of the supervision signal

- **Location:** Chapter 2, “Ce qui détermine le transfert zéro-shot”.
- **Form:** two-panel quantitative diagnostic.
- **Question:** what do annotation density and public clinical text teach the extractor?
- **Content:** panel A connects empty-document rate, predicted density, and recall/value score. Panel B is a sorted dumbbell plot comparing full pretraining with the no-clinical ablation by eCRF section.
- **Message:** density teaches how much to predict; public clinical content has a concentrated effect on treatment fields that a global mean hides.
- **Data:** density variants and the 200-record clinical-content ablation.

### Figure 9 — Contrastive training on familiar and novel types

- **Location:** Chapter 2, “Évaluer les descriptions absentes des benchmarks”.
- **Form:** paired dot plots for common and deliberately novel descriptions.
- **Question:** does MedEmbed help specifically when the requested type was absent from training benchmarks?
- **Content:** backbone and MedEmbed variants connected across common and novel panels; judge dependence is shown in a neutral annotation box.
- **Message:** the contrastive description space primarily supports transfer to novel types, but the score is a judge preference rather than human medical gold.
- **Gate:** the figure is final only after its A/B values are registered in `results.json`; until then it is rendered as a draft and not cited as definitive evidence.

### Figure 10 — Specialization versus retained openness

- **Location:** end of Chapter 2, “La spécialisation efface l’ouverture”.
- **Form:** synchronized two-panel slope or dumbbell plot.
- **Question:** what does eCRF specialization gain and what does it erase?
- **Content:** generalist, eCRF specialist, and mixed specialist shown on target eCRF performance and PARHAF zero-shot performance.
- **Message:** specialists converge on the target while losing most external open-vocabulary capacity; mixed training mitigates but does not remove the loss.
- **Replacement:** retires current `fig06b_renversement`.

### Figure 11 — Three evaluation units

- **Location:** Chapter 3, “Protocole d’évaluation”.
- **Form:** four-panel pedagogical TikZ example.
- **Question:** why can eCRF, NER, span F1, and value F1 not be interpreted as the same task?
- **Content:** one clinical sentence reused for one-value-per-field scoring, multi-mention NER, non-empty span overlap, and token-Jaccard value matching. A date or numeric formatting example exposes the surface-form limitation.
- **Message:** the metrics reward different units and use permissive matching rules.
- **Table retained:** evaluation set, unit, matching, threshold source, and main limitation.

### Figure 12 — Core capstone result

- **Location:** Chapter 3, spanning “Ajouter la structure du formulaire” and “Comparaison finale”.
- **Form:** full-width two-panel Matplotlib figure.
- **Question:** were the models already close before decoding, and what happens after applying form constraints?
- **Content:** panel A shows top-1 to compete trajectories for all models, with the 150M encoder and Qwen3.5-9B highlighted. It annotates the raw gap of about 0.032 and final gap of about 0.001. Panel B is a grouped dot plot of final value F1 and span F1, with paired confidence intervals for the principal comparison.
- **Message:** the decoder closes an already modest gap; it does not create small-model competitiveness from a large initial deficit.
- **Table retained:** complete model list, parameters, value F1, span F1, and uncertainty for registered comparisons.
- **Replacement:** supersedes the narrative roles of current `fig04_capstone` and `fig05_decodage_structurel`.

### Figure 13 — Equal aggregate score, different failure behavior

- **Location:** Chapter 3, “Ce que le score final masque”.
- **Form:** two-panel Matplotlib diagnostic.
- **Question:** in what ways does Qwen remain stronger despite a tied final value F1?
- **Content:** panel A compares the share of “correct value, wrong field” errors. Panel B plots complete risk-coverage curves and marks 50 percent coverage.
- **Message:** Qwen binds roles and ranks its uncertainty better; the encoder advantage is footprint, not equivalent error behavior.
- **Gate:** error taxonomy and risk-coverage values must be regenerated or verified from prediction-level data before final rendering.

### Figure 14 — Adaptation efficiency and external scope

- **Location:** end of Chapter 3, before the chapter conclusion.
- **Form:** three-panel Matplotlib small multiple.
- **Question:** how efficiently does the encoder adapt, and does that efficiency transfer across task structures?
- **Content:** panel A is the eCRF learning curve on a logarithmic training-record axis. Panels B and C show zero-shot to 100-example adaptation on PARHAF and FrACCO with matched trajectories only where both endpoints exist.
- **Message:** little synthetic supervision recovers much of the task-specific score, but the method is not universally superior; the published baseline remains much stronger on dense FrACCO NER.
- **Replacement:** incorporates and improves current `fig06_efficacite_donnees`; external tables remain in the body.

## Tables in the body

The body retains the following result-bearing tables:

1. evidence source, tested dimension, and claim not established;
2. corpus provenance, volume, license status, and downstream use;
3. TAPDL audit counters and resulting annotation total;
4. exact FED, MMD, MAUVE, and C2ST values;
5. extraction interventions, observed effect, control quality, and authorized interpretation;
6. OntoBench, fixed-benchmark, and novel-type judge results;
7. evaluation protocols and matching rules;
8. complete capstone model comparison;
9. PARHAF and FrACCO external results, presented as two blocks of one table if legible.

No table is removed solely because a figure uses the same experiment. A table remains when it supplies exact values, comparison completeness, sample sizes, confidence intervals, or control conditions that the plot intentionally suppresses.

## Appendix allocation

Appendices contain:

- hyperparameters for each model family;
- complete generation, TAPDL, and judge prompts;
- all 89 eCRF fields and their descriptions;
- run identifiers and training configurations;
- per-field and per-section result matrices;
- threshold sweeps and complete bootstrap distributions;
- additional dossier examples;
- focal-loss and imperfectly matched architecture variants;
- extended ablations that do not change a chapter-level conclusion.

## Existing figure disposition

| current asset | disposition |
|---|---|
| `fig03_decode_schema` | retain the concept; redraw with full sentence context and explicit limitation |
| `fig04_capstone` | replace with Figure 12 panel B |
| `fig05_decodage_structurel` | replace delta-only bars with Figure 12 panel A trajectories |
| `fig06_efficacite_donnees` | retain data; redesign inside Figure 14 |
| `fig06b_renversement` | retire; replace with Figure 10 |
| `fig07_scaling_llm` | remove from the main text because the undertrained 4B run prevents a scaling claim |
| `fig08_ablation_clinique` | retain result; redesign as Figure 8 panel B |

## Implementation layout

Schematic figures will be implemented in TikZ inside the relevant Part 3 chapter source or in small `figures/*.tex` inputs when reuse or source readability warrants separation. Quantitative figures will be generated by focused scripts under `plots/part_3/`, importing `plots/thesis_style.py`.

Each plotting script will:

1. read a registered JSON source or a named prediction parquet;
2. compute derived quantities rather than embedding final values by hand;
3. write a vector PDF and inspection PNG;
4. expose the data rows used for the figure in a compact machine-readable sidecar when the computation is non-trivial.

The first implementation pass updates `PARTIE3_INTRA.md` with exact figure and table placeholders. TeX integration follows only after the narrative and source data for a figure are stable.

## Verification

Every figure must pass four checks before inclusion:

1. **Numerical:** plotted values match the canonical registry or a reproducible score computation.
2. **Narrative:** the caption states no stronger claim than the corresponding paragraph and evidence permits.
3. **Visual:** PDF and PNG are rendered and inspected at thesis text width; labels remain legible without zooming.
4. **Consistency:** colors, family names, metric names, decimal precision, and model ordering match the other Part 3 figures and the result tables.

The integrated thesis PDF must then be inspected at every Part 3 figure and table page for overflow, float placement, caption separation, and accidental blank space.

## Completion criteria

The visual redesign is complete when:

- all fourteen figures exist as reviewable renders;
- all nine body tables are present or deliberately merged without losing exact evidence;
- every figure is introduced before it appears and followed by the interpretation it supports;
- all principal claims are traceable to `results.json` or a reproducible scoring command;
- no figure relies on `PARTIE3_NARRATIF_v2.md` or dashboard-only numbers;
- the Part 3 palette and typography are indistinguishable from Parts 1 and 2;
- the rendered thesis has no visual or float-placement regressions.
