from pathlib import Path

import pytest

MODELE = Path(__file__).resolve().parents[1] / "models" / "sentiment.joblib"
pytestmark = pytest.mark.skipif(not MODELE.exists(), reason="modèle non produit : python src/train.py")


@pytest.fixture(scope="module")
def client():
    from fastapi.testclient import TestClient

    from api.main import app
    with TestClient(app) as c:  # le "with" déclenche lifespan (chargement du modèle)
        yield c


def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["docs"] == "/docs"


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "OK"
    assert "sentiment.joblib" in body["model"]


def test_predict_ok(client):
    r = client.post("/predict", json={"text": "Livraison rapide, produit conforme, très satisfait"})
    assert r.status_code == 200
    body = r.json()
    assert body["label"] in {"POSITIVE", "NEGATIVE", "INDETERMINE"}
    assert 0.0 <= body["score"] <= 1.0


def test_predict_texte_vide(client):
    assert client.post("/predict", json={"text": ""}).status_code == 422


def test_predict_texte_blanc(client):
    assert client.post("/predict", json={"text": "   "}).status_code == 422


def test_predict_champ_manquant(client):
    assert client.post("/predict", json={}).status_code == 422
