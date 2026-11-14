"""Contrat de l'API : formes des requêtes et des réponses."""
from pydantic import BaseModel, Field


class AvisEntree(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000, description="L'avis à classer")


class Prediction(BaseModel):
    label: str
    score: float
    text: str


class Sante(BaseModel):
    status: str
    model: str
