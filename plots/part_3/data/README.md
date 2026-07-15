# Part 3 visual data

`registered` means the value is backed by `results.json`, a tracked score JSON,
or a named prediction parquet plus a reproducible command. `provisional` means
the value is useful for a review render but is barred from final thesis claims.

Final plots are built without `--allow-provisional`. Preview plots may be built
with that flag and must display `PRELIMINARY` in the lower-right margin.

## Observation schema

Every numeric observation has the same five fields:

- `value`: the plotted numeric value;
- `status`: exactly `registered` or `provisional`;
- `source`: a repository-tracked provenance record;
- `n`: the evaluation sample size when known, otherwise `null`;
- `note`: the metric definition, derivation, or remaining evidence gap.

The data-efficiency observations are the rounded value-micro-F1 scores recorded
in `research/lymphome/07_RESULTATS.md:198-202`. Their named prediction parquets
are recorded with each observation and can be rescored with:

```bash
uv run python research/lymphome/score_unified.py
```

Calibration values are the 410-document AURC and precision-at-50-percent-
coverage results registered in `research/lymphome/02_CHIFFRES_CANONIQUES.md`.
Role-binding shares remain provisional until their prediction-level
regeneration is recorded. Decoding deltas and paired bootstrap intervals remain
provisional until they are registered in `research/lymphome/results.json`.

## Stylometry and MMD

The MAUVE, FED, and C2ST values currently have only the tracked transcription in
`research/lymphome/PARTIE3_INTRA.md`; they therefore remain provisional. The
original `styleSOTA_1819572.out` and no reproducible MMD script/output pair were
found in the repository. MMD is intentionally absent from the manifest and must
not be inferred from MAUVE, FED, or C2ST. Figure 6 must use the three available
panels unless a repository-tracked primary MMD record is added.
