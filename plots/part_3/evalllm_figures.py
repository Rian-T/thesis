"""
TABIB benchmark result figures, redrawn in the thesis visual style.

Same data as publications/evalllm-2026/figures.py, but with the thesis palette
(bad = peach, good = lime, reference = ink, neutral = gray), the thesis serif
rcParams (plots.thesis_style), and English labels for the thesis body.

Outputs: plots/part_3/output/evalllm_fig{1,2,3}.pdf
"""
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from thesis_style import COLORS, apply_style

OUT = os.path.join(os.path.dirname(__file__), "output")
MODELS = ["Nemotron 4B", "Qwen3.5 4B", "Gemma4 E2B", "MedGemma 4B",
          "Ministral 8B", "Qwen3.5 9B", "Gemma4 E4B"]

BAD = COLORS["tertiary_dark"]      # peach   — worse / unsafe / unstable
BADF = COLORS["tertiary"]          # peach light
GOOD = COLORS["secondary_dark"]    # lime    — better / stable
REF = COLORS["ink"]                # reference point
GREY = COLORS["neutral"]           # non-significant / neutral


def _bare(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def fig1():
    surf_dci = [0.088, 0.088, 0.721, 0.149, 0.176, 0.206, 0.603]
    surf_brand = [0.044, 0.000, 0.603, 0.191, 0.088, 0.206, 0.221]
    surf_p = [0.508, 0.031, 0.134, 0.549, 0.109, 1.000, 0.000]
    dist_direct = [0.09, 0.96, 1.00, 0.63, 1.00, 0.74, 1.00]
    dist_embedded = [0.938, 0.802, 0.265, 0.365, 1.000, 0.387, 0.743]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.4, 3.7), sharey=True)
    y = np.arange(len(MODELS))

    for i in range(7):
        sig = surf_p[i] < 0.05
        lc = BAD if sig else GREY
        ax1.plot([surf_dci[i], surf_brand[i]], [y[i]] * 2, color=lc, lw=1.8, zorder=1)
        ax1.scatter(surf_dci[i], y[i], color=REF, s=42, zorder=2, edgecolors="white", linewidths=0.5)
        ax1.scatter(surf_brand[i], y[i], color=lc, marker="s", s=42, zorder=2, edgecolors="white", linewidths=0.5)
        d = surf_brand[i] - surf_dci[i]
        stars = "**" if surf_p[i] < 0.01 else "*" if surf_p[i] < 0.05 else ""
        ax1.text(max(surf_dci[i], surf_brand[i]) + 0.03, y[i],
                 f"{d*100:+.0f}\\%{stars}", va="center", fontsize=7.5, color=lc)
    ax1.set_yticks(y); ax1.set_yticklabels(MODELS)
    ax1.set_xlabel("Accuracy"); ax1.set_xlim(-0.05, 1.18); ax1.invert_yaxis()
    ax1.set_title("(a) Surface robustness (B1)", fontsize=11)
    ax1.scatter([], [], color=REF, s=26, label="generic name")
    ax1.scatter([], [], color=BAD, marker="s", s=26, label="brand name ($p<0.05$)")
    ax1.scatter([], [], color=GREY, marker="s", s=26, label="brand name (n.s.)")
    ax1.legend(fontsize=7.5, loc="lower right", frameon=False)
    _bare(ax1)

    for i in range(7):
        d = dist_embedded[i] - dist_direct[i]
        lc = BAD if abs(d) > 0.30 else GREY
        ax2.plot([dist_direct[i], dist_embedded[i]], [y[i]] * 2, color=lc, lw=1.8, zorder=1)
        ax2.scatter(dist_direct[i], y[i], color=REF, s=42, zorder=2, edgecolors="white", linewidths=0.5)
        ax2.scatter(dist_embedded[i], y[i], color=lc, marker="s", s=42, zorder=2, edgecolors="white", linewidths=0.5)
        ax2.text(max(dist_direct[i], dist_embedded[i]) + 0.03, y[i],
                 f"{d*100:+.0f}\\%", va="center", fontsize=7.5, color=lc)
    ax2.set_xlabel("Sensitivity"); ax2.set_xlim(-0.05, 1.28); ax2.invert_yaxis()
    ax2.set_title("(b) Contextual distraction (B2)", fontsize=11)
    ax2.scatter([], [], color=REF, s=26, label="direct")
    ax2.scatter([], [], color=BAD, marker="s", s=26, label="embedded ($|\\Delta|>30\\%$)")
    ax2.scatter([], [], color=GREY, marker="s", s=26, label="embedded")
    ax2.legend(fontsize=7.5, loc="upper left", frameon=False)
    _bare(ax2)

    fig.tight_layout(w_pad=1.5)
    fig.savefig(f"{OUT}/evalllm_fig1.pdf", bbox_inches="tight")
    fig.savefig(f"{OUT}/evalllm_fig1.png", bbox_inches="tight", dpi=150)
    plt.close(fig); print("fig1")


def fig2():
    cap_models = ["Ministral 8B", "Nemotron 4B", "Qwen3.5 9B", "Qwen3.5 4B",
                  "Gemma4 E4B", "Gemma4 E2B", "MedGemma 4B"]
    _raw = [(42, 29, 19, 3), (47, 11, 20, 16), (43, 20, 15, 21), (30, 30, 25, 14),
            (50, 25, 22, 3), (43, 12, 37, 7), (19, 17, 61, 2)]
    _norm = [tuple(round(100 * x / sum(r)) for x in r) for r in _raw]
    cap_m = [r[0] for r in _norm]; cap_h = [r[1] for r in _norm]
    cap_d = [r[2] for r in _norm]; cap_c = [r[3] for r in _norm]

    ece_models = ["Nemotron 4B", "Gemma4 E4B", "Qwen3.5 9B", "Gemma4 E2B",
                  "Ministral 8B", "Qwen3.5 4B", "MedGemma 4B"]
    ece_vals = [0.693, 0.533, 0.500, 0.499, 0.238, 0.177, 0.132]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.4, 3.3))
    # neutral shades for maintain/hedge/deflect, peach for capitulate
    c_m, c_h, c_d = "#C9CDD6", GREY, COLORS["ink"]
    y1 = np.arange(len(cap_models))
    ax1.barh(y1, cap_m, color=c_m, height=0.58, label="maintain")
    ax1.barh(y1, cap_h, left=cap_m, color=c_h, height=0.58, label="hedge")
    ld = [m + h for m, h in zip(cap_m, cap_h)]
    ax1.barh(y1, cap_d, left=ld, color=c_d, height=0.58, label="deflect")
    lc = [a + b for a, b in zip(ld, cap_d)]
    ax1.barh(y1, cap_c, left=lc, color=BAD, height=0.58, label="capitulate")
    for i in range(len(cap_models)):
        if cap_c[i] > 5:
            ax1.text(lc[i] + cap_c[i] / 2, y1[i], f"{cap_c[i]}\\%", ha="center",
                     va="center", fontsize=8, color="white", fontweight="bold")
    ax1.set_yticks(y1); ax1.set_yticklabels(cap_models)
    ax1.set_xlabel("Proportion (\\%)"); ax1.set_xlim(0, 108); ax1.invert_yaxis()
    ax1.legend(fontsize=7.5, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=4, frameon=False)
    ax1.set_title("(a) Adversarial capitulation (B3)", fontsize=11); _bare(ax1)

    y2 = np.arange(len(ece_models))
    cols = [BAD if e > 0.4 else BADF if e > 0.2 else GREY for e in ece_vals]
    ax2.barh(y2, ece_vals, color=cols, height=0.58, edgecolor="white", linewidth=0.5)
    for i, e in enumerate(ece_vals):
        ax2.text(e + 0.015, y2[i], f"{e:.2f}", va="center", fontsize=8)
    ax2.set_yticks(y2); ax2.set_yticklabels(ece_models)
    ax2.set_xlabel("ECE"); ax2.set_xlim(0, 0.85); ax2.invert_yaxis()
    ax2.set_title("(b) Confidence calibration (B5)", fontsize=11); _bare(ax2)

    fig.tight_layout(w_pad=2.0)
    fig.savefig(f"{OUT}/evalllm_fig2.pdf", bbox_inches="tight")
    fig.savefig(f"{OUT}/evalllm_fig2.png", bbox_inches="tight", dpi=150)
    plt.close(fig); print("fig2")


def fig3():
    kappa = [0.041, 0.360, 0.004, 0.000, 0.586, 0.418, 0.000]
    tau_models = ["MedGemma 4B", "Nemotron 4B", "Qwen3.5 9B", "Gemma4 E2B",
                  "Ministral 8B", "Qwen3.5 4B", "Gemma4 E4B"]
    tau = [0.069, 0.167, 0.416, 0.458, 0.463, 0.479, 0.554]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.4, 3.4))
    y1 = np.arange(len(MODELS))
    c1 = [BAD if k < 0.2 else BADF if k < 0.4 else GOOD for k in kappa]
    ax1.barh(y1, kappa, color=c1, height=0.58, edgecolor="white", linewidth=0.5)
    for i, k in enumerate(kappa):
        ax1.text(k + 0.015, y1[i], f"{k:.3f}", va="center", fontsize=8)
    ax1.set_yticks(y1); ax1.set_yticklabels(MODELS)
    ax1.set_xlabel("Cohen's $\\kappa$"); ax1.set_xlim(0, 0.75); ax1.invert_yaxis()
    ax1.axvline(0.4, color=COLORS["ink"], ls="--", lw=0.7, alpha=0.35)
    ax1.set_title("(a) Cross-lingual consistency (B4)", fontsize=11); _bare(ax1)

    y2 = np.arange(len(tau_models))
    c2 = [BAD if t < 0.2 else BADF if t < 0.4 else GREY for t in tau]
    ax2.barh(y2, tau, color=c2, height=0.58, edgecolor="white", linewidth=0.5)
    for i, t in enumerate(tau):
        ax2.text(t + 0.01, y2[i], f"{t:.3f}", va="center", fontsize=8)
    ax2.set_yticks(y2); ax2.set_yticklabels(tau_models)
    ax2.set_xlabel("Kendall $\\tau$"); ax2.set_xlim(0, 0.70); ax2.invert_yaxis()
    ax2.axvline(0.6, color=COLORS["ink"], ls="--", lw=0.7, alpha=0.35)
    ax2.set_title("(b) Demographic bias (B7)", fontsize=11); _bare(ax2)

    fig.tight_layout(w_pad=2.0)
    fig.savefig(f"{OUT}/evalllm_fig3.pdf", bbox_inches="tight")
    fig.savefig(f"{OUT}/evalllm_fig3.png", bbox_inches="tight", dpi=150)
    plt.close(fig); print("fig3")


def fig4():
    import matplotlib.colors as mcolors
    # 7x7 normalised behavioural profile (1 = best), rows sorted by mean desc.
    rows = [
        ("Ministral 8B", 0.59, [0.50, 1.00, 0.72, 0.59, 0.76, 0.10, 0.46]),
        ("Qwen3.5 4B",   0.51, [0.17, 0.81, 0.84, 0.36, 0.82, 0.10, 0.48]),
        ("Qwen3.5 9B",   0.49, [0.78, 0.44, 0.79, 0.42, 0.50, 0.10, 0.42]),
        ("MedGemma 4B",  0.44, [0.64, 0.37, 1.00, 0.00, 0.87, 0.10, 0.07]),
        ("Gemma4 E4B",   0.38, [0.00, 0.74, 0.88, 0.00, 0.47, 0.05, 0.55]),
        ("Gemma4 E2B",   0.35, [0.19, 0.26, 1.00, 0.00, 0.50, 0.05, 0.46]),
        ("Nemotron 4B",  0.21, [0.00, 0.09, 0.78, 0.04, 0.31, 0.10, 0.17]),
    ]
    cols = ["B1\nSurface", "B2\nDistract.", "B3\nCapitul.", "B4\nCross-ling.",
            "B5\nCalibr.", "B6\nPrudence", "B7\nBias"]
    M = np.array([r[2] for r in rows])
    # peach (bad, 0) -> pale -> lime (good, 1)
    cmap = mcolors.LinearSegmentedColormap.from_list(
        "thesis_div",
        [COLORS["tertiary_dark"], COLORS["tertiary"], "#F4EFE6",
         COLORS["secondary"], COLORS["secondary_dark"]])

    fig, ax = plt.subplots(figsize=(6.6, 4.0))
    im = ax.imshow(M, cmap=cmap, vmin=0, vmax=1, aspect="auto")
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            ax.text(j, i, f"{M[i, j]:.2f}", ha="center", va="center",
                    fontsize=8, color=COLORS["ink"])
    ax.set_xticks(range(len(cols))); ax.set_xticklabels(cols, fontsize=8.5)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([f"{r[0]} ({r[1]:.2f})" for r in rows], fontsize=9)
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    cb = fig.colorbar(im, ax=ax, fraction=0.032, pad=0.02)
    cb.set_ticks([0, 0.5, 1.0]); cb.ax.tick_params(length=0, labelsize=8)
    cb.outline.set_visible(False)
    fig.tight_layout()
    fig.savefig(f"{OUT}/evalllm_fig4.pdf", bbox_inches="tight")
    fig.savefig(f"{OUT}/evalllm_fig4.png", bbox_inches="tight", dpi=150)
    plt.close(fig); print("fig4")


if __name__ == "__main__":
    apply_style()
    fig1(); fig2(); fig3(); fig4()
