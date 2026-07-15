from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

import matplotlib.pyplot as plt

from plots.thesis_style import COLORS, apply_style

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "research/lymphome/results.json"
VISUAL_DATA = Path(__file__).parent / "data/visual_data.json"
DEFAULT_OUTPUT = Path(__file__).parent / "output"


class ProvisionalDataError(RuntimeError):
    """Raised when a final build encounters provisional visual evidence."""


@dataclass(frozen=True)
class Observation:
    value: float
    status: str
    source: str
    n: int | None = None
    note: str = ""


def semantic_colors() -> dict[str, str]:
    return {
        "encoder": COLORS["primary"],
        "llm": COLORS["tertiary"],
        "structure": COLORS["secondary"],
        "neutral": COLORS["neutral"],
        "failure": COLORS["baseline"],
    }


def _observations(node):
    if isinstance(node, dict) and "value" in node:
        yield node
    elif isinstance(node, dict):
        for child in node.values():
            yield from _observations(child)
    elif isinstance(node, list):
        for child in node:
            yield from _observations(child)


def load_visual_data(allow_provisional: bool = False) -> dict:
    data = json.loads(VISUAL_DATA.read_text())
    if not allow_provisional and any(
        observation["status"] == "provisional"
        for observation in _observations(data)
    ):
        raise ProvisionalDataError("principal visual data remain provisional")
    return data


def load_results() -> dict:
    return json.loads(RESULTS.read_text())


def result_value(
    benchmark: str, display: str, regime: str, metric: str
) -> float:
    matches = [
        entry
        for entry in load_results()[benchmark].values()
        if isinstance(entry, dict)
        and entry.get("display") == display
        and entry.get("regime") == regime
    ]
    if len(matches) != 1:
        raise KeyError((benchmark, display, regime, len(matches)))
    return float(matches[0][metric])


def configure_style() -> None:
    apply_style()
    plt.rcParams.update({"figure.constrained_layout.use": True})


def mark_preliminary(fig) -> None:
    fig.text(
        0.995,
        0.005,
        "PRELIMINARY",
        ha="right",
        va="bottom",
        color=COLORS["baseline"],
        fontsize=7,
        alpha=0.8,
    )


def save_figure(
    fig, stem: str, output_dir: Path = DEFAULT_OUTPUT
) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = [output_dir / f"{stem}.pdf", output_dir / f"{stem}.png"]
    fig.savefig(outputs[0], bbox_inches="tight")
    fig.savefig(outputs[1], bbox_inches="tight", dpi=200)
    plt.close(fig)
    return outputs
