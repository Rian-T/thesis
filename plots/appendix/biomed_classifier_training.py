"""
biomed_classifier_training.py — appendix technical-report figure.

Training curve of the 20-task content-type classifier (CamemBERTv2-base):
left panel = training loss with the learning-rate schedule (linear decay, 10%
warmup) overlaid; right panel = held-out accuracy over training for a few
representative dimensions. Data read verbatim from the run's trainer_state.json
(log_history), recovered from the trained checkpoint on Jean Zay.

Run:
  uv run --with matplotlib python plots/appendix/biomed_classifier_training.py
"""
import json
import os
import sys

import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from thesis_style import COLORS, apply_style

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(os.path.dirname(HERE), "..", "research", "jz_data", "biomed",
                     "trainer_state.json")

h = json.load(open(STATE))["log_history"]
tr = [(e["step"], e["loss"], e["learning_rate"]) for e in h if "loss" in e]
ev = [(e["step"], e["eval_content_type_accuracy"],
       e["eval_medical_subfield_accuracy"], e["eval_writing_style_accuracy"])
      for e in h if "eval_content_type_accuracy" in e]

ts, loss, lr = zip(*tr)
es, acc_ct, acc_sub, acc_ws = zip(*ev)
ks = 1e-3  # steps -> thousands

apply_style()
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 3.0))

# --- left: training loss + LR schedule ---
ax1.plot([s * ks for s in ts], loss, color=COLORS["primary_dark"], lw=1.4,
         label="training loss")
ax1.set_yscale("log")
ax1.set_xlabel("training step (thousands)")
ax1.set_ylabel("training loss (log)")
axr = ax1.twinx()
axr.plot([s * ks for s in ts], [v * 1e5 for v in lr], color=COLORS["tertiary_dark"],
         lw=1.1, ls="--", label="learning rate")
axr.set_ylabel(r"learning rate ($\times 10^{-5}$)")
ax1.set_title("Training loss and schedule", fontsize=9)
l1, lab1 = ax1.get_legend_handles_labels()
l2, lab2 = axr.get_legend_handles_labels()
ax1.legend(l1 + l2, lab1 + lab2, fontsize=7, loc="upper right", frameon=False)

# --- right: held-out accuracy over training ---
ax2.plot([s * ks for s in es], acc_ct, color=COLORS["primary_dark"], lw=1.4,
         label="content type")
ax2.plot([s * ks for s in es], acc_ws, color=COLORS["secondary_dark"], lw=1.2,
         label="writing style")
ax2.plot([s * ks for s in es], acc_sub, color=COLORS["tertiary_dark"], lw=1.2,
         label="medical subfield")
ax2.set_xlabel("training step (thousands)")
ax2.set_ylabel("held-out accuracy")
ax2.set_ylim(0.4, 1.0)
ax2.set_title("Held-out accuracy", fontsize=9)
ax2.legend(fontsize=7, loc="lower right", frameon=False)

fig.tight_layout()
out = os.path.join(HERE, "biomed_classifier_training.pdf")
fig.savefig(out, bbox_inches="tight")
print(f"wrote {out}")
