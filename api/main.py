"""Application FastAPI : GET /health et POST /predict."""
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from api.model import Prediction, SentimentClassifier, load_model
from api.schemas import HealthResponse, PredictRequest, PredictResponse

logger = logging.getLogger("api")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Charge le modèle une seule fois, avant la première requête."""
    logger.info("Démarrage de l'API...")
    app.state.classifier = load_model()
    logger.info("Modèle chargé : %s", app.state.classifier.model_name)
    yield
    logger.info("Arrêt de l'API")


app = FastAPI(
    title="Sentiment Analysis API",
    description="Classifie le sentiment d'un avis en français.",
    version="1.0.0",
    lifespan=lifespan,
)


def _classifier() -> SentimentClassifier:
    clf: SentimentClassifier | None = getattr(app.state, "classifier", None)
    if clf is None:
        raise HTTPException(status_code=503, detail="Modèle non chargé")
    return clf


@app.get("/")
async def racine() -> dict[str, str]:
    return {"service": "Sentiment Analysis API", "docs": "/docs"}


@app.get("/health", response_model=HealthResponse, summary="Santé de l'API")
async def health_check() -> dict[str, str]:
    return {"status": "OK", "model": _classifier().model_name}


@app.post("/predict", response_model=PredictResponse, summary="Classifier un texte")
async def predict(request: PredictRequest) -> Prediction:
    clf = _classifier()
    try:
        result = clf.predict(request.text)
    except Exception:
        logger.exception("Erreur lors de la prédiction")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur") from None
    logger.info("predict: %r -> %s (%.2f)", request.text[:50], result["label"], result["score"])
    return result