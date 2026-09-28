"""Un seul objet sklearn du texte brut à la classe prédite.

Nettoyage, TF-IDF et classifieur vivent dans le même `Pipeline`, loggé comme un
seul artefact MLflow. Conséquences :
- pas de train/serve skew : l'API appelle `pipeline.predict(texte_brut)`, exactement
  comme l'entraînement ;
- pas de vectorizer orphelin : un modèle et son vocabulaire sont versionnés ensemble ;
- pas de LabelEncoder : les classifieurs sklearn acceptent des labels texte.
"""

import re
from collections.abc import Iterable

from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.naive_bayes import ComplementNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
from sklearn.svm import LinearSVC

MODEL_TYPES = ("logreg", "linear_svc", "naive_bayes", "random_forest")

_ENTITY = re.compile(r"&?#\d+;|&\w+;")  # artefacts HTML d'AG News (#36; = $, &lt; ...)
_NON_WORD = re.compile(r"[^\w\s]")


def clean_texts(texts: Iterable[str]) -> list[str]:
    """Minuscules, sans entités HTML ni ponctuation. Fonction de module : picklable."""
    cleaned = []
    for text in texts:
        text = str(text).replace("\\", " ")
        text = _ENTITY.sub(" ", text)
        cleaned.append(_NON_WORD.sub(" ", text).lower())
    return cleaned


def _classifier(model_type: str, seed: int):
    if model_type == "logreg":
        # Régression logistique optimisée par SGD : mêmes probabilités qu'une LR,
        # ~10x plus rapide que lbfgs sur 120k documents x 200k n-grammes.
        return SGDClassifier(loss="log_loss", alpha=2e-6, max_iter=30, tol=1e-4, random_state=seed)
    if model_type == "linear_svc":
        # LinearSVC n'a pas de predict_proba : calibration par validation croisée.
        return CalibratedClassifierCV(LinearSVC(C=0.5, dual=True, random_state=seed), cv=3)
    if model_type == "naive_bayes":
        return ComplementNB(alpha=0.3)
    if model_type == "random_forest":
        # Ancienne baseline du projet, gardée pour la comparaison.
        return RandomForestClassifier(n_estimators=100, max_depth=10, n_jobs=-1, random_state=seed)
    raise ValueError(f"model_type inconnu : {model_type} (attendu : {', '.join(MODEL_TYPES)})")


def build_pipeline(model_type: str = "logreg", seed: int = 42) -> Pipeline:
    return Pipeline(
        [
            ("clean", FunctionTransformer(clean_texts)),
            (
                "tfidf",
                TfidfVectorizer(
                    ngram_range=(1, 2),
                    min_df=2,
                    max_df=0.95,
                    sublinear_tf=True,
                    max_features=200_000,
                ),
            ),
            ("clf", _classifier(model_type, seed)),
        ]
    )
