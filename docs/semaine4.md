# Semaine 4 : tests approfondis et qualité, notes du binôme

> Une à deux pages. Uniquement des chiffres issus de VOS exécutions.

## 1. Couverture

- Avant (étape A) : **91 %** de `api/` (69 instructions, 6 jamais exécutées), lignes manquantes toutes dans `api/main.py` : 49, 77-79, 85-87.
- Pour chacune, le comportement qu'aucun test ne vérifiait :
  - ligne 49 : la réponse 503 quand le modèle n'est pas chargé dans `app.state` ;
  - lignes 77-79 : la branche `except Exception`, c'est-à-dire une panne du modèle pendant une requête (réponse 500, message journalisé) ;
  - lignes 85-87 : le bloc `if __name__ == "__main__":`, qui lance uvicorn quand on exécute le fichier directement.
- Après (étape D) : **… %** (à recopier depuis `pytest --cov=api --cov-report=term-missing`). Aucune ligne exclue avec `# pragma: no cover` ; seul le bloc `if __name__ == "__main__":` reste non couvert, car pytest n'exécute jamais `main.py` comme programme.

## 2. Défauts trouvés

| Symptôme | Test qui l'a révélé | Correction |
| --- | --- | --- |
| `{"text": "   "}` reçoit 422 avec `detail` en simple chaîne (`"texte vide"`), alors que `{"text": ""}` reçoit la liste d'erreurs standard : deux formes pour le même refus | `test_frontieres_du_contrat[texte-fait-d-espaces]` (vérification de la forme du 422) | `field_validator` dans `PredictRequest` : même règle que `predict()` (`str.strip()`), le refus vient du schéma |
| Un blanc invisible (`"\x1f"`) passe le contrat (1 caractère) puis est refusé par `predict()` sous l'autre forme | Propriété hypothesis `test_tout_texte_de_blancs_est_refuse_sous_la_forme_standard` (contre-exemple), ajouté ensuite au test paramétré (`blanc-invisible-x1f`) | Même correction : `str.strip()` retire aussi ce caractère |
| Un texte fait de mots inventés reçoit un verdict franc avec 0,5162 de confiance : le modèle devine | Essai dans `/docs`, puis `src/courbe_seuil.py` | Seuil d'abstention `SEUIL_ABSTENTION = 0.60` dans `api/model.py` : sous le seuil, `INDETERMINE` |
| Une panne `ValueError("bug interne")` du modèle répond 422, comme une faute du client | `test_modele_en_panne_500_sans_message_interne[ValueError]` | `api/main.py` : plus de conversion `ValueError` → 422 ; toute panne répond 500 sans message interne |
| `.upper()` produisait n'importe quelle chaîne : mypy ne voyait rien, car `predict()` renvoyait un `dict` sans type | mypy, une fois les types précisés (`TypedDict`, `Literal`) | Correspondance explicite `CORRESPONDANCE` et vérification des classes du modèle au démarrage (`test_classes_inattendues_l_api_refuse_de_demarrer`) |

## 3. Seuil d'abstention

- Points de la courbe (`python src/courbe_seuil.py`, 58 avis de test) :
  - 0,50 : répond à 58 avis (100 %), exactitude 0,879, 7 erreurs ;
  - 0,60 : répond à 42 avis (72 %), exactitude 0,952, 2 erreurs, 16 vers un humain ;
  - 0,70 : répond à 37 avis (64 %), exactitude 1,000, 0 erreur, 21 vers un humain.
- Seuil retenu : **0,60** ; part des avis envoyés à un humain : **16 sur 58 (28 %)** ; justification : on passe de 7 à 2 erreurs en ne renvoyant que 28 % des avis. Monter à 0,70 supprime les 2 dernières erreurs mais envoie 5 avis de plus à un humain, et sur 58 avis seulement ce gain est fragile.

## 4. Jeu d'or

- 21 avis écrits par le binôme, absents des données d'entraînement, dont 8 difficiles (2 négations, 2 ironies, 2 avis mitigés, 2 avis d'un autre domaine).
- Bilan (`python src/bilan_jeu_or.py`) : justes **11**, abstentions **7**, erreurs franches déclarées **3**.
- Ce que ces chiffres disent du modèle :
  - les 3 erreurs franches viennent du vocabulaire : avec 316 termes, des mots comme « vendeur », « inadmissible », « illisible » ou « vis » sont inconnus, et le modèle décide sur des mots neutres. La négation « pas un mauvais produit » est lue comme « mauvais » : un sac de mots ne voit pas l'ordre ;
  - les 2 avis d'un autre domaine (film, restaurant) partent en abstention : le modèle ne se prononce pas hors de son domaine, ce qui est le comportement voulu ;
  - les deux ironies sont justes, mais grâce aux mots « cassé » et « attente », pas parce que le modèle comprend l'ironie.

## 5. Outils statiques

- Remarques au départ : ruff **11** (dont 3 dans les tests du TP1, sur des noms de variables `l`), mypy **0**.
- Parmi les défauts de la partie 2, combien ruff et mypy avaient-ils signalés ? **Aucun au départ.** ruff signalait le `raise` sans `from` dans le `except ValueError` de `main.py` (règle B904), à l'endroit exact du défaut, mais sans en voir la conséquence (un 422 au lieu d'un 500). mypy ne pouvait rien voir tant que `predict()` renvoyait un `dict` sans type.
- Conclusion : les outils statiques trouvent des fautes de forme et des incohérences de types, pas des erreurs de comportement. Les défauts de l'API ont été trouvés par les tests aux limites, hypothesis et les tests d'intégration ; mypy n'est devenu utile qu'après avoir typé le contrat.
