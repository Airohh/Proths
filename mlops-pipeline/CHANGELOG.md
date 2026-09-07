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

- README honnête, licence MIT, docs-cours / DVC / Timescale retirés
- Drift à deux CSV, API dans Compose, charge Production + reload
