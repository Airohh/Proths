# Proths — pipeline MLOps (classification de documents)

Le modèle est volontairement un **baseline** (TF-IDF + Random Forest / LightGBM). Ce que le dépôt montre, c’est la **boucle de production** : entraîner, enregistrer, servir, observer, et ne redéployer que si le nouveau modèle est vraiment meilleur.

```
Train → Deploy → Monitor → Retrain
```

Le détail opérationnel reste dans [`mlops-pipeline/`](mlops-pipeline/). Ce README est l’entrée portfolio.

---

## Ce que ça fait

Un texte arrive sur l’API. Il est vectorisé (TF-IDF, 1–2 grams), classé, et les métriques partent vers Prometheus. Un **retrain manuel** réentraîne, compare le F1, et ne promeut en `Production` que si le gain est ≥ `0.01`. Le **drift** compare `train.csv` à `drift.csv` (mix de classes + moyennes TF-IDF) ; s’il passe le seuil, on réentraîne sur les deux CSV, on promote, puis `POST /model/reload`.

Jeu de démo : 5 classes synthétiques (`technology`, `science`, `sports`, `business`, `health`). Les scripts savent aussi charger AG News / jeux Hugging Face — voir [`mlops-pipeline/docs/datasets.md`](mlops-pipeline/docs/datasets.md).

```
texte ──► TF-IDF ──► RF / LightGBM ──► label + confiance
                │                         │
                │                    /metrics
                ▼                         ▼
         MLflow (runs + registry)    Prometheus → Grafana
                ▲                         │
                └──── retrain manuel ou drift (2 CSV)
                      promote Production + /model/reload
```

| Étape | Ce qui tourne vraiment |
|--------|-------------------------|
| **Train** | `src/training/train.py` — split 80/20, accuracy / precision / recall / F1, run MLflow `document-classification` |
| **Deploy** | FastAPI charge `Production`, sinon `latest`, sinon pickle local. `POST /model/reload` après promote |
| **Monitor** | Compteurs Prometheus. Alertes : taux d’erreur, modèle absent, P95 > 1 s, plus aucune prédiction |
| **Retrain** | Manuel, ou drift `train.csv` vs `drift.csv`. Promote si ΔF1 ≥ 0.01, puis reload API |

---

## Démarrage rapide

Python 3.9+, Docker facultatif (monitoring).

```bash
git clone https://github.com/Airohh/Proths.git
cd Proths/mlops-pipeline

python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt

python scripts/generate_sample_data.py
python scripts/generate_drift_data.py
python src/training/train.py --model-type random_forest
uvicorn src.inference.api:app --reload
# ou: docker compose up -d --build   (API + MLflow + Prometheus + Grafana)
```

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"artificial intelligence machine learning\"}"
```

Réponse typique : `prediction`, `confidence`, `probabilities` par classe. Swagger : `http://localhost:8000/docs`.

### Monitoring (optionnel)

Compose lance **API, MLflow, Prometheus et Grafana**. Entraîne d’abord sur l’hôte pour remplir `models/` et `mlruns/`.

```bash
docker compose up -d
python scripts/generate_traffic.py
```

| Service | URL | Notes |
|---------|-----|--------|
| API | http://localhost:8000 | `/docs`, `/metrics` |
| MLflow | http://localhost:5000 | tracking + registry |
| Prometheus | http://localhost:9090 | scrape API + règles d’alerte |
| Grafana | http://localhost:3000 | `admin` / `admin`, dashboard provisionné |

### Retrain

```bash
python scripts/trigger_retrain.py --trigger manual
python scripts/trigger_retrain.py --trigger drift --current-data data/processed/drift.csv
python scripts/monitor_and_retrain.py --once
```

Sans `--current-data`, le trigger drift refuse (score 0, pas de faux positif).

---

## Stack

| Brique | Rôle ici |
|--------|----------|
| scikit-learn / LightGBM | baselines classif texte |
| MLflow | expériences, artefacts, stage `Production` |
| FastAPI | inférence + `/metrics` |
| Prometheus / Grafana | latence, erreurs, santé modèle |
| Docker Compose | API + MLflow + Prometheus + Grafana |
| GitHub Actions | pytest à la racine du repo |

---

## Limites (lues honnêtement)

- **Le modèle n’est pas le sujet.** TF-IDF + forêt / boosting, pas un transformer. La démo tourne sur des phrases-mots-clés générées, pas un corpus métier.
- **Le drift est un lab.** Mix de labels (CSV étiquetés) + moyennes TF-IDF. Pas un PSI / KS de prod, pas de collecte des textes de l’API.
- **Pas d’A/B, pas de DVC, pas de TimescaleDB.**
- **Reload explicite.** Promote MLflow puis `POST /model/reload` (le retrain le tente tout seul). CORS ouvert (`*`).

---

## Structure

```
Proths/
├── README.md                 ← vous êtes ici
├── LICENSE
└── mlops-pipeline/           ← application
    ├── src/training/         entraînement + TF-IDF
    ├── src/inference/        FastAPI
    ├── src/monitoring/       drift
    ├── src/retraining/       comparaison + promotion
    ├── scripts/              données, trafic, retrain, e2e
    ├── docker/               Prometheus, Grafana, Dockerfiles
    ├── docs/                 guides + dépannage
    └── tests/
```

| Doc | Contenu |
|-----|---------|
| [`mlops-pipeline/QUICKSTART.md`](mlops-pipeline/QUICKSTART.md) | enchaînement court |
| [`mlops-pipeline/docs/architecture.md`](mlops-pipeline/docs/architecture.md) | composants |
| [`mlops-pipeline/docs/AUTO_RETRAIN.md`](mlops-pipeline/docs/AUTO_RETRAIN.md) | triggers et comparaison |
| [`mlops-pipeline/docs/MONITORING_SETUP.md`](mlops-pipeline/docs/MONITORING_SETUP.md) | Prometheus / Grafana |
| [`mlops-pipeline/docs/datasets.md`](mlops-pipeline/docs/datasets.md) | AG News, Hugging Face, Kaggle |
| [`mlops-pipeline/docs/troubleshooting/`](mlops-pipeline/docs/troubleshooting/) | Docker, dashboards vides, métriques |

---

Licence [MIT](LICENSE).
