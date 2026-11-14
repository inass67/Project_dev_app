"""Raccord entre l'API et le modèle entraîné au TP2.

L'API n'entraîne rien et ne connaît pas scikit-learn : elle appelle le paquet sentiment_app
(TP6), installé avec pip install -e ., qui charge le modèle une seule fois. Plus aucun
bricolage du chemin d'import : l'API importe le paquet comme n'importe quelle bibliothèque.
"""
from typing import TypedDict

from api.schemas import Label
from sentiment_app.predict import CORRESPONDANCE, SEUIL_ABSTENTION, charger_modele
from sentiment_app.predict import predict as _predict

__all__ = ["CORRESPONDANCE", "SEUIL_ABSTENTION", "SentimentClassifier", "load_model"]


class Prediction(TypedDict):
    label: Label
    score: float
    text: str


class SentimentClassifier:
    """Enveloppe du modèle TP2 avec l'interface attendue par l'API."""

    model_name = "tfidf-logreg (TP2, models/sentiment.joblib)"

    def __init__(self) -> None:
        modele = charger_modele()  # FileNotFoundError si le joblib manque : on ne démarre pas
        inconnues = {str(c) for c in modele.classes_} - set(CORRESPONDANCE)
        if inconnues:  # un modèle réentraîné sur d'autres étiquettes casserait le contrat
            raise ValueError(f"classes inconnues du contrat : {sorted(inconnues)}")

    def predict(self, text: str) -> Prediction:
        """Renvoie l'étiquette du contrat, ou INDETERMINE quand le modèle hésite."""
        r = _predict(text)
        label: Label = (
            "INDETERMINE" if r["score"] < SEUIL_ABSTENTION else CORRESPONDANCE[r["label"]]
        )
        return {"label": label, "score": r["score"], "text": text[:100]}


def load_model() -> SentimentClassifier:
    """Construit le classifier (le cache de chargement est dans sentiment_app/predict.py)."""
    return SentimentClassifier()
