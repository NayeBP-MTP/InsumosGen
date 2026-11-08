import sqlite3
from pathlib import Path
from typing import Optional

DB_PATH = Path("data/generated_cliente_ids.sqlite3")
MAX_NNN = 999


class ClienteIdAllocator:
    """
    Reserva el consecutivo `NNN` del número de cliente (`AAMMDD + CC + 02 + NNN`) para que ventas en
    paralelo no obtengan el mismo número. Mismo patrón que utils/offer_id_allocator.py: SQLite local
    con transacción EXCLUSIVE.

    El consecutivo es el mayor entre lo que ya hay en BD (`maximo_bd`: el `NNN` más alto de hoy con
    ese prefijo en ExpedienteCliente.Cliente y Customer_Table.Customer_Id) y lo ya reservado aquí, + 1.
    """

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = Path(db_path or DB_PATH)

    def _init_db(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path, timeout=30) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS used_cliente_ids (
                    prefijo INTEGER NOT NULL,
                    nnn INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (prefijo, nnn)
                )
            """)
            conn.commit()

    def reservar(self, prefijo: int, maximo_bd: int = 0, simular: bool = False) -> int:
        """
        Devuelve el siguiente `NNN` (1-999) para `prefijo` (10 dígitos). Con `simular=True` calcula el
        mismo valor sin reservarlo (dry_run).
        """
        self._init_db()
        with sqlite3.connect(self.db_path, timeout=30, isolation_level="EXCLUSIVE") as conn:
            conn.execute("BEGIN EXCLUSIVE")
            reservado = conn.execute(
                "SELECT COALESCE(MAX(nnn), 0) FROM used_cliente_ids WHERE prefijo = ?", (prefijo,)
            ).fetchone()[0]
            nnn = max(int(maximo_bd or 0), reservado) + 1
            if nnn > MAX_NNN:
                raise RuntimeError(
                    f"Se agotaron los consecutivos del prefijo {prefijo} (máximo {MAX_NNN} por colaborador y día)."
                )
            if not simular:
                conn.execute("INSERT INTO used_cliente_ids (prefijo, nnn) VALUES (?, ?)", (prefijo, nnn))
            conn.commit()
        return nnn
