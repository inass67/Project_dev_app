# Compte rendu - Atelier 0

**Binôme :** Inas Mourid (@inass67) / Khadija Bounaji 
**Dépôt :** https://github.com/inass67/Project_dev_app

## 1. Répartition du travail
- Membre A (Inas Mourid) : vérification des outils, création de l'environnement virtuel,
  création et publication du dépôt GitHub, fiches de cadrage, vérification sur clone neuf.
- Membre B (Khadija Bounaji) : clone du dépôt, installation de l'environnement,
  ajout de sa ligne dans le tableau du binôme (README.md).

## 2. Résultats des contrôles
| Contrôle | Commande | Résultat |
|---|---|---|
| C1 Outils | python --version / git --version | Python 3.11.9 / Git 2.56.0 |
| C2 Fiches | pytest tests/test_cadrage.py -q | 12 passed |
| C3 .gitignore | git status | ni .venv, ni .env, ni .joblib, ni __pycache__ |
| C4 Diagnostic | python scripts/check_setup.py | 0 erreur, 0 avertissement |
| C5 Contributions | git shortlog -sn --all | deux membres présents |
| C6 Clone neuf | pytest -q | 38 passed |

## 3. Pourquoi .venv, .env et le modèle sont exclus du dépôt
- **.venv** : propre à chaque poste et très lourd ; il se recrée avec requirements.txt.
- **.env** : contient des secrets (clés d'API), qui ne doivent jamais être publiés.
- **Modèle (.joblib)** : fichier binaire lourd, reconstruit par le script d'entraînement.
- **Les métriques**, elles, sont suivies : légères, elles prouvent la qualité du modèle.

## 4. Questions de compréhension
1. **Pourquoi « ça marche sur mon poste » est insuffisant ?**
   Un fichier non commité ou un paquet installé à la main peut manquer chez les autres.
   Seule la vérification sur un clone neuf prouve que le dépôt est complet.
2. **Que contient un commit ?**
   Une photographie des fichiers ajoutés à l'index, un message, l'auteur, la date
   et un lien vers le commit précédent.
3. **Fichier ignoré ou supprimé de l'historique ?**
   Un fichier ignoré n'est simplement pas suivi par Git : il reste sur le disque.
   Un fichier supprimé de l'historique a été retiré de tous les commits passés.
   .gitignore n'agit pas sur un fichier déjà suivi.
4. **Comment reconstruire les données et le modèle ?**
   Cloner le dépôt, créer le venv, pip install -r requirements.txt,
   puis lancer le script qui génère les données et celui qui entraîne le modèle (TP 1).

## 5. Conclusion
L'environnement est reproductible : sur un clone neuf, pytest -q affiche 38 passed.