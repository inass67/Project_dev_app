# Journal des versions

## [1.0.0] - 2026-11-14

### Ajouté
- Paquet `sentiment_app` avec la fonction `predict(texte)`.
- Commande `sentiment "texte" [--json]`.
- Modèle TF-IDF + régression logistique sérialisé (Joblib) embarqué dans la roue.

### Limites connues
- Jeu d'entraînement de démonstration (290 avis) ; vocabulaire limité.
- Dépend de scikit-learn 1.5.* à cause de la sérialisation du modèle.
