import pandas as pd

from src.monitoring.drift_detection import detect_drift, label_mix_drift
from src.training.preprocessing import vectorize_for_drift


def test_label_mix_flags_skew():
    balanced = ["a", "b", "c", "d"] * 25
    skewed = ["a"] * 80 + ["b"] * 10 + ["c"] * 5 + ["d"] * 5
    score = label_mix_drift(balanced, skewed)
    assert score > 0.15


def test_same_mix_is_low():
    labels = ["tech", "sports"] * 50
    assert label_mix_drift(labels, labels) == 0.0


def test_vectorize_pair_same_width():
    ref = pd.DataFrame(
        {
            "text": [
                "machine learning neural networks python",
                "machine learning neural networks code",
                "football soccer champions league",
                "football soccer world cup",
            ],
            "label": ["technology", "technology", "sports", "sports"],
        }
    )
    curr = pd.DataFrame(
        {
            "text": [
                "football soccer champions league",
                "football soccer world cup",
                "football soccer champions league",
                "football soccer world cup",
            ],
            "label": ["sports", "sports", "sports", "sports"],
        }
    )
    X_ref, X_curr = vectorize_for_drift(ref, curr)
    assert X_ref.shape[1] == X_curr.shape[1]
    score, is_drift = detect_drift(
        X_ref,
        X_curr,
        threshold=0.15,
        reference_labels=ref["label"],
        current_labels=curr["label"],
    )
    assert is_drift
    assert score > 0.15
