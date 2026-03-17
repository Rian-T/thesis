"""
Generate combined_plot_v2.pdf — thesis visual style (Lavender & Lime palette).
3 panels: Medical QA Avg, MMLU ProfMed, Overall Avg.
"""
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import numpy as np
from matplotlib.ticker import MaxNLocator
from collections import OrderedDict
import os

# ── Thesis palette ──────────────────────────────────────────────────────────
COLORS = {
    "primary":       "#A694E8",  # Lavender
    "primary_dark":  "#5A48A0",
    "secondary":     "#ABCC6E",  # Lime
    "secondary_dark":"#5F8228",
    "tertiary":      "#F1B890",  # Peach
    "tertiary_dark": "#B46E3C",
    "neutral":       "#667082",
    "ink":           "#2D2A3C",
    "baseline_red":  "#C25A5A",  # Muted red for baselines
}

# ── Pre-cached data ──────────────────────────────────────────────────────────
BASELINES = {
    "Olmo2-phase1": {
        "display": "OLMo2-7B-stage1",
        "MedQA": 45.33, "MedMCQA": 41.14, "PubMedQA": 75.6,
        "MMLU Anatomy": 54.81, "MMLU ClinKnow": 63.4, "MMLU CollBio": 69.44,
        "MMLU CollMed": 53.18, "MMLU MedGen": 69.0, "MMLU ProfMed": 59.93,
    },
}

_TOKENS_10 = [1.0, 2.1, 4.2, 8.4, 12.6, 16.8, 21.0, 25.2, 29.4, 33.6]
_TOKENS_11 = [1.0, 2.1, 4.2, 6.3, 8.4, 12.6, 16.8, 21.0, 25.2, 29.4, 33.6]
_TOKENS_ART = [1.0, 2.1, 4.2, 6.3, 8.4, 10.5, 12.6, 14.7, 16.8, 18.9, 21.0, 23.1, 25.2, 27.3, 29.4, 31.5, 33.6]

DATA = {
    "Articles": {
        "tokens": _TOKENS_ART,
        "MedMCQA":   [42.67,42.08,42.96,41.55,42.89,41.31,42.17,41.53,41.14,41.29,41.64,41.55,42.15,41.67,41.96,41.69,41.91],
        "MedQA":     [44.3,44.15,44.85,43.99,44.3,44.54,44.23,45.4,45.72,45.48,44.15,44.93,45.01,44.78,44.78,45.72,44.85],
        "PubMedQA":  [75.8,76.0,77.0,76.0,77.2,77.0,77.0,76.2,76.6,76.6,76.2,76.6,76.6,76.4,76.4,76.0,76.4],
        "MMLU Anatomy":  [55.56,57.04,54.81,56.3,57.04,57.04,56.3,56.3,53.33,56.3,56.3,56.3,57.78,56.3,57.78,57.78,57.04],
        "MMLU ClinKnow": [61.13,61.51,64.91,63.02,62.64,63.02,61.89,62.64,61.89,63.4,63.02,63.4,64.53,63.77,63.77,64.15,64.15],
        "MMLU CollBio":  [69.44,70.83,68.75,69.44,70.14,68.06,67.36,68.06,67.36,68.75,68.06,68.75,68.75,66.67,70.14,69.44,70.83],
        "MMLU CollMed":  [54.34,56.07,57.23,59.54,58.38,58.96,59.54,57.23,59.54,60.12,60.69,59.54,60.12,61.27,61.27,59.54,59.54],
        "MMLU MedGen":   [68.0,67.0,67.0,67.0,64.0,66.0,69.0,69.0,68.0,67.0,65.0,67.0,69.0,68.0,68.0,70.0,69.0],
        "MMLU ProfMed":  [59.19,57.72,59.93,59.93,58.09,58.46,60.66,57.72,58.09,58.09,58.46,59.19,58.46,60.29,59.19,59.93,59.93],
    },
    "Edu3": {
        "tokens": _TOKENS_11,
        "MedMCQA":   [42.12,42.12,41.84,42.77,42.1,42.29,42.84,42.36,42.98,43.03,43.08],
        "MedQA":     [43.75,43.75,44.38,45.25,45.4,46.58,46.03,45.56,45.17,45.56,45.64],
        "PubMedQA":  [75.8,75.8,77.0,75.8,76.8,76.6,76.8,77.0,77.4,76.6,77.0],
        "MMLU Anatomy":  [56.3,56.3,54.07,57.78,54.07,55.56,53.33,55.56,56.3,56.3,57.04],
        "MMLU ClinKnow": [61.51,61.51,61.13,64.15,63.77,61.89,63.77,64.15,64.53,64.15,65.28],
        "MMLU CollBio":  [68.06,68.06,66.67,68.06,70.14,68.75,68.75,67.36,68.06,68.06,68.06],
        "MMLU CollMed":  [56.07,56.07,53.76,57.8,54.34,55.49,54.91,54.91,56.07,57.23,56.65],
        "MMLU MedGen":   [69.0,69.0,70.0,71.0,70.0,73.0,68.0,70.0,69.0,71.0,71.0],
        "MMLU ProfMed":  [58.82,58.82,57.72,58.09,59.19,58.46,58.46,58.46,59.56,59.56,58.82],
    },
    "Domain": {
        "tokens": _TOKENS_11,
        "MMLU ProfMed": [58.82,62.87,60.66,63.6,60.29,63.97,63.6,64.34,62.87,64.71,63.97],
    },
    " Case": {
        "tokens": _TOKENS_11,
        "MMLU ProfMed": [61.03,61.76,61.76,62.13,63.6,63.24,61.76,62.87,62.13,62.5,62.87],
    },
    "All": {
        "tokens": _TOKENS_ART,
        "MedMCQA":   [42.27,42.91,42.67,42.39,42.31,42.62,42.94,43.13,42.39,42.24,42.7,42.43,42.27,42.84,42.6,43.25,42.79],
        "MedQA":     [45.25,44.78,44.93,43.91,44.3,45.33,47.21,46.82,47.92,47.13,48.47,47.29,46.43,46.9,46.98,47.13,47.21],
        "PubMedQA":  [75.6,75.0,75.6,76.6,76.4,76.6,76.4,77.2,77.0,77.0,76.8,76.8,76.6,76.6,76.6,76.6,76.6],
        "MMLU Anatomy":  [55.56,55.56,57.04,56.3,60.0,60.0,64.44,58.52,60.74,62.22,60.74,60.74,60.74,61.48,60.0,59.26,60.0],
        "MMLU ClinKnow": [61.13,61.89,63.77,61.89,62.26,64.15,64.53,65.28,65.66,63.77,64.53,66.04,64.53,64.91,65.66,64.91,65.66],
        "MMLU CollBio":  [69.44,68.06,67.36,66.67,66.67,67.36,68.75,66.67,66.67,68.06,69.44,68.06,68.06,68.06,68.06,68.06,68.06],
        "MMLU CollMed":  [52.05,55.49,56.65,56.65,56.07,57.23,57.23,57.23,56.65,58.96,57.8,59.54,57.8,58.96,61.85,61.27,58.96],
        "MMLU MedGen":   [66.0,69.0,69.0,72.0,68.0,70.0,71.0,69.0,72.0,71.0,71.0,72.0,73.0,73.0,72.0,71.0,69.0],
        "MMLU ProfMed":  [57.35,58.46,58.82,61.4,60.29,61.4,62.87,59.93,58.09,60.66,59.56,60.66,59.56,61.4,61.03,61.76,61.4],
    },
}

PLOTS = [
    {
        "title": "Medical QA Average",
        "datasets": ["Articles", "Edu3"],
        "benchmarks": ["MedQA", "MedMCQA", "PubMedQA"],
        "ylabel": "Accuracy (%)",
    },
    {
        "title": "MMLU Professional Medicine",
        "datasets": ["Articles", "Domain", " Case"],
        "benchmarks": ["MMLU ProfMed"],
        "ylabel": "Accuracy (%)",
    },
    {
        "title": "Overall Average",
        "datasets": ["Articles", "All"],
        "benchmarks": ["MedQA","MedMCQA","PubMedQA","MMLU Anatomy","MMLU ClinKnow",
                        "MMLU CollBio","MMLU CollMed","MMLU MedGen","MMLU ProfMed"],
        "ylabel": "Accuracy (%)",
    },
]

# Map datasets to thesis colors — "our" variants get primary/secondary, baselines get tertiary/neutral
DATASET_STYLE = {
    "Articles": {"color": COLORS["neutral"],       "marker": "o", "label": "BE-Base",        "lw": 1.5, "ms": 5},
    "Edu3":     {"color": COLORS["primary"],       "marker": "s", "label": "BE-Educational", "lw": 2.0, "ms": 5},
    "Domain":   {"color": COLORS["secondary"],     "marker": "^", "label": "BE-Clinical",    "lw": 2.0, "ms": 6},
    " Case":    {"color": COLORS["tertiary"],      "marker": "D", "label": "BE-ClinicalCase","lw": 2.0, "ms": 5},
    "All":      {"color": COLORS["primary_dark"],  "marker": "X", "label": "BE-All",         "lw": 2.5, "ms": 7},
}

def set_thesis_style():
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["TeX Gyre Pagella", "Palatino", "DejaVu Serif"],
        "text.color": COLORS["ink"],
        "axes.labelcolor": COLORS["ink"],
        "xtick.color": COLORS["ink"],
        "ytick.color": COLORS["ink"],
        "font.size": 13, "axes.labelsize": 14, "axes.titlesize": 15,
        "xtick.labelsize": 12, "ytick.labelsize": 12, "legend.fontsize": 11,
        "figure.dpi": 300, "savefig.dpi": 300,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.edgecolor": COLORS["neutral"],
        "axes.linewidth": 0.8,
    })

def main():
    set_thesis_style()
    n = len(PLOTS)
    fig, axes = plt.subplots(1, n, figsize=(min(15, 4.8 * n), 5.5))

    all_handles = OrderedDict()
    baseline_handle = None

    for i, pcfg in enumerate(PLOTS):
        ax = axes[i]
        benchmarks = pcfg["benchmarks"]
        is_avg = len(benchmarks) > 1

        bl = BASELINES["Olmo2-phase1"]
        bl_val = np.mean([bl[b] for b in benchmarks])

        for ds in pcfg["datasets"]:
            d = DATA[ds]
            st = DATASET_STYLE[ds]
            x = np.array(d["tokens"])
            y = np.mean([np.array(d[b]) for b in benchmarks], axis=0) if is_avg else np.array(d[benchmarks[0]])

            # Line with bordered markers (thesis line plot style)
            ax.plot(x, y, "-", linewidth=st["lw"], color=st["color"], alpha=0.9, zorder=2)
            dark = st["color"]  # use same color darkened for border
            ax.plot(x, y, marker=st["marker"], markersize=st["ms"],
                    markerfacecolor=st["color"], markeredgecolor=COLORS["ink"],
                    markeredgewidth=0.5, linestyle="None", alpha=0.9, zorder=3)

            if st["label"] not in all_handles:
                h = mlines.Line2D([], [], color=st["color"], marker=st["marker"],
                                  markersize=8, markerfacecolor=st["color"],
                                  markeredgecolor=COLORS["ink"], markeredgewidth=0.5,
                                  linestyle="-", linewidth=st["lw"], label=st["label"])
                all_handles[st["label"]] = h

        # Baseline dashed line
        ax.axhline(y=bl_val, linestyle="--", color=COLORS["baseline_red"],
                   linewidth=1.5, alpha=0.7, zorder=1)

        if baseline_handle is None:
            baseline_handle = mlines.Line2D([], [], color=COLORS["baseline_red"],
                                            linestyle="--", linewidth=1.5, alpha=0.7,
                                            label="OLMo2-7B-stage1")

        # Only xlabel on middle panel, only ylabel on first panel
        if i == 1:
            ax.set_xlabel("Additional Tokens (B)", fontsize=16)
        else:
            ax.set_xlabel("")
        if i == 0:
            ax.set_ylabel(pcfg["ylabel"], fontsize=16)
        else:
            ax.set_ylabel("")

        ax.set_title(pcfg["title"], fontsize=18, fontweight="bold", pad=12)
        ax.tick_params(labelsize=13)
        ax.grid(True, axis="y", alpha=0.2, linestyle="--", color=COLORS["neutral"])
        ax.set_facecolor("white")

    # Legend with larger markers
    fig.subplots_adjust(bottom=0.22)
    combined = list(all_handles.values()) + [baseline_handle]
    # Rebuild handles with larger markers for legend readability
    legend_handles = []
    for h in list(all_handles.values()):
        lh = mlines.Line2D([], [], color=h.get_color(), marker=h.get_marker(),
                           markersize=12, markerfacecolor=h.get_markerfacecolor(),
                           markeredgecolor=COLORS["ink"], markeredgewidth=0.5,
                           linestyle="-", linewidth=h.get_linewidth(),
                           label=h.get_label())
        legend_handles.append(lh)
    legend_handles.append(mlines.Line2D([], [], color=COLORS["baseline_red"],
                                        linestyle="--", linewidth=2, alpha=0.7,
                                        label="OLMo2-7B-stage1"))
    legend = fig.legend(handles=legend_handles, loc="lower center",
                        ncol=len(legend_handles), frameon=True, framealpha=0.95,
                        facecolor="white", edgecolor=COLORS["neutral"],
                        bbox_to_anchor=(0.5, 0.02), fontsize=13)
    legend.get_frame().set_linewidth(0.5)
    plt.tight_layout(rect=[0, 0.12, 1, 0.96])

    out_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(out_dir, "combined_plot_v2.pdf")
    plt.savefig(path, dpi=300, bbox_inches="tight")
    print(f"Saved {path}")

if __name__ == "__main__":
    main()
