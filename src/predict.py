"""Fichier de compatibilité (TP6) : predict.py vit désormais dans le paquet sentiment_app.

Les anciennes habitudes continuent de fonctionner, sans logique métier ici :
  python src/predict.py "Livraison rapide, très satisfait"
  >>> from predict import predict ; predict("texte")
Lancé comme script, il demande le paquet installé : pip install -e .
"""
from sentiment_app.predict import MODELE, Resultat, charger_modele, main, predict

__all__ = ["MODELE", "Resultat", "charger_modele", "main", "predict"]

if __name__ == "__main__":
    raise SystemExit(main())
