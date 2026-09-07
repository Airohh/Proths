"""
Script de monitoring continu avec déclenchement automatique du retrain
Peut être exécuté en arrière-plan ou via cron
"""
import time
import sys
from pathlib import Path
from datetime import datetime

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent.parent))

from src.retraining.auto_retrain import AutoRetrainer, RetrainTrigger
from src.utils.logger import get_logger
from config import get_config

logger = get_logger(__name__)


def monitor_loop():
    """
    Boucle de monitoring qui vérifie le drift et déclenche le retrain si nécessaire
    """
    config = get_config()
    retrain_config = config.get('retrain', {})
    monitoring_config = config.get('monitoring', {})
    
    # Vérifier si le retrain est activé
    if not retrain_config.get('enabled', True):
        logger.warning("Retrain désactivé dans la configuration")
        return
    
    # Initialiser l'auto-retrainer
    retrainer = AutoRetrainer(config)
    
    # Intervalle de vérification (en secondes)
    check_interval = monitoring_config.get('check_interval', 3600)  # 1 heure par défaut
    
    logger.info(f"Démarrage du monitoring (intervalle: {check_interval}s)")
    
    while True:
        try:
            logger.info(f"Vérification du drift à {datetime.now()}")
            
            # Vérifier le drift
            data_config = config.get('data', {})
            processed_path = data_config.get('processed_path', 'data/processed')
            train_file = data_config.get('train_file', 'train.csv')
            data_path = Path(processed_path) / train_file
            
            if not data_path.exists():
                logger.error(f"Fichier de données introuvable: {data_path}")
                time.sleep(check_interval)
                continue
            
            current_path = Path(processed_path) / data_config.get("current_file", "drift.csv")
            if not current_path.exists():
                logger.error(
                    f"CSV courant introuvable: {current_path} "
                    "(envoie du trafic: python scripts/generate_traffic.py)"
                )
                time.sleep(check_interval)
                continue

            drift_score, is_drift = retrainer.check_drift(
                str(data_path), current_data_path=str(current_path)
            )

            if is_drift:
                logger.warning(f"Drift détecté (score: {drift_score:.4f}), déclenchement du retrain...")
                result = retrainer.retrain(
                    trigger=RetrainTrigger.DRIFT,
                    data_path=str(data_path),
                    current_data_path=str(current_path),
                )
                
                if result.success and result.deployed:
                    logger.info("[OK] Retrain reussi et nouveau modele deploye")
                elif result.success:
                    logger.info(f"[INFO] Retrain reussi mais modele pas deploye: {result.reason}")
                else:
                    logger.error(f"[ERROR] Retrain echoue: {result.reason}")
            else:
                logger.info(f"[OK] Pas de drift detecte (score: {drift_score:.4f})")
            
            # Attendre avant la prochaine vérification
            logger.info(f"Prochaine vérification dans {check_interval}s...")
            time.sleep(check_interval)
        
        except KeyboardInterrupt:
            logger.info("Arrêt du monitoring (interruption utilisateur)")
            break
        except Exception as e:
            logger.error(f"Erreur dans la boucle de monitoring: {e}", exc_info=True)
            # Attendre un peu avant de réessayer
            time.sleep(60)


def main():
    """
    Point d'entrée principal
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitoring continu avec auto-retrain')
    parser.add_argument(
        '--once',
        action='store_true',
        help='Exécuter une seule vérification (pas de boucle)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=None,
        help='Intervalle de vérification en secondes (override config)'
    )
    parser.add_argument(
        '--current-data',
        type=str,
        default=None,
        help='CSV courant (défaut: data/processed/drift.csv)'
    )
    
    args = parser.parse_args()
    
    if args.interval:
        config = get_config()
        config['monitoring']['check_interval'] = args.interval
    
    if args.once:
        # Exécuter une seule fois
        config = get_config()
        retrainer = AutoRetrainer(config)
        
        data_config = config.get('data', {})
        processed_path = data_config.get('processed_path', 'data/processed')
        train_file = data_config.get('train_file', 'train.csv')
        data_path = Path(processed_path) / train_file
        
        if not data_path.exists():
            logger.error(f"Fichier de données introuvable: {data_path}")
            sys.exit(1)

        current_path = (
            Path(args.current_data)
            if args.current_data
            else Path(processed_path) / data_config.get("current_file", "drift.csv")
        )
        if not current_path.exists():
            logger.error(f"CSV courant introuvable: {current_path}")
            sys.exit(1)

        drift_score, is_drift = retrainer.check_drift(
            str(data_path), current_data_path=str(current_path)
        )

        if is_drift:
            logger.warning("Drift détecté, déclenchement du retrain...")
            result = retrainer.retrain(
                trigger=RetrainTrigger.DRIFT,
                data_path=str(data_path),
                current_data_path=str(current_path),
            )
            
            if result.success:
                print(f"[OK] Retrain termine: {result.reason}")
                if result.deployed:
                    print(f"   Nouveau modele deploye")
            else:
                print(f"[ERROR] Retrain echoue: {result.reason}")
                sys.exit(1)
        else:
            print(f"[OK] Pas de drift detecte (score: {drift_score:.4f})")
    else:
        # Boucle continue
        monitor_loop()


if __name__ == "__main__":
    main()

