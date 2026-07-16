"""Figure 12: current encoder/LLM capstone comparison."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import NullLocator

from plots.part_3.common import (
    DEFAULT_OUTPUT,
    ProvisionalDataError,
    configure_style,
    load_visual_data,
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


@dataclass(frozen=True)
class DataEfficiencyCurve:
    training_records: tuple[int, ...]
    value_f1: tuple[float, ...]


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


def prepare_data_efficiency(data: dict | None = None) -> DataEfficiencyCurve:
    if data is None:
        data = load_visual_data(allow_provisional=True)
    observations = data["data_efficiency"]
    training_records = (10, 50, 100, 500, 1540)
    return DataEfficiencyCurve(
        training_records=training_records,
        value_f1=tuple(
            float(observations[f"train_{size}"]["value"])
            for size in training_records
        ),
    )


def _label_point(
    ax, x: float, y: float, value: float, color: str, y_offset: float = 8
) -> None:
    ax.annotate(
        f"{value:.3f}",
        (x, y),
        xytext=(0, y_offset),
        textcoords="offset points",
        ha="center",
        va="bottom" if y_offset >= 0 else "top",
        fontsize=8.5,
        color=color,
    )


# Field-competition slopegraph values (value-F1, before -> after).
# Self-contained on purpose: these are the canonical train-on-test-free
# numbers and must not be coupled to the shared capstone JSON node that
# also feeds fig12_final_comparison.
DECODING_SERIES = (
    {
        "label": "150M encoder",
        "before": 0.634,
        "after": 0.640,
        "color": COLORS["primary_dark"],
        "marker": "o",
        # right label placed just below its endpoint (encoder sits lower)
        "right_va": "top",
        "right_dy": -3,
    },
    {
        "label": "Qwen3.5-9B",
        "before": 0.665,
        "after": 0.650,
        "color": COLORS["tertiary_dark"],
        "marker": "D",
        # right label placed just above its endpoint (Qwen sits higher)
        "right_va": "bottom",
        "right_dy": 3,
    },
)


def _draw_trajectory(ax) -> None:
    for series in DECODING_SERIES:
        ys = (series["before"], series["after"])
        ax.plot(
            (0, 1), ys, color=series["color"], linewidth=2.0,
            marker=series["marker"], markersize=6.0,
            markerfacecolor=series["color"], markeredgecolor="white",
            markeredgewidth=0.8, zorder=3,
        )
        # left endpoint: value only
        ax.annotate(
            f"{series['before']:.3f}",
            (0, series["before"]),
            xytext=(-6, 0),
            textcoords="offset points",
            ha="right",
            va="center",
            fontsize=8.5,
            color=series["color"],
        )
        # right endpoint: model name + value (direct labelling, no legend)
        ax.annotate(
            f"{series['label']}  {series['after']:.3f}",
            (1, series["after"]),
            xytext=(8, series["right_dy"]),
            textcoords="offset points",
            ha="left",
            va=series["right_va"],
            fontsize=8.5,
            color=series["color"],
        )

    ax.set_xticks((0, 1), ("Before competition", "After competition"))
    ax.set_xlim(-0.22, 1.55)
    ax.set_ylim(0.62, 0.68)
    ax.set_ylabel(r"Value $F_1$")
    ax.grid(axis="y", color=COLORS["neutral"], alpha=0.2, linewidth=0.6,
            linestyle=":")
    ax.tick_params(axis="both", labelsize=8, width=0.5, length=3)


def _draw_final(ax, data: CapstoneData) -> None:
    metrics = (
        (r"Value $F_1$", data.encoder.value[1], data.qwen.value[1]),
        (r"Span $F_1$", data.encoder.final_span, data.qwen.final_span),
    )
    offsets = ((0.10, -0.10), (0.10, -0.10))
    for y, ((label, encoder, qwen), (encoder_offset, qwen_offset)) in enumerate(
        zip(metrics, offsets)
    ):
        y = 1 - y
        ax.scatter(
            encoder, y + encoder_offset, s=48, marker=data.encoder.marker,
            color=data.encoder.color, edgecolor="white", linewidth=0.8,
            label=data.encoder.label if y == 1 else None, zorder=3,
        )
        ax.scatter(
            qwen, y + qwen_offset, s=44, marker=data.qwen.marker,
            color=data.qwen.color, edgecolor="white", linewidth=0.8,
            label=data.qwen.label if y == 1 else None, zorder=3,
        )
        ax.text(
            encoder + 0.006, y + encoder_offset, f"{encoder:.3f}",
            ha="left", va="center", fontsize=8.5, color=data.encoder.color,
        )
        ax.text(
            qwen + 0.006, y + qwen_offset, f"{qwen:.3f}",
            ha="left", va="center", fontsize=8.5, color=data.qwen.color,
        )
    ax.set_yticks((1, 0), labels=(metrics[0][0], metrics[1][0]))
    ax.set_xlim(0.47, 0.69)
    ax.set_ylim(-0.35, 1.35)
    ax.set_xlabel(r"$F_1$")
    ax.grid(axis="x", color=COLORS["neutral"], alpha=0.12, linewidth=0.6)
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.legend(loc="lower right", frameon=False, fontsize=8)


def _make_decoding_figure(data: CapstoneData | None = None):
    fig, ax = plt.subplots(figsize=(5.5, 2.6))
    _draw_trajectory(ax)
    return fig


def _make_final_figure(data: CapstoneData):
    fig, ax = plt.subplots(figsize=(5.5, 2.45))
    _draw_final(ax, data)
    return fig


def _make_data_efficiency_figure(data: DataEfficiencyCurve):
    fig, ax = plt.subplots(figsize=(5.5, 2.55))
    ax.plot(
        data.training_records,
        data.value_f1,
        color=COLORS["primary_dark"],
        linewidth=1.8,
        marker="o",
        markersize=6.2,
        markerfacecolor=COLORS["primary"],
        markeredgecolor="white",
        markeredgewidth=0.8,
        zorder=3,
    )
    for index, (records, score) in enumerate(
        zip(data.training_records, data.value_f1)
    ):
        horizontal_offset = -4 if index == len(data.training_records) - 1 else 0
        alignment = "right" if horizontal_offset else "center"
        ax.annotate(
            f"{score:.3f}",
            (records, score),
            xytext=(horizontal_offset, 8),
            textcoords="offset points",
            ha=alignment,
            va="bottom",
            fontsize=8.5,
            color=COLORS["primary_dark"],
        )

    ax.set_xscale("log")
    ax.set_xlim(8, 1900)
    ax.set_xticks(data.training_records)
    ax.set_xticklabels(("10", "50", "100", "500", "1,540"))
    ax.xaxis.set_minor_locator(NullLocator())
    ax.set_ylim(0, 0.72)
    ax.set_yticks((0.0, 0.2, 0.4, 0.6))
    ax.set_xlabel("Synthetic training records")
    ax.set_ylabel(r"Value $F_1$")
    ax.grid(axis="y", color=COLORS["neutral"], alpha=0.2, linewidth=0.6,
            linestyle=":")
    ax.tick_params(axis="both", labelsize=8, width=0.5, length=3)
    return fig


def make_preview_figures():
    configure_style()
    data = load_visual_data(allow_provisional=True)
    capstone = prepare_capstone(data)
    efficiency = prepare_data_efficiency(data)
    return (
        _make_decoding_figure(capstone),
        _make_final_figure(capstone),
        _make_data_efficiency_figure(efficiency),
    )


def build(output_dir: Path = DEFAULT_OUTPUT, allow_provisional: bool = False) -> list[Path]:
    source = load_visual_data(allow_provisional=True)
    data = prepare_capstone(source)
    if data.provisional and not allow_provisional:
        raise ProvisionalDataError("Figure 12 inputs remain provisional")
    efficiency = prepare_data_efficiency(source)
    configure_style()
    outputs = []
    outputs.extend(
        save_figure(
            _make_decoding_figure(data), "fig12_decoding_competition", output_dir
        )
    )
    outputs.extend(
        save_figure(_make_final_figure(data), "fig12_final_comparison", output_dir)
    )
    outputs.extend(
        save_figure(
            _make_data_efficiency_figure(efficiency),
            "fig13_data_efficiency",
            output_dir,
        )
    )
    return outputs


if __name__ == "__main__":
    for output in build():
        print(output)
