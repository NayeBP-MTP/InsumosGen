import concurrent.futures
import socket
import ssl
import urllib.error
import urllib.request
from urllib.parse import urlparse

from config.credentials import CredentialsMissing
from config.settings import Settings
from services.connection_tester import ConnectionTester
from services.db import SqlServerRepository

TIMEOUT_SEG = 4
TIMEOUT_HTTP_SEG = 10


def _motivo_red(exc: BaseException, host: str) -> str:
    """Traduce un error de red a la causa real (DNS, timeout, rechazo…) en lugar de un 'no alcanzable'."""
    if isinstance(exc, urllib.error.URLError) and isinstance(exc.reason, BaseException):
        exc = exc.reason
    if isinstance(exc, socket.gaierror):
        return (f"el nombre '{host}' no se resuelve (DNS). Sin la VPN o el DNS interno el equipo no conoce ese "
                f"servidor. Detalle: {exc}")
    if isinstance(exc, (socket.timeout, TimeoutError)):
        return (f"no hubo respuesta en {TIMEOUT_SEG}s (timeout). Hay ruta de red pero algo la bloquea (firewall, "
                "VPN sin acceso a esa red) o el servidor está caído.")
    if isinstance(exc, ConnectionRefusedError):
        return "conexión rechazada: el servidor responde pero no hay nada escuchando en ese puerto."
    if isinstance(exc, ssl.SSLError):
        return f"falló el certificado/TLS ({exc}); un proxy o inspección de red puede estar interceptando."
    if isinstance(exc, OSError):
        return f"error de red {exc.errno}: {exc.strerror or exc}"
    return f"{type(exc).__name__}: {exc}"


def _problema_tcp(host: str, puerto: int):
    """None si el puerto responde; si no, la causa concreta."""
    try:
        with socket.create_connection((host, puerto), timeout=TIMEOUT_SEG):
            return None
    except OSError as exc:
        return _motivo_red(exc, host)


def _alcanzable(host: str, puerto: int) -> bool:
    return _problema_tcp(host, puerto) is None


def _problema_portal(url: str):
    """
    Pide la URL del portal por HTTPS (como lo haría el navegador, con el proxy del sistema). Cualquier
    respuesta HTTP < 500 cuenta como portal accesible; 5xx o un fallo de red se reportan con su causa.
    """
    host = urlparse(url).hostname
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT_HTTP_SEG):
            return None
    except urllib.error.HTTPError as exc:
        if exc.code < 500:
            return None
        return f"el portal respondió con error HTTP {exc.code} ({exc.reason}); el ambiente UAT está caído o fallando."
    except Exception as exc:  # noqa: BLE001 (se traduce a un mensaje)
        return _motivo_red(exc, host)


def _problema_base(base: str):
    """None si se puede iniciar sesión y ejecutar SELECT 1 en `base`; si no, la causa concreta."""
    try:
        conexion = SqlServerRepository(base).credenciales
    except CredentialsMissing as exc:
        return str(exc)
    resultado = ConnectionTester().probar(conexion, base=base)
    return None if resultado.ok else resultado.mensaje


def verificar_vpn(requiere_bd: bool = True, requiere_challenger: bool = False,
                  requiere_originacion: bool = False, requiere_cnfs: bool = False):
    """
    Comprueba que hay acceso a lo que la ejecución va a usar: el portal UAT y, según lo pedido, las bases
    botDB, Originacion, CNFS_uat y Challenger_uat. No se queda en "puerto abierto": entra al portal y
    abre sesión en cada base, y reporta la causa real de cada falla (DNS, timeout, credenciales, driver…).
    Devuelve (ok, problemas): cada problema es "Qué falla: por qué".
    """
    comprobaciones = [("Portal UAT de Provident", lambda: _problema_portal(Settings.BASE_URL))]
    bases = [("botDB", requiere_bd), ("Originacion", requiere_originacion), ("CNFS_uat", requiere_cnfs),
             ("Challenger_uat", requiere_challenger)]
    for base, requerida in bases:
        if requerida:
            comprobaciones.append((f"Base de datos {base}", lambda b=base: _problema_base(b)))

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(comprobaciones)) as pool:
        resultados = list(pool.map(lambda c: c[1](), comprobaciones))
    problemas = [f"{nombre}: {motivo}" for (nombre, _), motivo in zip(comprobaciones, resultados) if motivo]
    return not problemas, problemas
