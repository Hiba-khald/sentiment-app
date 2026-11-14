"""L'application FastAPI (version TP 2) : routes /v1 protégées, format d'erreur unique, CORS."""
import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from api import v1
from api.model import Prediction, SentimentClassifier, load_model
from api.schemas import HealthResponse, PredictRequest, PredictResponse
from api.securite import charger_cles

try:  # .env est facultatif : sans python-dotenv, on lit les variables déjà définies
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
except ImportError:  # pragma: no cover
    pass

logger = logging.getLogger("sentiment-api")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Charge le modèle une seule fois, avant la première requête."""
    logger.info("Démarrage de l'API...")
    nb_cles = len(charger_cles())  # une API_KEYS mal formée arrête le démarrage ici, pas à la 1re requête
    if nb_cles == 0:
        logger.warning("Aucune clé dans API_KEYS : les routes /v1 protégées répondront 401")
    app.state.classifier = load_model()
    logger.info("Modèle chargé : %s ; %d clé(s) d'API", app.state.classifier.model_name, nb_cles)
    yield
    logger.info("Arrêt de l'API")


app = FastAPI(
    title="Sentiment Analysis API",
    description="Classifie le sentiment d'un avis en français. Utilisez les routes /v1, avec une clé d'API.",
    version="1.2.0",
    lifespan=lifespan,
)

ORIGINES = [o.strip() for o in os.environ.get(
    "CORS_ORIGINS", "http://localhost:5500,http://127.0.0.1:5500").split(",") if o.strip()]
app.add_middleware(CORSMiddleware, allow_origins=ORIGINES, allow_methods=["GET", "POST"],
                   allow_headers=["Content-Type", "X-API-Key"])
app.include_router(v1.router)

CODES = {400: "REQUETE_INVALIDE", 401: "NON_AUTHENTIFIE", 403: "ACCES_REFUSE", 404: "INTROUVABLE",
         405: "METHODE_NON_AUTORISEE", 422: "ENTREE_INVALIDE", 500: "ERREUR_INTERNE",
         503: "MODELE_INDISPONIBLE"}


def _erreur_v1(statut: int, message: str, champs: list[dict] | None = None,
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


def _classifier() -> SentimentClassifier:
    clf: SentimentClassifier | None = getattr(app.state, "classifier", None)
    if clf is None:
        raise HTTPException(status_code=503, detail="Modèle non chargé")
    return clf


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Sentiment Analysis API", "docs": "/docs"}


@app.get("/health", response_model=HealthResponse, summary="Santé de l'API")
async def health_check() -> dict[str, str]:
    """Répond 200 si le modèle est chargé, 503 sinon. Reste public."""
    return {"status": "OK", "model": _classifier().model_name}


@app.post("/predict", response_model=PredictResponse, summary="Classifier un texte (dépréciée)",
          deprecated=True)
async def predict(request: PredictRequest, response: Response) -> Prediction:
    """Dépréciée : utilisez POST /v1/predict. Conservée pour ne pas casser les clients existants."""
    response.headers["Deprecation"] = "true"
    response.headers["Link"] = '</v1/predict>; rel="successor-version"'
    clf = _classifier()
    try:
        result = clf.predict(request.text)
    except Exception:
        logger.exception("Erreur lors de la prédiction")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur") from None
    logger.info("predict: %r -> %s (%.2f)", request.text[:50], result["label"], result["score"])
    return result
