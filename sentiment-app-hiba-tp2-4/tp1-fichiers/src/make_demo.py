"""Fabrique data/demo_reviews.csv : 290 avis en français, 145 positifs et 145 négatifs.

Un tiers des avis sont mitigés et 30 sont neutres : le jeu est volontairement difficile.
Le fichier est régénéré à l'identique à chaque exécution (graine fixe).
"""
import random
from pathlib import Path

import pandas as pd

RACINE = Path(__file__).resolve().parents[1]
SORTIE = RACINE / "data" / "demo_reviews.csv"
GRAINE = 42

POS = ["Livraison rapide", "Produit conforme à la description", "Très satisfait", "Excellente qualité",
       "Emballage soigné", "Service client réactif", "Je recommande", "Rapport qualité prix top",
       "Commande reçue en avance", "Pas déçu du tout", "Parfait, merci", "Produit de très bonne qualité"]
NEG = ["Livraison très lente", "Produit cassé à la réception", "Très déçu", "Qualité médiocre",
       "Service client injoignable", "Commande jamais reçue", "Je déconseille", "Remboursement toujours en attente",
       "Colis abîmé", "Produit non conforme", "À fuir", "Aucune réponse du vendeur"]
POS_PARTIEL = ["bon produit", "emballage correct", "prix honnête", "qualité correcte", "belle couleur"]
NEG_PARTIEL = ["livraison lente", "notice confuse", "colis un peu abîmé", "service client lent", "finition moyenne"]
NEUTRE = ["Colis reçu mardi", "Commande passée dimanche", "Produit reçu dans un carton standard",
          "Article livré à l'adresse indiquée", "Je n'ai pas encore testé le produit"]


def _avis(rng: random.Random, label: str, genre: str) -> str:
    principal, secondaire = (POS, NEG_PARTIEL) if label == "positive" else (NEG, POS_PARTIEL)
    if genre == "net":
        return f"{rng.choice(principal)}, {rng.choice(principal).lower()}"
    if genre == "mitige":
        if rng.random() < 0.3:  # l'ordre des propositions varie : le modèle doit l'apprendre
            return f"{rng.choice(secondaire).capitalize()} mais {rng.choice(principal).lower()}"
        return f"{rng.choice(principal)} mais {rng.choice(secondaire)}"
    return f"{rng.choice(NEUTRE)}. {rng.choice(principal)}"


def main() -> int:
    rng = random.Random(GRAINE)
    lignes = []
    for label in ("positive", "negative"):
        genres = ["net"] * 45 + ["mitige"] * 50 + ["neutre"] * 15 + ["net"] * 35
        for g in genres:
            lignes.append({"review": _avis(rng, label, g), "label": label})
    rng.shuffle(lignes)
    df = pd.DataFrame(lignes)
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(SORTIE, index=False, encoding="utf-8")
    print(f"{len(df)} avis écrits dans data/{SORTIE.name}")
    print(f"  {(df.label == 'positive').sum()} positifs, {(df.label == 'negative').sum()} négatifs")
    print("  dont 100 avis mitigés et 30 neutres, volontairement difficiles")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
