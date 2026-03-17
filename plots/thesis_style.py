"""
thesis_style.py — Centralized plot style for the thesis.

Single source of truth for colors, fonts, and matplotlib rcParams.
Mirrors thesis-style.sty so that LaTeX and Python figures stay in sync.

Usage:
    from plots.thesis_style import COLORS, apply_style, thesis_cmap
"""
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# ══════════════════════════════════════════════════════════════════════════════
# PALETTE  —  keep in sync with thesis-style.sty
# ══════════════════════════════════════════════════════════════════════════════

COLORS = {
    # Core palette (from \definecolor in thesis-style.sty)
    "primary":        "#A694E8",   # Lavender      — ThesisPrimary
    "primary_dark":   "#5A48A0",   # Dark lavender — ThesisPrimaryDark
    "secondary":      "#ABCC6E",   # Lime          — ThesisSecondary
    "secondary_dark": "#5F8228",   # Dark lime     — ThesisSecondaryDark
    "tertiary":       "#F1B890",   # Peach         — ThesisTertiary
    "tertiary_dark":  "#B46E3C",   # Dark peach    — ThesisTertiaryDark

    # Neutrals
    "neutral":        "#667082",   # Steel gray    — ThesisNeutral
    "ink":            "#2D2A3C",   # Dark plum     — ThesisInk
    "paper":          "#F9F7FC",   # Lavender tint — ThesisPaper
    "table_sep":      "#DCDAf0",   # Table headers — ThesisTableSep

    # Semantic (for plots)
    "baseline":       "#C25A5A",   # Muted red — dashed baseline lines
}

# ══════════════════════════════════════════════════════════════════════════════
# COLORMAPS
# ══════════════════════════════════════════════════════════════════════════════

# Sequential lavender: white → deep lavender (for heatmaps)
_LAVENDER_STOPS = ["#F9F7FC", "#DDD8F0", "#B8ADE0", "#A694E8", "#7A64C8", "#5A48A0"]
thesis_cmap = mcolors.LinearSegmentedColormap.from_list(
    "thesis_lavender", _LAVENDER_STOPS
)

# ══════════════════════════════════════════════════════════════════════════════
# RCPARAMS
# ══════════════════════════════════════════════════════════════════════════════

_RC = {
    # Font — match thesis body (TeX Gyre Pagella / Palatino)
    "text.usetex":       True,
    "font.family":       "serif",
    "font.serif":        ["TeX Gyre Pagella", "Palatino", "DejaVu Serif"],

    # Font sizes — designed for single-column thesis (~15 cm text width)
    "font.size":         11,
    "axes.labelsize":    12,
    "axes.titlesize":    14,
    "xtick.labelsize":   10,
    "ytick.labelsize":   10,
    "legend.fontsize":   10,

    # Colors
    "text.color":        COLORS["ink"],
    "axes.labelcolor":   COLORS["ink"],
    "xtick.color":       COLORS["ink"],
    "ytick.color":       COLORS["ink"],
    "axes.edgecolor":    COLORS["neutral"],

    # Spines
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "axes.linewidth":    0.6,

    # Resolution
    "figure.dpi":        300,
    "savefig.dpi":       300,
}


def apply_style():
    """Apply thesis rcParams. Call once at the top of each plot script."""
    plt.rcParams.update(_RC)
