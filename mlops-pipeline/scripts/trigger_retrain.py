"""
Script CLI pour déclencher un retrain manuel ou automatique
"""
import argparse
import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent.parent))

from src.retraining.auto_retrain import AutoRetrainer, RetrainTrigger
from src.utils.logger import get_logger

logger = get_logger(__name__)


def main():
    parser = argparse.ArgumentParser(description='Déclencher un retrain du modèle')
    parser.add_argument(
        '--trigger',
        type=str,
        default='manual',
        choices=['manual', 'drift', 'schedule'],
        help='Type de déclencheur (default: manual)'
    )
    parser.add_argument(
        '--data-path',
        type=str,
        default=None,
        help='CSV de référence / train (défaut: data/processed/train.csv)'
    )
    parser.add_argument(
        '--current-data',
        type=str,
        default=None,
        help='CSV courant pour le drift (ex. data/processed/drift.csv)'
    )
    parser.add_argument(
        '--model-type',
        type=str,
        default='random_forest',
        choices=['random_forest', 'lightgbm'],
        help='Type de modèle à entraîner (default: random_forest)'
    )
    
    args = parser.parse_args()
    
    # Mapper le trigger
    trigger_map = {
        'manual': RetrainTrigger.MANUAL,
        'drift': RetrainTrigger.DRIFT,
        'schedule': RetrainTrigger.SCHEDULE
    }
    trigger = trigger_map[args.trigger]
    
    # Initialiser l'auto-retrainer
    retrainer = AutoRetrainer()
    
    # Lancer le retrain
    logger.info(f"Démarrage du retrain (trigger: {trigger.value}, model: {args.model_type})...")
    result = retrainer.retrain(
        trigger=trigger,
        data_path=args.data_path,
        model_type=args.model_type,
        current_data_path=args.current_data,
    )
    
    # Afficher le résultat
    if result.success:
        print("\n[OK] Retrain termine avec succes!")
        print(f"   Raison: {result.reason}")
        if result.deployed:
            print(f"   [OK] Nouveau modele deploye en production")
            print(f"   Version: {result.new_model_version}")
            if result.improvement is not None:
                print(f"   Amelioration: {result.improvement:.4f}")
        else:
            print(f"   [INFO] Nouveau modele pas deploye (pas assez d'amelioration)")
    else:
        print(f"\n[ERROR] Retrain echoue: {result.reason}")
        if result.error:
            print(f"   Erreur: {result.error}")
        sys.exit(1)


if __name__ == "__main__":
    main()

