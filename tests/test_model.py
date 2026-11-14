import json
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
MODELE = RACINE / "models" / "sentiment.joblib"
pytestmark = pytest.mark.skipif(not MODELE.exists(), reason="modèle non produit : python src/train.py")


def test_predict_forme(root=RACINE):
    import sys
    sys.path.insert(0, str(root / "src"))
    from predict import predict
    r = predict("Livraison rapide, produit conforme, très satisfait")
    assert r["label"] in {"positive", "negative"}
    assert 0.5 <= r["score"] <= 1.0


@pytest.mark.parametrize("texte", ["", "   ", None, 42])
def test_predict_refuse_texte_invalide(texte):
    import sys
    sys.path.insert(0, str(RACINE / "src"))
    from predict import predict
    with pytest.raises(ValueError):
        predict(texte)


def test_f1_au_dessus_du_seuil():
    m = json.loads((RACINE / "models" / "metrics.json").read_text(encoding="utf-8"))
    assert m["f1_macro"] >= m["seuil_f1"], "modèle sous le seuil d'acceptation"
