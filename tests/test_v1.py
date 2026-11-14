"""Tests de l'API /v1 : clés, rôles, format d'erreur, CORS."""
from pathlib import Path

import pytest

from api.securite import charger_cles

MODELE = Path(__file__).resolve().parents[1] / "models" / "sentiment.joblib"
pytestmark = pytest.mark.skipif(not MODELE.exists(), reason="modèle non produit : python src/train.py")

CLE_CLIENT = "client-key-0123456789abcd"
CLE_ADMIN = "admin-key-0123456789abcdef"
AVIS = {"text": "Livraison rapide, produit conforme, très satisfait"}


@pytest.fixture
def client(monkeypatch):
    """Chaque test déclare ses propres clés : il ne dépend pas de votre .env."""
    monkeypatch.setenv("API_KEYS", f"{CLE_CLIENT}:client,{CLE_ADMIN}:admin")
    from fastapi.testclient import TestClient

    from api.main import app
    with TestClient(app) as c:
        yield c


def en_tete(cle):
    return {"X-API-Key": cle}


def test_sans_cle_401(client):
    r = client.post("/v1/predict", json=AVIS)
    assert r.status_code == 401
    assert r.json()["erreur"]["code"] == "NON_AUTHENTIFIE"


def test_cle_inconnue_401(client):
    r = client.post("/v1/predict", json=AVIS, headers=en_tete("cle-inconnue-0123456789"))
    assert r.status_code == 401
    assert r.json()["erreur"]["code"] == "NON_AUTHENTIFIE"


def test_client_peut_predire(client):
    r = client.post("/v1/predict", json=AVIS, headers=en_tete(CLE_CLIENT))
    assert r.status_code == 200
    assert r.json()["label"] in {"POSITIVE", "NEGATIVE", "INDETERMINE"}


def test_texte_blanc_422_avec_champ(client):
    r = client.post("/v1/predict", json={"text": "   "}, headers=en_tete(CLE_CLIENT))
    assert r.status_code == 422
    erreur = r.json()["erreur"]
    assert erreur["code"] == "ENTREE_INVALIDE"
    assert erreur["champs"][0]["champ"] == "body.text"


def test_client_refuse_sur_route_admin(client):
    r = client.get("/v1/modele", headers=en_tete(CLE_CLIENT))
    assert r.status_code == 403
    assert r.json()["erreur"]["code"] == "ACCES_REFUSE"


def test_admin_voit_le_modele(client):
    r = client.get("/v1/modele", headers=en_tete(CLE_ADMIN))
    assert r.status_code == 200
    assert r.json()["seuil_abstention"] == 0.6


def test_v1_health_public(client):
    assert client.get("/v1/health").status_code == 200


def test_ancienne_route_annonce_sa_depreciation(client):
    r = client.post("/predict", json=AVIS)
    assert r.status_code == 200
    assert r.headers["deprecation"] == "true"
    assert "successor-version" in r.headers["link"]


def test_cors_autorise_la_page_web(client):
    r = client.options("/v1/predict", headers={
        "Origin": "http://localhost:5500",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "x-api-key,content-type"})
    assert r.status_code == 200
    assert r.headers["access-control-allow-origin"] == "http://localhost:5500"


def test_cors_refuse_une_autre_origine(client):
    r = client.options("/v1/predict", headers={
        "Origin": "http://localhost:5600", "Access-Control-Request-Method": "POST"})
    assert r.status_code == 400


def test_cle_trop_courte_refusee():
    with pytest.raises(ValueError, match="trop courte"):
        charger_cles("abc:client")


def test_role_inconnu_refuse():
    with pytest.raises(ValueError, match="rôle inconnu"):
        charger_cles("une-cle-assez-longue-0123456:superuser")


def test_sans_cle_configuree_personne_nentre(monkeypatch):
    monkeypatch.setenv("API_KEYS", "")
    assert charger_cles() == {}