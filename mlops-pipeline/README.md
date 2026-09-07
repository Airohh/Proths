# mlops-pipeline

Code du repo. Le README et les scores sont à la [racine](../README.md).

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

`docker compose up -d --build` : API + MLflow + Prometheus + Grafana.

`pytest tests/ -q` : unitaires + un test qui enchaîne train / predict / drift.

- [Quick start](QUICKSTART.md)
- [Architecture](docs/architecture.md)
- [Retrain](docs/AUTO_RETRAIN.md)
- [metrics.json](reports/metrics.json)
