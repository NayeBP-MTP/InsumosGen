import json
from datetime import datetime
from pathlib import Path

PROGRESS_PATH = Path("data/run_progress.jsonl")


class Progress:
    """
    Canal de feedback entre los tests (subproceso pytest) y la ventana de progreso:
    cada evento es una línea JSON en data/run_progress.jsonl.
    Niveles: "info" (paso), "fase" (cambio de fase), "ok" y "error".
    """

    @staticmethod
    def reset() -> None:
        PROGRESS_PATH.parent.mkdir(parents=True, exist_ok=True)
        PROGRESS_PATH.write_text("", encoding="utf-8")

    @staticmethod
    def emit(msg: str, nivel: str = "info") -> None:
        try:
            PROGRESS_PATH.parent.mkdir(parents=True, exist_ok=True)
            evento = {"hora": datetime.now().strftime("%H:%M:%S"), "nivel": nivel, "msg": msg}
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
