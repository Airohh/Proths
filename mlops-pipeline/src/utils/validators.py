"""
Validateurs de données pour le pipeline MLOps
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional
import re


class DocumentInput(BaseModel):
    """Schéma de validation pour un document d'entrée"""
    text: str = Field(..., min_length=1, max_length=100000, description="Texte du document")
    
    @validator('text')
    def validate_text(cls, v):
        """Valide que le texte n'est pas vide après nettoyage"""
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Le texte ne peut pas être vide")
        return cleaned
    
    class Config:
        schema_extra = {
            "example": {
                "text": "This is a sample document about artificial intelligence and machine learning."
            }
        }


class BatchDocumentInput(BaseModel):
    """Schéma de validation pour un batch de documents"""
    texts: List[str] = Field(..., min_items=1, max_items=100, description="Liste de textes")
    
    @validator('texts')
    def validate_texts(cls, v):
        """Valide chaque texte dans la liste"""
        if not v:
            raise ValueError("La liste de textes ne peut pas être vide")
        
        validated_texts = []
        for text in v:
            if not isinstance(text, str):
                raise ValueError("Tous les éléments doivent être des chaînes de caractères")
            cleaned = text.strip()
            if not cleaned:
                raise ValueError("Aucun texte ne peut être vide")
            if len(cleaned) > 100000:
                raise ValueError("Chaque texte ne peut pas dépasser 100000 caractères")
            validated_texts.append(cleaned)
        
        return validated_texts
    
    class Config:
        schema_extra = {
            "example": {
                "texts": [
                    "Document about technology",
                    "Document about science"
                ]
            }
        }


class PredictionResponse(BaseModel):
    """Schéma de réponse pour une prédiction"""
    prediction: str = Field(..., description="Classe prédite")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confiance de la prédiction")
    probabilities: dict = Field(..., description="Probabilités pour toutes les classes")
    
    class Config:
        schema_extra = {
            "example": {
                "prediction": "technology",
                "confidence": 0.95,
                "probabilities": {
                    "technology": 0.95,
                    "science": 0.03,
                    "sports": 0.01,
                    "business": 0.01
                }
            }
        }


class BatchPredictionResponse(BaseModel):
    """Schéma de réponse pour un batch de prédictions"""
    predictions: List[PredictionResponse] = Field(..., description="Liste des prédictions")
    total: int = Field(..., description="Nombre total de prédictions")
    
    class Config:
        schema_extra = {
            "example": {
                "predictions": [
                    {
                        "prediction": "technology",
                        "confidence": 0.95,
                        "probabilities": {"technology": 0.95, "science": 0.05}
                    }
                ],
                "total": 1
            }
        }

