"""Jeu d'or : avis annotés à la main, dont des cas difficiles."""
from pathlib import Path

import pandas as pd
import pytest

RACINE = Path(__file__).resolve().parents[1]
MODELE = RACINE / "models" / "sentiment.joblib"
JEU_OR = RACINE / "data" / "jeu_or.csv"
pytestmark = pytest.mark.skipif(
    not MODELE.exists() or not JEU_OR.exists(),
    reason="modèle ou jeu d'or absent : python src/make_demo.py && python src/train.py",
)


def _predict(texte: str) -> dict:
    import sys
    sys.path.insert(0, str(RACINE / "src"))
    from predict import predict
    return predict(texte)


def test_jeu_or_predictions():
    df = pd.read_csv(JEU_OR)
    erreurs = [
        (texte, label, _predict(texte)["label"])
        for texte, label in zip(df["text"], df["label"], strict=True)
        if _predict(texte)["label"] != label
    ]
    assert not erreurs, f"avis du jeu d'or mal classés : {erreurs}"


@pytest.mark.xfail(reason="cas connu : avis mitigé classé positif à tort", strict=True)
def test_jeu_or_erreur_connue():
    assert _predict("Livraison rapide mais produit décevant")["label"] == "negative"
