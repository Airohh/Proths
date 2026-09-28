import pickle

import pytest

from src.training.pipeline import MODEL_TYPES, build_pipeline, clean_texts
from tests.conftest import make_docs


def test_clean_texts_removes_agnews_artifacts():
    raw = ["Wall St. Bears Claw Back #36;10 billion\\deal &lt;b&gt;"]
    tokens = clean_texts(raw)[0].split()
    assert tokens == ["wall", "st", "bears", "claw", "back", "10", "billion", "deal", "b"]


@pytest.mark.parametrize("model_type", MODEL_TYPES)
def test_every_model_type_trains_and_gives_probabilities(model_type):
    df = make_docs(240, seed=0)
    pipeline = build_pipeline(model_type).fit(df["text"], df["label"])
    proba = pipeline.predict_proba(["Goal in the playoff match"])
    assert proba.shape == (1, 4)
    assert proba.sum() == pytest.approx(1.0)


def test_raw_text_is_cleaned_inside_the_pipeline():
    """Pas de train/serve skew : le texte brut et le texte nettoyé donnent la même sortie."""
    df = make_docs(240, seed=0)
    pipeline = build_pipeline("logreg").fit(df["text"], df["label"])
    raw = "SHARES, profit & EARNINGS!!! (Reuters)"
    assert (pipeline.predict_proba([raw]) == pipeline.predict_proba(clean_texts([raw]))).all()


def test_pipeline_survives_pickling_with_its_vocabulary():
    df = make_docs(240, seed=0)
    pipeline = build_pipeline("logreg").fit(df["text"], df["label"])
    clone = pickle.loads(pickle.dumps(pipeline))
    assert clone.predict(["nasa space research"]) == pipeline.predict(["nasa space research"])


def test_unknown_model_type():
    with pytest.raises(ValueError):
        build_pipeline("xgboost")
