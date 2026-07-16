"""
Conclusion carbon (option B): the money plot -- capability per unit of carbon.

x = training carbon (kg CO2, log), y = medical-coding score (DOC rel-avg, 9-seed).
Baseline = the reused ModernCamemBERT base (no added biomedical carbon), drawn as
a dashed line: our continual-pretraining chain climbs above it at a few kg, while
the from-scratch DoctoModernBERT spends ~10x more carbon for a lower score.

CAVEAT: the DOC scores come from FINAL_RESULTS.md (a newer/broader coding
benchmark than the thesis body's OntoBook table on FRACCO/Cant/Dist). Carbon
numbers are consistent with the thesis.

Data (FINAL_RESULTS.md DOC rel-avg; CARBON_FOOTPRINT.md carbon, base excluded):
  ModernCamemBERT (base, reused)   63.6   ~0 added
  ModernCamemBERT-bio (CPT)        68.1   15.2 kg
  ModernCamemBERT-bio-v2 (base)    69.0   16.6 kg
  ModernCamemBERT-bio-v2-large     72.3   ~17 kg
  DoctoModernBERT (from scratch)   67.8   169 kg
"""
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from thesis_style import COLORS, apply_style

BASE = 63.6  # ModernCamemBERT base (reused, excluded from carbon)
# name, carbon kg, DOC score, regime, (dx, dy) label offset in points
POINTS = [
    ("ModernCamemBERT-bio",        15.2, 68.1, "cpt",     (8, -3)),
    ("bio-v2",                     16.6, 69.0, "cpt",     (8, 2)),
    ("bio-v2-large",               17.0, 72.3, "cpt",     (9, 0)),
    ("DoctoModernBERT",            169.0, 67.8, "scratch", (-10, -12)),
]
OUTPUT = os.path.join(os.path.dirname(__file__), "output", "conclusion_moneyplot")


def main():
    apply_style()
    fig, ax = plt.subplots(figsize=(5.6, 3.3))

    ax.axhline(BASE, ls="--", lw=0.9, color=COLORS["neutral"])
    ax.text(0.7, BASE + 0.2, "ModernCamemBERT base (reused, no added carbon)",
            fontsize=7.5, color=COLORS["neutral"], va="bottom")

    col = {"cpt": COLORS["secondary_dark"], "scratch": COLORS["tertiary_dark"]}
    for name, c, s, regime, (dx, dy) in POINTS:
        ax.scatter([c], [s], s=46, color=col[regime], zorder=3,
                   edgecolor="white", linewidth=0.6)
        ax.annotate(name, (c, s), textcoords="offset points", xytext=(dx, dy),
                    fontsize=8, color=COLORS["ink"],
                    ha="left" if dx >= 0 else "right")

    ax.set_xscale("log")
    ax.set_xlim(0.6, 500)
    ax.set_ylim(62.5, 74)
    ax.set_xlabel("Training carbon (kg CO$_2$eq, log scale)")
    ax.set_ylabel("Medical coding score")

    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(f"{OUTPUT}.{ext}", bbox_inches="tight")
        print(f"{OUTPUT}.{ext}")
    plt.close(fig)


if __name__ == "__main__":
    main()
