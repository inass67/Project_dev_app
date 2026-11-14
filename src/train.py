"""Entraîne le pipeline TF-IDF + régression logistique, le mesure et le sérialise."""
import json
import sys
from pathlib import Path

import joblib
import pandas as pd
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

RACINE = Path(__file__).resolve().parents[1]
DEMO = RACINE / "data" / "demo_reviews.csv"
MODELE = RACINE / "models" / "sentiment.joblib"
METRIQUES = RACINE / "models" / "metrics.json"
SEUIL_F1 = 0.85
GRAINE = 42


def construire_pipeline() -> Pipeline:
    """Vectoriseur et modèle dans un seul objet : la même transformation
    s'applique forcément à l'entraînement et en production."""
    return Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)),
        ("clf", LogisticRegression(max_iter=1000, class_weight="balanced", random_state=GRAINE)),
    ])


def main() -> int:
    if not DEMO.exists():
        print("data/demo_reviews.csv absent : lancez d'abord python src/make_demo.py", file=sys.stderr)
        return 1
    df = pd.read_csv(DEMO)
    print(f"Source : demo, {len(df)} avis ({(df.label == 'negative').sum()} négatifs)")

    # Découper AVANT toute transformation : sinon le jeu de test fuite dans l'entraînement
    X_train, X_test, y_train, y_test = train_test_split(
        df["review"], df["label"], test_size=0.2, random_state=GRAINE, stratify=df["label"]
    )
    print(f"{len(X_train)} avis d'entraînement, {len(X_test)} de test")

    pipeline = construire_pipeline()
    pipeline.fit(X_train, y_train)
    print(f"Vocabulaire : {len(pipeline.named_steps['tfidf'].vocabulary_)} termes")

    rapport = classification_report(y_test, pipeline.predict(X_test), output_dict=True, zero_division=0)
    f1 = rapport["macro avg"]["f1-score"]
    print(f"F1 macro sur le jeu de test : {f1:.3f} (seuil {SEUIL_F1})")

    # Sérialisation : le pipeline entier (vectoriseur + modèle) dans un seul fichier
    MODELE.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODELE)
    METRIQUES.write_text(json.dumps({
        "modele": "tfidf-logreg",
        "f1_macro": round(f1, 4),
        "seuil_f1": SEUIL_F1,
        "n_train": len(X_train),
        "n_test": len(X_test),
        "scikit_learn": sklearn.__version__,
        "joblib": joblib.__version__,
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print("Modèle : models/sentiment.joblib")
    print("Métriques : models/metrics.json (versionné dans Git, contrairement au modèle)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
