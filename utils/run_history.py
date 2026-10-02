import json
from pathlib import Path

HISTORY_PATH = Path("data/historial_ventas.json")


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
        HISTORY_PATH.write_text(
            json.dumps(RunHistory.load() + records, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
