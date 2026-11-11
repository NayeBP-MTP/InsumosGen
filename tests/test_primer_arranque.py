import tkinter as tk

import pytest
from keyring.errors import KeyringError

from config.credentials import ConnectionSettings, CredentialStore
from services.connection_gate import HOSTS_ARRANQUE
from tests.test_credentials import FakeKeyring
from ui import selector_ui
from utils import prereqs


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
    # Chrome y el driver ODBC "instalados" por defecto, para no depender de la máquina que corre la prueba.
    monkeypatch.setattr(selector_ui, "prerrequisitos_faltantes", lambda: [])
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


CHROME_FALTA = prereqs.Prerrequisito("Google Chrome", False, "No se encontró Google Chrome.", "https://chrome.test")
DRIVER_FALTA = prereqs.Prerrequisito("ODBC Driver", False, "No se encontró el driver.", "https://odbc.test")


def test_los_programas_faltantes_se_avisan_antes_que_las_conexiones_y_los_ajustes(ui, monkeypatch):
    monkeypatch.setattr(selector_ui, "prerrequisitos_faltantes", lambda: [CHROME_FALTA])

    assert ui._pasos_de_arranque() == ["prerrequisitos", "conexiones", "ajustes"]


def test_primer_arranque_avisa_de_los_programas_y_luego_sigue_con_el_resto(ui, monkeypatch):
    monkeypatch.setattr(selector_ui, "prerrequisitos_faltantes", lambda: [CHROME_FALTA])
    abiertas = []
    monkeypatch.setattr(ui, "_avisar_prerrequisitos", lambda: abiertas.append("prerrequisitos"))
    monkeypatch.setattr(selector_ui, "open_connections_dialog", lambda *a, **k: abiertas.append("conexiones"))
    monkeypatch.setattr(ui, "_open_settings_dialog", lambda: abiertas.append("ajustes"))

    ui._primer_arranque()

    assert abiertas == ["prerrequisitos", "conexiones", "ajustes"]


def test_el_aviso_ofrece_abrir_las_descargas(ui, monkeypatch):
    monkeypatch.setattr(selector_ui, "prerrequisitos_faltantes", lambda: [CHROME_FALTA, DRIVER_FALTA])
    mensajes, abiertas = [], []
    monkeypatch.setattr(selector_ui.messagebox, "askyesno", lambda titulo, texto, **k: mensajes.append(texto) or True)
    monkeypatch.setattr(selector_ui.webbrowser, "open", abiertas.append)

    ui._avisar_prerrequisitos()

    assert abiertas == ["https://chrome.test", "https://odbc.test"]
    assert "Google Chrome" in mensajes[0] and "No se encontró el driver." in mensajes[0]


def test_si_se_rechaza_el_aviso_no_se_abre_nada(ui, monkeypatch):
    monkeypatch.setattr(selector_ui, "prerrequisitos_faltantes", lambda: [CHROME_FALTA])
    abiertas = []
    monkeypatch.setattr(selector_ui.messagebox, "askyesno", lambda *a, **k: False)
    monkeypatch.setattr(selector_ui.webbrowser, "open", abiertas.append)

    ui._avisar_prerrequisitos()

    assert abiertas == []


def test_sin_programas_faltantes_no_hay_aviso(ui, monkeypatch):
    monkeypatch.setattr(selector_ui.messagebox, "askyesno", lambda *a, **k: (_ for _ in ()).throw(AssertionError()))

    ui._avisar_prerrequisitos()


def test_el_gate_pide_instalar_lo_que_falta_y_se_libera_al_instalarlo(ui, monkeypatch):
    _completar_conexiones(ui)
    _completar_ajustes(ui, monkeypatch)
    faltan = [CHROME_FALTA]
    monkeypatch.setattr(selector_ui, "prerrequisitos_faltantes", lambda: list(faltan))

    ui._actualizar_gate_ajustes()
    assert str(ui.insumo_combo.cget("state")) == "disabled"
    assert "Instalar Google Chrome" in ui.ajustes_aviso.cget("text")

    faltan.clear()  # el usuario instaló Chrome y volvió a la ventana
    ui._al_enfocar(type("Evento", (), {"widget": ui.root})())

    assert str(ui.insumo_combo.cget("state")) == "readonly"


def test_confirmar_sin_los_programas_no_inicia_la_ejecucion(ui, monkeypatch):
    monkeypatch.setattr(selector_ui, "prerrequisitos_faltantes", lambda: [DRIVER_FALTA])
    errores = []
    monkeypatch.setattr(selector_ui.messagebox, "showerror", lambda titulo, texto, **k: errores.append(texto))

    ui._on_confirm()

    assert "ODBC Driver" in errores[0]
    assert ui.confirmed is False
