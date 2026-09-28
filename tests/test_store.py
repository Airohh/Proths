import time

from src.inference.store import PredictionStore


def test_log_feedback_and_queries(tmp_path):
    store = PredictionStore(tmp_path / "p.db")
    ids = store.log(
        [
            {"text": "a", "predicted": "Sports", "confidence": 0.9},
            {"text": "b", "predicted": "World", "confidence": 0.6},
        ],
        model_version="1",
    )
    store.log([{"text": "c", "predicted": "Business", "confidence": 0.8}], model_version="2")

    assert len(store.recent(10)) == 3
    assert store.recent(10, model_version="1")["text"].tolist() == ["b", "a"]

    before = time.time()
    assert store.add_feedback(ids[0], "Sports") == {"predicted": "Sports", "true_label": "Sports"}
    assert store.add_feedback("inconnu", "Sports") is None

    labeled = store.labeled()
    assert labeled["true_label"].tolist() == ["Sports"]
    assert len(store.labeled(since=before - 1)) == 1
    assert store.labeled(since=time.time() + 1).empty
