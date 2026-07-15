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

## Chapter 7 capstone

Figure 12 uses `chapter7/capstone_410doc.json`, reproduced by
`chapter7/derive_capstone.py` from the exact current encoder and
`Qwen3.5-9B-de1540v2` parquets plus `v5_test.jsonl`. The script imports the
canonical `score_unified.py` functions, records input hashes and cross-fit
thresholds, and checks final points by exact display/regime identity against
`results.json`. Reproduce it with:

```bash
PYTHONPATH=. uv run --offline --python 3.12 --with pandas --with pyarrow \
  python plots/part_3/data/chapter7/derive_capstone.py
```

The exact final span/value scores agree with the primary registry only at its
four-decimal precision. The derived observations remain `provisional` because
the registry lacks full-precision raw top-1 points and currently declares its
results provisional. Existing paired intervals are manuscript leads, not
prediction-artifact regenerations. Preview Figure 12 is therefore watermarked
and final mode fails atomically.

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

## Chapter 8 quantitative audit

All three Chapter 8 figures remain provisional because at least one principal
endpoint is absent from `research/lymphome/results.json`. Preview renders are
therefore watermarked; final mode rejects the chapter before creating any
output. The chapter records live under `chapter8/` and are consumed through
`visual_data.json`, while values already in `results.json` continue to be loaded
from that primary registry rather than duplicated here.

### Figure 8 — 200-document supervision intervention

The historical `scores_unified_410.json` output evaluates the three `ab20`
prediction files, which cover 200 documents, against all 410 gold documents.
Its global `0.1383/0.1169/0.1102` values therefore include 210 documents for
which these interventions have no predictions and are not used in Figure 8.

`derive_ablation.py` imports the canonical top-1, scoring, and cross-fit
functions from `research/lymphome/score_unified.py`, intersects the three
prediction supports exactly, and reports value-micro-F1 on those 200 documents.
Section scores use each model's global cross-fit threshold on the corresponding
report fold; no section-specific retuning is used. Reproduce the tracked
machine-readable output with:

```bash
PYTHONPATH=. uv run --with pandas --with pyarrow \
  python plots/part_3/data/chapter8/derive_ablation.py \
  > plots/part_3/data/chapter8/ablation_200doc.json
```

Input SHA-256 values embedded in the output are:

- scorer `score_unified.py`: `863058884a52f23c84704d6883745dd5c2e0d73f749169fca1743bf404a4d836`;
- gold `v5_test.jsonl`: `f65ee070c2f70e7e213b9b6084963d5ec4b57547a3dbaffe4117a468251951aa`;
- FULL predictions: `1479c141cbe3f407c91f24aeea57d91c4d8ca844b8adfa81ffa69d4a9f1727b3`;
- no-clinical predictions: `f3e9abd71c29c6ac6d6cdc5de72e199262dd60242d9d2173f4e84ce73a00c4b5`;
- biomedical-matched predictions: `0d45f3262e17cd0eff975ba8e6379869bcc114d3e544dd6f678f0e0e7170ab07`.

The resulting global scores are FULL `0.2051978`, no-clinical `0.1826377`,
and biomedical-matched `0.1700135`. The section panel deliberately replaces
the stale dashboard transcription with this reproducible rule. It does not
invent empty-document rates, prediction density, or recall. The three treatment
sections—first line, other lines, and second line—have zero no-clinical
value-F1; the separate latest-news section also has zero but is not described
as a treatment section.

### Figure 9 — current judge report

`judge_eval_report.md` was read from the current scoring location
`/lustre/fsn1/projects/rech/rua/uvb79kr/onto/medembed-outputs/judge_eval/report.md`
on Jean Zay (mtime `2026-07-14 10:43`). Its source SHA-256 is
`b4a9adb3207d26a1ac2a99f2caa0cf779782f6ffd93136208bd6194f091d3a41`.
The repository copy has a single conventional trailing LF added by the patch
workflow, so its tracked-file SHA-256 is
`f72aa67573117008488f12d3287fd7b708a1b4d987d7b8a5aec4fbcb901d2ecd`;
the textual report content is otherwise unchanged.

The report derivation and copy are distinct operations. The documented scoring
entry point is executed in the remote repository and consumes the current
`pool.jsonl`, `verdicts.jsonl`, and every `preds_<model>.parquet` under the
judge-eval base directory:

```bash
# Derive/refresh the report on Jean Zay.
ssh jeanzay 'cd "$WORK/french-medgliner" && \
  uv run python gen/judge_eval/score.py'

# Copy the already-derived primary report, then normalize one final LF exactly
# as stored in the repository.
ssh jeanzay 'cat /lustre/fsn1/projects/rech/rua/uvb79kr/onto/medembed-outputs/judge_eval/report.md' \
  > /tmp/judge_eval_report.md
python3 -c 'from pathlib import Path; s=Path("/tmp/judge_eval_report.md").read_text(); Path("plots/part_3/data/chapter8/judge_eval_report.md").write_text(s.rstrip("\n")+"\n")'
```

The scorer's configured input base is
`/lustre/fsn1/projects/rech/rua/uvb79kr/onto/medembed-outputs/judge_eval/`;
the relevant inputs are its `pool.jsonl`, `verdicts.jsonl`, and model prediction
parquets. The tracked report is a copy of the scorer output, not a local
re-derivation.

The exact A/B inputs are MedEmbed `0.517/0.382` and MC-bio `0.478/0.333`
for common/novel LLM-judge MAP, with 1,496 common and 682 novel queries.
The report also records judge honeypot performance `192/197 = 0.975`. Figure 9
calls the plotted metric `LLM-judge MAP`, never accuracy, and remains
provisional because it is not registered in `results.json` and is not human
medical gold.

### Figure 10 — independent checkpoint endpoints

The local source paths are
`research/lymphome/scores_parhaf_bio_dev.json` and
`research/lymphome/scores_unified_410.json`. The former is the current corrected
multi-mention NER scorer output on the 31-document PARHAF development split. Its
source SHA-256 is
`860b757740b01381182f5fdc716c101447bb144b4fc9c51c1e83d97371b74bb1`;
the tracked copy differs only by a final LF and hashes to
`f0f805e7c8585fc8f8434435930a559eaa39323b17c23b9e3d8181331ff991ee`.
The analogous tracked copy of `scores_unified_410.json` hashes to
`dd003417b204155454372a502078caad8c79db879176c81f248be40497f555ed`
(source without final LF:
`c5bdc31d3267e3c84169231ec273c0ca7c1ced44abc2b7fab9c3515e1eeba54f`).

Generation and copying are separate:

```bash
# Derive the 31-document corrected PARHAF NER output.
(cd research/lymphome && \
  uv run --with pandas --with pyarrow \
    python score_unified.py --bench bio --subset dev)

# Derive the 410-document eCRF output.
(cd research/lymphome && \
  uv run --with pandas --with pyarrow \
    python score_unified.py --bench lymphome)

# From the repository root, copy and normalize the two JSON outputs exactly as
# stored in the repository (2-space indentation and one final LF).
python3 -m json.tool --indent 2 \
  research/lymphome/scores_parhaf_bio_dev.json \
  plots/part_3/data/chapter8/scores_parhaf_bio_dev.json
python3 -m json.tool --indent 2 \
  research/lymphome/scores_unified_410.json \
  plots/part_3/data/chapter8/scores_unified_410.json
```

Both derivations use `research/lymphome/score_unified.py` (SHA-256
`863058884a52f23c84704d6883745dd5c2e0d73f749169fca1743bf404a4d836`).
The relevant eCRF inputs are `data/v5_test.jsonl` (SHA-256
`f65ee070c2f70e7e213b9b6084963d5ec4b57547a3dbaffe4117a468251951aa`),
`data/preds_lym_v3e.parquet` (`c5e47817596fb47ddb5d7709c1d1174c325085315f37bd901fdd919e1b40fe15`),
`data/preds_lym_lym-V5FROMV3B-v3b410.parquet`
(`19aaffad4a29af7758103c7dc961a9f7e239331d8fc1542ab1d4514cbdb04826`),
and `data/preds_lym_lym-V5MIX6-mix6410.parquet`
(`d939b2ad8d04717db94f84c46ea991e94252f96b80bd59555cbe0f4a158dee98`).

The relevant PARHAF inputs are `data/parhaf/parhaf_bio_all.jsonl`
(`155e4f44bc5c648db4b1bdaeeef9260d8e5cbb9af3bad5319e98d4b243d99720`),
the dev split `parhaf_bio_dev.jsonl`
(`1fb3ef906cce49e6f18f60783e20c6296fd1db7b5e9a97d09ce60b7ddfaa3349`),
and four prediction parquets:

- `v3b-pristine`: `8f80301d8026c1bb0c1edd0f521ef6b38c539b4e840ebd7e37b7a7c323eb3b2e`;
- `v3e`: `41e1cbd7e6a84b8bcb82ca64ac6c7f96c290cccadf337bb763da7172fc9b730a`;
- `lym-V5FROMV3B`: `c57e37dd924096ab08fde89dd367fd92dc90a85ccec577b71413bf2d58203fcc`;
- `lym-V5MIX6`: `dcb142adbd6f32485c5bf580b64d94ef17dfb9a6c833bd5512d62a312905bc2c`.

No repository-tracked config, trainer state, job log, checkpoint path, or hash
was found that proves a v3b→V5FROMV3B or v3e→MIX6 ancestry. A follow-up remote
crosswalk audit was unavailable when SSH escalation reached its usage limit.
Filenames and scorer aliases are insufficient evidence. Figure 10 therefore
shows four independent checkpoint endpoints with no line, arrow, or lineage
claim:

- `v3b` generalist: eCRF/PARHAF `0.2241/0.2577`;
- `FROMV3B` specialist: eCRF/PARHAF `0.6467/0.0179`;
- `v3e` generalist: eCRF/PARHAF `0.1832/0.1598`;
- `MIX6` specialist: eCRF/PARHAF `0.6574/0.1531`.

The registered eCRF endpoints and registered generalist PARHAF values are read
directly from `results.json`. Only the missing v3e eCRF and specialized PARHAF
endpoints are kept in the supplement. These current NER values supersede the
old top-1 dashboard leads. The comparison is descriptive only; it does not
assert checkpoint ancestry or a causal protection effect from mixing.
