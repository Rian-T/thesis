"""
Generate combined_educational_scores.pdf — thesis visual style.
Heatmap: educational score distributions by document type and domain.
Same layout as original but with thesis Lavender palette.
"""
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import os

# ── Thesis palette ──────────────────────────────────────────────────────────
INK = "#2D2A3C"
NEUTRAL = "#667082"
# Lavender sequential: white → light lavender → deep lavender
CMAP_COLORS = ["#F9F7FC", "#DDD8F0", "#B8ADE0", "#A694E8", "#7A64C8", "#5A48A0"]
THESIS_CMAP = mcolors.LinearSegmentedColormap.from_list("thesis_lavender", CMAP_COLORS)

# ── Data ─────────────────────────────────────────────────────────────────────
TYPE_LABELS = ["Study", "Review", "Clinical case", "Other"]
TYPE_COUNTS = ["n=100,387,809", "n=6,811,226", "n=2,122,403", "n=24,295,531"]
TYPE_DATA = np.array([
    # score 1, 2, 3, 4, 5  (rows = categories, cols = scores)
    [0.7, 7.9, 10.0, 78.7, 2.6],   # Study
    [0.3, 1.6, 5.0, 86.9, 6.1],    # Review
    [4.0, 14.4, 24.6, 57.0, 0.0],  # Clinical case
    [43.4, 30.9, 14.6, 11.1, 0.0], # Other
]) / 100.0

DOMAIN_LABELS = ["Biomedical", "Clinical", "Other"]
DOMAIN_COUNTS = ["n=116,221,134", "n=2,182,784", "n=15,213,051"]
DOMAIN_DATA = np.array([
    [1.8, 9.4, 10.9, 75.3, 2.6],   # Biomedical
    [6.0, 23.4, 26.6, 44.0, 0.0],  # Clinical
    [60.1, 29.4, 8.3, 2.1, 0.0],   # Other
]) / 100.0

SCORE_LABELS = ["1", "2", "3", "4", "5"]


def set_thesis_style():
    plt.rcParams.update({
        "text.usetex": True,
        "font.family": "serif",
        "font.serif": ["Palatino", "TeX Gyre Pagella"],
        "text.color": INK,
        "axes.labelcolor": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "font.size": 11, "axes.labelsize": 12, "axes.titlesize": 14,
        "xtick.labelsize": 11, "ytick.labelsize": 11,
        "figure.dpi": 300, "savefig.dpi": 300,
    })


def plot_heatmap(ax, data, row_labels, row_counts, title, show_ylabel=True):
    im = ax.imshow(data, cmap=THESIS_CMAP, aspect="auto", vmin=0, vmax=0.9)

    # Grid lines
    ax.set_xticks(np.arange(data.shape[1]))
    ax.set_yticks(np.arange(data.shape[0]))
    ax.set_xticklabels(SCORE_LABELS)
    ylabels = [f"{lab}\n\\footnotesize{{{cnt}}}" for lab, cnt in zip(row_labels, row_counts)]
    ax.set_yticklabels(ylabels)

    # Cell borders
    for edge, spine in ax.spines.items():
        spine.set_visible(False)
    ax.set_xticks(np.arange(data.shape[1] + 1) - 0.5, minor=True)
    ax.set_yticks(np.arange(data.shape[0] + 1) - 0.5, minor=True)
    ax.grid(which="minor", color="white", linewidth=2)
    ax.tick_params(which="minor", bottom=False, left=False)

    # Value annotations
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            val = data[i, j]
            if val == 0:
                text = "--"
            else:
                text = f"{val * 100:.1f}\\%"
            color = "white" if val > 0.45 else INK
            ax.text(j, i, text, ha="center", va="center",
                    fontsize=10, color=color)

    ax.set_title(title, fontweight="bold", pad=10)
    ax.set_xlabel("Educational Score")
    if show_ylabel:
        ax.set_ylabel("")


def main():
    set_thesis_style()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 3.5),
                                    gridspec_kw={"width_ratios": [4, 3]})

    plot_heatmap(ax1, TYPE_DATA, TYPE_LABELS, TYPE_COUNTS,
                 "By Document Type")
    plot_heatmap(ax2, DOMAIN_DATA, DOMAIN_LABELS, DOMAIN_COUNTS,
                 "By Domain", show_ylabel=True)

    # Colorbar
    cbar = fig.colorbar(ax1.images[0], ax=[ax1, ax2], location="right",
                        fraction=0.02, pad=0.03, label="Proportion (\\%)")
    cbar.ax.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, _: f"{x * 100:.0f}"))

    plt.tight_layout()

    out_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(out_dir, "combined_educational_scores.pdf")
    plt.savefig(path, dpi=300, bbox_inches="tight")
    print(f"Saved {path}")


if __name__ == "__main__":
    main()
