import json
import sys

import pytest
from keyring.errors import NoKeyringError, PasswordDeleteError

from config.credentials import (
    DRIVER_POR_DEFECTO,
    SERVICE,
    ConnectionSettings,
    CredentialsMissing,
    CredentialStore,
    EstrellaCredentials,
)
from utils.paths import APP_NAME, app_data_dir


class FakeKeyring:
    """Backend en memoria con la misma interfaz que el módulo keyring."""

    def __init__(self):
        self.guardado = {}

    def get_keyring(self):
        return self

    def set_password(self, servicio, usuario, password):
        self.guardado[(servicio, usuario)] = password

    def get_password(self, servicio, usuario):
        return self.guardado.get((servicio, usuario))

    def delete_password(self, servicio, usuario):
        try:
            del self.guardado[(servicio, usuario)]
        except KeyError:
            raise PasswordDeleteError("no existe") from None


class BackendRoto(FakeKeyring):
    def set_password(self, servicio, usuario, password):
        raise NoKeyringError("sin backend")


@pytest.fixture
def backend():
    return FakeKeyring()


@pytest.fixture
def store(tmp_path, backend):
    return CredentialStore(path=tmp_path / "connections.json", backend=backend)


CONEXION = ConnectionSettings(server="srv,1433", user="sa", password="p;a{ss}=1", driver="ODBC Driver 18 for SQL Server")


def test_conexion_ida_y_vuelta(store):
    store.save_connection("PESOS_OFFER", CONEXION)

    assert store.get_connection("PESOS_OFFER") == CONEXION
    assert store.list_hosts() == ["PESOS_OFFER"]


def test_la_contrasena_nunca_se_escribe_en_disco(store, backend, tmp_path):
    store.save_connection("PESOS_OFFER", CONEXION)
    store.save_estrella(EstrellaCredentials("qa1", "2075000000001", "Secreta*1"))

    contenido = (tmp_path / "connections.json").read_text(encoding="utf-8")

    assert "p;a{ss}=1" not in contenido
    assert "Secreta*1" not in contenido
    assert backend.guardado[(SERVICE, "host:PESOS_OFFER")] == "p;a{ss}=1"
    assert backend.guardado[(SERVICE, "estrella:qa1")] == "Secreta*1"


def test_host_sin_configurar_lanza_credentials_missing(store):
    with pytest.raises(CredentialsMissing) as e:
        store.get_connection("CNFS")

    assert "CNFS" in str(e.value)


def test_host_sin_contrasena_en_el_almacen_lanza_credentials_missing(store, backend):
    store.save_connection("CNFS", CONEXION)
    backend.guardado.clear()  # p. ej. el usuario borró la entrada desde Windows

    with pytest.raises(CredentialsMissing):
        store.get_connection("CNFS")


def test_driver_vacio_usa_el_de_por_defecto(store):
    store.save_connection("CNFS", ConnectionSettings(server="s", user="u", password="p", driver=""))

    assert store.get_connection("CNFS").driver == DRIVER_POR_DEFECTO


def test_borrar_conexion_limpia_json_y_almacen(store, backend):
    store.save_connection("CNFS", CONEXION)

    store.delete_connection("CNFS")

    assert store.list_hosts() == []
    assert backend.guardado == {}
    store.delete_connection("CNFS")  # borrar algo inexistente no falla


def test_varias_estrellas_ordenadas_por_alias(store):
    store.save_estrella(EstrellaCredentials("zeta", "222", "p2"))
    store.save_estrella(EstrellaCredentials("alfa", "111", "p1"))

    assert store.list_estrellas() == [("alfa", "111"), ("zeta", "222")]
    assert store.get_estrella("zeta") == EstrellaCredentials("zeta", "222", "p2")


def test_estrella_inexistente_lanza_credentials_missing(store):
    with pytest.raises(CredentialsMissing):
        store.get_estrella("nadie")


def test_borrar_estrella(store, backend):
    store.save_estrella(EstrellaCredentials("qa1", "111", "p"))

    store.delete_estrella("qa1")

    assert store.list_estrellas() == []
    assert backend.guardado == {}


@pytest.mark.parametrize("host,servidor,usuario", [("", "s", "u"), ("H", " ", "u"), ("H", "s", "")])
def test_no_guarda_conexiones_con_campos_vacios(store, host, servidor, usuario):
    with pytest.raises(ValueError):
        store.save_connection(host, ConnectionSettings(servidor, usuario, "p"))

    assert store.list_hosts() == []


def test_json_corrupto_se_trata_como_vacio(tmp_path, backend):
    ruta = tmp_path / "connections.json"
    ruta.write_text("{ no es json", encoding="utf-8")
    store = CredentialStore(path=ruta, backend=backend)

    assert store.list_hosts() == []
    store.save_connection("CNFS", CONEXION)  # y se puede volver a escribir
    assert json.loads(ruta.read_text(encoding="utf-8"))["hosts"]["CNFS"]["server"] == "srv,1433"


def test_backend_disponible_con_almacen_funcional(store, backend):
    ok, detalle = store.backend_disponible()

    assert ok is True
    assert detalle == "FakeKeyring"
    assert backend.guardado == {}  # la entrada de prueba no queda


def test_backend_no_disponible_informa_el_motivo(tmp_path):
    store = CredentialStore(path=tmp_path / "connections.json", backend=BackendRoto())

    ok, detalle = store.backend_disponible()

    assert ok is False
    assert "sin backend" in detalle


def test_app_data_dir_desde_codigo_fuente_es_data_del_repo():
    assert app_data_dir().name == "data"


def test_app_data_dir_congelado_usa_localappdata(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))

    carpeta = app_data_dir()

    assert carpeta == tmp_path / APP_NAME
    assert carpeta.is_dir()
