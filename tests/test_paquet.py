"""Tests du paquet INSTALLÉ (ignorés dans le dépôt, sauf VERIFICATION_LIVRABLE=1)."""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

_spec = importlib.util.find_spec("sentiment_app")
if not (_spec and "site-packages" in (_spec.origin or "")) and not os.environ.get("VERIFICATION_LIVRABLE"):
    pytest.skip("paquet non installé : python scripts/verifier_livrable.py", allow_module_level=True)

import sentiment_app  # noqa: E402

COMMANDE = shutil.which("sentiment", path=str(Path(sys.executable).parent))


def test_importe_depuis_le_paquet_installe():
    assert "site-packages" in sentiment_app.__file__


def test_version():
    assert sentiment_app.__version__ == "1.0.0"


def test_predict_positif():
    assert sentiment_app.predict("très satisfait, livraison rapide, je recommande")["label"] == "positive"


def test_predict_negatif():
    assert sentiment_app.predict("produit défectueux, très déçu, à éviter")["label"] == "negative"


def test_texte_vide():
    with pytest.raises(ValueError):
        sentiment_app.predict("   ")


def test_commande():
    assert COMMANDE, "commande sentiment introuvable"
    r = subprocess.run([COMMANDE, "--json", "colis abîmé"], capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0
    assert "label" in json.loads(r.stdout)
