"""
Vanishing / exploding gradient in recurrent networks.

This is the ANALYTICAL bound, not measured data. Pascanu, Mikolov & Bengio
(ICML 2013), "On the difficulty of training Recurrent Neural Networks", show that
the long-term contribution of the gradient is bounded by a geometric factor in the
number of backprop steps t-k:

    || dL_t/dh_t * prod_{i=k}^{t-1} dh_{i+1}/dh_i ||  <=  eta^{t-k} || dL_t/dh_t ||,

with eta < 1 a bound on the per-step Jacobian norm (their Eq. for the shrink case),
and the spectral condition: lambda_1 < 1 makes long-term components vanish,
lambda_1 > 1 lets them explode. We simply plot eta^{t-k}. Nothing here is
digitised from the paper's figures; only the eta^{t-k} law is taken from it.

Generates: plots/related_works/rnn_gradient.pdf
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import matplotlib.pyplot as plt
from thesis_style import COLORS, apply_style

apply_style()

# steps back in time (t - k)
d = np.arange(0, 41)

# eta values: < 1 vanish, = 1 stable, > 1 explode
curves = [
    (0.7,  "vanishing", COLORS["primary_dark"]),
    (0.9,  "vanishing", COLORS["primary"]),
    (1.0,  "stable",    COLORS["neutral"]),
    (1.1,  "exploding", COLORS["tertiary"]),
    (1.3,  "exploding", COLORS["tertiary_dark"]),
]

fig, ax = plt.subplots(figsize=(5.4, 3.4))

# shade the stable line region lightly
ax.axhline(1.0, color=COLORS["neutral"], lw=0.6, ls=(0, (4, 3)), zorder=1)

for eta, kind, color in curves:
    y = eta ** d
    ls = (0, (4, 3)) if kind == "stable" else "-"
    lw = 1.2 if kind == "stable" else 1.8
    ax.plot(d, y, color=color, lw=lw, ls=ls, zorder=3)
    # direct end-of-line label (Tufte: no legend box)
    if eta != 1.0:
        xi = d[-1]
        ax.annotate(rf"$\eta={eta}$",
                    xy=(xi, eta ** xi), xytext=(3, 0),
                    textcoords="offset points", va="center", ha="left",
                    color=color, fontsize=9)

ax.annotate(r"$\eta=1$", xy=(d[-1], 1.0), xytext=(3, 0),
            textcoords="offset points", va="center", ha="left",
            color=COLORS["neutral"], fontsize=9)

ax.set_yscale("log")
ax.set_xlim(0, 47)
ax.set_ylim(1e-7, 1e6)
ax.set_xlabel(r"backprop steps into the past $\;(t-k)$")
ax.set_ylabel(r"relative gradient norm $\;\eta^{\,t-k}$")

# region words, placed in the open space
ax.text(0.5, 3e-6, "gradient vanishes", color=COLORS["primary_dark"],
        fontsize=10, ha="left", va="bottom")
ax.text(0.5, 2e5, "gradient explodes", color=COLORS["tertiary_dark"],
        fontsize=10, ha="left", va="top")

ax.tick_params(length=3)
fig.tight_layout()

out = os.path.join(os.path.dirname(__file__), "rnn_gradient.pdf")
fig.savefig(out, bbox_inches="tight")
print("wrote", out)
