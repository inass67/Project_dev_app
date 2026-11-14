"""API FastAPI : /v1 protégée (TP 2) et anciennes routes du TP 1, dépréciées."""
import logging
import os
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request, Response
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

try:
    from dotenv import load_dotenv

    load_dotenv()  # lit .env à la racine : API_KEYS, CORS_ORIGINS...
except ImportError:  # pragma: no cover
    pass

from api import v1  # noqa: E402
from api.model import SentimentClassifier, model_name  # noqa: E402
from api.schemas import HealthResponse, PredictRequest, PredictResponse  # noqa: E402
from api.securite import charger_cles  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Démarrage de l'API...")
    cles = charger_cles()  # ValueError si API_KEYS est mal formée : l'API refuse de démarrer
    app.state.classifier = SentimentClassifier()
    log.info("Modèle chargé : %s ; %d clé(s) d'API", model_name, len(cles))
    if not cles:
        log.warning("Aucune clé dans API_KEYS : les routes /v1 protégées refuseront tous les appels")
    yield


app = FastAPI(title="sentiment-app", version="2.0.0", lifespan=lifespan)

ORIGINES = [o.strip() for o in os.environ.get(
    "CORS_ORIGINS", "http://localhost:5500,http://127.0.0.1:5500").split(",") if o.strip()]
app.add_middleware(CORSMiddleware, allow_origins=ORIGINES, allow_methods=["GET", "POST"],
                   allow_headers=["Content-Type", "X-API-Key"])

app.include_router(v1.router)


# --- Anciennes routes du TP 1 : conservées, mais dépréciées -------------------------------
@app.get("/health", response_model=HealthResponse, deprecated=True)
def health() -> dict[str, str]:
    return {"status": "OK", "model": model_name}


@app.post("/predict", response_model=PredictResponse, deprecated=True)
def predict_ancien(corps: PredictRequest, request: Request, response: Response) -> dict[str, Any]:
    response.headers["Deprecation"] = "true"
    response.headers["Link"] = '</v1/predict>; rel="successor-version"'
    clf: SentimentClassifier = request.app.state.classifier
    return clf.predict_sans_abstention(corps.text)


# --- Format d'erreur unique sous /v1 --------------------------------------------------------
CODES = {400: "REQUETE_INVALIDE", 401: "NON_AUTHENTIFIE", 403: "ACCES_REFUSE", 404: "INTROUVABLE",
         405: "METHODE_NON_AUTORISEE", 422: "ENTREE_INVALIDE", 500: "ERREUR_INTERNE",
         503: "MODELE_INDISPONIBLE"}


def _erreur_v1(statut: int, message: str, champs: list[dict[str, str]] | None = None,
               en_tetes: dict[str, str] | None = None) -> JSONResponse:
    corps = {"erreur": {"code": CODES.get(statut, f"HTTP_{statut}"), "message": message,
                        "champs": champs or []}}
    return JSONResponse(corps, status_code=statut, headers=en_tetes)


@app.exception_handler(StarletteHTTPException)
async def erreur_http(request: Request, exc: StarletteHTTPException) -> Response:
    """Sous /v1, le format unique ; ailleurs, le format d'origine de FastAPI, inchangé."""
    if request.url.path.startswith("/v1"):
        return _erreur_v1(exc.status_code, str(exc.detail), en_tetes=getattr(exc, "headers", None))
    return await http_exception_handler(request, exc)


@app.exception_handler(RequestValidationError)
async def erreur_validation(request: Request, exc: RequestValidationError) -> Response:
    if request.url.path.startswith("/v1"):
        champs = [{"champ": ".".join(str(x) for x in e["loc"]), "message": e["msg"]} for e in exc.errors()]
        return _erreur_v1(422, "Entrée refusée par le contrat de l'API", champs)
    return await request_validation_exception_handler(request, exc)
