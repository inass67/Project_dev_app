# sentiment-app

Classe le sentiment (positive / negative) d'un avis client rédigé en français.
Le modèle (TF-IDF + régression logistique, sérialisé avec Joblib) est embarqué dans la roue.

## Installation

    pip install sentiment_app-1.0.0-py3-none-any.whl

## Exemple

    sentiment "Livraison rapide, produit conforme"
    sentiment --json "Colis abîmé, je suis déçu"

En Python :

    from sentiment_app import predict
    predict("Très satisfait")   # {'label': 'positive', 'score': 0.9}

## Limites

- Entraîné sur un jeu de démonstration de 290 avis : vocabulaire réduit.
- Les avis mitigés ou hors domaine peuvent être mal classés ; la confiance ne garantit pas la justesse.
- Le modèle sérialisé dépend de scikit-learn 1.5 : ne charger que des fichiers Joblib de confiance.
