"""Télécharge AG News (Hugging Face), mappe les 4 classes, écrit train + holdout."""
import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).parent.parent))

LABELS = {0: "World", 1: "Sports", 2: "Business", 3: "Sci/Tech"}


def _to_frame(split, limit: int, seed: int) -> pd.DataFrame:
    from datasets import load_dataset

    ds = load_dataset("ag_news", split=split)
    ds = ds.shuffle(seed=seed)
    if limit and limit < len(ds):
        ds = ds.select(range(limit))
    df = pd.DataFrame(ds)
    if df["label"].dtype != object:
        df["label"] = df["label"].map(LABELS)
    df = df[["text", "label"]].dropna()
    return df


def main():
    parser = argparse.ArgumentParser(description="Préparer AG News")
    parser.add_argument("--train-limit", type=int, default=4000)
    parser.add_argument("--holdout-limit", type=int, default=800)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--train-out", default="data/processed/train.csv")
    parser.add_argument("--holdout-out", default="data/processed/holdout.csv")
    args = parser.parse_args()

    print("[INFO] Téléchargement AG News (Hugging Face)...")
    train = _to_frame("train", args.train_limit, args.seed)
    holdout = _to_frame("test", args.holdout_limit, args.seed)

    Path(args.train_out).parent.mkdir(parents=True, exist_ok=True)
    train.to_csv(args.train_out, index=False)
    holdout.to_csv(args.holdout_out, index=False)

    print(f"[OK] train    {len(train)} -> {args.train_out}")
    print(train["label"].value_counts().to_string())
    print(f"[OK] holdout  {len(holdout)} -> {args.holdout_out}")
    print(holdout["label"].value_counts().to_string())


if __name__ == "__main__":
    main()
