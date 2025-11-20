"""
Script pour télécharger des datasets depuis Kaggle ou HuggingFace
"""
import argparse
import pandas as pd
from pathlib import Path
import sys
from typing import Optional

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent.parent))

from src.utils.logger import get_logger
from config import get_config

logger = get_logger(__name__)


def download_kaggle_dataset(dataset_name: str, output_dir: str = "data/raw") -> pd.DataFrame:
    """
    Télécharge un dataset depuis Kaggle
    
    Args:
        dataset_name: Nom du dataset (format: username/dataset-name)
        output_dir: Répertoire de sortie
    
    Returns:
        DataFrame avec les données
    """
    try:
        import kaggle
    except ImportError:
        logger.error("Kaggle API non installée. Installez avec: pip install kaggle")
        logger.info("Ou utilisez HuggingFace avec --source huggingface")
        raise
    
    logger.info(f"Téléchargement du dataset Kaggle: {dataset_name}")
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Télécharger le dataset
    kaggle.api.dataset_download_files(
        dataset_name,
        path=str(output_path),
        unzip=True
    )
    
    logger.info(f"Dataset téléchargé dans {output_path}")
    
    # Essayer de charger le CSV
    csv_files = list(output_path.glob("*.csv"))
    if csv_files:
        df = pd.read_csv(csv_files[0])
        logger.info(f"Données chargées: {len(df)} lignes, {len(df.columns)} colonnes")
        return df
    else:
        logger.warning("Aucun fichier CSV trouvé dans le dataset téléchargé")
        return pd.DataFrame()


def download_huggingface_dataset(
    dataset_name: str,
    split: str = "train",
    text_column: str = "text",
    label_column: str = "label",
    output_dir: str = "data/raw"
) -> pd.DataFrame:
    """
    Télécharge un dataset depuis HuggingFace
    
    Args:
        dataset_name: Nom du dataset HuggingFace
        split: Split à télécharger (train, test, validation)
        text_column: Nom de la colonne texte
        label_column: Nom de la colonne label
        output_dir: Répertoire de sortie
    
    Returns:
        DataFrame avec les données
    """
    try:
        from datasets import load_dataset
    except ImportError:
        logger.error("HuggingFace datasets non installé. Installez avec: pip install datasets")
        raise
    
    logger.info(f"Téléchargement du dataset HuggingFace: {dataset_name}")
    
    # Charger le dataset
    dataset = load_dataset(dataset_name, split=split)
    
    # Convertir en DataFrame
    df = pd.DataFrame(dataset)
    
    # Renommer les colonnes si nécessaire
    if text_column not in df.columns:
        # Essayer de trouver automatiquement la colonne texte
        possible_text_cols = [col for col in df.columns if 'text' in col.lower() or 'sentence' in col.lower()]
        if possible_text_cols:
            text_column = possible_text_cols[0]
            logger.info(f"Colonne texte trouvée automatiquement: {text_column}")
        else:
            raise ValueError(f"Colonne '{text_column}' introuvable. Colonnes disponibles: {df.columns.tolist()}")
    
    if label_column not in df.columns:
        # Essayer de trouver automatiquement la colonne label
        possible_label_cols = [col for col in df.columns if 'label' in col.lower() or 'class' in col.lower()]
        if possible_label_cols:
            label_column = possible_label_cols[0]
            logger.info(f"Colonne label trouvée automatiquement: {label_column}")
        else:
            raise ValueError(f"Colonne '{label_column}' introuvable. Colonnes disponibles: {df.columns.tolist()}")
    
    # Sélectionner et renommer les colonnes
    df = df[[text_column, label_column]].rename(columns={text_column: 'text', label_column: 'label'})
    
    # Sauvegarder
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    output_file = output_path / f"{dataset_name.replace('/', '_')}_{split}.csv"
    df.to_csv(output_file, index=False)
    
    logger.info(f"Dataset sauvegardé: {output_file}")
    logger.info(f"Données: {len(df)} lignes")
    logger.info(f"Classes: {df['label'].value_counts().to_dict()}")
    
    return df


def download_popular_dataset(dataset_type: str = "news", output_dir: str = "data/raw") -> pd.DataFrame:
    """
    Télécharge un dataset populaire prédéfini
    
    Args:
        dataset_type: Type de dataset (news, sentiment, spam, etc.)
        output_dir: Répertoire de sortie
    
    Returns:
        DataFrame avec les données
    """
    datasets = {
        "news": {
            "source": "huggingface",
            "name": "ag_news",
            "text_column": "text",
            "label_column": "label"
        },
        "sentiment": {
            "source": "huggingface",
            "name": "imdb",
            "text_column": "text",
            "label_column": "label"
        },
        "spam": {
            "source": "huggingface",
            "name": "sms_spam",
            "text_column": "sms",
            "label_column": "label"
        },
        "tweets": {
            "source": "huggingface",
            "name": "tweet_eval",
            "text_column": "text",
            "label_column": "label"
        }
    }
    
    if dataset_type not in datasets:
        raise ValueError(f"Type de dataset non supporté: {dataset_type}. Options: {list(datasets.keys())}")
    
    config = datasets[dataset_type]
    
    if config["source"] == "huggingface":
        return download_huggingface_dataset(
            config["name"],
            text_column=config["text_column"],
            label_column=config["label_column"],
            output_dir=output_dir
        )
    else:
        raise ValueError(f"Source non supportée: {config['source']}")


def main():
    parser = argparse.ArgumentParser(description="Télécharger un dataset pour l'entraînement")
    parser.add_argument(
        "--source",
        type=str,
        choices=["kaggle", "huggingface", "popular"],
        default="popular",
        help="Source du dataset"
    )
    parser.add_argument(
        "--dataset",
        type=str,
        help="Nom du dataset (format: username/dataset pour Kaggle, ou nom pour HuggingFace)"
    )
    parser.add_argument(
        "--type",
        type=str,
        choices=["news", "sentiment", "spam", "tweets"],
        default="news",
        help="Type de dataset populaire (si --source=popular)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/raw",
        help="Répertoire de sortie"
    )
    parser.add_argument(
        "--split",
        type=str,
        default="train",
        help="Split à télécharger (pour HuggingFace)"
    )
    
    args = parser.parse_args()
    
    config = get_config()
    output_dir = args.output or config.get('data', {}).get('raw_path', 'data/raw')
    
    try:
        if args.source == "popular":
            logger.info(f"Téléchargement du dataset populaire: {args.type}")
            df = download_popular_dataset(args.type, output_dir)
        elif args.source == "kaggle":
            if not args.dataset:
                raise ValueError("--dataset est requis pour Kaggle")
            df = download_kaggle_dataset(args.dataset, output_dir)
        elif args.source == "huggingface":
            if not args.dataset:
                raise ValueError("--dataset est requis pour HuggingFace")
            df = download_huggingface_dataset(args.dataset, args.split, output_dir=output_dir)
        
        logger.info(f"[OK] Dataset telecharge avec succes: {len(df)} lignes")
        logger.info(f"[INFO] Repartition des classes:")
        if 'label' in df.columns:
            print(df['label'].value_counts())
        
    except Exception as e:
        logger.error(f"Erreur lors du téléchargement: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

