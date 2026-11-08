"""Pruebas unitarias (sin BD) de las recetas, el estado persistido y el runner."""
from datetime import datetime

import pytest

from insumos.contexto import ContextoVenta, ErrorContexto
from insumos.log_operacion import LogOperacion
from insumos.modulo import Modulo
from insumos.pendientes import PendientesStore
from insumos.recetas import PAUSA_QA, RECETAS
from insumos.runner import RunnerRecetas


class Fuente:
    def leer_expediente(self, numero_contrato=None, id_expediente=None):
        return {"IdExpedienteCliente": 7329, "numeroContrato": "240021110", "Agencia": 2075000000335,
                "Cliente": 0, "NombreCliente": "JOSÉ LUIS PÉREZ RODRÍGUEZ", "RFCCliente": "R",
                "DomicilioCliente": "Z", "FechaNacimiento": datetime(1996, 9, 3, 5, 0)}


class Bitacora:
    """Registra qué módulos corrieron y permite hacer fallar uno."""

    def __init__(self, falla=None):
        self.llamadas, self.falla = [], falla

    def fabrica(self, nombre):
        bitacora = self

        class Falso(Modulo):
            def ejecutar(self, ctx, log, dry_run=False):
                bitacora.llamadas.append((nombre, dry_run))
                if bitacora.falla == nombre:
                    raise RuntimeError(f"falló {nombre}")
                return ctx

        return Falso()


def _runner(tmp_path, bitacora=None, dry_run=False):
    bitacora = bitacora or Bitacora()
    runner = RunnerRecetas(dry_run=dry_run, directorio_logs=tmp_path / "logs",
                           pendientes=PendientesStore(tmp_path / "pendientes.json"), fabrica=bitacora.fabrica)
    return runner, bitacora


def _ctx(tipo="CN"):
    return ContextoVenta(tipo=tipo, numero_contrato="240021110", id_expediente=7329, fuente=Fuente())


# --- recetas como datos ---

def test_las_seis_recetas_del_diseno():
    assert {r.id: r.pasos for r in RECETAS.values()} == {
        "CN_REGISTRO_INTERMEDIO": ("RENOMBRAR_CLIENTE", "AGREEMENT", PAUSA_QA, "CREAR_ID_CLIENTE",
                                   "ACTUALIZAR_ID_CLIENTE", "REGISTRO_CLIENTE"),
        "CN_REGISTRADO": ("RENOMBRAR_CLIENTE", "CREAR_ID_CLIENTE", "AGREEMENT", "REGISTRO_CLIENTE"),
        "CN_REGISTRO_DISPERSADO": ("RENOMBRAR_CLIENTE", "PASO_22_DISPERSADO", "AGREEMENT", PAUSA_QA,
                                   "CREAR_ID_CLIENTE", "ACTUALIZAR_ID_CLIENTE", "REGISTRO_CLIENTE"),
        "CN_REGISTRADO_DISPERSION": ("RENOMBRAR_CLIENTE", "CREAR_ID_CLIENTE", "PASO_22_DISPERSADO",
                                     "AGREEMENT", "REGISTRO_CLIENTE"),
        "CF_DISPERSADO": ("RENOMBRAR_CLIENTE", "PASO_22_DISPERSADO", "AGREEMENT", "REGISTRO_CLIENTE"),
        "CF_REGISTRADO": ("RENOMBRAR_CLIENTE", "AGREEMENT", "REGISTRO_CLIENTE"),
    }
    assert [RECETAS[i].tipo_venta for i in RECETAS] == ["CN", "CN", "CN", "CN", "CF", "CF"]


def test_sin_pausa_qa_quita_solo_la_pausa():
    r = RECETAS["CN_REGISTRO_INTERMEDIO"]
    assert r.tiene_pausa_qa and not r.sin_pausa_qa().tiene_pausa_qa
    assert r.sin_pausa_qa().pasos == tuple(p for p in r.pasos if p != PAUSA_QA)
    assert RECETAS["CN_REGISTRADO"].sin_pausa_qa() == RECETAS["CN_REGISTRADO"]


def test_todos_los_modulos_de_las_recetas_existen_en_la_fabrica_por_defecto():
    from insumos.runner import fabrica_por_defecto
    fabrica = fabrica_por_defecto(dry_run=True)
    for receta in RECETAS.values():
        for paso in receta.pasos:
            if paso != PAUSA_QA:
                assert fabrica(paso).nombre == paso


# --- ejecución ---

def test_ejecuta_los_modulos_en_orden_y_deja_el_log_y_el_estado(tmp_path):
    runner, bit = _runner(tmp_path)
    r = runner.ejecutar(RECETAS["CN_REGISTRADO"], _ctx())
    assert r.estado == "completada" and r.ejecutados == list(RECETAS["CN_REGISTRADO"].pasos)
    assert [n for n, _ in bit.llamadas] == list(RECETAS["CN_REGISTRADO"].pasos)
    assert LogOperacion("240021110", tmp_path / "logs").modulos_completados() == list(RECETAS["CN_REGISTRADO"].pasos)
    entrada = runner.pendientes.obtener("240021110")
    assert entrada["estado"] == "completada" and entrada["receta"] == "CN_REGISTRADO"
    assert runner.pendientes.pendientes() == []  # una completada no se ofrece para retomar


def test_la_receta_debe_coincidir_con_el_tipo_de_venta(tmp_path):
    runner, bit = _runner(tmp_path)
    with pytest.raises(ErrorContexto, match="CF"):
        runner.ejecutar(RECETAS["CF_REGISTRADO"], _ctx("CN"))
    assert bit.llamadas == []


def test_sin_numero_de_contrato_no_arranca(tmp_path):
    runner, _ = _runner(tmp_path)
    with pytest.raises(ErrorContexto, match="numero_contrato"):
        runner.ejecutar(RECETAS["CN_REGISTRADO"], ContextoVenta(tipo="CN", id_expediente=1))


# --- PAUSA_QA ---

def test_la_pausa_detiene_la_receta_y_guarda_lo_que_qa_necesita(tmp_path):
    runner, bit = _runner(tmp_path)
    r = runner.ejecutar(RECETAS["CN_REGISTRO_INTERMEDIO"], _ctx())
    assert r.estado == "esperando_qa" and r.ejecutados == ["RENOMBRAR_CLIENTE", "AGREEMENT"]
    assert [n for n, _ in bit.llamadas] == ["RENOMBRAR_CLIENTE", "AGREEMENT"]
    (entrada,) = runner.pendientes.pendientes()
    assert entrada["estado"] == "esperando_qa" and entrada["paso_actual"] == PAUSA_QA
    assert entrada["para_qa"] == {"numero_contrato": "240021110", "fecha_nacimiento": "1996-09-03",
                                  "nombre_cliente": "JOSÉ LUIS PÉREZ RODRÍGUEZ"}
    assert "PAUSA_QA" not in LogOperacion("240021110", tmp_path / "logs").modulos_completados()


def test_volver_a_ejecutar_en_pausa_no_la_salta(tmp_path):
    runner, bit = _runner(tmp_path)
    runner.ejecutar(RECETAS["CN_REGISTRO_INTERMEDIO"], _ctx())
    r = runner.ejecutar(RECETAS["CN_REGISTRO_INTERMEDIO"], _ctx())
    assert r.estado == "esperando_qa" and r.ejecutados == []
    assert [n for n, _ in bit.llamadas] == ["RENOMBRAR_CLIENTE", "AGREEMENT"]


def test_la_pausa_sobrevive_a_cerrar_el_programa_y_se_retoma_tras_qa(tmp_path):
    runner, _ = _runner(tmp_path)
    runner.ejecutar(RECETAS["CN_REGISTRO_INTERMEDIO"], _ctx())

    # "otro proceso": runner nuevo, módulos nuevos, mismo disco
    runner2, bit2 = _runner(tmp_path)
    r = runner2.continuar_tras_qa("240021110", fuente=Fuente())
    assert r.estado == "completada"
    assert r.ejecutados == ["CREAR_ID_CLIENTE", "ACTUALIZAR_ID_CLIENTE", "REGISTRO_CLIENTE"]
    assert [n for n, _ in bit2.llamadas] == r.ejecutados  # no repite lo anterior a la pausa
    assert runner2.pendientes.obtener("240021110")["estado"] == "completada"
    assert LogOperacion("240021110", tmp_path / "logs").modulos_completados() == [
        "RENOMBRAR_CLIENTE", "AGREEMENT", PAUSA_QA, "CREAR_ID_CLIENTE", "ACTUALIZAR_ID_CLIENTE", "REGISTRO_CLIENTE"]


def test_continuar_exige_una_operacion_esperando_qa(tmp_path):
    runner, _ = _runner(tmp_path)
    with pytest.raises(ErrorContexto, match="No hay"):
        runner.continuar_tras_qa("999")
    runner.ejecutar(RECETAS["CN_REGISTRADO"], _ctx())
    with pytest.raises(ErrorContexto, match="no está esperando QA"):
        runner.continuar_tras_qa("240021110")


def test_receta_sin_pausa_no_se_detiene(tmp_path):
    runner, _ = _runner(tmp_path)
    r = runner.ejecutar(RECETAS["CN_REGISTRO_INTERMEDIO"].sin_pausa_qa(), _ctx())
    assert r.estado == "completada" and PAUSA_QA not in r.ejecutados


# --- fallas y reanudación ---

def test_una_falla_se_registra_y_detiene_la_receta(tmp_path):
    runner, bit = _runner(tmp_path, Bitacora(falla="CREAR_ID_CLIENTE"))
    r = runner.ejecutar(RECETAS["CN_REGISTRADO"], _ctx())
    assert (r.estado, r.modulo_fallido, r.error) == ("fallida", "CREAR_ID_CLIENTE", "falló CREAR_ID_CLIENTE")
    assert [n for n, _ in bit.llamadas] == ["RENOMBRAR_CLIENTE", "CREAR_ID_CLIENTE"]
    (entrada,) = runner.pendientes.pendientes()
    assert entrada["estado"] == "fallida" and entrada["paso_actual"] == "CREAR_ID_CLIENTE"
    log = LogOperacion("240021110", tmp_path / "logs")
    assert log.modulos_completados() == ["RENOMBRAR_CLIENTE"]  # el que falló quedó iniciado, no completado


def test_volver_a_ejecutar_retoma_en_el_modulo_que_fallo(tmp_path):
    runner, _ = _runner(tmp_path, Bitacora(falla="AGREEMENT"))
    runner.ejecutar(RECETAS["CN_REGISTRADO"], _ctx())

    runner2, bit2 = _runner(tmp_path)  # ya no falla
    r = runner2.ejecutar(RECETAS["CN_REGISTRADO"], _ctx())
    assert r.estado == "completada" and r.ejecutados == ["AGREEMENT", "REGISTRO_CLIENTE"]
    assert [n for n, _ in bit2.llamadas] == ["AGREEMENT", "REGISTRO_CLIENTE"]
    assert runner2.pendientes.pendientes() == []


# --- dry_run ---

def test_dry_run_corre_todo_incluida_la_pausa_y_no_persiste_nada(tmp_path):
    runner, bit = _runner(tmp_path, dry_run=True)
    r = runner.ejecutar(RECETAS["CN_REGISTRO_DISPERSADO"], _ctx())
    assert r.estado == "completada"
    assert [n for n, _ in bit.llamadas] == [p for p in RECETAS["CN_REGISTRO_DISPERSADO"].pasos if p != PAUSA_QA]
    assert all(dry for _, dry in bit.llamadas)
    assert not (tmp_path / "pendientes.json").exists() and not (tmp_path / "logs").exists()


def test_dry_run_con_falla_la_informa_sin_persistir(tmp_path):
    runner, _ = _runner(tmp_path, Bitacora(falla="AGREEMENT"), dry_run=True)
    r = runner.ejecutar(RECETAS["CF_REGISTRADO"], _ctx("CF"))
    assert (r.estado, r.modulo_fallido) == ("fallida", "AGREEMENT")
    assert not (tmp_path / "pendientes.json").exists()


# --- contexto y almacén ---

def test_contexto_ida_y_vuelta_a_dict():
    ctx = ContextoVenta(tipo="CF", numero_contrato="240021111", id_expediente=7331, con_seguro=False,
                        inicio=datetime(2026, 11, 8, 12, 30, 5))
    copia = ContextoVenta.desde_dict(ctx.a_dict(), fuente="F")
    assert (copia.tipo, copia.numero_contrato, copia.id_expediente, copia.con_seguro, copia.inicio) == (
        "CF", "240021111", 7331, False, datetime(2026, 11, 8, 12, 30, 5))
    assert copia.fuente == "F" and not copia.expediente_cargado  # el resto se recarga de la BD


class TestPendientesStore:
    def test_guardar_mezcla_campos_y_conserva_la_creacion(self, tmp_path):
        s = PendientesStore(tmp_path / "p.json")
        a = s.guardar("1", estado="en_curso", receta="X")
        b = s.guardar("1", estado="fallida", error="boom")
        assert b["estado"] == "fallida" and b["receta"] == "X" and b["creada"] == a["creada"]
        assert s.obtener("1")["error"] == "boom" and s.obtener("2") is None

    def test_pendientes_solo_los_retomables_mas_recientes_primero(self, tmp_path):
        s = PendientesStore(tmp_path / "p.json")
        for id_, estado in (("1", "completada"), ("2", "esperando_qa"), ("3", "fallida"), ("4", "en_curso")):
            s.guardar(id_, estado=estado)
        assert {e["operacion_id"] for e in s.pendientes()} == {"2", "3", "4"}
        assert {e["operacion_id"] for e in s.listar()} == {"1", "2", "3", "4"}

    def test_eliminar(self, tmp_path):
        s = PendientesStore(tmp_path / "p.json")
        s.guardar("1", estado="fallida")
        s.eliminar("1"); s.eliminar("1")
        assert s.listar() == []

    def test_archivo_dañado_falla_con_mensaje_claro(self, tmp_path):
        ruta = tmp_path / "p.json"
        ruta.write_text("{no es json", encoding="utf-8")
        with pytest.raises(ValueError, match="dañado"):
            PendientesStore(ruta).pendientes()

    def test_acentos_se_guardan_legibles(self, tmp_path):
        s = PendientesStore(tmp_path / "p.json")
        s.guardar("1", estado="esperando_qa", para_qa={"nombre_cliente": "JOSÉ"})
        assert "JOSÉ" in (tmp_path / "p.json").read_text(encoding="utf-8")
