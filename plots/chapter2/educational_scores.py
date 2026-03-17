"""
Educational score distribution heatmap.
Generates: plots/chapter2/combined_educational_scores.pdf
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import matplotlib.pyplot as plt
import numpy as np
from thesis_style import COLORS, apply_style, thesis_cmap

# ── Data ─────────────────────────────────────────────────────────────────────
TYPE_LABELS = ["Study", "Review", "Clinical case", "Other"]
TYPE_COUNTS = ["n=100,387,809", "n=6,811,226", "n=2,122,403", "n=24,295,531"]
TYPE_DATA = np.array([
    [0.7, 7.9, 10.0, 78.7, 2.6],
    [0.3, 1.6, 5.0, 86.9, 6.1],
    [4.0, 14.4, 24.6, 57.0, 0.0],
    [43.4, 30.9, 14.6, 11.1, 0.0],
]) / 100.0

DOMAIN_LABELS = ["Biomedical", "Clinical", "Other"]
DOMAIN_COUNTS = ["n=116,221,134", "n=2,182,784", "n=15,213,051"]
DOMAIN_DATA = np.array([
    [1.8, 9.4, 10.9, 75.3, 2.6],
    [6.0, 23.4, 26.6, 44.0, 0.0],
    [60.1, 29.4, 8.3, 2.1, 0.0],
]) / 100.0

SCORE_LABELS = ["1", "2", "3", "4", "5"]


def plot_heatmap(ax, data, row_labels, row_counts, title):
    im = ax.imshow(data, cmap=thesis_cmap, aspect="auto", vmin=0, vmax=1.0)

    ax.set_xticks(np.arange(data.shape[1]))
    ax.set_yticks(np.arange(data.shape[0]))
    ax.set_xticklabels(SCORE_LABELS)
    ylabels = [f"{lab}\n\\footnotesize{{{cnt}}}" for lab, cnt in zip(row_labels, row_counts)]
    ax.set_yticklabels(ylabels)

    for edge in ax.spines.values():
        edge.set_visible(False)
    ax.set_xticks(np.arange(data.shape[1] + 1) - 0.5, minor=True)
    ax.set_yticks(np.arange(data.shape[0] + 1) - 0.5, minor=True)
    ax.grid(which="minor", color="white", linewidth=2)
    ax.tick_params(which="minor", bottom=False, left=False)

    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            val = data[i, j]
            text = "--" if val == 0 else f"{val * 100:.1f}\\%"
            color = "white" if val > 0.45 else COLORS["ink"]
            ax.text(j, i, text, ha="center", va="center", fontsize=10, color=color)

    ax.set_title(title, fontweight="bold", pad=10)
    ax.set_xlabel("Educational Score")
    return im


def main():
    apply_style()
    fig = plt.figure(figsize=(11, 4.8), layout="constrained")

    # Top row: 2 heatmaps. Bottom row: empty | colorbar | empty
    gs = fig.add_gridspec(2, 4, width_ratios=[3, 1, 1, 3], height_ratios=[1, 0.05],
                          hspace=0.2)

    ax1 = fig.add_subplot(gs[0, :2])   # left heatmap spans cols 0-1
    ax2 = fig.add_subplot(gs[0, 2:])   # right heatmap spans cols 2-3
    cbar_ax = fig.add_subplot(gs[1, 1:3])  # colorbar spans middle cols only

    im = plot_heatmap(ax1, TYPE_DATA, TYPE_LABELS, TYPE_COUNTS, "By Document Type")
    plot_heatmap(ax2, DOMAIN_DATA, DOMAIN_LABELS, DOMAIN_COUNTS, "By Domain")

    cbar = fig.colorbar(im, cax=cbar_ax, orientation="horizontal")
    cbar.set_ticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    cbar.ax.xaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, _: f"{x * 100:.0f}\\%"))
    cbar.set_label("Proportion", fontsize=11)

    out = os.path.join(os.path.dirname(__file__), "combined_educational_scores.pdf")
    plt.savefig(out, dpi=300, bbox_inches="tight")
    print(f"Saved {out}")


if __name__ == "__main__":
    main()
