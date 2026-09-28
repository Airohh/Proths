"""Détection de drift sur le trafic, sans vrais labels.

On compare les N dernières prédictions au profil de référence du modèle
(mesuré sur le holdout au moment de l'entraînement) :

- PSI sur la répartition des classes prédites : le mix du trafic a-t-il bougé ?
  (PSI < 0.1 stable, 0.1–0.2 à surveiller, > 0.2 changement significatif)
- chi² sur les mêmes comptes : p-value, à titre indicatif (sur de gros volumes
  elle devient minuscule pour des écarts minimes, d'où la décision sur le PSI) ;
- Kolmogorov–Smirnov sur la confiance max : le modèle devient-il moins sûr de lui ?
  C'est souvent le premier signe d'un vocabulaire qu'il ne connaît pas.

La performance réelle (précision sur les labels de feedback) est suivie à part,
dans monitor.py : c'est le seul signal qui dit si le modèle a *tort*.
"""

from dataclasses import asdict, dataclass, field

import numpy as np
from scipy import stats

EPS = 1e-4


def psi(expected: np.ndarray, actual: np.ndarray) -> float:
    """Population Stability Index entre deux distributions de probabilité."""
    expected = np.clip(np.asarray(expected, dtype=float), EPS, None)
    actual = np.clip(np.asarray(actual, dtype=float), EPS, None)
    expected, actual = expected / expected.sum(), actual / actual.sum()
    return float(np.sum((actual - expected) * np.log(actual / expected)))


@dataclass
class DriftReport:
    n: int
    enough_data: bool
    psi: float = 0.0
    chi2_pvalue: float = 1.0
    ks_stat: float = 0.0
    ks_pvalue: float = 1.0
    mean_confidence: float = 0.0
    reference_mean_confidence: float = 0.0
    class_distribution: dict = field(default_factory=dict)
    drift: bool = False
    reasons: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def detect_drift(
    profile: dict,
    predicted: list[str],
    confidences: list[float],
    *,
    psi_threshold: float = 0.2,
    ks_threshold: float = 0.15,
    min_samples: int = 200,
) -> DriftReport:
    classes = profile["classes"]
    ref_dist = np.array([profile["class_distribution"][c] for c in classes])
    ref_conf = np.asarray(profile["confidences"], dtype=float)
    n = len(predicted)

    report = DriftReport(
        n=n,
        enough_data=n >= min_samples,
        reference_mean_confidence=float(ref_conf.mean()) if len(ref_conf) else 0.0,
    )
    if n == 0:
        return report

    counts = np.array([sum(1 for p in predicted if p == c) for c in classes], dtype=float)
    current_dist = counts / n
    report.class_distribution = {
        c: round(float(v), 4) for c, v in zip(classes, current_dist, strict=True)
    }
    report.psi = psi(ref_dist, current_dist)
    expected_counts = np.clip(ref_dist, EPS, None)
    expected_counts = expected_counts / expected_counts.sum() * n
    report.chi2_pvalue = float(stats.chisquare(counts, expected_counts).pvalue)

    conf = np.asarray(confidences, dtype=float)
    report.mean_confidence = float(conf.mean())
    ks = stats.ks_2samp(ref_conf, conf)
    report.ks_stat, report.ks_pvalue = float(ks.statistic), float(ks.pvalue)

    if report.enough_data:
        if report.psi > psi_threshold:
            report.reasons.append(f"PSI classes {report.psi:.3f} > {psi_threshold}")
        if report.ks_stat > ks_threshold:
            report.reasons.append(f"KS confiance {report.ks_stat:.3f} > {ks_threshold}")
        report.drift = bool(report.reasons)
    return report
