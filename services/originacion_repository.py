from datetime import datetime
from typing import Optional

from services.db import SqlServerRepository


class OriginacionRepository(SqlServerRepository):
    """
    Acceso a Originacion.dbo.ExpedienteCliente (host Pesos_Offer, variables PESOS_OFFER_*).
    Hoy solo lectura de ventas; las escrituras de los módulos de insumo se agregan en el paso 2.3.
    """

    def __init__(self, dry_run: bool = False):
        super().__init__("Originacion", dry_run=dry_run)

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
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT IdExpedienteCliente, NombreCliente, Agencia, Cliente, IdOferta, IdPaso, "
                "numeroContrato, folioContrato, FechaFinalizacion "
                "FROM [dbo].[ExpedienteCliente] "
                "WHERE idAgente = ? AND IdOferta = ? AND FechaFinalizacion >= ? "
                "ORDER BY FechaFinalizacion DESC",
                (id_agente, id_oferta, desde),
            )
            columnas = [c[0] for c in cursor.description]
            return [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
