# mlops-pipeline

Application du lab. Pitch et F1 : [README racine](../README.md).

```bash
pip install -r requirements.txt
python scripts/prepare_ag_news.py
python src/training/train.py --model-type random_forest
uvicorn src.inference.api:app --reload
```

```bash
python scripts/generate_traffic.py --skew sports --requests 30 --delay 0.2
python scripts/trigger_retrain.py --trigger drift --current-data data/processed/predictions.csv
```

| Commande | Rôle |
|----------|------|
| `docker compose up -d --build` | API + MLflow + Prometheus + Grafana |
| `pytest tests/ -q` | unitaires + boucle train/predict/drift |

Docs : [QUICKSTART](QUICKSTART.md) · [architecture](docs/architecture.md) · [retrain](docs/AUTO_RETRAIN.md) · [metrics](reports/metrics.json)
