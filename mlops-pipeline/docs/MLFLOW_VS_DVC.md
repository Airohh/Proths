# 🔄 MLflow vs DVC - La Différence

## 🎯 Vue d'Ensemble

En MLOps, vous avez besoin de **deux outils complémentaires** :

| Outil | Pour Quoi ? | Exemple |
|-------|-------------|---------|
| **MLflow** | Versionner les **modèles** et tracker les **expériences** | "Modèle v1.2 avec accuracy 0.92" |
| **DVC** | Versionner les **données** | "Dataset train.csv v3 avec 120k lignes" |

---

## 📊 MLflow - Pour les Modèles

### Qu'est-ce que MLflow ?

**MLflow** est un outil pour gérer le **cycle de vie des modèles** :
- ✅ Tracking des expériences (paramètres, métriques)
- ✅ Registry de modèles (versioning des modèles)
- ✅ Déploiement de modèles

### Ce que MLflow Fait

#### 1. **Tracking des Expériences**
Quand vous entraînez un modèle, MLflow enregistre :
- Les paramètres utilisés (learning_rate, n_estimators, etc.)
- Les métriques obtenues (accuracy, f1_score, etc.)
- Le code utilisé
- Les artifacts (modèles, graphiques)

**Exemple :**
```python
with mlflow.start_run():
    mlflow.log_param("model_type", "random_forest")
    mlflow.log_param("n_estimators", 100)
    mlflow.log_metric("accuracy", 0.92)
    mlflow.log_metric("f1_score", 0.91)
    mlflow.sklearn.log_model(model, "model")
```

#### 2. **Model Registry**
MLflow peut stocker plusieurs versions d'un modèle :

```
document-classifier/
├── v1.0  (accuracy: 0.90)
├── v1.1  (accuracy: 0.92) ← Production
└── v1.2  (accuracy: 0.93) ← Staging
```

Vous pouvez :
- Comparer les versions
- Promouvoir une version en production
- Rollback si problème

#### 3. **Interface Web**
MLflow fournit une interface web pour :
- Voir toutes vos expériences
- Comparer les modèles
- Télécharger des modèles
- Voir les métriques en graphiques

---

## 📦 DVC - Pour les Données

### Qu'est-ce que DVC ?

**DVC** est un outil pour versionner les **données** et les **artifacts** :
- ✅ Versionner les datasets
- ✅ Stocker les gros fichiers dans le cloud
- ✅ Traçabilité des données

### Ce que DVC Fait

#### 1. **Versioning des Données**
Vous pouvez versionner vos datasets :

```bash
# Version 1
dvc add data/train.csv
git commit -m "Dataset v1 - 100k lignes"

# Vous modifiez le dataset (120k lignes)
dvc add data/train.csv
git commit -m "Dataset v2 - 120k lignes"
```

#### 2. **Stockage Distant**
DVC stocke les données dans :
- S3 (Amazon)
- Google Drive
- Stockage local
- etc.

#### 3. **Reproductibilité**
Vous pouvez revenir à n'importe quelle version de données :
```bash
git checkout <commit-hash>
dvc checkout  # Télécharge la bonne version des données
```

---

## 🔄 Comment Ils Travaillent Ensemble

### Workflow Typique

```
1. DVC versionne les données
   └─> data/train.csv v2 (120k lignes)

2. Vous entraînez un modèle avec ces données
   └─> MLflow track l'expérience et versionne le modèle
       └─> model v1.2 (accuracy: 0.92)

3. Vous pouvez lier les deux :
   - "Modèle v1.2 a été entraîné avec dataset v2"
```

### Exemple Concret

```python
# 1. DVC a versionné votre dataset
# data/processed/train.csv (version 2)

# 2. Vous entraînez avec MLflow
with mlflow.start_run():
    # Charger les données (versionnées par DVC)
    df = pd.read_csv("data/processed/train.csv")
    
    # Entraîner le modèle
    model = train_model(df)
    
    # MLflow enregistre le modèle
    mlflow.log_param("dataset_version", "v2")  # Lien avec DVC
    mlflow.log_metric("accuracy", 0.92)
    mlflow.sklearn.log_model(model, "model", 
                            registered_model_name="document-classifier")
```

---

## 📊 Comparaison Détaillée

| Aspect | MLflow | DVC |
|-------|--------|-----|
| **Objectif** | Modèles et expériences | Données et artifacts |
| **Stocke** | Modèles, métriques, paramètres | Datasets, fichiers volumineux |
| **Interface** | Web UI (http://localhost:5000) | Ligne de commande |
| **Versioning** | Versions de modèles (v1.0, v1.1) | Versions de données (commits Git) |
| **Taille** | Modèles (quelques Mo à Go) | Datasets (Go à To) |
| **Stockage** | Local ou serveur MLflow | Cloud (S3, GDrive, etc.) |
| **Utilisation** | Comparer modèles, déployer | Reproduire expériences, collaborer |

---

## 🎯 Dans Votre Projet

### MLflow est Utilisé Pour :

✅ **Tracking des expériences** (`src/training/train.py`)
```python
with mlflow.start_run():
    mlflow.log_param("model_type", "random_forest")
    mlflow.log_metric("accuracy", 0.92)
    mlflow.sklearn.log_model(model, "model")
```

✅ **Registry de modèles** (stockage des modèles entraînés)
```python
# Charger un modèle depuis MLflow
model = mlflow.sklearn.load_model("models:/document-classifier/latest")
```

✅ **Interface web** (http://localhost:5000)

### DVC est Configuré Pour :

✅ **Versionner les datasets** (quand vous l'utiliserez)
```bash
dvc add data/processed/train.csv
```

✅ **Versionner les modèles** (alternative à MLflow pour le stockage)

---

## 💡 Quand Utiliser Quoi ?

### Utilisez MLflow pour :
- ✅ Tracker toutes vos expériences
- ✅ Comparer différents modèles
- ✅ Gérer les versions de modèles
- ✅ Déployer des modèles
- ✅ Voir les métriques en graphiques

### Utilisez DVC pour :
- ✅ Versionner les datasets
- ✅ Collaborer sur les données
- ✅ Reproduire des expériences avec les bonnes données
- ✅ Stocker les gros fichiers

---

## 🔧 Configuration Actuelle

### MLflow
- ✅ Configuré dans `docker-compose.yml`
- ✅ Utilisé dans `src/training/train.py`
- ✅ Interface disponible sur http://localhost:5000

### DVC
- ✅ Initialisé (`.dvc/` existe)
- ✅ Configuré pour stockage local (`./data`)
- ⏸️ Pas encore utilisé activement (optionnel)

---

## 🚀 Exemple de Workflow Complet

```bash
# 1. Versionner les données avec DVC
dvc add data/processed/train.csv
git add data/processed/train.csv.dvc
git commit -m "Dataset v2 - 120k lignes"

# 2. Entraîner le modèle (MLflow track automatiquement)
python src/training/train.py

# 3. Voir les résultats dans MLflow UI
# Ouvrir http://localhost:5000

# 4. Si besoin, revenir à une ancienne version de données
git checkout <ancien-commit>
dvc checkout  # Télécharge l'ancienne version
```

---

## 📚 Résumé

| | MLflow | DVC |
|---|---|---|
| **Pour** | Modèles | Données |
| **Versionne** | Modèles (v1.0, v1.1) | Datasets (commits Git) |
| **Interface** | Web UI | CLI |
| **Dans ce projet** | ✅ Actif | ⏸️ Configuré mais optionnel |

**En bref :**
- **MLflow** = "GitHub pour les modèles"
- **DVC** = "Git pour les données"

Les deux sont complémentaires et travaillent ensemble pour un pipeline MLOps complet ! 🚀

---

## 🎓 Pour Aller Plus Loin

- **MLflow** : https://mlflow.org/docs/latest/index.html
- **DVC** : https://dvc.org/doc
- **MLflow + DVC** : https://dvc.org/doc/use-cases/data-and-model-versioning

