"""Tests du paquet INSTALLÉ (pas des sources)."""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

_spec = importlib.util.find_spec("sentiment_app")
if not (_spec and "site-packages" in (_spec.origin or "")) and not os.environ.get("VERIFICATION_LIVRABLE"):
    pytest.skip("paquet non installé : python scripts/verifier_livrable.py", allow_module_level=True)

import sentiment_app  # noqa: E402

# La commande est installée à côté de l'interpréteur qui lance les tests
COMMANDE = shutil.which("sentiment", path=str(Path(sys.executable).parent))


def test_importe_depuis_le_paquet_installe():
    assert "site-packages" in sentiment_app.__file__, "le test lit les sources, pas la roue installée"


def test_version():
    assert sentiment_app.__version__ == "1.0.0"


def test_predict_renvoie_un_label():
    r = sentiment_app.predict("Livraison rapide, produit conforme, très satisfait")
    assert r["label"] in {"positive", "negative"} and 0.5 <= r["score"] <= 1


def test_predict_texte_vide():
    with pytest.raises(ValueError):
        sentiment_app.predict("   ")


def test_commande_installee():
    assert COMMANDE, "commande sentiment introuvable"
    r = subprocess.run([COMMANDE, "--json", "Livraison rapide, très satisfait"],
                       capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0 and "label" in json.loads(r.stdout)


def test_commande_refuse_texte_vide():
    r = subprocess.run([COMMANDE, " "], capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 2