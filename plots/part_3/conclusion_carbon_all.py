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

# (label, training kg, data-prep kg) -- ordered by training carbon, descending.
MODELS = [
    ("DrBERT",                           26.1,   0.0),
    ("DoctoModernBERT",                  10.9, 158.1),
    ("AliBERT",                           8.2,   0.0),
    ("CamemBERT-bio",                     0.8,   0.0),
    ("ModernCamemBERT-bio",              0.46, 14.7),
    ("ModernCamemBERT-bio-v2",           0.06,  1.37),
]
OUTPUT = os.path.join(os.path.dirname(__file__), "output", "conclusion_carbon_all")


def main():
    apply_style()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 3.0), sharey=True)

    y = list(range(len(MODELS)))[::-1]  # first entry on top
    train = [m[1] for m in MODELS]
    prep = [m[2] for m in MODELS]

    # (a) model training
    ax1.barh(y, train, height=0.6, color=COLORS["primary"],
             edgecolor=COLORS["primary_dark"], linewidth=0.7)
    for yi, v in zip(y, train):
        ax1.text(v + 0.6, yi, f"{round(v, 2):g}", va="center", ha="left",
                 fontsize=8.5, color=COLORS["ink"])
    ax1.set_yticks(y); ax1.set_yticklabels([m[0] for m in MODELS], fontsize=9)
    ax1.set_xlim(0, 31); ax1.set_xlabel("kg CO$_2$eq")
    ax1.set_title("Model training", fontsize=10.5)
    ax1.tick_params(axis="y", length=0)

    # (b) data preparation (LLM curation of the corpus)
    ax2.barh(y, prep, height=0.6, color=COLORS["tertiary"],
             edgecolor=COLORS["tertiary_dark"], linewidth=0.7)
    for yi, v in zip(y, prep):
        lab = f"{round(v, 2):g}" if v > 0 else "\\textemdash"
        ax2.text(v + 3.5 if v > 0 else 3.5, yi, lab, va="center", ha="left",
                 fontsize=8.5, color=COLORS["ink"])
    ax2.set_xlim(0, 185); ax2.set_xlabel("kg CO$_2$eq")
    ax2.set_title("Data preparation", fontsize=10.5)
    ax2.tick_params(axis="y", length=0)

    for ax in (ax1, ax2):
        ax.margins(y=0.08)

    fig.tight_layout(w_pad=1.6)
    for ext in ("pdf", "png"):
        fig.savefig(f"{OUTPUT}.{ext}", bbox_inches="tight")
        print(f"{OUTPUT}.{ext}")
    plt.close(fig)


if __name__ == "__main__":
    main()
