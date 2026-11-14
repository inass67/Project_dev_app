"""Le modèle de sentiment, devenu un paquet installable (TP6).

Le modèle n'est pas dans le paquet : son chemin vient de la variable d'environnement
SENTIMENT_MODELE, sinon de models/sentiment.joblib à côté du paquet (cas du dépôt).

Usage :
  >>> from sentiment_app.predict import predict ; predict("texte")
  >>> from sentiment_app.predict import classer ; classer("texte")   # étiquette du contrat
"""
import os
import sys
from functools import lru_cache
from pathlib import Path
from typing import Literal, TypedDict

import joblib

Label = Literal["POSITIVE", "NEGATIVE", "INDETERMINE"]

# Seuil d'abstention, choisi avec src/courbe_seuil.py sur le jeu de démonstration (58 avis de test) :
# à 0,60, le modèle répond à 42 avis (72 %), avec 2 erreurs au lieu de 7 ; les 16 autres vont à un humain.
SEUIL_ABSTENTION = 0.60
# Étiquettes du modèle -> étiquettes du contrat : une correspondance explicite, vérifiée au démarrage
CORRESPONDANCE: dict[str, Label] = {"positive": "POSITIVE", "negative": "NEGATIVE"}


def chemin_modele() -> Path:
    """SENTIMENT_MODELE si elle est définie, sinon models/sentiment.joblib à côté du paquet."""
    variable = os.environ.get("SENTIMENT_MODELE")
    if variable:
        return Path(variable)
    return Path(__file__).resolve().parents[1] / "models" / "sentiment.joblib"


MODELE = chemin_modele()


class Resultat(TypedDict):
    """Retour de predict() : un type précis, que mypy suit jusqu'au contrat de l'API (TP4)."""
    label: str
    score: float


class Verdict(TypedDict):
    """Retour de classer() : l'étiquette du contrat, seuil d'abstention appliqué."""
    label: Label
    score: float


@lru_cache(maxsize=1)
def charger_modele():
    """Chargé une seule fois par processus, pas à chaque appel."""
    if not MODELE.exists():
        raise FileNotFoundError(
            f"modèle introuvable : {MODELE} (lancez python src/train.py, "
            "ou indiquez son chemin dans SENTIMENT_MODELE)"
        )
    return joblib.load(MODELE)


def predict(texte: str) -> Resultat:
    """Renvoie {'label': 'positive'|'negative', 'score': float}."""
    if not isinstance(texte, str) or not texte.strip():
        raise ValueError("texte vide")
    pipeline = charger_modele()
    etiquette = pipeline.predict([texte])[0]
    score = float(pipeline.predict_proba([texte]).max())
    return {"label": str(etiquette), "score": round(score, 4)}


def classer(texte: str) -> Verdict:
    """L'étiquette du contrat : INDETERMINE quand la confiance est sous le seuil d'abstention."""
    r = predict(texte)
    label: Label = "INDETERMINE" if r["score"] < SEUIL_ABSTENTION else CORRESPONDANCE[r["label"]]
    return {"label": label, "score": r["score"]}


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    resultat = predict(" ".join(sys.argv[1:]))
    print(f"{resultat['label']} (confiance {resultat['score']:.0%})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
