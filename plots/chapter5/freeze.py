"""
freeze.py — Chapter 5 freeze-intervention figure (dot plot, not bars: the
differences are small, so a zero-based bar chart would hide them).

Downstream average F1 (French Base, 8 tasks, 9 seeds) for the freeze interventions,
against the MLM baseline and the full CLM detour. Freezing low layers during the
CLM phase drops the model back to the MLM baseline; freezing mid layers, or
freezing low layers during the decay, preserves the gain. Numbers from tab:freeze.

Run: uv run --with matplotlib python plots/chapter5/freeze.py
"""
import os, sys
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from thesis_style import COLORS, apply_style

# (label, F1) sorted ascending for the dot plot
rows = [
    ("MLM baseline",            57.9),
    ("freeze L0–7 (CLM)",  58.4),
    ("freeze L0–7 (decay)",60.3),
    ("freeze L8–14 (CLM)", 60.3),
    ("CLM detour",              60.8),
]
MLM, CLM = 57.9, 60.8

apply_style()
fig, ax = plt.subplots(figsize=(5.6, 2.7))
ys = range(len(rows))
# reference lines: MLM (gray) and CLM (accent)
ax.axvline(MLM, color=COLORS["neutral"], lw=1.0, ls=":", zorder=1)
ax.axvline(CLM, color=COLORS["primary_dark"], lw=1.0, ls=":", zorder=1)
ax.text(MLM, len(rows)-0.4, "MLM", color=COLORS["neutral"], fontsize=7.5, ha="center", va="bottom")
ax.text(CLM, len(rows)-0.4, "CLM", color=COLORS["primary_dark"], fontsize=7.5, ha="center", va="bottom")
for y, (lab, v) in zip(ys, rows):
    keeps = v >= (MLM + CLM) / 2
    c = COLORS["primary_dark"] if keeps else COLORS["neutral"]
    ax.plot([v], [y], "o", color=c, markersize=7, zorder=3)
    ax.annotate(f"{v:.1f}", (v, y), xytext=(8, 0), textcoords="offset points",
                va="center", fontsize=8, color=COLORS["ink"])
ax.set_yticks(list(ys)); ax.set_yticklabels([r[0] for r in rows])
ax.set_ylim(-0.5, len(rows)-0.1)
ax.set_xlim(57.3, 61.4)
ax.set_xlabel(r"downstream average $F_1$ (\%)")

fig.tight_layout()
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "freeze.pdf")
fig.savefig(out, bbox_inches="tight")
print("wrote", out)
