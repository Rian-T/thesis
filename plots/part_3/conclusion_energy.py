"""
Conclusion energy figure: training carbon cost of biomedical encoders.

Message carried by bar length alone: continual pretraining (CamemBERT-bio) costs
a fraction of the carbon of training a comparable model from scratch (DrBERT),
at no real loss of accuracy. Linear axis on purpose, so 0.80 kg reads as a sliver
next to 26.11 kg and the 32x is visible without any in-plot prose.

Data: \Cref{tab:carbon} in sources/part_2/chapter4/article.tex.
  DrBERT        2,560 GPU-h   26.11 kg CO2   (from scratch)
  AliBERT         960 GPU-h    8.16 kg CO2   (from scratch)
  CamemBERT-bio    78 GPU-h    0.80 kg CO2   (continual pretraining)
Basis: 34 g CO2eq per kWh (France, 2022-2023).

Generates:
    plots/part_3/output/conclusion_energy.pdf   (vector, manuscript)
    plots/part_3/output/conclusion_energy.png   (raster, review)
"""
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from thesis_style import COLORS, apply_style

# name, kg CO2, GPU-hours, is_ours
MODELS = [
    ("DrBERT",        26.11, "2,560 GPU-h", False),
    ("AliBERT",        8.16,   "960 GPU-h", False),
    ("CamemBERT-bio",  0.80,    "78 GPU-h", True),
]

OUTPUT = os.path.join(os.path.dirname(__file__), "output", "conclusion_energy")


def main():
    apply_style()
    fig, ax = plt.subplots(figsize=(5.4, 2.5))

    names = [m[0] for m in MODELS]
    co2 = [m[1] for m in MODELS]
    y = list(range(len(MODELS)))[::-1]  # first entry on top

    colors = [
        COLORS["secondary"] if m[3] else COLORS["tertiary"] for m in MODELS
    ]
    edges = [
        COLORS["secondary_dark"] if m[3] else COLORS["tertiary_dark"]
        for m in MODELS
    ]

    ax.barh(y, co2, height=0.62, color=colors, edgecolor=edges, linewidth=0.8)

    for yi, m in zip(y, MODELS):
        # value + GPU-h to the right of each bar
        ax.text(
            m[1] + 0.4, yi,
            f"{m[1]:.2f} kg CO$_2$   ({m[2]})",
            va="center", ha="left", fontsize=9, color=COLORS["ink"],
        )

    ax.set_yticks(y)
    ax.set_yticklabels(names, fontsize=10)
    ax.set_xlabel("Training emissions (kg CO$_2$eq)")
    ax.set_xlim(0, 34)
    ax.tick_params(axis="y", length=0)
    ax.margins(y=0.12)

    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(f"{OUTPUT}.{ext}", bbox_inches="tight")
        print(f"{OUTPUT}.{ext}")
    plt.close(fig)


if __name__ == "__main__":
    main()
