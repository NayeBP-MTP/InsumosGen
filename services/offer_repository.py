import time
from dataclasses import dataclass, fields
from datetime import datetime
from typing import Optional

import pyodbc

from config.credentials import ConnectionSettings, CredentialStore


@dataclass
class OfferData:
    """
    Representa una fila de la tabla botDB.dbo.Ofertas.
    Ver plantilla de referencia en config/Context/offers.sql.
    """
    idOferta: int
    nombreCliente: str
    porcentajeCalidadCliente: float
    montoOferta: float
    tipoDeOferta: str  # 'RE' (Refin) o 'AD' (Agregar)
    agenciaCliente: int
    seccionCliente: str
    amOferta: str
    branchOferta: int
    descOferta: str
    semana: int
    Customer_Id: int
    Agreement_Num: int
    FechaNacimiento: str  # 'YYYY-MM-DD HH:MM:SS.fff'
    RFC: str
    Customer_Status_Code: str = "CC"
    Agreement_Status_Code: str = "AC"
    telefonoCliente1: Optional[str] = None
    telefonoCliente2: Optional[str] = None
    direccionCliente: Optional[str] = None
    idEstatusOferta: int = 1
    EstatusComentario: Optional[str] = None
    Agreement_Id: Optional[int] = None
    Agreement_Db_Id: Optional[int] = None
    Agreement_Balance: Optional[float] = None
    DireccionCobranzaCliente: Optional[str] = None
    VendidaProvidigital: Optional[str] = None
    FechaActualizacion: Optional[str] = None
    EarlySettlementRebateValue: Optional[float] = None
    Outstanding_Balance: Optional[float] = None

    def __post_init__(self):
        if not self.FechaActualizacion:
            self.FechaActualizacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


class OfferRepository:
    """
    Acceso a la tabla botDB.dbo.Ofertas usada por el flujo de Cliente Frecuente.
    La cadena de conexiÃ³n se lee de variables del almacén de credenciales (CredentialStore), nunca hardcodeada.
    """

    HOST = "PESOS_OFFER"
    BASE = "botDB"

    def __init__(self, conexion: Optional[ConnectionSettings] = None):
        self.conexion = conexion or CredentialStore().get_connection(self.HOST)
        self.database = self.BASE

    def _get_connection(self, intentos: int = 3):
        """
        Reintenta la conexión ante errores transitorios ("Named pipe provider: no se
        pudo abrir...", '08001'/'08S01'): con varias corridas en paralelo abriendo
        conexiones al mismo tiempo contra la VPN, el primer intento a veces falla
        aunque el servidor esté disponible.
        """
        connection_string = self.conexion.connection_string(self.database)
        for intento in range(1, intentos + 1):
            try:
                return pyodbc.connect(connection_string)
            except pyodbc.Error as exc:
                sqlstate = exc.args[0] if exc.args else ""
                if sqlstate not in ("08001", "08S01") or intento == intentos:
                    raise
                print(f"Conexión a botDB falló (intento {intento}/{intentos}, {sqlstate}), reintentando…")
                time.sleep(2 * intento)

    def test_connection(self) -> bool:
        """Verifica que la conexiÃ³n a botDB pueda establecerse. Ãštil para diagnÃ³stico."""
        with self._get_connection() as conn:
            conn.execute("SELECT 1").fetchone()
        return True

    def insert_offer(self, offer: OfferData) -> None:
        """Inserta una fila en dbo.Ofertas a partir de un OfferData."""
        columns = [f.name for f in fields(offer)]
        values = [getattr(offer, name) for name in columns]

        columns_sql = ", ".join(f"[{name}]" for name in columns)
        placeholders_sql = ", ".join("?" for _ in columns)

        query = f"INSERT INTO [dbo].[Ofertas] ({columns_sql}) VALUES ({placeholders_sql})"

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, values)
            conn.commit()

    def offer_exists(self, id_oferta: int) -> bool:
        """Comprueba si ya existe una oferta con ese idOferta (para evitar duplicados)."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT 1 FROM [dbo].[Ofertas] WHERE [idOferta] = ?", (id_oferta,)
            ).fetchone()
        return row is not None

    def get_max_semana(self) -> int:
        """Semana (AAAASS) mÃ¡s reciente presente en dbo.Ofertas."""
        with self._get_connection() as conn:
            fila = conn.execute("SELECT MAX([semana]) FROM [dbo].[Ofertas]").fetchone()
        return int(fila[0]) if fila and fila[0] is not None else 0

    def get_offer(self, id_oferta: int):
        """Devuelve la fila completa de dbo.Ofertas como dict, o None si no existe."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM [dbo].[Ofertas] WHERE [idOferta] = ?", (id_oferta,))
            row = cursor.fetchone()
            if row is None:
                return None
            return dict(zip([c[0] for c in cursor.description], row))

    # Campos que se comparan entre lo insertado y lo leÃ­do de la BD
    _CAMPOS_VERIFICACION = (
        "nombreCliente", "agenciaCliente", "branchOferta", "montoOferta",
        "idEstatusOferta", "Customer_Id", "descOferta", "semana",
    )

    @staticmethod
    def _normalizar(valor):
        if isinstance(valor, str):
            return valor.strip()
        if valor is None:
            return None
        try:
            return float(valor)  # int / Decimal / float
        except (TypeError, ValueError):
            return str(valor).strip()

    def verify_offer_inserted(self, offer: OfferData, retries: int = 5, delay: float = 2.0) -> dict:
        """
        Lee de la BD (conexiÃ³n nueva) la oferta reciÃ©n insertada y comprueba que exista y
        que sus campos clave coincidan con lo insertado. Reintenta `retries` veces con
        `delay` segundos entre intentos por si hay retraso de escritura/replicaciÃ³n.
        Devuelve la fila leÃ­da; lanza AssertionError si no aparece o no coincide.
        """
        ultimo_error = None
        for intento in range(1, retries + 1):
            fila = self.get_offer(offer.idOferta)
            if fila is None:
                ultimo_error = f"idOferta={offer.idOferta} no existe en dbo.Ofertas"
            else:
                diferencias = {
                    campo: (getattr(offer, campo), fila.get(campo))
                    for campo in self._CAMPOS_VERIFICACION
                    if self._normalizar(getattr(offer, campo)) != self._normalizar(fila.get(campo))
                }
                if not diferencias:
                    return fila
                ultimo_error = (
                    f"idOferta={offer.idOferta} existe pero difiere en {diferencias} "
                    "(insertado, leÃ­do)"
                )
            if intento < retries:
                time.sleep(delay)
        raise AssertionError(
            f"La oferta no quedÃ³ correctamente insertada en botDB tras {retries} intentos: "
            f"{ultimo_error}"
        )

    def delete_offer(self, id_oferta: int) -> None:
        """Elimina una oferta por idOferta. Uso previsto: limpieza de datos de prueba."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM [dbo].[Ofertas] WHERE [idOferta] = ?", (id_oferta,))
            conn.commit()


if __name__ == "__main__":
    repo = OfferRepository()
    ok = repo.test_connection()
    print("ConexiÃ³n a botDB exitosa" if ok else "No se pudo conectar a botDB")
