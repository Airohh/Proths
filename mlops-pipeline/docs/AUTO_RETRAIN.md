# Retrain

| Trigger | Comportement |
|---------|----------------|
| `manual` | Réentraîne le CSV, compare le F1, promote `Production` si gain ≥ 0.01, puis `POST /model/reload` |
| `drift` | Compare `train.csv` à `--current-data`. Score = max(moyennes TF-IDF, distance du mix de labels). Si seuil dépassé : concatène les deux CSV, réentraîne, promote, reload |
| `schedule` | Même chemin que manual (pas de cron branché) |

```bash
python scripts/generate_sample_data.py
python scripts/generate_drift_data.py
python scripts/trigger_retrain.py --trigger drift --current-data data/processed/drift.csv
python scripts/monitor_and_retrain.py --once
```

Sans `--current-data`, le trigger drift refuse (pas de comparaison du train à lui-même).

**Ce qui n’existe pas :** collecte des textes de l’API, A/B 50/50, rollback automatique.
