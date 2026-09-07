# Proths

Pipeline MLOps en local. Le modèle classe des articles (TF-IDF + Random Forest, dataset AG News). L’idée : entraîner, servir, garder les prédictions, voir si le trafic a bougé, réentraîner, et ne passer en Production que si le F1 monte.

Le code est dans [`mlops-pipeline/`](mlops-pipeline/).

## Résultat

4000 articles en train, 800 en holdout (split test officiel AG News, seed 42).

| Split | n | Accuracy | F1 pondéré |
|-------|---|----------|------------|
| Validation (20 % du train) | 800 | 0.724 | 0.725 |
| Holdout | 800 | 0.729 | 0.728 |

Fichier : [`mlops-pipeline/reports/metrics.json`](mlops-pipeline/reports/metrics.json).

## Comment ça s’enchaîne

L’API (`/predict`) écrit chaque prédiction dans `data/processed/predictions.csv`.

Le drift compare ce journal au train : mix des labels **prédits** + moyennes TF-IDF. S’il dépasse le seuil, on réentraîne sur train + journal. Si le F1 gagne au moins 0.01, le modèle passe Production et l’API le recharge (`POST /model/reload`).

Le journal n’a pas les vrais labels. Le drift est donc approximatif (pas PSI, pas KS). Pas de DVC, pas de Kubernetes.

## Lancer

```bash
git clone https://github.com/Airohh/Proths.git
cd Proths/mlops-pipeline
python -m venv .venv
# Windows : .venv\Scripts\activate
pip install -r requirements.txt

python scripts/prepare_ag_news.py
python src/training/train.py --model-type random_forest
uvicorn src.inference.api:app --reload
```

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"Oil prices fall as OPEC signals higher output\"}"
```

```bash
python scripts/generate_traffic.py --skew sports --requests 30 --delay 0.2
python scripts/trigger_retrain.py --trigger drift --current-data data/processed/predictions.csv
```

Sans `predictions.csv`, le trigger drift refuse. C’est voulu.

| Service | URL |
|---------|-----|
| API | http://localhost:8000/docs |
| MLflow | http://localhost:5000 |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 (`admin` / `admin`) |

`docker compose up -d --build` lance API + MLflow + Prometheus + Grafana.

## Stack

scikit-learn, MLflow, FastAPI, Prometheus, Grafana, Docker Compose, GitHub Actions

## Docs

- [`mlops-pipeline/QUICKSTART.md`](mlops-pipeline/QUICKSTART.md)
- [`mlops-pipeline/docs/architecture.md`](mlops-pipeline/docs/architecture.md)
- [`mlops-pipeline/docs/AUTO_RETRAIN.md`](mlops-pipeline/docs/AUTO_RETRAIN.md)

Licence [MIT](LICENSE).
