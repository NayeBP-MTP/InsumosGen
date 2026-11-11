import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import keyring
from keyring.errors import KeyringError, PasswordDeleteError

from utils.paths import app_data_dir


SERVICE = "InsumosGen"
DRIVER_POR_DEFECTO = "ODBC Driver 17 for SQL Server"


class CredentialsMissing(Exception):
    """Faltan datos o contraseña de un host o de una estrella; `recurso` dice cuál."""

    def __init__(self, recurso: str):
        self.recurso = recurso
        super().__init__(f"Faltan credenciales de {recurso}. Captúralas en 'Conexiones y estrellas'.")


@dataclass
class ConnectionSettings:
    """Conexión a un host de SQL Server."""
    server: str
    user: str
    password: str
    driver: str = DRIVER_POR_DEFECTO

    def connection_string(self, database: Optional[str] = None) -> str:
        """
        Cadena de conexión ODBC. Usuario, contraseña y base se escapan con {...} (`}` -> `}}`):
        las contraseñas capturadas en la UI pueden llevar `;`, `{` o `=` y romperían la cadena.
        """
        partes = [f"DRIVER={{{self.driver}}}", f"SERVER={self.server}"]
        if database:
            partes.append(f"DATABASE={_escapar_odbc(database)}")
        partes += [f"UID={_escapar_odbc(self.user)}", f"PWD={_escapar_odbc(self.password)}"]
        return ";".join(partes) + ";"


def _escapar_odbc(valor: str) -> str:
    return "{" + valor.replace("}", "}}") + "}"


@dataclass
class EstrellaCredentials:
    """Credenciales de una estrella del portal, identificada por un alias."""
    alias: str
    estrella_id: str
    password: str


class CredentialStore:
    """
    Almacén de credenciales administrado desde la app (sustituye al .env).

    Las contraseñas viven en el Administrador de credenciales de Windows (vía keyring, cifradas
    por usuario con DPAPI); lo demás (servidor, usuario, driver, alias, ID de estrella) va en
    connections.json dentro de app_data_dir(). Nunca se escribe una contraseña en disco.

    Hosts y estrellas se guardan con la clave de keyring `host:<HOST>` / `estrella:<alias>`.
    Los hosts son nombres libres (p. ej. PESOS_OFFER, CHALLENGER); el mapeo base -> host vive
    en config/databases.py y este módulo no lo valida.
    """

    ARCHIVO = "connections.json"

    def __init__(self, path: Optional[Path] = None, backend=keyring):
        self._path = Path(path) if path else app_data_dir() / self.ARCHIVO
        self._backend = backend

    # ── Disponibilidad del almacén seguro ─────────────────────────────────────────────────────

    def backend_disponible(self) -> tuple[bool, str]:
        """
        Comprueba que el almacén seguro funciona de verdad: escribe, lee y borra una entrada de
        prueba. Devuelve (ok, detalle); `detalle` nombra el backend o explica la falla.
        """
        nombre = type(self._backend.get_keyring()).__name__ if hasattr(self._backend, "get_keyring") else "?"
        sonda = "sonda:disponibilidad"
        try:
            self._backend.set_password(SERVICE, sonda, "ok")
            leido = self._backend.get_password(SERVICE, sonda)
            self._borrar_password(sonda)
        except (KeyringError, OSError) as e:
            return False, f"{nombre}: {e}"
        if leido != "ok":
            return False, f"{nombre}: la lectura no coincide con lo escrito"
        return True, nombre

    # ── Hosts de BD ───────────────────────────────────────────────────────────────────────────

    def list_hosts(self) -> list[str]:
        return sorted(self._leer()["hosts"])

    def get_connection(self, host: str) -> ConnectionSettings:
        datos = self._leer()["hosts"].get(host)
        password = self._backend.get_password(SERVICE, f"host:{host}")
        if not datos or password is None:
            raise CredentialsMissing(f"host {host}")
        return ConnectionSettings(
            server=datos["server"],
            user=datos["user"],
            password=password,
            driver=datos.get("driver") or DRIVER_POR_DEFECTO,
        )

    def save_connection(self, host: str, conexion: ConnectionSettings) -> None:
        self._exigir("host", host)
        self._exigir("servidor", conexion.server)
        self._exigir("usuario", conexion.user)
        self._backend.set_password(SERVICE, f"host:{host}", conexion.password)
        datos = self._leer()
        datos["hosts"][host] = {
            "server": conexion.server.strip(),
            "user": conexion.user.strip(),
            "driver": (conexion.driver or DRIVER_POR_DEFECTO).strip(),
        }
        self._escribir(datos)

    def delete_connection(self, host: str) -> None:
        datos = self._leer()
        datos["hosts"].pop(host, None)
        self._escribir(datos)
        self._borrar_password(f"host:{host}")

    # ── Estrellas del portal ──────────────────────────────────────────────────────────────────

    def list_estrellas(self) -> list[tuple[str, str]]:
        """(alias, ID de estrella) ordenados por alias; sin contraseñas."""
        estrellas = self._leer()["estrellas"]
        return [(alias, estrellas[alias]["id"]) for alias in sorted(estrellas)]

    def get_estrella(self, alias: str) -> EstrellaCredentials:
        datos = self._leer()["estrellas"].get(alias)
        password = self._backend.get_password(SERVICE, f"estrella:{alias}")
        if not datos or password is None:
            raise CredentialsMissing(f"la estrella '{alias}'")
        return EstrellaCredentials(alias=alias, estrella_id=datos["id"], password=password)

    def save_estrella(self, estrella: EstrellaCredentials) -> None:
        self._exigir("alias", estrella.alias)
        self._exigir("ID de estrella", estrella.estrella_id)
        self._backend.set_password(SERVICE, f"estrella:{estrella.alias}", estrella.password)
        datos = self._leer()
        datos["estrellas"][estrella.alias] = {"id": estrella.estrella_id.strip()}
        self._escribir(datos)

    def delete_estrella(self, alias: str) -> None:
        datos = self._leer()
        datos["estrellas"].pop(alias, None)
        self._escribir(datos)
        self._borrar_password(f"estrella:{alias}")

    # ── Internos ──────────────────────────────────────────────────────────────────────────────

    @staticmethod
    def _exigir(campo: str, valor: str) -> None:
        if not (valor or "").strip():
            raise ValueError(f"El campo '{campo}' no puede estar vacío.")

    def _borrar_password(self, usuario: str) -> None:
        try:
            self._backend.delete_password(SERVICE, usuario)
        except PasswordDeleteError:
            pass  # ya no existía

    def _leer(self) -> dict:
        try:
            datos = json.loads(self._path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            datos = {}
        datos.setdefault("hosts", {})
        datos.setdefault("estrellas", {})
        return datos

    def _escribir(self, datos: dict) -> None:
        # Escritura atómica: un corte a media escritura no deja el JSON truncado.
        self._path.parent.mkdir(parents=True, exist_ok=True)
        temporal = self._path.with_suffix(".tmp")
        temporal.write_text(json.dumps(datos, indent=2, ensure_ascii=False), encoding="utf-8")
        os.replace(temporal, self._path)
