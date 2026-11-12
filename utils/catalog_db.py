import sqlite3
from pathlib import Path
from utils.paths import app_data_dir


DB_PATH = app_data_dir() / "catalog.sqlite3"

# seccion: seccionCliente observada para esa agencia en insumos reales de
# InsumosGen (generadores/output de dbo.Ofertas). NULL = sin evidencia encontrada;
# ver config/Context/REGLAS_DE_NEGOCIO.md para el detalle y el nivel de confianza
# de cada valor (Izcalli 335 y Tijuana 111 con muchas muestras; el resto con 1).
#
# star_name/dm/dm_focus_id/dm_name/am/am_focus_id/am_name: metadata organizacional
# (estrella/gerente de distrito/gerente de área) de solo referencia — ningún flujo
# de automatización los usa hoy. None = sin dato.
AGENCIAS_SEED = [
    # (label, agencia, focus_id, password, seccion, star_name, dm, dm_focus_id, dm_name, am, am_focus_id, am_name)
    ("Izcalli 335",        "2075000000335", "2075000343335", "Estrella1*",       "R",  None, None, None, None, None, None, None),
    ("Izcalli 334",        "2075000000334", "2075020343334", "Agente123$",       "D",
     "Argelia Morales", "IzcalliDM62R", None, "Mónica Iguala", None, None, None),
    ("Izcalli 009",        "2075000000009", "2075000009001", "Agente123$",       None, None, None, None, None, None, None, None),
    ("Izcalli 010",        "2075000000010", "2075000010001", "Agente123$",       None, None, None, None, None, None, None, None),
    ("Tijuana 111",        "2093000000111", "2093000082560", "AgenteEstrella15*", "A", None, None, None, None, None, None, None),
    ("Tijuana 112",        "2093000000112", "2093020082561", "Agente123$",       "D",
     "Sergio Mendoza López", "TijuanaBRM71A", None, "Manuel Alvarez Soto", None, None, None),
    ("Tijuana 123",        "2093000000123", "2093000082591", "AgenteEstrella16*", None, None, None, None, None, None, None, None),
    ("Tijuana 0002",       "2093000000002", "2093000002001", "Agente123$",       "B",  None, None, None, None, None, None, None),
    ("Tijuana 0003",       "2093000000003", "2093000003001", "Agente123$",       None, None, None, None, None, None, None, None),
    ("Zacatecas 239",      "2060000001239", "2060000012349", "EstrellaZ2*",      "Q",  None, None, None, None, None, None, None),
    ("Zacatecas 238",      "2060000001238", "2060000012348", "EstrellaZ1*",      "B",  None, None, None, None, None, None, None),
    ("Aguascalientes 234", "2025000001234", "2025000012345", "EstrellaAC1*",     "S",  None, None, None, None, None, None, None),
    ("San Luis Potosí 234","2049000001234", "2049000012345", "EstrellaSL1*",     None, None, None, None, None, None, None, None),
    ("Chihuahua 002",      "2095000000002", "2095000010002", "Agente123$",       "A",
     "Carlos Alanis Hernández", "ChichuahuaDM12A", "2095000020222", "Violeta Pruebas",
     "AM123 Chihuahua", "2095000090333", "Maxim Pruebas"),
    # OJO: el focus_id 2019000020001 pertenece a Agency_Id 2019000000002 en
    # botDB.dbo.Agency_Representative_AWS, NO a 2019000000001 (esa es la agencia de
    # la Estrella/DM/AM de la captura original). Confirmado por consulta directa:
    # agenciaCliente debe ser 2019000000002 para que el front liste las ofertas de
    # este usuario.
    ("Celaya 001",         "2019000000002", "2019000020001", "Agente123$",       "E",
     "Carlos Cortés", "IRAcambaro DM26FF", "2019000010002", "César Coraza",
     "AM2296 Celaya", "2019000010003", "Cirilo Castillo"),
    # Confirmado por consulta directa a Agency_Representative_AWS: 2075000012345 sí
    # está vinculado a 2075000001234 (a diferencia de Celaya). Metadata organizacional
    # tomada del ejemplo documentado en config/Context/usuariosAgencias.md.
    ("Izcalli 234",         "2075000001234", "2075000012345", "Pr0v1d1g1Tal1*",   "C",
     "Pablo Enciso", "IzcalliDM62C", "2075000012789", "Katerin Perez",
     "AM530 Izcalli", "2075000012987", "Yadira gonzalez"),
    ("Izcalli 333",         "2075000000333", "2075020343333", "Agente123$",       "E",
     None, None, None, None, None, None, None),
    ("Tijuana 113",         "2093000000113", "2093020082562", "Agente123$",       "E",
     None, None, None, None, None, None, None),
]

METODOS_ENTREGA_SEED = [
    ("Efectivo",),
    ("Cheque",),
    ("HSBC",),
    ("Finabien",),
    ("BBVA",),
]


class CatalogDB:

    @staticmethod
    def _connect():
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        return sqlite3.connect(DB_PATH, timeout=30)

    @staticmethod
    def init_db():
        with CatalogDB._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS agencias (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    label        TEXT NOT NULL,
                    agencia      TEXT NOT NULL UNIQUE,
                    focus_id     TEXT NOT NULL,
                    password     TEXT NOT NULL,
                    seccion      TEXT,
                    activa       INTEGER NOT NULL DEFAULT 1,
                    star_name    TEXT,
                    dm           TEXT,
                    dm_focus_id  TEXT,
                    dm_name      TEXT,
                    am           TEXT,
                    am_focus_id  TEXT,
                    am_name      TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS metodos_entrega (
                    id     INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL UNIQUE,
                    activo INTEGER NOT NULL DEFAULT 1
                )
            """)

            # Migración: bases creadas antes de agregar estas columnas.
            columnas = {r[1] for r in conn.execute("PRAGMA table_info(agencias)")}
            if "seccion" not in columnas:
                conn.execute("ALTER TABLE agencias ADD COLUMN seccion TEXT")
            for nueva_columna in (
                "star_name", "dm", "dm_focus_id", "dm_name", "am", "am_focus_id", "am_name"
            ):
                if nueva_columna not in columnas:
                    conn.execute(f"ALTER TABLE agencias ADD COLUMN {nueva_columna} TEXT")

            for (label, agencia, focus_id, password, seccion, star_name, dm, dm_focus_id,
                 dm_name, am, am_focus_id, am_name) in AGENCIAS_SEED:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO agencias
                        (label, agencia, focus_id, password, seccion, star_name,
                         dm, dm_focus_id, dm_name, am, am_focus_id, am_name)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (label, agencia, focus_id, password, seccion, star_name,
                     dm, dm_focus_id, dm_name, am, am_focus_id, am_name)
                )
                if seccion is not None:
                    # Completa 'seccion' en filas ya existentes (creadas antes de esta
                    # columna) que aún no la tengan, sin pisar un valor ya confirmado.
                    conn.execute(
                        "UPDATE agencias SET seccion = ? WHERE agencia = ? AND seccion IS NULL",
                        (seccion, agencia)
                    )

            for row in METODOS_ENTREGA_SEED:
                conn.execute(
                    "INSERT OR IGNORE INTO metodos_entrega (nombre) VALUES (?)",
                    row
                )

            conn.commit()

    @staticmethod
    def get_agencias() -> list[dict]:
        CatalogDB.init_db()
        with CatalogDB._connect() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM agencias WHERE activa = 1 ORDER BY label"
            ).fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def get_metodos_entrega() -> list[dict]:
        CatalogDB.init_db()
        with CatalogDB._connect() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM metodos_entrega WHERE activo = 1 ORDER BY nombre"
            ).fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def get_agencia_by_label(label: str) -> dict | None:
        CatalogDB.init_db()
        with CatalogDB._connect() as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM agencias WHERE label = ? AND activa = 1",
                (label,)
            ).fetchone()
        return dict(row) if row else None

    @staticmethod
    def add_agencia(
        label: str, agencia: str, focus_id: str, password: str, seccion: str = None,
        star_name: str = None, dm: str = None, dm_focus_id: str = None, dm_name: str = None,
        am: str = None, am_focus_id: str = None, am_name: str = None,
    ) -> None:
        CatalogDB.init_db()
        with CatalogDB._connect() as conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO agencias
                    (label, agencia, focus_id, password, seccion, star_name,
                     dm, dm_focus_id, dm_name, am, am_focus_id, am_name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (label, agencia, focus_id, password, seccion, star_name,
                 dm, dm_focus_id, dm_name, am, am_focus_id, am_name)
            )
            conn.commit()

    @staticmethod
    def add_metodo_entrega(nombre: str) -> None:
        CatalogDB.init_db()
        with CatalogDB._connect() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO metodos_entrega (nombre) VALUES (?)",
                (nombre,)
            )
            conn.commit()

    @staticmethod
    def desactivar_agencia(label: str) -> None:
        CatalogDB.init_db()
        with CatalogDB._connect() as conn:
            conn.execute(
                "UPDATE agencias SET activa = 0 WHERE label = ?",
                (label,)
            )
            conn.commit()


if __name__ == "__main__":
    CatalogDB.init_db()

    print("=== AGENCIAS ===")
    for ag in CatalogDB.get_agencias():
        print(f"  [{ag['id']}] {ag['label']} | Agencia: {ag['agencia']} | FocusId: {ag['focus_id']}")

    print("\n=== MÉTODOS DE ENTREGA ===")
    for m in CatalogDB.get_metodos_entrega():
        print(f"  [{m['id']}] {m['nombre']}")

    print(f"\nBD creada en: {DB_PATH.resolve()}")
