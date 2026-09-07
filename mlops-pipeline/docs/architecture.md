# Architecture

Tout tourne en local.

```
AG News → TF-IDF → Random Forest → MLflow
                FastAPI /predict
                predictions.csv
                drift vs train
                promote si le F1 monte → POST /model/reload
                Prometheus → Grafana
```

| Dossier | Rôle |
|---------|------|
| `src/training/` | Fit, log MLflow |
| `src/inference/` | Charge Production, sinon latest, sinon le pickle. `POST /model/reload` |
| `src/monitoring/` | Drift : moyennes TF-IDF + mix de labels |
| `src/retraining/` | Compare le F1, promote, ping reload |
| Compose | API, MLflow, Prometheus, Grafana |

Pas de DVC, pas de Timescale, pas de K8s, pas d’auth.
