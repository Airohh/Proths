# Prometheus - Pipeline MLOps

Pipeline MLOps pour la classification de documents. Train → Deploy → Monitor → Retrain.

## Démarrage rapide

```bash
cd mlops-pipeline
pip install -r requirements.txt
python scripts/generate_sample_data.py
python src/training/train.py
uvicorn src.inference.api:app --reload
```

API : http://localhost:8000  
Docs : [mlops-pipeline/README.md](mlops-pipeline/README.md)

## Stack

MLflow, DVC, FastAPI, Docker, Prometheus, Grafana
