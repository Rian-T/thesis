"""
Chinchilla compute-optimal scaling: parameters and tokens rise together with compute.

ALL points are VERBATIM from Table 3 ("tab:compute") of Hoffmann et al. 2022,
"Training Compute-Optimal Large Language Models" (arXiv:2203.15556), main.tex:406-414.
Nothing is digitised from a figure: the loss curves / IsoFLOP parabolas are image-only
and are deliberately NOT reproduced. We only plot the authors' own projected
(FLOPs, parameters, tokens) rows, which directly show the headline result: for
compute-optimal training, model size and training tokens scale in equal proportion
(their fitted exponents a = b = 0.50, Approach 1).

Generates: plots/related_works/chinchilla_scaling.pdf
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator
from thesis_style import COLORS, apply_style

apply_style()

# Verbatim Table 3 (Approach 1 projections)
flops  = np.array([1.92e19, 1.21e20, 1.23e22, 5.76e23, 3.85e24,
                   9.90e24, 3.43e25, 1.27e26, 1.30e28])
params = np.array([0.4e9, 1e9, 10e9, 67e9, 175e9, 280e9, 520e9, 1e12, 10e12])
tokens = np.array([8.0e9, 20.2e9, 205.1e9, 1.5e12, 3.7e12,
                   5.9e12, 11.0e12, 21.2e12, 216.2e12])

fig, ax = plt.subplots(figsize=(5.6, 3.5))

ax.plot(flops, params, "-o", color=COLORS["primary_dark"], lw=1.7, ms=4.5,
        label="parameters", zorder=3)
ax.plot(flops, tokens, "-o", color=COLORS["secondary_dark"], lw=1.7, ms=4.5,
        label="training tokens", zorder=3)

# Gopher compute budget (the "1 Gopher unit" row, 5.76e23 FLOPs) — verbatim reference
ax.axvline(5.76e23, color=COLORS["neutral"], lw=0.7, ls=(0, (4, 3)), zorder=1)
ax.text(5.76e23, 4e14, "Gopher\nbudget", color=COLORS["neutral"], fontsize=8.5,
        ha="center", va="top", linespacing=1.0)

ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel("training compute (FLOPs)")
ax.set_ylabel("compute-optimal size")
ax.set_xlim(5e18, 5e28)
ax.set_ylim(3e8, 8e14)
ax.xaxis.set_major_locator(LogLocator(base=10, numticks=8))
ax.tick_params(length=3)

ax.legend(loc="upper left", frameon=False, handlelength=1.6, labelspacing=0.5)

fig.tight_layout()
out = os.path.join(os.path.dirname(__file__), "chinchilla_scaling.pdf")
fig.savefig(out, bbox_inches="tight")
print("wrote", out)
