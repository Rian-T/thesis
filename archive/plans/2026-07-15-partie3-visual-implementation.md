# Part 3 Visual Redesign Implementation Plan

## Revision pass: readability before prose

- [ ] Inspect every Part 3 PNG and rendered TikZ at manuscript scale; record the
      single question answered and a keep/simplify/split decision.
- [ ] Split the public-clinical-text ablation into a global plot and a
      section-level plot, each referenced before its float.
- [ ] Remove status columns, repeated row-level sample sizes, internal run names,
      and provenance metadata from body tables and figures.
- [ ] Restyle TikZ schemas against the Parts I--II templates and render them in
      the complete manuscript.
- [ ] Replace aggregate-only MedEmbed evidence with OntoBench-FR v9 per-task
      retrieval results and distinguish FrACCO retrieval from FrACCO NER.
- [ ] Compile and inspect all Part 3 pages for overlap, tiny text, whitespace,
      and float order.
- [ ] Audit every telegraphic bullet for repetition, missing context, wrong
      order, unsupported transitions, and evidence-level mismatch.
- [ ] Present the narrative audit before converting any bullet block to prose.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build, verify, and integrate the fourteen approved Part 3 figures and nine result-bearing tables while preserving the exact visual language of Parts 1 and 2.

**Architecture:** Separate evidence from presentation. A provenance manifest and typed loader provide every plotted value; focused Matplotlib scripts build quantitative figures; focused TikZ inputs build explanatory figures; chapter sources consume only reviewed outputs. Preview builds may expose provisional results, but final builds fail until every principal observation is registered and traceable.

**Tech Stack:** Python 3, Matplotlib, pandas, pyarrow, pytest, JSON, TikZ/PGFPlots, `siunitx`, `booktabs`, `latexmk`, Poppler (`pdfinfo`, `pdftoppm`, `pdffonts`).

## Global Constraints

- Treat `research/lymphome/PARTIE3_INTRA.md` as the narrative source and ignore `PARTIE3_NARRATIF_v2.md`.
- Treat `research/lymphome/results.json` as the primary quantitative registry; never promote a dashboard-only number to a final figure.
- Reuse `thesis-style.sty`, `plots/thesis_style.py`, and `guidelines/visual-style.md`; do not add a Part 3 palette.
- Lavender `#A694E8` denotes our encoder, peach `#F1B890` denotes LLMs, lime `#ABCC6E` denotes accepted supervision or structure, gray `#667082` denotes neutral/external baselines, and muted red `#C25A5A` denotes a loss, failure, or inaccessible target.
- Deliver vector PDF for the thesis and PNG for review. Use TeX Gyre Pagella/Palatino through the existing style.
- Keep result tables in the body. Move only hyperparameters, complete prompts, run configurations, full field dictionaries, threshold sweeps, and exhaustive per-field results to appendices.
- Never stage unrelated dirty-worktree changes. Every commit command names its files explicitly.
- A preview figure may use a provisional observation only when the caption and manifest mark it provisional. The final thesis build must reject provisional principal observations.
- Do not claim that structural decoding creates the small model's competitiveness: the raw encoder/9B gap is approximately 0.032 before decoding.

---

## File Map

### Create

- `plots/part_3/__init__.py` — package marker.
- `plots/part_3/common.py` — paths, typed observations, registry loading, style, save helper.
- `plots/part_3/build_all.py` — deterministic CLI for Figures 6, 8, 9, 10, 12, 13, and 14.
- `plots/part_3/plot_chapter9.py` — Chapter 1 quantitative Figure 6.
- `plots/part_3/plot_chapter8.py` — Chapter 2 quantitative Figures 8–10.
- `plots/part_3/plot_chapter7.py` — Chapter 3 quantitative Figures 12–14.
- `plots/part_3/data/visual_data.json` — non-capstone observations with source, status, and sample size.
- `plots/part_3/data/README.md` — provenance contract and derivation commands.
- `plots/part_3/output/*.pdf` and `*.png` — generated outputs, one stem per quantitative figure.
- `sources/part_3/figures/fig01_longitudinal_to_ecrf.tex`
- `sources/part_3/figures/fig02_evidence_map.tex`
- `sources/part_3/figures/fig03_supervision_routes.tex`
- `sources/part_3/figures/fig04_wavefront.tex`
- `sources/part_3/figures/fig05_tapdl.tex`
- `sources/part_3/figures/fig07_medembed.tex`
- `sources/part_3/figures/fig11_metrics.tex`
- `tests/part_3/test_visual_data.py` — provenance and provisional-state tests.
- `tests/part_3/test_visual_build.py` — output, style, and smoke tests.

### Modify

- `research/lymphome/PARTIE3_INTRA.md` — exact figure/table placements and review captions.
- `sources/part_3/chapter9/article.tex` — Chapter 1 figures/tables.
- `sources/part_3/chapter8/article.tex` — Chapter 2 figures/tables.
- `sources/part_3/chapter7/article.tex` — Chapter 3 figures/tables.
- `sources/appendix.tex` — Part 3 hyperparameters, prompts, field dictionary, and exhaustive diagnostics only.
- `research/lymphome/results.json` — only when a verified missing observation is registered with source metadata.

### Retire after replacement verification

- `research/lymphome/make_partie3_figs.py`
- superseded assets under `research/lymphome/partie3_figs/`; retain them until the new thesis pages have been visually approved.

---

### Task 1: Establish the Visual Evidence Contract

**Files:**

- Create: `plots/part_3/data/visual_data.json`
- Create: `plots/part_3/data/README.md`
- Create: `tests/part_3/test_visual_data.py`
- Inspect: `research/lymphome/results.json`
- Inspect: `research/lymphome/02_CHIFFRES_CANONIQUES.md`
- Inspect: `research/lymphome/06_TAPDL.md`
- Inspect: `research/lymphome/07_RESULTATS.md`
- Inspect: `research/lymphome/PARTIE3_EXTRA.md`

**Interfaces:**

- Produces: JSON observations shaped as `{value, status, source, n, note}`.
- `status` is exactly `registered` or `provisional`.
- Later tasks consume keys under `stylometry`, `supervision`, `novel_types`, `decoding`, `errors`, and `data_efficiency`.

- [ ] **Step 1: Write the failing provenance test**

```python
import json
from pathlib import Path

DATA = Path("plots/part_3/data/visual_data.json")


def walk(node, path="root"):
    if isinstance(node, dict) and "value" in node:
        yield path, node
    elif isinstance(node, dict):
        for key, value in node.items():
            yield from walk(value, f"{path}.{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from walk(value, f"{path}[{index}]")


def test_every_observation_is_traceable():
    payload = json.loads(DATA.read_text())
    observations = list(walk(payload))
    assert observations
    for path, observation in observations:
        assert observation["status"] in {"registered", "provisional"}, path
        assert observation["source"].strip(), path
        assert isinstance(observation["value"], (int, float)), path


def test_no_dashboard_only_final_observation():
    payload = json.loads(DATA.read_text())
    for path, observation in walk(payload):
        if observation["status"] == "registered":
            assert "dashboard" not in observation["source"].lower(), path
```

- [ ] **Step 2: Run the test and confirm it fails because the manifest is absent**

Run:

```bash
uv run --with pytest pytest tests/part_3/test_visual_data.py -v
```

Expected: FAIL with `FileNotFoundError` for `visual_data.json`.

- [ ] **Step 3: Create the manifest with audited observations**

Use this exact top-level shape:

```json
{
  "_meta": {
    "schema": 1,
    "created": "2026-07-15",
    "final_requires_all_principal_registered": true
  },
  "stylometry": {},
  "supervision": {},
  "novel_types": {},
  "decoding": {},
  "errors": {},
  "data_efficiency": {}
}
```

Populate the known registered observations from the repository, including:

- TAPDL: 275544 raw proposals, 15868 literal misses, 7441 fuzzy recoveries, 27491 raw collisions, 237194 final spans, 89 fields;
- data efficiency: `(10, 0.182)`, `(50, 0.485)`, `(100, 0.544)`, `(500, 0.603)`, `(1540, 0.659)`, sourced to `07_RESULTATS.md:198-202` and the named prediction parquets;
- calibration: Qwen AURC 0.228 and precision-at-50-percent 0.813; encoder AURC 0.313 and precision 0.667, sourced to `02_CHIFFRES_CANONIQUES.md:93-94`;
- role-binding error shares: Qwen 0.405 and encoder 0.605, marked provisional until prediction-level regeneration is recorded;
- decoding deltas and intervals from `PARTIE3_INTRA.md:164`, marked provisional until registered in `results.json`;
- stylometry values already printed in `PARTIE3_INTRA.md:69-73`: MAUVE 0.040/0.017/0.006, FED 0.28/0.35/0.74, C2ST 0.991/0.988/0.985.

For MMD, apply one non-ambiguous rule: include the panel only if the original `styleSOTA_1819572.out` or a reproducible script/output pair is found and copied into a repository-tracked source record. Otherwise update the design spec and Figure 6 caption to a three-panel figure; never invent or infer MMD from the other metrics.

- [ ] **Step 4: Document derivation and status rules**

In `plots/part_3/data/README.md`, record:

```markdown
# Part 3 visual data

`registered` means the value is backed by `results.json`, a tracked score JSON,
or a named prediction parquet plus a reproducible command. `provisional` means
the value is useful for a review render but is barred from final thesis claims.

Final plots are built without `--allow-provisional`. Preview plots may be built
with that flag and must display `PRELIMINARY` in the lower-right margin.
```

- [ ] **Step 5: Run the provenance tests**

Run:

```bash
uv run --with pytest pytest tests/part_3/test_visual_data.py -v
```

Expected: both tests PASS.

- [ ] **Step 6: Commit only the contract files**

```bash
git add plots/part_3/data/visual_data.json plots/part_3/data/README.md tests/part_3/test_visual_data.py
git commit -m "test: register Part 3 visual evidence"
```

---

### Task 2: Build Shared Plot Infrastructure

**Files:**

- Create: `plots/part_3/__init__.py`
- Create: `plots/part_3/common.py`
- Create: `plots/part_3/build_all.py`
- Create: `tests/part_3/test_visual_build.py`

**Interfaces:**

- Produces: `Observation`, `load_visual_data`, `load_results`, `result_value`, `save_figure`, `mark_preliminary`.
- Plot modules expose `build(output_dir: Path, allow_provisional: bool) -> list[Path]`.

- [ ] **Step 1: Write failing loader and style tests**

```python
from pathlib import Path
import pytest

from plots.part_3.common import (
    ProvisionalDataError,
    load_visual_data,
    result_value,
    semantic_colors,
)


def test_final_loader_rejects_provisional_principal_values():
    with pytest.raises(ProvisionalDataError):
        load_visual_data(allow_provisional=False)


def test_preview_loader_accepts_provisional_values():
    assert load_visual_data(allow_provisional=True)["_meta"]["schema"] == 1


def test_semantic_palette_matches_thesis():
    assert semantic_colors() == {
        "encoder": "#A694E8",
        "llm": "#F1B890",
        "structure": "#ABCC6E",
        "neutral": "#667082",
        "failure": "#C25A5A",
    }


def test_registered_capstone_value_is_loaded_by_identity():
    assert result_value("ecrf", "MC-bio-gliner (v3b)", "capstone", "value") == pytest.approx(0.6467)
```

- [ ] **Step 2: Run the tests and confirm the module is missing**

Run:

```bash
uv run --with pytest --with matplotlib pytest tests/part_3/test_visual_build.py -v
```

Expected: collection FAIL with `ModuleNotFoundError: plots.part_3.common`.

- [ ] **Step 3: Implement the typed loader and style contract**

```python
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

import matplotlib.pyplot as plt

from plots.thesis_style import COLORS, apply_style

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "research/lymphome/results.json"
VISUAL_DATA = Path(__file__).parent / "data/visual_data.json"
DEFAULT_OUTPUT = Path(__file__).parent / "output"


class ProvisionalDataError(RuntimeError):
    pass


@dataclass(frozen=True)
class Observation:
    value: float
    status: str
    source: str
    n: int | None = None
    note: str = ""


def semantic_colors() -> dict[str, str]:
    return {
        "encoder": COLORS["primary"],
        "llm": COLORS["tertiary"],
        "structure": COLORS["secondary"],
        "neutral": COLORS["neutral"],
        "failure": COLORS["baseline"],
    }


def _observations(node):
    if isinstance(node, dict) and "value" in node:
        yield node
    elif isinstance(node, dict):
        for child in node.values():
            yield from _observations(child)
    elif isinstance(node, list):
        for child in node:
            yield from _observations(child)


def load_visual_data(allow_provisional: bool = False) -> dict:
    data = json.loads(VISUAL_DATA.read_text())
    if not allow_provisional and any(x["status"] == "provisional" for x in _observations(data)):
        raise ProvisionalDataError("principal visual data remain provisional")
    return data


def load_results() -> dict:
    return json.loads(RESULTS.read_text())


def result_value(benchmark: str, display: str, regime: str, metric: str) -> float:
    matches = [entry for entry in load_results()[benchmark].values()
               if isinstance(entry, dict)
               and entry.get("display") == display
               and entry.get("regime") == regime]
    if len(matches) != 1:
        raise KeyError((benchmark, display, regime, len(matches)))
    return float(matches[0][metric])


def configure_style() -> None:
    apply_style()
    plt.rcParams.update({"figure.constrained_layout.use": True})


def mark_preliminary(fig) -> None:
    fig.text(0.995, 0.005, "PRELIMINARY", ha="right", va="bottom",
             color=COLORS["baseline"], fontsize=7, alpha=0.8)


def save_figure(fig, stem: str, output_dir: Path = DEFAULT_OUTPUT) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = [output_dir / f"{stem}.pdf", output_dir / f"{stem}.png"]
    fig.savefig(outputs[0], bbox_inches="tight")
    fig.savefig(outputs[1], bbox_inches="tight", dpi=200)
    plt.close(fig)
    return outputs
```

- [ ] **Step 4: Implement the build CLI**

`build_all.py` parses `--allow-provisional` and `--output-dir`, imports the three chapter modules, calls each `build`, and prints one relative output path per line. It must exit non-zero on `ProvisionalDataError`.

- [ ] **Step 5: Run the common tests**

Run:

```bash
uv run --with pytest --with matplotlib pytest tests/part_3/test_visual_build.py -v
```

Expected: four tests PASS.

- [ ] **Step 6: Commit the infrastructure**

```bash
git add plots/part_3/__init__.py plots/part_3/common.py plots/part_3/build_all.py tests/part_3/test_visual_build.py
git commit -m "feat: add Part 3 plotting infrastructure"
```

---

### Task 3: Place the Complete Visual Story in `PARTIE3_INTRA.md`

**Files:**

- Modify: `research/lymphome/PARTIE3_INTRA.md`

**Interfaces:**

- Produces: fourteen numbered figure markers, nine body-table placements, and review captions that TeX integration follows.

- [ ] **Step 1: Add a structural-count regression check**

Run before editing:

```bash
rg -n '^!\[|^\*Figure\.|^\|.*\|' research/lymphome/PARTIE3_INTRA.md
```

Save the output in the task notes; it establishes which current figures and tables are being replaced.

- [ ] **Step 2: Insert the approved figure markers**

Use exact stems and place each before the paragraph that interprets it:

```markdown
![](../../plots/part_3/output/fig12_capstone.png)

*Figure 12. Avant la compétition entre champs, Qwen3.5-9B devance l'encodeur de 150 M de 3,2 points. La contrainte aide l'extracteur et dégrade le générateur ; après son application, leur différence de value-F1 est indétectable dans l'intervalle de confiance courant.*
```

For TikZ-only figures, use a descriptive marker rather than a fake raster path:

```markdown
> **Figure 1 — dossier longitudinal vers eCRF.** Frise du dossier `lym_76`; `CHOEP-14` apparaît en première puis en deuxième ligne et alimente deux champs distincts.
```

- [ ] **Step 3: Keep the nine evidence-bearing tables in place**

Ensure the Markdown contains tables for evidence limits, corpus provenance, TAPDL audit, stylometry, extractor interventions, MedEmbed/judge results, metric rules, complete capstone results, and external validation. Do not move the capstone or external tables to appendices.

- [ ] **Step 4: Remove stale visual claims**

Delete references to `fig06b_renversement` and `fig07_scaling_llm`. Replace any sentence implying that decoder structure alone makes the encoder competitive with the approved raw-gap wording.

- [ ] **Step 5: Verify numbering and coverage**

Run:

```bash
for n in $(seq 1 14); do rg -q "Figure $n[ .—]" research/lymphome/PARTIE3_INTRA.md || exit 1; done
```

Expected: exit code 0.

- [ ] **Step 6: Commit the narrative map**

```bash
git add research/lymphome/PARTIE3_INTRA.md
git commit -m "docs: map Part 3 visual narrative"
```

---

### Task 4: Build Chapter 1 TikZ Figures 1–5

**Files:**

- Create: `sources/part_3/figures/fig01_longitudinal_to_ecrf.tex`
- Create: `sources/part_3/figures/fig02_evidence_map.tex`
- Create: `sources/part_3/figures/fig03_supervision_routes.tex`
- Create: `sources/part_3/figures/fig04_wavefront.tex`
- Create: `sources/part_3/figures/fig05_tapdl.tex`
- Modify later: `sources/part_3/chapter9/article.tex`

**Interfaces:**

- Each file contains one `figure` environment with a unique `fig:p3-*` label.
- Each diagram uses thesis color tokens, not raw hex values.

- [ ] **Step 1: Create a compilation harness**

Create `/tmp/part3-figure-harness.tex` with the thesis preamble and one `\input{sources/part_3/figures/<file>}` at a time. Compile from the repository root so all style files resolve.

- [ ] **Step 2: Implement Figure 1 as a concrete worked example**

Use at most five dated document cards, one horizontal timeline, and four selected eCRF fields. Highlight the two `CHOEP-14` occurrences with the same lavender token treatment and connect them to distinct first-/second-line fields. The figure label is `fig:p3-task`.

- [ ] **Step 3: Compile and inspect Figure 1**

Run:

```bash
latexmk -pdf -interaction=nonstopmode -outdir=/tmp /tmp/part3-figure-harness.tex
pdftoppm -png -singlefile -r 180 /tmp/part3-figure-harness.pdf /tmp/fig01
```

Expected: one PDF page; no overfull box in the log; all document text legible at thesis width.

- [ ] **Step 4: Implement Figure 2 as an evidence map**

Place the inaccessible hospital target in a gray/red dashed central card. Connect synthetic eCRF, PARHAF, FrACCO, and the LLM judge with differently labeled evidence arrows. Every proxy card has a one-line “tests” and “does not establish” field. Label: `fig:p3-evidence`.

- [ ] **Step 5: Implement Figure 3 as two non-interchangeable lanes**

Upper lane: public biomedical paragraphs → LLM annotation → grounding/distillation → generalist extractor. Lower lane: PMC-Patients case → longitudinal generation → TAPDL → eCRF specialist. Join only at specialist training. Label: `fig:p3-supervision-routes`.

- [ ] **Step 6: Implement Figure 4 as four wavefront panels**

Panels: source case, structured chronology, generation at `t` with the future in a hatched gray region, assembled record. Use a real verified excerpt and label `fig:p3-wavefront`.

- [ ] **Step 7: Implement Figure 5 with audited TAPDL counters**

Flow one example through report, LLM field/string pair, exact search, fuzzy recovery, global offsets, collision resolution, and final silver span. Put 275544, 15868, 7441, 27491, and 237194 on their actual transitions. Label: `fig:p3-tapdl`.

- [ ] **Step 8: Compile all five figures and inspect them at final width**

Run the harness for each file, render each PDF to PNG, and inspect every PNG. Expected: no more than ten principal boxes per diagram, no clipped arrows, no text below 7 pt in the final thesis.

- [ ] **Step 9: Commit the five reviewed TikZ figures**

```bash
git add sources/part_3/figures/fig01_longitudinal_to_ecrf.tex sources/part_3/figures/fig02_evidence_map.tex sources/part_3/figures/fig03_supervision_routes.tex sources/part_3/figures/fig04_wavefront.tex sources/part_3/figures/fig05_tapdl.tex
git commit -m "feat: add Part 3 supervision diagrams"
```

---

### Task 5: Build Chapter 1 Stylometry Figure 6

**Files:**

- Create: `plots/part_3/plot_chapter9.py`
- Modify: `tests/part_3/test_visual_build.py`
- Modify if evidence requires: `docs/superpowers/specs/2026-07-15-partie3-visual-design.md`

**Interfaces:**

- Produces: `fig06_stylometry.pdf` and `.png`.

- [ ] **Step 1: Add the failing output test**

```python
def test_chapter9_builds_stylometry(tmp_path):
    from plots.part_3.plot_chapter9 import build
    outputs = build(tmp_path, allow_provisional=True)
    assert {path.name for path in outputs} == {
        "fig06_stylometry.pdf", "fig06_stylometry.png"
    }
```

- [ ] **Step 2: Implement raw-axis small multiples**

Read `stylometry` from `visual_data.json`. Use one horizontal dot panel per traceable metric, identical source ordering, direct numeric labels, and subtitles stating direction (`higher is closer` or `lower is closer`). Do not normalize across metrics.

- [ ] **Step 3: Apply the MMD evidence rule**

If a tracked MMD source exists, render four panels. If it does not, render MAUVE/FED/C2ST only and amend the committed design spec in the same commit to say three panels. This is an evidence correction, not a visual preference.

- [ ] **Step 4: Test and inspect**

Run:

```bash
uv run --with pytest --with matplotlib pytest tests/part_3/test_visual_build.py::test_chapter9_builds_stylometry -v
pdfinfo plots/part_3/output/fig06_stylometry.pdf
```

Expected: PASS; one-page vector PDF.

- [ ] **Step 5: Commit Figure 6 and any evidence-driven spec correction**

```bash
git add plots/part_3/plot_chapter9.py tests/part_3/test_visual_build.py docs/superpowers/specs/2026-07-15-partie3-visual-design.md
git commit -m "feat: plot Part 3 stylometric evidence"
```

---

### Task 6: Build Shared Explanatory TikZ Figures 7 and 11

**Files:**

- Create: `sources/part_3/figures/fig07_medembed.tex`
- Create: `sources/part_3/figures/fig11_metrics.tex`

**Interfaces:**

- Labels: `fig:p3-medembed` and `fig:p3-metrics`.

- [ ] **Step 1: Implement Figure 7 as lineage plus inference**

Panel A must show two inputs to MedEmbed—ModernCamemBERT-bio and OntoBook-derived terminology pairs—without implying that the OntoBook checkpoint is stacked after the CLM checkpoint. Panel B uses one actual type description, candidate spans, and similarity scores.

- [ ] **Step 2: Implement Figure 11 from one shared clinical sentence**

Reuse one sentence across four panels: one-value eCRF scoring, multi-mention NER, permissive span overlap, and token-Jaccard value matching. Include one date-format pair that is clinically equivalent but not guaranteed to satisfy the surface metric.

- [ ] **Step 3: Compile and inspect both figures**

Run each through the standalone harness. Expected: no overflow and the shared sentence remains readable at final text width.

- [ ] **Step 4: Commit**

```bash
git add sources/part_3/figures/fig07_medembed.tex sources/part_3/figures/fig11_metrics.tex
git commit -m "feat: add MedEmbed and metric diagrams"
```

---

### Task 7: Build Chapter 2 Quantitative Figures 8–10

**Files:**

- Create: `plots/part_3/plot_chapter8.py`
- Modify: `tests/part_3/test_visual_build.py`

**Interfaces:**

- Produces: `fig08_supervision_signal.*`, `fig09_novel_types.*`, `fig10_specialization_tradeoff.*`.

- [ ] **Step 1: Add exact output smoke tests**

```python
def test_chapter8_builds_three_figures(tmp_path):
    from plots.part_3.plot_chapter8 import build
    names = {p.name for p in build(tmp_path, allow_provisional=True)}
    assert names == {
        "fig08_supervision_signal.pdf", "fig08_supervision_signal.png",
        "fig09_novel_types.pdf", "fig09_novel_types.png",
        "fig10_specialization_tradeoff.pdf", "fig10_specialization_tradeoff.png",
    }
```

- [ ] **Step 2: Implement Figure 8**

Panel A uses annotation-density observations and makes the sequence empty-document rate → prediction density → recall/value score explicit. Panel B is a sorted dumbbell plot of full versus no-clinical pretraining by eCRF section. Directly label treatment sections that fall to zero; do not summarize them only through the global 0.138 versus 0.117 mean.

- [ ] **Step 3: Implement Figure 9 with a strict provisional gate**

Plot common and novel types as paired panels. If the MedEmbed A/B values are not registered, build only with `allow_provisional=True`, add the preliminary mark, and make the final loader fail. The caption must say “LLM-judge MAP”, never “accuracy”.

- [ ] **Step 4: Implement Figure 10 as a target/openness trade-off**

Use the generalist, eCRF-specialist, and mixed-specialist checkpoints. Left panel: eCRF target score. Right panel: PARHAF zero-shot score. Connect the same checkpoint across panels with consistent marker shape and direct labels.

- [ ] **Step 5: Test and inspect all three**

Run:

```bash
uv run --with pytest --with matplotlib pytest tests/part_3/test_visual_build.py::test_chapter8_builds_three_figures -v
```

Expected: PASS in preview mode. Final mode remains blocked while Figure 9 inputs are provisional.

- [ ] **Step 6: Commit**

```bash
git add plots/part_3/plot_chapter8.py tests/part_3/test_visual_build.py
git commit -m "feat: plot open-vocabulary transfer evidence"
```

---

### Task 8: Build the Core Capstone Figure 12

**Files:**

- Create: `plots/part_3/plot_chapter7.py`
- Modify: `tests/part_3/test_visual_build.py`
- Modify when verified: `research/lymphome/results.json`

**Interfaces:**

- Produces: `fig12_capstone.pdf` and `.png`.

- [ ] **Step 1: Add a result-identity test**

```python
def test_core_capstone_values_have_expected_identity():
    from plots.part_3.common import result_value
    assert result_value("ecrf", "MC-bio-gliner (v3b)", "capstone", "value") == pytest.approx(0.6467)
    assert result_value("ecrf", "Qwen3.5-9B", "capstone", "value") == pytest.approx(0.6460)
```

- [ ] **Step 2: Recompute or register raw top-1 and compete values**

Use the named 410-record parquets in `results.json` and the unified scorer. Store top-1, compete, paired bootstrap delta, and paired model difference with `_src` metadata. Do not use the old delta table in `make_partie3_figs.py`.

- [ ] **Step 3: Implement Figure 12 panel A**

Draw each model as a trajectory from `top-1` to `compete`. Keep secondary models thin and gray by family tint; emphasize the 150M encoder in dark lavender and Qwen3.5-9B in dark peach. Annotate `0.633 → 0.647`, `0.665 → 0.646`, raw gap about 0.032, and final difference about 0.001 only from the verified registry.

- [ ] **Step 4: Implement Figure 12 panel B**

Use a dot plot, not bars. Group model families spatially; show final value F1 and span F1 with different marker shapes; direct-label models. Add paired confidence intervals to the principal encoder/Qwen comparison and keep the complete numerical table in the chapter.

- [ ] **Step 5: Test and inspect**

Run:

```bash
uv run --with pytest --with matplotlib --with pandas --with pyarrow pytest tests/part_3/test_visual_build.py -k capstone -v
pdffonts plots/part_3/output/fig12_capstone.pdf
```

Expected: tests PASS; fonts embedded; no raster image object in the PDF.

- [ ] **Step 6: Commit**

```bash
git add plots/part_3/plot_chapter7.py tests/part_3/test_visual_build.py research/lymphome/results.json
git commit -m "feat: plot the Part 3 capstone comparison"
```

---

### Task 9: Build Error-Behavior Figure 13

**Files:**

- Modify: `plots/part_3/plot_chapter7.py`
- Modify: `plots/part_3/data/visual_data.json`
- Modify: `tests/part_3/test_visual_build.py`

**Interfaces:**

- Produces: `fig13_error_behavior.pdf` and `.png`.

- [ ] **Step 1: Regenerate prediction-level summaries**

Read the exact encoder and Qwen prediction parquets named by the capstone entries. Generate the role-binding error share and full risk-coverage series using the same 410 records and metric configuration. Store the resulting curve arrays with source parquet, scoring command, and record count in `visual_data.json`; change their status to `registered` only after the regenerated headline values match 0.405/0.605 and 0.228/0.313 within 0.001.

- [ ] **Step 2: Implement the two panels**

Panel A compares “correct value, wrong field” shares with direct percentages. Panel B plots risk against coverage for both models, annotates AURC, and marks precision at 50 percent coverage. The caption notes that Qwen confidence is measured under guided JSON decoding.

- [ ] **Step 3: Add and run the smoke test**

```python
def test_error_behavior_builds(tmp_path):
    from plots.part_3.plot_chapter7 import build_error_behavior
    assert {p.suffix for p in build_error_behavior(tmp_path, False)} == {".pdf", ".png"}
```

Run with pandas and pyarrow. Expected: PASS in final mode only after both analyses are registered.

- [ ] **Step 4: Commit**

```bash
git add plots/part_3/plot_chapter7.py plots/part_3/data/visual_data.json tests/part_3/test_visual_build.py
git commit -m "feat: plot capstone error behavior"
```

---

### Task 10: Build Adaptation and External-Scope Figure 14

**Files:**

- Modify: `plots/part_3/plot_chapter7.py`
- Modify: `tests/part_3/test_visual_build.py`

**Interfaces:**

- Produces: `fig14_adaptation_scope.pdf` and `.png`.

- [ ] **Step 1: Implement the eCRF learning curve**

Use the five registered points from `visual_data.json`, an actual logarithmic x-axis, direct point labels, and a thin horizontal Qwen3.5-9B final reference. Label the reference by model and value, not by promotional parameter-ratio wording.

- [ ] **Step 2: Implement PARHAF and FrACCO adaptation panels**

Read zero-shot and 100-document fine-tuned values from `results.json`. Draw a connected trajectory only when both endpoints exist. Show `n=31` on PARHAF. Keep `gliner-biomed` visible on FrACCO so the 0.867 result defines the method's scope.

- [ ] **Step 3: Add the output test and run it**

```python
def test_adaptation_scope_builds(tmp_path):
    from plots.part_3.plot_chapter7 import build_adaptation_scope
    names = {p.name for p in build_adaptation_scope(tmp_path, True)}
    assert names == {"fig14_adaptation_scope.pdf", "fig14_adaptation_scope.png"}
```

Expected: PASS; the three panels share family colors but not necessarily identical y limits if the caption makes the scales explicit.

- [ ] **Step 4: Commit**

```bash
git add plots/part_3/plot_chapter7.py tests/part_3/test_visual_build.py
git commit -m "feat: plot adaptation efficiency and scope"
```

---

### Task 11: Integrate Figures and Tables into the Three TeX Chapters

**Files:**

- Modify: `sources/part_3/chapter9/article.tex`
- Modify: `sources/part_3/chapter8/article.tex`
- Modify: `sources/part_3/chapter7/article.tex`
- Modify: `sources/appendix.tex`

**Interfaces:**

- Chapter 9 consumes Figures 1–6.
- Chapter 8 consumes Figures 7–10.
- Chapter 7 consumes Figures 11–14.

- [ ] **Step 1: Audit existing dirty changes before editing**

Run:

```bash
git diff -- sources/part_3/chapter7/article.tex sources/part_3/chapter8/article.tex sources/part_3/chapter9/article.tex
```

Preserve every unrelated user edit. Apply changes with targeted patches only.

- [ ] **Step 2: Integrate Chapter 9 visuals and four tables**

Input Figures 1–5 at the approved narrative locations and include `plots/part_3/output/fig06_stylometry.pdf`. Add or retain provenance, TAPDL audit, and stylometry tables using `booktabs`, `siunitx`, no vertical rules, and exact sample sizes.

- [ ] **Step 3: Integrate Chapter 8 visuals and two tables**

Input Figure 7 and include Figures 8–10. Retain the interventions table and the complete MedEmbed/novel-type result table. Put judge limitations in the caption and main text, not a footnote alone.

- [ ] **Step 4: Integrate Chapter 7 visuals and three tables**

Input Figure 11 and include Figures 12–14. Retain metric definitions, complete capstone results, and a two-block PARHAF/FrACCO table. Place the Figure 12 caption and paragraph so the 0.032 raw gap precedes the decoder interpretation.

- [ ] **Step 5: Route reproducibility material to the appendix**

Keep headline setup facts in the chapters, but place the complete model-family hyperparameters, full generation/TAPDL/judge prompts, 89-field dictionary, run identifiers, threshold sweeps, bootstrap distributions, and exhaustive per-field matrices in `sources/appendix.tex`. Reuse the existing `app:gliner-prompts` section rather than duplicating it.

- [ ] **Step 6: Verify labels and references**

Use these exact figure labels:

```text
fig:p3-task
fig:p3-evidence
fig:p3-supervision-routes
fig:p3-wavefront
fig:p3-tapdl
fig:p3-stylometry
fig:p3-medembed
fig:p3-supervision-signal
fig:p3-novel-types
fig:p3-specialization
fig:p3-metrics
fig:p3-capstone
fig:p3-error-behavior
fig:p3-adaptation-scope
```

Use these exact table labels:

```text
tab:p3-evidence
tab:p3-corpus
tab:p3-tapdl
tab:p3-stylometry
tab:p3-interventions
tab:p3-medembed
tab:p3-metrics
tab:p3-capstone
tab:p3-external
```

Run:

```bash
rg -o '\\label\{fig:p3-[^}]+' sources/part_3 | sort
rg -o '\\label\{tab:p3-[^}]+' sources/part_3 | sort
```

Expected: fourteen unique figure labels and nine unique table labels.

- [ ] **Step 7: Commit chapter and appendix integration without staging other files**

```bash
git add sources/part_3/chapter9/article.tex sources/part_3/chapter8/article.tex sources/part_3/chapter7/article.tex sources/appendix.tex
git commit -m "docs: integrate Part 3 visual evidence"
```

---

### Task 12: Retire Legacy Assets and Perform End-to-End Verification

**Files:**

- Delete after comparison: `research/lymphome/make_partie3_figs.py`
- Delete or archive after comparison: superseded `research/lymphome/partie3_figs/fig03*`, `fig04*`, `fig05*`, `fig06*`, `fig06b*`, `fig07*`, `fig08*`
- Verify: `thesis.pdf`

**Interfaces:**

- Produces: a clean final Part 3 build with fourteen figures and nine body tables.

- [ ] **Step 1: Run the final data gate without provisional allowance**

```bash
uv run --with matplotlib --with pandas --with pyarrow python -m plots.part_3.build_all
```

Expected: success and fourteen plot files (seven PDF plus seven PNG). If it raises `ProvisionalDataError`, do not weaken the gate; resolve the named evidence source.

- [ ] **Step 2: Run the complete test suite**

```bash
uv run --with pytest --with matplotlib --with pandas --with pyarrow pytest tests/part_3 -v
```

Expected: all tests PASS.

- [ ] **Step 3: Build the thesis**

```bash
latexmk -pdf -interaction=nonstopmode thesis.tex
```

Expected: exit code 0 and an updated `thesis.pdf`.

- [ ] **Step 4: Check LaTeX warnings and structural counts**

```bash
rg -n 'Overfull|Undefined reference|multiply defined|LaTeX Warning' thesis.log
```

Expected: no Part 3 overfull boxes, undefined references, or duplicate labels.

- [ ] **Step 5: Render and inspect every Part 3 page**

Use `pdftotext -layout` to identify Part 3 page numbers, render them with `pdftoppm -r 160`, and inspect each image. Check text size, color semantics, captions, float order, blank space, and table width.

- [ ] **Step 6: Compare new and legacy assets before deletion**

Confirm every legacy figure's narrative role is covered by Figures 8, 10, 12, or 14. Then remove only the superseded files; keep no stale Markdown references.

- [ ] **Step 7: Run final reference scans**

```bash
rg -n 'partie3_figs|fig06b_renversement|fig07_scaling_llm|DASH' research/lymphome/PARTIE3_INTRA.md sources/part_3 plots/part_3
```

Expected: no matches except an explicit historical note in the design/plan documents.

- [ ] **Step 8: Commit final cleanup and verified PDF separately**

```bash
git add research/lymphome/make_partie3_figs.py research/lymphome/partie3_figs research/lymphome/PARTIE3_INTRA.md sources/part_3 plots/part_3 tests/part_3
git commit -m "refactor: retire legacy Part 3 figures"
```

If the repository policy tracks `thesis.pdf`, stage it alone in a final commit after confirming that no unrelated generated files enter the diff.

---

## Final Review Checklist

- [ ] Fourteen figure numbers appear once in the narrative and once in TeX.
- [ ] Nine evidence-bearing tables remain in the body.
- [ ] The final plot command succeeds without `--allow-provisional`.
- [ ] Figure 12 leads with the modest 0.032 raw gap, not a decoder-hype claim.
- [ ] Figure 13 states Qwen's calibration and role-binding advantages.
- [ ] Figure 14 shows the FrACCO limitation prominently.
- [ ] No result comes only from `/tmp/dashboard.md` or `PARTIE3_NARRATIF_v2.md`.
- [ ] Lavender/peach meanings never reverse.
- [ ] All quantitative PDFs contain vector text and embedded fonts.
- [ ] Every TikZ example is traceable to a verified synthetic or public-text example.
- [ ] No Part 3 page has an overfull element or unreadable label at normal zoom.
