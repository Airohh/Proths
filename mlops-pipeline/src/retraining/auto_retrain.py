"""
Pipeline d'auto-retrain avec détection de drift et comparaison de modèles
"""
import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import mlflow
import mlflow.sklearn
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.training.train import train_baseline_model
from src.training.preprocessing import preprocess_data, vectorize_for_drift
from src.monitoring.drift_detection import detect_drift
from src.utils.logger import get_logger
from config import get_config

logger = get_logger(__name__)


class RetrainTrigger(Enum):
    """Types de déclencheurs pour le retrain"""
    DRIFT = "drift"
    SCHEDULE = "schedule"
    MANUAL = "manual"
    PERFORMANCE_DROP = "performance_drop"


@dataclass
class RetrainResult:
    """Résultat d'un retrain"""
    success: bool
    new_model_version: Optional[str] = None
    old_model_metric: Optional[float] = None
    new_model_metric: Optional[float] = None
    improvement: Optional[float] = None
    deployed: bool = False
    reason: str = ""
    error: Optional[str] = None


class AutoRetrainer:
    """
    Pipeline d'auto-retrain avec détection de drift et comparaison de modèles
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialise l'auto-retrainer
        
        Args:
            config: Configuration (optionnel, charge depuis config.yaml si None)
        """
        if config is None:
            config = get_config()
        
        self.config = config
        self.retrain_config = config.get('retrain', {})
        self.mlflow_config = config.get('mlflow', {})
        self.data_config = config.get('data', {})
        
        # Setup MLflow
        mlflow.set_tracking_uri(self.mlflow_config.get('tracking_uri', 'http://localhost:5000'))
        mlflow.set_experiment(self.mlflow_config.get('experiment_name', 'document-classification'))
        
        logger.info("AutoRetrainer initialisé", extra={
            'extra_fields': {
                'retrain_enabled': self.retrain_config.get('enabled', True),
                'trigger_type': self.retrain_config.get('trigger', {}).get('type', 'drift')
            }
        })
    
    def check_drift(
        self, 
        reference_data_path: str,
        current_data_path: Optional[str] = None,
        current_data: Optional[np.ndarray] = None
    ) -> Tuple[float, bool]:
        """
        Vérifie s'il y a du drift dans les données
        
        Args:
            reference_data_path: Chemin vers les données de référence
            current_data_path: Chemin vers les données actuelles (optionnel)
            current_data: Données actuelles en numpy array (optionnel)
        
        Returns:
            drift_score, is_drift
        """
        logger.info("Vérification du drift...")

        if current_data is None and not current_data_path:
            logger.warning("Aucune donnée actuelle fournie, pas de drift détecté")
            return 0.0, False

        ref_df = pd.read_csv(reference_data_path)
        curr_df = None
        if current_data_path:
            curr_df = pd.read_csv(current_data_path)

        if current_data is not None:
            X_ref, _ = vectorize_for_drift(ref_df, ref_df)
            X_curr = current_data
            curr_labels = None
        else:
            X_ref, X_curr = vectorize_for_drift(ref_df, curr_df)
            curr_labels = curr_df["label"] if "label" in curr_df.columns else None

        ref_labels = ref_df["label"] if "label" in ref_df.columns else None
        threshold = self.retrain_config.get("trigger", {}).get("drift_threshold", 0.15)
        drift_score, is_drift = detect_drift(
            X_ref,
            X_curr,
            threshold=threshold,
            reference_labels=ref_labels,
            current_labels=curr_labels,
        )
        
        logger.info(
            f"Drift détecté: {is_drift} (score: {drift_score:.4f}, seuil: {threshold})",
            extra={'extra_fields': {'drift_score': drift_score, 'is_drift': is_drift}}
        )
        
        return drift_score, is_drift
    
    def get_current_production_model(self, model_name: str = "document-classifier-random_forest") -> Optional[Any]:
        """
        Récupère le modèle actuellement en production depuis MLflow
        
        Args:
            model_name: Nom du modèle dans MLflow registry
        
        Returns:
            Modèle ou None si non trouvé
        """
        try:
            client = mlflow.tracking.MlflowClient()
            
            # Récupérer la dernière version en production
            try:
                latest_versions = client.get_latest_versions(model_name, stages=["Production"])
                if latest_versions:
                    model_version = latest_versions[0].version
                    model_uri = f"models:/{model_name}/{model_version}"
                    model = mlflow.sklearn.load_model(model_uri)
                    logger.info(f"Modèle de production trouvé: {model_name} v{model_version}")
                    return model, model_version
            except Exception:
                # Si pas de modèle en production, prendre le latest
                model_uri = f"models:/{model_name}/latest"
                model = mlflow.sklearn.load_model(model_uri)
                logger.info(f"Modèle latest trouvé: {model_name}")
                return model, "latest"
        
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du modèle: {e}", exc_info=True)
            return None, None
    
    def get_model_metrics(self, model_name: str, version: str) -> Optional[Dict[str, float]]:
        """
        Récupère les métriques d'un modèle depuis MLflow
        
        Args:
            model_name: Nom du modèle
            version: Version du modèle
        
        Returns:
            Dict avec les métriques ou None
        """
        try:
            client = mlflow.tracking.MlflowClient()
            model_version = client.get_model_version(model_name, version)
            
            # Récupérer les métriques depuis le run associé
            run_id = model_version.run_id
            run = client.get_run(run_id)
            
            metrics = {
                'accuracy': run.data.metrics.get('accuracy', 0.0),
                'precision': run.data.metrics.get('precision', 0.0),
                'recall': run.data.metrics.get('recall', 0.0),
                'f1_score': run.data.metrics.get('f1_score', 0.0)
            }
            
            return metrics
        
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des métriques: {e}", exc_info=True)
            return None
    
    def train_new_model(
        self,
        data_path: str,
        model_type: str = 'random_forest',
        include_new_data: bool = True,
        extra_data_path: Optional[str] = None,
    ) -> Tuple[Any, Dict[str, float], str]:
        """
        Entraîne un nouveau modèle
        
        Args:
            data_path: Chemin vers les données d'entraînement
            model_type: Type de modèle ('random_forest' ou 'lightgbm')
            include_new_data: Inclure les nouvelles données de production (si disponibles)
        
        Returns:
            model, metrics, run_id
        """
        logger.info(f"Entraînement d'un nouveau modèle ({model_type})...")
        
        # Charger les données
        df = pd.read_csv(data_path)
        
        if include_new_data and extra_data_path and os.path.exists(extra_data_path):
            extra = pd.read_csv(extra_data_path)
            df = pd.concat([df, extra], ignore_index=True)
            logger.info(f"Données courantes concaténées: {extra_data_path} ({len(extra)} lignes)")

        X, y = preprocess_data(df)
        
        # Split train/validation
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Entraînement avec MLflow tracking
        with mlflow.start_run() as run:
            model, metrics = train_baseline_model(
                X_train, y_train, X_val, y_val,
                model_type=model_type
            )
            
            # Logging
            mlflow.log_param("model_type", model_type)
            # Utiliser shape[0] pour les matrices sparse
            train_size = X_train.shape[0] if hasattr(X_train, 'shape') else len(X_train)
            val_size = X_val.shape[0] if hasattr(X_val, 'shape') else len(X_val)
            mlflow.log_param("train_size", train_size)
            mlflow.log_param("val_size", val_size)
            mlflow.log_param("retrain", True)
            
            for metric_name, metric_value in metrics.items():
                mlflow.log_metric(metric_name, metric_value)
            
            # Enregistrer le modèle
            model_name = f"document-classifier-{model_type}"
            mlflow.sklearn.log_model(
                model,
                "model",
                registered_model_name=model_name
            )
            
            run_id = run.info.run_id
            logger.info(
                f"Nouveau modèle entraîné (run_id: {run_id})",
                extra={'extra_fields': {'metrics': metrics, 'run_id': run_id}}
            )
            
            return model, metrics, run_id
    
    def compare_models(
        self,
        old_model_metrics: Dict[str, float],
        new_model_metrics: Dict[str, float],
        comparison_metric: str = "f1_score"
    ) -> Tuple[bool, float]:
        """
        Compare deux modèles et détermine si le nouveau est meilleur
        
        Args:
            old_model_metrics: Métriques de l'ancien modèle
            new_model_metrics: Métriques du nouveau modèle
            comparison_metric: Métrique à utiliser pour la comparaison
        
        Returns:
            is_better, improvement
        """
        old_metric = old_model_metrics.get(comparison_metric, 0.0)
        new_metric = new_model_metrics.get(comparison_metric, 0.0)
        
        improvement = new_metric - old_metric
        min_improvement = self.retrain_config.get('min_improvement', 0.01)
        
        is_better = improvement >= min_improvement
        
        logger.info(
            f"Comparaison des modèles ({comparison_metric}): "
            f"ancien={old_metric:.4f}, nouveau={new_metric:.4f}, "
            f"amélioration={improvement:.4f}",
            extra={'extra_fields': {
                'old_metric': old_metric,
                'new_metric': new_metric,
                'improvement': improvement,
                'is_better': is_better
            }}
        )
        
        return is_better, improvement
    
    def deploy_model(
        self,
        model_name: str,
        version: str,
        stage: str = "Production"
    ) -> bool:
        """
        Déploie un modèle en production dans MLflow
        
        Args:
            model_name: Nom du modèle
            version: Version du modèle
            stage: Stage de déploiement (Production, Staging, etc.)
        
        Returns:
            True si succès, False sinon
        """
        try:
            client = mlflow.tracking.MlflowClient()
            
            # Transitionner le modèle vers Production
            client.transition_model_version_stage(
                name=model_name,
                version=version,
                stage=stage
            )
            
            # Archiver les anciennes versions en production (optionnel)
            # On pourrait garder plusieurs versions en staging pour A/B testing
            
            logger.info(
                f"Modèle déployé: {model_name} v{version} → {stage}",
                extra={'extra_fields': {'model_name': model_name, 'version': version, 'stage': stage}}
            )
            
            return True
        
        except Exception as e:
            logger.error(f"Erreur lors du déploiement: {e}", exc_info=True)
            return False
    
    def notify_api_reload(self) -> bool:
        """Demande à l'API de recharger Production. No-op si elle ne tourne pas."""
        url = os.getenv("API_RELOAD_URL", "http://localhost:8000/model/reload")
        try:
            import requests

            response = requests.post(url, timeout=5)
            if response.status_code == 200:
                logger.info(f"API rechargée: {url}")
                return True
            logger.warning(f"Reload API {response.status_code}: {response.text}")
        except Exception as exc:
            logger.info(f"API absente, reload ignoré ({exc})")
        return False

    def retrain(
        self,
        trigger: RetrainTrigger = RetrainTrigger.MANUAL,
        data_path: Optional[str] = None,
        model_type: str = "random_forest",
        current_data_path: Optional[str] = None,
    ) -> RetrainResult:
        """
        Pipeline complet de retrain
        
        Args:
            trigger: Type de déclencheur
            data_path: Chemin vers les données (optionnel, utilise config par défaut)
            model_type: Type de modèle à entraîner
        
        Returns:
            RetrainResult avec les détails du retrain
        """
        logger.info(f"Démarrage du retrain (trigger: {trigger.value})...")
        
        # Vérifier si le retrain est activé
        if not self.retrain_config.get('enabled', True):
            return RetrainResult(
                success=False,
                reason="Retrain désactivé dans la configuration"
            )
        
        try:
            # Chemin des données
            if data_path is None:
                processed_path = self.data_config.get('processed_path', 'data/processed')
                train_file = self.data_config.get('train_file', 'train.csv')
                data_path = os.path.join(processed_path, train_file)
            
            if trigger == RetrainTrigger.DRIFT:
                if not current_data_path:
                    return RetrainResult(
                        success=False,
                        reason="Drift: fournir --current-data (ex. data/processed/drift.csv)",
                    )
                drift_score, is_drift = self.check_drift(
                    data_path, current_data_path=current_data_path
                )
                if not is_drift:
                    return RetrainResult(
                        success=False,
                        reason=f"Pas de drift détecté (score: {drift_score:.4f})",
                    )
            
            # 2. Récupérer le modèle actuel en production
            model_name = f"document-classifier-{model_type}"
            current_model, current_version = self.get_current_production_model(model_name)
            
            if current_model is None:
                logger.warning("Aucun modèle en production trouvé, entraînement d'un nouveau modèle")
                current_metrics = None
            else:
                # Récupérer les métriques du modèle actuel
                current_metrics = self.get_model_metrics(model_name, current_version)
            
            # 3. Entraîner un nouveau modèle
            new_model, new_metrics, run_id = self.train_new_model(
                data_path,
                model_type=model_type,
                extra_data_path=current_data_path,
            )
            
            # 4. Comparer les modèles
            if current_metrics is None:
                # Pas de modèle actuel, déployer directement
                is_better = True
                improvement = None
            else:
                comparison_metric = self.retrain_config.get('comparison_metric', 'f1_score')
                is_better, improvement = self.compare_models(
                    current_metrics,
                    new_metrics,
                    comparison_metric=comparison_metric
                )
            
            # 5. Déployer si meilleur
            deployed = False
            if is_better:
                # Récupérer la version du nouveau modèle
                client = mlflow.tracking.MlflowClient()
                latest_versions = client.get_latest_versions(model_name)
                if latest_versions:
                    new_version = latest_versions[0].version
                    deployed = self.deploy_model(model_name, new_version, stage="Production")
                    
                    if deployed:
                        logger.info("[OK] Nouveau modele deploye en production")
                        self.notify_api_reload()
                    else:
                        logger.error("[ERROR] Echec du deploiement du nouveau modele")
                else:
                    logger.error("Impossible de récupérer la version du nouveau modèle")
                    deployed = False
            else:
                logger.info(
                    f"[INFO] Nouveau modele pas meilleur (amelioration: {improvement:.4f}), "
                    "pas de deploiement"
                )
            
            # 6. Retourner le résultat
            comparison_metric = self.retrain_config.get('comparison_metric', 'f1_score')
            result = RetrainResult(
                success=True,
                new_model_version=run_id,
                old_model_metric=current_metrics.get(comparison_metric) if current_metrics else None,
                new_model_metric=new_metrics.get(comparison_metric),
                improvement=improvement,
                deployed=deployed,
                reason="Retrain réussi" if deployed else "Nouveau modèle pas meilleur"
            )
            
            return result
        
        except Exception as e:
            logger.error(f"Erreur lors du retrain: {e}", exc_info=True)
            return RetrainResult(
                success=False,
                error=str(e),
                reason=f"Erreur: {str(e)}"
            )

