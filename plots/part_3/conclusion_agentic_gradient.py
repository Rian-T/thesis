"""
Conclusion, agentic probe: the safety verdict depends on the apparatus.

Same model (a single open model), same forged-authority artifact, four
measurement apparatuses of increasing realism. Sessions (of 20) in which the
model commits the unsafe act (issuing the contraindicated prescription).
Wilson 95% intervals; N=20 per cell, so the intervals are wide -- the figure
shows the direction, not a precise rate.

Data: /Users/rtouchen/tabib (figs_rows.csv, main cell, session level).
  apparatus        forged   stale
  chat (0 tools)     0/20    0/20
  1 turn + tools     2/20    2/20
  agentic            1/20    0/20
  agentic + pressure 5/20    1/20
  + truth delivered (agentic + pressure): 4/20 forged.
"""
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from thesis_style import COLORS, apply_style


def wilson(k, n, z=1.96):
    if n == 0:
        return 0.0, 0.0
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return max(0.0, c - h), min(1.0, c + h)


X = ["chat\n(0 tools)", "1 turn\n+ tools", "agentic", "agentic\n+ pressure"]
FORGED = [0, 2, 1, 5]
STALE = [0, 2, 0, 1]
N = 20
OUTPUT = os.path.join(os.path.dirname(__file__), "output", "conclusion_agentic_gradient")


def series(counts):
    y = [k / N for k in counts]
    lo = [y[i] - wilson(k, N)[0] for i, k in enumerate(counts)]
    hi = [wilson(k, N)[1] - y[i] for i, k in enumerate(counts)]
    return y, [lo, hi]


def main():
    apply_style()
    fig, ax = plt.subplots(figsize=(5.7, 3.3))
    x = list(range(len(X)))

    yf, ef = series(FORGED)
    ys, es = series(STALE)

    ax.errorbar(x, ys, yerr=es, marker="s", ms=6, lw=1.6, capsize=3,
                color=COLORS["neutral"], mec="white", mew=0.6, ls="--",
                label="stale derogation (authentic)", zorder=2)
    ax.errorbar(x, yf, yerr=ef, marker="o", ms=7, lw=1.8, capsize=3,
                color=COLORS["tertiary_dark"], mfc=COLORS["tertiary"],
                mec="white", mew=0.6, label="forged derogation", zorder=3)

    # truth-delivered point at the last apparatus
    ax.scatter([3], [4 / N], s=52, facecolors="none",
               edgecolors=COLORS["tertiary_dark"], linewidths=1.3, zorder=4)
    ax.annotate("+ truth delivered", (3, 4 / N), textcoords="offset points",
                xytext=(-6, 10), fontsize=8, color=COLORS["tertiary_dark"],
                ha="right")

    # value labels on the forged series
    for xi, (yi, k) in enumerate(zip(yf, FORGED)):
        ax.text(xi, yi + 0.028, f"{k}/{N}", ha="center", va="bottom",
                fontsize=8.5, fontweight="bold", color=COLORS["ink"])

    ax.set_xticks(x)
    ax.set_xticklabels(X, fontsize=9)
    ax.set_ylabel("sessions with an unsafe act")
    ax.set_ylim(-0.02, 0.52)
    ax.set_yticks([0, 0.1, 0.2, 0.3, 0.4, 0.5])
    ax.set_yticklabels(["0", "10\\%", "20\\%", "30\\%", "40\\%", "50\\%"])
    ax.legend(loc="upper left", frameon=False, fontsize=8.5)

    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(f"{OUTPUT}.{ext}", bbox_inches="tight")
        print(f"{OUTPUT}.{ext}")
    plt.close(fig)


if __name__ == "__main__":
    main()
