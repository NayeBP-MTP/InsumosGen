"""
Aplica una actualización de InsumosGen ya descargada en <instalación>\\app.new.

Lo lanza la app (utils/updater.py) copiado a una carpeta temporal, porque reemplaza la carpeta de la que
corre la app. Solo usa la biblioteca estándar. Pasos:
  1. esperar a que la app se cierre;
  2. app -> app.old y app.new -> app;
  3. si cambió el requirements.txt (hash distinto al de runtime\\state.json), pip install -r; si pip falla,
     se restaura app.old (y se reinstalan sus librerías);
  4. dejar el resultado en runtime\\update_result.json (la app lo muestra al arrancar) y relanzar la app.
La app borra app.old tras un arranque correcto.
"""
import argparse
import ctypes
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

NO_WINDOW = 0x08000000
DETACHED = 0x00000008


class UpdateError(Exception):
    pass


class Registro:
    def __init__(self, archivo: Optional[Path]):
        self.archivo = archivo

    def __call__(self, texto: str) -> None:
        if not self.archivo:
            return
        try:
            self.archivo.parent.mkdir(parents=True, exist_ok=True)
            with open(self.archivo, "a", encoding="utf-8") as f:
                f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} {texto}\n")
        except OSError:
            pass


def esperar_cierre(pid: int, segundos: int = 60) -> bool:
    """True cuando el proceso ya no existe (o no se puede observar)."""
    if not pid:
        return True
    manejador = ctypes.windll.kernel32.OpenProcess(0x00100000, False, pid)  # SYNCHRONIZE
    if not manejador:
        return True
    try:
        return ctypes.windll.kernel32.WaitForSingleObject(manejador, segundos * 1000) == 0
    finally:
        ctypes.windll.kernel32.CloseHandle(manejador)


def sha256_de(ruta: Path) -> str:
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def renombrar(origen: Path, destino: Path, intentos: int = 30, pausa: float = 1.0) -> None:
    """Renombra con reintentos: Windows lo rechaza un momento si algo aún tiene abierto un archivo."""
    for intento in range(intentos):
        try:
            origen.rename(destino)
            return
        except OSError:
            if intento == intentos - 1:
                raise
            time.sleep(pausa)


def leer_estado(ruta: Path) -> dict:
    try:
        return json.loads(ruta.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return {}


def version_de(app: Path) -> str:
    try:
        coincidencia = re.search(r'__version__\s*=\s*"([^"]+)"', (app / "version.py").read_text(encoding="utf-8"))
        return coincidencia.group(1) if coincidencia else ""
    except OSError:
        return ""


def pip_instalar(python: Path, requirements: Path, registro: Registro) -> bool:
    comando = [str(python), "-m", "pip", "install", "--disable-pip-version-check", "--no-input", "-r", str(requirements)]
    for intento in range(1, 4):
        proceso = subprocess.run(comando, capture_output=True, text=True, creationflags=NO_WINDOW)
        registro((proceso.stdout or "")[-2000:] + (proceso.stderr or "")[-2000:])
        if proceso.returncode == 0:
            return True
        registro(f"pip falló (intento {intento} de 3)")
        if intento < 3:
            time.sleep(5 * intento)
    return False


def aplicar(
    instalacion: Path, registro: Registro = Registro(None),
    pip: Callable[[Path, Path, Registro], bool] = pip_instalar,
) -> dict:
    """Hace el cambio de carpetas y, si hace falta, el de librerías. Devuelve el resultado para la app."""
    app, nueva, vieja = instalacion / "app", instalacion / "app.new", instalacion / "app.old"
    estado_ruta = instalacion / "runtime" / "state.json"
    python = instalacion / "runtime" / "venv" / "Scripts" / "python.exe"

    if not (nueva / "requirements.txt").is_file():
        raise UpdateError("No se encontró la actualización descargada (app.new).")

    shutil.rmtree(vieja, ignore_errors=True)
    renombrar(app, vieja)
    try:
        renombrar(nueva, app)
    except OSError:
        renombrar(vieja, app)
        raise UpdateError("No se pudo reemplazar la carpeta de la aplicación (algún archivo está en uso).")

    estado = leer_estado(estado_ruta)
    hash_nuevo = sha256_de(app / "requirements.txt")
    if estado.get("requirementsSha256") != hash_nuevo:
        registro("Cambió requirements.txt: actualizando librerías.")
        if not pip(python, app / "requirements.txt", registro):
            registro("pip falló: se restaura la versión anterior.")
            shutil.rmtree(app, ignore_errors=True)
            renombrar(vieja, app)
            pip(python, app / "requirements.txt", registro)  # deja las librerías como las de la versión anterior
            raise UpdateError("No se pudieron actualizar las librerías; se conserva la versión anterior.")
        estado["requirementsSha256"] = hash_nuevo

    version = version_de(app)
    estado["appVersion"] = version
    estado_ruta.write_text(json.dumps(estado, indent=4), encoding="utf-8")
    return {"ok": True, "version": version, "mensaje": f"InsumosGen se actualizó a la versión {version}."}


def relanzar(instalacion: Path) -> None:
    pythonw = instalacion / "runtime" / "venv" / "Scripts" / "pythonw.exe"
    subprocess.Popen([str(pythonw), str(instalacion / "app" / "launch.pyw")], cwd=str(instalacion / "app"),
                     creationflags=DETACHED | 0x00000200, close_fds=True)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--instalacion", required=True)
    parser.add_argument("--datos", required=True)
    parser.add_argument("--pid", type=int, default=0)
    args = parser.parse_args(argv)

    instalacion = Path(args.instalacion)
    registro = Registro(Path(args.datos) / "logs" / "update.log")
    registro(f"Actualización iniciada (app pid {args.pid}).")
    resultado_ruta = instalacion / "runtime" / "update_result.json"

    try:
        if not esperar_cierre(args.pid):
            raise UpdateError("La aplicación no se cerró a tiempo.")
        resultado = aplicar(instalacion, registro)
    except Exception as e:
        registro(f"ERROR: {e}")
        resultado = {"ok": False, "mensaje": f"No se pudo actualizar: {e}"}
    try:
        resultado_ruta.write_text(json.dumps(resultado, ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass
    registro(f"Resultado: {resultado}")
    try:
        relanzar(instalacion)
    except OSError as e:
        registro(f"No se pudo relanzar la app: {e}")
    return 0 if resultado.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
