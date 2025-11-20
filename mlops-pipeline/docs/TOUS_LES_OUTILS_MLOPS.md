# 🛠️ Tous les Outils MLOps - Guide Complet

Ce guide explique **tous les outils** utilisés dans votre projet MLOps, avec des explications simples et des exemples concrets.

---

## 📊 Table des Matières

1. [Outils de Machine Learning](#outils-de-machine-learning)
2. [Outils MLOps](#outils-mlops)
3. [Outils de Déploiement](#outils-de-déploiement)
4. [Outils de Monitoring](#outils-de-monitoring)
5. [Outils d'Infrastructure](#outils-dinfrastructure)
6. [Outils de Qualité de Code](#outils-de-qualité-de-code)

---

## 🤖 Outils de Machine Learning

### 1. **scikit-learn**

**Qu'est-ce que c'est ?**
La bibliothèque Python la plus populaire pour le machine learning.

**À quoi ça sert ?**
- Entraîner des modèles (Random Forest, SVM, etc.)
- Préparer les données (preprocessing)
- Évaluer les modèles (métriques)

**Dans votre projet :**
```python
# src/training/train.py
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)
accuracy = accuracy_score(y_val, y_pred)
```

**Pourquoi l'utiliser ?**
- ✅ Simple à utiliser
- ✅ Bien documenté
- ✅ Compatible avec MLflow
- ✅ Parfait pour commencer

**Site officiel :** https://scikit-learn.org/

---

### 2. **LightGBM**

**Qu'est-ce que c'est ?**
Un framework de gradient boosting très rapide et performant.

**À quoi ça sert ?**
- Entraîner des modèles de boosting (meilleure performance que Random Forest souvent)
- Gérer de gros datasets efficacement

**Dans votre projet :**
```python
# src/training/train.py
import lightgbm as lgb

model = lgb.LGBMClassifier(
    n_estimators=100,
    max_depth=10,
    learning_rate=0.1
)
```

**Pourquoi l'utiliser ?**
- ✅ Très rapide
- ✅ Très performant
- ✅ Gère bien les gros datasets
- ✅ Alternative moderne à XGBoost

**Site officiel :** https://lightgbm.readthedocs.io/

---

### 3. **pandas**

**Qu'est-ce que c'est ?**
La bibliothèque Python pour manipuler des données tabulaires (comme Excel).

**À quoi ça sert ?**
- Lire/écrire des fichiers CSV
- Manipuler des DataFrames
- Nettoyer les données

**Dans votre projet :**
```python
# scripts/prepare_ag_news.py
import pandas as pd

df = pd.read_csv("data/raw/train.csv")
df['label'] = df['label'].map(LABEL_MAPPING)
df.to_csv("data/processed/train.csv", index=False)
```

**Pourquoi l'utiliser ?**
- ✅ Standard de l'industrie
- ✅ Facile à utiliser
- ✅ Très puissant

**Site officiel :** https://pandas.pydata.org/

---

### 4. **numpy**

**Qu'est-ce que c'est ?**
La bibliothèque Python pour les calculs numériques (matrices, arrays).

**À quoi ça sert ?**
- Calculs mathématiques
- Manipulation de tableaux
- Base de beaucoup de bibliothèques ML

**Dans votre projet :**
```python
import numpy as np

# Utilisé partout pour les calculs
drift_score = np.mean(np.abs(ref_mean - curr_mean))
```

**Pourquoi l'utiliser ?**
- ✅ Très rapide (écrit en C)
- ✅ Standard de l'industrie
- ✅ Utilisé par scikit-learn, pandas, etc.

**Site officiel :** https://numpy.org/

---

## 🔄 Outils MLOps

### 5. **MLflow**

**Qu'est-ce que c'est ?**
L'outil le plus populaire pour gérer le cycle de vie des modèles ML.

**À quoi ça sert ?**
- **Tracking** : Enregistrer toutes vos expériences (paramètres, métriques)
- **Model Registry** : Versionner et gérer vos modèles
- **Deployment** : Déployer des modèles facilement

**Dans votre projet :**
```python
# src/training/train.py
import mlflow
import mlflow.sklearn

with mlflow.start_run():
    mlflow.log_param("model_type", "random_forest")
    mlflow.log_metric("accuracy", 0.92)
    mlflow.sklearn.log_model(model, "model", 
                            registered_model_name="document-classifier")
```

**Interface Web :**
- URL : http://localhost:5000
- Vous pouvez voir toutes vos expériences
- Comparer les modèles
- Télécharger des modèles

**Pourquoi l'utiliser ?**
- ✅ Gratuit et open-source
- ✅ Compatible avec tous les frameworks ML
- ✅ Interface web intuitive
- ✅ Standard de l'industrie

**Site officiel :** https://mlflow.org/

**Commandes utiles :**
```bash
# Lancer l'interface web
mlflow ui --port 5000

# Voir les runs
mlflow runs list

# Charger un modèle
mlflow.sklearn.load_model("models:/document-classifier/latest")
```

---

### 6. **DVC (Data Version Control)**

**Qu'est-ce que c'est ?**
Comme Git, mais pour les données et les modèles.

**À quoi ça sert ?**
- Versionner les datasets (comme Git versionne le code)
- Stocker les gros fichiers dans le cloud
- Reproduire des expériences avec les bonnes données

**Dans votre projet :**
```bash
# Versionner un dataset
dvc add data/processed/train.csv

# Télécharger une version spécifique
dvc checkout

# Envoyer au stockage distant
dvc push
```

**Pourquoi l'utiliser ?**
- ✅ Git ne peut pas gérer les gros fichiers
- ✅ Reproducibilité garantie
- ✅ Collaboration facilitée
- ✅ Économie d'espace

**Site officiel :** https://dvc.org/

**Voir aussi :** `docs/DVC_EXPLICATION.md`

---

## 🚀 Outils de Déploiement

### 7. **FastAPI**

**Qu'est-ce que c'est ?**
Un framework Python moderne et rapide pour créer des APIs REST.

**À quoi ça sert ?**
- Créer une API pour servir vos modèles
- Recevoir des requêtes HTTP
- Retourner des prédictions

**Dans votre projet :**
```python
# src/inference/api.py
from fastapi import FastAPI

app = FastAPI()

@app.post("/predict")
async def predict(document: DocumentInput):
    prediction = model.predict([document.text])
    return {"prediction": prediction}
```

**Avantages :**
- ✅ Très rapide (plus rapide que Flask)
- ✅ Documentation automatique (Swagger)
- ✅ Validation automatique des données
- ✅ Support async/await

**Site officiel :** https://fastapi.tiangolo.com/

**Endpoints dans votre projet :**
- `GET /` : Health check
- `GET /health` : Health check détaillé
- `POST /predict` : Prédiction pour un document
- `POST /predict/batch` : Prédiction pour plusieurs documents
- `GET /metrics` : Métriques Prometheus
- `GET /docs` : Documentation Swagger

---

### 8. **Uvicorn**

**Qu'est-ce que c'est ?**
Un serveur ASGI (Asynchronous Server Gateway Interface) pour Python.

**À quoi ça sert ?**
- Lancer votre API FastAPI
- Gérer les requêtes HTTP
- Support async/await

**Dans votre projet :**
```bash
# Lancer l'API
uvicorn src.inference.api:app --reload
```

**Pourquoi l'utiliser ?**
- ✅ Très rapide
- ✅ Support async
- ✅ Standard pour FastAPI
- ✅ Auto-reload en développement

**Site officiel :** https://www.uvicorn.org/

---

### 9. **Docker**

**Qu'est-ce que c'est ?**
Un système de containerisation qui permet d'emballer une application avec toutes ses dépendances.

**À quoi ça sert ?**
- Créer des images de votre application
- Déployer de manière reproductible
- Isoler les environnements

**Dans votre projet :**
```dockerfile
# docker/Dockerfile
FROM python:3.9
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "src.inference.api:app", "--host", "0.0.0.0"]
```

**Commandes utiles :**
```bash
# Construire l'image
docker build -t mlops-api .

# Lancer le container
docker run -p 8000:8000 mlops-api

# Voir les containers
docker ps
```

**Pourquoi l'utiliser ?**
- ✅ "Ça marche sur ma machine" → résolu
- ✅ Reproducibilité garantie
- ✅ Facile à déployer
- ✅ Isolation des dépendances

**Site officiel :** https://www.docker.com/

---

### 10. **Docker Compose**

**Qu'est-ce que c'est ?**
Un outil pour gérer plusieurs containers Docker ensemble.

**À quoi ça sert ?**
- Lancer plusieurs services en même temps (API, MLflow, Prometheus, Grafana)
- Configurer les réseaux entre services
- Gérer les volumes (stockage)

**Dans votre projet :**
```yaml
# docker-compose.yml
services:
  mlflow:
    build: ./docker/Dockerfile.mlflow
    ports:
      - "5000:5000"
  
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
  
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
```

**Commandes utiles :**
```bash
# Lancer tous les services
docker-compose up -d

# Arrêter tous les services
docker-compose down

# Voir les logs
docker-compose logs
```

**Pourquoi l'utiliser ?**
- ✅ Facile de gérer plusieurs services
- ✅ Configuration centralisée
- ✅ Réseau automatique entre services

**Site officiel :** https://docs.docker.com/compose/

---

## 📊 Outils de Monitoring

### 11. **Prometheus**

**Qu'est-ce que c'est ?**
Un système de monitoring et d'alerte open-source.

**À quoi ça sert ?**
- Collecter des métriques (latence, erreurs, etc.)
- Stocker les métriques dans une base de données temporelle
- Créer des alertes

**Dans votre projet :**
```python
# src/inference/api.py
from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter('api_requests_total', 'Total requests')
REQUEST_LATENCY = Histogram('api_latency_seconds', 'Request latency')

@app.post("/predict")
async def predict(...):
    REQUEST_COUNT.inc()
    with REQUEST_LATENCY.time():
        # Votre code
        pass
```

**Interface Web :**
- URL : http://localhost:9090
- Vous pouvez voir toutes les métriques
- Créer des requêtes (PromQL)
- Configurer des alertes

**Pourquoi l'utiliser ?**
- ✅ Standard de l'industrie
- ✅ Très puissant
- ✅ Intégration facile
- ✅ Gratuit et open-source

**Site officiel :** https://prometheus.io/

**Métriques dans votre projet :**
- `api_requests_total` : Nombre total de requêtes
- `api_latency_seconds` : Temps de réponse
- `predictions_total` : Nombre de prédictions
- `prediction_errors_total` : Nombre d'erreurs
- `model_loaded` : État du modèle (1 = chargé, 0 = non chargé)

---

### 12. **Grafana**

**Qu'est-ce que c'est ?**
Un outil de visualisation et d'analyse de données.

**À quoi ça sert ?**
- Créer des graphiques à partir des métriques Prometheus
- Créer des dashboards
- Configurer des alertes visuelles

**Dans votre projet :**
- URL : http://localhost:3000
- Login : admin / admin (par défaut)
- Se connecte à Prometheus pour récupérer les métriques

**Pourquoi l'utiliser ?**
- ✅ Visualisations magnifiques
- ✅ Dashboards personnalisables
- ✅ Alertes visuelles
- ✅ Gratuit et open-source

**Site officiel :** https://grafana.com/

**Dashboards typiques :**
- Performance de l'API (latence, throughput)
- Erreurs et exceptions
- Utilisation des ressources (CPU, mémoire)
- Métriques du modèle (accuracy, confiance)

---

## 🏗️ Outils d'Infrastructure

### 13. **GitHub Actions**

**Qu'est-ce que c'est ?**
Un système de CI/CD intégré à GitHub.

**À quoi ça sert ?**
- Exécuter des tests automatiquement quand vous poussez du code
- Déployer automatiquement
- Lancer des pipelines d'entraînement

**Dans votre projet :** (À venir)
```yaml
# .github/workflows/ci.yml
name: CI
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: pytest tests/
```

**Pourquoi l'utiliser ?**
- ✅ Gratuit pour les projets publics
- ✅ Intégré à GitHub
- ✅ Facile à configurer
- ✅ Automatisation complète

**Site officiel :** https://github.com/features/actions

---

### 14. **TimescaleDB**

**Qu'est-ce que c'est ?**
Une base de données PostgreSQL optimisée pour les données temporelles (time-series).

**À quoi ça sert ?**
- Stocker les métriques de monitoring
- Requêtes temporelles rapides
- Compression automatique

**Dans votre projet :**
- Configuré dans `docker-compose.yml`
- Utilisé pour stocker les métriques Prometheus (optionnel)

**Pourquoi l'utiliser ?**
- ✅ Optimisé pour les données temporelles
- ✅ Compatible PostgreSQL
- ✅ Compression automatique
- ✅ Requêtes rapides

**Site officiel :** https://www.timescale.com/

---

## 🔧 Outils de Qualité de Code

### 15. **pytest**

**Qu'est-ce que c'est ?**
Un framework de tests pour Python.

**À quoi ça sert ?**
- Écrire et exécuter des tests
- Vérifier que votre code fonctionne
- Détecter les bugs

**Dans votre projet :**
```python
# tests/test_api.py
def test_predict():
    response = client.post("/predict", json={"text": "test"})
    assert response.status_code == 200
```

**Commandes utiles :**
```bash
# Lancer tous les tests
pytest

# Avec couverture de code
pytest --cov=src tests/

# Mode verbeux
pytest -v
```

**Pourquoi l'utiliser ?**
- ✅ Standard de l'industrie
- ✅ Facile à utiliser
- ✅ Beaucoup de plugins
- ✅ Intégration CI/CD

**Site officiel :** https://docs.pytest.org/

---

### 16. **black**

**Qu'est-ce que c'est ?**
Un formateur de code Python automatique.

**À quoi ça sert ?**
- Formater automatiquement votre code
- Style cohérent
- Pas de débats sur les espaces/tabs

**Dans votre projet :**
```bash
# Formater tout le code
black src/

# Vérifier sans modifier
black --check src/
```

**Pourquoi l'utiliser ?**
- ✅ Style cohérent automatique
- ✅ Gain de temps
- ✅ Pas de débats de style
- ✅ Standard de l'industrie

**Site officiel :** https://black.readthedocs.io/

---

### 17. **flake8**

**Qu'est-ce que c'est ?**
Un linter pour Python (détecte les erreurs de style et de code).

**À quoi ça sert ?**
- Détecter les erreurs de code
- Vérifier le style (PEP 8)
- Améliorer la qualité du code

**Dans votre projet :**
```bash
# Linter le code
flake8 src/
```

**Pourquoi l'utiliser ?**
- ✅ Détecte les erreurs avant l'exécution
- ✅ Vérifie le style
- ✅ Améliore la qualité
- ✅ Gratuit et open-source

**Site officiel :** https://flake8.pycqa.org/

---

### 18. **mypy**

**Qu'est-ce que c'est ?**
Un vérificateur de types statique pour Python.

**À quoi ça sert ?**
- Vérifier les types de variables
- Détecter les erreurs de type avant l'exécution
- Améliorer la maintenabilité

**Dans votre projet :**
```bash
# Vérifier les types
mypy src/
```

**Pourquoi l'utiliser ?**
- ✅ Détecte les erreurs de type
- ✅ Améliore la maintenabilité
- ✅ Documentation implicite
- ✅ Compatible avec les IDE

**Site officiel :** https://mypy.readthedocs.io/

---

### 19. **pre-commit**

**Qu'est-ce que c'est ?**
Un framework pour gérer des hooks Git (scripts qui s'exécutent avant chaque commit).

**À quoi ça sert ?**
- Exécuter des tests avant de committer
- Formater le code automatiquement
- Vérifier le style
- Empêcher les commits avec des erreurs

**Dans votre projet :**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    hooks:
      - id: black
  - repo: https://github.com/pycqa/flake8
    hooks:
      - id: flake8
```

**Pourquoi l'utiliser ?**
- ✅ Qualité de code garantie
- ✅ Pas de code mal formaté dans le repo
- ✅ Automatisation
- ✅ Gain de temps

**Site officiel :** https://pre-commit.com/

---

## 📦 Outils de Données

### 20. **datasets (HuggingFace)**

**Qu'est-ce que c'est ?**
Une bibliothèque pour télécharger et utiliser des datasets.

**À quoi ça sert ?**
- Télécharger des datasets depuis HuggingFace
- Charger des datasets facilement
- Convertir en pandas DataFrame

**Dans votre projet :**
```python
# scripts/download_dataset.py
from datasets import load_dataset

dataset = load_dataset("ag_news", split="train")
df = pd.DataFrame(dataset)
```

**Pourquoi l'utiliser ?**
- ✅ Accès à des milliers de datasets
- ✅ Facile à utiliser
- ✅ Standardisé
- ✅ Gratuit

**Site officiel :** https://huggingface.co/docs/datasets/

---

### 21. **kaggle**

**Qu'est-ce que c'est ?**
L'API officielle de Kaggle pour télécharger des datasets.

**À quoi ça sert ?**
- Télécharger des datasets depuis Kaggle
- Soumettre des solutions
- Accéder aux compétitions

**Dans votre projet :**
```python
# scripts/download_dataset.py
import kaggle

kaggle.api.dataset_download_files(
    "username/dataset-name",
    path="data/raw",
    unzip=True
)
```

**Pourquoi l'utiliser ?**
- ✅ Accès aux datasets Kaggle
- ✅ Automatisation
- ✅ Intégration facile

**Site officiel :** https://www.kaggle.com/docs/api

---

## 🔐 Outils de Configuration

### 22. **python-dotenv**

**Qu'est-ce que c'est ?**
Une bibliothèque pour charger des variables d'environnement depuis un fichier `.env`.

**À quoi ça sert ?**
- Stocker des secrets (clés API, mots de passe)
- Configuration par environnement
- Sécurité (ne pas committer les secrets)

**Dans votre projet :**
```python
# config/__init__.py
from dotenv import load_dotenv

load_dotenv()  # Charge le fichier .env
```

**Pourquoi l'utiliser ?**
- ✅ Sécurité (secrets non commités)
- ✅ Configuration flexible
- ✅ Standard de l'industrie

**Site officiel :** https://pypi.org/project/python-dotenv/

---

### 23. **PyYAML**

**Qu'est-ce que c'est ?**
Une bibliothèque pour lire/écrire des fichiers YAML.

**À quoi ça sert ?**
- Lire des fichiers de configuration
- Configuration lisible et structurée

**Dans votre projet :**
```python
# config/__init__.py
import yaml

with open("config/config.yaml", 'r') as f:
    config = yaml.safe_load(f)
```

**Pourquoi l'utiliser ?**
- ✅ Format lisible
- ✅ Standard pour les configs
- ✅ Supporté partout

**Site officiel :** https://pyyaml.org/

---

## 📋 Résumé des Outils par Catégorie

### Machine Learning
- ✅ scikit-learn
- ✅ LightGBM
- ✅ pandas
- ✅ numpy

### MLOps
- ✅ MLflow
- ✅ DVC

### Déploiement
- ✅ FastAPI
- ✅ Uvicorn
- ✅ Docker
- ✅ Docker Compose

### Monitoring
- ✅ Prometheus
- ✅ Grafana
- ✅ TimescaleDB

### Infrastructure
- ✅ GitHub Actions

### Qualité de Code
- ✅ pytest
- ✅ black
- ✅ flake8
- ✅ mypy
- ✅ pre-commit

### Données
- ✅ datasets (HuggingFace)
- ✅ kaggle

### Configuration
- ✅ python-dotenv
- ✅ PyYAML

---

## 🎯 Comment Choisir les Outils ?

### Pour un Projet Simple
- scikit-learn
- FastAPI
- MLflow
- Docker

### Pour un Projet Moyen
- Tout ce qui est dans votre projet actuel

### Pour un Projet Avancé
- Ajouter Kubernetes
- Ajouter Feature Store
- Ajouter A/B Testing
- Ajouter Multi-cloud

---

## 📚 Ressources

- **Documentation officielle** de chaque outil (liens dans chaque section)
- **Votre projet** : Exemples concrets dans le code
- **Communautés** : Stack Overflow, Reddit, Discord

---

**Maintenant vous connaissez tous les outils ! 🎉**

