"""Tests de l'API /v1 : clés, rôles, format d'erreur, CORS. Ils déclarent leurs propres clés."""
from pathlib import Path

import pytest

from api.securite import charger_cles

MODELE = Path(__file__).resolve().parents[1] / "models" / "sentiment.joblib"
pytestmark = pytest.mark.skipif(not MODELE.exists(), reason="modèle non produit : python src/train.py")

CLE_CLIENT = "client-key-0123456789abcdef"
CLE_ADMIN = "admin-key-0123456789abcdefgh"
TEXTE = "Livraison rapide, produit conforme, très satisfait"


@pytest.fixture(scope="module")
def client():
    from fastapi.testclient import TestClient

    from api.main import app
    mp = pytest.MonkeyPatch()
    mp.setenv("API_KEYS", f"{CLE_CLIENT}:client,{CLE_ADMIN}:admin")
    with TestClient(app) as c:
        yield c
    mp.undo()


def _post(client, texte=TEXTE, cle=CLE_CLIENT):
    en_tetes = {"X-API-Key": cle} if cle else {}
    return client.post("/v1/predict", json={"text": texte}, headers=en_tetes)


def test_health_public(client):
    r = client.get("/v1/health")
    assert r.status_code == 200 and r.json()["status"] == "OK"


def test_predict_sans_cle_401(client):
    r = _post(client, cle=None)
    assert r.status_code == 401
    assert r.json()["erreur"]["code"] == "NON_AUTHENTIFIE"


def test_predict_cle_inconnue_401(client):
    r = _post(client, cle="x" * 20)
    assert r.status_code == 401
    assert r.json()["erreur"]["code"] == "NON_AUTHENTIFIE"


def test_predict_cle_client_ok(client):
    r = _post(client)
    assert r.status_code == 200
    assert r.json()["label"] in {"POSITIVE", "NEGATIVE", "INDETERMINE"}


def test_predict_cle_admin_ok(client):
    assert _post(client, cle=CLE_ADMIN).status_code == 200


def test_predict_texte_blanc_422(client):
    r = _post(client, texte="   ")
    assert r.status_code == 422
    erreur = r.json()["erreur"]
    assert erreur["code"] == "ENTREE_INVALIDE"
    assert erreur["champs"][0]["champ"] == "body.text"


def test_predict_texte_vide_422(client):
    assert _post(client, texte="").status_code == 422


def test_modele_client_403(client):
    r = client.get("/v1/modele", headers={"X-API-Key": CLE_CLIENT})
    assert r.status_code == 403
    assert r.json()["erreur"]["code"] == "ACCES_REFUSE"


def test_modele_admin_ok(client):
    r = client.get("/v1/modele", headers={"X-API-Key": CLE_ADMIN})
    assert r.status_code == 200
    assert r.json()["seuil_abstention"] == 0.6


def test_route_v1_inconnue_format_unique(client):
    r = client.get("/v1/nimporte-quoi")
    assert r.status_code == 404
    assert r.json()["erreur"]["code"] == "INTROUVABLE"


def test_ancienne_route_deprecated(client):
    r = client.post("/predict", json={"text": TEXTE})
    assert r.status_code == 200
    assert r.headers["deprecation"] == "true"
    assert "/v1/predict" in r.headers["link"]


def test_cors_origine_autorisee(client):
    r = client.options("/v1/predict", headers={
        "Origin": "http://localhost:5500", "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type,x-api-key"})
    assert r.status_code == 200
    assert r.headers["access-control-allow-origin"] == "http://localhost:5500"


def test_cors_origine_refusee(client):
    r = client.options("/v1/predict", headers={
        "Origin": "http://localhost:5600", "Access-Control-Request-Method": "POST"})
    assert r.status_code == 400


def test_charger_cles_valide():
    assert charger_cles(f"{CLE_CLIENT}:client, {CLE_ADMIN}:admin,") == {CLE_CLIENT: "client", CLE_ADMIN: "admin"}


def test_charger_cles_vide():
    assert charger_cles("") == {}


def test_charger_cles_role_inconnu():
    with pytest.raises(ValueError, match="rôle inconnu"):
        charger_cles(f"{CLE_CLIENT}:superuser")


def test_charger_cles_trop_courte_sans_fuite():
    with pytest.raises(ValueError) as e:
        charger_cles("court:client")
    assert "court" not in str(e.value).replace("trop courte", "")
