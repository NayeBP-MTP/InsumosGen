import sqlite3
from datetime import date, timedelta
from pathlib import Path
from utils.paths import app_data_dir


DB_PATH = app_data_dir() / "generated_birthdates.sqlite3"


class BirthdateAllocator:
    """
    Genera fechas de nacimiento únicas para evitar duplicidad entre ventas,
    incluso ejecutando pruebas en paralelo.
    """

    @staticmethod
    def _init_db():
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(DB_PATH, timeout=30) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS used_birthdates (
                    birthdate TEXT PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    @staticmethod
    def get_unique_birthdate() -> str:
        """
        Retorna una fecha única en formato dd/mm/yyyy.
        Rango sugerido: personas mayores de edad.
        """
        BirthdateAllocator._init_db()

        # Fecha base: 02/07/1995
        base = date(1995, 7, 2)

        with sqlite3.connect(DB_PATH, timeout=30, isolation_level="EXCLUSIVE") as conn:
            conn.execute("BEGIN EXCLUSIVE")

            for offset in range(0, 5000):
                candidate = base + timedelta(days=offset)
                candidate_str = candidate.strftime("%d/%m/%Y")

                try:
                    conn.execute(
                        "INSERT INTO used_birthdates (birthdate) VALUES (?)",
                        (candidate_str,)
                    )
                    conn.commit()
                    return candidate_str

                except sqlite3.IntegrityError:
                    continue

            raise RuntimeError("No hay fechas disponibles para asignar")