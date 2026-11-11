from pathlib import Path
from typing import Optional

from config.credentials import ConnectionSettings, CredentialStore


# Prefijo de las variables del .env -> host del almacén. BOTDB_* es el nombre histórico de
# PESOS_OFFER; el resto coincide con el host.
PREFIJOS_HOST = {
    "BOTDB": "PESOS_OFFER",
    "PESOS_OFFER": "PESOS_OFFER",
    "CHALLENGER": "CHALLENGER",
    "CNFS": "CNFS",
    "CUSTOMER_APP": "CUSTOMER_APP",
    "PAYMENTLINK": "PAYMENTLINK",
}


def leer_env(ruta: Path) -> dict[str, str]:
    """Pares CLAVE=VALOR de un .env (ignora comentarios, líneas vacías, `export` y comillas)."""
    valores = {}
    for linea in Path(ruta).read_text(encoding="utf-8-sig").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, _, valor = linea.partition("=")
        clave = clave.removeprefix("export ").strip()
        valor = valor.strip()
        if len(valor) >= 2 and valor[0] == valor[-1] and valor[0] in "\"'":
            valor = valor[1:-1]
        valores[clave] = valor
    return valores


def importar_env(store: CredentialStore, ruta: Path) -> list[str]:
    """
    Migra al almacén los hosts de un .env legado (una sola vez: nunca pisa un host que ya esté
    configurado). Solo importa los que tienen servidor, usuario y contraseña. Devuelve los hosts
    importados, sin repetir.
    """
    ya_configurados = set(store.list_hosts())
    valores = leer_env(ruta)
    importados = []
    for prefijo, host in PREFIJOS_HOST.items():
        if host in ya_configurados:
            continue
        server = valores.get(f"{prefijo}_SERVER", "")
        user = valores.get(f"{prefijo}_USER", "")
        password = valores.get(f"{prefijo}_PASSWORD", "")
        if not (server and user and password):
            continue
        driver: Optional[str] = valores.get(f"{prefijo}_DRIVER") or None
        store.save_connection(host, ConnectionSettings(server=server, user=user, password=password,
                                                       driver=driver or ""))
        if host not in importados:
            importados.append(host)
    return importados
