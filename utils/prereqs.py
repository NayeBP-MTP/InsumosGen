import os
import re
from dataclasses import dataclass
from typing import Callable, Optional

import pyodbc

from services.connection_tester import URL_DRIVER_ODBC

try:
    import winreg
except ImportError:  # no Windows: la app solo se instala en Windows, pero los módulos deben poder importarse
    winreg = None


URL_CHROME = "https://www.google.com/chrome/"
_DRIVER_ODBC = re.compile(r"^ODBC Driver (17|18) for SQL Server$")
_CLAVE_CHROME = r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"


@dataclass(frozen=True)
class Prerrequisito:
    """Programa externo que la app no instala: se detecta y, si falta, se indica dónde bajarlo."""
    nombre: str
    ok: bool
    detalle: str
    url: str


def _leer_app_path(raiz, vista: int = 0) -> Optional[str]:
    """Valor predeterminado de `App Paths\\chrome.exe` en la raíz del registro dada (None si no existe)."""
    if winreg is None:
        return None
    try:
        with winreg.OpenKey(raiz, _CLAVE_CHROME, 0, winreg.KEY_READ | vista) as clave:
            return winreg.QueryValueEx(clave, "")[0]
    except OSError:
        return None


def ruta_chrome(
    leer_clave: Callable = _leer_app_path, existe: Callable = os.path.isfile, entorno=os.environ,
) -> Optional[str]:
    """Ruta de chrome.exe: primero el registro (HKCU/HKLM, 64 y 32 bits), luego las carpetas habituales."""
    raices = [(winreg.HKEY_CURRENT_USER, 0)] if winreg else []
    if winreg:
        raices += [(winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_64KEY),
                   (winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_32KEY)]
    for raiz, vista in raices:
        ruta = leer_clave(raiz, vista)
        if ruta and existe(ruta):
            return ruta
    for variable in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA"):
        base = entorno.get(variable)
        if base:
            ruta = os.path.join(base, "Google", "Chrome", "Application", "chrome.exe")
            if existe(ruta):
                return ruta
    return None


def drivers_odbc_instalados(listar: Callable = pyodbc.drivers) -> list:
    """Drivers 'ODBC Driver 17/18 for SQL Server' instalados."""
    return sorted(d for d in listar() if _DRIVER_ODBC.match(d))


def verificar(chrome: Callable = ruta_chrome, drivers: Callable = drivers_odbc_instalados) -> list:
    """Estado de cada prerrequisito externo (Chrome y el driver ODBC de SQL Server)."""
    instalados = drivers()
    return [
        Prerrequisito(
            "Google Chrome", bool(chrome()),
            "No se encontró Google Chrome. Instálalo para poder ejecutar las pruebas.",
            URL_CHROME,
        ),
        Prerrequisito(
            "ODBC Driver 17 o 18 for SQL Server", bool(instalados),
            "No se encontró el driver ODBC de SQL Server (17 o 18). Instálalo para conectarte a las bases de "
            "datos; si no tienes permisos de administrador, pídelo a TI.",
            URL_DRIVER_ODBC,
        ),
    ]


def faltantes(**kwargs) -> list:
    return [p for p in verificar(**kwargs) if not p.ok]
