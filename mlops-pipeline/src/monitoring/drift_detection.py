"""
Détection de drift des données.

Score = max(
  L1 des moyennes TF-IDF (shift de vocabulaire),
  distance de variation totale des labels si les deux CSV sont étiquetés
)
"""
import numpy as np
import pandas as pd


def _densify(data):
    if hasattr(data, "toarray"):
        return data.toarray()
    return np.asarray(data)


def feature_mean_drift(reference_data, current_data) -> float:
    reference_data = _densify(reference_data)
    current_data = _densify(current_data)
    if reference_data.ndim != 2 or current_data.ndim != 2:
        return 0.0
    if reference_data.shape[1] != current_data.shape[1]:
        return 0.5
    ref_mean = np.mean(reference_data, axis=0)
    curr_mean = np.mean(current_data, axis=0)
    return float(np.mean(np.abs(ref_mean - curr_mean)))


def label_mix_drift(reference_labels, current_labels) -> float:
    """Distance de variation totale entre deux répartitions de classes (0–1)."""
    ref = pd.Series(reference_labels).value_counts(normalize=True)
    curr = pd.Series(current_labels).value_counts(normalize=True)
    classes = ref.index.union(curr.index)
    p = ref.reindex(classes, fill_value=0.0)
    q = curr.reindex(classes, fill_value=0.0)
    return float(0.5 * np.abs(p - q).sum())


def detect_drift(
    reference_data,
    current_data,
    threshold=0.1,
    reference_labels=None,
    current_labels=None,
):
    feature_score = feature_mean_drift(reference_data, current_data)
    label_score = 0.0
    if reference_labels is not None and current_labels is not None:
        label_score = label_mix_drift(reference_labels, current_labels)
    drift_score = max(feature_score, label_score)
    return drift_score, drift_score > threshold


def calculate_data_quality_metrics(data):
    data = _densify(data)
    return {
        "mean": float(np.mean(data)),
        "std": float(np.std(data)),
        "min": float(np.min(data)),
        "max": float(np.max(data)),
        "null_count": int(np.isnan(data).sum()) if np.issubdtype(data.dtype, np.floating) else 0,
        "shape": data.shape,
    }
