"""
Pipeline de training avec MLflow tracking
"""
import os
import sys
import argparse
import pandas as pd
import numpy as np
from pathlib import Path
import mlflow
import mlflow.sklearn
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
import lightgbm as lgb

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent.parent))

from src.training.preprocessing import preprocess_data


def train_baseline_model(X_train, y_train, X_val, y_val, model_type='random_forest'):
    """
    Entraîne un modèle baseline (Random Forest ou LightGBM)
    
    Args:
        X_train: Features d'entraînement
        y_train: Labels d'entraînement
        X_val: Features de validation
        y_val: Labels de validation
        model_type: Type de modèle ('random_forest' ou 'lightgbm')
    
    Returns:
        Modèle entraîné et métriques
    """
    if model_type == 'random_forest':
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
    elif model_type == 'lightgbm':
        model = lgb.LGBMClassifier(
            n_estimators=100,
            max_depth=10,
            learning_rate=0.1,
            random_state=42,
            verbose=-1
        )
    else:
        raise ValueError(f"Modèle non supporté: {model_type}")
    
    # Entraînement
    model.fit(X_train, y_train)
    
    # Prédictions
    y_pred = model.predict(X_val)
    
    # Métriques
    metrics = {
        'accuracy': accuracy_score(y_val, y_pred),
        'precision': precision_score(y_val, y_pred, average='weighted'),
        'recall': recall_score(y_val, y_pred, average='weighted'),
        'f1_score': f1_score(y_val, y_pred, average='weighted')
    }
    
    return model, metrics


def main():
    parser = argparse.ArgumentParser(description='Training pipeline')
    parser.add_argument('--data-path', type=str, default='data/processed/train.csv',
                       help='Chemin vers les données d\'entraînement')
    parser.add_argument('--model-type', type=str, default='random_forest',
                       choices=['random_forest', 'lightgbm'],
                       help='Type de modèle à entraîner')
    parser.add_argument('--experiment-name', type=str, default='document-classification',
                       help='Nom de l\'expérience MLflow')
    
    args = parser.parse_args()
    
    # Setup MLflow
    mlflow.set_experiment(args.experiment_name)
    
    print(f"[INFO] Chargement des donnees depuis {args.data_path}")
    df = pd.read_csv(args.data_path)
    
    print(f"[INFO] Preprocessing des donnees...")
    X, y = preprocess_data(df)
    
    print(f"[INFO] Split train/validation (80/20)...")
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"[INFO] Entrainement du modele {args.model_type}...")
    
    with mlflow.start_run():
        # Entraînement
        model, metrics = train_baseline_model(
            X_train, y_train, X_val, y_val, 
            model_type=args.model_type
        )
        
        # Logging des paramètres
        mlflow.log_param("model_type", args.model_type)
        # Utiliser shape[0] pour les matrices sparse
        train_size = X_train.shape[0] if hasattr(X_train, 'shape') else len(X_train)
        val_size = X_val.shape[0] if hasattr(X_val, 'shape') else len(X_val)
        mlflow.log_param("train_size", train_size)
        mlflow.log_param("val_size", val_size)
        
        # Logging des métriques
        for metric_name, metric_value in metrics.items():
            mlflow.log_metric(metric_name, metric_value)
        
        # Logging du modèle
        mlflow.sklearn.log_model(
            model,
            "model",
            registered_model_name=f"document-classifier-{args.model_type}"
        )
        
        print(f"\n[OK] Entrainement termine!")
        print(f"[INFO] Metriques:")
        for metric_name, metric_value in metrics.items():
            print(f"   {metric_name}: {metric_value:.4f}")
        
        # Classification report
        y_pred = model.predict(X_val)
        print(f"\n[INFO] Classification Report:")
        print(classification_report(y_val, y_pred))
        
        # Sauvegarder le modèle localement
        model_path = Path("models") / f"{args.model_type}_model.pkl"
        model_path.parent.mkdir(exist_ok=True)
        mlflow.sklearn.save_model(model, str(model_path))
        print(f"\n[OK] Modele sauvegarde dans {model_path}")


if __name__ == "__main__":
    main()

