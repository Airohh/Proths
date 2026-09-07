# Proths — pipeline MLOps (classification de documents)

Le modèle est un **baseline** (TF-IDF + Random Forest). Le dépôt montre la **boucle** : entraîner, servir, journaliser, détecter un shift, ne redéployer que si le F1 monte.

```
Train → Deploy → Monitor → Retrain
```

Détail dans [`mlops-pipeline/`](mlops-pipeline/).

---

## Résultat (AG News)

Random Forest, TF-IDF 5k 1–2 grams, **4 000** articles train / **800** holdout (split test officiel, seed 42).

| Split | n | Accuracy | F1 pondéré |
|-------|---|----------|------------|
| Validation (20 % du train) | 800 | 0.724 | **0.725** |
| Holdout AG News `test` | 800 | 0.729 | **0.728** |

Val et holdout sont alignés : pas de miracle, pas de fuite évidente. Un transformer ferait mieux ; ici le sujet est la boucle, pas le SOTA.

Chiffres : [`mlops-pipeline/reports/metrics.json`](mlops-pipeline/reports/metrics.json).

---

## Ce que ça fait

Un article arrive sur l’API. TF-IDF → RF → label + confiance. Chaque prédiction est **écrite** dans `data/processed/predictions.csv`. Le drift compare le train à ce journal (mix des **labels prédits** + moyennes TF-IDF). S’il passe le seuil : retrain sur train+journal, promote si ΔF1 ≥ 0.01, `POST /model/reload`.

```
AG News ──► TF-IDF ──► Random Forest ──► MLflow
                              │
                         FastAPI /predict
                              │
                    predictions.csv ──► drift vs train
                              │
                    promote Production + /model/reload
                              │
                         Prometheus → Grafana
```

| Étape | Réel |
|--------|------|
| **Train** | AG News (HF), split 80/20 + holdout, MLflow `document-classification` |
| **Deploy** | `Production` → `latest` → pickle. `POST /model/reload` |
| **Monitor** | Prometheus + **journal des prédictions** |
| **Retrain** | Drift sur le journal, pas un CSV fantaisiste |

---

## Démarrage rapide

```bash
git clone https://github.com/Airohh/Proths.git
cd Proths/mlops-pipeline
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt

python scripts/prepare_ag_news.py
python src/training/train.py --model-type random_forest
uvicorn src.inference.api:app --reload
# ou: docker compose up -d --build
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

| Service | URL |
|---------|-----|
| API | http://localhost:8000/docs |
| MLflow | http://localhost:5000 |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 (`admin` / `admin`) |

Sans `predictions.csv` (pas encore de trafic), le trigger drift refuse.

---

## Stack

scikit-learn · MLflow · FastAPI · Prometheus / Grafana · Docker Compose · GitHub Actions

---

## Limites

- **Baseline.** F1 holdout ~0.73 sur AG News, pas un LLM.
- **Drift lab.** Le journal n’a pas de label vrai : on compare le mix **prédit** au train. Seuil simple (pas PSI / KS).
- **Pas d’A/B, pas de DVC, pas de TimescaleDB.**
- **Reload explicite.** CORS `*`.

---

| Doc | Contenu |
|-----|---------|
| [`mlops-pipeline/QUICKSTART.md`](mlops-pipeline/QUICKSTART.md) | enchaînement court |
| [`mlops-pipeline/docs/architecture.md`](mlops-pipeline/docs/architecture.md) | composants |
| [`mlops-pipeline/docs/AUTO_RETRAIN.md`](mlops-pipeline/docs/AUTO_RETRAIN.md) | drift sur le journal |
| [`mlops-pipeline/reports/metrics.json`](mlops-pipeline/reports/metrics.json) | F1 val / holdout |

Licence [MIT](LICENSE).
