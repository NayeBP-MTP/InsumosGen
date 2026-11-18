import sqlite3
from datetime import date, timedelta
from pathlib import Path
from utils.paths import app_data_dir


DB_PATH = app_data_dir() / "generated_offer_ids.sqlite3"


class OfferIdAllocator:
    """
    Genera identificadores únicos para las ofertas del flujo Cliente Frecuente
    (idOferta, Customer_Id, Agreement_Num), evitando colisiones entre ejecuciones,
    incluso en paralelo. Reutiliza el patrón de utils/birthdate_allocator.py.

    Reglas de negocio (ver config/Context/offers.sql):
      - idOferta      = AAMM(4) + persona(1) + consecutivo(3)  -> 8 dígitos
      - Customer_Id   = branch(4) + AAMM(4) + persona(1) + consecutivo(4) -> 13 dígitos
      - Agreement_Num = AAMM(4) + persona(1) + consecutivo(4) -> 9 dígitos
      - semana        = AAAASS, semana ISO que cambia cada miércoles (no lunes)

    `persona` y `consecutivo` son el mismo par de valores para las tres claves;
    solo cambia el ancho de relleno del consecutivo (3 dígitos en idOferta,
    4 dígitos en Customer_Id/Agreement_Num), por lo que el consecutivo se
    limita a 1-999 por persona/mes.
    """

    @staticmethod
    def _init_db():
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(DB_PATH, timeout=30) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS used_offer_ids (
                    id_oferta INTEGER PRIMARY KEY,
                    customer_id INTEGER,
                    agreement_num INTEGER,
                    aamm TEXT,
                    persona INTEGER,
                    consecutivo INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    @staticmethod
    def calcular_semana(hoy: date = None) -> int:
        """
        Retorna la semana en formato AAAASS (año ISO + semana ISO de 2 dígitos),
        donde el número de semana avanza cada miércoles en lugar del lunes
        estándar de ISO 8601.
        """
        hoy = hoy or date.today()
        # Desplazar 2 días hacia atrás convierte el miércoles en el equivalente
        # de "lunes" para efectos del cálculo ISO, de modo que la semana no
        # avanza hasta el miércoles real.
        referencia = hoy - timedelta(days=2)
        anio_iso, semana_iso, _ = referencia.isocalendar()
        return int(f"{anio_iso}{semana_iso:02d}")

    @staticmethod
    def get_unique_ids(branch: int, hoy: date = None) -> dict:
        """
        Retorna un dict con idOferta, Customer_Id, Agreement_Num y semana,
        garantizados como únicos (persistidos en SQLite).
        """
        OfferIdAllocator._init_db()
        hoy = hoy or date.today()
        aamm = hoy.strftime("%y%m")

        with sqlite3.connect(DB_PATH, timeout=30, isolation_level="EXCLUSIVE") as conn:
            conn.execute("BEGIN EXCLUSIVE")

            for persona in range(0, 10):
                for consecutivo in range(1, 1000):
                    id_oferta = int(f"{aamm}{persona}{consecutivo:03d}")

                    try:
                        customer_id = int(f"{branch:04d}{aamm}{persona}{consecutivo:04d}")
                        agreement_num = int(f"{aamm}{persona}{consecutivo:04d}")

                        conn.execute(
                            """INSERT INTO used_offer_ids
                               (id_oferta, customer_id, agreement_num, aamm, persona, consecutivo)
                               VALUES (?, ?, ?, ?, ?, ?)""",
                            (id_oferta, customer_id, agreement_num, aamm, persona, consecutivo)
                        )
                        conn.commit()

                        return {
                            "idOferta": id_oferta,
                            "Customer_Id": customer_id,
                            "Agreement_Num": agreement_num,
                            "semana": OfferIdAllocator.calcular_semana(hoy),
                        }

                    except sqlite3.IntegrityError:
                        continue

            raise RuntimeError("No hay identificadores disponibles para asignar este mes")


if __name__ == "__main__":
    ids = OfferIdAllocator.get_unique_ids(branch=2025)
    print(ids)
