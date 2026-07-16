"""
Conclusion carbon figure: where the training budget actually goes.

The argument the bars carry: pretraining an encoder is the cheap part; the
dominant cost on both sides is the language model that curates the training
corpus. Continual pretraining on a small, targeted biomedical corpus keeps the
whole pipeline about ten times lighter than training a comparable model from
scratch on a web-scale one.

Data: repo moderncamembert-bio-v2 CARBON_FOOTPRINT.md (reserved GPU-hours,
34 g CO2eq/kWh, France; H100 700 W, PUE 1.2). Each continual-pretraining stage
excludes its reused base; the from-scratch model counts everything.
  ModernCamemBERT-bio-v2 : pretraining 0.52 kg (18 GPU-h) + curation 16.1 kg (564)
  DoctoModernBERT        : pretraining 10.94 kg (383)  + curation 158.1 kg (5537)

Generates:
    plots/part_3/output/conclusion_carbon.pdf
    plots/part_3/output/conclusion_carbon.png
"""
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from thesis_style import COLORS, apply_style

# name, pretraining kg, curation kg
MODELS = [
    ("DoctoModernBERT",          10.94, 158.1),  # from scratch
    ("ModernCamemBERT-bio-v2",    0.52,  16.1),  # continual pretraining
]

OUTPUT = os.path.join(os.path.dirname(__file__), "output", "conclusion_carbon")


def main():
    apply_style()
    fig, ax = plt.subplots(figsize=(5.6, 2.35))

    y = [1, 0]  # DoctoModernBERT on top
    pre = [m[1] for m in MODELS]
    cur = [m[2] for m in MODELS]
    names = [m[0] for m in MODELS]

    ax.barh(y, pre, height=0.55, color=COLORS["primary"],
            edgecolor=COLORS["primary_dark"], linewidth=0.7, label="pretraining")
    ax.barh(y, cur, height=0.55, left=pre, color=COLORS["tertiary"],
            edgecolor=COLORS["tertiary_dark"], linewidth=0.7,
            label="LLM corpus curation")

    for yi, m in zip(y, MODELS):
        total = m[1] + m[2]
        ax.text(total + 3, yi, f"{total:.0f} kg CO$_2$", va="center", ha="left",
                fontsize=9, color=COLORS["ink"])

    ax.set_yticks(y)
    ax.set_yticklabels(names, fontsize=9.5)
    ax.set_xlabel("Training emissions (kg CO$_2$eq)")
    ax.set_xlim(0, 200)
    ax.tick_params(axis="y", length=0)
    ax.margins(y=0.35)

    ax.legend(loc="lower right", frameon=False, fontsize=8.5,
              handlelength=1.1, borderaxespad=0.3)

    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(f"{OUTPUT}.{ext}", bbox_inches="tight")
        print(f"{OUTPUT}.{ext}")
    plt.close(fig)


if __name__ == "__main__":
    main()
