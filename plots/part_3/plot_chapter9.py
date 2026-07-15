"""Quantitative figure for Part 3, Chapter 1."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

from plots.part_3.common import (
    DEFAULT_OUTPUT,
    ProvisionalDataError,
    configure_style,
    load_visual_data,
    mark_preliminary,
    save_figure,
    semantic_colors,
)


@dataclass(frozen=True)
class StylometryPanel:
    """Raw observations and display metadata for one stylometric metric."""

    key: str
    title: str
    direction: str
    sources: tuple[str, ...]
    values: tuple[float, ...]
    statuses: tuple[str, ...]
    provenance: tuple[str, ...]
    precision: int
    limits: tuple[float, float]
    ticks: tuple[float, ...]


_SOURCE_KEYS = ("pmc_patients", "synthetic_records", "e3c")
_SOURCE_LABELS = ("PMC-Patients", "Dossiers synthétiques", "E3C")
_METRICS = (
    (
        "mauve",
        "MAUVE",
        "plus haut = plus proche",
        3,
        (0.0, 0.050),
        (0.0, 0.02, 0.04),
    ),
    ("fed", "FED", "plus bas = plus proche", 2, (0.0, 0.85), (0.0, 0.4, 0.8)),
    (
        "mmd2",
        r"MMD$^2$",
        "plus bas = plus proche",
        4,
        (0.0, 0.00105),
        (0.0, 0.0005, 0.001),
    ),
    (
        "c2st",
        "C2ST",
        "plus bas = plus proche",
        3,
        (0.48, 1.025),
        (0.5, 0.75, 1.0),
    ),
)


def prepare_stylometry(data: dict | None = None) -> tuple[StylometryPanel, ...]:
    """Load the registered stylometry observations without transforming them."""

    if data is None:
        data = load_visual_data(allow_provisional=True)
    observations = data["stylometry"]
    panels = []
    for key, title, direction, precision, limits, ticks in _METRICS:
        metric = observations[key]
        selected = tuple(metric[source] for source in _SOURCE_KEYS)
        panels.append(
            StylometryPanel(
                key=key,
                title=title,
                direction=direction,
                sources=_SOURCE_LABELS,
                values=tuple(float(item["value"]) for item in selected),
                statuses=tuple(item["status"] for item in selected),
                provenance=tuple(item["source"] for item in selected),
                precision=precision,
                limits=limits,
                ticks=ticks,
            )
        )
    return tuple(panels)


def _decimal_label(value: float, precision: int) -> str:
    return f"{value:.{precision}f}".replace(".", ",")


def _draw_panel(ax, panel: StylometryPanel, show_sources: bool) -> None:
    colors = semantic_colors()
    y_positions = (2, 1, 0)

    ax.scatter(
        panel.values,
        y_positions,
        s=38,
        color=colors["neutral"],
        edgecolor="white",
        linewidth=0.7,
        zorder=3,
    )
    for value, y_position in zip(panel.values, y_positions):
        ax.annotate(
            _decimal_label(value, panel.precision),
            (value, y_position),
            xytext=(5, 0),
            textcoords="offset points",
            ha="left",
            va="center",
            fontsize=8,
            color=colors["neutral"],
        )

    ax.set_title(panel.title, fontsize=11, fontweight="bold", pad=19)
    ax.text(
        0.5,
        1.035,
        panel.direction,
        transform=ax.transAxes,
        ha="center",
        va="bottom",
        fontsize=7.5,
        color=colors["neutral"],
    )
    ax.set_xlim(*panel.limits)
    ax.set_xticks(panel.ticks)
    ax.xaxis.set_major_formatter(
        FuncFormatter(lambda value, _position: _decimal_label(value, panel.precision))
    )
    ax.set_ylim(-0.55, 2.55)
    ax.set_yticks(y_positions, labels=panel.sources)
    ax.tick_params(
        axis="y",
        labelleft=show_sources,
        length=0 if not show_sources else 3,
    )

    ax.grid(axis="y", color=colors["neutral"], alpha=0.14, linewidth=0.6)
    ax.tick_params(axis="x", labelsize=7.5, length=3, width=0.5)
    ax.tick_params(axis="y", labelsize=8.5)
    ax.spines["left"].set_visible(False)

    if panel.key == "c2st":
        ax.axvline(
            0.5,
            color=colors["neutral"],
            linestyle=(0, (2, 2)),
            linewidth=0.8,
            alpha=0.65,
            zorder=1,
        )
        ax.text(
            0.5,
            -0.42,
            "indiscernables",
            ha="left",
            va="center",
            fontsize=6.8,
            color=colors["neutral"],
        )


def _make_figure(panels: tuple[StylometryPanel, ...]):
    fig, axes = plt.subplots(
        1,
        4,
        figsize=(7.2, 2.65),
        sharey=True,
        gridspec_kw={"wspace": 0.22},
    )
    for index, (ax, panel) in enumerate(zip(axes, panels)):
        _draw_panel(ax, panel, show_sources=index == 0)
    return fig


def build(
    output_dir: Path = DEFAULT_OUTPUT, allow_provisional: bool = False
) -> list[Path]:
    """Build Figure 6 from the tracked stylometry evidence."""

    panels = prepare_stylometry()
    provisional = any(
        status == "provisional"
        for panel in panels
        for status in panel.statuses
    )
    if provisional and not allow_provisional:
        raise ProvisionalDataError("stylometry observations remain provisional")

    configure_style()
    fig = None
    try:
        fig = _make_figure(panels)
        if provisional:
            mark_preliminary(fig)
        return save_figure(fig, "fig06_stylometry", output_dir)
    except BaseException:
        if fig is not None:
            plt.close(fig)
        raise


if __name__ == "__main__":
    for output in build():
        print(output)
