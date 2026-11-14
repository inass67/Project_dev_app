"""Adapte la fonction predict() du TP 1 au contrat de l'API."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from predict import charger_modele, predict  # noqa: E402

model_name = "tfidf-logreg (models/sentiment.joblib)"


def classer(texte: str) -> dict:
    r = predict(texte)
    return {"label": r["label"].upper(), "score": round(r["score"], 3), "text": texte}


__all__ = ["charger_modele", "classer", "model_name"]
