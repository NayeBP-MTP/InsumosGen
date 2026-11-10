"""Pruebas unitarias (sin navegador ni BD) de la integración de recetas en run.py."""
import pytest

import run
from config.settings import Settings
from insumos.contexto import ErrorContexto
from insumos.recetas import RECETAS
from insumos.runner import ResultadoReceta

LOTE_CN = {"id": "lote1", "tipo_cliente": "CN", "agencia_label": "Izcalli 335", "agencia": "2075000000335",
           "focus_id": "2075000343335", "password": "x", "metodo_entrega": "BBVA", "con_seguro": True,
           "cantidad": 2, "receta": "CN_REGISTRADO"}
LOTE_CF = {**LOTE_CN, "id": "lote2", "tipo_cliente": "CF", "cantidad": 1, "receta": "CF_REGISTRADO"}


def venta_ok(contrato="240021110", tipo="CN", id_exp=7329):
    return {"ciclo": 1, "estado": "exitoso", "error": None, "tipo": tipo, "agencia_label": "Izcalli 335",
            "con_seguro": True, "inicio": "2026-11-08 12:30:05.123456", "folio": None, "id_oferta": 0,
            "nombre_ine": "NAYELI BENITEZ PEREZ", "numero_contrato": contrato, "folio_contrato": "PR1",
            "id_expediente": id_exp}


def venta_fallida():
    return {"ciclo": 2, "estado": "fallido", "error": "Facematch rechazado"}


class RunnerFalso:
    def __init__(self, resultados):
        self.resultados, self.llamadas = list(resultados), []

    def ejecutar(self, receta, ctx):
        self.llamadas.append((receta, ctx))
        r = self.resultados.pop(0) if len(self.resultados) > 1 else self.resultados[0]
        if isinstance(r, Exception):
            raise r
        return r


def resultado(estado, **kw):
    return ResultadoReceta("CN_REGISTRADO", "240021110", estado, **kw)


@pytest.fixture
def entorno(monkeypatch):
    """Sin navegador ni disco: lotes de venta y runner falsos; historial y progreso capturados."""
    e = type("E", (), {})()
    e.lotes, e.historial, e.eventos, e.runner = [], [], [], RunnerFalso([resultado("completada")])
    e.respuestas = {}  # run_id -> detalle devuelto por el "pytest" del lote

    def lote_falso(tipo, grupo, run_config, controller=None):
        e.lotes.append((tipo, len(grupo)))
        return e.respuestas[f"{tipo.lower()}_{grupo[0]['batch_id']}"]

    monkeypatch.setattr(run, "_ejecutar_lote_venta", lote_falso)
    monkeypatch.setattr(run, "_crear_runner", lambda: e.runner)
    monkeypatch.setattr(run.RunHistory, "append", staticmethod(lambda r: e.historial.extend(r)))
    monkeypatch.setattr(run.Progress, "emit", staticmethod(lambda msg, nivel="info": e.eventos.append((nivel, msg))))
    monkeypatch.setattr(Settings, "NUMERO_COLABORADOR", "")
    return e


def ronda(slots, config=None, n=1):
    run._ejecutar_ronda(slots, config or {}, [], n)


# ---------- _construir_slots ----------

def test_slots_de_ventas_con_receta_y_sin_ella_conservan_la_forma_de_siempre():
    config = {"ventas_batches": [LOTE_CN, {**LOTE_CF, "receta": None}, {k: v for k, v in LOTE_CF.items() if k != "receta"}]}
    slots = run._construir_slots(config)
    assert [len(slots[t]) for t in ("OF", "CF", "CN", "AGENCIA")] == [0, 2, 2, 0]
    cn = slots["CN"][0]
    assert cn["estado"] == "pendiente" and cn["batch_id"] == "lote1" and cn["config"]["receta"] == "CN_REGISTRADO"
    assert "id" not in cn["config"] and "cantidad" not in cn["config"]


def test_slots_de_oferta_y_agencia_no_cambian():
    slots = run._construir_slots({"ofertas": [{"agencia_label": "A"}], "agencias": [{"sucursal": "S"}, {"sucursal": "T"}]})
    assert [len(slots[t]) for t in ("OF", "CF", "CN", "AGENCIA")] == [1, 0, 0, 2]
    assert slots["OF"][0] == {"estado": "pendiente", "intentos": 0, "detalle": "Sin ejecutar",
                              "config": {"agencia_label": "A"}}


def test_una_receta_inexistente_o_de_otro_tipo_se_rechaza():
    with pytest.raises(ValueError, match="no existe"):
        run._construir_slots({"ventas_batches": [{**LOTE_CN, "receta": "INVENTADA"}]})
    with pytest.raises(ValueError, match="ventas CN y la receta CF_REGISTRADO es para ventas CF"):
        run._construir_slots({"ventas_batches": [{**LOTE_CN, "receta": "CF_REGISTRADO"}]})
    with pytest.raises(ValueError, match="ventas CF"):
        run._construir_slots({"ventas_batches": [{**LOTE_CF, "receta": "CN_REGISTRADO"}]})


def test_toda_receta_del_catalogo_es_aceptada_para_su_tipo():
    for r in RECETAS.values():
        lote = {**(LOTE_CN if r.tipo_venta == "CN" else LOTE_CF), "receta": r.id}
        assert run._construir_slots({"ventas_batches": [lote]})[r.tipo_venta]


# ---------- venta + receta ----------

def test_venta_exitosa_ejecuta_la_receta_sobre_su_contrato(entorno):
    slots = run._construir_slots({"ventas_batches": [{**LOTE_CN, "cantidad": 1}]})
    entorno.respuestas["cn_lote1"] = [venta_ok()]
    ronda(slots)
    (slot,) = slots["CN"]
    assert slot["estado"] == "exitosa" and slot["venta_ok"] is True and slot["intentos"] == 1
    assert slot["detalle"] == "contrato 240021110 · receta CN registrado"
    (receta, ctx), = entorno.runner.llamadas
    assert receta.id == "CN_REGISTRADO"
    assert (ctx.tipo, ctx.numero_contrato, ctx.id_expediente, ctx.con_seguro) == ("CN", "240021110", 7329, True)
    assert ctx.inicio.isoformat() == "2026-11-08T12:30:05.123456"
    assert [h["estado"] for h in entorno.historial] == ["exitosa"]
    assert ("ok", "Receta CN_REGISTRADO completada (contrato 240021110)") in entorno.eventos


def test_los_eventos_de_la_receta_no_se_cuentan_como_ciclos_de_la_ui(entorno):
    from ui.progress_ui import _PATRON_CICLO
    slots = run._construir_slots({"ventas_batches": [{**LOTE_CN, "cantidad": 1}]})
    entorno.respuestas["cn_lote1"] = [venta_ok()]
    ronda(slots)
    assert not any(_PATRON_CICLO.search(m) for nivel, m in entorno.eventos if nivel in ("ok", "error"))


def test_en_un_lote_de_varias_ventas_solo_la_exitosa_corre_la_receta(entorno):
    slots = run._construir_slots({"ventas_batches": [LOTE_CN]})  # cantidad 2
    entorno.respuestas["cn_lote1"] = [venta_ok(), venta_fallida()]
    ronda(slots)
    ok, mala = slots["CN"]
    assert ok["estado"] == "exitosa" and len(entorno.runner.llamadas) == 1
    assert mala["estado"] == "pendiente" and not mala.get("venta_ok") and mala["detalle"] == "Facematch rechazado"
    assert run._venta_pendiente(mala) and not run._venta_pendiente(ok)


def test_la_venta_cf_manda_su_tipo_y_su_oferta(entorno):
    slots = run._construir_slots({"ventas_batches": [LOTE_CF]})
    v = {**venta_ok("240021111", "CF", 7331), "id_oferta": 26110020, "nombreCliente": "ROBERTO LÓPEZ"}
    entorno.respuestas["cf_lote2"] = [v]
    ronda(slots)
    (receta, ctx), = entorno.runner.llamadas
    assert receta.id == "CF_REGISTRADO" and ctx.tipo == "CF" and ctx.numero_contrato == "240021111"


def test_sin_pausa_qa_en_el_lote_se_pasa_a_la_receta(entorno):
    slots = run._construir_slots({"ventas_batches": [{**LOTE_CN, "cantidad": 1, "receta": "CN_REGISTRO_INTERMEDIO",
                                                      "sin_pausa_qa": True}]})
    entorno.respuestas["cn_lote1"] = [venta_ok()]
    ronda(slots)
    assert not entorno.runner.llamadas[0][0].tiene_pausa_qa


def test_lote_sin_receta_se_comporta_como_antes(entorno):
    lote = {k: v for k, v in LOTE_CN.items() if k != "receta"}
    slots = run._construir_slots({"ventas_batches": [{**lote, "cantidad": 1}]})
    entorno.respuestas["cn_lote1"] = [{**venta_ok(), "nombreCliente": "X", "folio": "F1"}]
    ronda(slots)
    (slot,) = slots["CN"]
    assert slot["estado"] == "exitosa" and slot["detalle"] == "X · folio F1" and "venta_ok" not in slot
    assert entorno.runner.llamadas == []


def test_el_colaborador_de_la_corrida_se_aplica_antes_de_la_receta(entorno):
    slots = run._construir_slots({"ventas_batches": [{**LOTE_CN, "cantidad": 1}]})
    entorno.respuestas["cn_lote1"] = [venta_ok()]
    ronda(slots, {"numero_colaborador": "07"})
    assert Settings.NUMERO_COLABORADOR == "07"


# ---------- pausa de QA ----------

def test_la_pausa_de_qa_deja_el_slot_esperando_y_no_se_reintenta(entorno):
    entorno.runner = RunnerFalso([resultado("esperando_qa")])
    slots = run._construir_slots({"ventas_batches": [{**LOTE_CN, "cantidad": 1, "receta": "CN_REGISTRO_INTERMEDIO"}]})
    entorno.respuestas["cn_lote1"] = [venta_ok()]
    ronda(slots)
    (slot,) = slots["CN"]
    assert slot["estado"] == "esperando_qa" and slot["venta_ok"] is True
    assert slot["detalle"] == "En pausa de QA: contrato 240021110 · python -m insumos continuar 240021110"
    assert not run._venta_pendiente(slot) and not run._receta_pendiente(slot)

    entorno.lotes.clear(); entorno.runner.llamadas.clear()
    ronda(slots, n=2)  # un reintento no toca ni la venta ni la receta en pausa
    assert entorno.lotes == [] and entorno.runner.llamadas == [] and slot["intentos"] == 1


# ---------- fallas y reintento ----------

def test_si_la_receta_falla_la_venta_queda_hecha_y_el_reintento_solo_repite_la_receta(entorno):
    entorno.runner = RunnerFalso([resultado("fallida", modulo_fallido="AGREEMENT", error="boom"),
                                  resultado("completada")])
    slots = run._construir_slots({"ventas_batches": [{**LOTE_CN, "cantidad": 1}]})
    entorno.respuestas["cn_lote1"] = [venta_ok()]
    ronda(slots)
    (slot,) = slots["CN"]
    assert slot["estado"] == "fallida" and slot["venta_ok"] is True
    assert slot["detalle"] == "Receta CN_REGISTRADO falló en AGREEMENT: boom"
    assert run._receta_pendiente(slot) and not run._venta_pendiente(slot)

    assert entorno.lotes == [("CN", 1)]
    ronda(slots, n=2)
    assert entorno.lotes == [("CN", 1)]  # la venta NO se repitió
    assert slot["estado"] == "exitosa" and slot["intentos"] == 2  # ronda de la venta + reintento de la receta
    assert [h["estado"] for h in entorno.historial] == ["fallida", "exitosa"]


def test_falla_deshecha_sola_lo_indica(entorno):
    entorno.runner = RunnerFalso([resultado("fallida", modulo_fallido="RENOMBRAR_CLIENTE", error="x", deshecho=True)])
    slots = run._construir_slots({"ventas_batches": [{**LOTE_CN, "cantidad": 1}]})
    entorno.respuestas["cn_lote1"] = [venta_ok()]
    ronda(slots)
    assert "(se deshizo sola)" in slots["CN"][0]["detalle"]


def test_un_error_del_runner_deja_el_slot_fallido_con_el_motivo(entorno):
    entorno.runner = RunnerFalso([ErrorContexto("El contrato 240021110 es una venta CN y se pidió una receta CF.")])
    slots = run._construir_slots({"ventas_batches": [{**LOTE_CN, "cantidad": 1}]})
    entorno.respuestas["cn_lote1"] = [venta_ok()]
    ronda(slots)
    (slot,) = slots["CN"]
    assert slot["estado"] == "fallida" and slot["venta_ok"] is True and "es una venta CN" in slot["detalle"]
    assert [n for n, m in entorno.eventos if n == "error" and "FALLÓ" in m] == ["error"]


def test_venta_sin_contrato_localizado_falla_y_se_relocaliza_al_reintentar(entorno, monkeypatch):
    slots = run._construir_slots({"ventas_batches": [{**LOTE_CN, "cantidad": 1}]})
    sin_contrato = {**venta_ok(), "numero_contrato": None, "id_expediente": None}
    entorno.respuestas["cn_lote1"] = [sin_contrato]
    monkeypatch.setattr(run, "_localizar_contrato", lambda venta: None)  # la BD sigue sin responder
    ronda(slots)
    (slot,) = slots["CN"]
    assert slot["estado"] == "fallida" and slot["venta_ok"] is True and "no se localizó su contrato" in slot["detalle"]
    assert entorno.runner.llamadas == []

    def ya_responde(venta):
        venta.update(numero_contrato="240021110", id_expediente=7329)
    monkeypatch.setattr(run, "_localizar_contrato", ya_responde)
    ronda(slots, n=2)
    assert slot["estado"] == "exitosa" and entorno.lotes == [("CN", 1)]
    assert entorno.runner.llamadas[0][1].numero_contrato == "240021110"


def test_una_venta_que_fallo_se_reintenta_completa_y_luego_corre_su_receta(entorno):
    slots = run._construir_slots({"ventas_batches": [{**LOTE_CN, "cantidad": 1}]})
    entorno.respuestas["cn_lote1"] = [venta_fallida()]
    ronda(slots)
    (slot,) = slots["CN"]
    assert slot["estado"] == "pendiente" and run._venta_pendiente(slot) and entorno.runner.llamadas == []
    entorno.respuestas["cn_lote1"] = [venta_ok()]
    ronda(slots, n=2)
    assert slot["estado"] == "exitosa" and entorno.lotes == [("CN", 1), ("CN", 1)] and slot["intentos"] == 2


def test_recetas_pendientes_y_ventas_pendientes_conviven_en_una_misma_ronda(entorno):
    entorno.runner = RunnerFalso([resultado("fallida", modulo_fallido="AGREEMENT", error="boom"),
                                  resultado("completada")])
    slots = run._construir_slots({"ventas_batches": [LOTE_CN]})  # cantidad 2
    entorno.respuestas["cn_lote1"] = [venta_ok(), venta_fallida()]
    ronda(slots)
    primero, segundo = slots["CN"]
    assert (primero["estado"], segundo["estado"]) == ("fallida", "pendiente")

    entorno.respuestas["cn_lote1"] = [venta_ok("240021112", id_exp=7335)]
    ronda(slots, n=2)
    assert (primero["estado"], segundo["estado"]) == ("exitosa", "exitosa")
    assert entorno.lotes == [("CN", 2), ("CN", 1)]  # solo se repitió la venta de la que falló
    assert [c.numero_contrato for _, c in entorno.runner.llamadas] == ["240021110", "240021110", "240021112"]
