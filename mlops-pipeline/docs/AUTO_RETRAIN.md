# Retrain

| Trigger | Ce que ça fait |
|---------|----------------|
| `manual` | Réentraîne le CSV, compare le F1, promote si gain ≥ 0.01, `POST /model/reload` |
| `drift` | Compare `train.csv` à `data/processed/predictions.csv`. Score = max(moyennes TF-IDF, mix des labels prédits). Au-dessus du seuil : concatène, réentraîne, promote, reload |
| `schedule` | Pareil que manual (pas de cron) |

```bash
python scripts/prepare_ag_news.py
python src/training/train.py --model-type random_forest
# API allumée, puis :
python scripts/generate_traffic.py --skew sports --requests 30 --delay 0.2
python scripts/trigger_retrain.py --trigger drift --current-data data/processed/predictions.csv
```

Le journal n’a pas les vrais labels. Sans `predictions.csv`, le trigger drift refuse.

Si l’API n’a pas encore tourné : `python scripts/generate_drift_data.py`.
