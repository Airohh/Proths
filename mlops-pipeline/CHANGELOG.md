# Changelog

Lab MLOps local. Pas une plateforme 100 %.

## État réel

| Composant | État |
|-----------|------|
| Training (TF-IDF + RF / LightGBM + MLflow) | Démo OK |
| API FastAPI | Démo OK — charge `/latest` au boot |
| Prometheus / Grafana / alertes | Démo OK si l’API tourne sur l’hôte |
| Retrain manuel + compare F1 | Démo OK |
| Drift `train.csv` vs `drift.csv` | Démo OK (mix de labels + TF-IDF) |
| Reload API après promote | `POST /model/reload` |
| CI | Workflow à la racine |
| DVC / TimescaleDB / A/B / K8s | Hors périmètre |

## 2026-09

- AG News par défaut, F1 holdout ~0.73 dans `reports/metrics.json`
- Journal `/predict` → drift sur `predictions.csv`
- CI : boucle train → predict → drift
- Docs-cours / DVC / Timescale retirés ; API dans Compose
