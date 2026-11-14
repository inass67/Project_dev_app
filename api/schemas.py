"""Contrats d'entrée et de sortie de l'API (Pydantic v2)."""
from typing import Literal

from pydantic import BaseModel, Field, field_validator

# Les trois étiquettes du contrat : INDETERMINE quand la confiance est sous le seuil d'abstention (TP4)
Label = Literal["POSITIVE", "NEGATIVE", "INDETERMINE"]


class PredictRequest(BaseModel):
    """Requête de prédiction."""
    text: str = Field(..., min_length=1, max_length=2000, description="Texte à classifier",
                      examples=["Livraison rapide, produit conforme, très satisfait"])

    @field_validator("text")
    @classmethod
    def texte_non_blanc(cls, valeur: str) -> str:
        """Même règle que predict() du TP2 (str.strip()) : un texte fait de blancs est vide.

        Refusé ici, le texte reçoit le 422 standard de FastAPI (detail en liste),
        au lieu d'un 422 de forme différente produit par api/main.py.
        """
        if not valeur.strip():
            raise ValueError("texte vide une fois les blancs retirés")
        return valeur


class PredictResponse(BaseModel):
    """Réponse de prédiction."""
    label: Label = Field(..., description="POSITIVE, NEGATIVE, ou INDETERMINE si la confiance "
                                          "est sous le seuil d'abstention (avis à faire vérifier)")
    score: float = Field(..., ge=0, le=1, description="Confiance de la classe prédite")
    text: str = Field(..., description="Aperçu du texte analysé (100 caractères)")


class HealthResponse(BaseModel):
    """Réponse de l'endpoint de santé."""
    status: str = Field(..., description="OK si le modèle est chargé")
    model: str = Field(..., description="Nom du modèle servi")


class ErrorResponse(BaseModel):
    """Format standard des erreurs FastAPI."""
    detail: str
