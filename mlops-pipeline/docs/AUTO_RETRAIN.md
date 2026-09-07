# Retrain

| Trigger | Comportement |
|---------|----------------|
| `manual` | Réentraîne le CSV, compare le F1, promote si gain ≥ 0.01, `POST /model/reload` |
| `drift` | Compare `train.csv` au **journal des prédictions** (`data/processed/predictions.csv`). Score = max(moyennes TF-IDF, mix des **labels prédits**). Si seuil dépassé : concatène, réentraîne, promote, reload |
| `schedule` | Comme manual (pas de cron) |

```bash
python scripts/prepare_ag_news.py
python src/training/train.py --model-type random_forest
# API up, puis :
python scripts/generate_traffic.py --skew sports --requests 30 --delay 0.2
python scripts/trigger_retrain.py --trigger drift --current-data data/processed/predictions.csv
```

Le journal n’a pas de vérité terrain : on compare le mix **prédit** au mix du train. Sans fichier courant, le trigger drift refuse.

`generate_drift_data.py` reste un fallback synthétique si l’API n’a pas encore tourné.
