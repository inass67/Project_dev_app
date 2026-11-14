"""Tout ce que l'interface sait de l'API /v1 : routes, clé, codes d'erreur."""
import os
from collections import Counter
from dataclasses import dataclass

import httpx

try:
    from dotenv import load_dotenv

    load_dotenv()  # Streamlit ne lit pas .env de lui-même
except ImportError:  # pragma: no cover
    pass

API_URL = os.environ.get("API_URL", "http://127.0.0.1:8000")
API_KEY = os.environ.get("API_KEY", "")

INJOIGNABLE = "API injoignable : lancez d'abord uvicorn api.main:app"
REFUS = "Avis refusé par l'API : saisissez un texte non vide (2000 caractères au plus)."
SANS_MODELE = "Le modèle n'est pas chargé côté API : lancez python src/train.py, puis relancez l'API."
CLE = "Clé d'API absente ou refusée : vérifiez API_KEY dans le fichier .env."
VERDICTS = {"POSITIVE": "Avis positif", "NEGATIVE": "Avis négatif",
            "INDETERMINE": "Je ne sais pas : à vérifier"}


@dataclass
class Reponse:
    """Ce que l'interface affiche : un verdict, ou un message d'erreur lisible."""

    ok: bool
    label: str | None = None
    score: float | None = None
    message: str = ""


def creer_session() -> httpx.Client:
    """La connexion à l'API. Les tests la remplacent par un client en mémoire."""
    return httpx.Client(base_url=API_URL, timeout=10, headers={"X-API-Key": API_KEY})


def _code(r: httpx.Response) -> str:
    """Le code stable d'une erreur /v1 (ENTREE_INVALIDE, NON_AUTHENTIFIE...), ou une chaîne vide."""
    try:
        return r.json()["erreur"]["code"]
    except (ValueError, KeyError, TypeError):
        return ""


def sante(session: httpx.Client) -> Reponse:
    try:
        r = session.get("/v1/health")
    except httpx.TransportError:
        return Reponse(False, message=INJOIGNABLE)
    if r.status_code == 200:
        return Reponse(True, message=r.json().get("model", ""))
    if _code(r) == "MODELE_INDISPONIBLE":
        return Reponse(False, message=SANS_MODELE)
    return Reponse(False, message=f"API en erreur ({r.status_code}).")


def predire(session: httpx.Client, texte: str) -> Reponse:
    try:
        r = session.post("/v1/predict", json={"text": texte})
    except httpx.TransportError:
        return Reponse(False, message=INJOIGNABLE)
    if r.status_code == 200:
        corps = r.json()
        return Reponse(True, label=corps["label"], score=corps["score"])
    code = _code(r)
    if code == "ENTREE_INVALIDE":
        return Reponse(False, message=REFUS)
    if code == "MODELE_INDISPONIBLE":
        return Reponse(False, message=SANS_MODELE)
    if code in ("NON_AUTHENTIFIE", "ACCES_REFUSE"):
        return Reponse(False, message=CLE)
    return Reponse(False, message=f"Erreur interne de l'API ({r.status_code}).")


def predire_lot(session: httpx.Client, textes: list[str]) -> list[Reponse]:
    return [predire(session, texte) for texte in textes]


def resumer(reponses: list[Reponse]) -> dict[str, int]:
    """Nombre d'avis par verdict ; les refus et les erreurs sont comptés à part."""
    compte = Counter(r.label if r.ok else "REFUS OU ERREUR" for r in reponses)
    return dict(sorted(compte.items()))
