"""Métriques sur le holdout et profil de référence pour le drift."""

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score


def evaluate(model, df: pd.DataFrame) -> dict[str, float]:
    """Accuracy, F1 macro et F1 par classe (classes équilibrées : le macro est la référence)."""
    y_true = df["label"]
    y_pred = model.predict(df["text"])
    metrics = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "f1_macro": float(f1_score(y_true, y_pred, average="macro")),
    }
    labels = sorted(y_true.unique())
    per_class = f1_score(y_true, y_pred, average=None, labels=labels)
    for label, score in zip(labels, per_class, strict=True):
        metrics[f"f1_{_slug(label)}"] = float(score)
    return metrics


def reference_profile(model, df: pd.DataFrame, max_confidences: int = 2000, seed: int = 42):
    """Ce que « normal » veut dire pour ce modèle, mesuré sur le holdout.

    - répartition des classes prédites (comparée au trafic via PSI / chi²) ;
    - échantillon des confiances max (comparé au trafic via KS).
    Loggé avec le modèle : chaque version porte sa propre référence.
    """
    proba = model.predict_proba(df["text"])
    classes = [str(c) for c in model.classes_]
    predicted = np.asarray(classes)[proba.argmax(axis=1)]
    counts = pd.Series(predicted).value_counts(normalize=True)
    confidences = proba.max(axis=1)
    rng = np.random.default_rng(seed)
    if len(confidences) > max_confidences:
        confidences = rng.choice(confidences, size=max_confidences, replace=False)
    return {
        "classes": classes,
        "class_distribution": {c: float(counts.get(c, 0.0)) for c in classes},
        "confidences": [round(float(c), 4) for c in confidences],
        "n": int(len(df)),
    }


def _slug(label: str) -> str:
    return "".join(ch if ch.isalnum() else "_" for ch in str(label).lower())
