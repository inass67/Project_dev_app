"""Contrôle le livrable du paquet comme le fera le correcteur."""
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
VERSION = "1.0.0"
AVIS = "Colis abîmé, je suis déçu"
lignes: list[str] = []
echecs = 0


def noter(ok: bool, message: str, detail: str = "") -> bool:
    global echecs
    echecs += not ok
    ligne = f"[{'OK' if ok else 'ÉCHEC'}] {message}" + (f" : {detail}" if detail else "")
    print(ligne)
    lignes.append(ligne)
    return ok


def lancer(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess:
    env = {**os.environ, "VERIFICATION_LIVRABLE": "1"}
    return subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", check=False)


def terminer() -> int:
    bilan = "Bilan : CONFORME" if echecs == 0 else f"Bilan : NON CONFORME ({echecs} échec(s))"
    print(bilan)
    lignes.append(bilan)
    RAPPORT.parent.mkdir(parents=True, exist_ok=True)
    RAPPORT.write_text("\n".join(lignes) + "\n", encoding="utf-8")
    print(f"Rapport : {RAPPORT.relative_to(RACINE).as_posix()}")
    return 0 if echecs == 0 else 1


def main() -> int:
    roue = DIST / f"sentiment_app-{VERSION}-py3-none-any.whl"
    sdist = DIST / f"sentiment_app-{VERSION}.tar.gz"
    if not noter(roue.exists(), "roue présente", roue.name):
        return terminer()
    noter(sdist.exists(), "distribution source présente", sdist.name)
    with zipfile.ZipFile(roue) as z:
        noms = z.namelist()
        noter("sentiment_app/modele/sentiment.joblib" in noms, "modèle embarqué dans la roue")
        ep = [n for n in noms if n.endswith("entry_points.txt")]
        noter(bool(ep) and "sentiment" in z.read(ep[0]).decode(), "commande « sentiment » déclarée")
        noter(not any(n.startswith("tests/") for n in noms), "pas de tests dans la roue")
    noter(f"[{VERSION}]" in (RACINE / "CHANGELOG.md").read_text(encoding="utf-8"),
          "CHANGELOG.md décrit cette version", f"[{VERSION}]")
    with tempfile.TemporaryDirectory() as tmp:
        dossier = Path(tmp)
        venv.create(dossier / "env", with_pip=True)
        binaires = dossier / "env" / ("Scripts" if sys.platform == "win32" else "bin")
        python = binaires / ("python.exe" if sys.platform == "win32" else "python")
        r = lancer([str(python), "-m", "pip", "install", "-q", str(roue), "pytest"], dossier)
        if not noter(r.returncode == 0, "installation de la roue dans un environnement neuf",
                     r.stderr.strip().splitlines()[-1] if r.returncode else ""):
            return terminer()
        r = lancer([str(python), "-m", "pytest", "-q", "-p", "no:cacheprovider",
                    str(RACINE / "tests" / "test_paquet.py")], dossier)
        bilan = (r.stdout.strip().splitlines() or ["(aucune sortie)"])[-1]
        noter(r.returncode == 0 and "skipped" not in bilan, "tests lancés sur le paquet installé", bilan)
        commande = binaires / ("sentiment.exe" if sys.platform == "win32" else "sentiment")
        r = lancer([str(commande), "--json", AVIS], dossier)
        erreur = (r.stderr.strip().splitlines() or [""])[-1]
        noter(r.returncode == 0 and '"label"' in r.stdout, "commande installée", r.stdout.strip() or erreur)
    return terminer()


if __name__ == "__main__":
    raise SystemExit(main())
