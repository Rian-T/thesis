"""
Benchmark vs generalisation — two side-by-side panels showing the near-inverse
ordering. Left: standard benchmark (strict macro-F1). Right: generalisation to
novel types (reference-free judge MAP). Same model = same colour across panels,
so the rank flip is visible at a glance.

Numbers verified against publications/gliner (judge_eval/benchmark reports).
Generates: plots/chapter18/benchmark_vs_judge.pdf
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import matplotlib.pyplot as plt
from thesis_style import COLORS, apply_style

# model -> colour (consistent across panels)
COLOR = {
    "baseline": COLORS["neutral"],
    "GLiNER2-large":              COLORS["tertiary_dark"],
    "entity-tuned":               COLORS["primary_dark"],
    "multi-task":                 COLORS["secondary_dark"],
}

# left panel: standard benchmark, strict macro-F1
BENCH = {
    "baseline": 0.389,
    "GLiNER2-large":              0.346,
    "entity-tuned":               0.331,
    "multi-task":                 0.266,
}
# right panel: generalisation to novel types, judge MAP
NOVEL = {
    "entity-tuned":               0.476,
    "baseline": 0.381,
    "multi-task":                 0.302,
    "GLiNER2-large":              0.285,
}


def panel(ax, data, title, ylabel=None):
    items = sorted(data.items(), key=lambda kv: kv[1], reverse=True)
    names = [k for k, _ in items]
    vals = [v for _, v in items]
    cols = [COLOR[k] for k in names]
    x = range(len(names))
    bars = ax.bar(x, vals, color=cols, width=0.7, edgecolor=COLORS["ink"], linewidth=0.5)
    for xi, v in zip(x, vals):
        ax.text(xi, v + 0.012, f"{v:.3f}", ha="center", va="bottom",
                fontsize=10, color=COLORS["ink"])
    ax.set_xticks(list(x))
    ax.set_xticklabels(names, fontsize=10)
    ax.set_ylim(0, 0.55)
    ax.set_title(title, fontsize=13, pad=10)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=12)
    ax.grid(True, axis="y", alpha=0.18, linestyle="--", color=COLORS["neutral"])
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.set_facecolor("white")


def main():
    apply_style()
    fig, axes = plt.subplots(1, 2, figsize=(8.8, 3.4))
    panel(axes[0], BENCH, "Standard benchmark", ylabel="strict macro-$F_1$")
    panel(axes[1], NOVEL, "Generalisation to novel types", ylabel="judge MAP")
    fig.patch.set_facecolor("white")
    plt.tight_layout()
    out = os.path.join(os.path.dirname(__file__), "benchmark_vs_judge.pdf")
    plt.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    print("Saved", out)


if __name__ == "__main__":
    main()
