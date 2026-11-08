"""Pruebas unitarias (sin BD) del módulo REGISTRO_CLIENTE."""
from datetime import date, datetime

import pytest

from insumos import plantillas
from insumos.contexto import ContextoVenta, ErrorContexto
from insumos.log_operacion import LogOperacion
from insumos.modulos.registro_cliente import (
    RegistroCliente, construir_customer, construir_direccion, persona_del_log)
from services.cnfs_repository import CnfsRepository
from services.originacion_repository import OriginacionRepository

HOY = date(2026, 11, 7)
PERSONA = {"nombre": "JOSÉ LUIS", "apellido_paterno": "PÉREZ", "apellido_materno": "RODRÍGUEZ",
           "nombre_completo": "JOSÉ LUIS PÉREZ RODRÍGUEZ"}


class Fuente(OriginacionRepository):
    def __init__(self, cliente=2611070402001, domicilio="CALLE 1 COL CENTRO"):
        super().__init__(dry_run=True)
        self.cliente, self.domicilio = cliente, domicilio

    def leer_expediente(self, numero_contrato=None, id_expediente=None):
        return {"IdExpedienteCliente": 7329, "numeroContrato": "240021110", "Agencia": 2075000000335,
                "Cliente": self.cliente, "NombreCliente": PERSONA["nombre_completo"], "RFCCliente": "PERJ960903AB1",
                "DomicilioCliente": self.domicilio, "FechaNacimiento": datetime(1996, 9, 3, 5, 0)}


class RepoCnfs(CnfsRepository):
    def __init__(self, existe=False, dry_run=True):
        super().__init__(dry_run=dry_run)
        self.existe, self.transacciones = existe, []

    def customer_existe(self, customer_id):
        return self.existe

    def _escribir_transaccion(self, sentencias):
        sentencias = [(s, tuple(p)) for s, p in sentencias]
        if self.dry_run:
            self.dry_run_log.extend(sentencias)  # igual que SqlServerRepository: sentencias planas
        else:
            self.transacciones.append(sentencias)


def _ctx(tipo="CN", persona=PERSONA, **kw):
    ctx = ContextoVenta(tipo=tipo, numero_contrato="240021110", fuente=Fuente(**kw))
    ctx.persona = persona
    return ctx.cargar_expediente()


def test_customer_conserva_las_155_columnas_y_orden():
    v = construir_customer(_ctx(), PERSONA, HOY)
    assert list(v) == list(plantillas.CUSTOMER) and len(v) == 155


def test_valores_de_customer():
    v = construir_customer(_ctx(), PERSONA, HOY)
    assert v["Customer_Id"] == 2611070402001 and v["Agency_Id"] == 2075000000335
    assert v["Agency_Segment_Db_Id"] == v["Agency_Segment_Id"] == 2075
    assert v["Birth_Date"] == "1996-09-03" and v["Creation_Date"] == "2026-11-07"
    assert v["Creation_Week"] == 202645
    assert v["Disposable_Income_Date"] == v["First_Agreement_Creation_Date"] == "2026-11-14"
    assert v["Display_Name"] == "JOSÉ LUIS PÉREZ RODRÍGUEZ"
    assert v["Forename"] == "JOSÉ LUIS" and v["Surname"] == "PÉREZ RODRÍGUEZ"
    assert v["Nearest_Relative_Address"] == "CALLE 1 COL CENTRO"


def test_status_code_cc_en_cf_y_aa_en_cn():
    assert construir_customer(_ctx("CF"), PERSONA, HOY)["Customer_Status_Code"] == "CC"
    assert construir_customer(_ctx("CN"), PERSONA, HOY)["Customer_Status_Code"] == "AA"


def test_sin_domicilio_se_conserva_el_de_la_plantilla():
    ctx = _ctx(domicilio=None)
    assert construir_customer(ctx, PERSONA, HOY)["Nearest_Relative_Address"] == plantillas.CUSTOMER["Nearest_Relative_Address"]
    assert construir_direccion(ctx)["Full_Address"] == plantillas.CUSTOMER_ADDRESS["Full_Address"]


def test_direccion():
    v = construir_direccion(_ctx())
    assert list(v) == list(plantillas.CUSTOMER_ADDRESS) and len(v) == 27
    assert v["Customer_Id"] == 2611070402001 and v["Full_Address"] == "CALLE 1 COL CENTRO"


def test_el_resto_de_columnas_queda_como_la_plantilla():
    v = construir_customer(_ctx(), PERSONA, HOY)
    tocadas = {"Customer_Id", "Agency_Id", "Agency_Segment_Db_Id", "Agency_Segment_Id", "Birth_Date",
               "Creation_Date", "Creation_Week", "Display_Name", "Disposable_Income_Date",
               "First_Agreement_Creation_Date", "Forename", "Surname", "Nearest_Relative_Address",
               "Customer_Status_Code"}
    assert all(v[c] == p for c, p in plantillas.CUSTOMER.items() if c not in tocadas)


def test_plantillas_intactas():
    antes = dict(plantillas.CUSTOMER), dict(plantillas.CUSTOMER_ADDRESS)
    construir_customer(_ctx(), PERSONA, HOY), construir_direccion(_ctx())
    assert (plantillas.CUSTOMER, plantillas.CUSTOMER_ADDRESS) == antes


def test_dry_run_deja_las_dos_altas_en_una_transaccion_y_no_loguea(tmp_path):
    repo, log = RepoCnfs(), LogOperacion("x", tmp_path)
    RegistroCliente(repo=repo, hoy=HOY).ejecutar(_ctx(), log, dry_run=True)
    assert [s.split("]")[1].strip(" .[") for s, _ in repo.dry_run_log] == ["Customer_Table", "Customer_Address_Table"]
    assert log.entradas() == []


def test_escritura_real_loguea_cliente_y_direccion_en_orden(tmp_path):
    repo, log = RepoCnfs(dry_run=False), LogOperacion("240021110", tmp_path)
    RegistroCliente(repo=repo, hoy=HOY).ejecutar(_ctx(), log)
    assert len(repo.transacciones) == 1
    tablas = [e["tabla"] for e in log.entradas() if e["tipo"] == "insert"]
    assert tablas == ["CNFS_uat.NFS_DBO.Customer_Table", "CNFS_uat.NFS_DBO.Customer_Address_Table"]
    # deshacer: primero la dirección y luego el cliente
    assert [e["tabla"].split(".")[-1] for e in log.escrituras_para_deshacer()] == [
        "Customer_Address_Table", "Customer_Table"]


def test_sin_cliente_pide_crear_id_antes(tmp_path):
    repo = RepoCnfs()
    with pytest.raises(ErrorContexto, match="CREAR_ID_CLIENTE"):
        RegistroCliente(repo=repo, hoy=HOY).ejecutar(_ctx(cliente=0), LogOperacion("x", tmp_path), dry_run=True)
    assert repo.dry_run_log == []


def test_sin_persona_pide_renombrar_antes(tmp_path):
    with pytest.raises(ErrorContexto, match="RENOMBRAR_CLIENTE"):
        RegistroCliente(repo=RepoCnfs(), hoy=HOY).ejecutar(_ctx(persona=None), LogOperacion("x", tmp_path), dry_run=True)


def test_recupera_la_persona_del_log_al_reanudar(tmp_path):
    log = LogOperacion("240021110", tmp_path)
    log.escritura("RENOMBRAR_CLIENTE", "update", "PESOS_OFFER", "Originacion.dbo.ExpedienteCliente",
                  {"IdExpedienteCliente": 7329}, anterior={"NombreCliente": "VIEJO"},
                  nuevo={"NombreCliente": PERSONA["nombre_completo"], "RFCCliente": "R", "persona": PERSONA})
    assert persona_del_log(log, 7329) == PERSONA and persona_del_log(log, 1) is None
    repo = RepoCnfs()
    RegistroCliente(repo=repo, hoy=HOY).ejecutar(_ctx(persona=None), log, dry_run=True)
    assert len(repo.dry_run_log) == 2


def test_idempotente_si_el_cliente_ya_existe(tmp_path):
    repo, log = RepoCnfs(existe=True, dry_run=False), LogOperacion("x", tmp_path)
    RegistroCliente(repo=repo, hoy=HOY).ejecutar(_ctx(), log)
    assert repo.transacciones == [] and log.entradas() == []


def test_dry_run_distinto_al_del_repositorio_falla(tmp_path):
    with pytest.raises(ValueError, match="dry_run"):
        RegistroCliente(repo=RepoCnfs(dry_run=True), hoy=HOY).ejecutar(_ctx(), LogOperacion("x", tmp_path))
