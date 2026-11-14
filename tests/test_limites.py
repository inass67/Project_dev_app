"""Tests aux limites du contrat d'entrée (TP4, étape B).

PredictRequest promet un champ « text », chaîne de 1 à 2000 caractères.
Ce fichier vérifie cette promesse à ses frontières, puis au hasard (hypothesis).
"""
import json
import sys
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

MODELE = Path(__file__).resolve().parents[1] / "models" / "sentiment.joblib"
pytestmark = pytest.mark.skipif(not MODELE.exists(), reason="modèle non produit : python src/train.py")

ETIQUETTES_DU_CONTRAT = {"POSITIVE", "NEGATIVE", "INDETERMINE"}
# Tous les caractères que str.strip() retire : la règle de predict() (TP2) et du schéma (TP4)
BLANCS = [chr(i) for i in range(sys.maxunicode + 1) if chr(i).isspace()]


@pytest.fixture(scope="module")
def client():
    """Portée « module » : l'API démarre une fois pour tout le fichier (hypothesis l'exige)."""
    from fastapi.testclient import TestClient

    from api.main import app

    with TestClient(app) as c:  # le « with » exécute le lifespan : le modèle est chargé
        yield c


def en_json(valeur: object) -> bytes:
    """Corps de requête JSON, sous forme d'octets : permet aussi d'envoyer un corps invalide."""
    return json.dumps(valeur).encode("utf-8")


def verifier_forme_standard(reponse) -> None:
    """Un 422 de FastAPI : « detail » est une liste d'objets avec loc, msg et type."""
    detail = reponse.json()["detail"]
    assert isinstance(detail, list) and detail, f"detail n'est pas une liste d'erreurs : {detail!r}"
    for erreur in detail:
        assert {"loc", "msg", "type"} <= set(erreur), f"erreur sans loc/msg/type : {erreur!r}"


# Étape B.1 : un seul test paramétré, chaque cas avec son code attendu.
CAS = [
    pytest.param(en_json({"text": ""}), 422, id="texte-vide"),
    pytest.param(en_json({"text": "   "}), 422, id="texte-fait-d-espaces"),
    pytest.param(en_json({"text": "a"}), 200, id="un-seul-caractere"),
    pytest.param(en_json({"text": "a" * 2000}), 200, id="2000-caracteres"),
    pytest.param(en_json({"text": "a" * 2001}), 422, id="2001-caracteres"),
    pytest.param(en_json({}), 422, id="champ-absent"),
    pytest.param(en_json({"text": 42}), 422, id="champ-d-un-autre-type"),
    pytest.param(b"pas du json", 422, id="corps-qui-n-est-pas-du-json"),
    # B.6 : un blanc invisible. "\x1f" (séparateur d'unité) n'est pas une espace pour l'œil,
    # mais str.strip() le retire : le texte est donc vide pour predict(). Avant la correction
    # du schéma, il passait le contrat (1 caractère) puis recevait un 422 d'une autre forme.
    pytest.param(en_json({"text": "\x1f"}), 422, id="blanc-invisible-x1f"),
]


@pytest.mark.parametrize("corps, code_attendu", CAS)
def test_frontieres_du_contrat(client, corps, code_attendu):
    reponse = client.post("/predict", content=corps, headers={"Content-Type": "application/json"})
    assert reponse.status_code == code_attendu
    if code_attendu == 422:  # B.2 : la forme compte autant que le code
        verifier_forme_standard(reponse)


# Étape B.5 : deux propriétés vérifiées au hasard par hypothesis.
@settings(deadline=None)
@given(texte=st.text(min_size=1, max_size=2000).filter(lambda t: t.strip() != ""))
def test_tout_texte_non_blanc_recoit_une_etiquette(client, texte):
    reponse = client.post("/predict", json={"text": texte})
    assert reponse.status_code == 200
    corps = reponse.json()
    assert corps["label"] in ETIQUETTES_DU_CONTRAT
    assert 0.0 <= corps["score"] <= 1.0


@settings(deadline=None)
@given(texte=st.text(alphabet=st.sampled_from(BLANCS), min_size=1, max_size=50))
def test_tout_texte_de_blancs_est_refuse_sous_la_forme_standard(client, texte):
    reponse = client.post("/predict", json={"text": texte})
    assert reponse.status_code == 422
    verifier_forme_standard(reponse)
