# Semaine 3 : l'API, notes du binôme

> Deux questions, quelques phrases chacune. Répondez avec ce que vous avez observé, pas avec le cours.

## 1. Pourquoi l'API refuse-t-elle de démarrer sans `models/sentiment.joblib`, plutôt que de démarrer et de répondre 503 ?

Au contrôle T20, après avoir renommé le modèle, `uvicorn api.main:app` s'est arrêté tout de suite avec `FileNotFoundError: models/sentiment.joblib absent : lancez python src/train.py`, puis `Application startup failed`. Une API sans modèle ne pourra jamais répondre correctement : en refusant de démarrer, elle rend la panne visible immédiatement, au moment du lancement, avec un message qui dit quoi faire. Si elle démarrait quand même, elle paraîtrait en marche et répondrait 503 à chaque client, et on ne découvrirait le problème qu'en production. Le 503 sert plutôt aux indisponibilités passagères, quand le modèle disparaît en cours de route.

## 2. Un texte vide est refusé deux fois : par Pydantic, puis par `predict()`. Est-ce redondant ?

Au contrôle T18, `{"text": ""}` a reçu un 422 avec un `detail` en liste, produit par Pydantic avant même d'appeler la fonction. Mais `{"text": "   "}` passait Pydantic (il contient au moins un caractère), puis était refusé par `predict()` avec un 422 de forme différente (`{"detail": "texte vide"}`). Les deux contrôles ne sont donc pas redondants : ils n'appliquent pas la même règle, et un texte d'espaces ne se fait arrêter que par le second. Garder les deux protège le modèle s'il est appelé sans passer par l'API, mais il faut que la règle soit la même aux deux endroits : c'est ce que le TP4 a corrigé, avec `str.strip()` dans le schéma.