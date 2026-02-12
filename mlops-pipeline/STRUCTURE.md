# Structure du Projet

```
mlops-pipeline/
├── README.md                       # Vue d'ensemble
├── QUICKSTART.md
├── CHANGELOG.md
├── STRUCTURE.md
│
├── config/
│   ├── config.yaml                 # Tous les paramètres
│   └── __init__.py                 # Chargement de la config
│
├── src/
│   ├── training/                   # Pipeline d'entraînement
│   │   ├── train.py                # Script d'entraînement
│   │   └── preprocessing.py        # Préparation des données
│   │
│   ├── inference/                  # API de prédiction
│   │   └── api.py                  # API FastAPI
│   │
│   ├── monitoring/                 # Monitoring
│   │   └── drift_detection.py      # Détection de drift
│   │
│   ├── retraining/                 # Auto-retrain
│   │   └── auto_retrain.py          # Pipeline d'auto-retrain
│   │
│   └── utils/                      # Utilitaires
│       ├── logger.py               # Logging structuré
│       └── validators.py           # Validation des données
│
├── tests/
│   ├── test_api.py
│   └── test_preprocessing.py
│
├── scripts/
│   ├── download_dataset.py         # Télécharger datasets
│   ├── prepare_ag_news.py          # Préparer AG News
│   ├── generate_sample_data.py     # Générer données de test
│   ├── generate_traffic.py         # Générer du trafic API
│   ├── trigger_retrain.py          # Déclencher retrain
│   ├── monitor_and_retrain.py      # Monitoring continu
│   ├── test_end_to_end.py          # Tests end-to-end
│   └── start_services.ps1          # Script PowerShell (Windows)
│
├── docker/
│   ├── Dockerfile                  # Image API
│   ├── Dockerfile.mlflow           # Image MLflow
│   ├── prometheus/
│   │   ├── prometheus.yml          # Config Prometheus
│   │   └── alerts.yml              # Alertes
│   └── grafana/
│       ├── dashboards/
│       │   └── mlops-dashboard.json # Dashboard pré-configuré
│       └── provisioning/           # Provisioning automatique
│
├── docs/
│   ├── EXPLICATION_COMPLETE.md     # Explication détaillée (821 lignes)
│   ├── AUTO_RETRAIN.md             # Guide auto-retrain
│   ├── MONITORING_SETUP.md         # Guide monitoring
│   ├── QU_EST_CE_QUE_MLOPS.md      # Concepts MLOps
│   ├── TOUS_LES_OUTILS_MLOPS.md    # Guide des outils
│   ├── CONCEPTS_AVANCES_MLOPS.md   # Concepts avancés
│   ├── architecture.md             # Architecture du système
│   ├── datasets.md                  # Guide des datasets
│   └── troubleshooting/            # Guides de dépannage
│       ├── README.md
│       ├── demarrage-services.md
│       ├── installation-docker.md
│       └── remplir-services.md
│
├── data/
│   ├── raw/                        # Données brutes
│   └── processed/                  # Données préprocessées
│
├── models/
├── mlruns/
│
├── docker-compose.yml
├── requirements.txt
├── Makefile
├── env.example
└── mlflow.yaml
```

## Fichiers Principaux

### Documentation

- **README.md** : Vue d'ensemble, structure, quick start, roadmap
- **QUICKSTART.md** : Démarrage rapide en 5 minutes
- **CHANGELOG.md** : Historique complet des changements et état du projet
- **docs/EXPLICATION_COMPLETE.md** : Explication détaillée de tout (821 lignes)

### Configuration

- **config/config.yaml** : Configuration centralisée (modèles, API, monitoring, retrain)
- **env.example** : Template pour les variables d'environnement
- **docker-compose.yml** : Services Docker (Prometheus, Grafana, MLflow, TimescaleDB)

### Code Source

- **src/training/** : Pipeline d'entraînement
- **src/inference/** : API FastAPI
- **src/monitoring/** : Détection de drift
- **src/retraining/** : Auto-retrain complet

## Organisation de la Documentation

### À la Racine

- **README.md** : Point d'entrée principal
- **QUICKSTART.md** : Démarrage rapide
- **CHANGELOG.md** : Historique

### Dans `docs/`

- **Guides techniques** : AUTO_RETRAIN.md, MONITORING_SETUP.md, etc.
- **Concepts** : QU_EST_CE_QUE_MLOPS.md, TOUS_LES_OUTILS_MLOPS.md
- **troubleshooting/** : Guides de dépannage

## Fichiers Supprimés (Nettoyage)

Les fichiers suivants ont été supprimés car redondants :

- RESUME_CHANGEMENTS.md → Fusionné dans CHANGELOG.md
- RESUME_FINAL.md → Fusionné dans CHANGELOG.md
- GUIDE_COMPLET.md → Remplacé par docs/EXPLICATION_COMPLETE.md
- SETUP.md → Remplacé par QUICKSTART.md
- DEMARRAGE_RAPIDE.md → Déplacé dans docs/troubleshooting/
- GUIDE_DEMARRAGE.md → Déplacé dans docs/troubleshooting/

## Fichiers Déplacés

- DEMARRER_DOCKER.md → docs/troubleshooting/installation-docker.md
- POPULER_SERVICES.md → docs/troubleshooting/remplir-services.md
- PROBLEME_DOCKER.md → docs/troubleshooting/installation-docker.md

## Structure Finale

**Organisation claire et logique** :
- 📄 Documentation principale à la racine
- Documentation : `docs/`
- Dépannage : `docs/troubleshooting/`
- 💻 Code source dans `src/`
- 🧪 Tests dans `tests/`
- 📜 Scripts dans `scripts/`
- 🐳 Docker dans `docker/`

