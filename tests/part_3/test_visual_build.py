from pathlib import Path
from types import SimpleNamespace

import pytest

from plots.part_3 import build_all
from plots.part_3.common import (
    ProvisionalDataError,
    load_visual_data,
    result_value,
    semantic_colors,
)


def test_final_loader_rejects_provisional_principal_values():
    with pytest.raises(ProvisionalDataError):
        load_visual_data(allow_provisional=False)


def test_preview_loader_accepts_provisional_values():
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
