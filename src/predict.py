"""Interroge le modèle sérialisé : python src/predict.py "texte de l'avis"."""
import sys
from functools import lru_cache
from pathlib import Path
from typing import TypedDict

import joblib

MODELE = Path(__file__).resolve().parents[1] / "models" / "sentiment.joblib"


class Resultat(TypedDict):
    label: str
    score: float


@lru_cache(maxsize=1)
def charger_modele():
    """Chargé une seule fois par processus, pas à chaque appel (désérialisation)."""
    if not MODELE.exists():
        raise FileNotFoundError("models/sentiment.joblib absent : lancez python src/train.py")
    return joblib.load(MODELE)


def predict(texte: str) -> Resultat:
    """Renvoie {'label': 'positive'|'negative', 'score': float}."""
    if not isinstance(texte, str) or not texte.strip():
        raise ValueError("texte vide")
    pipeline = charger_modele()
    etiquette = pipeline.predict([texte])[0]
    score = float(pipeline.predict_proba([texte]).max())
    return {"label": str(etiquette), "score": round(score, 4)}


if __name__ == "__main__":
    r = predict(" ".join(sys.argv[1:]))
    print(f"{r['label']} (confiance {r['score']:.0%})")
