"""
needle.py — Chapter 5 needle-in-a-haystack figure.

Binary retrieval accuracy of the CLM-detour vs the MLM-only model on a synthetic
French needle-in-a-haystack task, by context length and by needle position. The
detour helps at every length and position. Data verbatim from the run outputs.

Run: uv run --with matplotlib python plots/chapter5/needle.py
"""
import json, os, sys
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from thesis_style import COLORS, apply_style

HERE = os.path.dirname(os.path.abspath(__file__))
clm = json.load(open(os.path.join(HERE, "data", "needle_clm.json")))["test_metrics"]
mlm = json.load(open(os.path.join(HERE, "data", "needle_mlm.json")))["test_metrics"]

apply_style()
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 2.9))

# (a) by context length
lens = [512, 1024, 2048, 4096, 8192]
cl = [clm["by_length"][str(L)]["accuracy"] * 100 for L in lens]
ml = [mlm["by_length"][str(L)]["accuracy"] * 100 for L in lens]
ax1.plot(lens, cl, color=COLORS["primary_dark"], lw=1.7, marker="o", markersize=3.5, label="CLM detour")
ax1.plot(lens, ml, color=COLORS["neutral"], lw=1.3, ls="--", marker="o", markersize=3, label="MLM only")
ax1.set_xscale("log", base=2)
ax1.set_xticks(lens); ax1.set_xticklabels([str(L) for L in lens])
ax1.set_xlabel("context length (tokens)")
ax1.set_ylabel("retrieval accuracy (\%)")
ax1.set_title("By context length", fontsize=9)
ax1.legend(fontsize=7.5, loc="lower left", frameon=False)
ax1.minorticks_off()

# (b) by needle position
pos = ["start", "middle", "end"]
cp = [clm["by_position"][p]["accuracy"] * 100 for p in pos]
mp = [mlm["by_position"][p]["accuracy"] * 100 for p in pos]
x = range(len(pos))
ax2.plot(x, cp, color=COLORS["primary_dark"], lw=1.7, marker="o", markersize=3.5, label="CLM detour")
ax2.plot(x, mp, color=COLORS["neutral"], lw=1.3, ls="--", marker="o", markersize=3, label="MLM only")
ax2.set_xticks(list(x)); ax2.set_xticklabels(pos)
ax2.set_xlabel("needle position")
ax2.set_ylabel("retrieval accuracy (\%)")
ax2.set_title("By needle position", fontsize=9)
ax2.set_xlim(-0.3, 2.3)

fig.tight_layout()
out = os.path.join(HERE, "needle.pdf")
fig.savefig(out, bbox_inches="tight")
print("wrote", out)
