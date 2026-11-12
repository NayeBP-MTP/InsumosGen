"""
Actualizaciones de InsumosGen desde los releases de GitHub.

`comprobar()` consulta el último release y dice si hay una versión nueva (nunca lanza: sin red o con la
VPN del cliente bloqueando GitHub devuelve ESTADO_ERROR). `descargar_actualizacion()` baja el zip del
release, verifica su SHA-256 y lo extrae a `<instalación>\\app.new`; `lanzar_actualizacion()` cierra el
trabajo de esta app entregándoselo a `installer/update.py`, que hace el cambio de carpetas fuera de este
proceso (no se puede reemplazar el código que está corriendo).

Mantenerlo simple: si el updater falla, el respaldo es siempre bajar el Setup.exe a mano.
"""
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional
from urllib.error import HTTPError

from packaging.version import InvalidVersion, Version

from utils.paths import app_instalada
from version import __version__

REPO = "NayeBP-MTP/InsumosGen"
API_ULTIMO_RELEASE = f"https://api.github.com/repos/{REPO}/releases/latest"
URL_RELEASES = f"https://github.com/{REPO}/releases"
TIMEOUT_SEGUNDOS = 8

ESTADO_AL_DIA = "al_dia"
ESTADO_NUEVA = "nueva"
ESTADO_ERROR = "error"

RAIZ_APP = Path(__file__).resolve().parents[1]
ARCHIVO_RESULTADO = "update_result.json"


class ActualizacionError(Exception):
    """La actualización no se pudo preparar; el mensaje es apto para mostrarlo al usuario."""


class PythonNuevoError(ActualizacionError):
    """El release pide otra versión de Python: solo se puede actualizar con el Setup.exe nuevo."""


@dataclass
class Resultado:
    estado: str
    version_actual: str
    version_nueva: str = ""
    notas: str = ""
    url_zip: str = ""
    url_sha256: str = ""
    url_setup: str = ""
    url_pagina: str = URL_RELEASES
    mensaje: str = ""

    @property
    def hay_nueva(self) -> bool:
        return self.estado == ESTADO_NUEVA

    @property
    def puede_actualizar_solo(self) -> bool:
        """El release trae el zip y su hash, y esta copia es una instalación (no un clon de desarrollo)."""
        return self.hay_nueva and bool(self.url_zip and self.url_sha256) and app_instalada()


def _abrir_url(url: str):
    peticion = urllib.request.Request(
        url, headers={"Accept": "application/vnd.github+json", "User-Agent": f"InsumosGen/{__version__}"})
    return urllib.request.urlopen(peticion, timeout=TIMEOUT_SEGUNDOS)


def _error(version_actual: str, mensaje: str) -> Resultado:
    return Resultado(ESTADO_ERROR, version_actual, mensaje=mensaje)


def comprobar(version_actual: str = __version__, abrir: Callable = _abrir_url) -> Resultado:
    """Consulta el último release publicado. Nunca lanza excepciones."""
    try:
        with abrir(API_ULTIMO_RELEASE) as respuesta:
            datos = json.loads(respuesta.read().decode("utf-8"))
        etiqueta = str(datos["tag_name"])
        nueva = Version(etiqueta.lstrip("vV"))
        actual = Version(version_actual)
    except HTTPError as e:
        if e.code in (403, 429):
            return _error(version_actual, "GitHub limitó las consultas desde esta red; intenta más tarde.")
        if e.code == 404:
            return _error(version_actual, "Todavía no hay ningún release publicado.")
        return _error(version_actual, f"GitHub respondió con el error {e.code}.")
    except InvalidVersion:
        return _error(version_actual, "La versión del release no es válida.")
    except Exception:
        return _error(version_actual, "No se pudo consultar GitHub (sin conexión o la red lo bloquea).")

    if nueva <= actual:
        return Resultado(ESTADO_AL_DIA, version_actual, version_nueva=str(nueva))

    activos = {a.get("name", ""): a.get("browser_download_url", "") for a in datos.get("assets", [])}
    zip_nombre = f"InsumosGen-{nueva}.zip"
    return Resultado(
        ESTADO_NUEVA, version_actual, version_nueva=str(nueva),
        notas=(datos.get("body") or "").strip(),
        url_zip=activos.get(zip_nombre, ""),
        url_sha256=activos.get(zip_nombre + ".sha256", ""),
        url_setup=activos.get(f"InsumosGen-Setup-{nueva}.exe", ""),
        url_pagina=datos.get("html_url") or URL_RELEASES,
    )


_comprobado_al_arrancar = False


def comprobar_al_arrancar(**kwargs) -> Optional[Resultado]:
    """La consulta automática: una sola por arranque de la app (la UI se vuelve a abrir en cada ronda)."""
    global _comprobado_al_arrancar
    if _comprobado_al_arrancar:
        return None
    _comprobado_al_arrancar = True
    return comprobar(**kwargs)


# --- Instalación ------------------------------------------------------------------------------------------

def carpeta_instalacion() -> Optional[Path]:
    r"""`%LOCALAPPDATA%\Programs\InsumosGen` (el padre de `app\`), o None si esto no es una instalación."""
    if not app_instalada():
        return None
    carpeta = RAIZ_APP.parent
    return carpeta if (carpeta / "runtime").is_dir() else None


def _leer_sha256(texto: str) -> str:
    token = (texto.split() or [""])[0].lower()
    if not re.fullmatch(r"[0-9a-f]{64}", token):
        raise ActualizacionError("El archivo de verificación (.sha256) del release no es válido.")
    return token


def _extraer(zip_ruta: Path, destino: Path) -> None:
    raiz = destino.resolve()
    with zipfile.ZipFile(zip_ruta) as zf:
        for nombre in zf.namelist():
            if raiz not in (raiz / nombre).resolve().parents:
                raise ActualizacionError("El paquete de la actualización trae rutas no válidas.")
        zf.extractall(destino)


def serie_de_python_requerida(app_nueva: Path) -> Optional[tuple]:
    """La serie de Python (p. ej. (3, 13)) que fija el bootstrap.ps1 del release, o None si no se encuentra."""
    bootstrap = app_nueva / "installer" / "bootstrap.ps1"
    if not bootstrap.is_file():
        return None
    coincidencia = re.search(r"\$PythonSerie\s*=\s*@\((\d+)\s*,\s*(\d+)\)", bootstrap.read_text(encoding="utf-8-sig"))
    return (int(coincidencia.group(1)), int(coincidencia.group(2))) if coincidencia else None


def descargar_actualizacion(
    resultado: Resultado, instalacion: Path, abrir: Callable = _abrir_url,
    progreso: Optional[Callable[[int, int], None]] = None,
) -> Path:
    r"""
    Baja el zip del release, verifica su SHA-256 y lo extrae a `<instalación>\app.new`. Devuelve esa carpeta.
    Lanza ActualizacionError (o PythonNuevoError si el release necesita otro Python).
    """
    if not resultado.puede_actualizar_solo:
        raise ActualizacionError("Este release no se puede instalar desde la app.")
    try:
        with abrir(resultado.url_sha256) as r:
            esperado = _leer_sha256(r.read().decode("utf-8"))

        temporal = Path(tempfile.mkdtemp(prefix="insumosgen_update_"))
        try:
            zip_ruta = temporal / f"InsumosGen-{resultado.version_nueva}.zip"
            h = hashlib.sha256()
            with abrir(resultado.url_zip) as r, open(zip_ruta, "wb") as f:
                total = int(r.headers.get("Content-Length") or 0) if hasattr(r, "headers") else 0
                hecho = 0
                for bloque in iter(lambda: r.read(1 << 16), b""):
                    f.write(bloque)
                    h.update(bloque)
                    hecho += len(bloque)
                    if progreso:
                        progreso(hecho, total)
            if h.hexdigest() != esperado:
                raise ActualizacionError("La descarga está dañada (no coincide con su SHA-256); intenta de nuevo.")

            nueva = instalacion / "app.new"
            shutil.rmtree(nueva, ignore_errors=True)
            _extraer(zip_ruta, nueva)
        finally:
            shutil.rmtree(temporal, ignore_errors=True)
    except ActualizacionError:
        raise
    except Exception as e:
        raise ActualizacionError(f"No se pudo descargar la actualización ({e}).") from e

    serie = serie_de_python_requerida(nueva)
    if serie and serie != tuple(sys.version_info[:2]):
        shutil.rmtree(nueva, ignore_errors=True)
        raise PythonNuevoError(
            f"La versión {resultado.version_nueva} necesita Python {serie[0]}.{serie[1]}; "
            "descarga el instalador nuevo.")
    return nueva


def lanzar_actualizacion(instalacion: Path, pid: int) -> None:
    r"""
    Lanza `update.py` (copiado a una carpeta temporal, porque reemplaza la carpeta de la que corre la app)
    y regresa; quien llama debe cerrar la app enseguida. Usa el update.py del release nuevo si lo trae.
    """
    origen = instalacion / "app.new" / "installer" / "update.py"
    if not origen.is_file():
        origen = RAIZ_APP / "installer" / "update.py"
    carpeta = Path(tempfile.mkdtemp(prefix="insumosgen_helper_"))
    helper = carpeta / "update.py"
    shutil.copy2(origen, helper)
    pythonw = instalacion / "runtime" / "venv" / "Scripts" / "pythonw.exe"
    from utils.paths import app_data_dir  # evita ciclo en importaciones tempranas

    subprocess.Popen(
        [str(pythonw), str(helper), "--instalacion", str(instalacion), "--datos", str(app_data_dir()),
         "--pid", str(pid)],
        creationflags=0x00000008 | 0x00000200,  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
        close_fds=True, cwd=str(carpeta),
    )


def cerrar_actualizacion(instalacion: Optional[Path] = None) -> Optional[dict]:
    """
    Al arrancar tras una actualización: borra `app.old` y devuelve (una sola vez) el resultado que dejó
    `update.py` ({"ok": bool, "version": ..., "mensaje": ...}), o None si no hubo ninguna.
    """
    instalacion = instalacion or carpeta_instalacion()
    if not instalacion:
        return None
    shutil.rmtree(instalacion / "app.old", ignore_errors=True)
    archivo = instalacion / "runtime" / ARCHIVO_RESULTADO
    if not archivo.is_file():
        return None
    try:
        datos = json.loads(archivo.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        datos = None
    try:
        archivo.unlink()
    except OSError:
        pass
    return datos if isinstance(datos, dict) else None
