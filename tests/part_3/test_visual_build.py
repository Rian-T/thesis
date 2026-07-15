import json
from pathlib import Path
from types import SimpleNamespace

import matplotlib.pyplot as plt
from PIL import Image
import pytest

from plots.part_3 import build_all
from plots.part_3 import common
from plots.part_3.common import (
    ProvisionalDataError,
    load_visual_data,
    mark_preliminary,
    result_value,
    save_figure,
    semantic_colors,
)


def _write_visual_fixture(path: Path, status: str) -> None:
    path.write_text(
        json.dumps(
            {
                "_meta": {"schema": 1},
                "observations": {
                    "metric": {
                        "value": 0.5,
                        "status": status,
                        "source": "test fixture",
                    }
                },
            }
        )
    )


def test_final_loader_rejects_provisional_fixture(tmp_path, monkeypatch):
    fixture = tmp_path / "visual_data.json"
    _write_visual_fixture(fixture, "provisional")
    monkeypatch.setattr(common, "VISUAL_DATA", fixture)

    with pytest.raises(ProvisionalDataError):
        load_visual_data(allow_provisional=False)


def test_final_loader_accepts_registered_fixture(tmp_path, monkeypatch):
    fixture = tmp_path / "visual_data.json"
    _write_visual_fixture(fixture, "registered")
    monkeypatch.setattr(common, "VISUAL_DATA", fixture)

    assert load_visual_data(allow_provisional=False)["_meta"]["schema"] == 1


def test_preview_loader_accepts_provisional_fixture(tmp_path, monkeypatch):
    fixture = tmp_path / "visual_data.json"
    _write_visual_fixture(fixture, "provisional")
    monkeypatch.setattr(common, "VISUAL_DATA", fixture)

    assert load_visual_data(allow_provisional=True)["_meta"]["schema"] == 1


def test_semantic_palette_matches_thesis():
    assert semantic_colors() == {
        "encoder": "#A694E8",
        "llm": "#F1B890",
        "structure": "#ABCC6E",
        "neutral": "#667082",
        "failure": "#C25A5A",
    }


def test_registered_capstone_value_is_loaded_by_identity():
    assert result_value(
        "ecrf", "MC-bio-gliner (v3b)", "capstone", "value"
    ) == pytest.approx(0.6467)


def test_result_value_preserves_zero(monkeypatch):
    monkeypatch.setattr(
        common,
        "load_results",
        lambda: {
            "benchmark": {
                "only": {
                    "display": "Model",
                    "regime": "raw",
                    "value": 0,
                }
            }
        },
    )

    assert result_value("benchmark", "Model", "raw", "value") == 0.0


def test_result_value_rejects_duplicate_identity(monkeypatch):
    entry = {"display": "Model", "regime": "raw", "value": 0.5}
    monkeypatch.setattr(
        common,
        "load_results",
        lambda: {"benchmark": {"first": entry, "second": entry.copy()}},
    )

    with pytest.raises(KeyError) as error:
        result_value("benchmark", "Model", "raw", "value")

    assert error.value.args[0] == ("benchmark", "Model", "raw", 2)


def test_result_value_rejects_missing_identity(monkeypatch):
    monkeypatch.setattr(common, "load_results", lambda: {"benchmark": {}})

    with pytest.raises(KeyError) as error:
        result_value("benchmark", "Model", "raw", "value")

    assert error.value.args[0] == ("benchmark", "Model", "raw", 0)


def test_mark_preliminary_places_exact_lower_right_label():
    fig = plt.figure()
    try:
        mark_preliminary(fig)

        assert len(fig.texts) == 1
        label = fig.texts[0]
        assert label.get_text() == "PRELIMINARY"
        assert label.get_position() == (0.995, 0.005)
        assert label.get_ha() == "right"
        assert label.get_va() == "bottom"
    finally:
        plt.close(fig)


def test_save_figure_writes_pdf_and_180_dpi_png_and_closes(tmp_path):
    fig, ax = plt.subplots()
    figure_number = fig.number
    ax.plot([0, 1], [0, 1])

    outputs = save_figure(fig, "example", tmp_path)

    assert outputs == [tmp_path / "example.pdf", tmp_path / "example.png"]
    assert all(path.is_file() and path.stat().st_size > 0 for path in outputs)
    with Image.open(outputs[1]) as image:
        assert image.info["dpi"][0] == pytest.approx(180, abs=0.1)
        assert image.info["dpi"][1] == pytest.approx(180, abs=0.1)
    assert not plt.fignum_exists(figure_number)


def test_save_figure_failure_cleans_outputs_and_closes(
    tmp_path, monkeypatch
):
    fig = plt.figure()
    figure_number = fig.number
    calls = 0

    def failing_savefig(path, **_kwargs):
        nonlocal calls
        calls += 1
        Path(path).write_bytes(b"partial")
        if calls == 2:
            raise RuntimeError("png export failed")

    monkeypatch.setattr(fig, "savefig", failing_savefig)

    with pytest.raises(RuntimeError, match="png export failed"):
        save_figure(fig, "broken", tmp_path)

    assert not (tmp_path / "broken.pdf").exists()
    assert not (tmp_path / "broken.png").exists()
    assert not list(tmp_path.glob("*broken*"))
    assert not plt.fignum_exists(figure_number)


def test_build_all_calls_chapter_builders_and_prints_relative_paths(
    tmp_path, monkeypatch, capsys
):
    calls = []

    def fake_import_module(module_name):
        def build(output_dir, allow_provisional):
            calls.append((module_name, output_dir, allow_provisional))
            return [output_dir / f"{module_name.rsplit('.', 1)[-1]}.pdf"]

        return SimpleNamespace(build=build)

    monkeypatch.setattr(build_all, "import_module", fake_import_module)

    assert build_all.main(
        ["--allow-provisional", "--output-dir", str(tmp_path)]
    ) == 0
    assert calls == [
        ("plots.part_3.plot_chapter9", tmp_path, True),
        ("plots.part_3.plot_chapter8", tmp_path, True),
        ("plots.part_3.plot_chapter7", tmp_path, True),
    ]
    printed = capsys.readouterr().out.splitlines()
    assert [Path(line).name for line in printed] == [
        "plot_chapter9.pdf",
        "plot_chapter8.pdf",
        "plot_chapter7.pdf",
    ]
    assert all(not Path(line).is_absolute() for line in printed)


def test_build_all_returns_nonzero_on_provisional_data(
    tmp_path, monkeypatch, capsys
):
    def fake_import_module(_module_name):
        def build(_output_dir, _allow_provisional):
            raise ProvisionalDataError("principal visual data remain provisional")

        return SimpleNamespace(build=build)

    monkeypatch.setattr(build_all, "import_module", fake_import_module)

    assert build_all.main(["--output-dir", str(tmp_path)]) != 0
    assert "principal visual data remain provisional" in capsys.readouterr().err
