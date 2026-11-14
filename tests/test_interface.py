"""TP 3 : la page Streamlit, exécutée sans navigateur (AppTest) contre l'API en mémoire."""
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
pytest.importorskip("streamlit")
pytest.importorskip("fastapi")
if not (RACINE / "models" / "sentiment.joblib").exists():
    pytest.skip("modèle absent : python src/train.py", allow_module_level=True)

sys.path.insert(0, str(RACINE))
sys.path.insert(0, str(RACINE / "ui"))
import client  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from streamlit.testing.v1 import AppTest  # noqa: E402

from api.main import app  # noqa: E402

PAGE = str(RACINE / "ui" / "app.py")
CLE = "cle-client-de-test-0123456789"


@pytest.fixture
def api(monkeypatch):
    monkeypatch.setenv("API_KEYS", f"{CLE}:client")
    with TestClient(app) as c:
        c.headers["X-API-Key"] = CLE
        yield c


@pytest.fixture
def page(api, monkeypatch):
    monkeypatch.setattr(client, "creer_session", lambda: api)  # la page parle à l'API en mémoire
    return AppTest.from_file(PAGE, default_timeout=30).run()


def analyser(page, texte):
    page.text_area[0].input(texte).run()
    page.button[0].click().run()
    return page


def test_page_annonce_api_prete(page):
    assert "API prête" in page.caption[0].value


def test_avis_positif(page):
    assert analyser(page, "Livraison rapide, produit conforme, très satisfait").metric[0].label == "Avis positif"


def test_texte_inconnu_je_ne_sais_pas(page):
    resultat = analyser(page, "xqzvb wlkptr grombu")
    assert resultat.metric[0].label.startswith("Je ne sais pas")
    assert "seuil d'abstention" in resultat.info[0].value


def test_texte_vide_avertissement(page):
    assert analyser(page, "   ").warning[0].value == client.REFUS
