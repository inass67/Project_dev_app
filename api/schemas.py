"""Contrat de l'API : formes des requêtes, des réponses et des erreurs."""
from typing import Literal

from pydantic import BaseModel, Field, field_validator

Label = Literal["POSITIVE", "NEGATIVE", "INDETERMINE"]


class PredictRequest(BaseModel):
    """Requête de prédiction."""
    text: str = Field(..., min_length=1, max_length=2000, description="Texte à classifier",
                      examples=["Livraison rapide, produit conforme, très satisfait"])

    @field_validator("text")
    @classmethod
    def refuser_texte_blanc(cls, valeur: str) -> str:
        """Même règle que predict() de src/predict.py : un texte vide une fois ses blancs retirés est refusé."""
        if not valeur.strip():
            raise ValueError("texte vide une fois les blancs retirés")
        return valeur


class PredictResponse(BaseModel):
    label: Label
    score: float = Field(..., ge=0, le=1)
    text: str


class HealthResponse(BaseModel):
    status: str
    model: str


class ChampInvalide(BaseModel):
    champ: str
    message: str


class DetailErreur(BaseModel):
    code: str = Field(..., description="Code stable, à tester côté client : ENTREE_INVALIDE, NON_AUTHENTIFIE...")
    message: str = Field(..., description="Message lisible, susceptible de changer")
    champs: list[ChampInvalide] = Field(default_factory=list)


class ErreurV1(BaseModel):
    """Format unique de toutes les erreurs de /v1."""
    erreur: DetailErreur


# Compatibilité avec le TP 1
AvisEntree = PredictRequest
Prediction = PredictResponse
Sante = HealthResponse
