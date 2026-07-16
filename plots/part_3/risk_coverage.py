"""
Risk--coverage figure (Part 3, chapter 7): selective risk vs coverage on the
lymphoma eCRF, for MC-bio-gliner (encoder) against Qwen3.5-4B (generator).

Message: the generator ranks its predictions by confidence more reliably. It
keeps a lower area under the risk--coverage curve (AURC 0.207 against 0.239) and
a higher precision at 50% coverage (0.828 against 0.770).

Generates:
    plots/part_3/output/fig_risk_coverage.pdf   (vector, for the manuscript)
    plots/part_3/output/fig_risk_coverage.png   (r=150, for on-screen review)
"""
import sys, os, json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from thesis_style import COLORS, apply_style


DATA = os.path.join(os.path.dirname(__file__), "data", "chapter7",
                    "risk_coverage_curve.json")


def main():
    apply_style()

    with open(DATA) as f:
        d = json.load(f)

    enc = d["MC-bio-gliner"]
    gen = d["Qwen3.5-4B"]

    enc_color = COLORS.get("encoder", COLORS["primary_dark"])
    gen_color = COLORS.get("neutral", COLORS["tertiary"])

    fig, ax = plt.subplots(figsize=(6.2, 4.2))

    # ── Curves + faint fill under each (evokes the AURC) ──────────────────────
    ex = np.array(enc["coverage"]); ey = np.array(enc["risk"])
    gx = np.array(gen["coverage"]); gy = np.array(gen["risk"])

    ax.fill_between(gx, gy, alpha=0.12, color=gen_color, zorder=1)
    ax.fill_between(ex, ey, alpha=0.12, color=enc_color, zorder=1)

    ax.plot(gx, gy, "-", color=gen_color, linewidth=1.8, zorder=3,
            label="Qwen3.5-4B")
    ax.plot(ex, ey, "-", color=enc_color, linewidth=1.8, zorder=4,
            label="MC-bio-gliner")

    # ── AURC labels near each curve (read from JSON, never stale) ─────────────
    ax.text(0.80, 0.45, f"AURC {enc['aurc']:.3f}", color=COLORS["primary_dark"],
            fontsize=9, ha="left", va="center", rotation=32)
    ax.text(0.82, 0.245, f"AURC {gen['aurc']:.3f}", color=gen_color,
            fontsize=9, ha="left", va="center", rotation=14)

    # ── 50% coverage marker + precision annotations ───────────────────────────
    ax.axvline(0.5, color=COLORS["neutral"], linewidth=0.8,
               linestyle=(0, (2, 3)), alpha=0.7, zorder=2)

    # precision = 1 - risk at 50% coverage
    enc_risk50 = 1.0 - enc["prec_at_50"]   # 0.230
    gen_risk50 = 1.0 - gen["prec_at_50"]   # 0.138
    ax.plot(0.5, enc_risk50, "o", markersize=6, markerfacecolor=enc_color,
            markeredgecolor="white", markeredgewidth=0.8, zorder=6)
    ax.plot(0.5, gen_risk50, "o", markersize=6, markerfacecolor=gen_color,
            markeredgecolor="white", markeredgewidth=0.8, zorder=6)

    ax.annotate(rf"prec@50\% = {enc['prec_at_50']:.3f}", (0.5, enc_risk50),
                xytext=(0.475, enc_risk50 + 0.055), ha="right", va="bottom",
                fontsize=8.5, color=COLORS["primary_dark"])
    ax.annotate(rf"prec@50\% = {gen['prec_at_50']:.3f}", (0.5, gen_risk50),
                xytext=(0.475, gen_risk50 - 0.055), ha="right", va="top",
                fontsize=8.5, color=gen_color)

    # ── Axes ──────────────────────────────────────────────────────────────────
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 0.60)
    ax.set_xlabel("coverage")
    ax.set_ylabel("selective risk (error rate)")
    ax.set_xticks([0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0])
    ax.grid(True, axis="y", alpha=0.25, linestyle="--", color=COLORS["neutral"])
    ax.set_facecolor("white")

    ax.legend(frameon=False, loc="upper left", fontsize=9,
              handletextpad=0.6, borderaxespad=0.6)

    plt.tight_layout()

    out_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(out_dir, exist_ok=True)
    pdf = os.path.join(out_dir, "fig_risk_coverage.pdf")
    png = os.path.join(out_dir, "fig_risk_coverage.png")
    plt.savefig(pdf, bbox_inches="tight")
    plt.savefig(png, dpi=150, bbox_inches="tight")
    print(f"Saved {pdf}")
    print(f"Saved {png}")


if __name__ == "__main__":
    main()
