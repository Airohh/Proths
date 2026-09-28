"""Rejoue le split `stream` contre l'API, avec biais de classe et feedback différé.

    python scripts/simulate_traffic.py --n 500                           # trafic normal
    python scripts/simulate_traffic.py --n 500 --skew Sports --ratio 0.7 # drift de mix
    python scripts/simulate_traffic.py --n 500 --feedback 0.5            # 50 % labellisés

Le vrai label est connu (split test d'AG News) : il est renvoyé via /feedback,
comme le ferait une équipe d'annotation ou un utilisateur qui corrige.
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def sample_stream(
    stream: pd.DataFrame, n: int, skew: str | None, ratio: float, seed: int
) -> pd.DataFrame:
    """n articles ; si `skew`, une part `ratio` vient de cette classe."""
    rng = np.random.default_rng(seed)
    if not skew:
        return stream.sample(n=n, replace=n > len(stream), random_state=seed)
    n_skew = int(n * ratio)
    pool, rest = stream[stream["label"] == skew], stream[stream["label"] != skew]
    parts = [
        pool.sample(n=n_skew, replace=n_skew > len(pool), random_state=seed),
        rest.sample(n=n - n_skew, replace=n - n_skew > len(rest), random_state=seed),
    ]
    return pd.concat(parts).iloc[rng.permutation(n)]


def run_traffic(
    client,
    stream: pd.DataFrame,
    *,
    n: int,
    skew: str | None = None,
    ratio: float = 0.7,
    feedback: float = 1.0,
    batch_size: int = 50,
    seed: int = 0,
) -> dict:
    """`client` : httpx.Client ou fastapi TestClient (même interface .post)."""
    rng = np.random.default_rng(seed)
    rows = sample_stream(stream, n, skew, ratio, seed)
    sent = correct = labeled = 0
    for start in range(0, len(rows), batch_size):
        chunk = rows.iloc[start : start + batch_size]
        response = client.post("/predict/batch", json={"texts": chunk["text"].tolist()})
        response.raise_for_status()
        for pred, true_label in zip(response.json()["predictions"], chunk["label"], strict=True):
            sent += 1
            if rng.random() < feedback:
                fb = client.post(
                    "/feedback", json={"prediction_id": pred["prediction_id"], "label": true_label}
                )
                fb.raise_for_status()
                labeled += 1
                correct += fb.json()["correct"]
    return {"sent": sent, "labeled": labeled, "accuracy": correct / labeled if labeled else None}


def main() -> None:
    import httpx

    from src import data

    parser = argparse.ArgumentParser()
    parser.add_argument("--api-url", default="http://localhost:8000")
    parser.add_argument("--n", type=int, default=500)
    parser.add_argument("--skew", default=None, help="World | Sports | Business | Sci/Tech")
    parser.add_argument("--ratio", type=float, default=0.7)
    parser.add_argument("--feedback", type=float, default=1.0)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    with httpx.Client(base_url=args.api_url, timeout=60) as client:
        stats = run_traffic(
            client,
            data.load("stream"),
            n=args.n,
            skew=args.skew,
            ratio=args.ratio,
            feedback=args.feedback,
            seed=args.seed,
        )
    print(stats)


if __name__ == "__main__":
    main()
