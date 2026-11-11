import tkinter as tk

import pytest
from keyring.errors import KeyringError

from config.credentials import ConnectionSettings, CredentialStore
from services.connection_gate import HOSTS_ARRANQUE
from tests.test_credentials import FakeKeyring
from ui import selector_ui


@pytest.fixture
def ui(tmp_path, monkeypatch):
    """SelectorUI sin conexiones, sin ajustes y con un almacén falso (sin tocar el real ni un .env)."""
    try:
        probe = tk.Tk()
        probe.destroy()
    except tk.TclError:
        pytest.skip("sin pantalla para Tk")
    almacen = CredentialStore(path=tmp_path / "connections.json", backend=FakeKeyring())
    monkeypatch.setattr(selector_ui, "CredentialStore", lambda: almacen)
    monkeypatch.setattr(selector_ui, "ENV_LEGADO", tmp_path / "no_existe.env")
    monkeypatch.setattr(selector_ui, "USER_SETTINGS_PATH", tmp_path / "user_settings.json")
    selector = selector_ui.SelectorUI(config_path=tmp_path / "run_config.json")
    selector.almacen = almacen
    yield selector
    try:
        selector.root.destroy()
    except tk.TclError:
        pass


def _completar_conexiones(ui):
    for host in HOSTS_ARRANQUE:
        ui.almacen.save_connection(host, ConnectionSettings("srv", "usr", "pwd"))


def _completar_ajustes(ui, monkeypatch):
    ui.celular_var.set("5530262844")
    ui.correo_var.set("prueba@providigital.com")
    ui.nombre_ine_var.set("NAYELI BENITEZ PEREZ")
    ui.colaborador_var.set("04")
    monkeypatch.setattr(ui, "_estado_archivos", lambda: [("archivo", True, "")])


def test_sin_nada_configurado_se_abren_primero_las_conexiones_y_despues_los_ajustes(ui):
    assert ui._pasos_de_arranque() == ["conexiones", "ajustes"]


def test_con_las_conexiones_ya_guardadas_solo_faltan_los_ajustes(ui):
    _completar_conexiones(ui)

    assert ui._pasos_de_arranque() == ["ajustes"]


def test_con_los_ajustes_completos_solo_falta_la_conexion(ui, monkeypatch):
    _completar_ajustes(ui, monkeypatch)

    assert ui._pasos_de_arranque() == ["conexiones"]


def test_con_todo_completo_no_se_abre_nada(ui, monkeypatch):
    _completar_conexiones(ui)
    _completar_ajustes(ui, monkeypatch)

    assert ui._pasos_de_arranque() == []


def test_solo_se_exige_pesos_offer_al_arrancar(ui):
    assert HOSTS_ARRANQUE == ["PESOS_OFFER"]
    assert ui._conexiones_pendientes() == ["PESOS_OFFER"]


def test_sin_almacen_seguro_las_conexiones_cuentan_como_pendientes(ui, monkeypatch):
    def sin_almacen(*args, **kwargs):
        raise KeyringError("sin backend")

    monkeypatch.setattr(selector_ui, "hosts_sin_configurar", sin_almacen)

    assert ui._conexiones_pendientes() == ["PESOS_OFFER"]


def test_primer_arranque_abre_las_ventanas_en_orden(ui, monkeypatch):
    abiertas = []
    monkeypatch.setattr(
        selector_ui, "open_connections_dialog",
        lambda parent, store, hosts=None, mensaje="": abiertas.append(("conexiones", hosts)),
    )
    monkeypatch.setattr(ui, "_open_settings_dialog", lambda: abiertas.append(("ajustes", None)))

    ui._primer_arranque()

    assert abiertas == [("conexiones", HOSTS_ARRANQUE), ("ajustes", None)]


def test_primer_arranque_abre_la_segunda_ventana_aunque_se_cierre_la_primera_sin_guardar(ui, monkeypatch):
    abiertas = []
    monkeypatch.setattr(selector_ui, "open_connections_dialog", lambda *a, **k: abiertas.append("conexiones") or False)
    monkeypatch.setattr(ui, "_open_settings_dialog", lambda: abiertas.append("ajustes"))

    ui._primer_arranque()

    assert abiertas == ["conexiones", "ajustes"]
    assert ui._conexiones_pendientes()  # sigue pendiente: el gate sigue bloqueado


def test_el_gate_bloquea_el_menu_y_nombra_lo_que_falta(ui):
    assert str(ui.insumo_combo.cget("state")) == "disabled"
    aviso = ui.ajustes_aviso.cget("text")

    assert "Pesos_Offer" in aviso and "Nombre como aparece en la INE" in aviso


def test_el_gate_se_libera_al_completar_conexiones_y_ajustes(ui, monkeypatch):
    _completar_conexiones(ui)
    _completar_ajustes(ui, monkeypatch)

    ui._actualizar_gate_ajustes()

    assert str(ui.insumo_combo.cget("state")) == "readonly"
