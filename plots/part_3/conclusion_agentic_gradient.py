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


X_EN = ["chat\n(0 tools)", "1 turn\n+ tools", "agentic", "agentic\n+ pressure"]
X_FR = ["chat\n(0 outil)", "1 tour\n+ outils", "agent", "agent\n+ pression"]
FORGED = [0, 2, 1, 5]
STALE = [0, 2, 0, 1]
N = 20
OUTPUT = os.path.join(os.path.dirname(__file__), "output", "conclusion_agentic_gradient")


def cerr(counts):
    """Wilson 95% interval expressed on the raw-count scale."""
    lo, hi = [], []
    for k in counts:
        l, h = wilson(k, N)
        lo.append(k - l * N)
        hi.append(h * N - k)
    return [lo, hi]


def main():
    french = "--fr" in sys.argv
    x_labels = X_FR if french else X_EN
    apply_style()
    plt.rcParams.update({"xtick.labelsize": 11, "ytick.labelsize": 11,
                         "axes.labelsize": 12.5})
    fig, ax = plt.subplots(figsize=(6.6, 3.6))
    x = list(range(len(x_labels)))

    # the y-axis carries the count directly (of 20), so no floating value labels
    ax.errorbar(x, STALE, yerr=cerr(STALE), marker="s", ms=6, lw=1.6, capsize=3,
                color=COLORS["neutral"], mec="white", mew=0.6, ls="--", zorder=2)
    ax.errorbar(x, FORGED, yerr=cerr(FORGED), marker="o", ms=7, lw=1.9, capsize=3,
                color=COLORS["tertiary_dark"], mfc=COLORS["tertiary"],
                mec="white", mew=0.6, zorder=3)
    # truth-delivered point at the last apparatus (open marker)
    ax.scatter([3], [4], s=54, facecolors="none",
               edgecolors=COLORS["tertiary_dark"], linewidths=1.3, zorder=4)

    # direct labels at the right, on each line -- no legend box, no in-plot text
    ax.text(3.10, 5.2, "falsifiée" if french else "forged",
            color=COLORS["tertiary_dark"], va="center",
            ha="left", fontsize=10.5)
    ax.text(3.10, 3.9, "vérité fournie" if french else "truth delivered",
            color=COLORS["tertiary_dark"],
            va="center", ha="left", fontsize=9)
    ax.text(3.10, 1.0, "authentique, périmée" if french else "stale, authentic",
            color=COLORS["neutral"], va="center",
            ha="left", fontsize=10)

    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, fontsize=11)
    ax.set_xlim(-0.3, 4.35)
    ax.set_ylabel("sessions avec acte dangereux (sur 20)" if french
                  else "sessions with an unsafe act (of 20)")
    ax.set_ylim(-0.4, 10.2)
    ax.set_yticks([0, 2, 4, 6, 8, 10])

    fig.tight_layout()
    output = f"{OUTPUT}_fr" if french else OUTPUT
    for ext in ("pdf", "png"):
        fig.savefig(f"{output}.{ext}", bbox_inches="tight")
        print(f"{output}.{ext}")
    plt.close(fig)


if __name__ == "__main__":
    main()
