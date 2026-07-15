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


def test_save_figure_closes_when_output_directory_creation_fails(tmp_path):
    output_file = tmp_path / "not-a-directory"
    output_file.write_text("occupied")
    fig = plt.figure()
    figure_number = fig.number

    with pytest.raises(FileExistsError):
        save_figure(fig, "broken", output_file)

    assert not plt.fignum_exists(figure_number)


def test_save_figure_publication_failure_removes_both_outputs_and_closes(
    tmp_path, monkeypatch
):
    fig = plt.figure()
    figure_number = fig.number
    original_replace = Path.replace
    replacements = 0

    def fail_second_replace(path, target):
        nonlocal replacements
        replacements += 1
        if replacements == 2:
            raise OSError("png publication failed")
        return original_replace(path, target)

    monkeypatch.setattr(Path, "replace", fail_second_replace)

    with pytest.raises(OSError, match="png publication failed"):
        save_figure(fig, "broken", tmp_path)

    assert not (tmp_path / "broken.pdf").exists()
    assert not (tmp_path / "broken.png").exists()
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


def test_chapter9_prepares_registered_raw_stylometry_in_fixed_order():
    from plots.part_3.plot_chapter9 import prepare_stylometry

    panels = prepare_stylometry()

    assert [panel.key for panel in panels] == [
        "mauve",
        "fed",
        "mmd2",
        "c2st",
    ]
    assert all(
        panel.sources == ("PMC-Patients", "Dossiers synthétiques", "E3C")
        for panel in panels
    )
    assert [panel.values for panel in panels] == [
        pytest.approx((0.040, 0.017, 0.006)),
        pytest.approx((0.28, 0.35, 0.74)),
        pytest.approx((0.0002, 0.0003, 0.0009)),
        pytest.approx((0.991, 0.988, 0.985)),
    ]
    assert all(panel.statuses == ("registered",) * 3 for panel in panels)
    assert all(
        panel.provenance
        == ("plots/part_3/data/stylometry/styleSOTA_1819572.out",) * 3
        for panel in panels
    )


def test_chapter9_render_is_native_width_with_labels_on_both_left_panels():
    from plots.part_3.plot_chapter9 import _make_figure, prepare_stylometry

    fig = _make_figure(prepare_stylometry())
    try:
        width, _height = fig.get_size_inches()
        assert width == pytest.approx(5.5)
        assert len(fig.axes) == 4
        for index in (0, 2):
            assert [
                label.get_text()
                for label in fig.axes[index].get_yticklabels()
                if label.get_visible()
            ] == ["PMC-Patients", "Dossiers synthétiques", "E3C"]
        for index in (1, 3):
            assert all(
                not label.get_visible()
                for label in fig.axes[index].get_yticklabels()
            )
        visible_text = [
            text
            for ax in fig.axes
            for text in (
                [ax.title]
                + list(ax.texts)
                + list(ax.get_xticklabels())
                + list(ax.get_yticklabels())
            )
            if text.get_visible() and text.get_text()
        ]
        assert visible_text
        assert min(text.get_fontsize() for text in visible_text) >= 7
    finally:
        plt.close(fig)


def test_chapter9_builds_stylometry_without_preliminary_watermark(
    tmp_path, monkeypatch
):
    from plots.part_3 import plot_chapter9

    preliminary_calls = []
    monkeypatch.setattr(
        plot_chapter9,
        "mark_preliminary",
        lambda fig: preliminary_calls.append(fig),
    )

    outputs = plot_chapter9.build(tmp_path, allow_provisional=True)

    assert outputs == [
        tmp_path / "fig06_stylometry.pdf",
        tmp_path / "fig06_stylometry.png",
    ]
    assert all(path.is_file() and path.stat().st_size > 0 for path in outputs)
    assert preliminary_calls == []


def test_chapter9_final_build_accepts_registered_stylometry(
    tmp_path, monkeypatch
):
    from plots.part_3 import plot_chapter9

    preliminary_calls = []
    monkeypatch.setattr(
        plot_chapter9,
        "mark_preliminary",
        lambda fig: preliminary_calls.append(fig),
    )

    outputs = plot_chapter9.build(tmp_path, allow_provisional=False)

    assert outputs == [
        tmp_path / "fig06_stylometry.pdf",
        tmp_path / "fig06_stylometry.png",
    ]
    assert all(path.is_file() and path.stat().st_size > 0 for path in outputs)
    assert preliminary_calls == []
