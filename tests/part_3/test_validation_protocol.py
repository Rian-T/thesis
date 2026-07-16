from research.lymphome.score_unified import compete, top1
from research.lymphome.validation_protocol import evaluate_with_validation_threshold
import pytest
import pandas as pd


def test_threshold_is_selected_on_validation_and_applied_unchanged_to_test():
    validation_gold = {"v1": {"field": [[0, 5, "alpha"]]}, "v2": {}}
    validation_texts = {"v1": "alpha", "v2": "noise"}
    validation_predictions = {
        "v1": {"field": (0.9, 0, 5, None)},
        "v2": {"field": (0.7, 0, 5, None)},
    }

    test_gold = {"t1": {"field": [[0, 5, "alpha"]]}}
    test_texts = {"t1": "alpha"}
    test_predictions = {"t1": {"field": (0.5, 0, 5, None)}}

    result = evaluate_with_validation_threshold(
        validation_predictions,
        validation_gold,
        validation_texts,
        test_predictions,
        test_gold,
        test_texts,
        mode="value",
        thresholds=[0.0, 0.8],
    )

    assert result["threshold"] == 0.8
    assert result["validation_f1"] == 1.0
    assert result["test_f1"] == 0.0


def test_validation_and_test_documents_must_be_disjoint():
    gold = {"shared": {}}
    texts = {"shared": ""}

    with pytest.raises(ValueError, match="disjoint"):
        evaluate_with_validation_threshold(
            {}, gold, texts, {}, gold, texts,
            mode="value", thresholds=[0.0],
        )


def test_threshold_ties_choose_the_highest_threshold_independently_of_order():
    validation_gold = {"v": {}}
    validation_texts = {"v": ""}
    test_gold = {"t": {}}
    test_texts = {"t": ""}

    for thresholds in ([0.2, 0.8], [0.8, 0.2]):
        result = evaluate_with_validation_threshold(
            {}, validation_gold, validation_texts,
            {}, test_gold, test_texts,
            mode="value", thresholds=thresholds,
        )
        assert result["threshold"] == 0.8


def test_mode_must_be_span_or_value():
    with pytest.raises(ValueError, match="mode"):
        evaluate_with_validation_threshold(
            {}, {"v": {}}, {"v": ""},
            {}, {"t": {}}, {"t": ""},
            mode="values", thresholds=[0.0],
        )


def test_threshold_grid_must_not_be_empty():
    with pytest.raises(ValueError, match="threshold"):
        evaluate_with_validation_threshold(
            {}, {"v": {}}, {"v": ""},
            {}, {"t": {}}, {"t": ""},
            mode="value", thresholds=[],
        )


def test_top1_is_invariant_to_row_order_when_confidences_tie():
    rows = [
        {"doc_id": "d", "key": "field", "start": 5, "end": 9,
         "confidence": 0.8, "value": "late"},
        {"doc_id": "d", "key": "field", "start": 1, "end": 4,
         "confidence": 0.8, "value": "early"},
    ]

    assert top1(pd.DataFrame(rows)) == top1(pd.DataFrame(reversed(rows)))
    assert top1(pd.DataFrame(rows))["d"]["field"][1:3] == (1, 4)


def test_competition_is_invariant_to_field_order_when_confidences_tie():
    forward = {"d": {
        "z_field": (0.8, 0, 5, "same"),
        "a_field": (0.8, 0, 5, "same"),
    }}
    reverse = {"d": dict(reversed(list(forward["d"].items())))}

    assert compete(forward) == compete(reverse)
    assert set(compete(forward)["d"]) == {"a_field"}
