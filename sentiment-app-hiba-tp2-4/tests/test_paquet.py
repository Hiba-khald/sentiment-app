"""Tests du paquet INSTALLÉ : ils ne visent pas les sources du dépôt."""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

# Ces tests visent le paquet INSTALLÉ. Dans le dépôt, l'API ajoute src/ au chemin d'import :
# sentiment_app y serait trouvé dans les sources, ce qui ne prouve rien. On les ignore donc,
# sauf quand scripts/verifier_livrable.py les lance (VERIFICATION_LIVRABLE=1) : là, ils doivent passer.
_spec = importlib.util.find_spec("sentiment_app")
if not (_spec and "site-packages" in (_spec.origin or "")) and not os.environ.get("VERIFICATION_LIVRABLE"):
    pytest.skip("paquet non installé : python scripts/verifier_livrable.py", allow_module_level=True)

import sentiment_app  # noqa: E402
from sentiment_app import predict  # noqa: E402

# La commande est installée à côté de l'interpréteur qui lance les tests (bin/ sous Linux, Scripts sous Windows).
# On ne compte pas sur le PATH : il dépend de l'activation de l'environnement.
COMMANDE = shutil.which("sentiment", path=str(Path(sys.executable).parent))
AVIS = "Produit défectueux, service client injoignable, je réclame un remboursement"


def test_importe_depuis_le_paquet_installe():
    assert "site-packages" in sentiment_app.__file__, "le test lit les sources, pas la roue installée"


def test_version_lue_dans_les_metadonnees():
    assert sentiment_app.__version__ == "1.0.0"


def test_predict_renvoie_label_et_score():
    r = predict(AVIS)
    assert r["label"] in {"positive", "negative"}
    assert 0.5 <= r["score"] <= 1.0


def test_predict_refuse_texte_vide():
    with pytest.raises(ValueError, match="texte vide"):
        predict("   ")


def test_modele_emarque_dans_le_paquet():
    modele = Path(sentiment_app.__file__).resolve().parent / "modele" / "sentiment.joblib"
    assert modele.exists(), "le modèle doit être embarqué dans la roue"


def test_commande_installee():
    assert COMMANDE is not None, "commande « sentiment » introuvable à côté de l'interpréteur"
    r = subprocess.run([COMMANDE, "--json", AVIS], capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stderr
    assert '"label"' in r.stdout
    assert json.loads(r.stdout)["label"] in {"positive", "negative"}
