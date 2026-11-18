"""
Lanzador de la app instalada (los accesos directos ejecutan `pythonw.exe launch.pyw`, sin consola).

Marca el proceso como instalado, para que los datos vayan a %LOCALAPPDATA%\InsumosGen (los subprocesos
pytest heredan la variable), fija el directorio de trabajo y abre la UI. Sin consola un error no se ve,
así que se registra en <datos>/logs/launch.log.
"""
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path

os.environ["INSUMOSGEN_INSTALADO"] = "1"

RAIZ = Path(__file__).resolve().parent
os.chdir(RAIZ)
sys.path.insert(0, str(RAIZ))


def _registrar_error() -> None:
    try:
        from utils.paths import app_data_dir

        carpeta = app_data_dir() / "logs"
        carpeta.mkdir(parents=True, exist_ok=True)
        with open(carpeta / "launch.log", "a", encoding="utf-8") as log:
            log.write(f"\n--- {datetime.now():%Y-%m-%d %H:%M:%S} ---\n{traceback.format_exc()}")
    except Exception:
        pass


if __name__ == "__main__":
    try:
        import run

        run.main()
    except Exception:
        _registrar_error()
        raise
