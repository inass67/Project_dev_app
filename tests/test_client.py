"""TP 3 : le client de l'interface, testé avec une fausse API (httpx.MockTransport)."""
import sys
from pathlib import Path

import pytest

httpx = pytest.importorskip("httpx")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ui"))
import client  # noqa: E402


def session(statut=200, corps=None, erreur=None):
    def repondre(requete):
        if erreur:
            raise erreur
        return httpx.Response(statut, json=corps) if corps is not None else httpx.Response(statut, text="oups")
    return httpx.Client(base_url="http://api", transport=httpx.MockTransport(repondre))


def test_verdict():
    r = client.predire(session(200, {"label": "POSITIVE", "score": 0.9, "text": "x"}), "x")
    assert (r.ok, r.label, r.score) == (True, "POSITIVE", 0.9)


def test_entree_invalide():
    assert client.predire(session(422, {"erreur": {"code": "ENTREE_INVALIDE"}}), " ").message == client.REFUS


def test_sans_cle_message_explicite():
    r = client.predire(session(401, {"erreur": {"code": "NON_AUTHENTIFIE"}}), "x")
    assert not r.ok and r.message == client.CLE


def test_modele_indisponible():
    assert client.predire(session(503, {"erreur": {"code": "MODELE_INDISPONIBLE"}}), "x").message == client.SANS_MODELE


def test_api_injoignable():
    r = client.predire(session(erreur=httpx.ConnectError("refusé")), "x")
    assert r.message == client.INJOIGNABLE


def test_erreur_non_json():
    assert "500" in client.predire(session(500), "x").message


def test_sante():
    assert client.sante(session(200, {"status": "OK", "model": "m"})).message == "m"
    assert client.sante(session(erreur=httpx.ConnectError("x"))).message == client.INJOIGNABLE


def test_resumer_et_lot():
    s = session(200, {"label": "NEGATIVE", "score": 0.8, "text": "x"})
    reponses = client.predire_lot(s, ["a", "b"]) + [client.Reponse(False, message="x")]
    assert client.resumer(reponses) == {"NEGATIVE": 2, "REFUS OU ERREUR": 1}


def test_session_porte_la_cle(monkeypatch):
    monkeypatch.setattr(client, "API_KEY", "ma-cle")
    assert client.creer_session().headers["X-API-Key"] == "ma-cle"
