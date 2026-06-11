"""
forgetting.py — Catastrophic forgetting: source-domain validation loss vs. replay rate.

DATA SOURCE — verbatim from published table:
  Ibrahim et al. (2024) "Simple and Scalable Strategies to Continually Pre-train
  Large Language Models." TMLR 06/2024. arXiv:2403.08763.
  Table 2: "Final loss of English-only 405M parameter models trained with varying
  amounts of replay." — D0 (Pile) validation loss column, 405M model.

  Weak shift  (English Pile → English SlimPajama):
    baseline (Pile only):            D0 = 2.17
    no replay:                       D0 = 2.44
    0.5% replay:                     D0 = 2.27
    1%   replay:                     D0 = 2.26
    5%   replay:                     D0 = 2.23
    10%  replay:                     D0 = 2.21
    50%  replay:                     D0 = 2.16
    joint training (upper bound):    D0 = 2.17

  Strong shift (English Pile → German):
    baseline (Pile only):            D0 = 2.17  (same model)
    no replay:                       D0 = 3.56
    1%   replay:                     D0 = 2.83
    5%   replay:                     D0 = 2.57
    10%  replay:                     D0 = 2.46
    25%  replay:                     D0 = 2.33
    50%  replay:                     D0 = 2.24
    joint training (upper bound):    D0 = 2.26

Nothing is digitised from a figure.  All numbers are copied from Table 2 of the
paper exactly as printed.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from thesis_style import COLORS, apply_style
apply_style()

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# ── verbatim data from Table 2, Ibrahim et al. 2024 ──────────────────────────

# Replay rates shared by both conditions (use as x ticks; 0 = no replay)
# We plot against a numeric x-axis: 0, 0.5, 1, 5, 10, 25, 50 (%)
# Only weak shift has 0.5% and lacks 25%; strong shift has 25% and lacks 0.5%.
# Plot them as separate series with their own x-values.

weak_x   = [0,    0.5,  1,    5,    10,   50  ]
weak_d0  = [2.44, 2.27, 2.26, 2.23, 2.21, 2.16]

strong_x  = [0,    1,    5,    10,   25,   50  ]
strong_d0 = [3.56, 2.83, 2.57, 2.46, 2.33, 2.24]

baseline_d0 = 2.17   # source-only (Pile only) — same for both conditions
weak_joint  = 2.17   # joint-training upper bound, weak shift
strong_joint = 2.26  # joint-training upper bound, strong shift

# ── figure ───────────────────────────────────────────────────────────────────

fig, ax = plt.subplots(figsize=(5.6, 3.5))

ax.plot(weak_x, weak_d0,
        color=COLORS["primary_dark"], lw=1.7, marker="o", ms=4.5,
        label=r"weak shift (En$\to$En)")

ax.plot(strong_x, strong_d0,
        color=COLORS["secondary_dark"], lw=1.7, marker="s", ms=4.5,
        label=r"strong shift (En$\to$De)")

# Baseline: source-only loss (horizontal dashed) — labelled in the legend
ax.axhline(baseline_d0, color=COLORS["neutral"], lw=1.1, ls="--", zorder=1,
           label="source-only baseline")

# Joint-training upper bounds (small horizontal ticks at x=50, right edge)
ax.plot([50], [weak_joint],   marker="_", ms=10, lw=0,
        color=COLORS["primary_dark"], zorder=5)
ax.plot([50], [strong_joint], marker="_", ms=10, lw=0,
        color=COLORS["secondary_dark"], zorder=5)

ax.set_xscale("symlog", linthresh=0.4)
ax.set_xticks([0, 0.5, 1, 5, 10, 25, 50])
ax.set_xticklabels(["0", "0.5", "1", "5", "10", "25", "50"])

ax.set_xlabel(r"replay rate (\%\ of source data mixed in)")
ax.set_ylabel(r"source-domain val.\ loss $\downarrow$")

ax.tick_params(length=3)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

ax.legend(frameon=False, fontsize=9, loc="upper right")

fig.tight_layout()

out = os.path.join(os.path.dirname(__file__), "forgetting.pdf")
fig.savefig(out, bbox_inches="tight")
print(f"Saved to {out}")
