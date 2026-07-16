"""
Money figure (Part 3): parameters (log) vs value-F1 on the lymphoma eCRF.

Tufte: the message ("same value-F1 at far fewer parameters") is carried by the
positions of the points and by the caption, not by in-plot prose. No connector,
no annotation text, restrained markers and thesis colors.

Generates:
    plots/part_3/output/money_params_vs_f1.pdf   (vector, for the manuscript)
    plots/part_3/output/money_params_vs_f1.png   (r=150, on-screen review)
"""
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import numpy as np
from thesis_style import COLORS, apply_style

# ── Data ──────────────────────────────────────────────────────────────────────
# x = parameters in billions (log axis); y = value-F1 after field competition
OURS     = (0.150, 0.640)   # MC-bio-gliner, published model
BASELINE = (0.184, 0.367)   # GLiNER-BioMed, size-matched
LLM = [                            # Qwen3.5 generative family
    (0.8, 0.628),
    (2.0, 0.645),
    (4.0, 0.658),
    (9.0, 0.650),
]


def main():
    apply_style()
    fig, ax = plt.subplots(figsize=(5.6, 4.0))

    llm_x = np.array([p[0] for p in LLM])
    llm_y = np.array([p[1] for p in LLM])

    # Generative scaling series: thin neutral line + small markers
    ax.plot(llm_x, llm_y, "-", color=COLORS["neutral"], linewidth=1.4,
            alpha=0.9, zorder=2)
    ax.plot(llm_x, llm_y, "o", markersize=5, markerfacecolor=COLORS["neutral"],
            markeredgecolor=COLORS["ink"], markeredgewidth=0.5, linestyle="None",
            zorder=3)

    # Size-matched baseline: single peach square
    ax.plot([BASELINE[0]], [BASELINE[1]], "s", markersize=7,
            markerfacecolor=COLORS["tertiary"], markeredgecolor=COLORS["ink"],
            markeredgewidth=0.5, linestyle="None", zorder=3)

    # Ours: single lavender diamond
    ax.plot([OURS[0]], [OURS[1]], "D", markersize=8,
            markerfacecolor=COLORS["primary_dark"], markeredgecolor=COLORS["ink"],
            markeredgewidth=0.5, linestyle="None", zorder=4)

    # Axes
    ax.set_xscale("log")
    ax.set_xlim(0.11, 12)
    ax.set_ylim(0.32, 0.70)
    ax.set_xticks([0.15, 0.3, 1, 3, 9])
    ax.set_xticklabels(["0.15", "0.3", "1", "3", "9"])
    ax.minorticks_off()
    ax.set_xlabel("Parameters (billions, log scale)")
    ax.set_ylabel(r"Value-$F_1$")
    ax.grid(True, axis="y", alpha=0.2, linestyle="--", color=COLORS["neutral"])
    ax.set_facecolor("white")

    # Legend (no frame), thesis markers, bare names
    handles = [
        mlines.Line2D([], [], color=COLORS["primary_dark"], marker="D",
                      markersize=8, markerfacecolor=COLORS["primary_dark"],
                      markeredgecolor=COLORS["ink"], markeredgewidth=0.5,
                      linestyle="None", label="MC-bio-gliner"),
        mlines.Line2D([], [], color=COLORS["tertiary"], marker="s",
                      markersize=7, markerfacecolor=COLORS["tertiary"],
                      markeredgecolor=COLORS["ink"], markeredgewidth=0.5,
                      linestyle="None", label="GLiNER-BioMed"),
        mlines.Line2D([], [], color=COLORS["neutral"], marker="o", markersize=5,
                      markerfacecolor=COLORS["neutral"], markeredgecolor=COLORS["ink"],
                      markeredgewidth=0.5, linestyle="-", linewidth=1.4,
                      label="Qwen3.5"),
    ]
    ax.legend(handles=handles, frameon=False, fontsize=8.5, loc="lower right",
              handletextpad=0.5, labelspacing=0.4)

    fig.tight_layout()
    out = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(out, exist_ok=True)
    fig.savefig(os.path.join(out, "money_params_vs_f1.pdf"), bbox_inches="tight")
    fig.savefig(os.path.join(out, "money_params_vs_f1.png"), dpi=150,
                bbox_inches="tight")
    print("wrote money_params_vs_f1.{pdf,png}")


if __name__ == "__main__":
    main()
