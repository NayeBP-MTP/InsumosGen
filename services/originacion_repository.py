from datetime import datetime
from typing import Optional

from services.db import SqlServerRepository

COLUMNAS_EXPEDIENTE = (
    "IdExpedienteCliente, numeroContrato, folioContrato, NombreCliente, RFCCliente, "
    "DomicilioCliente, FechaNacimiento, Agencia, Cliente, IdOferta, IdPaso, idAgente, "
    "FechaFinalizacion"
)
COLUMNAS_MONTOS = (
    "IdExpedienteOferta, IdExpedienteCliente, MontoTotal, MontoTotalSeguro, PrimerPagoSemanal, "
    "PrimerPagoSemanalSeguro, PagoSubsecuente, PagoSubsecuenteSeguro"
)


class OriginacionRepository(SqlServerRepository):
    """
    Acceso a Originacion.dbo.ExpedienteCliente y ExpedienteOferta (host Pesos_Offer, variables
    PESOS_OFFER_*). Implementa la `FuenteExpediente` que usa `ContextoVenta`.

    Nota: `ExpedienteCliente.IdExpedienteOferta` viene NULL en todas las filas (comprobado en UAT);
    el vínculo real es `ExpedienteOferta.IdExpedienteCliente`.
    """

    def __init__(self, dry_run: bool = False):
        super().__init__("Originacion", dry_run=dry_run)

    def _consultar(self, sql: str, params=()) -> list:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            columnas = [c[0] for c in cursor.description]
            return [dict(zip(columnas, fila)) for fila in cursor.fetchall()]

    # --- lecturas ---

    def hora_servidor(self) -> datetime:
        """Hora del servidor SQL (SYSDATETIME): la misma con la que se escribe FechaFinalizacion."""
        with self._get_connection() as conn:
            return conn.execute("SELECT SYSDATETIME()").fetchone()[0]

    def buscar_venta_finalizada(
        self, id_agente: int, desde: datetime, id_oferta: int = 0
    ) -> list:
        """
        Expedientes del vendedor `id_agente` (estrella) finalizados desde `desde` (hora del
        servidor), del más reciente al más antiguo. `id_oferta`: el de la oferta CF, o 0 en CN.
        """
        return self._consultar(
            f"SELECT {COLUMNAS_EXPEDIENTE} FROM [dbo].[ExpedienteCliente] "
            "WHERE idAgente = ? AND IdOferta = ? AND FechaFinalizacion >= ? "
            "ORDER BY FechaFinalizacion DESC",
            (id_agente, id_oferta, desde),
        )

    def leer_expediente(self, numero_contrato=None, id_expediente=None) -> dict:
        """Expediente por `numeroContrato` (criterio más seguro) o `IdExpedienteCliente`."""
        if numero_contrato:
            filas = self._consultar(
                f"SELECT {COLUMNAS_EXPEDIENTE} FROM [dbo].[ExpedienteCliente] "
                "WHERE numeroContrato = ?", (str(numero_contrato),),
            )
            descripcion = f"numeroContrato={numero_contrato}"
        elif id_expediente:
            filas = self._consultar(
                f"SELECT {COLUMNAS_EXPEDIENTE} FROM [dbo].[ExpedienteCliente] "
                "WHERE IdExpedienteCliente = ?", (int(id_expediente),),
            )
            descripcion = f"IdExpedienteCliente={id_expediente}"
        else:
            raise ValueError("Falta numero_contrato o id_expediente.")
        if not filas:
            raise LookupError(f"No hay expediente con {descripcion} en Originacion.")
        if len(filas) > 1:
            raise LookupError(f"{len(filas)} expedientes con {descripcion}; se esperaba uno.")
        return filas[0]

    def buscar_por_nombre_ine(self, nombre: str, desde: datetime, id_agente: Optional[int] = None) -> list:
        """
        Respaldo para localizar una venta sin contrato: nombre de la INE + FechaFinalizacion.
        Ojo: `FechaFinalizacion` es datetime (redondea a 3.3 ms); pasar un `desde` igual a la hora
        exacta de un expediente puede dejarlo fuera. Usa la hora de inicio de la venta.
        """
        sql = (
            f"SELECT {COLUMNAS_EXPEDIENTE} FROM [dbo].[ExpedienteCliente] "
            "WHERE NombreCliente = ? AND FechaFinalizacion >= ?"
        )
        params = [nombre, desde]
        if id_agente is not None:
            sql += " AND idAgente = ?"
            params.append(id_agente)
        return self._consultar(sql + " ORDER BY FechaFinalizacion DESC", params)

    def leer_montos(self, id_expediente: int) -> dict:
        """Montos de la oferta del expediente (la más reciente si hubiera varias)."""
        filas = self._consultar(
            f"SELECT TOP 1 {COLUMNAS_MONTOS} FROM [dbo].[ExpedienteOferta] "
            "WHERE IdExpedienteCliente = ? ORDER BY IdExpedienteOferta DESC", (int(id_expediente),),
        )
        if not filas:
            raise LookupError(f"El expediente {id_expediente} no tiene fila en ExpedienteOferta.")
        return filas[0]

    def max_cliente_con_prefijo(self, prefijo: int) -> Optional[int]:
        """Mayor `Cliente` de 13 dígitos que empieza con `prefijo` (11 dígitos), o None."""
        base = int(prefijo) * 100
        fila = self._consultar(
            "SELECT MAX(Cliente) AS maximo FROM [dbo].[ExpedienteCliente] "
            "WHERE Cliente BETWEEN ? AND ?", (base, base + 99),
        )[0]
        return fila["maximo"]

    # --- escrituras (con dry_run) ---

    def actualizar_nombre_rfc(self, id_expediente: int, nombre: str, rfc: str) -> None:
        self._escribir(
            "UPDATE [dbo].[ExpedienteCliente] SET NombreCliente = ?, RFCCliente = ? "
            "WHERE IdExpedienteCliente = ?", (nombre, rfc, int(id_expediente)),
        )

    def actualizar_cliente(self, id_expediente: int, cliente: int) -> None:
        self._escribir(
            "UPDATE [dbo].[ExpedienteCliente] SET Cliente = ? WHERE IdExpedienteCliente = ?",
            (int(cliente), int(id_expediente)),
        )

    def actualizar_id_paso(self, id_expediente: int, id_paso: int) -> None:
        self._escribir(
            "UPDATE [dbo].[ExpedienteCliente] SET IdPaso = ? WHERE IdExpedienteCliente = ?",
            (int(id_paso), int(id_expediente)),
        )
