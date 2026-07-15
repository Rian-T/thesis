"""Figure 12: current encoder/LLM capstone comparison."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt

from plots.part_3.common import (
    DEFAULT_OUTPUT,
    ProvisionalDataError,
    configure_style,
    load_visual_data,
    mark_preliminary,
    save_figure,
)
from plots.thesis_style import COLORS


@dataclass(frozen=True)
class SystemScores:
    label: str
    value: tuple[float, float]
    final_span: float
    color: str
    marker: str


@dataclass(frozen=True)
class CapstoneData:
    encoder: SystemScores
    qwen: SystemScores
    raw_qwen_minus_encoder: float
    final_encoder_minus_qwen: float
    final_ci: tuple[float, float]
    provisional: bool


def prepare_capstone(data: dict | None = None) -> CapstoneData:
    if data is None:
        data = load_visual_data(allow_provisional=True)
    chapter = data["chapter7"]["capstone"]

    def observation(model: str, variant: str, metric: str) -> dict:
        return chapter[model][variant][metric]

    selected = [
        observation("encoder", "top1", "value_f1"),
        observation("encoder", "final", "value_f1"),
        observation("encoder", "final", "span_f1"),
        observation("qwen", "top1", "value_f1"),
        observation("qwen", "final", "value_f1"),
        observation("qwen", "final", "span_f1"),
    ]
    encoder = SystemScores(
        "150M encoder",
        (float(selected[0]["value"]), float(selected[1]["value"])),
        float(selected[2]["value"]),
        COLORS["primary_dark"],
        "o",
    )
    qwen = SystemScores(
        "Qwen3.5-9B",
        (float(selected[3]["value"]), float(selected[4]["value"])),
        float(selected[5]["value"]),
        COLORS["tertiary_dark"],
        "D",
    )
    interval = data["decoding"]["post_decoding_encoder_minus_qwen"]
    ci = (float(interval["ci95_low"]["value"]), float(interval["ci95_high"]["value"]))
    provisional = any(item["status"] == "provisional" for item in selected)
    provisional |= any(item["status"] == "provisional" for item in interval.values())
    return CapstoneData(
        encoder,
        qwen,
        qwen.value[0] - encoder.value[0],
        encoder.value[1] - qwen.value[1],
        ci,
        provisional,
    )


def _draw_trajectory(ax, data: CapstoneData) -> None:
    for system in (data.encoder, data.qwen):
        ax.plot(
            (0, 1), system.value, color=system.color, linewidth=2.2,
            marker=system.marker, markersize=6.5, markeredgecolor="white",
            markeredgewidth=0.8, label=system.label, zorder=3,
        )
    ax.text(0.5, 0.687, r"raw Qwen -- encoder gap $\approx$ 0.032", ha="center", va="bottom", fontsize=8.2, color=COLORS["neutral"])
    ax.text(0.07, 0.629, r"0.633 $\rightarrow$ 0.647  (+0.014)", color=data.encoder.color, fontsize=8.3, ha="left")
    ax.text(0.07, 0.670, r"0.665 $\rightarrow$ 0.646  (-0.019)", color=data.qwen.color, fontsize=8.3, ha="left")
    ax.set_xticks((0, 1), ("Top-1", "Top-1 + competition"))
    ax.set_xlim(-0.15, 1.15)
    ax.set_ylim(0.60, 0.695)
    ax.set_ylabel("Value-F1")
    ax.set_title("A  Before / after structural decoding", loc="left", fontsize=10.5, fontweight="bold")
    ax.grid(axis="y", color=COLORS["neutral"], alpha=0.16, linewidth=0.6)
    ax.legend(loc="lower left", frameon=False, fontsize=7.5, handlelength=1.4)


def _draw_final(ax, data: CapstoneData) -> None:
    metrics = (("Value-F1", data.encoder.value[1], data.qwen.value[1]), ("Span-F1", data.encoder.final_span, data.qwen.final_span))
    for x, (_label, encoder, qwen) in enumerate(metrics):
        ax.scatter(x - 0.07, encoder, s=48, marker=data.encoder.marker, color=data.encoder.color, edgecolor="white", linewidth=0.8, zorder=3)
        ax.scatter(x + 0.07, qwen, s=44, marker=data.qwen.marker, color=data.qwen.color, edgecolor="white", linewidth=0.8, zorder=3)
        ax.plot((x - 0.07, x + 0.07), (encoder, qwen), color=COLORS["neutral"], alpha=0.45, linewidth=0.8, zorder=1)
    ax.text(0, 0.669, r"Value-F1: difference $\approx 0$", ha="center", fontsize=8.2, color=COLORS["neutral"])
    ax.text(0, 0.630, "$\\Delta$ encoder -- Qwen = +0.0007\npaired 95 \\% CI [-0.0068, 0.0084]\n(provisional)", ha="center", va="top", fontsize=7.2, color=COLORS["neutral"])
    ax.text(1, data.qwen.final_span + 0.012, "0.554", ha="center", fontsize=7.5, color=data.qwen.color)
    ax.text(1, data.encoder.final_span - 0.018, "0.507", ha="center", fontsize=7.5, color=data.encoder.color)
    ax.set_xticks((0, 1), ("Value-F1", "Span-F1"))
    ax.set_xlim(-0.45, 1.45)
    ax.set_ylim(0.48, 0.69)
    ax.set_title("B  Final comparison", loc="left", fontsize=10.5, fontweight="bold")
    ax.grid(axis="y", color=COLORS["neutral"], alpha=0.16, linewidth=0.6)
    ax.tick_params(axis="y", labelleft=False, length=0)
    ax.spines["left"].set_visible(False)


def _make_figure(data: CapstoneData):
    fig, axes = plt.subplots(1, 2, figsize=(5.5, 3.05), gridspec_kw={"wspace": 0.28, "width_ratios": (1.12, 0.88)})
    _draw_trajectory(axes[0], data)
    _draw_final(axes[1], data)
    return fig


def make_preview_figure():
    configure_style()
    return _make_figure(prepare_capstone())


def build(output_dir: Path = DEFAULT_OUTPUT, allow_provisional: bool = False) -> list[Path]:
    data = prepare_capstone()
    if data.provisional and not allow_provisional:
        raise ProvisionalDataError("Figure 12 inputs remain provisional")
    configure_style()
    fig = None
    try:
        fig = _make_figure(data)
        if data.provisional:
            mark_preliminary(fig)
        return save_figure(fig, "fig12_capstone", output_dir)
    except BaseException:
        if fig is not None:
            plt.close(fig)
        raise


if __name__ == "__main__":
    for output in build():
        print(output)
