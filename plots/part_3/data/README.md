# Part 3 visual data

`research/lymphome/results.json` remains the primary metric registry.
`visual_data.json` is an audit supplement for figures, not a competing source of
truth. Here, `registered` means the value is backed by that registry or by a
repository-tracked primary artifact. `provisional` means the value is useful for
a review render but is barred from final thesis claims.

Final plots are built without `--allow-provisional`. Preview plots may be built
with that flag and must display `PRELIMINARY` in the lower-right margin.

## Observation schema

Every numeric observation has the same five fields:

- `value`: the plotted numeric value;
- `status`: exactly `registered` or `provisional`;
- `source`: a repository-tracked provenance record;
- `n`: the evaluation sample size when known, otherwise `null`;
- `note`: the metric definition, derivation, or remaining evidence gap.

The five data-efficiency observations are dashboard-transcribed rounded
value-micro-F1 scores recorded in `research/lymphome/07_RESULTATS.md:198-202`.
They remain `provisional` until each point is explicitly rescored and registered
in `results.json`. The generic root invocation of `score_unified.py` is not a
reproduction recipe for these exact points, and the older `-de*.parquet` files
are not asserted to be their 410-record evaluation source.

Calibration values are the 410-document AURC and precision-at-50-percent-
coverage results registered in `research/lymphome/02_CHIFFRES_CANONIQUES.md`.
Role-binding shares remain provisional until their prediction-level
regeneration is recorded. Decoding deltas and paired bootstrap intervals remain
provisional until they are registered in `research/lymphome/results.json`.

## Stylometry primary artifacts

The complete Jean Zay scoring provenance is tracked under `stylometry/`:

- `sota_dist_test.py`: exact scoring script, including `N = 1000`;
- `sota_style_jz.sbatch`: exact Slurm submission script;
- `styleSOTA_1819572.out`: exact primary output for job 1819572.

The primary output registers MAUVE, FED, MMD squared, and C2ST for PMC patients,
the synthetic clinical corpus, and E3C. Figure 6 therefore has four panels—one
per metric—with no inferred values.

The script and log call PARHAF a real hospital reference. That terminology is
incorrect: PARHAF is human-written fictitious clinical text, not a real
hospital-record corpus. The manifest notes preserve this correction while the
provenance files remain exact copies of the remote originals.
