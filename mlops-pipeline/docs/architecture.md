# Architecture du Pipeline MLOps

## Vue d'ensemble

Le pipeline suit le cycle complet : **Train → Deploy → Monitor → Retrain**

## Composants

### 1. Training Pipeline
- **Preprocessing** : TF-IDF vectorization
- **Modèle** : Random Forest ou LightGBM (baseline)
- **Tracking** : MLflow pour expériences et modèles
- **Versioning** : DVC pour les données

### 2. Deployment
- **API** : FastAPI pour prédictions
- **Containerisation** : Docker
- **CI/CD** : GitHub Actions

### 3. Monitoring
- **Métriques** : Prometheus
- **Visualisation** : Grafana
- **Drift Detection** : Détection automatique de dérive

### 4. Auto-Retrain
- **Déclenchement** : Automatique si drift détecté
- **A/B Testing** : Comparaison de modèles
- **Rollback** : Automatique si performance dégradée

## Flux de données

```
Données brutes → Preprocessing → Training → Modèle → API → Monitoring
                                                      ↓
                                              Auto-Retrain (si drift)
```

## Stack technique

- **ML** : scikit-learn, LightGBM
- **MLOps** : MLflow, DVC
- **API** : FastAPI, Uvicorn
- **Monitoring** : Prometheus, Grafana
- **Infra** : Docker, GitHub Actions

