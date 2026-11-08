"""Pruebas unitarias (sin BD ni navegador) de la localización del contrato de una venta."""
from datetime import datetime

from flows import resultado_venta
from flows.resultado_venta import ResultadoVenta, localizar_venta

INICIO = datetime(2026, 11, 6, 20, 30, 0)


def _fila(contrato="240021109", nombre="NAYELI BENITEZ PEREZ"):
    return {
        "IdExpedienteCliente": 7328, "NombreCliente": nombre, "numeroContrato": contrato,
        "folioContrato": "PR24003109",
    }


class FakeRepo:
    def __init__(self, respuestas):
        self.respuestas = list(respuestas)
        self.llamadas = []

    def buscar_venta_finalizada(self, id_agente, desde, id_oferta=0):
        self.llamadas.append((id_agente, desde, id_oferta))
        return self.respuestas.pop(0) if len(self.respuestas) > 1 else self.respuestas[0]


def _resultado(**kw):
    return ResultadoVenta(tipo="CN", agencia_label="Izcalli 335", con_seguro=True, inicio=INICIO, **kw)


class TestLocalizarVenta:
    def test_completa_contrato_y_nombre_de_la_ine(self, monkeypatch):
        monkeypatch.setattr(resultado_venta.Settings, "ESTRELLA", "2075000343335")
        repo = FakeRepo([[_fila()]])
        r = localizar_venta(_resultado(id_oferta=26110020), repo)
        assert (r.numero_contrato, r.nombre_ine, r.id_expediente) == ("240021109", "NAYELI BENITEZ PEREZ", 7328)
        assert repo.llamadas == [(2075000343335, INICIO, 26110020)]

    def test_varios_candidatos_toma_el_mas_reciente(self, monkeypatch):
        monkeypatch.setattr(resultado_venta.Settings, "ESTRELLA", "1")
        repo = FakeRepo([[_fila("240021110"), _fila("240021109")]])
        assert localizar_venta(_resultado(), repo).numero_contrato == "240021110"

    def test_espera_a_que_aparezca(self, monkeypatch):
        monkeypatch.setattr(resultado_venta.Settings, "ESTRELLA", "1")
        monkeypatch.setattr(resultado_venta, "LOCALIZAR_INTERVALO", 0)
        repo = FakeRepo([[], [], [_fila()]])
        assert localizar_venta(_resultado(), repo).numero_contrato == "240021109"
        assert len(repo.llamadas) == 3

    def test_no_aparece_deja_el_contrato_en_none(self, monkeypatch):
        monkeypatch.setattr(resultado_venta.Settings, "ESTRELLA", "1")
        monkeypatch.setattr(resultado_venta, "LOCALIZAR_ESPERA", 0)
        assert localizar_venta(_resultado(), FakeRepo([[]])).numero_contrato is None

    def test_sin_hora_de_inicio_no_consulta(self):
        repo = FakeRepo([[_fila()]])
        r = ResultadoVenta(tipo="CN", agencia_label="x", con_seguro=False)
        assert localizar_venta(r, repo).numero_contrato is None and repo.llamadas == []

    def test_error_de_bd_no_rompe_la_venta(self, monkeypatch):
        monkeypatch.setattr(resultado_venta.Settings, "ESTRELLA", "1")

        class Roto:
            def buscar_venta_finalizada(self, *a, **k):
                raise RuntimeError("sin VPN")
        assert localizar_venta(_resultado(), Roto()).numero_contrato is None


def test_a_dict_serializa_la_fecha():
    d = _resultado(folio="F1").a_dict()
    assert d["inicio"] == "2026-11-06 20:30:00" and d["folio"] == "F1" and d["con_seguro"] is True
