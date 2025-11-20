"""
Détection de drift des données
"""
import numpy as np
from scipy import stats
from sklearn.metrics import pairwise_distances


def detect_drift(reference_data, current_data, threshold=0.1):
    """
    Détecte le drift entre les données de référence et les données actuelles
    
    Args:
        reference_data: Données de référence (numpy array)
        current_data: Données actuelles (numpy array)
        threshold: Seuil de drift (0-1)
    
    Returns:
        drift_score: Score de drift (0-1)
        is_drift: Boolean indiquant si drift détecté
    """
    # Kolmogorov-Smirnov test pour chaque feature
    drift_scores = []
    
    # Si les données sont trop grandes, échantillonner
    if len(reference_data) > 10000:
        reference_data = reference_data[np.random.choice(len(reference_data), 10000, replace=False)]
    if len(current_data) > 10000:
        current_data = current_data[np.random.choice(len(current_data), 10000, replace=False)]
    
    # Pour les données sparse (TF-IDF), calculer la distance moyenne
    if hasattr(reference_data, 'toarray'):
        reference_data = reference_data.toarray()
        current_data = current_data.toarray()
    
    # Calculer la distance moyenne entre les distributions
    if reference_data.shape[1] == current_data.shape[1]:
        # Distance de MMD (Maximum Mean Discrepancy) simplifiée
        ref_mean = np.mean(reference_data, axis=0)
        curr_mean = np.mean(current_data, axis=0)
        
        drift_score = np.mean(np.abs(ref_mean - curr_mean))
    else:
        # Si dimensions différentes, utiliser distance entre moyennes
        drift_score = 0.5  # Par défaut, drift modéré
    
    is_drift = drift_score > threshold
    
    return drift_score, is_drift


def calculate_data_quality_metrics(data):
    """
    Calcule des métriques de qualité des données
    
    Args:
        data: Données (numpy array ou sparse matrix)
    
    Returns:
        dict avec métriques de qualité
    """
    if hasattr(data, 'toarray'):
        data = data.toarray()
    
    metrics = {
        'mean': float(np.mean(data)),
        'std': float(np.std(data)),
        'min': float(np.min(data)),
        'max': float(np.max(data)),
        'null_count': int(np.isnan(data).sum()) if hasattr(data, 'sum') else 0,
        'shape': data.shape
    }
    
    return metrics

