"""Pruebas unitarias (sin BD) del módulo AGREEMENT."""
from datetime import date, datetime

import pytest

from insumos import plantillas
from insumos.contexto import ContextoVenta, ErrorContexto
from insumos.log_operacion import LogOperacion
from insumos.modulos.agreement import Agreement, construir_agreement
from services.cnfs_repository import CnfsRepository
from services.originacion_repository import OriginacionRepository

HOY = date(2026, 11, 7)
OFERTA = {"MontoTotal": 10520.39, "MontoTotalSeguro": 11028.61, "PrimerPagoSemanal": 562.26,
          "PrimerPagoSemanalSeguro": 589.36, "PagoSubsecuente": 321.23, "PagoSubsecuenteSeguro": 336.75}


class Fuente(OriginacionRepository):
    def __init__(self, cliente=0, oferta=None):
        super().__init__(dry_run=True)
        self.cliente, self.oferta = cliente, oferta or OFERTA

    def leer_expediente(self, numero_contrato=None, id_expediente=None):
        return {"IdExpedienteCliente": 7329, "numeroContrato": "240021110", "Agencia": 2075000000335,
                "Cliente": self.cliente, "NombreCliente": "X", "RFCCliente": "Y", "DomicilioCliente": "Z",
                "FechaNacimiento": datetime(1996, 9, 3)}

    def leer_montos(self, id_expediente):
        return self.oferta


class RepoCnfs(CnfsRepository):
    def __init__(self, existe=False, dry_run=True):
        super().__init__(dry_run=dry_run)
        self.existe, self.escrituras = existe, []

    def agreement_existe(self, numero_contrato):
        return self.existe

    def _escribir(self, sql, params=()):
        (self.dry_run_log if self.dry_run else self.escrituras).append((sql, tuple(params)))


def _ctx(con_seguro, cliente=0, oferta=None):
    return ContextoVenta(tipo="CN", numero_contrato="240021110", con_seguro=con_seguro,
                         fuente=Fuente(cliente, oferta))


def _construir(con_seguro, cliente=0):
    ctx = _ctx(con_seguro, cliente).cargar_montos()
    return construir_agreement(ctx, HOY)


def test_conserva_las_76_columnas_de_la_plantilla_en_su_orden():
    v = _construir(False)
    assert list(v) == list(plantillas.AGREEMENT) and len(v) == 76


def test_valores_de_la_venta_sin_seguro():
    v = _construir(False)
    assert v["Agreement_Num"] == 240021110 and v["Agreement_Status_Code"] == "AC"
    assert v["Customer_Id"] == 0 and v["Absolute_Arrears"] == 0
    for col in ("Total_Amount_Payable", "Settlement_Balance", "Total_Amount_Payable_At_Issue",
                "Issue_Value", "Outstanding_Balance"):
        assert v[col] == 10520.39, col
    for col in ("First_Instalment_Value", "First_Instalment_Value_At_Issue"):
        assert v[col] == 562.26, col
    for col in ("Final_Instalment_Value", "Regular_Instalment_Value", "Regular_Instalment_Value_At_Issue",
                "Final_Instalment_Value_At_Issue"):
        assert v[col] == 321.23, col


def test_valores_de_la_venta_con_seguro():
    v = _construir(True)
    assert v["Issue_Value"] == 11028.61 and v["First_Instalment_Value"] == 589.36
    assert v["Regular_Instalment_Value"] == 336.75 and v["Final_Instalment_Value"] == 336.75


def test_fechas_y_semana_de_hoy():
    v = _construir(False)
    assert v["Actual_Paid_Up_Date"] == v["Creation_Date"] == v["Last_Updated_Datetime"] == "2026-11-07 00:00:00"
    assert v["Actual_Paid_Up_Week"] == 202645  # sábado 7-nov-2026: semana de negocio 45 (corte en miércoles)


def test_customer_id_toma_el_cliente_del_contexto():
    assert _construir(False, cliente=2611070402001)["Customer_Id"] == 2611070402001


def test_el_resto_de_columnas_queda_como_la_plantilla():
    v = _construir(False)
    tocadas = {"Absolute_Arrears", "Actual_Paid_Up_Date", "Actual_Paid_Up_Week", "Agreement_Num",
               "Agreement_Status_Code", "Creation_Date", "Customer_Id", "Final_Instalment_Value",
               "Total_Amount_Payable", "Settlement_Balance", "Last_Updated_Datetime",
               "First_Instalment_Value_At_Issue", "Regular_Instalment_Value_At_Issue",
               "Total_Amount_Payable_At_Issue", "First_Instalment_Value", "Regular_Instalment_Value",
               "Final_Instalment_Value_At_Issue", "Issue_Value", "Outstanding_Balance"}
    for col, valor in plantillas.AGREEMENT.items():
        if col not in tocadas:
            assert v[col] == valor, col


def test_la_plantilla_original_no_se_modifica():
    antes = dict(plantillas.AGREEMENT)
    _construir(True)
    assert plantillas.AGREEMENT == antes


def test_montos_en_cero_fallan_sin_insertar(tmp_path):
    repo = RepoCnfs()
    modulo = Agreement(repo=repo, hoy=HOY)
    ctx = _ctx(True, oferta={**OFERTA, "MontoTotalSeguro": 0})
    with pytest.raises(ErrorContexto, match="MontoTotalSeguro"):
        modulo.ejecutar(ctx, LogOperacion("x", tmp_path), dry_run=True)
    assert repo.dry_run_log == []


def test_dry_run_deja_el_insert_y_no_loguea(tmp_path):
    repo, log = RepoCnfs(), LogOperacion("x", tmp_path)
    Agreement(repo=repo, hoy=HOY).ejecutar(_ctx(False), log, dry_run=True)
    (sql, params), = repo.dry_run_log
    assert sql.startswith("INSERT INTO [NFS_DBO].[Agreement_Table] (") and sql.count("?") == len(params) == 76
    assert log.entradas() == []


def test_insert_real_loguea_el_contrato_antes_de_escribir(tmp_path):
    repo, log = RepoCnfs(dry_run=False), LogOperacion("240021110", tmp_path)
    Agreement(repo=repo, hoy=HOY).ejecutar(_ctx(True), log)
    assert len(repo.escrituras) == 1
    (e,) = [x for x in log.entradas() if x["tipo"] == "insert"]
    assert e["host"] == "CNFS" and e["tabla"] == "CNFS_uat.NFS_DBO.Agreement_Table"
    assert e["llave"] == {"Agreement_Num": 240021110} and e["nuevo"]["Customer_Id"] == 0


def test_idempotente_si_el_contrato_ya_existe(tmp_path):
    repo, log = RepoCnfs(existe=True, dry_run=False), LogOperacion("x", tmp_path)
    Agreement(repo=repo, hoy=HOY).ejecutar(_ctx(True), log)
    assert repo.escrituras == [] and log.entradas() == []


def test_dry_run_distinto_al_del_repositorio_falla(tmp_path):
    with pytest.raises(ValueError, match="dry_run"):
        Agreement(repo=RepoCnfs(dry_run=True), hoy=HOY).ejecutar(_ctx(True), LogOperacion("x", tmp_path))
