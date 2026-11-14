"""Tests de l'API en mémoire (TestClient) : aucun serveur à lancer."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
pytest.importorskip("fastapi")

if not (Path(__file__).resolve().parents[1] / "models" / "sentiment.joblib").exists():
    pytest.skip("modèle absent : python src/train.py", allow_module_level=True)

from fastapi.testclient import TestClient  # noqa: E402

from api.main import app  # noqa: E402


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "OK"
    assert "sentiment.joblib" in r.json()["model"]


def test_predict_positif(client):
    r = client.post("/predict", json={"text": "Livraison rapide, produit conforme, très satisfait"})
    assert r.status_code == 200
    assert r.json()["label"] == "POSITIVE"


def test_predict_negatif(client):
    r = client.post("/predict", json={"text": "Produit défectueux, très déçu, à éviter"})
    assert r.json()["label"] == "NEGATIVE"


def test_texte_vide(client):
    assert client.post("/predict", json={"text": "   "}).status_code == 422


def test_champ_manquant(client):
    assert client.post("/predict", json={}).status_code == 422


def test_score_entre_0_et_1(client):
    s = client.post("/predict", json={"text": "bon produit"}).json()["score"]
    assert 0 <= s <= 1
