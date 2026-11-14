"""Fabrique un jeu de 290 avis clients étiquetés (145 positifs, 145 négatifs).

Le jeu est reproductible (graine fixe) et volontairement difficile :
100 avis mitigés et 30 neutres.
"""
import csv
import random
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
SORTIE = RACINE / "data" / "demo_reviews.csv"
GRAINE = 42

POS = [
    "produit conforme", "livraison rapide", "très satisfait", "excellent rapport qualité prix",
    "je recommande", "parfait", "service client réactif", "emballage soigné", "très bonne qualité",
    "super produit", "rien à redire", "colis arrivé en avance", "je suis ravi", "top",
    "fonctionne parfaitement", "très content de mon achat", "vendeur sérieux", "bonne surprise",
    "facile à utiliser", "belle finition", "je rachèterai", "merci beaucoup", "génial",
]
NEG = [
    "produit défectueux", "livraison en retard", "très déçu", "mauvaise qualité",
    "je ne recommande pas", "colis abîmé", "service client injoignable", "arnaque",
    "remboursement refusé", "ne fonctionne pas", "cassé à la réception", "à éviter",
    "commande incomplète", "décevant", "trop cher pour ce que c'est", "nul",
    "aucune réponse du vendeur", "produit non conforme", "je suis mécontent", "horrible",
    "erreur de taille", "pièce manquante", "jamais reçu",
]
NEUTRE = ["commande passée la semaine dernière", "produit reçu", "acheté pour un cadeau",
          "deuxième commande sur ce site", "utilisé quelques jours"]


def avis(rng: random.Random, principal: list[str], secondaire: list[str], mitige: bool, neutre: bool) -> str:
    morceaux = rng.sample(principal, 2)
    if mitige:
        morceaux.append("mais " + rng.choice(secondaire))
    if neutre:
        morceaux.insert(0, rng.choice(NEUTRE))
    texte = ", ".join(morceaux)
    return texte[0].upper() + texte[1:] + "."


def main() -> int:
    rng = random.Random(GRAINE)
    lignes = []
    for label, principal, secondaire in (("positive", POS, NEG), ("negative", NEG, POS)):
        for i in range(145):
            lignes.append({"review": avis(rng, principal, secondaire, mitige=i < 50, neutre=50 <= i < 65),
                           "label": label})
    rng.shuffle(lignes)
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    with SORTIE.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["review", "label"])
        w.writeheader()
        w.writerows(lignes)
    print(f"{len(lignes)} avis écrits dans data/demo_reviews.csv")
    print("  145 positifs, 145 négatifs")
    print("  dont 100 avis mitigés et 30 neutres, volontairement difficiles")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
