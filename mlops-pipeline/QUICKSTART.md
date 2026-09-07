# Quick start

```bash
pip install -r requirements.txt
python scripts/prepare_ag_news.py
python src/training/train.py --model-type random_forest
uvicorn src.inference.api:app --reload
```

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"Oil prices fall as OPEC signals higher output\"}"

python scripts/generate_traffic.py --skew sports --requests 30 --delay 0.2
python scripts/trigger_retrain.py --trigger drift --current-data data/processed/predictions.csv
```

Fallback sans réseau Hugging Face : `python scripts/generate_sample_data.py`.
