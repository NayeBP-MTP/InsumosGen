import os
import socket
from urllib.parse import urlparse

from dotenv import load_dotenv

from config.settings import Settings

load_dotenv()

TIMEOUT_SEG = 4


def _host_puerto_botdb():
    r"""Host y puerto de BOTDB_SERVER (formatos 'host', 'host,1433', 'host\instancia')."""
    server = os.environ.get("BOTDB_SERVER", "").strip()
    if not server:
        return None
    host, _, puerto = server.replace("tcp:", "").partition(",")
    return host.split("\\")[0], int(puerto) if puerto.strip().isdigit() else 1433


def _host_puerto_challenger():
    r"""Host y puerto de CHALLENGER_SERVER, igual formato que BOTDB_SERVER."""
    server = os.environ.get("CHALLENGER_SERVER", "").strip()
    if not server:
        return None
    host, _, puerto = server.replace("tcp:", "").partition(",")
    return host.split("\\")[0], int(puerto) if puerto.strip().isdigit() else 1433


def _alcanzable(host: str, puerto: int) -> bool:
    try:
        with socket.create_connection((host, puerto), timeout=TIMEOUT_SEG):
            return True
    except OSError:
        return False


def verificar_vpn(requiere_bd: bool = True, requiere_challenger: bool = False):
    """
    Comprueba que hay acceso a los recursos internos de Provident (señal de VPN activa):
    el portal UAT y, si `requiere_bd`/`requiere_challenger`, el SQL Server de
    botDB/Challenger_uat. Devuelve (ok, faltantes).
    """
    destinos = [("Portal UAT de Provident", urlparse(Settings.BASE_URL).hostname, 443)]
    if requiere_bd:
        botdb = _host_puerto_botdb()
        if botdb is None:
            return False, ["Variable BOTDB_SERVER no configurada en .env"]
        destinos.append(("Base de datos botDB", *botdb))
    if requiere_challenger:
        challenger = _host_puerto_challenger()
        if challenger is None:
            return False, ["Variable CHALLENGER_SERVER no configurada en .env"]
        destinos.append(("Base de datos Challenger_uat", *challenger))

    faltantes = [f"{nombre} ({host}:{puerto})" for nombre, host, puerto in destinos
                 if not _alcanzable(host, puerto)]
    return not faltantes, faltantes
