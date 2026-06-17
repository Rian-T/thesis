"""
cka_raw_curves.py — appendix figure: raw per-layer CKA with seed spread.

Per-layer linear CKA (held-out clinical text, float64) for the CLM-vs-MLM pair and
for a same-objective MLM seed-noise control, with the band spanning the three
seeds. The complement of the divergence shown in the chapter; here the raw CKA and
its seed spread are given for reproducibility.

Run: uv run --with matplotlib python plots/chapter5/cka_raw_curves.py
"""
import json, os, sys
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from thesis_style import COLORS, apply_style

HERE = os.path.dirname(os.path.abspath(__file__))
cka = json.load(open(os.path.join(HERE, "data", "cka_mlm_control_heldout.json")))

def curve(node):
    pl = node["per_layer"]
    xs = sorted(int(k) for k in pl)
    mean = [pl[str(i)]["mean"] for i in xs]
    lo = [min(pl[str(i)]["values"]) for i in xs]
    hi = [max(pl[str(i)]["values"]) for i in xs]
    return xs, mean, lo, hi

apply_style()
fig, ax = plt.subplots(figsize=(5.8, 3.0))
for node, color, lab, ls in [
    (cka["reference"], COLORS["primary_dark"], "CLM vs MLM", "-"),
    (cka["control"],   COLORS["neutral"],      "MLM seed noise", "--"),
]:
    xs, m, lo, hi = curve(node)
    ax.fill_between(xs, lo, hi, color=color, alpha=0.15, lw=0)
    ax.plot(xs, m, color=color, lw=1.6, ls=ls, marker="o", markersize=3, label=lab)
ax.set_xlabel("layer")
ax.set_ylabel("linear CKA")
ax.set_xlim(-0.5, 21.5)
ax.legend(fontsize=8, loc="lower left", frameon=False)
fig.tight_layout()
out = os.path.join(HERE, "cka_raw_curves.pdf")
fig.savefig(out, bbox_inches="tight")
print("wrote", out)
