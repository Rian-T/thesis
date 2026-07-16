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
    """Small multiples: one panel per metric, actual values as horizontal bars.

    Each panel shows the three sources' distance to PARHAF on one metric, with
    the value printed at each bar. This reads as values, not ranks. The three
    distributional metrics agree that PMC-Patients sits closest; the C2ST panel
    reverses that order by a razor-thin margin, and its chance line at 0.5 makes
    the real conclusion visible: all three sources sit far from PARHAF.
    """

    colors = semantic_colors()
    sources = panels[0].sources
    tones = _SOURCE_TONES

    fig, axes = plt.subplots(2, 2, figsize=(6.3, 3.7))
    axes = axes.ravel()

    for col, (ax, panel) in enumerate(zip(axes, panels)):
        y_of = {i: len(sources) - 1 - i for i in range(len(sources))}
        for i, (value, tone) in enumerate(zip(panel.values, tones)):
            ax.barh(
                y_of[i], value, height=0.62, color=tone,
                edgecolor="white", linewidth=0.6, zorder=3,
            )
            ax.annotate(
                _decimal_label(value, panel.precision),
                (value, y_of[i]),
                xytext=(4, 0), textcoords="offset points",
                va="center", ha="left", fontsize=7.5, color="#2D2A3C",
            )

        ax.set_xlim(*panel.limits)
        ax.set_xticks(panel.ticks)
        ax.set_ylim(-0.6, len(sources) - 0.4)
        ax.set_yticks([y_of[i] for i in range(len(sources))])
        # source labels only on the left column, to avoid repetition
        if col % 2 == 0:
            ax.set_yticklabels(sources, fontsize=8)
        else:
            ax.set_yticklabels([])
        ax.tick_params(axis="x", labelsize=7)
        ax.tick_params(axis="y", length=0)
        ax.set_title(
            f"{panel.title}   {panel.direction}",
            fontsize=8.5, color=colors["neutral"], pad=4,
        )
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
        ax.grid(axis="x", color=colors["neutral"], alpha=0.12, linewidth=0.5)

        # C2ST: mark the 0.5 chance line so the reader sees all bars sit far above it
        if panel.key == "c2st":
            ax.axvline(0.5, color=colors["neutral"], linestyle="--",
                       linewidth=0.9, alpha=0.8, zorder=2)
            ax.annotate(
                "chance", (0.5, len(sources) - 0.5),
                xytext=(2, 0), textcoords="offset points",
                fontsize=6.8, color=colors["neutral"], ha="left", va="center",
            )

    fig.tight_layout()
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
