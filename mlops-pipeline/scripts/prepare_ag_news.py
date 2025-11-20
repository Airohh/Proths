"""
Script pour préparer le dataset AG News avec les noms de catégories
"""
import pandas as pd
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from src.utils.logger import get_logger

logger = get_logger(__name__)

# Mapping des labels AG News
LABEL_MAPPING = {
    0: "World",
    1: "Sports", 
    2: "Business",
    3: "Sci/Tech"
}

def prepare_ag_news(input_file: str = "data/raw/ag_news_train.csv", 
                    output_file: str = "data/processed/train.csv"):
    """
    Prépare le dataset AG News en convertissant les labels numériques en noms
    
    Args:
        input_file: Fichier d'entrée
        output_file: Fichier de sortie
    """
    logger.info(f"Chargement du dataset depuis {input_file}")
    df = pd.read_csv(input_file)
    
    logger.info(f"Dataset chargé: {len(df)} lignes")
    logger.info(f"Colonnes: {df.columns.tolist()}")
    
    # Vérifier si les labels sont numériques
    if 'label' in df.columns and df['label'].dtype in ['int64', 'int32', 'float64']:
        logger.info("Conversion des labels numériques en noms de catégories")
        df['label'] = df['label'].map(LABEL_MAPPING)
        
        # Vérifier qu'il n'y a pas de valeurs manquantes
        missing = df['label'].isna().sum()
        if missing > 0:
            logger.warning(f"{missing} labels non mappés trouvés")
            df = df.dropna(subset=['label'])
    
    # S'assurer que les colonnes sont 'text' et 'label'
    if 'text' not in df.columns or 'label' not in df.columns:
        logger.error(f"Colonnes attendues: 'text' et 'label'. Trouvées: {df.columns.tolist()}")
        raise ValueError("Format de colonnes incorrect")
    
    # Créer le répertoire de sortie
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Sauvegarder
    df.to_csv(output_file, index=False)
    logger.info(f"[OK] Dataset prepare sauvegarde dans {output_file}")
    logger.info(f"[INFO] Repartition des classes:")
    print(df['label'].value_counts())
    
    # Afficher quelques exemples
    logger.info("\n[INFO] Exemples de donnees:")
    for i in range(min(3, len(df))):
        print(f"\nExemple {i+1}:")
        print(f"  Label: {df.iloc[i]['label']}")
        print(f"  Texte: {df.iloc[i]['text'][:100]}...")
    
    return df


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Préparer le dataset AG News")
    parser.add_argument("--input", type=str, default="data/raw/ag_news_train.csv",
                       help="Fichier d'entrée")
    parser.add_argument("--output", type=str, default="data/processed/train.csv",
                       help="Fichier de sortie")
    
    args = parser.parse_args()
    
    prepare_ag_news(args.input, args.output)

