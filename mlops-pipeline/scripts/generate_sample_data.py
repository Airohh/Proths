"""
Script pour générer des données de test pour la classification de documents
"""
import pandas as pd
import numpy as np
from pathlib import Path

# Créer le dossier data/processed si nécessaire
Path("data/processed").mkdir(parents=True, exist_ok=True)

# Générer des données de test
np.random.seed(42)

# Catégories de documents
categories = {
    'technology': [
        'artificial intelligence machine learning deep learning neural networks',
        'cloud computing serverless microservices docker kubernetes',
        'programming python javascript typescript software development',
        'data science analytics big data data engineering',
        'cybersecurity encryption authentication security protocols'
    ],
    'science': [
        'quantum physics particle physics theoretical physics research',
        'biology genetics molecular biology evolution ecosystem',
        'chemistry organic chemistry biochemistry chemical reactions',
        'astronomy space exploration planets stars galaxies',
        'mathematics algebra calculus statistics probability'
    ],
    'sports': [
        'football soccer world cup champions league',
        'basketball nba playoffs championship finals',
        'tennis wimbledon french open grand slam',
        'olympics athletics swimming track and field',
        'cycling tour de france mountain biking racing'
    ],
    'business': [
        'startup entrepreneurship venture capital funding investment',
        'marketing digital marketing social media advertising',
        'finance banking stock market cryptocurrency trading',
        'management leadership team building project management',
        'ecommerce online retail customer experience sales'
    ],
    'health': [
        'nutrition healthy eating diet exercise fitness',
        'mental health wellness meditation stress management',
        'medical research healthcare treatment diagnosis',
        'fitness training workout strength conditioning',
        'preventive medicine public health epidemiology'
    ]
}

# Générer le dataset
data = []
for category, texts in categories.items():
    for _ in range(100):  # 100 documents par catégorie
        base_text = np.random.choice(texts)
        # Ajouter de la variabilité
        words = base_text.split()
        # Mélanger et ajouter des mots
        np.random.shuffle(words)
        text = ' '.join(words[:np.random.randint(5, len(words))])
        data.append({
            'text': text,
            'label': category
        })

# Créer DataFrame
df = pd.DataFrame(data)

# Mélanger
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

# Sauvegarder
df.to_csv('data/processed/train.csv', index=False)
print(f"[OK] Dataset genere : {len(df)} documents")
print(f"[INFO] Repartition par categorie:")
print(df['label'].value_counts())

