# Pipeline MLOps - Classification de Documents

Pipeline MLOps end-to-end pour classification de documents avec monitoring, auto-retrain et déploiement automatisé.

## 🎯 Objectif

Démontrer la maîtrise de l'industrialisation de l'IA avec un pipeline complet : **Train → Deploy → Monitor → Retrain**

## 📁 Structure du Projet

```
mlops-pipeline/
├── data/
│   ├── raw/              # Données brutes
│   ├── processed/        # Données préprocessées
│   └── .dvc/             # Versioning DVC
├── models/               # Modèles sauvegardés
├── src/
│   ├── training/         # Code d'entraînement
│   ├── inference/        # Code de prédiction
│   ├── monitoring/       # Code de monitoring
│   ├── retraining/       # Code d'auto-retrain
│   └── utils/            # Utilitaires
├── tests/                # Tests unitaires
├── docker/               # Configs Docker
├── .github/workflows/    # CI/CD
├── notebooks/            # Notebooks d'exploration
└── docs/                 # Documentation
```

## 🛠️ Stack Technique

- **MLflow** : Tracking d'expériences, registry de modèles
- **DVC** : Versioning des données
- **FastAPI** : API de prédiction
- **Docker** : Containerisation
- **GitHub Actions** : CI/CD
- **Prometheus** : Collecte de métriques
- **Grafana** : Visualisation
- **TimescaleDB** : Stockage métriques temporelles

## 🚀 Quick Start

### Installation

```bash
# Cloner le repo
git clone <repo-url>
cd mlops-pipeline

# Créer environnement virtuel
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Installer dépendances
pip install -r requirements.txt

# Setup DVC
dvc init
dvc remote add -d storage <remote-storage>

# Setup MLflow
mlflow ui --port 5000
```

### Training

```bash
python src/training/train.py
```

### API

```bash
uvicorn src.inference.api:app --reload
```

### Monitoring

**Option 1 : Avec Docker** (Prometheus + Grafana)
```bash
# Lancer Prometheus et Grafana
docker-compose up -d

# Accéder aux services:
# - Prometheus: http://localhost:9090
# - Grafana: http://localhost:3000 (admin/admin)
```

**Option 2 : Sans Docker** (MLflow UI seulement)
```bash
# Lancer MLflow UI
mlflow ui --port 5000

# Accéder: http://localhost:5000
```

**Note** : Si Docker n'est pas installé, voir `docs/troubleshooting/installation-docker.md`

### Auto-Retrain

```bash
# Retrain manuel
python scripts/trigger_retrain.py --trigger manual

# Retrain avec détection de drift
python scripts/trigger_retrain.py --trigger drift

# Monitoring continu avec auto-retrain
python scripts/monitor_and_retrain.py

# Une seule vérification
python scripts/monitor_and_retrain.py --once
```

### Tests End-to-End

```bash
# Tester le pipeline complet
python scripts/test_end_to_end.py
```

## 📊 Métriques Trackées

- **Performance** : Accuracy, Precision, Recall, F1, Latence, Throughput
- **Coûts** : Coût par prédiction, Infrastructure, Training
- **Qualité** : Drift score, Data quality, Model performance over time

## 📈 Roadmap

- [x] Structure du projet
- [x] Setup MLflow + DVC
- [x] Pipeline de training
- [x] API FastAPI
- [x] Monitoring Prometheus/Grafana
- [x] Auto-retrain
- [x] CI/CD
- [x] Dashboards Grafana pré-configurés
- [x] Alertes Prometheus
- [ ] A/B Testing avancé

## 📝 Documentation

### Guides Principaux
- **🚀 [QUICKSTART.md](QUICKSTART.md)** : Démarrage rapide en 5 minutes
- **📚 [docs/EXPLICATION_COMPLETE.md](docs/EXPLICATION_COMPLETE.md)** : Explication détaillée de tout (821 lignes)
- **📋 [CHANGELOG.md](CHANGELOG.md)** : Historique des changements et état du projet

### Guides Techniques
- **🔄 [docs/AUTO_RETRAIN.md](docs/AUTO_RETRAIN.md)** : Guide complet de l'auto-retrain
- **📊 [docs/MONITORING_SETUP.md](docs/MONITORING_SETUP.md)** : Guide du monitoring (Prometheus + Grafana)
- **🤖 [docs/QU_EST_CE_QUE_MLOPS.md](docs/QU_EST_CE_QUE_MLOPS.md)** : Concepts MLOps
- **🛠️ [docs/TOUS_LES_OUTILS_MLOPS.md](docs/TOUS_LES_OUTILS_MLOPS.md)** : Guide des outils utilisés
- **🚀 [docs/CONCEPTS_AVANCES_MLOPS.md](docs/CONCEPTS_AVANCES_MLOPS.md)** : Concepts avancés

### Dépannage
- **🔧 [docs/troubleshooting/](docs/troubleshooting/)** : Guides de résolution de problèmes

## 🔗 Liens Utiles

- [MLflow](https://mlflow.org/)
- [DVC](https://dvc.org/)
- [Prometheus](https://prometheus.io/)
- [Grafana](https://grafana.com/)

