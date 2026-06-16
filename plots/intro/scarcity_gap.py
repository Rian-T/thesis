"""
scarcity_gap.py — THE central scarcity figure (introduction).

Message: English has large BIOMEDICAL resources AND real CLINICAL corpora;
French has some biomedical proxies but essentially NO real, public clinical
text. The figure groups the bars into an ENGLISH block and a FRENCH block, and
within each block separates biomedical (neutral) from clinical (primary accent).
The French clinical floor is ZERO: there is no public corpus of real French
hospital notes.

UNIT-HONESTY CHOICE
-------------------
The corpora are measured in genuinely different units (abstracts / articles /
reports / notes / words). We do NOT pretend they are interchangeable: every bar
carries its own unit in its value label, and the horizontal log axis is an
order-of-magnitude reading aid (faint vertical gridlines at each power of ten),
not a claim of comparability. The caption states this.

DATA — all VERIFIED, from research/scarcity_datasets.md. biomed-fr (author's own
corpus) is deliberately EXCLUDED. No invented numbers; NOT-FOUND entries omitted.

  Block / row                       Size          Unit       kind
  ---------------------------------------------------------------------------
  EN biomedical  PubMed             29,090,670    abstracts  biomedical
  EN biomedical  PMC Open Access     7,949,676    articles   biomedical
  EN clinical    MIMIC-IV radiology  2,321,355    reports    clinical (real)
  EN clinical    MIMIC-IV discharge    331,794    notes      clinical (real)
  FR biomedical  CLEAR (technical)   2,840,003    words      biomedical
  FR biomedical  QUAERO                103,056    words      biomedical
  FR clinical    CAS (cases)           397,000    words      clinical (published-case)
  FR clinical    PARHAF (synthetic)      6,185    documents  clinical (synthetic)
  FR clinical    real public notes           0    —          none

Generates: plots/intro/scarcity_gap.pdf
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import matplotlib.pyplot as plt
from thesis_style import COLORS, apply_style

apply_style()

# ── Rows, grouped EN then FR; within each, biomedical then clinical ──────────
# kind: "bio" (neutral/secondary), "clin" (primary accent), "none" (zero, highlighted)
# (label, value, unit, kind)
# (label, value, unit, kind, description)
EN = [
    ("PubMed",             29_090_670, "abstracts", "bio",  "article abstracts"),
    ("PMC Open Access",     7_949_676, "articles",  "bio",  "full-text articles"),
    ("MIMIC-IV radiology",  2_321_355, "reports",   "clin", "real radiology reports"),
    ("MIMIC-IV discharge",    331_794, "notes",     "clin", "real discharge notes"),
]
FR = [
    ("CLEAR",               2_840_003, "words",     "bio",  "technical medical text"),
    ("QUAERO",                103_056, "words",     "bio",  "titles and drug leaflets"),
    ("CAS",                   397_000, "words",     "clin", "clinical cases from journals"),
    ("PARHAF",                  6_185, "documents", "clin", "synthetic clinical notes"),
    ("Real public notes",           0, "",          "none", "real hospital notes"),
]

C_BIO  = COLORS["neutral"]
C_CLIN = COLORS["primary_dark"]
C_NONE = COLORS["ink"]


def fmt(v, u):
    if v >= 1_000_000:
        s = f"{v/1_000_000:.2f}".rstrip("0").rstrip(".") + "M"
    elif v >= 1_000:
        s = f"{v/1_000:.1f}".rstrip("0").rstrip(".") + "k"
    else:
        s = f"{v:,}"
    return f"{s} {u}".strip()


# ── Build the y layout with a gap between the EN and FR blocks ───────────────
floor = 1e3          # left edge of bars on the log axis (a power of ten)
xmax  = 1e8
zmark = floor        # zero marker sits at the axis floor

ROW   = 1.0          # vertical step between rows (in data units)
BLOCK_GAP = 1.6      # extra space between the English and French blocks

rows = []   # (y, label, value, unit, kind, desc)
yy = 0.0
# place FR at the bottom, EN at the top → build bottom-up so first listed is highest
order = [("French",  FR), ("English", EN)]
block_spans = []
for bname, block in order:
    start = yy
    for label, v, u, kind, desc in reversed(block):
        rows.append((yy, label, v, u, kind, desc))
        yy += ROW
    block_spans.append((bname, start - 0.5 * ROW, yy - 0.5 * ROW))
    yy += BLOCK_GAP   # gap before next block

ymax = yy - BLOCK_GAP

fig, ax = plt.subplots(figsize=(8.6, 5.6))

# faint vertical gridlines at each power of ten (behind everything)
for p in range(3, 9):
    ax.axvline(10**p, color=COLORS["neutral"], lw=0.5, alpha=0.16, zorder=0)

BAR_H = 0.52
for (yi, label, v, u, kind, desc) in rows:
    if kind == "none":
        # sober zero punchline: a short upright tick at the floor + quiet italic label
        ax.plot([zmark], [yi], marker="|", ms=15, mec=C_NONE, mew=1.8,
                zorder=5, clip_on=False)
        ax.annotate("0  /  none", xy=(zmark, yi),
                    xytext=(12, 0), textcoords="offset points",
                    va="center", ha="left", fontsize=12, style="italic",
                    color=C_NONE)
    else:
        col = C_CLIN if kind == "clin" else C_BIO
        alpha = 0.92 if kind == "clin" else 0.40
        ax.barh(yi, v, left=floor, height=BAR_H, color=col, alpha=alpha,
                edgecolor="none", zorder=3)
        ax.annotate(fmt(v, u), xy=(v, yi), xytext=(8, 0),
                    textcoords="offset points", va="center", ha="left",
                    fontsize=11, color=COLORS["ink"])

ax.set_xscale("log")
# generous right margin so the longest value label never clips the frame
ax.set_xlim(floor, xmax * 6)
ax.set_ylim(-0.9, ymax + 0.9)

# y tick labels: dataset names
yticks  = [r[0] for r in rows]
ylabels = [r[1] for r in rows]
ax.set_yticks(yticks)
ax.set_yticklabels(ylabels, fontsize=12)

# colour the clinical tick labels to match their bars (none stays ink)
for tick, (_, _, _, _, kind, _) in zip(ax.get_yticklabels(), rows):
    if kind == "clin":
        tick.set_color(C_CLIN)
    elif kind == "none":
        tick.set_color(C_NONE)

# quiet italic sub-labels (description) sitting clearly below each row name
for (yi, label, v, u, kind, desc) in rows:
    ax.annotate(desc, xy=(0, yi), xytext=(-16, -14),
                textcoords="offset points",
                xycoords=("axes fraction", "data"),
                va="center", ha="right", fontsize=9, style="italic",
                color=COLORS["neutral"], annotation_clip=False)

# block labels (English / French) at the left margin, rotated, with a quiet rule
for bname, lo, hi in block_spans:
    mid = (lo + hi) / 2
    ax.annotate(bname, xy=(0, mid), xytext=(-150, 0),
                textcoords="offset points", xycoords=("axes fraction", "data"),
                va="center", ha="center", rotation=90,
                fontsize=13.5, color=COLORS["ink"],
                annotation_clip=False)
    # faint vertical rule spanning the block
    ax.annotate("", xy=(-0.020, hi), xytext=(-0.020, lo),
                xycoords=("axes fraction", "data"),
                annotation_clip=False,
                arrowprops=dict(arrowstyle="-", color=COLORS["neutral"],
                                lw=1.2, alpha=0.6))

# axis cosmetics — minimal chrome
ax.spines["left"].set_visible(False)
ax.spines["bottom"].set_color(COLORS["neutral"])
ax.spines["bottom"].set_alpha(0.5)
ax.tick_params(axis="y", length=0, pad=16)
ax.set_xlabel("corpus size   (log scale; unit varies, see each bar)",
              fontsize=10.5, color=COLORS["neutral"], labelpad=8)
ax.tick_params(axis="x", labelsize=10, colors=COLORS["neutral"])

# tiny frameless colour key, top-right
from matplotlib.patches import Patch
handles = [
    Patch(facecolor=C_BIO,  alpha=0.40, edgecolor="none", label="biomedical"),
    Patch(facecolor=C_CLIN, alpha=0.92, edgecolor="none", label="clinical"),
]
leg = ax.legend(handles=handles, loc="lower right", frameon=False,
                bbox_to_anchor=(1.0, 0.93),
                fontsize=10.5, handlelength=1.1, handleheight=1.1,
                labelcolor=COLORS["ink"], borderaxespad=0.0,
                labelspacing=0.6)

fig.patch.set_facecolor("white")
ax.set_facecolor("white")

fig.subplots_adjust(left=0.30, right=0.97, top=0.97, bottom=0.11)
out = os.path.join(os.path.dirname(__file__), "scarcity_gap.pdf")
fig.savefig(out, bbox_inches="tight", facecolor="white")
print("wrote", out)
