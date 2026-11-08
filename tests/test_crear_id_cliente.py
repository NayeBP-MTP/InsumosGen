"""Pruebas unitarias (sin BD) de CREAR_ID_CLIENTE y del allocator de consecutivos."""
import threading
from datetime import date, datetime

import pytest

from insumos.contexto import ContextoVenta, ErrorContexto
from insumos.log_operacion import LogOperacion
from insumos.modulos.crear_id_cliente import CrearIdCliente, prefijo_cliente
from services.cnfs_repository import CnfsRepository
from services.originacion_repository import OriginacionRepository
from utils.cliente_id_allocator import ClienteIdAllocator

HOY = date(2026, 11, 4)


class RepoOriginacion(OriginacionRepository):
    def __init__(self, cliente=0, maximo=None, dry_run=False):
        super().__init__(dry_run=dry_run)
        self.fila = {
            "IdExpedienteCliente": 7329, "numeroContrato": "240021110", "Agencia": 2075000000335,
            "Cliente": cliente, "NombreCliente": "X", "RFCCliente": "Y", "DomicilioCliente": "Z",
            "FechaNacimiento": datetime(1996, 9, 3),
        }
        self.maximo, self.escrituras, self.prefijos = maximo, [], []

    def leer_expediente(self, numero_contrato=None, id_expediente=None):
        return dict(self.fila)

    def max_cliente_con_prefijo(self, prefijo):
        self.prefijos.append(prefijo)
        return self.maximo

    def _escribir(self, sql, params=()):
        # igual que SqlServerRepository: en dry_run solo se registra, no se "escribe"
        (self.dry_run_log if self.dry_run else self.escrituras).append((sql, tuple(params)))


class RepoCnfs(CnfsRepository):
    def __init__(self, maximo=None):
        super().__init__(dry_run=True)
        self.maximo = maximo

    def max_customer_id_con_prefijo(self, prefijo):
        return self.maximo


def _modulo(tmp_path, cliente=0, max_exp=None, max_cnfs=None, colaborador="04", dry_run=False):
    return CrearIdCliente(
        repo=RepoOriginacion(cliente, max_exp, dry_run=dry_run), repo_cnfs=RepoCnfs(max_cnfs),
        allocator=ClienteIdAllocator(tmp_path / "ids.sqlite3"), colaborador=colaborador, hoy=HOY,
    )


def _ctx(modulo):
    """Contexto que lee del mismo repositorio (y por tanto del mismo `Cliente`) que el módulo."""
    return ContextoVenta(tipo="CN", numero_contrato="240021110", fuente=modulo.repo)


def test_prefijo_ejemplo_del_diseno():
    assert prefijo_cliente(date(2026, 11, 4), "04") == 2611040402
    assert prefijo_cliente(date(2026, 11, 4), "4") == 2611040402  # 1 dígito se rellena a 2


@pytest.mark.parametrize("colaborador", ["", None, "abc", "123", "-1"])
def test_colaborador_invalido(colaborador):
    with pytest.raises(ErrorContexto, match="colaborador"):
        prefijo_cliente(HOY, colaborador)


def test_primer_cliente_del_dia_es_001(tmp_path):
    m = _modulo(tmp_path)
    ctx = m.ejecutar(_ctx(m), LogOperacion("x", tmp_path))
    assert ctx.cliente == 2611040402001 and len(str(ctx.cliente)) == 13


def test_toma_el_mayor_entre_expediente_y_customer_table_mas_uno(tmp_path):
    m = _modulo(tmp_path, max_exp=2611040402003, max_cnfs=2611040402007)
    assert m.ejecutar(_ctx(m), LogOperacion("x", tmp_path)).cliente == 2611040402008
    m = _modulo(tmp_path / "b", max_exp=2611040402012, max_cnfs=None)
    assert m.ejecutar(_ctx(m), LogOperacion("y", tmp_path)).cliente == 2611040402013


def test_consulta_el_prefijo_de_10_digitos(tmp_path):
    m = _modulo(tmp_path)
    m.ejecutar(_ctx(m), LogOperacion("x", tmp_path))
    assert m.repo.prefijos == [2611040402]


def test_escribe_cliente_y_loguea_el_anterior(tmp_path):
    m, log = _modulo(tmp_path), LogOperacion("240021110", tmp_path)
    m.ejecutar(_ctx(m), log)
    assert m.repo.escrituras == [
        ("UPDATE [dbo].[ExpedienteCliente] SET Cliente = ? WHERE IdExpedienteCliente = ?", (2611040402001, 7329))
    ]
    (e,) = [x for x in log.entradas() if x["tipo"] == "update"]
    assert e["anterior"] == {"Cliente": 0} and e["nuevo"] == {"Cliente": 2611040402001}
    assert e["llave"] == {"IdExpedienteCliente": 7329}


def test_cf_con_cliente_lo_usa_sin_escribir_ni_reservar(tmp_path):
    m, log = _modulo(tmp_path, cliente=2075261100023), LogOperacion("x", tmp_path)
    ctx = m.ejecutar(_ctx(m), log)
    assert ctx.cliente == 2075261100023 and m.repo.escrituras == [] and log.entradas() == []
    assert not m.allocator.db_path.exists()  # ni siquiera abrió el allocator


def test_consecutivos_se_reservan_aunque_la_bd_no_cambie(tmp_path):
    # dos ventas seguidas con la BD aún sin el primero (p. ej. ventas en paralelo): no repiten
    ma, mb = _modulo(tmp_path), _modulo(tmp_path)
    a = ma.ejecutar(_ctx(ma), LogOperacion("a", tmp_path)).cliente
    b = mb.ejecutar(_ctx(mb), LogOperacion("b", tmp_path)).cliente
    assert (a, b) == (2611040402001, 2611040402002)


def test_dry_run_no_reserva_ni_escribe_ni_loguea(tmp_path):
    m, log = _modulo(tmp_path, dry_run=True), LogOperacion("x", tmp_path)
    ctx = m.ejecutar(_ctx(m), log, dry_run=True)
    assert ctx.cliente == 2611040402001 and log.entradas() == []
    assert m.repo.escrituras == [] and len(m.repo.dry_run_log) == 1
    # y sigue sin reservarse: la siguiente ejecución real obtiene el mismo número
    real = _modulo(tmp_path)
    assert real.ejecutar(_ctx(real), LogOperacion("y", tmp_path)).cliente == 2611040402001


def test_sin_colaborador_falla_antes_de_reservar_o_escribir(tmp_path):
    m = _modulo(tmp_path, colaborador="")
    with pytest.raises(ErrorContexto, match="colaborador"):
        m.ejecutar(_ctx(m), LogOperacion("x", tmp_path))
    assert m.repo.escrituras == []


class TestAllocator:
    def test_toma_el_mayor_de_bd_y_reservado(self, tmp_path):
        a = ClienteIdAllocator(tmp_path / "a.sqlite3")
        assert a.reservar(2611040402, maximo_bd=5) == 6
        assert a.reservar(2611040402, maximo_bd=0) == 7
        assert a.reservar(2611040402, maximo_bd=20) == 21
        assert a.reservar(2611040403, maximo_bd=0) == 1  # otro colaborador, otro consecutivo

    def test_simular_no_reserva(self, tmp_path):
        a = ClienteIdAllocator(tmp_path / "a.sqlite3")
        assert a.reservar(1, 0, simular=True) == 1 and a.reservar(1, 0, simular=True) == 1
        assert a.reservar(1, 0) == 1 and a.reservar(1, 0) == 2

    def test_se_agotan_los_999(self, tmp_path):
        with pytest.raises(RuntimeError, match="agotaron"):
            ClienteIdAllocator(tmp_path / "a.sqlite3").reservar(1, maximo_bd=999)

    def test_reservas_simultaneas_no_repiten(self, tmp_path):
        ruta, obtenidos = tmp_path / "a.sqlite3", []

        def reservar():
            for _ in range(10):
                obtenidos.append(ClienteIdAllocator(ruta).reservar(2611040402, 0))

        hilos = [threading.Thread(target=reservar) for _ in range(6)]
        [h.start() for h in hilos]
        [h.join() for h in hilos]
        assert sorted(obtenidos) == list(range(1, 61))
