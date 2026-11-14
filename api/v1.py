"""Les routes de la version 1 de l'API, protégées par clé et par rôle."""
import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request

from api.model import SentimentClassifier
from api.schemas import ErreurV1, HealthResponse, PredictRequest, PredictResponse
from api.securite import exiger

logger = logging.getLogger("api")

ERREURS: dict[int | str, dict[str, Any]] = {code: {"model": ErreurV1} for code in (401, 403, 422, 500, 503)}

router = APIRouter(prefix="/v1", tags=["v1"], responses=ERREURS)


def classifier(request: Request) -> SentimentClassifier:
    clf: SentimentClassifier | None = getattr(request.app.state, "classifier", None)
    if clf is None:
        raise HTTPException(503, "Modèle non chargé")
    return clf


# Le classifier, injecté par FastAPI dans chaque route qui le demande
Classifier = Annotated[SentimentClassifier, Depends(classifier)]


@router.get("/health", response_model=HealthResponse, summary="Santé (public)")
def sante(clf: Classifier) -> dict[str, str]:
    return {"status": "OK", "model": clf.model_name}


@router.post("/predict", response_model=PredictResponse, summary="Classer un avis (client, admin)",
             dependencies=[Depends(exiger("client", "admin"))])
def predire(corps: PredictRequest, clf: Classifier) -> dict[str, Any]:
    try:
        resultat = clf.predict(corps.text)
    except Exception:
        logger.exception("Erreur lors de la prédiction")
        raise HTTPException(500, "Erreur interne du serveur") from None
    # on journalise le verdict, pas le texte : un avis peut contenir des données personnelles
    logger.info("v1 predict -> %s (%.2f)", resultat["label"], resultat["score"])
    return resultat


@router.get("/modele", summary="Seuil et métriques du modèle (admin)", response_model=None,
            dependencies=[Depends(exiger("admin"))])
def modele(clf: Classifier) -> dict[str, Any]:
    return {"model": clf.model_name, "seuil_abstention": clf.seuil, "metriques": clf.metriques()}
