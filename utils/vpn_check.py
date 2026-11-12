import socket
from urllib.parse import urlparse

from config.credentials import CredentialsMissing, CredentialStore
from config.settings import Settings
from services.connection_tester import host_puerto

TIMEOUT_SEG = 4


def _destino_bd(host: str):
    r"""
    (destino, faltante) del SQL Server de `host` en el almacén de credenciales. `destino` es
    (host, puerto) o None si es una instancia con nombre sin puerto (se valida al iniciar sesión);
    `faltante` es el motivo si el host no está configurado.
    """
    try:
        server = CredentialStore().get_connection(host).server
    except CredentialsMissing:
        return None, f"Host {host} sin configurar: captúralo en 'Conexiones y estrellas'"
    return host_puerto(server), None


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
    for nombre, host, requerida in (("Base de datos botDB", "PESOS_OFFER", requiere_bd),
                                    ("Base de datos Challenger_uat", "CHALLENGER", requiere_challenger)):
        if not requerida:
            continue
        destino, faltante = _destino_bd(host)
        if faltante:
            return False, [faltante]
        if destino:
            destinos.append((nombre, *destino))

    faltantes = [f"{nombre} ({host}:{puerto})" for nombre, host, puerto in destinos
                 if not _alcanzable(host, puerto)]
    return not faltantes, faltantes
