"""Pruebas unitarias (sin BD) del módulo PASO_22_DISPERSADO."""
from datetime import datetime

import pytest

from insumos.contexto import ContextoVenta
from insumos.log_operacion import LogOperacion
from insumos.modulos.paso_22_dispersado import Paso22Dispersado
from services.originacion_repository import OriginacionRepository


class Repo(OriginacionRepository):
    def __init__(self, id_paso=30, cliente=0, dry_run=False):
        super().__init__(dry_run=dry_run)
        self.id_paso, self.cliente, self.escrituras = id_paso, cliente, []

    def leer_expediente(self, numero_contrato=None, id_expediente=None):
        return {"IdExpedienteCliente": 7329, "numeroContrato": "240021110", "Agencia": 2075000000335,
                "Cliente": self.cliente, "NombreCliente": "X", "RFCCliente": "Y", "DomicilioCliente": "Z",
                "FechaNacimiento": datetime(1996, 9, 3), "IdPaso": self.id_paso}

    def _escribir(self, sql, params=()):
        (self.dry_run_log if self.dry_run else self.escrituras).append((sql, tuple(params)))


def _ctx(repo):
    return ContextoVenta(tipo="CN", numero_contrato="240021110", fuente=repo)


@pytest.mark.parametrize("cliente", [0, 2611080402001])
def test_pone_el_paso_22_con_cliente_en_cero_o_con_valor(tmp_path, cliente):
    repo = Repo(cliente=cliente)
    Paso22Dispersado(repo=repo).ejecutar(_ctx(repo), LogOperacion("x", tmp_path))
    assert repo.escrituras == [
        ("UPDATE [dbo].[ExpedienteCliente] SET IdPaso = ? WHERE IdExpedienteCliente = ?", (22, 7329))]


def test_guarda_el_paso_anterior_en_el_log(tmp_path):
    repo, log = Repo(id_paso=30), LogOperacion("240021110", tmp_path)
    Paso22Dispersado(repo=repo).ejecutar(_ctx(repo), log)
    (e,) = [x for x in log.entradas() if x["tipo"] == "update"]
    assert (e["host"], e["tabla"], e["llave"]) == (
        "PESOS_OFFER", "Originacion.dbo.ExpedienteCliente", {"IdExpedienteCliente": 7329})
    assert e["anterior"] == {"IdPaso": 30} and e["nuevo"] == {"IdPaso": 22}


def test_no_cambia_ningun_otro_dato(tmp_path):
    repo = Repo()
    Paso22Dispersado(repo=repo).ejecutar(_ctx(repo), LogOperacion("x", tmp_path))
    (sql, _), = repo.escrituras
    assert "SET IdPaso = ?" in sql and sql.count("=") == 2  # SET IdPaso y WHERE Id


def test_idempotente_si_ya_esta_en_22(tmp_path):
    repo, log = Repo(id_paso=22), LogOperacion("x", tmp_path)
    Paso22Dispersado(repo=repo).ejecutar(_ctx(repo), log)
    assert repo.escrituras == [] and log.entradas() == []


def test_dry_run_deja_el_update_y_no_loguea(tmp_path):
    repo, log = Repo(dry_run=True), LogOperacion("x", tmp_path)
    Paso22Dispersado(repo=repo).ejecutar(_ctx(repo), log, dry_run=True)
    assert len(repo.dry_run_log) == 1 and repo.escrituras == [] and log.entradas() == []


def test_dry_run_distinto_al_del_repositorio_falla(tmp_path):
    repo = Repo(dry_run=True)
    with pytest.raises(ValueError, match="dry_run"):
        Paso22Dispersado(repo=repo).ejecutar(_ctx(repo), LogOperacion("x", tmp_path))
