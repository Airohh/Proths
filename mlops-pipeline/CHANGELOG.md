# Changelog

## septembre 2026

- AG News par défaut, F1 holdout 0.73 dans `reports/metrics.json`
- chaque `/predict` écrit `predictions.csv` ; le drift lit ce fichier
- CI à la racine : train → predict → drift
- docs-cours, DVC et Timescale retirés
- API dans Compose, `POST /model/reload` après promote
