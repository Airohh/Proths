# 🚀 Quick Start - Pipeline MLOps

## Démarrage en 5 minutes

### 1. Installation

```bash
# Créer environnement virtuel
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Installer dépendances
pip install -r requirements.txt

# Initialiser DVC
dvc init
```

### 2. Générer des données de test

```bash
python scripts/generate_sample_data.py
```

### 3. Entraîner le modèle

```bash
python src/training/train.py
```

### 4. Lancer l'API

```bash
uvicorn src.inference.api:app --reload
```

### 5. Tester

```bash
# Dans un autre terminal
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"text": "artificial intelligence machine learning"}'
```

## 📊 Accéder aux services

- **API** : http://localhost:8000
- **MLflow UI** : http://localhost:5000 (lancer avec `mlflow ui`)
- **Prometheus** : http://localhost:9090 (après `docker-compose up`)
- **Grafana** : http://localhost:3000 (après `docker-compose up`)

## 🎯 Prochaines étapes

1. Explorer les métriques dans MLflow (http://localhost:5000)
2. Lancer l'API : `uvicorn src.inference.api:app --reload`
3. Générer du trafic : `python scripts/generate_traffic.py`
4. Vérifier Prometheus (http://localhost:9090) et Grafana (http://localhost:3000)
5. Tester l'auto-retrain : `python scripts/trigger_retrain.py --trigger manual`

## 📚 Documentation

- **README.md** : Vue d'ensemble complète
- **docs/EXPLICATION_COMPLETE.md** : Explication détaillée de tout
- **docs/troubleshooting/** : Guides de dépannage

