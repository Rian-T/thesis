# Task 8 report — Figure 12 capstone

## Status

Implemented the two-panel English Figure 12 preview as
`fig12_capstone.{pdf,png}`. Final mode rejects the provisional inputs before
creating outputs. No `.tex` file was modified by this task.

## Exact evidence

- Gold: 410 documents, SHA-256
  `f65ee070c2f70e7e213b9b6084963d5ec4b57547a3dbaffe4117a468251951aa`.
- Canonical scorer SHA-256:
  `863058884a52f23c84704d6883745dd5c2e0d73f749169fca1743bf404a4d836`.
- Encoder parquet SHA-256:
  `19aaffad4a29af7758103c7dc961a9f7e239331d8fc1542ab1d4514cbdb04826`.
- Current Qwen `de1540v2` parquet SHA-256:
  `832e372990467c385b3db58d869ea12072938f6567ca8ddb334eeba8a80e83c2`.
- Encoder top-1/final value-F1:
  `0.6331050981187579 / 0.6466740725330404`; final span-F1
  `0.5074821907707991`.
- Qwen top-1/final value-F1:
  `0.6650600379463285 / 0.646012893119297`; final span-F1
  `0.5540968171691303`.
- Raw Qwen-minus-encoder gap: `0.0319549398275706`; final
  encoder-minus-Qwen gap: `0.0006611794137434`.
- Final exact scores agree with `results.json` only at its four-decimal
  precision, by unique display/regime identity.
- Paired manuscript interval shown only in preview and explicitly marked
  provisional: encoder-minus-Qwen `+0.0007 [-0.0068, 0.0084]`.

## Changed files

- `plots/part_3/plot_chapter7.py`
- `plots/part_3/data/chapter7/derive_capstone.py`
- `plots/part_3/data/chapter7/capstone_410doc.json`
- `plots/part_3/data/visual_data.json`
- `plots/part_3/data/README.md`
- `tests/part_3/test_visual_build.py`
- `tests/part_3/test_visual_data.py`
- `.superpowers/sdd/task-8-report.md`

Generated review artifacts (not for commit):
`plots/part_3/output/fig12_capstone.pdf` and `.png`.

## Commands and results

- Focused derivation through direct cached Python 3.12: exit 0; regenerated
  JSON byte-identical to the tracked artifact, SHA-256
  `9afb42c7d312896bcbab8ad27b8479c00e718ec3c36deb9165a7b93fc7a53956`.
- `test_visual_data.py`: `12 passed in 0.33s`.
- Figure 12 build subset: `4 passed, 25 deselected in 16.07s`.
- Final-mode direct check: `ProvisionalDataError`; output directory remained
  empty.
- Full `test_visual_build.py` and combined Part 3 invocations printed 19 and
  17 passing progress dots respectively, then the execution harness closed
  without a pytest summary despite reporting exit 0. These are not counted as
  complete-suite proof; the direct focused and data suites above are the
  reliable test evidence.
- `git diff --check`: exit 0.
- `pdfinfo`: one page, `405.42 x 229.902 pt`, 39,711 bytes.
- `pdffonts`: embedded subset `URWPalladioL-Roma`, `PazoMath`, and `CMSY10`.
- `pdfimages -list`: no raster images in the vector PDF.
- `pdftotext`: all English titles, labels, raw gap, provisional paired CI,
  and `PRELIMINARY` extracted.

## Render inspection

- Native Matplotlib figure width: exactly `5.5 in`; minimum effective visible
  text in the figure object: at least `7 pt` (automated test).
- Tight PDF page: `5.631 x 3.193 in` (`405.42 x 229.902 pt`).
- 180-dpi PNG: `1013 x 574 px`; PDF rendered at 180 dpi: `1014 x 575 px`.
- Original PNG and PDF-to-PNG render were inspected at original resolution.
  Opposite trajectory slopes, raw gap ordering, near-zero final value-F1
  difference, distinct circle/diamond markers, provisional CI, and watermark
  are visible. No code/run identifier appears in the figure.

## Self-review and concerns

The raw Qwen advantage is stated before the decoding result, so the graphic
does not imply that structural decoding creates encoder competitiveness. The
paired intervals remain provisional and no individual-score CI is fabricated.
The scientific concern is unchanged: the paired deltas/CIs have not been
regenerated from primary prediction artifacts, and `results.json` itself is
currently labelled provisional. Therefore only preview output is valid.

Operational concern: the shared offline uv wrapper intermittently returned
without executing or without a pytest summary. Direct cached Python 3.12 runs
provided reproducible focused evidence, but a clean uninterrupted full Part 3
suite should be rerun by the integrator.
