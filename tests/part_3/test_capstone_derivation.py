import numpy as np
import pytest

from plots.part_3.data.chapter7 import derive_capstone
from research.lymphome.validation_protocol import FINAL_THRESHOLDS


def test_final_threshold_grid_is_fixed_and_well_formed():
    assert FINAL_THRESHOLDS[0] == 0.001
    assert FINAL_THRESHOLDS[-1] == 0.99
    assert len(FINAL_THRESHOLDS) == len(set(FINAL_THRESHOLDS))
    assert all(a < b for a, b in zip(FINAL_THRESHOLDS, FINAL_THRESHOLDS[1:]))


def test_paired_interval_is_zero_for_identical_counts(monkeypatch):
    monkeypatch.setattr(derive_capstone, "BOOTSTRAP_REPLICATES", 100)
    counts = np.asarray([[2, 1, 1], [1, 0, 2]], dtype=np.int64)
    result = derive_capstone.paired_interval(counts, counts)
    assert result["difference"] == 0.0
    assert result["ci95"] == [0.0, 0.0]


def test_paired_interval_rejects_unpaired_or_malformed_counts():
    good = np.asarray([[1, 0, 0]], dtype=np.int64)
    with pytest.raises(ValueError, match="same shape"):
        derive_capstone.paired_interval(good, np.vstack([good, good]))
    with pytest.raises(ValueError, match="shape"):
        derive_capstone.paired_interval(np.asarray([1, 0, 0]), np.asarray([1, 0, 0]))
    with pytest.raises(ValueError, match="empty"):
        derive_capstone.paired_interval(np.empty((0, 3)), np.empty((0, 3)))


def test_competition_effect_endpoints_equal_reported_difference(monkeypatch):
    monkeypatch.setattr(derive_capstone, "BOOTSTRAP_REPLICATES", 100)
    raw = np.asarray([[1, 2, 1], [1, 1, 1]], dtype=np.int64)
    decoded = np.asarray([[2, 1, 0], [1, 0, 1]], dtype=np.int64)
    result = derive_capstone.paired_interval(raw, decoded)
    raw_f1 = derive_capstone.f1_from_counts(raw.sum(axis=0))
    decoded_f1 = derive_capstone.f1_from_counts(decoded.sum(axis=0))
    assert result["difference"] == pytest.approx(decoded_f1 - raw_f1)
