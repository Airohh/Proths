"""Journal des prédictions — source de drift (labels = prédictions, pas la vérité)."""
import threading
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

LOG_PATH = Path("data/processed/predictions.csv")
_LOCK = threading.Lock()


def log_predictions(rows: list[dict]) -> None:
    if not rows:
        return
    payload = []
    now = datetime.now(timezone.utc).isoformat()
    for row in rows:
        payload.append(
            {
                "text": row["text"],
                "label": row["label"],
                "confidence": row.get("confidence"),
                "timestamp": now,
            }
        )
    frame = pd.DataFrame(payload)
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _LOCK:
        header = not LOG_PATH.exists()
        frame.to_csv(LOG_PATH, mode="a", header=header, index=False)
