import concurrent.futures
from dataclasses import dataclass
from typing import Optional

import pyodbc

from config.credentials import (
    DRIVER_POR_DEFECTO,
    ConnectionSettings,
    CredentialsMissing,
    CredentialStore,
)
from services.connection_tester import ConnectionTester, ResultadoConexion


@dataclass(frozen=True)
class HostBd:
    """
    Host de SQL Server que la app sabe configurar, con la base y tabla que se prueban. Los hosts
    sin bases registradas todavía (Customer_App, PaymentLink) solo prueban el inicio de sesión.
    """
    host: str
    titulo: str
    base: Optional[str] = None
    tabla: Optional[str] = None


HOSTS_BD = {
    h.host: h for h in (
        HostBd("PESOS_OFFER", "Pesos_Offer (botDB, Originacion)", "botDB", "dbo.Ofertas"),
        HostBd("CNFS", "CNFS (CNFS_uat)", "CNFS_uat", "[NFS_DBO].[Customer_Table]"),
        HostBd("CHALLENGER", "Challenger (Challenger_uat)", "Challenger_uat", "dbo.AgencyStructure"),
        HostBd("CUSTOMER_APP", "Customer_App"),
        HostBd("PAYMENTLINK", "PaymentLink"),
    )
}


def hosts_requeridos(insumo: str) -> list[str]:
    """
    Hosts que necesita una corrida: Pesos_Offer siempre (botDB y Originacion); CNFS además al
    registrar clientes (las recetas escriben en CNFS_uat); Challenger para crear estructuras de agencia.
    """
    adicionales = {"REGISTRO": ["CNFS"], "AGENCIA": ["CHALLENGER"]}
    return ["PESOS_OFFER"] + adicionales.get(insumo, [])


def hosts_sin_configurar(store: CredentialStore, hosts: list[str]) -> list[str]:
    faltantes = []
    for host in hosts:
        try:
            store.get_connection(host)
        except CredentialsMissing:
            faltantes.append(host)
    return faltantes


def probar_hosts(store: CredentialStore, hosts: list[str],
                 tester: Optional[ConnectionTester] = None) -> dict[str, ResultadoConexion]:
    """Prueba en paralelo (TCP + login + lectura de la tabla esperada) cada host ya configurado."""
    tester = tester or ConnectionTester()

    def _probar(host: str) -> ResultadoConexion:
        info = HOSTS_BD[host]
        return tester.probar(store.get_connection(host), base=info.base, tabla=info.tabla)

    if not hosts:
        return {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(hosts)) as pool:
        return dict(zip(hosts, pool.map(_probar, hosts)))


def conexion_de_formulario(store: CredentialStore, host: str, server: str, user: str,
                           password: str, driver: str) -> ConnectionSettings:
    """
    Conexión a partir de lo capturado en el diálogo. Contraseña vacía = conservar la ya guardada
    (el diálogo nunca la muestra); si no hay ninguna guardada, es un error de captura.
    """
    server, user = server.strip(), user.strip()
    if not server or not user:
        raise ValueError("Captura servidor y usuario.")
    if not password:
        try:
            password = store.get_connection(host).password
        except CredentialsMissing:
            raise ValueError("Captura la contraseña.") from None
    return ConnectionSettings(server=server, user=user, password=password,
                              driver=driver.strip() or DRIVER_POR_DEFECTO)


def drivers_sql_server() -> list[str]:
    """Drivers ODBC de SQL Server instalados, para elegirlos en el diálogo."""
    return sorted(d for d in pyodbc.drivers() if "SQL Server" in d)


def driver_sugerido(instalados: list[str]) -> str:
    if DRIVER_POR_DEFECTO in instalados or not instalados:
        return DRIVER_POR_DEFECTO
    return instalados[-1]
