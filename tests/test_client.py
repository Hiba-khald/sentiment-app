"""Tests du client de l'interface, branché sur l'API en mémoire."""
from pathlib import Path

import httpx
import pytest

from ui import client

MODELE = Path(__file__).resolve().parents[1] / "models" / "sentiment.joblib"
pytestmark = pytest.mark.skipif(not MODELE.exists(), reason="modèle non produit")

CLE_CLIENT = "client-key-0123456789abcd"


@pytest.fixture
def api(monkeypatch):
    monkeypatch.setenv("API_KEYS", f"{CLE_CLIENT}:client")
    from fastapi.testclient import TestClient

    from api.main import app
    with TestClient(app, headers={"X-API-Key": CLE_CLIENT}) as c:
        yield c


def test_sante_ok(api):
    etat = client.sante(api)
    assert etat.ok and "tfidf" in etat.message


def test_predire_positif(api):
    r = client.predire(api, "Livraison rapide, produit conforme, très satisfait")
    assert r.ok and r.label in {"POSITIVE", "NEGATIVE", "INDETERMINE"} and r.score is not None


def test_sans_cle_message_explicite(api):
    api.headers.pop("X-API-Key")
    r = client.predire(api, "bien")
    assert not r.ok and r.message == client.CLE


def test_texte_vide_refuse(api):
    r = client.predire(api, "   ")
    assert not r.ok and r.message == client.REFUS


def test_api_injoignable():
    def panne(request):
        raise httpx.ConnectError("refusé")
    session = httpx.Client(base_url="http://x", transport=httpx.MockTransport(panne))
    assert client.predire(session, "bien").message == client.INJOIGNABLE


def test_resumer_compte_les_verdicts():
    reponses = [client.Reponse(True, "POSITIVE", 0.9), client.Reponse(True, "POSITIVE", 0.8),
                client.Reponse(False, message="x")]
    assert client.resumer(reponses) == {"POSITIVE": 2, "REFUS OU ERREUR": 1}