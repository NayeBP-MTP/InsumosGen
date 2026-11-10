import re
import socket
from dataclasses import dataclass
from enum import Enum
from typing import Optional

import pyodbc

from config.credentials import ConnectionSettings


TIMEOUT_TCP_SEG = 4
TIMEOUT_LOGIN_SEG = 5
PUERTO_SQL = 1433
URL_DRIVER_ODBC = "https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server"

_TABLA_VALIDA = re.compile(r"^\[?\w+\]?(\.\[?\w+\]?){0,2}$")


class Categoria(str, Enum):
    OK = "ok"
    SERVIDOR_INVALIDO = "servidor_invalido"
    HOST_INALCANZABLE = "host_inalcanzable"
    DRIVER_AUSENTE = "driver_ausente"
    LOGIN_RECHAZADO = "login_rechazado"
    BASE_INACCESIBLE = "base_inaccesible"
    TIMEOUT = "timeout"
    SIN_PERMISOS = "sin_permisos"
    ERROR = "error"


@dataclass
class ResultadoConexion:
    """Resultado de probar una conexión: `mensaje` es apto para mostrarse al usuario."""
    categoria: Categoria
    mensaje: str

    @property
    def ok(self) -> bool:
        return self.categoria is Categoria.OK


def host_puerto(server: str) -> Optional[tuple[str, int]]:
    r"""
    Host y puerto TCP de un SERVER de SQL Server ('host', 'host,1433', 'tcp:host,1433').
    None si es una instancia con nombre sin puerto ('host\instancia'): su puerto es dinámico
    y no se puede comprobar con un connect TCP directo.
    """
    destino = server.strip().replace("tcp:", "", 1)
    host, _, puerto = destino.partition(",")
    if "\\" in host and not puerto.strip():
        return None
    return host.split("\\")[0], int(puerto) if puerto.strip().isdigit() else PUERTO_SQL


def sanear(texto: str, password: str = "") -> str:
    """Quita contraseñas de un mensaje de error: pyodbc a veces refleja la cadena de conexión."""
    if password:
        texto = texto.replace(password, "****")
    return re.sub(r"(PWD=)(\{(?:[^}]|\}\})*\}|[^;]*)", r"\1****", texto, flags=re.IGNORECASE)


class ConnectionTester:
    """
    Prueba una conexión a SQL Server en pasos y traduce cada falla a su causa real:
    puerto TCP -> inicio de sesión + SELECT 1 -> (opcional) lectura de una tabla esperada.
    `conectar` y `abrir_socket` son inyectables para probar sin red.
    """

    def __init__(self, conectar=pyodbc.connect, abrir_socket=socket.create_connection):
        self._conectar = conectar
        self._abrir_socket = abrir_socket

    def probar(self, conexion: ConnectionSettings, base: Optional[str] = None,
               tabla: Optional[str] = None) -> ResultadoConexion:
        """
        `base`: base a la que iniciar sesión (si no, la predeterminada del usuario).
        `tabla`: tabla que debe poder leerse, p. ej. 'dbo.Ofertas', para detectar "login ok pero sin permisos".
        """
        if any(c in conexion.server for c in ";{}"):
            return ResultadoConexion(Categoria.SERVIDOR_INVALIDO, "El servidor tiene caracteres no válidos (; { }).")
        if tabla and not _TABLA_VALIDA.match(tabla):
            return ResultadoConexion(Categoria.ERROR, f"Nombre de tabla no válido: {tabla}")

        destino = host_puerto(conexion.server)
        if destino:
            problema = self._problema_tcp(*destino)
            if problema:
                return ResultadoConexion(
                    Categoria.HOST_INALCANZABLE,
                    f"No se alcanza {destino[0]}:{destino[1]} ({problema}). ¿Está activa la VPN del cliente?",
                )

        try:
            cnx = self._conectar(conexion.connection_string(base), timeout=TIMEOUT_LOGIN_SEG)
        except pyodbc.Error as exc:
            return self._traducir(exc, conexion, base)
        try:
            cnx.execute("SELECT 1").fetchone()
            if tabla:
                cnx.execute(f"SELECT TOP 1 1 FROM {tabla}").fetchone()
        except pyodbc.Error as exc:
            return self._traducir(exc, conexion, base, tabla)
        finally:
            cnx.close()
        return ResultadoConexion(Categoria.OK, "Conexión correcta.")

    def _problema_tcp(self, host: str, puerto: int) -> Optional[str]:
        try:
            with self._abrir_socket((host, puerto), timeout=TIMEOUT_TCP_SEG):
                return None
        except socket.gaierror:
            return "el nombre no se resuelve (DNS)"
        except socket.timeout:
            return f"sin respuesta en {TIMEOUT_TCP_SEG}s"
        except OSError as exc:
            return sanear(str(exc))

    @staticmethod
    def _traducir(exc: pyodbc.Error, conexion: ConnectionSettings, base: Optional[str],
                  tabla: Optional[str] = None) -> ResultadoConexion:
        sqlstate = exc.args[0] if exc.args else ""
        texto = sanear(str(exc.args[1] if len(exc.args) > 1 else exc).strip(), conexion.password)
        bajo = texto.lower()
        if sqlstate == "IM002" or "data source name not found" in bajo:
            return ResultadoConexion(
                Categoria.DRIVER_AUSENTE,
                f"No se encontró el driver ODBC '{conexion.driver}'. Instálalo desde {URL_DRIVER_ODBC} "
                f"o elige otro en la lista. Detalle: {texto}")
        if sqlstate in ("28000", "28P01") or "login failed" in bajo:
            return ResultadoConexion(
                Categoria.LOGIN_RECHAZADO,
                f"El servidor rechazó el usuario o la contraseña de '{conexion.user}'. Detalle: {texto}")
        if "cannot open database" in bajo:
            return ResultadoConexion(
                Categoria.BASE_INACCESIBLE,
                f"La base '{base}' no existe en ese servidor o el usuario no tiene permiso. Detalle: {texto}")
        if "permission was denied" in bajo or "invalid object name" in bajo:
            return ResultadoConexion(
                Categoria.SIN_PERMISOS,
                f"Inicia sesión, pero no puede leer {tabla or 'el objeto solicitado'}: "
                f"revisa los permisos o el nombre. Detalle: {texto}")
        if sqlstate == "HYT00" or "timeout" in bajo:
            return ResultadoConexion(
                Categoria.TIMEOUT,
                f"El servidor no contestó el inicio de sesión en {TIMEOUT_LOGIN_SEG}s: puede estar caído, "
                f"saturado o inaccesible desde tu red. Detalle: {texto}")
        return ResultadoConexion(Categoria.ERROR, f"[{sqlstate}] {texto}")
