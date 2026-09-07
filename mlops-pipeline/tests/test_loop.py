"""Boucle CI : petit train → /predict → journal → drift."""
import sys
from pathlib import Path

import pandas as pd
from fastapi.testclient import TestClient

from src.inference import api
from src.retraining.auto_retrain import AutoRetrainer

SPORTS = [
    "lakers defeat celtics in overtime playoff basketball game",
    "manchester united wins champions league final soccer football",
    "wimbledon tennis champion claims third grand slam title",
    "olympic swimming record broken in 200 meter freestyle",
    "tour de france cycling leader extends yellow jersey gap",
    "nba finals game seven buzzer beater seals championship",
    "world cup football quarterfinal goes to penalty shootout",
    "formula one grand prix victory after late overtake",
]


def _write_tiny_train(root: Path) -> None:
    rows = []
    templates = {
        "World": "senate votes sanctions after diplomatic talks overnight",
        "Sports": "football soccer championship final overtime victory",
        "Business": "oil prices fall as bank earnings beat forecasts",
        "Sci/Tech": "chipmaker forecasts weaker data center demand year",
    }
    for label, text in templates.items():
        for i in range(20):
            rows.append({"text": f"{text} article {i} {label.lower()}", "label": label})
    out = root / "data" / "processed"
    out.mkdir(parents=True)
    pd.DataFrame(rows).to_csv(out / "train.csv", index=False)


def test_train_predict_log_drift(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _write_tiny_train(tmp_path)

    sys.argv = [
        "train.py",
        "--model-type",
        "random_forest",
        "--holdout",
        "missing.csv",
        "--metrics-out",
        "reports/_test_metrics.json",
    ]
    from src.training.train import main as train_main

    train_main()
    api.load_model()

    client = TestClient(api.app)
    for text in SPORTS:
        response = client.post("/predict", json={"text": text})
        assert response.status_code == 200, response.text

    log = Path("data/processed/predictions.csv")
    assert log.exists()

    score, is_drift = AutoRetrainer().check_drift(
        "data/processed/train.csv",
        current_data_path=str(log),
    )
    assert score > 0
    assert is_drift
