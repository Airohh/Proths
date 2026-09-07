from src.inference.prediction_log import LOG_PATH, log_predictions


def test_log_predictions_appends(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    log_predictions(
        [{"text": "nasdaq futures rise on bank earnings", "label": "Business", "confidence": 0.8}]
    )
    log_predictions(
        [{"text": "lakers win in overtime", "label": "Sports", "confidence": 0.9}]
    )
    assert LOG_PATH.exists()
    lines = LOG_PATH.read_text(encoding="utf-8").strip().splitlines()
    assert lines[0].startswith("text,label,confidence,timestamp")
    assert len(lines) == 3
