import numpy as np
import pytest

from src.monitoring.drift import detect_drift, psi

PROFILE = {
    "classes": ["A", "B", "C", "D"],
    "class_distribution": {"A": 0.25, "B": 0.25, "C": 0.25, "D": 0.25},
    "confidences": list(np.linspace(0.6, 1.0, 400)),
}


def test_psi_is_zero_for_identical_distributions():
    assert psi([0.25] * 4, [0.25] * 4) == pytest.approx(0.0)


def test_psi_grows_with_the_shift():
    assert psi([0.25] * 4, [0.4, 0.2, 0.2, 0.2]) < psi([0.25] * 4, [0.7, 0.1, 0.1, 0.1])


def test_balanced_traffic_is_not_drift():
    predicted = ["A", "B", "C", "D"] * 100
    confidences = list(np.linspace(0.6, 1.0, 400))
    report = detect_drift(PROFILE, predicted, confidences)
    assert not report.drift
    assert report.psi < 0.01


def test_skewed_class_mix_is_drift():
    predicted = ["A"] * 280 + ["B", "C", "D"] * 40
    report = detect_drift(PROFILE, predicted, list(np.linspace(0.6, 1.0, 400)))
    assert report.drift
    assert any("PSI" in r for r in report.reasons)
    assert report.class_distribution["A"] == pytest.approx(0.7)


def test_confidence_collapse_is_drift():
    predicted = ["A", "B", "C", "D"] * 100
    report = detect_drift(PROFILE, predicted, [0.4] * 400)
    assert report.drift
    assert any("KS" in r for r in report.reasons)


def test_no_verdict_below_min_samples():
    report = detect_drift(PROFILE, ["A"] * 50, [0.9] * 50, min_samples=200)
    assert report.psi > 0.2
    assert not report.enough_data
    assert not report.drift
