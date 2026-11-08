"""ACTUALIZAR_ID_CLIENTE: propaga el Cliente del contexto a Agreement_Table y ExpedienteCliente."""
from typing import Optional

from insumos.contexto import ContextoVenta, ErrorContexto
from insumos.log_operacion import LogOperacion
from insumos.modulo import Modulo
from services.cnfs_repository import CnfsRepository
from services.originacion_repository import OriginacionRepository

HOST_CNFS = "CNFS"
TABLA_AGREEMENT = "CNFS_uat.NFS_DBO.Agreement_Table"
HOST_ORIGINACION = "PESOS_OFFER"
TABLA_EXPEDIENTE = "Originacion.dbo.ExpedienteCliente"


class ActualizarIdCliente(Modulo):
    """
    Para las recetas donde AGREEMENT corrió antes de tener número de cliente (1 y 3): pone el
    `Cliente` del contexto en `Agreement_Table.Customer_Id` (estaba en 0) y, solo si todavía no lo
    tiene, en `ExpedienteCliente.Cliente`. Requiere que AGREEMENT ya haya corrido.

    Idempotente: lo que ya tiene el valor se omite. No pisa un valor distinto de 0: si el contrato o
    el expediente ya traen otro cliente, falla sin escribir nada (las dos comprobaciones van antes
    de la primera escritura).
    """

    nombre = "ACTUALIZAR_ID_CLIENTE"

    def __init__(self, repo: Optional[OriginacionRepository] = None, repo_cnfs: Optional[CnfsRepository] = None):
        self.repo = repo or OriginacionRepository()
        self.repo_cnfs = repo_cnfs or CnfsRepository()

    def ejecutar(self, ctx: ContextoVenta, log: LogOperacion, dry_run: bool = False) -> ContextoVenta:
        dry_run = self._es_dry_run(dry_run, self.repo, self.repo_cnfs)
        ctx.cargar_expediente()
        if not ctx.cliente:
            raise ErrorContexto(
                f"El contexto no tiene Cliente (0): ejecuta CREAR_ID_CLIENTE antes de ACTUALIZAR_ID_CLIENTE."
            )

        en_agreement = self.repo_cnfs.customer_id_de_agreement(ctx.numero_contrato)
        if en_agreement is None and dry_run and "AGREEMENT" in ctx.simulado:
            en_agreement = 0  # AGREEMENT solo se simuló en esta ejecución: se da por hecho
        if en_agreement is None:
            raise ErrorContexto(
                f"El contrato {ctx.numero_contrato} no está en Agreement_Table: ejecuta AGREEMENT antes."
            )
        # El expediente se relee: ctx.cliente puede haberse puesto a mano sin escribirse en la BD.
        en_expediente = self.repo.leer_expediente(id_expediente=ctx.id_expediente)["Cliente"] or 0
        for donde, valor in (("Agreement_Table.Customer_Id", en_agreement), ("ExpedienteCliente.Cliente", en_expediente)):
            if valor not in (0, ctx.cliente):
                raise ErrorContexto(
                    f"{donde} ya trae {valor}, distinto del Cliente {ctx.cliente} del contexto: no se pisa."
                )

        if en_agreement == 0:
            if not dry_run:
                log.escritura(self.nombre, "update", HOST_CNFS, TABLA_AGREEMENT,
                              {"Agreement_Num": int(ctx.numero_contrato)},
                              anterior={"Customer_Id": 0}, nuevo={"Customer_Id": ctx.cliente})
            self.repo_cnfs.actualizar_customer_id_agreement(ctx.numero_contrato, ctx.cliente)
        else:
            print(f"ACTUALIZAR_ID_CLIENTE: el contrato {ctx.numero_contrato} ya tiene Customer_Id {ctx.cliente}.")

        if en_expediente == 0:
            if not dry_run:
                log.escritura(self.nombre, "update", HOST_ORIGINACION, TABLA_EXPEDIENTE,
                              {"IdExpedienteCliente": ctx.id_expediente},
                              anterior={"Cliente": 0}, nuevo={"Cliente": ctx.cliente})
            self.repo.actualizar_cliente(ctx.id_expediente, ctx.cliente)
        else:
            print(f"ACTUALIZAR_ID_CLIENTE: el expediente {ctx.id_expediente} ya tiene Cliente {ctx.cliente}.")
        return ctx
