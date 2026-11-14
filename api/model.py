"""Adapte le modèle du TP 1 au contrat de l'API, avec un seuil d'abstention."""
import json
import sys
from pathlib import Path
from typing import Any

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))

from predict import charger_modele, predict  # noqa: E402

SEUIL_ABSTENTION = 0.6
model_name = "tfidf-logreg (models/sentiment.joblib)"


class SentimentClassifier:
    """Le modèle chargé une fois, et la règle d'abstention : sous le seuil, un humain tranche."""

    model_name = model_name

    def __init__(self, seuil: float = SEUIL_ABSTENTION) -> None:
        self.seuil = seuil
        charger_modele()  # FileNotFoundError si le joblib manque : l'API ne démarre pas sans modèle

    def predict_sans_abstention(self, texte: str) -> dict[str, Any]:
        r = predict(texte)
        return {"label": r["label"].upper(), "score": round(r["score"], 3), "text": texte}

    def predict(self, texte: str) -> dict[str, Any]:
        r = self.predict_sans_abstention(texte)
        if r["score"] < self.seuil:
            r["label"] = "INDETERMINE"
        return r

    def metriques(self) -> dict[str, Any]:
        chemin = RACINE / "models" / "metrics.json"
        return json.loads(chemin.read_text(encoding="utf-8")) if chemin.exists() else {}


def classer(texte: str) -> dict[str, Any]:
    """Compatibilité TP 1 : prédiction sans abstention."""
    r = predict(texte)
    return {"label": r["label"].upper(), "score": round(r["score"], 3), "text": texte}


__all__ = ["SentimentClassifier", "charger_modele", "classer", "model_name", "SEUIL_ABSTENTION"]
