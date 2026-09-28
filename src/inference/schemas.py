"""Schémas d'entrée/sortie de l'API (Pydantic v2)."""

from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=20_000)]


class DocumentInput(BaseModel):
    text: Text = Field(..., examples=["Oil prices fall as OPEC signals higher output next quarter"])


class BatchDocumentInput(BaseModel):
    texts: list[Text] = Field(..., min_length=1, max_length=100)


class PredictionResponse(BaseModel):
    prediction_id: str = Field(..., description="à renvoyer dans POST /feedback")
    prediction: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    probabilities: dict[str, float]
    model_version: str


class BatchPredictionResponse(BaseModel):
    predictions: list[PredictionResponse]
    total: int


class FeedbackInput(BaseModel):
    prediction_id: str
    label: str = Field(..., examples=["Business"])


class FeedbackResponse(BaseModel):
    prediction_id: str
    correct: bool
