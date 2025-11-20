"""
Preprocessing des données pour la classification de documents
"""
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder


def preprocess_data(df, text_column='text', label_column='label', max_features=5000):
    """
    Preprocess les données pour la classification
    
    Args:
        df: DataFrame avec colonnes 'text' et 'label'
        text_column: Nom de la colonne contenant le texte
        label_column: Nom de la colonne contenant les labels
        max_features: Nombre maximum de features TF-IDF
    
    Returns:
        X: Features vectorisées (TF-IDF)
        y: Labels encodés
    """
    # Vérifier les colonnes
    if text_column not in df.columns:
        raise ValueError(f"Colonne '{text_column}' introuvable dans les données")
    if label_column not in df.columns:
        raise ValueError(f"Colonne '{label_column}' introuvable dans les données")
    
    # Nettoyage basique du texte
    df[text_column] = df[text_column].astype(str).str.lower()
    df[text_column] = df[text_column].str.replace(r'[^\w\s]', '', regex=True)
    
    # Vectorisation TF-IDF
    vectorizer = TfidfVectorizer(
        max_features=max_features,
        stop_words='english',
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.95
    )
    
    X = vectorizer.fit_transform(df[text_column])
    
    # Encodage des labels
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(df[label_column])
    
    print(f"[OK] Preprocessing termine:")
    print(f"   - Shape features: {X.shape}")
    print(f"   - Nombre de classes: {len(np.unique(y))}")
    print(f"   - Classes: {label_encoder.classes_}")
    
    # Sauvegarder le vectorizer et label_encoder pour l'inférence
    import pickle
    import os
    os.makedirs('models', exist_ok=True)
    
    with open('models/vectorizer.pkl', 'wb') as f:
        pickle.dump(vectorizer, f)
    
    with open('models/label_encoder.pkl', 'wb') as f:
        pickle.dump(label_encoder, f)
    
    return X, y


def load_preprocessing_artifacts():
    """
    Charge les artifacts de preprocessing (vectorizer, label_encoder)
    
    Returns:
        vectorizer, label_encoder
    """
    import pickle
    
    with open('models/vectorizer.pkl', 'rb') as f:
        vectorizer = pickle.load(f)
    
    with open('models/label_encoder.pkl', 'rb') as f:
        label_encoder = pickle.load(f)
    
    return vectorizer, label_encoder

