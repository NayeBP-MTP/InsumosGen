import os
import socket
from urllib.parse import urlparse

from dotenv import load_dotenv

from config.databases import CHALLENGER, PESOS_OFFER
from config.settings import Settings

load_dotenv()

TIMEOUT_SEG = 4


def _host_puerto(host_bd: str):
    r"""
    Host y puerto de `<HOST_BD>_SERVER` del .env (formatos 'host', 'host,1433', 'host\instancia').
    `host_bd` es el host de base de datos (ver config/databases.py), p. ej. PESOS_OFFER.
    """
    server = os.environ.get(f"{host_bd}_SERVER", "").strip()
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
        botdb = _host_puerto(PESOS_OFFER)
        if botdb is None:
            return False, [f"Variable {PESOS_OFFER}_SERVER no configurada en .env"]
        destinos.append(("Base de datos botDB", *botdb))
    if requiere_challenger:
        challenger = _host_puerto(CHALLENGER)
        if challenger is None:
            return False, [f"Variable {CHALLENGER}_SERVER no configurada en .env"]
        destinos.append(("Base de datos Challenger_uat", *challenger))

    faltantes = [f"{nombre} ({host}:{puerto})" for nombre, host, puerto in destinos
                 if not _alcanzable(host, puerto)]
    return not faltantes, faltantes
