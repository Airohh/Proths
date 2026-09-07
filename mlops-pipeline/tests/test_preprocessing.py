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
            'This is a test document about technology and computers',
            'Another test document about technology and software',
            'A science document about physics and research',
            'Another science document about physics and biology',
            'A sports document about football and tennis',
            'Another sports document about football and basketball',
        ],
        'label': ['tech', 'tech', 'science', 'science', 'sports', 'sports']
    })
    
    # Preprocessing
    X, y = preprocess_data(df, text_column='text', label_column='label')
    
    # Vérifications
    assert X.shape[0] == 6
    assert len(y) == 6
    assert len(np.unique(y)) == 3


def test_preprocessing_missing_column():
    """Test avec colonne manquante"""
    df = pd.DataFrame({
        'text': ['test'],
        'wrong_column': ['label']
    })
    
    with pytest.raises(ValueError):
        preprocess_data(df, text_column='text', label_column='label')

