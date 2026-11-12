import sqlite3
import string
from datetime import date
from pathlib import Path
from utils.paths import app_data_dir


DB_PATH = app_data_dir() / "generated_agency_ids.sqlite3"

# Sello fijo (2 dígitos) que marca cualquier insumo creado por esta herramienta,
# independiente del tipo de estructura. Ver config/Context/NUEVA_ESTRUCTURA_AGENCIA.md.
HERRAMIENTA_TAG = "11"

ALFABETO = string.ascii_uppercase
LETRA_INICIAL = "C"


class AgencyIdAllocator:
    """
    Genera Agency_Id únicos (13 dígitos) para el flujo "Nueva estructura de agencia".

    Esquema: [branch(4)][yymm(4)][HERRAMIENTA_TAG(2)][consecutivo(3)].
    El consecutivo reinicia en 1 por cada combinación (branch, yymm). Al no
    reutilizar nunca el "000" del esquema legado (BBBB+000+sufijo), no puede
    colisionar con Agency_Id ya existentes en Challenger_uat/botDB.

    Reutiliza el patrón de utils/offer_id_allocator.py (SQLite local con
    transacción EXCLUSIVE para evitar colisiones entre corridas, incluso en
    paralelo).
    """

    @staticmethod
    def _init_db():
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(DB_PATH, timeout=30) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS used_agency_ids (
                    agency_id INTEGER PRIMARY KEY,
                    branch INTEGER NOT NULL,
                    yymm TEXT NOT NULL,
                    consecutivo INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    @staticmethod
    def get_unique_agency_id(branch: int, hoy: date = None) -> int:
        """Devuelve el siguiente Agency_Id libre para `branch` en el mes actual (o `hoy`)."""
        AgencyIdAllocator._init_db()
        hoy = hoy or date.today()
        yymm = hoy.strftime("%y%m")

        with sqlite3.connect(DB_PATH, timeout=30, isolation_level="EXCLUSIVE") as conn:
            conn.execute("BEGIN EXCLUSIVE")

            fila = conn.execute(
                "SELECT MAX(consecutivo) FROM used_agency_ids WHERE branch = ? AND yymm = ?",
                (branch, yymm),
            ).fetchone()
            siguiente = (fila[0] or 0) + 1
            if siguiente > 999:
                raise RuntimeError(
                    f"Se agotaron los consecutivos de Agency_Id para branch={branch}, yymm={yymm}"
                )

            agency_id = int(f"{branch:04d}{yymm}{HERRAMIENTA_TAG}{siguiente:03d}")

            conn.execute(
                """INSERT INTO used_agency_ids (agency_id, branch, yymm, consecutivo)
                   VALUES (?, ?, ?, ?)""",
                (agency_id, branch, yymm, siguiente),
            )
            conn.commit()
            return agency_id


class AgencySectionAllocator:
    """
    Asigna la siguiente letra de sección disponible para un DM/AM nuevo, por
    sucursal. Es una secuencia propia de esta herramienta, independiente de las
    letras ya usadas históricamente en Challenger_uat.AgencyStructure (esos datos
    reutilizan letras entre distintos DMs sin una convención consistente). Empieza
    en 'C' y nunca repite una letra ya asignada para esa sucursal desde que existe
    esta herramienta.
    """

    @staticmethod
    def _init_db():
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(DB_PATH, timeout=30) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS used_section_letters (
                    branch INTEGER NOT NULL,
                    letra TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (branch, letra)
                )
            """)
            conn.commit()

    @staticmethod
    def get_next_section_letter(branch: int) -> str:
        AgencySectionAllocator._init_db()
        inicio = ALFABETO.index(LETRA_INICIAL)

        with sqlite3.connect(DB_PATH, timeout=30, isolation_level="EXCLUSIVE") as conn:
            conn.execute("BEGIN EXCLUSIVE")

            usadas = {
                row[0]
                for row in conn.execute(
                    "SELECT letra FROM used_section_letters WHERE branch = ?", (branch,)
                ).fetchall()
            }
            for letra in ALFABETO[inicio:]:
                if letra not in usadas:
                    conn.execute(
                        "INSERT INTO used_section_letters (branch, letra) VALUES (?, ?)",
                        (branch, letra),
                    )
                    conn.commit()
                    return letra

            raise RuntimeError(f"Se agotaron las letras de sección disponibles para branch={branch}")


if __name__ == "__main__":
    print(AgencyIdAllocator.get_unique_agency_id(branch=2075))
    print(AgencySectionAllocator.get_next_section_letter(branch=2075))
