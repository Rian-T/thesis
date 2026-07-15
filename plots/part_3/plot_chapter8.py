"""Quantitative figures for Part 3, Chapter 2 (open vocabulary)."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter

from plots.part_3.common import (
    DEFAULT_OUTPUT,
    ProvisionalDataError,
    configure_style,
    load_visual_data,
    mark_preliminary,
    result_value,
    save_figure,
    semantic_colors,
)


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
    "first": "1re ligne\nde traitement",
    "other": "autres lignes\nde traitement",
    "news": "dernières nouvelles",
    "second": "2e ligne\nde traitement",
    "demography": "démographie",
    "imaging": "imagerie",
    "antecedents": "antécédents",
    "history": "histoire de\nla maladie",
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
                label="v3b généraliste",
                kind="généraliste",
                ecrf=result_value(
                    "ecrf", "MC-bio-gliner (v3b)", "zero_shot", "value"
                ),
                parhaf=result_value(
                    "parhaf", "MC-bio-gliner (v3b)", "zero_shot", "value"
                ),
            ),
            TradeoffPoint(
                label="FROMV3B spécialiste",
                kind="spécialisé",
                ecrf=result_value(
                    "ecrf", "MC-bio-gliner (v3b)", "capstone", "value"
                ),
                parhaf=float(tradeoff_node["fromv3b_parhaf"]["value"]),
            ),
            TradeoffPoint(
                label="v3e généraliste",
                kind="généraliste",
                ecrf=float(tradeoff_node["v3e_ecrf"]["value"]),
                parhaf=result_value(
                    "parhaf", "MC-bio-gliner (v3e)", "zero_shot", "value"
                ),
            ),
            TradeoffPoint(
                label="MIX6 spécialiste",
                kind="spécialisé",
                ecrf=result_value(
                    "ecrf", "MC-bio-gliner (MIX)", "capstone", "value"
                ),
                parhaf=float(tradeoff_node["mix6_parhaf"]["value"]),
            ),
        ),
    )
    return supervision, novel_types, tradeoff


def _decimal(value: float, precision: int = 3) -> str:
    return f"{value:.{precision}f}".replace(".", ",")


def _style_numeric_axis(ax) -> None:
    colors = semantic_colors()
    ax.grid(axis="x", color=colors["neutral"], alpha=0.14, linewidth=0.6)
    ax.tick_params(axis="both", labelsize=8, width=0.5, length=3)
    ax.xaxis.set_major_formatter(
        FuncFormatter(lambda value, _position: _decimal(value, 2))
    )


def _make_supervision_figure(data: SupervisionData):
    colors = semantic_colors()
    fig, (global_ax, section_ax) = plt.subplots(
        1,
        2,
        figsize=(5.5, 4.0),
        layout="none",
        gridspec_kw={"width_ratios": (0.78, 2.22), "wspace": 0.48},
    )
    fig.subplots_adjust(
        left=0.20,
        right=0.98,
        bottom=0.19,
        top=0.89,
        wspace=0.62,
    )

    global_labels = ("complet", "sans clinique", "biomédical\napparié")
    global_colors = (colors["encoder"], colors["failure"], colors["neutral"])
    y_positions = (2, 1, 0)
    global_ax.barh(
        y_positions,
        data.global_values,
        height=0.48,
        color=global_colors,
        alpha=0.85,
        edgecolor="white",
        linewidth=0.6,
    )
    for value, y_position in zip(data.global_values, y_positions):
        global_ax.annotate(
            _decimal(value),
            (value, y_position),
            xytext=(3, 0),
            textcoords="offset points",
            ha="left",
            va="center",
            fontsize=8,
        )
    global_ax.set_yticks(y_positions, labels=global_labels)
    global_ax.set_xlim(0, 0.24)
    global_ax.set_title(
        f"Global · {data.n_documents} documents",
        fontsize=9.5,
        fontweight="bold",
        pad=9,
    )
    global_ax.spines["left"].set_visible(False)
    global_ax.tick_params(axis="y", length=0, labelsize=7.6)
    _style_numeric_axis(global_ax)

    section_positions = list(range(len(data.sections) - 1, -1, -1))
    for item, y_position in zip(data.sections, section_positions):
        section_ax.plot(
            (item.no_clinical, item.full),
            (y_position, y_position),
            color=colors["neutral"],
            alpha=0.45,
            linewidth=1.1,
            zorder=1,
        )
        section_ax.scatter(
            item.full,
            y_position,
            s=31,
            color=colors["encoder"],
            edgecolor="white",
            linewidth=0.6,
            zorder=3,
        )
        section_ax.scatter(
            item.no_clinical,
            y_position,
            s=31,
            color=colors["failure"],
            edgecolor="white",
            linewidth=0.6,
            zorder=3,
        )
        section_ax.annotate(
            _decimal(item.full),
            (item.full, y_position),
            xytext=(4, 3),
            textcoords="offset points",
            ha="left",
            va="bottom",
            fontsize=7.3,
            color=colors["encoder"],
        )
        section_ax.annotate(
            _decimal(item.no_clinical),
            (item.no_clinical, y_position),
            xytext=(4, -3),
            textcoords="offset points",
            ha="left",
            va="top",
            fontsize=7.3,
            color=colors["failure"],
            fontweight="bold" if item.key in {"first", "other", "second"} else None,
        )

    section_ax.set_yticks(
        section_positions,
        labels=[
            f"{item.label}\n$n={item.n_gold_cells}$" for item in data.sections
        ],
    )
    section_ax.set_xlim(-0.012, 0.43)
    section_ax.set_xticks((0.0, 0.2))
    section_ax.set_ylim(-0.65, len(data.sections) - 0.35)
    section_ax.set_title(
        "Sections · complet vs sans clinique",
        fontsize=9.5,
        fontweight="bold",
        pad=9,
    )
    section_ax.spines["left"].set_visible(False)
    section_ax.tick_params(axis="y", length=0, labelsize=7.2)
    _style_numeric_axis(section_ax)
    fig.supxlabel("value-micro-$F_1$", y=0.055, fontsize=8.5)
    return fig


def _make_novel_types_figure(data: NovelTypeData):
    colors = semantic_colors()
    fig, ax = plt.subplots(figsize=(5.5, 2.65))
    regimes = ("types communs", "types nouveaux")
    y_positions = (1, 0)
    for index, (regime, y_position) in enumerate(zip(regimes, y_positions)):
        medembed = data.medembed[index]
        mcbio = data.mcbio[index]
        ax.plot(
            (mcbio, medembed),
            (y_position, y_position),
            color=colors["neutral"],
            alpha=0.5,
            linewidth=1.3,
            zorder=1,
        )
        ax.scatter(
            mcbio,
            y_position,
            s=48,
            color=colors["neutral"],
            edgecolor="white",
            linewidth=0.7,
            zorder=3,
        )
        ax.scatter(
            medembed,
            y_position,
            s=48,
            color=colors["encoder"],
            edgecolor="white",
            linewidth=0.7,
            zorder=3,
        )
        ax.annotate(
            f"MC-bio  {_decimal(mcbio)}",
            (mcbio, y_position),
            xytext=(-5, -10),
            textcoords="offset points",
            ha="right",
            va="top",
            fontsize=8,
            color=colors["neutral"],
        )
        ax.annotate(
            f"MedEmbed  {_decimal(medembed)}",
            (medembed, y_position),
            xytext=(5, 9),
            textcoords="offset points",
            ha="left",
            va="bottom",
            fontsize=8,
            color=colors["encoder"],
            fontweight="bold",
        )
        ax.text(
            (mcbio + medembed) / 2,
            y_position + 0.14,
            f"$\\Delta$ +{_decimal(medembed - mcbio)}",
            ha="center",
            va="bottom",
            fontsize=7.5,
            color=colors["neutral"],
        )
        ax.text(
            0.292,
            y_position,
            f"{regime}\n{data.queries[index]} requêtes",
            ha="left",
            va="center",
            fontsize=8.3,
        )

    ax.set_xlim(0.29, 0.55)
    ax.set_ylim(-0.45, 1.43)
    ax.set_yticks([])
    ax.set_xlabel(data.metric, fontsize=9)
    ax.set_title(
        "Comparaison A/B du backbone contrastif",
        fontsize=10.5,
        fontweight="bold",
        pad=9,
    )
    ax.text(
        0.5,
        -0.28,
        "préférence du juge · pas une exactitude médicale humaine",
        transform=ax.transAxes,
        ha="center",
        va="top",
        fontsize=7.5,
        color=colors["neutral"],
    )
    ax.spines["left"].set_visible(False)
    _style_numeric_axis(ax)
    return fig


def _make_tradeoff_figure(data: TradeoffData):
    colors = semantic_colors()
    fig, ax = plt.subplots(figsize=(5.5, 3.45))
    label_offsets = {
        "v3b généraliste": (7, 7),
        "FROMV3B spécialiste": (-7, 8),
        "v3e généraliste": (7, -11),
        "MIX6 spécialiste": (-7, 8),
    }
    for point in data.points:
        is_generalist = point.kind == "généraliste"
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
            f"{point.label}\n({_decimal(point.ecrf)} ; {_decimal(point.parhaf)})",
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
    ax.set_xlabel("eCRF value-micro-$F_1$  (spécialisation)", fontsize=9)
    ax.set_ylabel("PARHAF NER value-micro-$F_1$  (ouverture)", fontsize=9)
    ax.set_title(
        "Spécialisation du formulaire vs transfert ouvert",
        fontsize=10.5,
        fontweight="bold",
        pad=9,
    )
    legend_handles = (
        Line2D(
            [],
            [],
            marker="o",
            linestyle="None",
            markerfacecolor="white",
            markeredgecolor=colors["encoder"],
            markeredgewidth=1.5,
            label="généraliste",
        ),
        Line2D(
            [],
            [],
            marker="o",
            linestyle="None",
            markerfacecolor=colors["structure"],
            markeredgecolor="white",
            label="spécialisé",
        ),
    )
    ax.legend(
        handles=legend_handles,
        loc="upper right",
        frameon=False,
        fontsize=7.5,
        ncols=2,
    )
    ax.text(
        0.5,
        -0.22,
        "points indépendants · ascendance des checkpoints non auditée",
        transform=ax.transAxes,
        ha="center",
        va="top",
        fontsize=7.2,
        color=colors["neutral"],
    )
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
    """Create the three provisional figures without saving them."""

    configure_style()
    supervision, novel_types, tradeoff = prepare_data()
    return (
        _make_supervision_figure(supervision),
        _make_novel_types_figure(novel_types),
        _make_tradeoff_figure(tradeoff),
    )


def build(
    output_dir: Path = DEFAULT_OUTPUT, allow_provisional: bool = False
) -> list[Path]:
    """Build Figures 8–10, gating all provisional evidence atomically."""

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
            _make_supervision_figure(supervision),
            "fig08_supervision_signal",
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
            if _is_provisional(chapter):
                mark_preliminary(fig)
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
