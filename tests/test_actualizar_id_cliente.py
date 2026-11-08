"""Pruebas unitarias (sin BD) del módulo ACTUALIZAR_ID_CLIENTE."""
from datetime import datetime

import pytest

from insumos.contexto import ContextoVenta, ErrorContexto
from insumos.log_operacion import LogOperacion
from insumos.modulos.actualizar_id_cliente import ActualizarIdCliente
from services.cnfs_repository import CnfsRepository
from services.originacion_repository import OriginacionRepository

CLIENTE = 2611080402001


class RepoOriginacion(OriginacionRepository):
    def __init__(self, en_bd=0, dry_run=False):
        super().__init__(dry_run=dry_run)
        self.en_bd, self.escrituras = en_bd, []

    def leer_expediente(self, numero_contrato=None, id_expediente=None):
        return {"IdExpedienteCliente": 7329, "numeroContrato": "240021110", "Agencia": 2075000000335,
                "Cliente": self.en_bd, "NombreCliente": "X", "RFCCliente": "Y", "DomicilioCliente": "Z",
                "FechaNacimiento": datetime(1996, 9, 3)}

    def _escribir(self, sql, params=()):
        (self.dry_run_log if self.dry_run else self.escrituras).append((sql, tuple(params)))


class RepoCnfs(CnfsRepository):
    def __init__(self, en_agreement=0, dry_run=False):
        super().__init__(dry_run=dry_run)
        self.en_agreement, self.escrituras = en_agreement, []

    def customer_id_de_agreement(self, numero_contrato):
        return self.en_agreement

    def _escribir(self, sql, params=()):
        (self.dry_run_log if self.dry_run else self.escrituras).append((sql, tuple(params)))


def _modulo(en_bd=0, en_agreement=0, dry_run=False):
    return ActualizarIdCliente(repo=RepoOriginacion(en_bd, dry_run), repo_cnfs=RepoCnfs(en_agreement, dry_run))


def _ctx(modulo, cliente=CLIENTE):
    ctx = ContextoVenta(tipo="CN", numero_contrato="240021110", fuente=modulo.repo).cargar_expediente()
    ctx.cliente = cliente  # lo que dejó CREAR_ID_CLIENTE (o se dio a mano) en el contexto
    return ctx


def test_actualiza_agreement_y_expediente(tmp_path):
    m, log = _modulo(), LogOperacion("240021110", tmp_path)
    m.ejecutar(_ctx(m), log)
    assert m.repo_cnfs.escrituras == [
        ("UPDATE [NFS_DBO].[Agreement_Table] SET Customer_Id = ? WHERE Agreement_Num = ?", (CLIENTE, 240021110))]
    assert m.repo.escrituras == [
        ("UPDATE [dbo].[ExpedienteCliente] SET Cliente = ? WHERE IdExpedienteCliente = ?", (CLIENTE, 7329))]


def test_log_con_el_valor_anterior_de_cada_escritura(tmp_path):
    m, log = _modulo(), LogOperacion("240021110", tmp_path)
    m.ejecutar(_ctx(m), log)
    agreement, expediente = [e for e in log.entradas() if e["tipo"] == "update"]
    assert (agreement["host"], agreement["llave"], agreement["anterior"], agreement["nuevo"]) == (
        "CNFS", {"Agreement_Num": 240021110}, {"Customer_Id": 0}, {"Customer_Id": CLIENTE})
    assert (expediente["host"], expediente["llave"], expediente["anterior"], expediente["nuevo"]) == (
        "PESOS_OFFER", {"IdExpedienteCliente": 7329}, {"Cliente": 0}, {"Cliente": CLIENTE})


def test_normalmente_el_expediente_ya_lo_tiene_por_crear_id_y_solo_actualiza_agreement(tmp_path):
    m = _modulo(en_bd=CLIENTE)
    m.ejecutar(_ctx(m), LogOperacion("x", tmp_path))
    assert len(m.repo_cnfs.escrituras) == 1 and m.repo.escrituras == []


def test_idempotente_si_ya_esta_todo(tmp_path):
    m, log = _modulo(en_bd=CLIENTE, en_agreement=CLIENTE), LogOperacion("x", tmp_path)
    m.ejecutar(_ctx(m), log)
    assert m.repo_cnfs.escrituras == [] and m.repo.escrituras == [] and log.entradas() == []


def test_sin_cliente_pide_crear_id(tmp_path):
    m = _modulo()
    with pytest.raises(ErrorContexto, match="CREAR_ID_CLIENTE"):
        m.ejecutar(_ctx(m, cliente=0), LogOperacion("x", tmp_path))


def test_sin_agreement_pide_agreement(tmp_path):
    m = _modulo(en_agreement=None)
    with pytest.raises(ErrorContexto, match="AGREEMENT"):
        m.ejecutar(_ctx(m), LogOperacion("x", tmp_path))
    assert m.repo.escrituras == []


@pytest.mark.parametrize("en_bd,en_agreement,donde", [(0, 999, "Agreement_Table"), (999, 0, "ExpedienteCliente")])
def test_no_pisa_otro_cliente_y_no_escribe_nada(tmp_path, en_bd, en_agreement, donde):
    m = _modulo(en_bd=en_bd, en_agreement=en_agreement)
    with pytest.raises(ErrorContexto, match=donde):
        m.ejecutar(_ctx(m), LogOperacion("x", tmp_path))
    assert m.repo_cnfs.escrituras == [] and m.repo.escrituras == []  # ni la parte que sí estaba en 0


def test_dry_run_deja_los_update_y_no_loguea(tmp_path):
    m, log = _modulo(dry_run=True), LogOperacion("x", tmp_path)
    m.ejecutar(_ctx(m), log, dry_run=True)
    assert len(m.repo_cnfs.dry_run_log) == 1 and len(m.repo.dry_run_log) == 1 and log.entradas() == []


def test_dry_run_distinto_al_de_los_repositorios_falla(tmp_path):
    m = _modulo(dry_run=True)
    with pytest.raises(ValueError, match="dry_run"):
        m.ejecutar(_ctx(m), LogOperacion("x", tmp_path), dry_run=False)
