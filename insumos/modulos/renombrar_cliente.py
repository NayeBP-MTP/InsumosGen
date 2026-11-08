"""RENOMBRAR_CLIENTE: nombre mexicano aleatorio y RFC coherente en ExpedienteCliente."""
from typing import Callable, Optional

from insumos.contexto import ContextoVenta, ErrorContexto
from insumos.log_operacion import LogOperacion
from insumos.modulo import Modulo
from services.originacion_repository import OriginacionRepository
from utils.mexican_names import MexicanNames

HOST = "PESOS_OFFER"
TABLA = "Originacion.dbo.ExpedienteCliente"


class RenombrarCliente(Modulo):
    """
    UPDATE de `NombreCliente` y `RFCCliente` del expediente. El RFC se deriva del nombre nuevo y de
    la `FechaNacimiento` actual (que no se cambia). Guarda el nombre/RFC originales en el log.

    Idempotente: si el log ya trae un renombrado de este módulo y el expediente tiene ese nombre,
    no genera otro (reanudar no cambia el nombre) y recupera las partes del nombre del log.
    """

    nombre = "RENOMBRAR_CLIENTE"

    def __init__(self, repo: Optional[OriginacionRepository] = None,
                 generar: Callable[[], dict] = MexicanNames.generar):
        self.repo = repo or OriginacionRepository()
        self._generar = generar

    def ejecutar(self, ctx: ContextoVenta, log: LogOperacion, dry_run: bool = False) -> ContextoVenta:
        dry_run = self._es_dry_run(dry_run, self.repo)
        ctx.cargar_expediente()
        if ctx.fecha_nacimiento is None:
            raise ErrorContexto(
                f"El expediente {ctx.id_expediente} no tiene FechaNacimiento: no se puede derivar el RFC."
            )

        previo = self._renombrado_previo(ctx, log)
        if previo is not None:
            ctx.persona = previo["persona"]
            print(f"RENOMBRAR_CLIENTE: el expediente {ctx.id_expediente} ya se renombró a "
                  f"'{ctx.nombre_cliente}'; se omite.")
            return ctx

        persona = self._generar()
        rfc = MexicanNames.rfc(persona, ctx.fecha_nacimiento.strftime("%d/%m/%Y"))
        nombre = persona["nombre_completo"]
        anterior = {"NombreCliente": ctx.nombre_cliente, "RFCCliente": ctx.rfc}
        nuevo = {"NombreCliente": nombre, "RFCCliente": rfc, "persona": persona}

        # Se anota antes de escribir: si la escritura falla, deshacer restaura valores que no cambiaron.
        if not dry_run:
            log.escritura(self.nombre, "update", HOST, TABLA,
                          {"IdExpedienteCliente": ctx.id_expediente}, anterior=anterior, nuevo=nuevo)
        self.repo.actualizar_nombre_rfc(ctx.id_expediente, nombre, rfc)

        ctx.nombre_cliente, ctx.rfc, ctx.persona = nombre, rfc, persona
        return ctx

    def _renombrado_previo(self, ctx: ContextoVenta, log: LogOperacion) -> Optional[dict]:
        """Último renombrado de este expediente en el log cuyo nombre sigue vigente en la BD."""
        for entrada in reversed(log.vigentes()):
            if (entrada["tipo"] == "update" and entrada["modulo"] == self.nombre
                    and entrada["llave"].get("IdExpedienteCliente") == ctx.id_expediente):
                nuevo = entrada["nuevo"]
                return nuevo if nuevo["NombreCliente"] == ctx.nombre_cliente else None
        return None
