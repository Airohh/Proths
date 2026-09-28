import mlflow
import pandas as pd
import pytest

from src import data, registry
from src.retraining.retrain import build_training_set
from src.training.train import decide_promotion, main, train_and_register


def test_decide_promotion():
    assert decide_promotion(None, 0.5, 0.01)[0]
    assert decide_promotion(0.80, 0.82, 0.01)[0]
    assert not decide_promotion(0.80, 0.805, 0.01)[0]
    assert not decide_promotion(0.80, 0.70, 0.01)[0]


def test_first_model_becomes_champion_then_equal_model_is_rejected(workspace):
    client = registry.setup_mlflow()
    train, holdout = data.load("train"), data.load("holdout")

    first = train_and_register(train, holdout, client=client, min_improvement=0.002)
    assert first.promoted and first.champion is None
    assert registry.champion_version(client) == first.version

    # Même données, même graine : aucun gain -> rejeté, le champion ne bouge pas.
    second = train_and_register(train, holdout, client=client, min_improvement=0.002)
    assert not second.promoted
    assert second.champion["f1_macro"] == first.candidate["f1_macro"]
    assert registry.champion_version(client) == first.version

    run = mlflow.get_run(second.run_id)
    assert run.data.tags["decision"] == "rejected"
    assert "champion_holdout_f1_macro" in run.data.metrics


def test_loaded_champion_carries_its_reference_profile(workspace):
    client = registry.setup_mlflow()
    train_and_register(data.load("train"), data.load("holdout"), client=client)
    champion = registry.load_champion(client)
    assert sorted(champion.profile["classes"]) == ["Business", "Sci/Tech", "Sports", "World"]
    assert sum(champion.profile["class_distribution"].values()) == pytest.approx(1.0)
    assert champion.holdout["f1_macro"] > 0.5


def test_cli_quality_gate(workspace):
    assert main(["--min-f1", "0.5", "--metrics-out", "m.json"]) == 0
    assert main(["--min-f1", "1.01", "--metrics-out", "m.json"]) == 1


def test_retrain_set_uses_true_labels_not_predictions():
    base = pd.DataFrame({"text": ["x", "y"], "label": ["World", "Sports"]})
    feedback = pd.DataFrame(
        {
            "text": ["y", "z"],
            "predicted": ["World", "World"],
            "true_label": ["Business", "Sci/Tech"],
        }
    )
    merged = build_training_set(base, feedback).set_index("text")["label"].to_dict()
    assert merged == {"x": "World", "y": "Business", "z": "Sci/Tech"}
