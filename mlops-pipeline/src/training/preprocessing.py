"""
Preprocessing des données pour la classification de documents
"""
import os
import pickle
from pathlib import Path

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder

VECTORIZER_PATH = Path("models") / "vectorizer.pkl"
LABEL_ENCODER_PATH = Path("models") / "label_encoder.pkl"


def clean_text_series(series: pd.Series) -> pd.Series:
    cleaned = series.astype(str).str.lower()
    return cleaned.str.replace(r"[^\w\s]", "", regex=True)


def _tfidf() -> TfidfVectorizer:
    return TfidfVectorizer(
        max_features=5000,
        stop_words="english",
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.95,
    )


def preprocess_data(df, text_column="text", label_column="label", max_features=5000):
    """Fit TF-IDF + labels. Écrit les artefacts. Réservé à l'entraînement."""
    if text_column not in df.columns:
        raise ValueError(f"Colonne '{text_column}' introuvable dans les données")
    if label_column not in df.columns:
        raise ValueError(f"Colonne '{label_column}' introuvable dans les données")

    frame = df.copy()
    frame[text_column] = clean_text_series(frame[text_column])

    vectorizer = _tfidf()
    vectorizer.max_features = max_features
    X = vectorizer.fit_transform(frame[text_column])

    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(frame[label_column])

    print("[OK] Preprocessing termine:")
    print(f"   - Shape features: {X.shape}")
    print(f"   - Nombre de classes: {len(np.unique(y))}")
    print(f"   - Classes: {label_encoder.classes_}")

    os.makedirs("models", exist_ok=True)
    with open(VECTORIZER_PATH, "wb") as f:
        pickle.dump(vectorizer, f)
    with open(LABEL_ENCODER_PATH, "wb") as f:
        pickle.dump(label_encoder, f)

    return X, y


def load_preprocessing_artifacts():
    with open(VECTORIZER_PATH, "rb") as f:
        vectorizer = pickle.load(f)
    with open(LABEL_ENCODER_PATH, "rb") as f:
        label_encoder = pickle.load(f)
    return vectorizer, label_encoder


def transform_texts(df, text_column="text", vectorizer=None):
    """Transforme sans refit — n'écrase pas vectorizer.pkl."""
    if text_column not in df.columns:
        raise ValueError(f"Colonne '{text_column}' introuvable dans les données")
    if vectorizer is None:
        vectorizer, _ = load_preprocessing_artifacts()
    texts = clean_text_series(df[text_column])
    return vectorizer.transform(texts)


def vectorize_for_drift(reference_df, current_df, text_column="text"):
    """Même espace TF-IDF pour ref et current. Pas d'écriture disque."""
    if VECTORIZER_PATH.exists():
        vectorizer, _ = load_preprocessing_artifacts()
        X_ref = transform_texts(reference_df, text_column, vectorizer)
        X_curr = transform_texts(current_df, text_column, vectorizer)
        return X_ref, X_curr

    vectorizer = _tfidf()
    ref_texts = clean_text_series(reference_df[text_column])
    curr_texts = clean_text_series(current_df[text_column])
    X_ref = vectorizer.fit_transform(ref_texts)
    X_curr = vectorizer.transform(curr_texts)
    return X_ref, X_curr
