import json
from pathlib import Path

DATA = Path("plots/part_3/data/visual_data.json")


def walk(node, path="root"):
    if isinstance(node, dict) and "value" in node:
        yield path, node
    elif isinstance(node, dict):
        for key, value in node.items():
            yield from walk(value, f"{path}.{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from walk(value, f"{path}[{index}]")


def test_every_observation_is_traceable():
    payload = json.loads(DATA.read_text())
    observations = list(walk(payload))
    assert observations
    for path, observation in observations:
        assert observation["status"] in {"registered", "provisional"}, path
        assert observation["source"].strip(), path
        assert isinstance(observation["value"], (int, float)), path


def test_no_dashboard_only_final_observation():
    payload = json.loads(DATA.read_text())
    for path, observation in walk(payload):
        if observation["status"] == "registered":
            assert "dashboard" not in observation["source"].lower(), path
