"""Tests du paquet installable (TP6) : emplacement du modèle, imports de l'API, commande sentiment."""
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
MODELE = RACINE / "models" / "sentiment.joblib"
avec_modele = pytest.mark.skipif(not MODELE.exists(), reason="modèle non produit : python src/train.py")


@pytest.fixture
def module_predict():
    """Le module qui charge le modèle ; son cache est vidé après le test."""
    import sentiment_app.predict as module

    yield module
    module.charger_modele.cache_clear()  # les tests suivants rechargent le vrai modèle


def test_le_modele_se_place_ou_l_on_veut(module_predict, monkeypatch, tmp_path):
    """SENTIMENT_MODELE indique au paquet installé où trouver le modèle, hors du dépôt."""
    ailleurs = tmp_path / "ailleurs.joblib"
    monkeypatch.setenv("SENTIMENT_MODELE", str(ailleurs))
    assert module_predict.chemin_modele() == ailleurs
    monkeypatch.setattr(module_predict, "MODELE", module_predict.chemin_modele())
    module_predict.charger_modele.cache_clear()
    with pytest.raises(FileNotFoundError, match="modèle introuvable"):
        module_predict.charger_modele()


def test_sans_variable_le_modele_du_depot(module_predict, monkeypatch):
    monkeypatch.delenv("SENTIMENT_MODELE", raising=False)
    assert module_predict.chemin_modele() == MODELE


def test_l_api_ne_bricole_plus_le_chemin_de_python():
    """L'API importe le paquet sentiment_app : plus aucun sys.path dans api/."""
    fautifs = [f.name for f in (RACINE / "api").glob("*.py") if "sys.path" in f.read_text(encoding="utf-8")]
    assert not fautifs, f"sys.path encore modifié dans : {fautifs}"


def test_commande_version(capsys):
    from sentiment_app.cli import main

    with pytest.raises(SystemExit) as fin:
        main(["--version"])
    assert fin.value.code == 0
    assert capsys.readouterr().out.startswith("sentiment-app ")


@avec_modele
def test_commande_predict_avis_positif(capsys):
    from sentiment_app.cli import main

    assert main(["predict", "Livraison rapide, produit conforme, très satisfait"]) == 0
    assert capsys.readouterr().out.split()[0] == "POSITIVE"


@avec_modele
def test_commande_predict_applique_le_seuil(capsys):
    """Comme l'API : sous le seuil d'abstention, INDETERMINE."""
    from sentiment_app.cli import main

    assert main(["predict", "xqzvb wlkptr grombu"]) == 0
    assert capsys.readouterr().out.split()[0] == "INDETERMINE"


def test_commande_predict_modele_introuvable(module_predict, monkeypatch, tmp_path, capsys):
    from sentiment_app.cli import main

    monkeypatch.setattr(module_predict, "MODELE", tmp_path / "absent.joblib")
    module_predict.charger_modele.cache_clear()
    assert main(["predict", "Très bon produit"]) == 1
    assert "modèle introuvable" in capsys.readouterr().err


@avec_modele
def test_commande_predict_texte_vide(capsys):
    from sentiment_app.cli import main

    assert main(["predict", "   "]) == 2
    assert "texte vide" in capsys.readouterr().err
