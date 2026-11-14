"""Fabrique 290 avis en français : 145 positifs, 145 négatifs,
dont 100 mitigés et 30 neutres, volontairement difficiles."""
import random
from pathlib import Path

import pandas as pd

RACINE = Path(__file__).resolve().parents[1]
SORTIE = RACINE / "data" / "demo_reviews.csv"
GRAINE = 42

POS = [
    "Livraison rapide, produit conforme, très satisfait",
    "Excellent produit, je recommande vivement",
    "Pas déçu du tout, qualité au rendez-vous",
    "Emballage soigné, notice claire, parfait",
    "Très bon rapport qualité prix, je rachèterai",
    "Service client réactif et produit conforme",
    "Super achat, fonctionne parfaitement",
    "Commande reçue en avance, très content",
    "Qualité irréprochable, je suis ravi",
    "Produit solide et bien fini, merci",
]
NEG = [
    "Produit cassé et service injoignable, à fuir",
    "Commande jamais reçue, remboursement en attente",
    "Qualité médiocre, je regrette mon achat",
    "Très déçu, le produit ne fonctionne pas",
    "Livraison catastrophique, colis perdu",
    "Service client nul, aucune réponse",
    "Article défectueux, je demande un remboursement",
    "Arnaque, ne correspond pas à la description",
    "Emballage abîmé et produit en panne",
    "Horrible expérience, je déconseille",
]
# Avis mitigés : un défaut et une qualité, étiquetés selon l'impression dominante
MITIGES_POS = [
    "Bon produit mais livraison un peu lente",
    "Qualité correcte, emballage perfectible, globalement content",
    "Livraison tardive mais le produit est excellent",
    "Prix élevé, mais il en vaut la peine",
]
MITIGES_NEG = [
    "Livraison rapide mais produit décevant",
    "Joli design, mais ça tombe en panne vite",
    "Service aimable, produit pourtant défectueux",
    "Emballage soigné mais le produit ne marche pas",
]
NEUTRES = [
    "Produit reçu mercredi",
    "Colis ouvert, en cours de test",
    "Commande passée la semaine dernière",
]
ADD = ["", " vraiment", " dans l'ensemble", " honnêtement", " franchement"]


def variante(rng: random.Random, base: str) -> str:
    mot = rng.choice(ADD)
    suite = rng.choice(["", ".", " !", " vraiment"])
    return f"{base}{mot}{suite}".strip()


def main() -> int:
    rng = random.Random(GRAINE)
    lignes = []
    for _ in range(115):
        lignes.append((variante(rng, rng.choice(POS)), "positive"))
    for _ in range(115):
        lignes.append((variante(rng, rng.choice(NEG)), "negative"))
    for _ in range(30):  # 15 + 15 avis mitigés pour atteindre 100 avec les suivants
        lignes.append((variante(rng, rng.choice(MITIGES_POS)), "positive"))
    # on complète à 145 / 145 avec mitigés et neutres
    for _ in range(25):
        lignes.append((variante(rng, rng.choice(MITIGES_NEG)), "negative"))
    for _ in range(5):
        lignes.append((variante(rng, rng.choice(NEUTRES)), "negative"))
    lignes = lignes[:290]
    rng.shuffle(lignes)
    df = pd.DataFrame(lignes, columns=["review", "label"])
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(SORTIE, index=False, encoding="utf-8")
    print(f"{len(df)} avis écrits dans {SORTIE.relative_to(RACINE)}")
    print(f"  {(df.label == 'positive').sum()} positifs, {(df.label == 'negative').sum()} négatifs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())