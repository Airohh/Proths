"""
Pipeline de training avec MLflow tracking
"""
import json
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
sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.training.preprocessing import (
    preprocess_data,
    transform_texts,
    load_preprocessing_artifacts,
)


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
    parser.add_argument('--holdout', type=str, default='data/processed/holdout.csv',
                       help='CSV holdout (ignoré s\'il n\'existe pas)')
    parser.add_argument('--metrics-out', type=str, default='reports/metrics.json',
                       help='Où écrire les métriques')
    
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

        report = {
            "dataset": Path(args.data_path).name,
            "model_type": args.model_type,
            "n_train": int(train_size),
            "n_val": int(val_size),
            "val": {k: float(v) for k, v in metrics.items()},
        }

        holdout_path = Path(args.holdout)
        if holdout_path.exists():
            holdout = pd.read_csv(holdout_path)
            vectorizer, label_encoder = load_preprocessing_artifacts()
            X_h = transform_texts(holdout, vectorizer=vectorizer)
            y_h = label_encoder.transform(holdout["label"])
            y_h_pred = model.predict(X_h)
            holdout_metrics = {
                "accuracy": float(accuracy_score(y_h, y_h_pred)),
                "precision": float(precision_score(y_h, y_h_pred, average="weighted")),
                "recall": float(recall_score(y_h, y_h_pred, average="weighted")),
                "f1_score": float(f1_score(y_h, y_h_pred, average="weighted")),
                "n": int(len(holdout)),
            }
            report["holdout"] = holdout_metrics
            for name, value in holdout_metrics.items():
                if name != "n":
                    mlflow.log_metric(f"holdout_{name}", value)
            print("\n[INFO] Holdout:")
            for name, value in holdout_metrics.items():
                print(f"   {name}: {value}" if name == "n" else f"   {name}: {value:.4f}")

        metrics_path = Path(args.metrics_out)
        metrics_path.parent.mkdir(parents=True, exist_ok=True)
        metrics_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"[OK] Metriques: {metrics_path}")


if __name__ == "__main__":
    main()

