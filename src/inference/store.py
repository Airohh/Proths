"""Journal des prédictions et des labels de feedback (SQLite, mode WAL).

Une ligne par prédiction : texte, classe prédite, confiance, version du modèle.
Le vrai label arrive plus tard (`POST /feedback`) et complète la même ligne.
SQLite plutôt qu'un CSV : écritures atomiques, plusieurs processus (API, monitor)
peuvent lire et écrire le même fichier.
"""

import sqlite3
import time
import uuid
from contextlib import contextmanager
from pathlib import Path

import pandas as pd

from config import get_config

SCHEMA = """
CREATE TABLE IF NOT EXISTS predictions (
    id            TEXT PRIMARY KEY,
    ts            REAL NOT NULL,
    text          TEXT NOT NULL,
    predicted     TEXT NOT NULL,
    confidence    REAL NOT NULL,
    model_version TEXT NOT NULL,
    true_label    TEXT,
    feedback_ts   REAL
);
CREATE INDEX IF NOT EXISTS idx_predictions_ts ON predictions (ts);
CREATE INDEX IF NOT EXISTS idx_predictions_feedback ON predictions (feedback_ts);
"""


class PredictionStore:
    def __init__(self, path: str | Path | None = None):
        self.path = Path(path or get_config()["store"]["predictions_db"])
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.executescript(SCHEMA)

    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.path, timeout=30)
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def log(self, rows: list[dict], model_version: str) -> list[str]:
        """rows : [{text, predicted, confidence}] -> identifiants de prédiction."""
        now = time.time()
        ids = [uuid.uuid4().hex for _ in rows]
        with self._connect() as conn:
            conn.executemany(
                "INSERT INTO predictions (id, ts, text, predicted, confidence, model_version) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                [
                    (pid, now, r["text"], r["predicted"], r["confidence"], model_version)
                    for pid, r in zip(ids, rows, strict=True)
                ],
            )
        return ids

    def add_feedback(self, prediction_id: str, true_label: str) -> dict | None:
        """Enregistre le vrai label. Retourne la ligne mise à jour, None si id inconnu."""
        with self._connect() as conn:
            cur = conn.execute(
                "UPDATE predictions SET true_label = ?, feedback_ts = ? WHERE id = ?",
                (true_label, time.time(), prediction_id),
            )
            if cur.rowcount == 0:
                return None
            row = conn.execute(
                "SELECT predicted, true_label FROM predictions WHERE id = ?", (prediction_id,)
            ).fetchone()
        return {"predicted": row[0], "true_label": row[1]}

    def recent(self, limit: int, model_version: str | None = None) -> pd.DataFrame:
        """Les `limit` dernières prédictions (optionnellement d'une seule version)."""
        query = "SELECT * FROM predictions"
        params: tuple = ()
        if model_version is not None:
            query += " WHERE model_version = ?"
            params = (model_version,)
        query += " ORDER BY ts DESC, rowid DESC LIMIT ?"
        with self._connect() as conn:
            return pd.read_sql_query(query, conn, params=(*params, limit))

    def labeled(self, since: float | None = None) -> pd.DataFrame:
        """Prédictions ayant reçu un vrai label (après `since` si fourni)."""
        query = "SELECT * FROM predictions WHERE true_label IS NOT NULL"
        params: tuple = ()
        if since is not None:
            query += " AND feedback_ts > ?"
            params = (since,)
        with self._connect() as conn:
            return pd.read_sql_query(query + " ORDER BY feedback_ts", conn, params=params)
