"""Vérifie le livrable TP 4 comme le ferait un correcteur."""
import os
import subprocess
import sys
import tempfile
import venv
import zipfile
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
DIST = RACINE / "dist"
RAPPORT = RACINE / "docs" / "livrable-tp4.txt"
lignes: list[str] = []
echecs = 0


def noter(ok: bool, texte: str, detail: str = "") -> bool:
    global echecs
    echecs += 0 if ok else 1
    ligne = f"[{'OK' if ok else 'ÉCHEC'}] {texte}" + (f" : {detail}" if detail else "")
    lignes.append(ligne)
    print(ligne)
    return ok


def lancer(cmd, cwd):
    env = {**os.environ, "VERIFICATION_LIVRABLE": "1"}
    return subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", check=False)


def terminer() -> int:
    bilan = "CONFORME" if echecs == 0 else "NON CONFORME"
    lignes.append(f"Bilan : {bilan}")
    print(f"Bilan : {bilan}")
    RAPPORT.parent.mkdir(exist_ok=True)
    RAPPORT.write_text("\n".join(lignes) + "\n", encoding="utf-8")
    print(f"Rapport : {RAPPORT.relative_to(RACINE)}")
    return 0 if echecs == 0 else 1


def main() -> int:
    roues = list(DIST.glob("*.whl"))
    sources = list(DIST.glob("*.tar.gz"))
    if not noter(len(roues) == 1, "une roue présente dans dist/", ", ".join(r.name for r in roues)):
        return terminer()
    noter(len(sources) == 1, "une distribution source présente")
    roue = roues[0]
    with zipfile.ZipFile(roue) as z:
        noms = z.namelist()
        noter(any(n.endswith("modele/sentiment.joblib") for n in noms), "modèle embarqué dans la roue")
        noter(any(n.endswith("entry_points.txt") for n in noms), "commande « sentiment » déclarée")
        noter(not any(n.startswith("tests/") for n in noms), "pas de tests dans la roue")
    chang = (RACINE / "CHANGELOG.md").read_text(encoding="utf-8") if (RACINE / "CHANGELOG.md").exists() else ""
    noter("[1.0.0]" in chang, "CHANGELOG.md décrit cette version")
    tag = subprocess.run(["git", "tag", "--points-at", "HEAD"], cwd=RACINE, capture_output=True, text=True).stdout
    noter("v1.0.0" in tag.split(), "étiquette Git sur le dernier commit : v1.0.0")

    with tempfile.TemporaryDirectory() as tmp:
        dossier = Path(tmp)
        venv.create(dossier / "env", with_pip=True)
        bin_ = dossier / "env" / ("Scripts" if sys.platform == "win32" else "bin")
        python = bin_ / ("python.exe" if sys.platform == "win32" else "python")
        r = lancer([str(python), "-m", "pip", "install", "-q", str(roue), "pytest"], dossier)
        if not noter(r.returncode == 0, "installation de la roue dans un environnement neuf",
                     (r.stderr.strip().splitlines() or [""])[-1] if r.returncode else ""):
            return terminer()
        r = lancer([str(python), "-m", "pytest", "-q", "-p", "no:cacheprovider",
                    str(RACINE / "tests" / "test_paquet.py")], dossier)
        bilan = (r.stdout.strip().splitlines() or ["(aucune sortie)"])[-1]
        noter(r.returncode == 0 and "skipped" not in bilan, "tests lancés sur le paquet installé", bilan)
        commande = bin_ / ("sentiment.exe" if sys.platform == "win32" else "sentiment")
        r = lancer([str(commande), "--json", "Livraison rapide, très satisfait"], dossier)
        noter(r.returncode == 0 and '"label"' in r.stdout, "commande installée",
              r.stdout.strip() or (r.stderr.strip().splitlines() or [""])[-1])
    return terminer()


if __name__ == "__main__":
    raise SystemExit(main())