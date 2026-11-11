import os
import sys
from pathlib import Path


APP_NAME = "ProvidigitalVentas"


def app_data_dir() -> Path:
    r"""
    Carpeta de datos escribibles del usuario (config, credenciales no secretas, SQLite...).

    Congelado (exe): %LOCALAPPDATA%\ProvidigitalVentas, fuera de la carpeta de instalación
    para que sobreviva a updates y desinstalación. Desde código fuente: <repo>/data, así el
    flujo de desarrollo no cambia.
    """
    if getattr(sys, "frozen", False):
        base = os.environ.get("LOCALAPPDATA")
        carpeta = (Path(base) if base else Path.home() / "AppData" / "Local") / APP_NAME
    else:
        carpeta = Path(__file__).resolve().parent.parent / "data"
    carpeta.mkdir(parents=True, exist_ok=True)
    return carpeta
