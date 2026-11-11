"""Pruebas unitarias de la UI de recetas: la lógica detrás de los botones y un humo de los widgets."""
import tkinter as tk

import pytest

from config.credentials import ConnectionSettings, CredentialStore
from config.databases import HOSTS
from config.settings import Settings
from insumos.deshacer import ResultadoDeshacer
from insumos.pendientes import COMPLETADA, EN_CURSO, ESPERANDO_QA, FALLIDA, PendientesStore
from insumos.recetas import RECETAS
from insumos.runner import ResultadoReceta
from tests.test_credentials import FakeKeyring
from ui import recetas_ui
from ui.recetas_ui import (
    CONTINUAR, DESHACER, REANUDAR, SIN_RECETA, acciones_de, confirmar_qa, describir_pendiente,
    ejecutar_accion, etiquetas_recetas, filas_en_pausa, fijar_colaborador, receta_id_de_etiqueta,
)
from ui.results_ui import contar_estados

CONTRATO = "240021112"


class RunnerFalso:
    def __init__(self, resultado=None, deshacer=None, error=None):
        self.resultado, self.res_deshacer, self.error, self.llamadas = resultado, deshacer, error, []

    def _responder(self, nombre, operacion_id):
        self.llamadas.append((nombre, operacion_id))
        if self.error:
            raise self.error
        return self.resultado

    def continuar_tras_qa(self, operacion_id):
        return self._responder("continuar", operacion_id)

    def reanudar(self, operacion_id):
        return self._responder("reanudar", operacion_id)

    def deshacer(self, operacion_id):
        self.llamadas.append(("deshacer", operacion_id))
        return self.res_deshacer


def res(estado, **kw):
    return ResultadoReceta("CN_REGISTRO_INTERMEDIO", CONTRATO, estado, **kw)


@pytest.fixture
def store(tmp_path):
    s = PendientesStore(tmp_path / "pendientes.json")
    s.guardar(CONTRATO, estado=ESPERANDO_QA, receta="CN_REGISTRO_INTERMEDIO",
              para_qa={"numero_contrato": CONTRATO, "fecha_nacimiento": "1996-09-15", "nombre_cliente": "SILVIA"})
    return s


def slot_en_pausa(estado=ESPERANDO_QA):
    return {"estado": estado, "intentos": 1, "detalle": "En pausa de QA", "venta_ok": True,
            "config": {"receta": "CN_REGISTRO_INTERMEDIO"}, "venta": {"numero_contrato": CONTRATO}}


# ---------- elegir receta ----------

def test_el_desplegable_ofrece_solo_las_recetas_del_tipo_y_la_receta_es_obligatoria():
    cn, cf = etiquetas_recetas("CN"), etiquetas_recetas("CF")
    assert set(cn) == {r.nombre for r in RECETAS.values() if r.tipo_venta == "CN"}
    assert set(cf) == {r.nombre for r in RECETAS.values() if r.tipo_venta == "CF"}
    assert SIN_RECETA not in cn + cf and not set(cn) & set(cf)
    assert etiquetas_recetas("CF", con_sin_receta=True) == [SIN_RECETA] + cf


def test_la_etiqueta_elegida_se_convierte_en_el_id_de_la_receta():
    for receta in RECETAS.values():
        assert receta_id_de_etiqueta(receta.tipo_venta, receta.nombre) == receta.id


def test_sin_receta_o_una_de_otro_tipo_no_genera_receta():
    assert receta_id_de_etiqueta("CN", SIN_RECETA) is None
    assert receta_id_de_etiqueta("CN", RECETAS["CF_DISPERSADO"].nombre) is None  # el tipo cambió tras elegir
    assert receta_id_de_etiqueta("CN", "inventada") is None


# ---------- colaborador ----------

def test_el_colaborador_sale_de_la_corrida_y_si_no_de_los_ajustes(monkeypatch, tmp_path):
    ajustes = tmp_path / "user_settings.json"
    ajustes.write_text('{"numero_colaborador": "09"}', encoding="utf-8")
    monkeypatch.setattr(Settings, "NUMERO_COLABORADOR", "")
    fijar_colaborador({"numero_colaborador": "07"}, ajustes)
    assert Settings.NUMERO_COLABORADOR == "07"
    monkeypatch.setattr(Settings, "NUMERO_COLABORADOR", "")
    fijar_colaborador(None, ajustes)
    assert Settings.NUMERO_COLABORADOR == "09"


def test_sin_colaborador_en_ningun_lado_no_toca_el_valor_actual(monkeypatch, tmp_path):
    monkeypatch.setattr(Settings, "NUMERO_COLABORADOR", "04")
    fijar_colaborador({}, tmp_path / "no_existe.json")
    assert Settings.NUMERO_COLABORADOR == "04"
    dañado = tmp_path / "roto.json"
    dañado.write_text("{no es json", encoding="utf-8")
    fijar_colaborador({}, dañado)
    assert Settings.NUMERO_COLABORADOR == "04"


# ---------- pausa de QA ----------

def test_filas_en_pausa_trae_lo_que_qa_necesita_y_solo_los_slots_en_pausa(store):
    slots = {"CN": [slot_en_pausa(), slot_en_pausa("exitosa"), slot_en_pausa("fallida")], "CF": [], "OF": []}
    filas = filas_en_pausa(slots, store)
    assert len(filas) == 1
    assert (filas[0]["tipo"], filas[0]["contrato"], filas[0]["fecha_nacimiento"], filas[0]["nombre_cliente"]) == \
        ("CN", CONTRATO, "1996-09-15", "SILVIA")


def test_confirmar_qa_completa_la_receta_y_deja_el_slot_exitoso(store):
    slot, runner = slot_en_pausa(), RunnerFalso(res("completada"))
    confirmar_qa(slot, runner, store)
    assert runner.llamadas == [("continuar", CONTRATO)]
    assert slot["estado"] == "exitosa" and CONTRATO in slot["detalle"]


def test_confirmar_qa_con_falla_deja_el_slot_fallido_para_reintentar(store):
    slot = slot_en_pausa()
    confirmar_qa(slot, RunnerFalso(res("fallida", modulo_fallido="REGISTRO_CLIENTE", error="sin conexión")), store)
    assert slot["estado"] == "fallida" and "REGISTRO_CLIENTE" in slot["detalle"] and "sin conexión" in slot["detalle"]


def test_confirmar_qa_si_ya_se_completo_por_otro_lado_solo_sincroniza_el_slot(store):
    store.guardar(CONTRATO, estado=COMPLETADA)
    slot, runner = slot_en_pausa(), RunnerFalso(res("completada"))
    confirmar_qa(slot, runner, store)
    assert slot["estado"] == "exitosa" and runner.llamadas == []


def test_confirmar_qa_propaga_el_error_y_conserva_la_pausa(store):
    slot = slot_en_pausa()
    with pytest.raises(RuntimeError):
        confirmar_qa(slot, RunnerFalso(error=RuntimeError("sin VPN")), store)
    assert slot["estado"] == ESPERANDO_QA


# ---------- contadores de resultados ----------

def test_esperando_qa_no_cuenta_como_pendiente_ni_como_exitosa():
    slots = {"CN": [slot_en_pausa(), slot_en_pausa("exitosa"), slot_en_pausa("fallida"), slot_en_pausa("pendiente")],
             "CF": [], "OF": [], "AGENCIA": []}
    assert contar_estados(slots) == {"total": 4, "ok": 1, "qa": 1, "pendientes": 2}


# ---------- retomar ----------

def test_acciones_segun_el_estado():
    assert acciones_de({"estado": ESPERANDO_QA}) == [CONTINUAR, DESHACER]
    assert acciones_de({"estado": EN_CURSO}) == [REANUDAR, DESHACER]
    assert acciones_de({"estado": FALLIDA}) == [REANUDAR, DESHACER]


@pytest.mark.parametrize("accion,metodo", [(CONTINUAR, "continuar"), (REANUDAR, "reanudar")])
def test_continuar_y_reanudar_informan_el_resultado(accion, metodo):
    runner = RunnerFalso(res("completada"))
    ok, mensaje = ejecutar_accion(accion, CONTRATO, runner)
    assert ok and CONTRATO in mensaje and runner.llamadas == [(metodo, CONTRATO)]
    assert ejecutar_accion(accion, CONTRATO, RunnerFalso(res("esperando_qa"))) == \
        (True, f"Receta CN_REGISTRO_INTERMEDIO: sigue en pausa de QA (contrato {CONTRATO}).")
    ok, mensaje = ejecutar_accion(accion, CONTRATO, RunnerFalso(res("fallida", modulo_fallido="AGREEMENT", error="x")))
    assert not ok and "AGREEMENT" in mensaje


def test_deshacer_informa_lo_revertido_y_marca_error_si_hay_conflictos():
    limpio = ResultadoDeshacer(CONTRATO, deshechas=["a", "b"])
    runner = RunnerFalso(deshacer=limpio)
    assert ejecutar_accion(DESHACER, CONTRATO, runner) == (True, f"Se revirtieron 2 escritura(s) del contrato {CONTRATO}.")
    assert runner.llamadas == [("deshacer", CONTRATO)]
    conflicto = ResultadoDeshacer(CONTRATO, deshechas=["a"], omitidas=[("Customer", "conflicto: cambió")])
    ok, mensaje = ejecutar_accion(DESHACER, CONTRATO, RunnerFalso(deshacer=conflicto))
    assert not ok and "conflictos" in mensaje


def test_el_detalle_de_cada_fila_dice_lo_util_para_ese_estado():
    assert "1996-09-15" in describir_pendiente({"estado": ESPERANDO_QA, "para_qa": {"fecha_nacimiento": "1996-09-15"}})
    assert describir_pendiente({"estado": FALLIDA, "paso_actual": "AGREEMENT", "error": "timeout"}) == "paso AGREEMENT · timeout"
    assert describir_pendiente({"estado": EN_CURSO}) == ""


def test_retomar_pendientes_no_abre_nada_si_no_hay_o_si_el_archivo_esta_danado(tmp_path, monkeypatch, capsys):
    abiertas = []
    monkeypatch.setattr(recetas_ui, "RetomarUI", lambda p: type("U", (), {"run": lambda s: abiertas.append(p)})())
    recetas_ui.retomar_pendientes(PendientesStore(tmp_path / "vacio.json"))
    roto = tmp_path / "roto.json"
    roto.write_text("{no es json", encoding="utf-8")
    recetas_ui.retomar_pendientes(PendientesStore(roto))
    assert abiertas == [] and "no se pudieron leer" in capsys.readouterr().out


def test_retomar_pendientes_abre_la_ventana_cuando_hay_operaciones(store, monkeypatch):
    abiertas = []
    monkeypatch.setattr(recetas_ui, "RetomarUI", lambda p: type("U", (), {"run": lambda s: abiertas.append(p)})())
    recetas_ui.retomar_pendientes(store)
    assert abiertas == [store]


# ---------- humo de los widgets (se construyen y destruyen sin mainloop) ----------

@pytest.fixture
def tk_ok():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("sin pantalla para Tk")
    root.destroy()


def test_resultados_se_construye_con_una_operacion_en_pausa(tk_ok, store, monkeypatch):
    monkeypatch.setattr(recetas_ui, "PendientesStore", lambda *a, **k: store)
    monkeypatch.setattr(Settings, "NUMERO_COLABORADOR", "04")  # ResultsUI lo puede sobrescribir; se restaura
    from ui.results_ui import ResultsUI

    slots = {"OF": [], "AGENCIA": [], "CF": [], "CN": [slot_en_pausa(), slot_en_pausa("exitosa")]}
    ui = ResultsUI({"ventas_batches": [{"agencia_label": "Izcalli 335"}]}, slots, 1)
    try:
        assert len(ui.panel_qa.frame.winfo_children()) == 1  # la caja "Esperando QA"
        filas = [ui.tree.item(i, "values") for i in ui.tree.get_children()]
        assert [f[2] for f in filas] == ["⏸ Esperando QA", "✔ Exitosa"]
        assert "Reintentar pendientes (0)" in ui.retry.cget("text") and str(ui.retry.cget("state")) == "disabled"
        assert "esperando a QA" in ui.banner_label.cget("text")
    finally:
        ui.root.destroy()


def test_resultados_sin_pausa_no_muestra_el_panel(tk_ok, monkeypatch):
    monkeypatch.setattr(Settings, "NUMERO_COLABORADOR", "04")
    from ui.results_ui import ResultsUI

    ui = ResultsUI({"ofertas": []}, {"OF": [], "AGENCIA": [], "CF": [], "CN": [slot_en_pausa("exitosa")]}, 1)
    try:
        assert ui.panel_qa.frame.winfo_children() == []
    finally:
        ui.root.destroy()


def test_la_ventana_de_retomar_lista_las_operaciones_y_habilita_segun_el_estado(tk_ok, store):
    ui = recetas_ui.RetomarUI(store, runner=RunnerFalso(res("completada")))
    try:
        assert ui.tree.get_children() == (CONTRATO,)
        ui.tree.selection_set(CONTRATO)
        ui._actualizar_botones()
        assert str(ui.botones[CONTINUAR].cget("state")) == "normal"
        assert str(ui.botones[REANUDAR].cget("state")) == "disabled"
        assert str(ui.botones[DESHACER].cget("state")) == "normal"
    finally:
        ui.root.destroy()


# ---------- insumo "Registrar Cliente" en el selector ----------

@pytest.fixture
def selector(tk_ok, tmp_path, monkeypatch):
    from ui import selector_ui

    monkeypatch.setattr(selector_ui, "USER_SETTINGS_PATH", tmp_path / "user_settings.json")
    # Almacén de conexiones falso con todos los hosts configurados (no toca el Administrador de
    # credenciales real) y sin un .env legado que importar.
    almacen = CredentialStore(path=tmp_path / "connections.json", backend=FakeKeyring())
    for host in HOSTS:
        almacen.save_connection(host, ConnectionSettings("srv", "usr", "pwd"))
    monkeypatch.setattr(selector_ui, "CredentialStore", lambda: almacen)
    monkeypatch.setattr(selector_ui, "ENV_LEGADO", tmp_path / "no_existe.env")
    ui = selector_ui.SelectorUI(config_path=tmp_path / "run_config.json")
    if not ui.agencias or not ui.metodos:
        ui.root.destroy()
        pytest.skip("sin catálogo de agencias/métodos")
    yield ui
    try:
        ui.root.destroy()
    except tk.TclError:  # _on_confirm ya la destruyó
        pass


def elegir(ui, texto):
    ui.insumo_label_var.set(texto)
    ui._on_insumo_changed()


def test_registrar_cliente_es_un_insumo_aparte_y_venta_no_ofrece_recetas(selector):
    from ui.selector_ui import INSUMOS

    assert ("REGISTRO", "Registrar Cliente") in INSUMOS
    elegir(selector, "Venta (CN / CF)")
    assert not any("receta_combo" in r for r in selector.ventas_rows)
    assert all("receta_var" not in r for r in selector.ventas_rows)
    assert selector.step2_title.cget("text") == "Ventas"
    elegir(selector, "Registrar Cliente")
    assert selector.step2_title.cget("text") == "Registrar Cliente"
    assert selector.confirm_btn.cget("text") == "▶  Registrar Cliente"
    fila = selector.registro_rows[0]
    assert fila["receta_combo"].cget("values") == tuple(etiquetas_recetas("CN"))
    assert fila["receta_var"].get() == etiquetas_recetas("CN")[0]  # la receta es obligatoria: sin 'Sin receta'


def test_los_lotes_de_cada_insumo_son_independientes(selector):
    elegir(selector, "Registrar Cliente")
    selector._agregar_fila_venta()
    assert (len(selector.registro_rows), len(selector.ventas_rows)) == (2, 1)
    elegir(selector, "Venta (CN / CF)")
    assert len(selector._filas_lotes()) == 1


def test_al_cambiar_el_tipo_del_lote_la_receta_es_de_ese_tipo(selector):
    elegir(selector, "Registrar Cliente")
    fila = selector.registro_rows[0]
    fila["tipo_var"].set("CF")
    selector._on_tipo_lote_cambiado(fila)
    assert fila["receta_combo"].cget("values") == tuple(etiquetas_recetas("CF"))
    assert fila["receta_var"].get() == etiquetas_recetas("CF")[0]


def configurar(selector, monkeypatch, tmp_path):
    from ui import selector_ui

    avisos = []
    monkeypatch.setattr(selector_ui.messagebox, "showwarning", lambda *a, **k: avisos.append(a))
    monkeypatch.setattr(selector_ui, "verificar_vpn", lambda **k: (True, []))
    selector.user_settings.update(nombre_ine="NAYELI BENITEZ PEREZ", numero_colaborador="04")
    selector.nombre_ine_var.set("NAYELI BENITEZ PEREZ")
    selector.colaborador_var.set("04")
    selector.celular_var.set("5530262844")
    selector.correo_var.set("prueba@providigital.com")
    return avisos


def test_confirmar_registrar_cliente_genera_lotes_con_receta(selector, monkeypatch, tmp_path):
    import json

    avisos = configurar(selector, monkeypatch, tmp_path)
    monkeypatch.setattr(selector, "_ajustes_completos", lambda: (True, []))
    elegir(selector, "Registrar Cliente")
    fila = selector.registro_rows[0]
    fila["agencia_var"].set(selector.agencias[0]["label"])
    fila["metodo_var"].set(selector.metodos[0]["nombre"])
    fila["receta_var"].set("CN registrado")
    selector._on_confirm()
    assert avisos == [] and selector.confirmed
    lote = json.loads(selector.config_path.read_text(encoding="utf-8"))["ventas_batches"][0]
    assert lote["receta"] == "CN_REGISTRADO" and lote["tipo_cliente"] == "CN"


def test_confirmar_venta_nunca_lleva_receta(selector, monkeypatch, tmp_path):
    import json

    configurar(selector, monkeypatch, tmp_path)
    monkeypatch.setattr(selector, "_ajustes_completos", lambda: (True, []))
    elegir(selector, "Venta (CN / CF)")
    fila = selector.ventas_rows[0]
    fila["agencia_var"].set(selector.agencias[0]["label"])
    fila["metodo_var"].set(selector.metodos[0]["nombre"])
    selector._on_confirm()
    assert selector.confirmed
    assert "receta" not in json.loads(selector.config_path.read_text(encoding="utf-8"))["ventas_batches"][0]
