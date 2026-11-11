import os
from pathlib import Path


APP_NAME = "InsumosGen"
# El lanzador de la app instalada (launch.pyw) fija esta variable; los subprocesos pytest la heredan.
ENV_INSTALADA = "INSUMOSGEN_INSTALADO"


def app_instalada() -> bool:
    """True si corre la versión instalada por Setup.exe (y no el código fuente de un clon)."""
    return os.environ.get(ENV_INSTALADA) == "1"


def app_data_dir() -> Path:
    r"""
    Carpeta de datos escribibles del usuario (config, credenciales no secretas, SQLite...).

    App instalada: %LOCALAPPDATA%\InsumosGen, fuera de la carpeta de instalación
    para que sobreviva a updates y desinstalación. Desde código fuente: <repo>/data, así el
    flujo de desarrollo no cambia.
    """
    if app_instalada():
        base = os.environ.get("LOCALAPPDATA")
        carpeta = (Path(base) if base else Path.home() / "AppData" / "Local") / APP_NAME
    else:
        carpeta = Path(__file__).resolve().parent.parent / "data"
    carpeta.mkdir(parents=True, exist_ok=True)
    return carpeta
