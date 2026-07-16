"""Quantitative figures for Part 3, Chapter 2 (open vocabulary)."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

from plots.part_3.common import (
    DEFAULT_OUTPUT,
    ProvisionalDataError,
    configure_style,
    load_visual_data,
    result_value,
    save_figure,
    semantic_colors,
)
from plots.thesis_style import COLORS


@dataclass(frozen=True)
class SectionComparison:
    key: str
    label: str
    full: float
    no_clinical: float
    n_gold_cells: int


@dataclass(frozen=True)
class SupervisionData:
    global_values: tuple[float, float, float]
    n_documents: int
    sections: tuple[SectionComparison, ...]


@dataclass(frozen=True)
class NovelTypeData:
    metric: str
    medembed: tuple[float, float]
    mcbio: tuple[float, float]
    queries: tuple[int, int]


@dataclass(frozen=True)
class TradeoffPoint:
    label: str
    kind: str
    ecrf: float
    parhaf: float


@dataclass(frozen=True)
class TradeoffData:
    points: tuple[TradeoffPoint, ...]


_SECTION_LABELS = {
    "first": "First treatment line",
    "other": "Other treatment lines",
    "news": "Latest status",
    "second": "Second treatment line",
    "demography": "Demographics",
    "imaging": "Imaging",
    "antecedents": "Medical history",
    "history": "Disease history",
}


def _is_provisional(node) -> bool:
    if isinstance(node, dict) and "value" in node:
        return node["status"] == "provisional"
    if isinstance(node, dict):
        return any(_is_provisional(child) for child in node.values())
    if isinstance(node, list):
        return any(_is_provisional(child) for child in node)
    return False


def prepare_data(
    data: dict | None = None,
) -> tuple[SupervisionData, NovelTypeData, TradeoffData]:
    """Load Chapter 8 evidence without inferring or interpolating endpoints."""

    if data is None:
        data = load_visual_data(allow_provisional=True)
    chapter = data["chapter8"]

    supervision_node = chapter["supervision_signal"]
    global_node = supervision_node["global"]
    sections = []
    for key, values in supervision_node["sections"].items():
        sections.append(
            SectionComparison(
                key=key,
                label=_SECTION_LABELS[key],
                full=float(values["full"]["value"]),
                no_clinical=float(values["no_clinical"]["value"]),
                n_gold_cells=int(values["full"]["n"]),
            )
        )
    sections.sort(key=lambda item: item.full - item.no_clinical, reverse=True)
    supervision = SupervisionData(
        global_values=tuple(
            float(global_node[key]["value"])
            for key in ("full", "no_clinical", "biomed_matched")
        ),
        n_documents=int(global_node["full"]["n"]),
        sections=tuple(sections),
    )

    judge = chapter["novel_types"]
    novel_types = NovelTypeData(
        metric="LLM-judge MAP",
        medembed=tuple(
            float(judge["v3c_medembed_e1"][regime]["value"])
            for regime in ("common", "novel")
        ),
        mcbio=tuple(
            float(judge["v3c_mcbio_e1"][regime]["value"])
            for regime in ("common", "novel")
        ),
        queries=tuple(
            int(judge["v3c_medembed_e1"][regime]["n"])
            for regime in ("common", "novel")
        ),
    )

    tradeoff_node = chapter["specialization_tradeoff"]
    tradeoff = TradeoffData(
        points=(
            TradeoffPoint(
                label="Generalist A",
                kind="generalist",
                ecrf=result_value(
                    "ecrf", "MC-bio-gliner (v3b)", "zero_shot", "value"
                ),
                parhaf=result_value(
                    "parhaf", "MC-bio-gliner (v3b)", "zero_shot", "value"
                ),
            ),
            TradeoffPoint(
                label="eCRF-only specialization",
                kind="specialist",
                ecrf=result_value(
                    "ecrf", "MC-bio-gliner (v3b)", "capstone", "value"
                ),
                parhaf=float(tradeoff_node["fromv3b_parhaf"]["value"]),
            ),
            TradeoffPoint(
                label="Generalist B",
                kind="generalist",
                ecrf=float(tradeoff_node["v3e_ecrf"]["value"]),
                parhaf=result_value(
                    "parhaf", "MC-bio-gliner (v3e)", "zero_shot", "value"
                ),
            ),
            TradeoffPoint(
                label="Mixed-supervision specialization",
                kind="specialist",
                ecrf=result_value(
                    "ecrf", "MC-bio-gliner (MIX)", "capstone", "value"
                ),
                parhaf=float(tradeoff_node["mix6_parhaf"]["value"]),
            ),
        ),
    )
    return supervision, novel_types, tradeoff


def _decimal(value: float, precision: int = 3) -> str:
    return f"{value:.{precision}f}"


def _style_numeric_axis(ax) -> None:
    colors = semantic_colors()
    ax.grid(axis="x", color=colors["neutral"], alpha=0.14, linewidth=0.6)
    ax.tick_params(axis="both", labelsize=8, width=0.5, length=3)
    ax.xaxis.set_major_formatter(
        FuncFormatter(lambda value, _position: _decimal(value, 2))
    )


def _make_global_supervision_figure(data: SupervisionData):
    colors = semantic_colors()
    fig, ax = plt.subplots(figsize=(5.5, 1.72))
    global_labels = (
        "Full corpus",
        "Without clinical text",
        "Biomedical control",
    )
    global_colors = (colors["encoder"], colors["failure"], colors["neutral"])
    y_positions = (2, 1, 0)
    for value, y_position, color in zip(
        data.global_values, y_positions, global_colors
    ):
        ax.plot((0, value), (y_position, y_position), color=color, linewidth=1.2)
        ax.scatter(value, y_position, s=42, color=color, zorder=3)
        ax.annotate(
            _decimal(value),
            (value, y_position),
            xytext=(6, 0),
            textcoords="offset points",
            ha="left",
            va="center",
            fontsize=8.5,
            color=color,
        )
    ax.set_yticks(y_positions, labels=global_labels)
    ax.set_xlim(0, 0.235)
    ax.set_xticks((0.0, 0.1, 0.2))
    ax.set_xlabel("value-micro-$F_1$", fontsize=9)
    ax.spines["left"].set_visible(False)
    _style_numeric_axis(ax)
    ax.tick_params(axis="y", length=0, labelsize=8.5)
    return fig


def _make_section_supervision_figure(data: SupervisionData):
    """Fused dumbbell: a Global header row on top, then per-section dumbbells
    sorted by the full/without-clinical gap (B3)."""

    fig, ax = plt.subplots(figsize=(5.5, 4.0))

    n_sections = len(data.sections)
    gap_above_global = 1.4
    global_y = n_sections - 1 + gap_above_global

    def _dumbbell(low, high, y):
        ax.plot(
            (low, high),
            (y, y),
            color=COLORS["neutral"],
            alpha=0.35,
            linewidth=2.2,
            solid_capstyle="round",
            zorder=1,
        )

    # Global header row: full / without-clinical / biomedical control.
    full, no_clinical, biomed = data.global_values
    _dumbbell(min(full, no_clinical, biomed), max(full, no_clinical, biomed), global_y)
    ax.scatter(biomed, global_y, s=44, color=COLORS["neutral"],
               edgecolor="white", linewidth=0.6, zorder=3)
    ax.scatter(no_clinical, global_y, s=44, color=COLORS["tertiary_dark"],
               edgecolor="white", linewidth=0.6, zorder=3)
    ax.scatter(full, global_y, s=44, color=COLORS["primary"],
               edgecolor="white", linewidth=0.6, zorder=3)

    # Per-section dumbbells, largest gap on top.
    section_positions = list(range(n_sections - 1, -1, -1))
    for item, y_position in zip(data.sections, section_positions):
        _dumbbell(
            min(item.no_clinical, item.full),
            max(item.no_clinical, item.full),
            y_position,
        )
        ax.scatter(item.no_clinical, y_position, s=40, color=COLORS["tertiary_dark"],
                   edgecolor="white", linewidth=0.6, zorder=3)
        ax.scatter(item.full, y_position, s=40, color=COLORS["primary"],
                   edgecolor="white", linewidth=0.6, zorder=3)

    y_ticks = section_positions + [global_y]
    y_labels = [item.label for item in data.sections] + ["Global"]
    ax.set_yticks(y_ticks, labels=y_labels)

    ax.set_xlim(-0.012, 0.43)
    ax.set_xticks((0.0, 0.1, 0.2, 0.3, 0.4))
    ax.set_ylim(-0.65, global_y + 0.6)
    ax.set_xlabel("value-micro-$F_1$", fontsize=9)
    ax.spines["left"].set_visible(False)
    ax.xaxis.set_major_formatter(
        FuncFormatter(lambda value, _position: _decimal(value, 2))
    )
    ax.grid(axis="x", color=COLORS["neutral"], alpha=0.2, linestyle=":", linewidth=0.6)
    ax.tick_params(axis="x", labelsize=8, width=0.5, length=3)
    ax.tick_params(axis="y", length=0, labelsize=8)

    ax.scatter([], [], s=40, color=COLORS["primary"], label="Full corpus")
    ax.scatter([], [], s=40, color=COLORS["tertiary_dark"], label="Without clinical text")
    ax.scatter([], [], s=40, color=COLORS["neutral"], label="Biomedical control")
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    return fig


def _make_novel_types_figure(data: NovelTypeData):
    """Compact dumbbell: MedEmbed vs ModernCamemBERT-bio on familiar and
    benchmark-absent descriptions, with the gain annotated on each row (B4)."""

    fig, ax = plt.subplots(figsize=(4.2, 1.9))
    regimes = ("Familiar\ndescriptions", "Benchmark-absent\ndescriptions")
    y_positions = (1, 0)
    for index, (regime, y_position) in enumerate(zip(regimes, y_positions)):
        medembed = data.medembed[index]
        mcbio = data.mcbio[index]
        ax.plot(
            (mcbio, medembed),
            (y_position, y_position),
            color=COLORS["neutral"],
            alpha=0.4,
            linewidth=2.4,
            solid_capstyle="round",
            zorder=1,
        )
        ax.scatter(
            mcbio,
            y_position,
            s=46,
            color=COLORS["neutral"],
            edgecolor="white",
            linewidth=0.7,
            zorder=3,
        )
        ax.scatter(
            medembed,
            y_position,
            s=82,
            color=COLORS["primary"],
            edgecolor="white",
            linewidth=0.7,
            zorder=4,
        )
        # Endpoint values, kept small and below the markers.
        ax.annotate(
            _decimal(mcbio),
            (mcbio, y_position),
            xytext=(0, -9),
            textcoords="offset points",
            ha="center",
            va="top",
            fontsize=7,
            color=COLORS["neutral"],
        )
        ax.annotate(
            _decimal(medembed),
            (medembed, y_position),
            xytext=(0, -9),
            textcoords="offset points",
            ha="center",
            va="top",
            fontsize=7,
            color=COLORS["primary_dark"],
        )
        # The gain, centred above the dumbbell.
        gain = medembed - mcbio
        ax.annotate(
            f"$+{gain:.3f}$",
            ((mcbio + medembed) / 2, y_position),
            xytext=(0, 8),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=8,
            fontweight="bold",
            color=COLORS["primary_dark"],
        )
    ax.set_xlim(0.315, 0.545)
    ax.set_ylim(-0.55, 1.55)
    ax.set_yticks(y_positions, labels=regimes)
    ax.set_xticks((0.35, 0.40, 0.45, 0.50))
    ax.set_xlabel(data.metric, fontsize=9)
    ax.spines["left"].set_visible(False)
    ax.xaxis.set_major_formatter(
        FuncFormatter(lambda value, _position: _decimal(value, 2))
    )
    ax.grid(axis="x", color=COLORS["neutral"], alpha=0.2, linestyle=":", linewidth=0.6)
    ax.tick_params(axis="x", labelsize=8, width=0.5, length=3)
    ax.tick_params(axis="y", length=0, labelsize=8, pad=6)
    ax.scatter([], [], s=82, color=COLORS["primary"], label="MedEmbed")
    ax.scatter([], [], s=46, color=COLORS["neutral"], label="ModernCamemBERT-bio")
    ax.legend(frameon=False, fontsize=7.5, loc="upper center",
              bbox_to_anchor=(0.5, 1.02), ncol=2, columnspacing=1.2,
              handletextpad=0.4)
    return fig


def _make_tradeoff_figure(data: TradeoffData):
    colors = semantic_colors()
    fig, ax = plt.subplots(figsize=(5.5, 3.45))
    label_offsets = {
        "Generalist A": (7, 7),
        "eCRF-only specialization": (-7, 8),
        "Generalist B": (7, -11),
        "Mixed-supervision specialization": (-7, 8),
    }
    for point in data.points:
        is_generalist = point.kind == "generalist"
        color = colors["encoder"] if is_generalist else colors["structure"]
        ax.scatter(
            point.ecrf,
            point.parhaf,
            s=62,
            facecolor="white" if is_generalist else color,
            edgecolor=color if is_generalist else "white",
            linewidth=1.6 if is_generalist else 0.7,
            zorder=3,
        )
        x_offset, y_offset = label_offsets[point.label]
        ax.annotate(
            point.label,
            (point.ecrf, point.parhaf),
            xytext=(x_offset, y_offset),
            textcoords="offset points",
            ha="left" if x_offset > 0 else "right",
            va="bottom" if y_offset > 0 else "top",
            fontsize=7.5,
            color=color,
        )

    ax.set_xlim(0.13, 0.70)
    ax.set_ylim(-0.005, 0.30)
    ax.set_xlabel("eCRF value-micro-$F_1$", fontsize=9)
    ax.set_ylabel("PARHAF NER value-micro-$F_1$", fontsize=9)
    ax.grid(color=colors["neutral"], alpha=0.14, linewidth=0.6)
    ax.tick_params(axis="both", labelsize=8, width=0.5, length=3)
    ax.xaxis.set_major_formatter(
        FuncFormatter(lambda value, _position: _decimal(value, 2))
    )
    ax.yaxis.set_major_formatter(
        FuncFormatter(lambda value, _position: _decimal(value, 2))
    )
    return fig


def make_preview_figures():
    """Create the four provisional figures without saving them."""

    configure_style()
    supervision, novel_types, tradeoff = prepare_data()
    return (
        _make_global_supervision_figure(supervision),
        _make_section_supervision_figure(supervision),
        _make_novel_types_figure(novel_types),
        _make_tradeoff_figure(tradeoff),
    )


def build(
    output_dir: Path = DEFAULT_OUTPUT, allow_provisional: bool = False
) -> list[Path]:
    """Build the Chapter 8 figures, gating provisional evidence atomically."""

    data = load_visual_data(allow_provisional=True)
    chapter = data["chapter8"]
    if _is_provisional(chapter) and not allow_provisional:
        raise ProvisionalDataError(
            "Chapter 8 principal observations remain provisional"
        )

    configure_style()
    supervision, novel_types, tradeoff = prepare_data(data)
    figures = (
        (
            _make_global_supervision_figure(supervision),
            "fig08_global_supervision",
        ),
        (
            _make_section_supervision_figure(supervision),
            "fig08_section_supervision",
        ),
        (_make_novel_types_figure(novel_types), "fig09_novel_types"),
        (
            _make_tradeoff_figure(tradeoff),
            "fig10_specialization_tradeoff",
        ),
    )
    outputs = []
    try:
        for fig, stem in figures:
            outputs.extend(save_figure(fig, stem, output_dir))
        return outputs
    except BaseException:
        for fig, _stem in figures:
            plt.close(fig)
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-provisional", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    for output in build(args.output_dir, args.allow_provisional):
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
