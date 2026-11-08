"""AGREEMENT: alta del contrato en CNFS_uat.NFS_DBO.Agreement_Table."""
from datetime import date
from typing import Optional

from insumos import plantillas
from insumos.contexto import ContextoVenta
from insumos.log_operacion import LogOperacion
from insumos.modulo import Modulo
from services.cnfs_repository import CnfsRepository
from utils.offer_id_allocator import OfferIdAllocator

HOST = "CNFS"
TABLA = "CNFS_uat.NFS_DBO.Agreement_Table"


def construir_agreement(ctx: ContextoVenta, hoy: date) -> dict:
    """
    Plantilla de Agreement_Table con los valores de la venta (ver CREAR_CLIENTES.md, módulo
    AGREEMENT). El resto de columnas conserva el valor de la plantilla. Requiere el contexto con
    expediente y montos cargados.
    """
    m = ctx.montos
    fecha = f"{hoy:%Y-%m-%d} 00:00:00"
    monto, primer_pago, pago_semanal = round(m.monto_prestamo, 2), round(m.primer_pago, 2), round(m.pago_semanal, 2)
    valores = dict(plantillas.AGREEMENT)
    valores.update({
        "Absolute_Arrears": 0,
        "Actual_Paid_Up_Date": fecha,
        "Actual_Paid_Up_Week": OfferIdAllocator.calcular_semana(hoy),
        "Agreement_Num": int(ctx.numero_contrato),
        "Agreement_Status_Code": "AC",
        "Creation_Date": fecha,
        "Customer_Id": ctx.cliente or 0,
        "Final_Instalment_Value": pago_semanal,
        "Total_Amount_Payable": monto,
        "Settlement_Balance": monto,
        "Last_Updated_Datetime": fecha,
        "First_Instalment_Value_At_Issue": primer_pago,
        "Regular_Instalment_Value_At_Issue": pago_semanal,
        "Total_Amount_Payable_At_Issue": monto,
        # alineados con la venta (aprobado)
        "First_Instalment_Value": primer_pago,
        "Regular_Instalment_Value": pago_semanal,
        "Final_Instalment_Value_At_Issue": pago_semanal,
        "Issue_Value": monto,
        "Outstanding_Balance": monto,
    })
    return valores


class Agreement(Modulo):
    """
    INSERT en `Agreement_Table`. Sin parámetros: `Customer_Id` toma el `Cliente` del contexto si ya
    existe y `0` si no (CN antes de CREAR_ID_CLIENTE; ACTUALIZAR_ID_CLIENTE lo propaga después).

    Idempotente: si el contrato ya está en `Agreement_Table` no inserta nada.
    """

    nombre = "AGREEMENT"

    def __init__(self, repo: Optional[CnfsRepository] = None, hoy: Optional[date] = None):
        self.repo = repo or CnfsRepository()
        self.hoy = hoy

    def ejecutar(self, ctx: ContextoVenta, log: LogOperacion, dry_run: bool = False) -> ContextoVenta:
        dry_run = self._es_dry_run(dry_run, self.repo)
        ctx.cargar_montos()  # también carga el expediente
        if self.repo.agreement_existe(ctx.numero_contrato):
            print(f"AGREEMENT: el contrato {ctx.numero_contrato} ya está en Agreement_Table; se omite.")
            return ctx

        valores = construir_agreement(ctx, self.hoy or date.today())
        # Se anota antes de escribir: si el INSERT falla, deshacer borra una fila que no existe.
        if not dry_run:
            log.escritura(self.nombre, "insert", HOST, TABLA, {"Agreement_Num": valores["Agreement_Num"]},
                          nuevo={"Agreement_Num": valores["Agreement_Num"], "Customer_Id": valores["Customer_Id"],
                                 "Issue_Value": valores["Issue_Value"]})
        self.repo.insertar_agreement(valores)
        return ctx
