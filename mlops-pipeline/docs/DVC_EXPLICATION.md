# 📦 DVC (Data Version Control) - Explication Simple

## 🎯 Qu'est-ce que DVC ?

**DVC** signifie **"Data Version Control"**. C'est comme Git, mais pour les **données et les modèles**.

### Le Problème que DVC Résout

Imaginez cette situation :
- Vous avez un dataset de 5 Go
- Vous entraînez un modèle et obtenez 90% d'accuracy
- Quelqu'un modifie le dataset
- Vous réentraînez et obtenez 85% d'accuracy
- **Problème :** Vous ne savez plus quelle version du dataset a donné 90% !

**DVC résout ça en versionnant vos données comme Git versionne votre code.**

---

## 🔍 Analogie avec Git

| Git | DVC |
|-----|-----|
| Versionne le **code** | Versionne les **données** et **modèles** |
| `git add fichier.py` | `dvc add data/train.csv` |
| `git commit -m "message"` | `dvc commit -m "message"` |
| `git push` | `dvc push` |
| `git pull` | `dvc pull` |

**La différence :** Git stocke le code dans le repo, DVC stocke les données dans un **stockage distant** (S3, Google Drive, etc.) et garde seulement des **pointeurs** dans Git.

---

## 💡 Pourquoi C'est Important en MLOps ?

### 1. **Reproductibilité**
- Vous pouvez revenir à n'importe quelle version de vos données
- Vous savez exactement quelles données ont été utilisées pour entraîner chaque modèle

### 2. **Collaboration**
- Plusieurs personnes peuvent travailler sur le même projet
- Chacun peut télécharger les bonnes versions des données

### 3. **Traçabilité**
- Vous pouvez voir l'historique des changements de données
- Vous savez quand et pourquoi les données ont changé

### 4. **Économie d'Espace**
- Les gros fichiers ne sont pas dans Git (qui n'est pas fait pour ça)
- Les données sont stockées dans un stockage cloud (S3, etc.)

---

## 🏗️ Comment DVC Fonctionne

### Structure Typique

```
votre-projet/
├── .git/              # Git versionne le code
├── .dvc/              # DVC versionne les données
│   ├── config         # Configuration DVC
│   └── cache/         # Cache local des données
│
├── data/
│   ├── train.csv      # Fichier de données (GROS)
│   └── train.csv.dvc  # Pointeur vers les données (PETIT)
│
├── code.py           # Git versionne ça
└── requirements.txt   # Git versionne ça
```

### Le Fichier `.dvc`

Quand vous faites `dvc add data/train.csv`, DVC crée `data/train.csv.dvc` :

```yaml
# data/train.csv.dvc
outs:
  - md5: a1b2c3d4e5f6...  # Hash du fichier
    size: 5242880          # Taille
    path: train.csv        # Nom du fichier
```

**Ce fichier est petit** et peut être versionné par Git. Le vrai fichier de données est stocké ailleurs.

---

## 🚀 Utilisation dans ce Projet

### Configuration Actuelle

Dans `.dvc/config`, vous avez :
```ini
[core]
    remote = storage

['remote "storage"']
    url = s3://your-bucket/mlops-data
```

Cela signifie que DVC stocke les données sur S3 (Amazon Web Services).

### Commandes de Base

#### 1. **Initialiser DVC** (déjà fait)
```bash
dvc init
```

#### 2. **Ajouter un Fichier au Versioning**
```bash
# Ajouter le dataset
dvc add data/processed/train.csv

# Cela crée data/processed/train.csv.dvc
# Le fichier .dvc est ajouté à Git
git add data/processed/train.csv.dvc
git commit -m "Ajouter dataset versionné"
```

#### 3. **Télécharger les Données**
```bash
# Si quelqu'un clone le repo, il peut récupérer les données
dvc pull
```

#### 4. **Envoyer les Données au Stockage**
```bash
# Envoyer les données vers S3 (ou autre stockage)
dvc push
```

#### 5. **Voir l'Historique**
```bash
# Voir les versions des données
dvc list --rev HEAD~1 data/
```

---

## 📊 Exemple Concret

### Scénario : Vous Modifiez le Dataset

```bash
# 1. Vous avez une version du dataset
dvc add data/processed/train.csv
git add data/processed/train.csv.dvc
git commit -m "Dataset v1 - 100k lignes"

# 2. Vous ajoutez plus de données (120k lignes)
# ... modification du dataset ...

# 3. Vous versionnez la nouvelle version
dvc add data/processed/train.csv
git add data/processed/train.csv.dvc
git commit -m "Dataset v2 - 120k lignes"

# 4. Vous pouvez revenir à l'ancienne version
git checkout HEAD~1
dvc checkout  # Télécharge la version correspondante
```

---

## ⚙️ Configuration pour ce Projet

### Option 1 : Stockage Local (Pour Débuter)

Si vous n'avez pas de compte S3, vous pouvez utiliser un stockage local :

```bash
# Modifier .dvc/config
[core]
    remote = local-storage

['remote "local-storage"']
    url = /path/to/storage  # Chemin local
```

### Option 2 : Google Drive (Gratuit)

```bash
# Installer le plugin
pip install dvc-gdrive

# Configurer
dvc remote add -d storage gdrive://votre-id-de-dossier
```

### Option 3 : S3 (Production)

```bash
# Configurer avec vos credentials AWS
dvc remote add -d storage s3://votre-bucket/mlops-data
dvc remote modify storage credentialpath ~/.aws/credentials
```

---

## 🎯 Quand Utiliser DVC dans ce Projet ?

### ✅ À Faire avec DVC :
- ✅ Versionner les datasets (`data/raw/`, `data/processed/`)
- ✅ Versionner les modèles entraînés (`models/*.pkl`)
- ✅ Versionner les artifacts de preprocessing

### ❌ Ne PAS faire avec DVC :
- ❌ Le code source (utilisez Git)
- ❌ Les petits fichiers de config
- ❌ Les fichiers temporaires

---

## 🔧 Commandes Utiles

```bash
# Voir l'état des fichiers DVC
dvc status

# Voir les métriques trackées
dvc metrics show

# Comparer deux versions
dvc diff HEAD~1

# Nettoyer le cache
dvc cache dir
dvc cache clean
```

---

## 📚 Ressources

- **Documentation officielle** : https://dvc.org/doc
- **Tutoriel interactif** : https://dvc.org/doc/start
- **Guide de migration** : https://dvc.org/doc/use-cases/versioning-data-and-model-files

---

## 🎓 Résumé Simple

**DVC = Git pour les données**

- ✅ Versionne les gros fichiers (données, modèles)
- ✅ Stocke les données dans le cloud
- ✅ Garde seulement des pointeurs dans Git
- ✅ Permet de revenir à n'importe quelle version
- ✅ Essentiel pour la reproductibilité en ML

**Dans ce projet :** DVC est configuré mais pas encore utilisé activement. Vous pouvez l'utiliser pour versionner votre dataset AG News et vos modèles entraînés.

---

## 💡 Conseil

Pour commencer, vous n'êtes **pas obligé** d'utiliser DVC tout de suite. Vous pouvez :
1. D'abord faire fonctionner votre pipeline
2. Ensuite, quand vous aurez plusieurs versions de données/modèles, utiliser DVC

**DVC est surtout utile quand :**
- Vous avez plusieurs versions de données
- Vous travaillez en équipe
- Vous voulez une traçabilité complète

Pour un projet de démonstration, DVC est un **bon bonus** mais pas obligatoire ! 🚀

