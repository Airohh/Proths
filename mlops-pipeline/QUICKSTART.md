# Quick start

Depuis `mlops-pipeline/` :

```bash
pip install -r requirements.txt
python scripts/generate_sample_data.py
python scripts/generate_drift_data.py
python src/training/train.py --model-type random_forest
```

API seule :

```bash
uvicorn src.inference.api:app --reload
```

Stack complète (après le train) :

```bash
docker compose up -d --build
```

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"artificial intelligence machine learning\"}"

python scripts/trigger_retrain.py --trigger drift --current-data data/processed/drift.csv
```

- API : http://localhost:8000/docs
- MLflow : http://localhost:5000
- Prometheus : http://localhost:9090
- Grafana : http://localhost:3000 (`admin` / `admin`)
