"""
LLaMA-13B vs GPT-3-175B on zero-shot common-sense reasoning.

ALL numbers are VERBATIM from Table 3 ("tab:commonsense") of Touvron et al. 2023,
"LLaMA: Open and Efficient Foundation Language Models" (arXiv:2302.13971),
acl2023.tex:292 (GPT-3) and :301 (LLaMA-13B). SIQA is omitted because GPT-3 has no
value in the source table (printed as "-"); nothing is invented.

The point: a 13B model trained on more tokens matches or beats a 175B model on most
of these tasks, i.e. "smaller model, more tokens" pays off.

Generates: plots/related_works/llama_vs_gpt3.pdf
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import matplotlib.pyplot as plt
from thesis_style import COLORS, apply_style

apply_style()

tasks = ["BoolQ", "PIQA", "HellaSwag", "WinoGrande", "ARC-e", "ARC-c", "OBQA"]
gpt3  = [60.5, 81.0, 78.9, 70.2, 68.8, 51.4, 57.6]   # GPT-3 175B
llama = [78.1, 80.1, 79.2, 73.0, 74.8, 52.7, 56.4]   # LLaMA 13B

x = np.arange(len(tasks))
w = 0.38

fig, ax = plt.subplots(figsize=(6.2, 3.3))

ax.bar(x - w/2, gpt3,  w, color=COLORS["tertiary"], edgecolor=COLORS["tertiary_dark"],
       linewidth=0.6, label="GPT-3 (175B)", zorder=3)
ax.bar(x + w/2, llama, w, color=COLORS["primary"], edgecolor=COLORS["primary_dark"],
       linewidth=0.6, label=r"LLaMA (13B)", zorder=3)

ax.set_xticks(x)
ax.set_xticklabels(tasks)
ax.set_ylabel("zero-shot accuracy")
ax.set_ylim(40, 90)
ax.tick_params(length=3)
ax.tick_params(axis="x", length=0)
ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.12), ncol=2,
          frameon=False, handlelength=1.3, columnspacing=2.0)

fig.tight_layout()
out = os.path.join(os.path.dirname(__file__), "llama_vs_gpt3.pdf")
fig.savefig(out, bbox_inches="tight")
print("wrote", out)
