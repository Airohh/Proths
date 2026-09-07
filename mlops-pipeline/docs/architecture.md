# Architecture

Lab local. Boucle visée : **Train → Registry → Serve → Observe → Retrain**.

```
AG News ──► TF-IDF ──► Random Forest ──► MLflow (run + registry)
                                              │
                                              ▼
                                         FastAPI /predict
                                              │
                                         /metrics ──► Prometheus ──► Grafana
                                              │
                         drift vs journal /predict (predictions.csv)
                                              │
                         promote Production si ΔF1 ≥ 0.01 ──► POST /model/reload
```

| Brique | Rôle réel |
|--------|-----------|
| `src/training/` | Fit TF-IDF + modèle, log MLflow |
| `src/inference/` | `Production` → `latest` → pickle local. `POST /model/reload` |
| `src/monitoring/` | max(moyennes TF-IDF, mix de labels). Pas un KS / PSI |
| `src/retraining/` | Compare F1, promote, ping reload. Pas d’A/B, pas de rollback auto |
| Compose | API + MLflow + Prometheus + Grafana |

Hors périmètre (volontairement absent) : DVC, TimescaleDB, Kubernetes, feature store, auth.
