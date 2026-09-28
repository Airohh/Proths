"""Chaque test tourne dans un dossier isolé : MLflow, données et journal locaux."""

import numpy as np
import pandas as pd
import pytest

from config import get_config

VOCAB = {
    "World": "election minister president talks troops embassy treaty parliament rebels summit",
    "Sports": "match goal coach season playoff tennis striker league champion stadium",
    "Business": "shares profit market earnings bank oil investors stocks merger quarterly",
    "Sci/Tech": "software internet chip google space nasa browser microsoft research wireless",
}
SHARED = "the new report said on monday after week year people officials".split()


def make_docs(n: int, seed: int, noise: float = 0.35) -> pd.DataFrame:
    """Documents synthétiques : mots de la classe + mots communs + mots d'une autre classe."""
    rng = np.random.default_rng(seed)
    labels = list(VOCAB)
    rows = []
    for i in range(n):
        label = labels[i % len(labels)]
        own = VOCAB[label].split()
        other = VOCAB[labels[rng.integers(len(labels))]].split()
        words = list(rng.choice(own, 4)) + list(rng.choice(SHARED, 6))
        words += list(rng.choice(other, int(noise * 10)))
        rng.shuffle(words)
        rows.append({"text": " ".join(words).capitalize() + ".", "label": label})
    return pd.DataFrame(rows)


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("MLFLOW_TRACKING_URI", f"sqlite:///{tmp_path}/mlruns/mlflow.db")
    monkeypatch.setenv("DATA_DIR", str(tmp_path / "data" / "processed"))
    monkeypatch.setenv("PREDICTIONS_DB", str(tmp_path / "data" / "predictions.db"))
    monkeypatch.setenv("MODEL_POLL_SECONDS", "0")
    monkeypatch.setenv("RETRAIN_COOLDOWN", "0")
    monkeypatch.setenv("API_RELOAD_URL", "http://127.0.0.1:9/unused")
    get_config.cache_clear()

    processed = tmp_path / "data" / "processed"
    processed.mkdir(parents=True)
    make_docs(400, seed=1).to_csv(processed / "train.csv", index=False)
    make_docs(200, seed=2).to_csv(processed / "holdout.csv", index=False)
    make_docs(400, seed=3).to_csv(processed / "stream.csv", index=False)
    yield tmp_path
    get_config.cache_clear()
