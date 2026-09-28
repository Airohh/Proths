"""AG News : téléchargement, cache local, découpage train / holdout / stream.

- train   : split train officiel (120 000 articles), éventuellement sous-échantillonné.
- holdout : moitié stratifiée du split test. Sert UNIQUEMENT à juger les modèles.
- stream  : autre moitié du split test. Joue le trafic de production ; ses vrais
            labels reviennent plus tard via POST /feedback.

holdout et stream sont disjoints : un label de feedback ne peut jamais fuiter
dans le jeu qui décide des promotions.
"""

import io
from pathlib import Path

import httpx
import pandas as pd
from sklearn.model_selection import train_test_split

from config import get_config

LABELS = ["World", "Sports", "Business", "Sci/Tech"]

# Source canonique (Hugging Face), puis miroir CSV du jeu original de Zhang et al. (2015).
HF_URL = "https://huggingface.co/datasets/fancyzhx/ag_news/resolve/main/data/{split}-00000-of-00001.parquet"
MIRROR_URL = (
    "https://raw.githubusercontent.com/mhjabreel/CharCnn_Keras/master/data/ag_news_csv/{split}.csv"
)


def _from_hf(split: str) -> pd.DataFrame:
    response = httpx.get(HF_URL.format(split=split), follow_redirects=True, timeout=120)
    response.raise_for_status()
    df = pd.read_parquet(io.BytesIO(response.content))
    return pd.DataFrame({"text": df["text"], "label": df["label"].map(dict(enumerate(LABELS)))})


def _from_mirror(split: str) -> pd.DataFrame:
    response = httpx.get(MIRROR_URL.format(split=split), follow_redirects=True, timeout=120)
    response.raise_for_status()
    df = pd.read_csv(io.BytesIO(response.content), header=None, names=["y", "title", "desc"])
    return pd.DataFrame(
        {
            "text": df["title"] + " " + df["desc"],
            "label": df["y"].map({i + 1: name for i, name in enumerate(LABELS)}),
        }
    )


def download_split(split: str, cache_dir: Path) -> pd.DataFrame:
    """Retourne le split AG News (text, label), depuis le cache si présent."""
    cache = cache_dir / f"ag_news_{split}.csv"
    if cache.exists():
        return pd.read_csv(cache)
    errors = []
    for loader in (_from_hf, _from_mirror):
        try:
            df = loader(split).dropna()
            break
        except Exception as exc:  # réseau, format : on tente la source suivante
            errors.append(f"{loader.__name__}: {exc}")
    else:
        raise RuntimeError("AG News introuvable : " + " | ".join(errors))
    cache_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(cache, index=False)
    return df


def stratified_sample(df: pd.DataFrame, n: int | None, seed: int) -> pd.DataFrame:
    if not n or n >= len(df):
        return df.reset_index(drop=True)
    sample, _ = train_test_split(df, train_size=n, stratify=df["label"], random_state=seed)
    return sample.reset_index(drop=True)


def split_test(test: pd.DataFrame, seed: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    holdout, stream = train_test_split(
        test, test_size=0.5, stratify=test["label"], random_state=seed
    )
    return holdout.reset_index(drop=True), stream.reset_index(drop=True)


def data_paths() -> dict[str, Path]:
    cfg = get_config()["data"]
    root = Path(cfg["processed_path"])
    return {
        "train": root / cfg["train_file"],
        "holdout": root / cfg["holdout_file"],
        "stream": root / cfg["stream_file"],
    }


def load(name: str) -> pd.DataFrame:
    """Charge train / holdout / stream préparés par scripts/prepare_ag_news.py."""
    path = data_paths()[name]
    if not path.exists():
        raise FileNotFoundError(f"{path} absent : lancer `make data` d'abord")
    return pd.read_csv(path)
