"""CSV courant biaisé (surtout sports) pour déclencher le drift vs train.csv."""
import numpy as np
import pandas as pd
from pathlib import Path

Path("data/processed").mkdir(parents=True, exist_ok=True)
np.random.seed(7)

categories = {
    "technology": [
        "artificial intelligence machine learning deep learning neural networks",
        "cloud computing serverless microservices docker kubernetes",
    ],
    "science": [
        "quantum physics particle physics theoretical physics research",
        "biology genetics molecular biology evolution ecosystem",
    ],
    "sports": [
        "football soccer world cup champions league",
        "basketball nba playoffs championship finals",
        "tennis wimbledon french open grand slam",
        "olympics athletics swimming track and field",
        "cycling tour de france mountain biking racing",
    ],
    "business": [
        "startup entrepreneurship venture capital funding investment",
        "marketing digital marketing social media advertising",
    ],
    "health": [
        "nutrition healthy eating diet exercise fitness",
        "mental health wellness meditation stress management",
    ],
}

# Train est ~équilibré (20 % / classe). Ici 80 % sports.
counts = {
    "sports": 400,
    "technology": 25,
    "science": 25,
    "business": 25,
    "health": 25,
}

rows = []
for label, n in counts.items():
    texts = categories[label]
    for _ in range(n):
        words = np.random.choice(texts).split()
        np.random.shuffle(words)
        rows.append({"text": " ".join(words[: max(4, len(words) - 1)]), "label": label})

df = pd.DataFrame(rows).sample(frac=1, random_state=7).reset_index(drop=True)
out = Path("data/processed/drift.csv")
df.to_csv(out, index=False)
print(f"[OK] Drift set: {len(df)} rows -> {out}")
print(df["label"].value_counts(normalize=True).round(3))
