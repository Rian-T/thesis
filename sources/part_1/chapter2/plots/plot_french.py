"""
Generate french_medmcqa_performance.pdf — thesis visual style (Lavender & Lime palette).
"""
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import numpy as np
import os

# ── Thesis palette ──────────────────────────────────────────────────────────
COLORS = {
    "primary":       "#A694E8",  # Lavender
    "primary_dark":  "#5A48A0",
    "secondary":     "#ABCC6E",  # Lime
    "tertiary":      "#F1B890",  # Peach
    "neutral":       "#667082",
    "ink":           "#2D2A3C",
    "baseline_red":  "#C25A5A",
}

# ── Pre-cached data ──────────────────────────────────────────────────────────
BASELINE_VALUE = 38.32  # Olmo2-phase1

RAW_DATA = {
    "Fr": [
        (1.0, 35.51), (2.1, 36.45), (4.2, 36.14), (8.4, 35.83),
        (12.6, 36.14), (16.8, 38.32), (21.0, 37.38), (25.2, 39.56),
        (29.4, 39.56), (33.6, 40.5),
    ],
    "Articles": [
        (1.0, 35.83), (2.1, 33.02), (4.2, 36.45), (8.4, 37.69),
        (12.6, 36.76), (16.8, 37.07), (21.0, 36.76), (25.2, 37.38),
        (29.4, 37.69), (33.6, 38.32),
    ],
    "All": [
        (1.0, 33.02), (2.1, 35.51), (4.2, 34.89), (8.4, 37.07),
        (12.6, 34.89), (16.8, 35.83), (21.0, 36.45), (25.2, 35.83),
        (29.4, 37.07), (33.6, 36.76),
    ],
}

DATASET_STYLE = {
    "Fr":       {"color": COLORS["secondary"],    "marker": "^", "label": "BE-French",  "lw": 2.5, "ms": 7},
    "Articles": {"color": COLORS["neutral"],      "marker": "o", "label": "BE-Base",    "lw": 1.5, "ms": 5},
    "All":      {"color": COLORS["primary_dark"], "marker": "X", "label": "BE-All",     "lw": 2.0, "ms": 6},
}

def set_thesis_style():
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["TeX Gyre Pagella", "Palatino", "DejaVu Serif"],
        "text.color": COLORS["ink"],
        "axes.labelcolor": COLORS["ink"],
        "xtick.color": COLORS["ink"],
        "ytick.color": COLORS["ink"],
        "font.size": 13, "axes.labelsize": 14, "axes.titlesize": 16,
        "xtick.labelsize": 12, "ytick.labelsize": 12, "legend.fontsize": 12,
        "figure.dpi": 300, "savefig.dpi": 300,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.edgecolor": COLORS["neutral"],
        "axes.linewidth": 0.8,
    })

def main():
    set_thesis_style()
    fig, ax = plt.subplots(figsize=(5.5, 4))

    for dataset in ["Fr", "Articles", "All"]:
        pts = RAW_DATA[dataset]
        st = DATASET_STYLE[dataset]
        x = np.array([p[0] for p in pts])
        y = np.array([p[1] for p in pts])

        ax.plot(x, y, "-", linewidth=st["lw"], color=st["color"], alpha=0.9, zorder=2)
        ax.plot(x, y, marker=st["marker"], markersize=st["ms"],
                markerfacecolor=st["color"], markeredgecolor=COLORS["ink"],
                markeredgewidth=0.5, linestyle="None", alpha=0.9, zorder=3)

    # Baseline
    ax.axhline(y=BASELINE_VALUE, linestyle="--", color=COLORS["baseline_red"],
               linewidth=1.5, alpha=0.7, zorder=1)

    ax.set_xlabel("Additional Tokens (B)")
    ax.set_ylabel("Accuracy (%)")
    ax.set_title("FrenchMedMCQA Performance", fontweight="medium")
    ax.grid(True, axis="y", alpha=0.2, linestyle="--", color=COLORS["neutral"])
    ax.set_facecolor("white")

    # Legend
    handles = [mlines.Line2D([], [], color=DATASET_STYLE[ds]["color"],
                              marker=DATASET_STYLE[ds]["marker"], markersize=7,
                              markerfacecolor=DATASET_STYLE[ds]["color"],
                              markeredgecolor=COLORS["ink"], markeredgewidth=0.5,
                              linestyle="-", linewidth=DATASET_STYLE[ds]["lw"],
                              label=DATASET_STYLE[ds]["label"])
               for ds in ["Fr", "Articles", "All"]]
    handles.append(mlines.Line2D([], [], color=COLORS["baseline_red"],
                                 linestyle="--", linewidth=1.5, alpha=0.7,
                                 label="OLMo2-7B-stage1"))
    ax.legend(handles=handles, frameon=True, framealpha=0.95,
              facecolor="white", edgecolor=COLORS["neutral"], loc="lower right")
    plt.tight_layout()

    out_dir = os.path.dirname(os.path.abspath(__file__))
    for fmt in ["pdf", "png"]:
        path = os.path.join(out_dir, f"french_medmcqa_performance.{fmt}")
        plt.savefig(path, dpi=300, bbox_inches="tight")
        print(f"Saved {path}")

if __name__ == "__main__":
    main()
