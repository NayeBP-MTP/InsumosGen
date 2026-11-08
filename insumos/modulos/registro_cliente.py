"""REGISTRO_CLIENTE: alta en Customer_Table y Customer_Address_Table (una sola transacción)."""
from datetime import date, timedelta
from typing import Optional

from insumos import plantillas
from insumos.contexto import ContextoVenta, ErrorContexto
from insumos.log_operacion import LogOperacion
from insumos.modulo import Modulo
from services.cnfs_repository import CnfsRepository
from utils.offer_id_allocator import OfferIdAllocator

HOST = "CNFS"
TABLA_CUSTOMER = "CNFS_uat.NFS_DBO.Customer_Table"
TABLA_ADDRESS = "CNFS_uat.NFS_DBO.Customer_Address_Table"


def persona_del_log(log: LogOperacion, id_expediente: int) -> Optional[dict]:
    """Partes del nombre que dejó RENOMBRAR_CLIENTE en el log (para reanudar en otro proceso)."""
    for entrada in reversed(log.vigentes()):
        if (entrada["tipo"] == "update" and entrada["modulo"] == "RENOMBRAR_CLIENTE"
                and entrada["llave"].get("IdExpedienteCliente") == id_expediente):
            return entrada["nuevo"].get("persona")
    return None


def construir_customer(ctx: ContextoVenta, persona: dict, hoy: date) -> dict:
    """Plantilla de Customer_Table con los valores de la venta (ver CREAR_CLIENTES.md)."""
    segmento = int(str(ctx.agencia)[:4])
    valores = dict(plantillas.CUSTOMER)
    valores.update({
        "Customer_Id": ctx.cliente,
        "Agency_Id": ctx.agencia,
        "Agency_Segment_Db_Id": segmento,
        "Agency_Segment_Id": segmento,
        "Birth_Date": ctx.fecha_nacimiento.date().isoformat(),
        "Creation_Date": hoy.isoformat(),
        "Creation_Week": OfferIdAllocator.calcular_semana(hoy),
        "Display_Name": ctx.nombre_cliente,
        "Disposable_Income_Date": (hoy + timedelta(days=7)).isoformat(),
        "First_Agreement_Creation_Date": (hoy + timedelta(days=7)).isoformat(),
        "Forename": persona["nombre"],
        "Surname": f"{persona['apellido_paterno']} {persona['apellido_materno']}",
        "Customer_Status_Code": ctx.status_code,
    })
    if ctx.domicilio:
        valores["Nearest_Relative_Address"] = ctx.domicilio
    return valores


def construir_direccion(ctx: ContextoVenta) -> dict:
    """Plantilla de Customer_Address_Table con el cliente y su domicilio."""
    valores = dict(plantillas.CUSTOMER_ADDRESS)
    valores["Customer_Id"] = ctx.cliente
    if ctx.domicilio:
        valores["Full_Address"] = ctx.domicilio
    return valores


class RegistroCliente(Modulo):
    """
    Registra al cliente en CNFS. Sin parámetros: `Customer_Status_Code` sale del tipo de venta del
    contexto (`CC` = CF, `AA` = CN). Requiere un `Cliente` distinto de 0 (CREAR_ID_CLIENTE o CF) y
    que el nombre ya esté renombrado (`ctx.persona`, o el log de RENOMBRAR_CLIENTE al reanudar).

    Idempotente: si el cliente ya está en `Customer_Table` no inserta nada.
    """

    nombre = "REGISTRO_CLIENTE"

    def __init__(self, repo: Optional[CnfsRepository] = None, hoy: Optional[date] = None):
        self.repo = repo or CnfsRepository()
        self.hoy = hoy

    def ejecutar(self, ctx: ContextoVenta, log: LogOperacion, dry_run: bool = False) -> ContextoVenta:
        dry_run = self._es_dry_run(dry_run, self.repo)
        ctx.cargar_expediente()
        if not ctx.cliente:
            raise ErrorContexto(
                f"El expediente {ctx.id_expediente} no tiene Cliente (0): ejecuta CREAR_ID_CLIENTE "
                f"antes de REGISTRO_CLIENTE."
            )
        persona = ctx.persona or persona_del_log(log, ctx.id_expediente)
        if not persona:
            raise ErrorContexto(
                f"No hay las partes del nombre de '{ctx.nombre_cliente}' (Forename/Surname): ejecuta "
                f"RENOMBRAR_CLIENTE antes de REGISTRO_CLIENTE."
            )
        if self.repo.customer_existe(ctx.cliente):
            print(f"REGISTRO_CLIENTE: el cliente {ctx.cliente} ya está en Customer_Table; se omite.")
            return ctx

        hoy = self.hoy or date.today()
        customer, direccion = construir_customer(ctx, persona, hoy), construir_direccion(ctx)
        # Se anotan antes de escribir; en orden de alta (deshacer los recorre al revés: dirección y luego cliente).
        if not dry_run:
            log.escritura(self.nombre, "insert", HOST, TABLA_CUSTOMER, {"Customer_Id": ctx.cliente},
                          nuevo={"Customer_Id": ctx.cliente, "Customer_Status_Code": ctx.status_code,
                                 "Display_Name": ctx.nombre_cliente})
            log.escritura(self.nombre, "insert", HOST, TABLA_ADDRESS,
                          {"Customer_Id": ctx.cliente, "Customer_Address_Db_Id": direccion["Customer_Address_Db_Id"]},
                          nuevo={"Customer_Id": ctx.cliente})
        self.repo.insertar_cliente_y_direccion(customer, direccion)
        return ctx
