import json
import os
from datetime import datetime
from pathlib import Path
from utils.paths import app_data_dir

# Ruta del canal de progreso de ESTE proceso. run.py la fija a una ruta propia
# por proceso (data/run_progress_<pid>.jsonl) vía Progress.set_path(), ANTES de
# iniciar cualquier ronda, para que dos ventanas de `python run.py` corriendo a
# la vez no compartan (ni se trunquen mutuamente con) el mismo archivo. Los
# subprocesos pytest heredan la ruta vía la variable de entorno
# PROVIDIGITAL_RUN_PROGRESS_PATH (set_path la deja en os.environ) y la leen aquí
# al importar este módulo. Sin ninguna de las dos (ej. un `pytest` suelto fuera
# de run.py), se usa la ruta de siempre.
PROGRESS_PATH = Path(os.environ.get("PROVIDIGITAL_RUN_PROGRESS_PATH", app_data_dir() / "run_progress.jsonl"))

# Si run.py lanzó este subproceso como una venta aislada (ver MAX_WORKERS_VENTAS
# en run.py), esta variable trae una etiqueta legible ("CN · Izcalli 335") para
# que el log combinado (utils/console_progress.py) pueda distinguir de qué venta
# viene cada evento cuando varias corren en paralelo y comparten este archivo.
_WORKER_TAG = os.environ.get("PROVIDIGITAL_RUN_TAG")


class Progress:
    """
    Canal de feedback entre los tests (subproceso pytest) y quien muestra el
    avance (ventana de progreso o log en consola): cada evento es una línea JSON
    en PROGRESS_PATH. Niveles: "info" (paso), "fase" (cambio de fase), "ok" y
    "error".
    """

    @staticmethod
    def set_path(path) -> None:
        """Fija la ruta del canal para ESTE proceso y la deja en os.environ para
        que los subprocesos pytest que lance (vía subprocess.Popen(env=...)) la
        hereden. Debe llamarse antes de Progress.reset()/emit() en run.py."""
        global PROGRESS_PATH
        PROGRESS_PATH = Path(path)
        os.environ["PROVIDIGITAL_RUN_PROGRESS_PATH"] = str(PROGRESS_PATH)

    @staticmethod
    def reset() -> None:
        PROGRESS_PATH.parent.mkdir(parents=True, exist_ok=True)
        PROGRESS_PATH.write_text("", encoding="utf-8")

    @staticmethod
    def emit(msg: str, nivel: str = "info") -> None:
        try:
            PROGRESS_PATH.parent.mkdir(parents=True, exist_ok=True)
            evento = {"hora": datetime.now().strftime("%H:%M:%S"), "nivel": nivel, "msg": msg}
            if _WORKER_TAG:
                evento["worker"] = _WORKER_TAG
            with PROGRESS_PATH.open("a", encoding="utf-8") as f:
                f.write(json.dumps(evento, ensure_ascii=False) + "\n")
        except Exception:
            pass  # el feedback nunca debe romper una ejecución

    @staticmethod
    def read_from(offset: int):
        """Devuelve (eventos_nuevos, nuevo_offset) leyendo desde `offset` bytes."""
        if not PROGRESS_PATH.exists():
            return [], 0
        with PROGRESS_PATH.open("rb") as f:
            f.seek(offset)
            data = f.read()
        # Solo líneas completas.
        fin = data.rfind(b"\n")
        if fin < 0:
            return [], offset
        eventos = []
        for linea in data[: fin + 1].decode("utf-8", errors="replace").splitlines():
            try:
                eventos.append(json.loads(linea))
            except json.JSONDecodeError:
                continue
        return eventos, offset + fin + 1
