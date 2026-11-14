"""Tests de la page Streamlit avec AppTest : exécution sans navigateur."""
from pathlib import Path

import httpx
import pytest
from streamlit.testing.v1 import AppTest

from ui import client

RACINE = Path(__file__).resolve().parents[1]
PAGE = str(RACINE / "ui" / "app.py")
MODELE = RACINE / "models" / "sentiment.joblib"
pytestmark = pytest.mark.skipif(not MODELE.exists(), reason="modèle non produit : python src/train.py")

CLE = "cle-interface-0123456789abcdef"


@pytest.fixture
def api(monkeypatch):
    from fastapi.testclient import TestClient

    from api.main import app
    monkeypatch.setenv("API_KEYS", f"{CLE}:client")
    with TestClient(app, headers={"X-API-Key": CLE}) as c:
        yield c


@pytest.fixture
def page(api, monkeypatch):
    monkeypatch.setattr(client, "creer_session", lambda: api)
    return AppTest.from_file(PAGE, default_timeout=30).run()


def analyser(page, texte):
    page.text_area[0].input(texte).run()
    page.button[0].click().run()
    return page


def test_page_annonce_api_prete(page):
    assert "API prête" in page.caption[0].value


def test_avis_positif(page):
    resultat = analyser(page, "Livraison rapide, très satisfait")
    assert resultat.metric[0].label == "Avis positif"


def test_texte_inconnu_je_ne_sais_pas(page):
    resultat = analyser(page, "xqzvb wlkptr grombu")
    assert resultat.metric[0].label.startswith("Je ne sais pas")
    assert "seuil d'abstention" in resultat.info[0].value


def test_texte_refuse_affiche_un_avertissement(page):
    resultat = analyser(page, "   ")
    assert resultat.warning[0].value == client.REFUS


def test_api_injoignable(monkeypatch):
    def handler(request):
        raise httpx.ConnectError("API arrêtée", request=request)

    session = httpx.Client(transport=httpx.MockTransport(handler), base_url="http://api.test")
    monkeypatch.setattr(client, "creer_session", lambda: session)
    page = AppTest.from_file(PAGE, default_timeout=30).run()
    assert any("API injoignable" in element.value for element in page.error)
