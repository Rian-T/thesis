"""
cka_mechanism.py — Chapter 5 (Beyond Masked Language Modeling) mechanism figure.

Two panels, from the held-out float64 CKA runs recovered from the project:
  (a) per-layer representational divergence (1 - CKA): the CLM-vs-MLM pair against
      a same-objective seed-noise control. The detour's mark is the early layers.
  (b) divergence during the MLM decay: it plateaus well above the seed-noise floor,
      so decaying back to MLM does not return the model to an MLM-like state
      (computational hysteresis).

Data: plots/chapter5/data/{cka_mlm_control_heldout,trajectory_decay_heldout_float64}.json
(verbatim from the run outputs; do not edit numbers).

Run:
  uv run --with matplotlib --with numpy python plots/chapter5/cka_mechanism.py
"""
import json
import os
import sys

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from thesis_style import COLORS, apply_style

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "data")

cka = json.load(open(os.path.join(D, "cka_mlm_control_heldout.json")))
traj = json.load(open(os.path.join(D, "trajectory_decay_heldout_float64.json")))["trajectory"]


def per_layer_div(node):
    pl = node["per_layer"]
    xs = sorted(int(k) for k in pl)
    return xs, [(1.0 - pl[str(i)]["mean"]) * 100 for i in xs]

lx, ref = per_layer_div(cka["reference"])   # CLM vs MLM
_,  ctl = per_layer_div(cka["control"])     # MLM seed noise

apply_style()
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 3.0))

# --- (a) per-layer divergence ---
ax1.axvspan(-0.5, 7.5, color=COLORS["neutral"], alpha=0.10, lw=0)  # early-layer band
ax1.plot(lx, ref, color=COLORS["primary_dark"], lw=1.7, marker="o", markersize=3,
         label="CLM vs MLM")
ax1.plot(lx, ctl, color=COLORS["neutral"], lw=1.2, ls="--", marker="o", markersize=2.5,
         label="MLM seed noise")
ax1.set_xlabel("layer")
ax1.set_ylabel(r"divergence (\%)")
ax1.set_title("Per-layer divergence", fontsize=9)
ax1.set_xlim(-0.5, 21.5)
ax1.legend(fontsize=7.5, loc="upper left", frameon=False)
ax1.annotate("early layers", xy=(3.5, max(ref[:8]) + 3), fontsize=7,
             color=COLORS["neutral"], ha="center")

# --- (b) divergence during decay ---
tb = np.array([p["tokens_B"] for p in traj])
dm = np.array([p["divergence_mean"] for p in traj])
ds = np.array([p.get("divergence_std", 0.0) for p in traj])
ctrl_floor = cka["control"]["mean_divergence_pct"]
ax2.fill_between(tb, dm - ds, dm + ds, color=COLORS["primary_dark"], alpha=0.15, lw=0)
ax2.plot(tb, dm, color=COLORS["primary_dark"], lw=1.7, marker="o", markersize=3)
ax2.axhline(ctrl_floor, color=COLORS["neutral"], lw=1.0, ls=":")
ax2.annotate("seed-noise floor", xy=(tb.mean(), ctrl_floor), xytext=(0, -11),
             textcoords="offset points", fontsize=7, color=COLORS["neutral"], ha="center")
ax2.set_xlabel("decay (billion tokens)")
ax2.set_ylabel(r"divergence (\%)")
ax2.set_title("During the MLM decay", fontsize=9)
ax2.set_ylim(min(ctrl_floor, dm.min()) - 4, dm.max() + 4)

fig.tight_layout()
out = os.path.join(HERE, "cka_mechanism.pdf")
fig.savefig(out, bbox_inches="tight")
print(f"wrote {out}")
