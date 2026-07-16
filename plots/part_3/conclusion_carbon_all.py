"""
Conclusion carbon (option A): training emissions of every compared model.

Carbon-only, so no benchmark-consistency issue: it just answers "how much carbon
to produce this biomedical encoder", base model reused (excluded). Continual
pretraining (reuses a public base) vs from scratch, across two eras.

Data (reserved GPU-hours, 34 gCO2/kWh France; base excluded):
  CamemBERT-bio          0.8 kg   continual pretraining   (thesis Ch.4)
  AliBERT                8.2 kg   from scratch            (thesis Ch.4)
  ModernCamemBERT-bio-v2 16.6 kg  continual pretraining   (CARBON_FOOTPRINT.md)
  DrBERT                 26.1 kg  from scratch            (thesis Ch.4)
  DoctoModernBERT        169 kg   from scratch            (CARBON_FOOTPRINT.md)
"""
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from thesis_style import COLORS, apply_style

# name, kg CO2, regime
MODELS = [
    ("CamemBERT-bio",          0.8,  "cpt"),
    ("AliBERT",                8.2,  "scratch"),
    ("ModernCamemBERT-bio-v2", 16.6, "cpt"),
    ("DrBERT",                 26.1, "scratch"),
    ("DoctoModernBERT",        169.0, "scratch"),
]
OUTPUT = os.path.join(os.path.dirname(__file__), "output", "conclusion_carbon_all")


def main():
    apply_style()
    fig, ax = plt.subplots(figsize=(5.6, 2.7))

    MODELS.sort(key=lambda m: m[1])
    y = list(range(len(MODELS)))
    col = {"cpt": COLORS["secondary"], "scratch": COLORS["tertiary"]}
    edge = {"cpt": COLORS["secondary_dark"], "scratch": COLORS["tertiary_dark"]}
    colors = [col[m[2]] for m in MODELS]
    edges = [edge[m[2]] for m in MODELS]

    ax.barh(y, [m[1] for m in MODELS], height=0.62, color=colors,
            edgecolor=edges, linewidth=0.8)
    for yi, m in zip(y, MODELS):
        ax.text(m[1] * 1.15, yi, f"{m[1]:g} kg", va="center", ha="left",
                fontsize=8.5, color=COLORS["ink"])

    ax.set_yticks(y)
    ax.set_yticklabels([m[0] for m in MODELS], fontsize=9)
    ax.set_xscale("log")
    ax.set_xlim(0.4, 400)
    ax.set_xlabel("Training emissions (kg CO$_2$eq, log scale)")
    ax.tick_params(axis="y", length=0)

    handles = [
        mpatches.Patch(facecolor=COLORS["secondary"], edgecolor=COLORS["secondary_dark"],
                       label="continual pretraining"),
        mpatches.Patch(facecolor=COLORS["tertiary"], edgecolor=COLORS["tertiary_dark"],
                       label="from scratch"),
    ]
    ax.legend(handles=handles, loc="lower right", frameon=False, fontsize=8.5,
              handlelength=1.1)

    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(f"{OUTPUT}.{ext}", bbox_inches="tight")
        print(f"{OUTPUT}.{ext}")
    plt.close(fig)


if __name__ == "__main__":
    main()
