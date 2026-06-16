"""
medical_ai_pubs.py — Chapter 1 Tufte figure: medical-AI publications per year.

Three PubMed yearly-count series, 1960–2025, from PubMed E-utilities esearch.fcgi
(db=pubmed, datetype=pdat, rettype=count). Access date 2026-06-15.
Source: research/ch1_deep.md Part B. Exact (URL-decoded) queries:

  Series 1 (AI envelope):  "artificial intelligence"[MeSH Terms]
  Series 2 (expert sys.):  "expert system"[tiab] OR "expert systems"[tiab]
  Series 3 (deep learn.):  "deep learning"[tiab]
  Series 4 (machine learning): "machine learning"[tiab]  (accessed 2026-06-16)

2025 counts are partial-year; recent years still accrue with indexing lag.

Run:
  uv run --with matplotlib --with numpy python plots/intro/medical_ai_pubs.py
"""
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import PchipInterpolator

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from thesis_style import COLORS, apply_style

# ──────────────────────────────────────────────────────────────────────────────
# DATA (verbatim from research/ch1_deep.md Part B — do not edit numbers)
# ──────────────────────────────────────────────────────────────────────────────

# Series 1 — "artificial intelligence"[MeSH Terms]
ai = {
    1960: 1, 1961: 3, 1962: 6, 1963: 4, 1964: 3, 1965: 2, 1966: 1, 1967: 0,
    1968: 0, 1969: 0, 1970: 0, 1971: 1, 1972: 1, 1973: 0, 1974: 1, 1975: 0,
    1976: 3, 1977: 0, 1978: 1, 1979: 0, 1980: 1, 1981: 0, 1982: 0, 1983: 5,
    1984: 1, 1985: 40, 1986: 142, 1987: 177, 1988: 197, 1989: 271, 1990: 358,
    1991: 436, 1992: 424, 1993: 595, 1994: 705, 1995: 889, 1996: 833,
    1997: 957, 1998: 993, 1999: 1030, 2000: 1225, 2001: 1316, 2002: 1423,
    2003: 1757, 2004: 2713, 2005: 3579, 2006: 4009, 2007: 4391, 2008: 4835,
    2009: 4572, 2010: 4389, 2011: 5205, 2012: 5454, 2013: 6667, 2014: 6656,
    2015: 6478, 2016: 6481, 2017: 7696, 2018: 10233, 2019: 14585, 2020: 19032,
    2021: 24936, 2022: 29695, 2023: 26228, 2024: 38015, 2025: 50559,  # 2025 partial
}

# Series 2 — "expert system"[tiab] OR "expert systems"[tiab]
expert = {
    1975: 0, 1976: 1, 1977: 0, 1978: 0, 1979: 0, 1980: 0, 1981: 1, 1982: 2,
    1983: 3, 1984: 17, 1985: 54, 1986: 47, 1987: 82, 1988: 96, 1989: 129,
    1990: 139, 1991: 142, 1992: 110, 1993: 117, 1994: 116, 1995: 128,
    1996: 103, 1997: 105, 1998: 75, 1999: 74, 2000: 80, 2001: 82, 2002: 56,
    2003: 60, 2004: 71, 2005: 73, 2006: 88, 2007: 77, 2008: 85, 2009: 76,
    2010: 75, 2011: 79, 2012: 80, 2013: 80, 2014: 83, 2015: 71, 2016: 86,
    2017: 93, 2018: 96, 2019: 100, 2020: 98, 2021: 120, 2022: 132, 2023: 120,
    2024: 107, 2025: 116,
}

# Series 3 — "deep learning"[tiab]
deep = {
    2010: 9, 2011: 13, 2012: 11, 2013: 34, 2014: 60, 2015: 128, 2016: 289,
    2017: 806, 2018: 2142, 2019: 4367, 2020: 7604, 2021: 12285, 2022: 16930,
    2023: 18525, 2024: 20989, 2025: 27390,  # 2025 partial
}

# Series 4 — "machine learning"[tiab]  (accessed 2026-06-16)
ml = {
    1988: 3, 1989: 1, 1990: 5, 1991: 7, 1992: 11, 1993: 13, 1994: 17, 1995: 23,
    1996: 21, 1997: 22, 1998: 20, 1999: 23, 2000: 35, 2001: 56, 2002: 70,
    2003: 94, 2004: 148, 2005: 192, 2006: 278, 2007: 335, 2008: 409, 2009: 491,
    2010: 556, 2011: 706, 2012: 767, 2013: 1083, 2014: 1360, 2015: 1735,
    2016: 2294, 2017: 3320, 2018: 5503, 2019: 8721, 2020: 13326, 2021: 19578,
    2022: 24760, 2023: 28019, 2024: 34037, 2025: 46363,  # 2025 partial
}


Y_FLOOR = 0.5  # log-axis bottom

# Per-series plotting start year: where each series stops being single-digit
# noise and becomes a continuous, meaningful signal. Data values are NOT
# altered — only the plotted x-range start is chosen, and the small pre-start
# region is rendered as a flat near-zero floor so the log axis reads
# "near zero, then rising" instead of an ugly sawtooth.
START = {"ai": 1960, "expert": 1981, "deep": 2010, "ml": 1990}


def series(d, start=None, floor_to=None):
    """Sorted (years, counts) from `start` onward. Counts below 1 are clamped to
    `floor_to` (default Y_FLOOR) so the line sits flat at a near-zero floor
    rather than zig-zagging between 0 and small values on the log axis."""
    f = Y_FLOOR if floor_to is None else floor_to
    xs = [x for x in sorted(d) if start is None or x >= start]
    ys = [max(d[x], f) for x in xs]
    return xs, ys


def smooth(xs, ys, n=12, win=3):
    """Light centered rolling mean (window `win`) to damp single-year noise,
    then monotone cubic (PCHIP) interpolation on a fine yearly grid for a clean
    render. Both run in log space (the axis is log). The rolling mean tames the
    isolated single-year spikes in the floored near-zero region; PCHIP is
    shape-preserving so it never overshoots below the floor between points."""
    xa = np.asarray(xs, dtype=float)
    la = np.log10(np.asarray(ys, dtype=float))
    # centered rolling mean with shrinking window at the ends (keeps endpoints)
    k = win // 2
    sm = np.array([la[max(0, i - k):i + k + 1].mean() for i in range(len(la))])
    pchip = PchipInterpolator(xa, sm)
    xf = np.linspace(xa[0], xa[-1], (len(xa) - 1) * n + 1)
    return xf, np.power(10.0, pchip(xf))


# ──────────────────────────────────────────────────────────────────────────────
# PLOT
# ──────────────────────────────────────────────────────────────────────────────

apply_style()

fig, ax = plt.subplots(figsize=(6.2, 4.7))

ax.set_yscale("log")

# Envelope: artificial intelligence (solid, primary).
x_ai, y_ai = series(ai, start=START["ai"], floor_to=1.0)
ax.plot(*smooth(x_ai, y_ai), color=COLORS["primary_dark"], lw=1.8,
        solid_capstyle="round", zorder=4)

# Expert systems: the old paradigm (dashed, peach-dark).
x_es, y_es = series(expert, start=START["expert"])
ax.plot(*smooth(x_es, y_es), color=COLORS["tertiary_dark"], lw=1.2, ls="--",
        dash_capstyle="round", zorder=3)

# Deep learning: the new paradigm (dotted, lime-dark).
x_dl, y_dl = series(deep, start=START["deep"])
ax.plot(*smooth(x_dl, y_dl), color=COLORS["secondary_dark"], lw=1.4, ls=":",
        dash_capstyle="round", zorder=3)

# Machine learning: the bridge between paradigms (dash-dot, darkened slate).
ML_COLOR = "#4a4e69"  # darkened neutral slate — distinct from the other three
x_ml, y_ml = series(ml, start=START["ml"])
ax.plot(*smooth(x_ml, y_ml), color=ML_COLOR, lw=1.3, ls="-.",
        dash_capstyle="round", zorder=3)

# ── Direct line labels at the right end (no legend box) ──
# The three modern curves crowd together at the top right. The tall y-axis lets
# us fan their labels out with big vertical gaps; leaders are drawn in the same
# top-to-bottom order as the curve endpoints (AI > ML > DL) so they never cross
# or touch each other.
LBL = dict(va="center", ha="left", fontsize=9, linespacing=0.95)
LEADER = lambda c: dict(arrowstyle="-", color=c, lw=0.6, shrinkA=2, shrinkB=4)
ax.annotate("artificial\nintelligence", xy=(2025, ai[2025]), xytext=(2029.5, 120000),
            color=COLORS["primary_dark"], arrowprops=LEADER(COLORS["primary_dark"]), **LBL)
ax.annotate("machine\nlearning", xy=(2025, ml[2025]), xytext=(2029.5, 14000),
            color=ML_COLOR, arrowprops=LEADER(ML_COLOR), **LBL)
ax.annotate("deep\nlearning", xy=(2025, deep[2025]), xytext=(2029.5, 2200),
            color=COLORS["secondary_dark"], arrowprops=LEADER(COLORS["secondary_dark"]), **LBL)
ax.text(2029.0, expert[2025], "expert\nsystems", color=COLORS["tertiary_dark"], **LBL)

# ── Axes ──
ax.set_xlim(1958, 2040)
ax.set_ylim(Y_FLOOR, 200000)
ax.set_xlabel("year")
ax.set_ylabel("publications per year (log scale)")
ax.set_xticks([1960, 1970, 1980, 1990, 2000, 2010, 2020])
ax.set_yticks([1, 10, 100, 1000, 10000])
ax.set_yticklabels(["1", "10", "100", "1000", "10000"])

# ── Milestone annotations: full-height faint vertical lines, with their text
#    labels placed in the top margin above every curve so they never collide. ──
#   yr, label, vertical offset (axes fraction above top) — each label is
#   horizontally centred on its own line; MYCIN (1975) and INTERNIST-1 (1982)
#   are staggered in height so their text never overlaps.
milestones = [
    (1975, "MYCIN",       0.075),
    (1982, "INTERNIST-1", 0.015),
    (2012, "AlexNet",     0.015),
    (2022, "ChatGPT",     0.015),
]
for yr, lab, dy in milestones:
    ax.axvline(yr, color=COLORS["neutral"], lw=0.6, alpha=0.35, zorder=1)
    ax.text(yr, 1.0 + dy, lab, transform=ax.get_xaxis_transform(),
            va="bottom", ha="center", fontsize=7.5, color=COLORS["neutral"],
            linespacing=0.9, zorder=5)
ax.minorticks_off()

# Faint y guide only.
ax.grid(axis="y", which="major", color=COLORS["neutral"], lw=0.4, alpha=0.18)
ax.tick_params(length=3, width=0.5)

fig.tight_layout()

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "medical_ai_pubs.pdf")
fig.savefig(out, bbox_inches="tight")
print(f"wrote {out}")
