"""CREAR_ID_CLIENTE: número de cliente de 13 dígitos (AAMMDD + colaborador + 02 + NNN)."""
from datetime import date
from typing import Optional

from config.settings import Settings
from insumos.contexto import ContextoVenta, ErrorContexto
from insumos.log_operacion import LogOperacion
from insumos.modulo import Modulo
from services.cnfs_repository import CnfsRepository
from services.originacion_repository import OriginacionRepository
from utils.cliente_id_allocator import ClienteIdAllocator

HOST = "PESOS_OFFER"
TABLA = "Originacion.dbo.ExpedienteCliente"
SUFIJO_UAT = "02"


def prefijo_cliente(hoy: date, colaborador: str) -> int:
    """`AAMMDD + CC + 02` (10 dígitos). `colaborador`: número de colaborador de 1 o 2 dígitos."""
    colaborador = str(colaborador or "").strip()
    if not colaborador.isdigit() or len(colaborador) > 2:
        raise ErrorContexto(
            f"Número de colaborador inválido: {colaborador!r}. Captura 1 o 2 dígitos en los Ajustes "
            f"de usuario (numero_colaborador en data/run_config.json)."
        )
    return int(f"{hoy:%y%m%d}{colaborador.zfill(2)}{SUFIJO_UAT}")


class CrearIdCliente(Modulo):
    """
    Deja el número de cliente en `ExpedienteCliente.Cliente` y en `ctx.cliente`. Si el expediente
    ya trae un `Cliente` distinto de 0 (CF, o un CN ya procesado) lo usa tal cual sin escribir.

    Consecutivo `NNN`: el mayor de hoy con el mismo prefijo en `ExpedienteCliente.Cliente` y
    `Customer_Table.Customer_Id` + 1 (`001` si no hay), reservado en SQLite para ventas paralelas.
    """

    nombre = "CREAR_ID_CLIENTE"

    def __init__(self, repo: Optional[OriginacionRepository] = None, repo_cnfs: Optional[CnfsRepository] = None,
                 allocator: Optional[ClienteIdAllocator] = None, colaborador: Optional[str] = None,
                 hoy: Optional[date] = None):
        self.repo = repo or OriginacionRepository()
        self.repo_cnfs = repo_cnfs or CnfsRepository()
        self.allocator = allocator or ClienteIdAllocator()
        self.colaborador = Settings.NUMERO_COLABORADOR if colaborador is None else colaborador
        self.hoy = hoy

    def ejecutar(self, ctx: ContextoVenta, log: LogOperacion, dry_run: bool = False) -> ContextoVenta:
        dry_run = self._es_dry_run(dry_run, self.repo)
        ctx.cargar_expediente()
        if ctx.cliente:
            print(f"CREAR_ID_CLIENTE: el expediente {ctx.id_expediente} ya tiene Cliente {ctx.cliente}; se usa tal cual.")
            return ctx

        prefijo = prefijo_cliente(self.hoy or date.today(), self.colaborador)
        maximos = [
            m % 1000 for m in (
                self.repo.max_cliente_con_prefijo(prefijo),
                self.repo_cnfs.max_customer_id_con_prefijo(prefijo),
            ) if m is not None
        ]
        nnn = self.allocator.reservar(prefijo, max(maximos, default=0), simular=dry_run)
        cliente = prefijo * 1000 + nnn

        # Se anota antes de escribir: si la escritura falla, deshacer restaura el 0 que ya estaba.
        if not dry_run:
            log.escritura(self.nombre, "update", HOST, TABLA, {"IdExpedienteCliente": ctx.id_expediente},
                          anterior={"Cliente": ctx.cliente}, nuevo={"Cliente": cliente})
        self.repo.actualizar_cliente(ctx.id_expediente, cliente)
        ctx.cliente = cliente
        return ctx
