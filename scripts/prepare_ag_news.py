"""Prépare data/processed/{train,holdout,stream}.csv à partir d'AG News.

python scripts/prepare_ag_news.py                    # 120 000 articles de train
python scripts/prepare_ag_news.py --train-size 5000  # démarrage à froid (démo)
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import get_config  # noqa: E402
from src import data  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Préparer AG News")
    parser.add_argument("--train-size", type=int, default=None, help="défaut : tout le split train")
    parser.add_argument("--raw-dir", default="data/raw", help="cache des téléchargements")
    args = parser.parse_args()

    seed = int(get_config()["data"]["seed"])
    raw = Path(args.raw_dir)
    train = data.stratified_sample(data.download_split("train", raw), args.train_size, seed)
    holdout, stream = data.split_test(data.download_split("test", raw), seed)

    paths = data.data_paths()
    paths["train"].parent.mkdir(parents=True, exist_ok=True)
    for name, frame in (("train", train), ("holdout", holdout), ("stream", stream)):
        frame.to_csv(paths[name], index=False)
        counts = frame["label"].value_counts().to_dict()
        print(f"{name:8s} {len(frame):6d} -> {paths[name]}  {counts}")


if __name__ == "__main__":
    main()
