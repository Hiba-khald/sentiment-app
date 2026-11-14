"""Vérifie le livrable du TP 4 comme le correcteur : fichiers, roue, installation isolée."""
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
AVIS = "Produit défectueux, service client injoignable, je réclame un remboursement"
RESULTATS: list[tuple[bool, str, str]] = []


def noter(ok: bool, label: str, detail: str = "") -> bool:
    RESULTATS.append((ok, label, detail))
    print(f"[{'OK' if ok else 'ÉCHEC'}] {label}" + (f" : {detail}" if detail else ""))
    return ok


def lancer(cmd: list[str], cwd: Path = RACINE) -> subprocess.CompletedProcess:
    # VERIFICATION_LIVRABLE rend les tests du paquet obligatoires : un test ignoré ne prouve rien.
    env = {**os.environ, "VERIFICATION_LIVRABLE": "1"}
    return subprocess.run(
        cmd,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def dernieres_lignes(sortie: str, nombre: int = 3) -> str:
    lignes = [ligne for ligne in sortie.strip().splitlines() if ligne.strip()]
    return " | ".join(lignes[-nombre:])


def controler_dist() -> tuple[Path | None, Path | None]:
    if not DIST.is_dir():
        noter(False, "dossier dist/ présent", "lancez d'abord python -m build")
        return None, None
    whls = sorted(DIST.glob("*.whl"))
    sources = sorted(DIST.glob("*.tar.gz"))
    autres = [p.name for p in DIST.iterdir() if p.is_file() and p not in whls + sources]
    roue_ok = noter(
        whls == [DIST / "sentiment_app-1.0.0-py3-none-any.whl"],
        "roue présente : sentiment_app-1.0.0-py3-none-any.whl",
        ", ".join(p.name for p in whls) or "aucune",
    )
    source_ok = noter(
        sources == [DIST / "sentiment_app-1.0.0.tar.gz"],
        "distribution source présente : sentiment_app-1.0.0.tar.gz",
        ", ".join(p.name for p in sources) or "aucune",
    )
    noter(not autres, "aucun autre fichier dans dist/", ", ".join(autres) if autres else "")
    if not (roue_ok and source_ok):
        return None, None
    return whls[0], sources[0]


def controler_roue(roue: Path) -> bool:
    with zipfile.ZipFile(roue) as z:
        noms = set(z.namelist())
    requis = {
        "sentiment_app/__init__.py",
        "sentiment_app/cli.py",
        "sentiment_app/predict.py",
        "sentiment_app/modele/sentiment.joblib",
        "sentiment_app-1.0.0.dist-info/METADATA",
        "sentiment_app-1.0.0.dist-info/entry_points.txt",
    }
    manquants = sorted(requis - noms)
    noter(not manquants, "contenu de la roue complet", ", ".join(manquants) if manquants else "")
    noter(not any("test" in nom.lower() for nom in noms), "pas de tests dans la roue")
    with zipfile.ZipFile(roue) as z:
        points = z.read("sentiment_app-1.0.0.dist-info/entry_points.txt").decode("utf-8")
    noter("sentiment = sentiment_app.cli:main" in points, "commande « sentiment » déclarée")
    return not manquants and "sentiment = sentiment_app.cli:main" in points


def controler_changelog() -> bool:
    texte = (RACINE / "CHANGELOG.md").read_text(encoding="utf-8") if (RACINE / "CHANGELOG.md").exists() else ""
    return noter("## [1.0.0]" in texte, "CHANGELOG.md décrit cette version : [1.0.0]")


def controler_etiquette() -> bool:
    r = subprocess.run(["git", "tag", "--points-at", "HEAD"], cwd=RACINE, capture_output=True, text=True)
    etiquette = "v1.0.0" in r.stdout.split()
    return noter(etiquette, "étiquette Git sur le dernier commit : v1.0.0", r.stdout.strip())


def controler_installation_isolee(roue: Path) -> bool:
    with tempfile.TemporaryDirectory() as tmp:
        dossier = Path(tmp)
        venv.create(dossier / "env", with_pip=True)
        binaires = dossier / "env" / ("Scripts" if sys.platform == "win32" else "bin")
        python = binaires / ("python.exe" if sys.platform == "win32" else "python")
        r = lancer([str(python), "-m", "pip", "install", "-q", str(roue), "pytest"], dossier)
        if not noter(r.returncode == 0, "installation de la roue dans un environnement neuf",
                     dernieres_lignes(r.stderr or r.stdout)):
            return False
        r = lancer([str(python), "-m", "pytest", "-q", "-p", "no:cacheprovider",
                    str(RACINE / "tests" / "test_paquet.py")], dossier)
        bilan = (r.stdout.strip().splitlines() or ["(aucune sortie)"])[-1]
        if not noter(r.returncode == 0 and "skipped" not in bilan, "tests lancés sur le paquet installé", bilan):
            return False
        commande = binaires / ("sentiment.exe" if sys.platform == "win32" else "sentiment")
        r = lancer([str(commande), "--json", AVIS], dossier)
        erreur = (r.stderr.strip().splitlines() or [""])[-1]  # la dernière ligne d'une trace dit l'essentiel
        return noter(r.returncode == 0 and '"label"' in r.stdout, "commande installée", r.stdout.strip() or erreur)


def terminer() -> int:
    conforme = all(ok for ok, _, _ in RESULTATS)
    lignes = [f"[{'OK' if ok else 'ÉCHEC'}] {label}" + (f" : {detail}" if detail else "")
              for ok, label, detail in RESULTATS]
    lignes.append(f"Bilan : {'CONFORME' if conforme else 'NON CONFORME'}")
    RAPPORT.parent.mkdir(parents=True, exist_ok=True)
    RAPPORT.write_text("\n".join(lignes) + "\n", encoding="utf-8")
    print(f"Rapport : {RAPPORT}")
    return 0 if conforme else 1


def main() -> int:
    roue, _ = controler_dist()
    if roue is not None:
        controler_roue(roue)
    controler_changelog()
    controler_etiquette()
    if roue is not None:
        controler_installation_isolee(roue)
    return terminer()


if __name__ == "__main__":
    raise SystemExit(main())
