"""
Tests pour le preprocessing
"""
import pytest
import pandas as pd
import numpy as np
from src.training.preprocessing import preprocess_data


def test_preprocessing():
    """Test basique du preprocessing"""
    # Données de test
    df = pd.DataFrame({
        'text': [
            'This is a test document about technology',
            'Another document about science',
            'A third document about sports'
        ],
        'label': ['tech', 'science', 'sports']
    })
    
    # Preprocessing
    X, y = preprocess_data(df, text_column='text', label_column='label')
    
    # Vérifications
    assert X.shape[0] == 3  # 3 documents
    assert len(y) == 3  # 3 labels
    assert len(np.unique(y)) == 3  # 3 classes uniques


def test_preprocessing_missing_column():
    """Test avec colonne manquante"""
    df = pd.DataFrame({
        'text': ['test'],
        'wrong_column': ['label']
    })
    
    with pytest.raises(ValueError):
        preprocess_data(df, text_column='text', label_column='label')

