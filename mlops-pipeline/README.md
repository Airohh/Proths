# mlops-pipeline

Application du lab. Pitch et limites : [README racine](../README.md).

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/generate_sample_data.py
python scripts/generate_drift_data.py
python src/training/train.py --model-type random_forest
uvicorn src.inference.api:app --reload
# ou docker compose up -d --build
```

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"artificial intelligence machine learning\"}"
```

| Commande | Rôle |
|----------|------|
| `docker compose up -d --build` | API + MLflow + Prometheus + Grafana |
| `python scripts/generate_traffic.py` | Charge l’API pour remplir les dashboards |
| `python scripts/trigger_retrain.py --trigger drift --current-data data/processed/drift.csv` | Drift à deux CSV + promote + reload |
| `pytest tests/ -v` | Tests unitaires (passent sans modèle) |

Docs utiles : [QUICKSTART](QUICKSTART.md) · [architecture](docs/architecture.md) · [retrain](docs/AUTO_RETRAIN.md) · [monitoring](docs/MONITORING_SETUP.md) · [datasets](docs/datasets.md)
