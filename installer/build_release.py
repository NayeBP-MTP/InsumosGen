"""
Genera el zip de código de un release: dist/InsumosGen-X.Y.Z.zip (+ .sha256).

Lo que entra es lo que el usuario necesita para correr la app (código, tests e2e, requirements.txt,
launch.pyw, bootstrap.ps1); no entran las carpetas de contexto, la documentación ni lo del repo.
La versión sale de version.py. El zip es reproducible (mismo contenido -> mismo hash): entradas
ordenadas y fechas fijas.

Uso:
    python installer/build_release.py [--salida dist]
"""
import argparse
import fnmatch
import hashlib
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Iterable, List

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from version import __version__  # noqa: E402

NOMBRE_APP = "InsumosGen"

# Carpetas completas que no viajan con la app.
EXCLUIR_CARPETAS = (
    "InsumosGen/",      # contexto y generadores SQL del dominio (no es parte de la app)
    ".claude/",
    ".github/",
    "release-notes/",   # las notas viajan en el release de GitHub, no en el zip
    "installer/installer.iss",
    "installer/build_release.py",
    "tests/test_build_release.py",  # prueba el propio script de build, que no viaja
    "dist/",
    "data/",
    "screenshots/",
    "allure-results/",
)
# Patrones sobre el nombre del archivo (en cualquier carpeta).
EXCLUIR_PATRONES = ("*.md", "*.log", "*.sql", "captured_requests_*", "debug_*", ".gitignore", ".gitattributes", "*.pyc")
# Excepciones a los patrones anteriores.
INCLUIR_SIEMPRE = ("README.md",)

FECHA_FIJA = (2020, 1, 1, 0, 0, 0)  # zip reproducible


def archivos_del_repo(raiz: Path = RAIZ) -> List[str]:
    """Archivos versionados y los nuevos sin ignorar (en CI son los mismos que los versionados)."""
    salida = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=raiz, capture_output=True, check=True,
    ).stdout.decode("utf-8")
    return sorted({ruta for ruta in salida.split("\0") if ruta})


def incluir(ruta: str) -> bool:
    if ruta in INCLUIR_SIEMPRE:
        return True
    if any(ruta == c.rstrip("/") or ruta.startswith(c) for c in EXCLUIR_CARPETAS):
        return False
    nombre = ruta.rsplit("/", 1)[-1]
    return not any(fnmatch.fnmatch(nombre, patron) for patron in EXCLUIR_PATRONES)


def seleccionar(rutas: Iterable[str]) -> List[str]:
    return sorted(ruta for ruta in rutas if incluir(ruta))


def construir_zip(rutas: Iterable[str], raiz: Path, destino: Path) -> Path:
    destino.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for ruta in sorted(rutas):
            info = zipfile.ZipInfo(ruta, FECHA_FIJA)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, (raiz / ruta).read_bytes())
    return destino


def sha256_de(ruta: Path) -> str:
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def escribir_sha256(archivo: Path) -> Path:
    """`<archivo>.sha256` con '<hash>  <nombre>' (formato de sha256sum, el que lee el updater)."""
    destino = archivo.with_name(archivo.name + ".sha256")
    destino.write_text(f"{sha256_de(archivo)}  {archivo.name}\n", encoding="utf-8")
    return destino


def construir(salida: Path, raiz: Path = RAIZ, version: str = __version__) -> Path:
    rutas = seleccionar(archivos_del_repo(raiz))
    zip_ruta = construir_zip(rutas, raiz, salida / f"{NOMBRE_APP}-{version}.zip")
    escribir_sha256(zip_ruta)
    return zip_ruta


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--salida", default=str(RAIZ / "dist"), help="carpeta de salida (por defecto dist/)")
    args = parser.parse_args()
    zip_ruta = construir(Path(args.salida))
    print(f"{zip_ruta}  ({zip_ruta.stat().st_size / 1e6:.1f} MB)")
    print(f"sha256: {sha256_de(zip_ruta)}")


if __name__ == "__main__":
    main()
