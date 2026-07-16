"""
Conclusion carbon figure: training vs data-preparation, per encoder.

Each bar splits into two costs: the model TRAINING (pretraining / continual
pretraining) and the DATA PREPARATION (the LLM that rewrites, annotates or
generates the corpus). ModernCamemBERT-bio is split into v1 and the marginal
v2 (the ontology augmentation), to show v2 adds little. The pre-LLM-curation
encoders (CamemBERT-bio, AliBERT, DrBERT) have no data-preparation cost.

Data (kg CO2eq, reserved GPU-hours, 34 gCO2/kWh France; base excluded):
  CARBON_FOOTPRINT.md / FINAL_RESULTS.md.
    DoctoModernBERT          training 10.9  + data prep 158.1  (= 169)
    DrBERT                   training 26.1                     (from scratch)
    ModernCamemBERT-bio v1   training 0.46  + data prep 14.7   (= 15.2)
    AliBERT                  training 8.2                       (from scratch)
    ModernCamemBERT-bio v2   training 0.06  + data prep 1.37   (= 1.4, marginal)
    CamemBERT-bio            training 0.8                       (continual pretraining)
"""
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from thesis_style import COLORS, apply_style

# (label, training kg, data-prep kg) -- top to bottom.
# v1 and v2 kept adjacent so the marginal cost of v2 reads at a glance.
MODELS = [
    ("DoctoModernBERT",                  10.9, 158.1),
    ("DrBERT",                           26.1,   0.0),
    ("ModernCamemBERT-bio (v1)",          0.46, 14.7),
    ("ModernCamemBERT-bio-v2 (marginal)", 0.06,  1.37),
    ("AliBERT",                           8.2,   0.0),
    ("CamemBERT-bio",                     0.8,   0.0),
]
OUTPUT = os.path.join(os.path.dirname(__file__), "output", "conclusion_carbon_all")


def main():
    apply_style()
    fig, ax = plt.subplots(figsize=(5.9, 3.0))

    y = list(range(len(MODELS)))[::-1]  # first entry on top
    train = [m[1] for m in MODELS]
    prep = [m[2] for m in MODELS]

    ax.barh(y, train, height=0.6, color=COLORS["primary"],
            edgecolor=COLORS["primary_dark"], linewidth=0.7, label="training")
    ax.barh(y, prep, height=0.6, left=train, color=COLORS["tertiary"],
            edgecolor=COLORS["tertiary_dark"], linewidth=0.7,
            label="data preparation")

    for yi, m in zip(y, MODELS):
        total = m[1] + m[2]
        ax.text(total + 2.5, yi, f"{round(total, 1):g} kg", va="center",
                ha="left", fontsize=8.5, color=COLORS["ink"])

    ax.set_yticks(y)
    ax.set_yticklabels([m[0] for m in MODELS], fontsize=9)
    ax.set_xlabel("Training emissions (kg CO$_2$eq)")
    ax.set_xlim(0, 190)
    ax.tick_params(axis="y", length=0)
    ax.margins(y=0.08)

    ax.legend(loc="lower right", frameon=False, fontsize=8.5, handlelength=1.1,
              borderaxespad=0.4)

    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(f"{OUTPUT}.{ext}", bbox_inches="tight")
        print(f"{OUTPUT}.{ext}")
    plt.close(fig)


if __name__ == "__main__":
    main()
