"""Tests du client HTTP de l'interface : réponses, codes d'erreur, résumé."""
import json

import httpx
import pytest

from ui import client


def session_avec(handler) -> httpx.Client:
    return httpx.Client(transport=httpx.MockTransport(handler), base_url="http://api.test")


def test_creer_session_envoie_url_et_cle(monkeypatch):
    monkeypatch.setattr(client, "API_URL", "http://api.test")
    monkeypatch.setattr(client, "API_KEY", "cle-test")
    session = client.creer_session()
    try:
        assert str(session.base_url).rstrip("/") == "http://api.test"
        assert session.headers["X-API-Key"] == "cle-test"
    finally:
        session.close()


def test_sante_ok():
    session = session_avec(lambda request: httpx.Response(200, json={"status": "OK", "model": "modele-test"}))
    reponse = client.sante(session)
    assert reponse.ok is True
    assert reponse.message == "modele-test"


def test_sante_api_injoignable():
    def handler(request):
        raise httpx.ConnectError("API arrêtée", request=request)

    reponse = client.sante(session_avec(handler))
    assert reponse.ok is False
    assert reponse.message == client.INJOIGNABLE


def test_predire_ok():
    session = session_avec(lambda request: httpx.Response(
        200, json={"label": "POSITIVE", "score": 0.78, "text": "bien"}))
    reponse = client.predire(session, "bien")
    assert reponse.ok is True
    assert reponse.label == "POSITIVE"
    assert reponse.score == 0.78


def test_predire_entree_invalide():
    session = session_avec(lambda request: httpx.Response(
        422, json={"erreur": {"code": "ENTREE_INVALIDE", "message": "peu importe", "champs": []}}))
    reponse = client.predire(session, " ")
    assert reponse.ok is False
    assert reponse.message == client.REFUS


def test_predire_modele_indisponible():
    session = session_avec(lambda request: httpx.Response(
        503, json={"erreur": {"code": "MODELE_INDISPONIBLE", "message": "peu importe", "champs": []}}))
    reponse = client.predire(session, "bien")
    assert reponse.ok is False
    assert reponse.message == client.SANS_MODELE


def test_predire_cle_absente_ou_refusee():
    for statut, code in ((401, "NON_AUTHENTIFIE"), (403, "ACCES_REFUSE")):
        session = session_avec(lambda request, statut=statut, code=code: httpx.Response(
            statut, json={"erreur": {"code": code, "message": "peu importe", "champs": []}}))
        reponse = client.predire(session, "bien")
        assert reponse.ok is False
        assert reponse.message == client.CLE


def test_predire_erreur_inconnue():
    session = session_avec(lambda request: httpx.Response(
        500, json={"erreur": {"code": "THEIERE", "message": "peu importe", "champs": []}}))
    reponse = client.predire(session, "bien")
    assert reponse.ok is False
    assert reponse.message == "Erreur interne de l'API (500)."


def test_predire_lot_et_resumer():
    def handler(request):
        texte = json.loads(request.content)["text"]
        if texte == " ":
            return httpx.Response(422, json={"erreur": {"code": "ENTREE_INVALIDE", "message": "", "champs": []}})
        label = "POSITIVE" if texte == "bon" else "NEGATIVE" if texte == "mauvais" else "INDETERMINE"
        return httpx.Response(200, json={"label": label, "score": 0.5, "text": texte})

    reponses = client.predire_lot(session_avec(handler), ["bon", "mauvais", " ", "bof"])
    resume = client.resumer(reponses)
    assert resume["POSITIVE"] == 1
    assert resume["NEGATIVE"] == 1
    assert resume["INDETERMINE"] == 1
    assert resume["REFUS OU ERREUR"] == 1
