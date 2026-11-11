import json
import time
from pathlib import Path
from utils.paths import app_data_dir

HISTORY_PATH = app_data_dir() / "historial_ventas.json"
_LOCK_PATH = app_data_dir() / "historial_ventas.lock"
_LOCK_TIMEOUT_S = 15
_LOCK_POLL_S = 0.05


class RunHistory:
    """Historial persistente de intentos de venta (un registro por intento)."""

    @staticmethod
    def load() -> list:
        if not HISTORY_PATH.exists():
            return []
        try:
            return json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []

    @staticmethod
    def append(records: list) -> None:
        if not records:
            return
        HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
        # Lock de archivo (crear-si-no-existe, atómico en Windows/POSIX) para que dos
        # procesos escribiendo el historial a la vez (p. ej. lotes de venta en
        # paralelo) no se pisen con un read-modify-write sin proteger.
        limite = time.monotonic() + _LOCK_TIMEOUT_S
        fd = None
        while fd is None:
            try:
                fd = _LOCK_PATH.open("x")
            except FileExistsError:
                if time.monotonic() > limite:
                    raise TimeoutError(
                        f"No se pudo obtener el lock de {_LOCK_PATH} tras {_LOCK_TIMEOUT_S}s"
                    )
                time.sleep(_LOCK_POLL_S)
        try:
            HISTORY_PATH.write_text(
                json.dumps(RunHistory.load() + records, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        finally:
            fd.close()
            _LOCK_PATH.unlink(missing_ok=True)
