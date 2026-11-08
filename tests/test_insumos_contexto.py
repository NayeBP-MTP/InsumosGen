"""Pruebas unitarias (sin BD) de ContextoVenta, la interfaz de módulo y el log de operación."""
from datetime import datetime
from types import SimpleNamespace

import pytest

from insumos.contexto import ContextoVenta, ErrorContexto, Montos, elegir_montos
from insumos.log_operacion import LogOperacion
from insumos.modulo import Modulo

EXPEDIENTE = {
    "IdExpedienteCliente": 7329, "numeroContrato": "240021110",
    "Agencia": 2075000000335, "Cliente": 0, "NombreCliente": "NAYELI BENITEZ PEREZ",
    "RFCCliente": "BEPN951222AB1", "DomicilioCliente": "CALLE 1", "FechaNacimiento": datetime(1995, 12, 22),
}
OFERTA = {
    "MontoTotal": 10000.0, "MontoTotalSeguro": 10500.0,
    "PrimerPagoSemanal": 530.39, "PrimerPagoSemanalSeguro": 560.0,
    "PagoSubsecuente": 303.05, "PagoSubsecuenteSeguro": 320.0,
}


class FakeFuente:
    def __init__(self, expediente=None, oferta=None):
        self.expediente, self.oferta = expediente or EXPEDIENTE, oferta or OFERTA
        self.lecturas = []

    def leer_expediente(self, numero_contrato=None, id_expediente=None):
        self.lecturas.append(("expediente", numero_contrato, id_expediente))
        return self.expediente

    def leer_montos(self, id_expediente):
        self.lecturas.append(("montos", id_expediente))
        return self.oferta


class TestElegirMontos:
    def test_sin_seguro(self):
        assert elegir_montos(OFERTA, False) == Montos(10000.0, 530.39, 303.05)

    def test_con_seguro(self):
        assert elegir_montos(OFERTA, True) == Montos(10500.0, 560.0, 320.0)

    @pytest.mark.parametrize("valor", [None, 0, 0.0, -5])
    def test_monto_nulo_o_cero_falla_nombrando_la_columna(self, valor):
        with pytest.raises(ErrorContexto, match="PrimerPagoSemanalSeguro"):
            elegir_montos({**OFERTA, "PrimerPagoSemanalSeguro": valor}, True)

    def test_solo_importa_la_columna_del_modo_elegido(self):
        # el seguro en NULL no estorba a una venta sin seguro
        assert elegir_montos({**OFERTA, "MontoTotalSeguro": None}, False).monto_prestamo == 10000.0


class TestContextoVenta:
    def _ctx(self, fuente, **kw):
        return ContextoVenta(tipo="CN", numero_contrato="240021110", fuente=fuente, **kw)

    def test_tipo_invalido(self):
        with pytest.raises(ErrorContexto):
            ContextoVenta(tipo="XX")

    def test_status_code(self):
        assert ContextoVenta(tipo="CF").status_code == "CC"
        assert ContextoVenta(tipo="CN").status_code == "AA"

    def test_no_lee_nada_hasta_que_se_pide(self):
        fuente = FakeFuente()
        self._ctx(fuente)
        assert fuente.lecturas == []

    def test_carga_expediente_una_sola_vez(self):
        fuente = FakeFuente()
        ctx = self._ctx(fuente).cargar_expediente().cargar_expediente()
        assert ctx.nombre_cliente == "NAYELI BENITEZ PEREZ" and ctx.agencia == 2075000000335
        assert ctx.cliente == 0 and ctx.id_expediente == 7329
        assert fuente.lecturas == [("expediente", "240021110", None)]

    def test_cliente_null_se_toma_como_cero_y_cf_conserva_su_numero(self):
        assert self._ctx(FakeFuente({**EXPEDIENTE, "Cliente": None})).cargar_expediente().cliente == 0
        cf = self._ctx(FakeFuente({**EXPEDIENTE, "Cliente": 2075261100020})).cargar_expediente()
        assert cf.cliente == 2075261100020

    def test_cargar_montos_carga_tambien_el_expediente_y_respeta_el_seguro(self):
        fuente = FakeFuente()
        ctx = self._ctx(fuente, con_seguro=False).cargar_montos().cargar_montos()
        assert ctx.montos == Montos(10000.0, 530.39, 303.05)
        assert fuente.lecturas == [("expediente", "240021110", None), ("montos", 7329)]

    def test_montos_en_cero_fallan_sin_dejar_el_contexto_a_medias(self):
        ctx = self._ctx(FakeFuente(oferta={**OFERTA, "MontoTotalSeguro": 0}))
        with pytest.raises(ErrorContexto):
            ctx.cargar_montos()
        assert ctx.montos is None

    def test_sin_contrato_ni_expediente_o_sin_fuente(self):
        with pytest.raises(ErrorContexto, match="numero_contrato"):
            ContextoVenta(tipo="CN", fuente=FakeFuente()).cargar_expediente()
        with pytest.raises(ErrorContexto, match="fuente"):
            ContextoVenta(tipo="CN", numero_contrato="1").cargar_expediente()

    def test_desde_resultado_venta(self):
        r = SimpleNamespace(tipo="CF", numero_contrato="240021111", id_expediente=7331,
                            con_seguro=True, inicio=None)
        ctx = ContextoVenta.desde_resultado_venta(r)
        assert (ctx.tipo, ctx.numero_contrato, ctx.id_expediente) == ("CF", "240021111", 7331)
        r.numero_contrato = None
        with pytest.raises(ErrorContexto):
            ContextoVenta.desde_resultado_venta(r)


class TestLogOperacion:
    def test_sin_archivo_esta_vacio(self, tmp_path):
        log = LogOperacion("240021110", tmp_path)
        assert log.entradas() == [] and log.modulos_completados() == []

    def test_escrituras_y_marcas_se_guardan_en_orden(self, tmp_path):
        log = LogOperacion("240021110", tmp_path)
        log.modulo_iniciado("RENOMBRAR_CLIENTE")
        log.escritura("RENOMBRAR_CLIENTE", "update", "PESOS_OFFER", "Originacion.dbo.ExpedienteCliente",
                      {"IdExpedienteCliente": 7329}, anterior={"NombreCliente": "VIEJO"},
                      nuevo={"NombreCliente": "NUEVO"})
        log.modulo_completado("RENOMBRAR_CLIENTE")
        log.modulo_iniciado("AGREEMENT")
        assert [e["tipo"] for e in log.entradas()] == [
            "modulo_iniciado", "update", "modulo_completado", "modulo_iniciado"]
        assert log.modulos_completados() == ["RENOMBRAR_CLIENTE"]  # AGREEMENT quedó a medias

    def test_deshacer_recorre_en_orden_inverso_y_solo_escrituras(self, tmp_path):
        log = LogOperacion("x", tmp_path)
        log.modulo_iniciado("A")
        log.escritura("A", "insert", "CNFS", "t1", {"id": 1}, nuevo={"id": 1})
        log.escritura("A", "update", "PESOS_OFFER", "t2", {"id": 2}, anterior={"v": 1}, nuevo={"v": 2})
        log.modulo_completado("A")
        assert [e["tabla"] for e in log.escrituras_para_deshacer()] == ["t2", "t1"]

    def test_accion_invalida(self, tmp_path):
        with pytest.raises(ValueError):
            LogOperacion("x", tmp_path).escritura("A", "merge", "h", "t", {})

    def test_fechas_y_acentos_se_serializan(self, tmp_path):
        log = LogOperacion("x", tmp_path)
        log.escritura("A", "update", "h", "t", {"id": 1}, anterior={"f": datetime(2026, 11, 7), "n": "Adán"})
        assert log.entradas()[0]["anterior"] == {"f": "2026-11-07 00:00:00", "n": "Adán"}

    def test_un_archivo_por_operacion(self, tmp_path):
        LogOperacion("a", tmp_path).modulo_iniciado("M")
        assert LogOperacion("b", tmp_path).entradas() == []


def test_modulo_es_abstracto_y_su_ejecutar_devuelve_el_contexto(tmp_path):
    with pytest.raises(TypeError):
        Modulo()

    class Eco(Modulo):
        nombre = "ECO"

        def ejecutar(self, ctx, log, dry_run=False):
            log.modulo_completado(self.nombre)
            return ctx

    ctx = ContextoVenta(tipo="CN")
    log = LogOperacion("x", tmp_path)
    assert Eco().ejecutar(ctx, log) is ctx and log.modulos_completados() == ["ECO"]
