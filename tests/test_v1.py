"""TP 2 : la version 1 de l'API (clés, rôles, format d'erreur, CORS, dépréciation)."""
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
pytest.importorskip("fastapi")
if not (RACINE / "models" / "sentiment.joblib").exists():
    pytest.skip("modèle absent : python src/train.py", allow_module_level=True)

from fastapi.testclient import TestClient  # noqa: E402

from api.main import app  # noqa: E402
from api.securite import charger_cles  # noqa: E402

CLIENT = "cle-client-de-test-0123456789"
ADMIN = "cle-admin-de-test-0123456789"
POSITIF = {"text": "Livraison rapide, produit conforme, très satisfait"}


@pytest.fixture
def api(monkeypatch):
    # les tests déclarent leurs propres clés : ils ne dépendent pas de votre .env
    monkeypatch.setenv("API_KEYS", f"{CLIENT}:client,{ADMIN}:admin")
    with TestClient(app) as c:
        yield c


def poster(api, corps, cle=CLIENT):
    en_tetes = {"X-API-Key": cle} if cle else {}
    return api.post("/v1/predict", json=corps, headers=en_tetes)


# --- Configuration des clés ---------------------------------------------------------------
def test_cles_lues_avec_leur_role():
    assert charger_cles(f"{CLIENT}:client, {ADMIN}:admin,") == {CLIENT: "client", ADMIN: "admin"}


def test_aucune_cle_personne_n_entre():
    assert charger_cles("") == {}


def test_cle_trop_courte_refusee_sans_recopier_la_cle():
    with pytest.raises(ValueError) as e:
        charger_cles("courte:client")
    assert "courte" not in str(e.value)


def test_role_inconnu_refuse():
    with pytest.raises(ValueError, match="rôle inconnu"):
        charger_cles(f"{CLIENT}:superadmin")


# --- Authentification (401) ---------------------------------------------------------------
def test_sans_cle_401(api):
    r = poster(api, POSITIF, cle=None)
    assert r.status_code == 401
    assert r.json()["erreur"]["code"] == "NON_AUTHENTIFIE"
    assert "WWW-Authenticate" in r.headers


def test_cle_inconnue_401(api):
    r = poster(api, POSITIF, cle="une-cle-que-personne-ne-connait")
    assert r.status_code == 401
    assert r.json()["erreur"]["message"] == "Clé d'API invalide"


# --- Prédiction --------------------------------------------------------------------------
def test_client_obtient_un_verdict(api):
    r = poster(api, POSITIF)
    assert r.status_code == 200
    assert r.json()["label"] == "POSITIVE"
    assert 0.6 <= r.json()["score"] <= 1


def test_admin_peut_aussi_predire(api):
    assert poster(api, POSITIF, cle=ADMIN).status_code == 200


def test_avis_negatif(api):
    assert poster(api, {"text": "Produit défectueux, très déçu, à éviter"}).json()["label"] == "NEGATIVE"


def test_texte_inconnu_abstention(api):
    r = poster(api, {"text": "xqzvb wlkptr grombu"})
    assert r.json()["label"] == "INDETERMINE"


def test_texte_renvoye_tel_quel(api):
    assert poster(api, POSITIF).json()["text"] == POSITIF["text"]


# --- Contrat d'entrée (422) ---------------------------------------------------------------
def test_texte_blanc_422_avec_le_champ(api):
    r = poster(api, {"text": "   "})
    assert r.status_code == 422
    erreur = r.json()["erreur"]
    assert erreur["code"] == "ENTREE_INVALIDE"
    assert erreur["champs"][0]["champ"] == "body.text"


def test_texte_trop_long_422(api):
    assert poster(api, {"text": "a" * 2001}).status_code == 422


def test_champ_manquant_422(api):
    assert poster(api, {}).json()["erreur"]["code"] == "ENTREE_INVALIDE"


def test_mauvais_type_422(api):
    assert poster(api, {"text": 12}).status_code == 422


# --- Autorisation (403) -------------------------------------------------------------------
def test_modele_refuse_au_client(api):
    r = api.get("/v1/modele", headers={"X-API-Key": CLIENT})
    assert r.status_code == 403
    assert r.json()["erreur"]["code"] == "ACCES_REFUSE"


def test_modele_accessible_a_l_admin(api):
    r = api.get("/v1/modele", headers={"X-API-Key": ADMIN})
    assert r.status_code == 200
    assert r.json()["seuil_abstention"] == 0.6
    assert "f1_macro" in r.json()["metriques"]


def test_modele_sans_cle_401_avant_403(api):
    assert api.get("/v1/modele").status_code == 401


# --- Santé et routes inconnues ---------------------------------------------------------------
def test_health_v1_publique(api):
    r = api.get("/v1/health")
    assert r.status_code == 200
    assert r.json()["status"] == "OK"


def test_route_inconnue_format_v1(api):
    r = api.get("/v1/nexiste-pas")
    assert r.status_code == 404
    assert r.json()["erreur"]["code"] == "INTROUVABLE"


def test_methode_non_autorisee(api):
    assert api.get("/v1/predict", headers={"X-API-Key": CLIENT}).json()["erreur"]["code"] == "METHODE_NON_AUTORISEE"


def test_hors_v1_format_fastapi_inchange(api):
    r = api.get("/nexiste-pas")
    assert r.status_code == 404
    assert "detail" in r.json()


# --- Ancienne route : dépréciée mais fonctionnelle -----------------------------------------
def test_ancienne_route_depreciee(api):
    r = api.post("/predict", json=POSITIF)
    assert r.status_code == 200
    assert r.headers["deprecation"] == "true"
    assert "/v1/predict" in r.headers["link"]


def test_ancienne_route_barree_dans_docs(api):
    schema = api.get("/openapi.json").json()
    assert schema["paths"]["/predict"]["post"]["deprecated"] is True


# --- CORS -----------------------------------------------------------------------------------
def preflight(api, origine):
    return api.options("/v1/predict", headers={
        "Origin": origine, "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type,x-api-key"})


def test_cors_page_autorisee(api):
    r = preflight(api, "http://localhost:5500")
    assert r.status_code == 200
    assert r.headers["access-control-allow-origin"] == "http://localhost:5500"


def test_cors_autre_port_refuse(api):
    r = preflight(api, "http://localhost:5600")
    assert r.status_code == 400
    assert "access-control-allow-origin" not in r.headers


# --- Pas de secret dans le dépôt ------------------------------------------------------------
def test_env_ignore_par_git():
    assert ".env" in (RACINE / ".gitignore").read_text(encoding="utf-8")


def test_env_example_sans_vraie_cle():
    exemple = (RACINE / ".env.example").read_text(encoding="utf-8")
    assert "API_KEYS=" in exemple
    assert "remplacez" in exemple
