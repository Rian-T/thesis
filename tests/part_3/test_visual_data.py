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
CHAPTER8_ARTIFACTS = {
    Path("plots/part_3/data/chapter8/derive_ablation.py"):
        "41666964046a00c5084aac6358818a4a11d5a9621358c1ccadc9b6b76a2465a3",
    Path("plots/part_3/data/chapter8/ablation_200doc.json"):
        "499bc6ab525bf7c353348ed7dd3b838f58091a777e6ebec94e40ccf6e8014780",
    Path("plots/part_3/data/chapter8/judge_eval_report.md"):
        "f72aa67573117008488f12d3287fd7b708a1b4d987d7b8a5aec4fbcb901d2ecd",
    Path("plots/part_3/data/chapter8/scores_parhaf_bio_dev.json"):
        "f0f805e7c8585fc8f8434435930a559eaa39323b17c23b9e3d8181331ff991ee",
    Path("plots/part_3/data/chapter8/scores_unified_410.json"):
        "dd003417b204155454372a502078caad8c79db879176c81f248be40497f555ed",
}
CHAPTER7_ARTIFACTS = {
    Path("plots/part_3/data/chapter7/derive_capstone.py"),
    Path("plots/part_3/data/chapter7/capstone_410doc.json"),
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


def test_chapter8_primary_artifact_contents_are_hash_locked():
    for artifact, expected_sha256 in CHAPTER8_ARTIFACTS.items():
        assert artifact.is_file(), artifact
        assert hashlib.sha256(artifact.read_bytes()).hexdigest() == expected_sha256


def test_chapter7_artifacts_are_present_and_hash_locked_by_manifest():
    payload = json.loads(DATA.read_text())
    hashes = payload["chapter7"]["artifact_sha256"]
    assert set(hashes) == {str(path) for path in CHAPTER7_ARTIFACTS}
    for artifact in CHAPTER7_ARTIFACTS:
        assert artifact.is_file()
        assert hashlib.sha256(artifact.read_bytes()).hexdigest() == hashes[str(artifact)]


def test_chapter7_observations_match_exact_derived_artifact_and_registry():
    payload = json.loads(DATA.read_text())
    chapter = payload["chapter7"]["capstone"]
    derived_path = Path("plots/part_3/data/chapter7/capstone_410doc.json")
    derived = json.loads(derived_path.read_text())
    registry = json.loads(Path("research/lymphome/results.json").read_text())
    expected = {
        ("encoder", "top1", "value_f1"): 0.6331050981187579,
        ("encoder", "final", "value_f1"): 0.6466740725330404,
        ("qwen", "top1", "value_f1"): 0.6650600379463285,
        ("qwen", "final", "value_f1"): 0.646012893119297,
    }
    for (model, variant, metric), value in expected.items():
        observation = chapter[model][variant][metric]
        assert observation["value"] == value == derived["systems"][model][variant][metric]
        assert observation["status"] == "provisional"
        assert observation["source"] == str(derived_path)
        assert observation["n"] == derived["n_documents"] == 410
    for model, display in {"encoder": "MC-bio-gliner (v3b)", "qwen": "Qwen3.5-9B"}.items():
        matches = [row for row in registry["ecrf"].values() if row.get("display") == display and row.get("regime") == "capstone"]
        assert len(matches) == 1
        assert round(derived["systems"][model]["final"]["value_f1"], 4) == matches[0]["value"]
        assert round(derived["systems"][model]["final"]["span_f1"], 4) == matches[0]["span"]


def test_chapter8_ablation_uses_exact_200_document_intersection():
    payload = json.loads(DATA.read_text())
    ablation = payload["chapter8"]["supervision_signal"]
    source_path = Path("plots/part_3/data/chapter8/ablation_200doc.json")
    source = json.loads(source_path.read_text())

    for model, observation in ablation["global"].items():
        assert observation["value"] == source["global"][model]["value_f1"]
        assert observation["n"] == source["n_documents"] == 200
        assert observation["status"] == "provisional"
        assert observation["source"] == str(source_path)
    expected_cells = {
        "first": 1680,
        "other": 86,
        "news": 322,
        "second": 360,
        "demography": 839,
        "imaging": 712,
        "antecedents": 434,
        "history": 3793,
    }
    assert {
        section: values["full"]["n"]
        for section, values in ablation["sections"].items()
    } == expected_cells
    for section, models in ablation["sections"].items():
        assert set(models) == {"full", "no_clinical"}
        for model, observation in models.items():
            source_observation = source["sections"][section]
            assert observation["value"] == source_observation["models"][model]["value_f1"]
            assert observation["n"] == source_observation["n_gold_cells"]
            assert observation["status"] == "provisional"
            assert observation["source"] == str(source_path)
    for section in ("first", "other", "news", "second"):
        note = ablation["sections"][section]["no_clinical"]["note"]
        assert "raw candidate row" in note
        assert "prediction" not in note
        source_models = source["sections"][section]["models"]
        assert "n_raw_candidate_rows" in source_models["no_clinical"]
        assert "n_predictions" not in source_models["no_clinical"]


def test_chapter8_judge_values_use_current_primary_report():
    payload = json.loads(DATA.read_text())
    judge = payload["chapter8"]["novel_types"]

    assert judge["v3c_medembed_e1"]["common"]["value"] == 0.517
    assert judge["v3c_medembed_e1"]["novel"]["value"] == 0.382
    assert judge["v3c_mcbio_e1"]["common"]["value"] == 0.478
    assert judge["v3c_mcbio_e1"]["novel"]["value"] == 0.333
    for model in judge.values():
        assert model["common"]["n"] == 1496
        assert model["novel"]["n"] == 682
        for observation in model.values():
            assert observation["status"] == "provisional"
            assert "LLM-judge MAP" in observation["note"]


def test_chapter8_judge_citations_point_to_exact_report_rows():
    payload = json.loads(DATA.read_text())
    judge = payload["chapter8"]["novel_types"]
    report = Path("plots/part_3/data/chapter8/judge_eval_report.md")
    lines = report.read_text().splitlines()
    expected = {
        ("v3c_medembed_e1", "common"): ("v3c-medembed-e1", "0.517"),
        ("v3c_medembed_e1", "novel"): ("v3c-medembed-e1", "0.382"),
        ("v3c_mcbio_e1", "common"): ("v3c-mcbio-e1", "0.478"),
        ("v3c_mcbio_e1", "novel"): ("v3c-mcbio-e1", "0.333"),
    }
    for (model, regime), tokens in expected.items():
        citation = judge[model][regime]["source"]
        line_number = int(citation.rsplit(":", 1)[1])
        cited_line = lines[line_number - 1]
        assert regime in cited_line
        assert all(token in cited_line for token in tokens)


def test_chapter8_tradeoff_keeps_current_ner_endpoints_provisional():
    payload = json.loads(DATA.read_text())
    tradeoff = payload["chapter8"]["specialization_tradeoff"]
    results = json.loads(Path("research/lymphome/results.json").read_text())
    parhaf = json.loads(
        Path("plots/part_3/data/chapter8/scores_parhaf_bio_dev.json").read_text()
    )
    unified = json.loads(
        Path("plots/part_3/data/chapter8/scores_unified_410.json").read_text()
    )

    def unique_value(rows, model, variant):
        matches = [
            row["value"]
            for row in rows
            if row["model"] == model and row["variant"] == variant
        ]
        assert len(matches) == 1
        return matches[0]

    def registered_value(benchmark, display, regime):
        matches = [
            entry["value"]
            for entry in results[benchmark].values()
            if entry.get("display") == display
            and entry.get("regime") == regime
        ]
        assert len(matches) == 1
        return matches[0]

    registered_artifact_pairs = (
        (
            registered_value("ecrf", "MC-bio-gliner (v3b)", "zero_shot"),
            unique_value(unified, "v3b (zs)", "top-1 + compete"),
        ),
        (
            registered_value("parhaf", "MC-bio-gliner (v3b)", "zero_shot"),
            unique_value(parhaf, "v3b-pristine", "ner"),
        ),
        (
            registered_value("ecrf", "MC-bio-gliner (v3b)", "capstone"),
            unique_value(unified, "GLiNER-150M (v3b)", "top-1 + compete"),
        ),
        (
            registered_value("parhaf", "MC-bio-gliner (v3e)", "zero_shot"),
            unique_value(parhaf, "v3e", "ner"),
        ),
        (
            registered_value("ecrf", "MC-bio-gliner (MIX)", "capstone"),
            unique_value(unified, "GLiNER-150M (MIX6)", "top-1 + compete"),
        ),
    )
    for registered, artifact in registered_artifact_pairs:
        assert registered == artifact

    expected = {
        "fromv3b_parhaf": (
            unique_value(parhaf, "lym-V5FROMV3B", "ner"),
            "plots/part_3/data/chapter8/scores_parhaf_bio_dev.json",
        ),
        "v3e_ecrf": (
            unique_value(unified, "v3e (zs)", "top-1 + compete"),
            "plots/part_3/data/chapter8/scores_unified_410.json",
        ),
        "mix6_parhaf": (
            unique_value(parhaf, "lym-V5MIX6", "ner"),
            "plots/part_3/data/chapter8/scores_parhaf_bio_dev.json",
        ),
    }
    assert set(tradeoff) == set(expected)
    for endpoint, (value, source) in expected.items():
        observation = tradeoff[endpoint]
        assert observation["value"] == value
        assert observation["source"] == source
        assert observation["status"] == "provisional"
