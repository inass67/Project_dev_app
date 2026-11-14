# Semaine 2 : le modèle de sentiment, notes du binôme

## Mesures

| Jeu de données | Avis de test | F1 macro |
| --- | --- | --- |
| Démonstration (290 avis) | 58 | 0,879 |
| Allociné (20 000 avis) | 4 000 | 0,920 |

Sur le jeu de démonstration, `python src/evaluate.py` donne la matrice de confusion suivante : 27 avis négatifs et 24 avis positifs bien classés, 2 négatifs pris pour des positifs et 5 positifs pris pour des négatifs, soit 7 erreurs sur 58 avis. Le vocabulaire appris compte 316 termes (149 529 sur Allociné).

## Analyse des erreurs

Les erreurs du modèle tombent sur des avis mitigés, qui commencent par un reproche puis finissent par un compliment, ou l'inverse : les tournures « sauf que ensuite », « mais finalement » ou « avant que » retournent le sens de la phrase, et c'est la fin de l'avis qui donne le vrai verdict. Le modèle TF-IDF + régression logistique additionne le poids de chaque mot ou paire de mots sans tenir compte de leur place : il voit autant de mots négatifs que positifs, ne sait pas que le connecteur annule ce qui précède, et suit souvent la première moitié de l'avis. Pour corriger ces erreurs, il faudrait une représentation qui garde l'ordre et le contexte des mots, par exemple des embeddings de phrase, plutôt que d'ajouter des bigrammes, que le modèle utilise déjà.

## Pourquoi le F1 est meilleur sur Allociné

Le jeu Allociné contient 20 000 vraies critiques, soit près de 70 fois plus d'exemples, et un vocabulaire bien plus riche : le modèle rencontre davantage de formulations différentes. Le jeu de démonstration, lui, est volontairement difficile, avec un tiers d'avis mitigés.