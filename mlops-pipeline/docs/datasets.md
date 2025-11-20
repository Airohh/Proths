# Guide des Datasets

Ce guide explique comment télécharger et utiliser des datasets pour le projet MLOps.

## 🎯 Options de Datasets

### Option 1: Datasets Populaires (Recommandé pour commencer)

Le script `download_dataset.py` supporte plusieurs datasets populaires prêts à l'emploi :

```bash
# Dataset de classification de news (AG News)
python scripts/download_dataset.py --source popular --type news

# Dataset de sentiment (IMDB)
python scripts/download_dataset.py --source popular --type sentiment

# Dataset de détection de spam
python scripts/download_dataset.py --source popular --type spam

# Dataset de classification de tweets
python scripts/download_dataset.py --source popular --type tweets
```

### Option 2: HuggingFace Datasets

HuggingFace offre des milliers de datasets pour la classification de texte :

```bash
# Exemple: AG News
python scripts/download_dataset.py --source huggingface --dataset ag_news

# Exemple: 20 Newsgroups
python scripts/download_dataset.py --source huggingface --dataset scikit-learn/twenty_newsgroups

# Exemple: BBC News
python scripts/download_dataset.py --source huggingface --dataset SetFit/bbc-news
```

**Datasets HuggingFace recommandés pour la classification de documents :**
- `ag_news` - Classification de news (4 classes)
- `imdb` - Sentiment analysis (2 classes)
- `yelp_review_full` - Reviews (5 classes)
- `amazon_polarity` - Sentiment (2 classes)
- `dbpedia_14` - Classification de textes Wikipedia (14 classes)
- `yahoo_answers_topics` - Questions/réponses (10 classes)

### Option 3: Kaggle Datasets

Pour utiliser Kaggle, vous devez d'abord configurer l'API :

1. Créer un compte Kaggle
2. Télécharger votre API token : https://www.kaggle.com/settings
3. Placer `kaggle.json` dans `~/.kaggle/` (Linux/Mac) ou `C:\Users\<username>\.kaggle\` (Windows)

```bash
# Exemple: News Category Dataset
python scripts/download_dataset.py --source kaggle --dataset rmisra/news-category-dataset

# Exemple: BBC News Dataset
python scripts/download_dataset.py --source kaggle --dataset yufengdev/bbc-fulltext-and-category
```

**Datasets Kaggle recommandés :**
- `rmisra/news-category-dataset` - 200k+ articles de news
- `yufengdev/bbc-fulltext-and-category` - Articles BBC
- `datasnaek/youtube-new` - Titres et catégories YouTube

## 📊 Structure des Données

Le script attend un format standard :
- Colonne `text` : Le texte à classifier
- Colonne `label` : La classe/catégorie

Si votre dataset utilise d'autres noms de colonnes, le script essaiera de les détecter automatiquement.

## 🔄 Workflow Complet

```bash
# 1. Télécharger un dataset
python scripts/download_dataset.py --source popular --type news

# 2. Préparer les données (optionnel, si besoin de preprocessing supplémentaire)
python scripts/prepare_data.py --input data/raw/ag_news_train.csv --output data/processed/train.csv

# 3. Entraîner le modèle
python src/training/train.py --data-path data/processed/train.csv

# 4. Lancer l'API
uvicorn src.inference.api:app --reload
```

## 🎓 Datasets pour Démonstration

Pour un projet de démonstration MLOps, je recommande :

1. **AG News** (petit, rapide) : `--type news`
2. **20 Newsgroups** (moyen, réaliste) : `--source huggingface --dataset scikit-learn/twenty_newsgroups`
3. **BBC News** (bon pour démo) : `--source huggingface --dataset SetFit/bbc-news`

## 📝 Notes

- Les datasets sont téléchargés dans `data/raw/` par défaut
- Le script génère automatiquement un fichier CSV prêt à l'emploi
- Pour les gros datasets, considérez utiliser DVC pour le versioning

## 🔗 Ressources

- [HuggingFace Datasets](https://huggingface.co/datasets)
- [Kaggle Datasets](https://www.kaggle.com/datasets)
- [Papers with Code Datasets](https://paperswithcode.com/datasets)

