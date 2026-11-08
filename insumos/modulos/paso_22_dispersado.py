"""PASO_22_DISPERSADO: pasa el expediente al paso 22 (dispersado)."""
from typing import Optional

from insumos.contexto import ContextoVenta
from insumos.log_operacion import LogOperacion
from insumos.modulo import Modulo
from services.originacion_repository import OriginacionRepository

HOST = "PESOS_OFFER"
TABLA = "Originacion.dbo.ExpedienteCliente"
ID_PASO_DISPERSADO = 22


class Paso22Dispersado(Modulo):
    """
    UPDATE de `ExpedienteCliente.IdPaso` a 22, guardando el `IdPaso` anterior en el log.

    Precondición: solo que exista el expediente. `Cliente` puede estar en 0, así que va antes o
    después de CREAR_ID_CLIENTE; no requiere AGREEMENT ni REGISTRO_CLIENTE. Por ahora no cambia
    ningún otro dato.

    Idempotente: si el expediente ya está en el paso 22 no escribe nada.
    """

    nombre = "PASO_22_DISPERSADO"

    def __init__(self, repo: Optional[OriginacionRepository] = None):
        self.repo = repo or OriginacionRepository()

    def ejecutar(self, ctx: ContextoVenta, log: LogOperacion, dry_run: bool = False) -> ContextoVenta:
        dry_run = self._es_dry_run(dry_run, self.repo)
        ctx.cargar_expediente()
        # IdPaso se lee de la BD en cada ejecución: cambia con el avance de la venta y no vive en el contexto.
        id_paso = self.repo.leer_expediente(id_expediente=ctx.id_expediente)["IdPaso"]
        if id_paso == ID_PASO_DISPERSADO:
            print(f"PASO_22_DISPERSADO: el expediente {ctx.id_expediente} ya está en el paso 22; se omite.")
            return ctx

        # Se anota antes de escribir: si el UPDATE falla, deshacer restaura el paso que ya tenía.
        if not dry_run:
            log.escritura(self.nombre, "update", HOST, TABLA, {"IdExpedienteCliente": ctx.id_expediente},
                          anterior={"IdPaso": id_paso}, nuevo={"IdPaso": ID_PASO_DISPERSADO})
        self.repo.actualizar_id_paso(ctx.id_expediente, ID_PASO_DISPERSADO)
        return ctx
