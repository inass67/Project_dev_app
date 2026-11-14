"""Contrôle C1 : le modèle sérialisé respecte le seuil du cadrage."""
import json
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
METRIQUES = RACINE / "models" / "metrics.json"


@pytest.mark.skipif(not METRIQUES.exists(), reason="lancez python src/train.py")
def test_f1_au_dessus_du_seuil():
    m = json.loads(METRIQUES.read_text(encoding="utf-8"))
    assert m["f1_macro"] >= m["seuil_f1"]


@pytest.mark.skipif(not (RACINE / "models" / "sentiment.joblib").exists(), reason="modèle absent")
def test_modele_recharge():
    import joblib
    pipeline = joblib.load(RACINE / "models" / "sentiment.joblib")
    assert set(pipeline.classes_) == {"negative", "positive"}
