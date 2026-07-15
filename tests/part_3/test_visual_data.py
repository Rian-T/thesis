import json
import hashlib
import re
from pathlib import Path

DATA = Path("plots/part_3/data/visual_data.json")
OBSERVATION_FIELDS = {"value", "status", "source", "n", "note"}
STYLOMETRY_SOURCE = Path(
    "plots/part_3/data/stylometry/styleSOTA_1819572.out"
)
STYLOMETRY_ARTIFACTS = {
    Path("plots/part_3/data/stylometry/sota_dist_test.py"):
        "b9250f4547b982078a6894d1c990e9482efb21fb7a6ac1ae85423a670584c1f9",
    Path("plots/part_3/data/stylometry/sota_style_jz.sbatch"):
        "b5f75fbe9beca4f72e5421e04c9b12d94fd36190f6ec39e08a3d185ee98ce9ab",
    STYLOMETRY_SOURCE:
        "aef20e6f35d99d25b48cd8ee472aa1470b834fe101dc51ce8a789b72fedd447c",
}
SECONDARY_ONLY_SOURCES = {
    "partie3_intra.md",
    "partie3_extra.md",
    "07_resultats.md",
}


def walk(node, path="root"):
    if isinstance(node, dict) and "value" in node:
        yield path, node
    elif isinstance(node, dict):
        for key, value in node.items():
            yield from walk(value, f"{path}.{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from walk(value, f"{path}[{index}]")


def source_paths(source):
    for citation in source.split(";"):
        citation = citation.strip()
        yield Path(re.sub(r":\d+(?:-\d+)?$", "", citation))


def test_every_observation_is_traceable():
    payload = json.loads(DATA.read_text())
    observations = list(walk(payload))
    assert observations
    for path, observation in observations:
        assert set(observation) == OBSERVATION_FIELDS, path
        assert observation["status"] in {"registered", "provisional"}, path
        assert observation["source"].strip(), path
        assert isinstance(observation["value"], (int, float)), path


def test_registered_sources_exist_and_are_not_secondary_only():
    payload = json.loads(DATA.read_text())
    for path, observation in walk(payload):
        if observation["status"] == "registered":
            citations = list(source_paths(observation["source"]))
            assert citations, path
            for citation in citations:
                assert citation.is_file(), f"{path}: missing {citation}"
            assert any(
                citation.name.lower() not in SECONDARY_ONLY_SOURCES
                and "dashboard" not in str(citation).lower()
                for citation in citations
            ), f"{path}: registered observation has only secondary sources"


def test_data_efficiency_remains_provisional_until_rescored():
    payload = json.loads(DATA.read_text())
    expected = {
        "train_10": 0.182,
        "train_50": 0.485,
        "train_100": 0.544,
        "train_500": 0.603,
        "train_1540": 0.659,
    }
    assert set(payload["data_efficiency"]) == set(expected)
    for key, value in expected.items():
        observation = payload["data_efficiency"][key]
        assert observation["value"] == value
        assert observation["status"] == "provisional"
        assert "-de" not in observation["source"]


def test_primary_stylometry_artifacts_are_exact_copies():
    for artifact, expected_sha256 in STYLOMETRY_ARTIFACTS.items():
        assert artifact.is_file(), artifact
        assert hashlib.sha256(artifact.read_bytes()).hexdigest() == expected_sha256


def test_stylometry_registers_all_four_primary_metrics():
    payload = json.loads(DATA.read_text())
    expected = {
        "mauve": {"pmc_patients": 0.040, "synthetic_records": 0.017, "e3c": 0.006},
        "fed": {"pmc_patients": 0.28, "synthetic_records": 0.35, "e3c": 0.74},
        "mmd2": {"pmc_patients": 0.0002, "synthetic_records": 0.0003, "e3c": 0.0009},
        "c2st": {"pmc_patients": 0.991, "synthetic_records": 0.988, "e3c": 0.985},
    }
    assert set(payload["stylometry"]) == set(expected)
    for metric, sources in expected.items():
        assert set(payload["stylometry"][metric]) == set(sources)
        for source, value in sources.items():
            observation = payload["stylometry"][metric][source]
            assert observation["value"] == value
            assert observation["status"] == "registered"
            assert observation["source"] == str(STYLOMETRY_SOURCE)
            assert observation["n"] == 1000
            assert "PARHAF is human-written fictitious clinical text" in observation["note"]
            assert "not a real hospital-record corpus" in observation["note"]
