import subprocess
import sys
import time
from pathlib import Path
from typing import Optional, TextIO

from utils.paths import app_data_dir


def python_ejecutable() -> str:
    """
    Intérprete para lanzar subprocesos (pytest, el generador del video). La app instalada arranca con
    `pythonw.exe` (sin consola); sus subprocesos deben usar el `python.exe` hermano para tener
    stdout/stderr válidos, y se ocultan con `opciones_subproceso`.
    """
    actual = Path(sys.executable)
    if actual.name.lower() == "pythonw.exe":
        consola = actual.with_name("python.exe")
        if consola.is_file():
            return str(consola)
    return sys.executable


def sin_consola() -> bool:
    """True si el proceso corre sin consola (pythonw.exe deja `sys.stdout` y `sys.stderr` en None)."""
    return sys.stdout is None or sys.stderr is None


def abrir_log(nombre: str) -> Optional[TextIO]:
    """
    Log donde se vuelca la salida de un subproceso cuando no hay consola donde mostrarla
    (`<datos>/logs/<nombre>.log`, en modo añadir). Con consola devuelve None: la salida se ve ahí.
    """
    if not sin_consola():
        return None
    carpeta = app_data_dir() / "logs"
    carpeta.mkdir(parents=True, exist_ok=True)
    return open(carpeta / f"{nombre}.log", "a", encoding="utf-8", errors="replace")


def opciones_subproceso(log: Optional[TextIO]) -> dict:
    """Argumentos extra de `Popen`: sin consola, la ventana se oculta y la salida va al log."""
    if log is None:
        return {}
    return {
        "creationflags": getattr(subprocess, "CREATE_NO_WINDOW", 0),
        "stdout": log,
        "stderr": subprocess.STDOUT,
    }


def limpiar_logs(dias: int = 14) -> int:
    """Borra los logs de `<datos>/logs` con más de `dias` días; devuelve cuántos quitó."""
    carpeta = app_data_dir() / "logs"
    if not carpeta.is_dir():
        return 0
    limite = time.time() - dias * 86400
    borrados = 0
    for archivo in carpeta.glob("*.log"):
        try:
            if archivo.stat().st_mtime < limite:
                archivo.unlink()
                borrados += 1
        except OSError:
            pass  # en uso por otra corrida: se limpia la próxima vez
    return borrados
