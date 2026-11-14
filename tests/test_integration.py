"""Tests d'intégration : l'API telle qu'elle tourne vraiment (TP4, étape D).

Les tests du TP3 vérifient des réponses ; ceux-ci vérifient le démarrage de l'API
et son comportement quand le modèle manque ou tombe en panne.
Toute modification passe par monkeypatch, qui restaure l'état à la fin du test.
"""
from pathlib import Path

import pytest

MODELE = Path(__file__).resolve().parents[1] / "models" / "sentiment.joblib"
pytestmark = pytest.mark.skipif(not MODELE.exists(), reason="modèle non produit : python src/train.py")


@pytest.fixture
def app():
    from api.main import app

    return app


@pytest.fixture
def module_predict():
    """Le module du paquet (TP6) qui charge le modèle, tel que l'API l'utilise."""
    from sentiment_app import predict

    yield predict
    predict.charger_modele.cache_clear()  # les tests suivants rechargent le vrai modèle


def test_demarrage_reel_charge_le_modele():
    """D.1 : un client ouvert par « with » exécute le lifespan."""
    from fastapi.testclient import TestClient

    from api.main import app

    with TestClient(app) as client:
        reponse = client.get("/health")
    assert reponse.status_code == 200
    assert "TP2" in reponse.json()["model"]


def test_modele_absent_l_api_refuse_de_demarrer(app, module_predict, monkeypatch, tmp_path):
    """D.2 : le contrôle T20 du TP3, devenu automatique."""
    from fastapi.testclient import TestClient

    monkeypatch.setattr(module_predict, "MODELE", tmp_path / "absent.joblib")
    module_predict.charger_modele.cache_clear()  # sinon le modèle déjà en cache masque l'absence
    with pytest.raises(FileNotFoundError):
        with TestClient(app):
            pass


def test_classes_inattendues_l_api_refuse_de_demarrer(app, monkeypatch):
    """E.3 : un modèle dont une classe n'a pas de correspondance dans le contrat ne démarre pas."""
    from fastapi.testclient import TestClient

    import api.model

    monkeypatch.setattr(api.model, "CORRESPONDANCE", {"positive": "POSITIVE"})
    with pytest.raises(ValueError, match="classes inconnues"):
        with TestClient(app):
            pass


def test_modele_non_charge_503(app, monkeypatch):
    """D.3 : l'API démarrée, le modèle retiré de app.state : 503 sur /health et /predict."""
    from fastapi.testclient import TestClient

    with TestClient(app) as client:
        monkeypatch.setattr(app.state, "classifier", None)
        assert client.get("/health").status_code == 503
        assert client.post("/predict", json={"text": "Très bon produit"}).status_code == 503


@pytest.mark.parametrize("panne", [RuntimeError("bug interne"), ValueError("bug interne")],
                         ids=["RuntimeError", "ValueError"])
def test_modele_en_panne_500_sans_message_interne(app, monkeypatch, panne):
    """D.4 : quelle que soit l'exception du modèle, 500, et rien de son message côté client."""
    from fastapi.testclient import TestClient

    def predict_en_panne(text: str):
        raise panne

    with TestClient(app) as client:
        monkeypatch.setattr(app.state.classifier, "predict", predict_en_panne)
        reponse = client.post("/predict", json={"text": "Très bon produit"})
    assert reponse.status_code == 500
    assert "bug interne" not in reponse.text
