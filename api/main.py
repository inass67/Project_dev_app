"""API FastAPI : GET /health et POST /predict."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from api.model import charger_modele, classer, model_name
from api.schemas import AvisEntree, Prediction, Sante

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Démarrage de l'API...")
    charger_modele()  # FileNotFoundError si le joblib manque : on ne démarre pas sans modèle
    log.info("Modèle chargé : %s", model_name)
    yield


app = FastAPI(title="sentiment-app", version="1.0.0", lifespan=lifespan)


@app.get("/health", response_model=Sante)
def health() -> Sante:
    return Sante(status="OK", model=model_name)


@app.post("/predict", response_model=Prediction)
def predict(avis: AvisEntree) -> Prediction:
    if not avis.text.strip():
        raise HTTPException(status_code=422, detail="texte vide")
    return Prediction(**classer(avis.text))
