"""Classe un avis avec le modèle entraîné : python src/predict.py "texte"."""
import sys
from functools import lru_cache
from pathlib import Path
from typing import TypedDict

import joblib

RACINE = Path(__file__).resolve().parents[1]
MODELE = RACINE / "models" / "sentiment.joblib"


class Resultat(TypedDict):
    label: str
    score: float


@lru_cache(maxsize=1)
def charger_modele():
    """Chargé une seule fois par processus, pas à chaque appel."""
    if not MODELE.exists():
        raise FileNotFoundError("models/sentiment.joblib absent : lancez python src/train.py")
    return joblib.load(MODELE)


def predict(texte: str) -> Resultat:
    """Renvoie {'label': 'positive'|'negative', 'score': float}."""
    if not isinstance(texte, str) or not texte.strip():
        raise ValueError("texte vide")
    pipeline = charger_modele()
    etiquette = pipeline.predict([texte])[0]
    score = float(pipeline.predict_proba([texte]).max())
    return {"label": str(etiquette), "score": round(score, 4)}


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    try:
        r = predict(" ".join(args))
    except (ValueError, FileNotFoundError) as e:
        print(f"erreur : {e}", file=sys.stderr)
        return 2
    print(f"{r['label']} (confiance {r['score']:.0%})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
