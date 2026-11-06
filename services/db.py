import os
import time
from dataclasses import dataclass

import pyodbc
from dotenv import load_dotenv

from config.databases import HOSTS, host_de

load_dotenv()

DRIVER_POR_DEFECTO = "ODBC Driver 17 for SQL Server"


@dataclass(frozen=True)
class Credenciales:
    server: str
    user: str
    password: str
    driver: str


def credenciales_de_host(host: str) -> Credenciales:
    """Lee `<HOST>_SERVER/USER/PASSWORD/DRIVER` del entorno (.env)."""
    if host not in HOSTS:
        raise ValueError(f"Host '{host}' desconocido. Hosts: {', '.join(HOSTS)}.")
    faltantes = [
        f"{host}_{campo}" for campo in ("SERVER", "USER", "PASSWORD")
        if not os.environ.get(f"{host}_{campo}")
    ]
    if faltantes:
        raise EnvironmentError(
            f"Faltan variables de entorno para el host {host}: {', '.join(faltantes)}. "
            "Revisa tu .env contra .env.example."
        )
    return Credenciales(
        server=os.environ[f"{host}_SERVER"],
        user=os.environ[f"{host}_USER"],
        password=os.environ[f"{host}_PASSWORD"],
        driver=os.environ.get(f"{host}_DRIVER", DRIVER_POR_DEFECTO),
    )


class SqlServerRepository:
    """
    Base de los repositorios de SQL Server. Se construye con el nombre de la BASE; el host (y con
    él las credenciales del .env) se resuelve con config/databases.py, así una base nunca se abre
    con las credenciales de otro host.

    Con `dry_run=True` las escrituras (`_escribir`) no se ejecutan: se guardan en `dry_run_log`
    como (sql, params). Las lecturas siguen yendo a la BD.
    """

    def __init__(self, base: str, dry_run: bool = False):
        self.base = base
        self.host = host_de(base)
        self.dry_run = dry_run
        self.dry_run_log: list = []

    @property
    def credenciales(self) -> Credenciales:
        # Lazy: construir el repositorio (p. ej. en dry-run o en pruebas) no exige el .env.
        return credenciales_de_host(self.host)

    def _connection_string(self) -> str:
        c = self.credenciales
        return (
            f"DRIVER={{{c.driver}}};"
            f"SERVER={c.server};"
            f"DATABASE={self.base};"
            f"UID={c.user};"
            f"PWD={c.password};"
        )

    def _get_connection(self, intentos: int = 3):
        """
        Reintenta la conexión ante errores transitorios ("Named pipe provider: no se
        pudo abrir...", '08001'/'08S01'): con varias corridas en paralelo abriendo
        conexiones al mismo tiempo contra la VPN, el primer intento a veces falla
        aunque el servidor esté disponible.
        """
        connection_string = self._connection_string()
        for intento in range(1, intentos + 1):
            try:
                return pyodbc.connect(connection_string)
            except pyodbc.Error as exc:
                sqlstate = exc.args[0] if exc.args else ""
                if sqlstate not in ("08001", "08S01") or intento == intentos:
                    raise
                print(
                    f"Conexión a {self.base} ({self.host}) falló "
                    f"(intento {intento}/{intentos}, {sqlstate}), reintentando…"
                )
                time.sleep(2 * intento)

    def test_connection(self) -> bool:
        """Verifica que la conexión pueda establecerse. Útil para diagnóstico."""
        with self._get_connection() as conn:
            conn.execute("SELECT 1").fetchone()
        return True

    def _escribir(self, sql: str, params=()) -> None:
        """Ejecuta una escritura con commit, o la registra en `dry_run_log` si `dry_run`."""
        if self.dry_run:
            self.dry_run_log.append((sql, tuple(params)))
            return
        with self._get_connection() as conn:
            conn.cursor().execute(sql, params)
            conn.commit()
