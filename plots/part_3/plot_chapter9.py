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
_SOURCE_LABELS = ("PMC-Patients", "Synthetic records", "E3C")
_METRICS = (
    (
        "mauve",
        "MAUVE",
        "higher = closer",
        3,
        (0.0, 0.050),
        (0.0, 0.02, 0.04),
    ),
    ("fed", "FED", "lower = closer", 2, (0.0, 0.85), (0.0, 0.4, 0.8)),
    (
        "mmd2",
        r"MMD$^2$",
        "lower = closer",
        4,
        (0.0, 0.00105),
        (0.0, 0.0005, 0.001),
    ),
    (
        "c2st",
        "C2ST",
        "lower = closer",
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
    return f"{value:.{precision}f}"


# Three tones from the neutral (control-data) family: distinguishing the three
# public sources without leaving the "neutral" register the caption asks for.
_SOURCE_TONES = ("#2D2A3C", "#667082", "#98A0AE")
_SOURCE_MARKERS = ("o", "s", "^")


def _closeness_order(panel: StylometryPanel) -> tuple[int, ...]:
    """Indices of the sources ranked from closest to PARHAF to furthest."""

    closest_is_high = panel.direction.startswith("higher")
    return tuple(
        sorted(
            range(len(panel.values)),
            key=lambda index: panel.values[index],
            reverse=closest_is_high,
        )
    )


def _make_figure(panels: tuple[StylometryPanel, ...]):
    """A compact slopegraph: every source on every metric at once.

    Each metric ranks the three public sources by how close they sit to
    PARHAF (top = closest). The three distributional metrics agree; only the
    C2ST classifier reverses the order, and that disagreement reads directly
    as the crossing of the lines on the right.
    """

    colors = semantic_colors()
    sources = panels[0].sources
    x_positions = list(range(len(panels)))
    y_levels = (1.0, 0.5, 0.0)  # closest, middle, furthest

    # source_y[source_index] -> list of y over the four metrics.
    source_y: list[list[float]] = [[] for _ in sources]
    for panel in panels:
        order = _closeness_order(panel)
        for rank, source_index in enumerate(order):
            source_y[source_index].append(y_levels[rank])

    fig, ax = plt.subplots(figsize=(5.3, 2.85))

    for source_index in range(len(sources)):
        tone = _SOURCE_TONES[source_index]
        marker = _SOURCE_MARKERS[source_index]
        ys = source_y[source_index]
        ax.plot(
            x_positions,
            ys,
            color=tone,
            linewidth=1.4,
            alpha=0.9,
            zorder=2,
            solid_capstyle="round",
        )
        ax.scatter(
            x_positions,
            ys,
            s=30,
            color=tone,
            marker=marker,
            edgecolor="white",
            linewidth=0.6,
            zorder=3,
        )
        # Direct label at the left end — no legend needed.
        ax.annotate(
            sources[source_index],
            (x_positions[0], ys[0]),
            xytext=(-8, 0),
            textcoords="offset points",
            ha="right",
            va="center",
            fontsize=8,
            color=tone,
        )
        # Raw value at every node, above the marker.
        for panel, x_position, y_value in zip(panels, x_positions, ys):
            ax.annotate(
                _decimal_label(panel.values[source_index], panel.precision),
                (x_position, y_value),
                xytext=(0, 6),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=6.8,
                color=tone,
            )

    # Column headers: metric name + the direction convention.
    for panel, x_position in zip(panels, x_positions):
        ax.text(
            x_position,
            1.29,
            panel.title,
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
            color=colors["neutral"],
        )
        ax.text(
            x_position,
            1.20,
            panel.direction,
            ha="center",
            va="bottom",
            fontsize=7,
            color=colors["neutral"],
        )

    # Vertical guide rails, one per metric.
    for x_position in x_positions:
        ax.axvline(
            x_position,
            color=colors["neutral"],
            alpha=0.15,
            linewidth=0.6,
            linestyle=":",
            zorder=0,
        )

    ax.set_xlim(-0.95, len(panels) - 1 + 0.35)
    ax.set_ylim(-0.28, 1.18)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    # The one non-obvious fact the ranking hides: every C2ST score sits in a
    # razor-thin band far above chance, so all three sources are trivially
    # separable from PARHAF.
    ax.text(
        (len(panels) - 1) / 2,
        -0.26,
        r"C2ST scores all in $[0.985,\,0.991]$ — far above the $0.5$ chance line",
        ha="center",
        va="bottom",
        fontsize=7.5,
        color=colors["neutral"],
    )
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
