"""
quality_ablation_flat.py — appendix figure for the pre-detour negative result.

Each point is one quality-signal document filter applied before the CLM decay,
scored on FrACCO ICD-coding (top-100, micro-F1, mean +/- std over 3 seeds). The
band is the spread of the points: every filter lands inside it, so filtering by a
quality signal does not move downstream coding. Data read from the run JSONs in
~/dev/colm/ModernBERT/outputs/quality-ablation/.

Run:
  uv run --with matplotlib python plots/appendix/quality_ablation_flat.py
"""
import glob
import json
import os
import sys

import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from thesis_style import COLORS, apply_style

SRC = os.path.expanduser("~/dev/colm/ModernBERT/outputs/quality-ablation")
LABELS = {
    "synth20": "added synthetic", "writ7": "writing quality", "cont7": "content richness",
    "only": "single source", "edu7": "educational", "term7": "terminology",
    "fw15": "structure", "ct-filter": "content type",
}

rows = []
for f in glob.glob(os.path.join(SRC, "decay-clm-mc-bio-*-1B.json")):
    var = os.path.basename(f)[len("decay-clm-mc-bio-"):-len("-1B.json")]
    ag = json.load(open(f))["aggregated"]["eval"]["multilabel"]
    node = ag["fracco_icd_doc_top100"][f"decay-clm-mc-bio-{var}-1B"]
    rows.append((LABELS.get(var, var),
                 node["metrics_mean"]["f1_micro"] * 100,
                 node["metrics_std"]["f1_micro"] * 100))
rows.sort(key=lambda r: r[1])
labels, means, stds = zip(*rows)
y = range(len(rows))

apply_style()
fig, ax = plt.subplots(figsize=(5.4, 3.0))
lo = min(m - s for m, s in zip(means, stds))
hi = max(m + s for m, s in zip(means, stds))
ax.axvspan(lo, hi, color=COLORS["neutral"], alpha=0.12, zorder=0)
ax.errorbar(means, list(y), xerr=stds, fmt="o", color=COLORS["primary_dark"],
            ecolor=COLORS["neutral"], elinewidth=1, capsize=2.5, markersize=4, zorder=3)
ax.set_yticks(list(y))
ax.set_yticklabels(labels)
ax.set_xlabel("FrACCO top-100 micro-F1")
ax.set_title("Quality-signal document filters (3 seeds)", fontsize=9)
ax.margins(y=0.08)

fig.tight_layout()
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "quality_ablation_flat.pdf")
fig.savefig(out, bbox_inches="tight")
print(f"wrote {out}; spread = {hi-lo:.2f} pp")
