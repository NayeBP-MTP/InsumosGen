import pytest

from config.credentials import ConnectionSettings, CredentialsMissing, CredentialStore
from services import agency_repository, offer_repository
from tests.test_credentials import FakeKeyring
from utils import vpn_check


CONEXION = ConnectionSettings(server="srv,1433", user="sa", password="p;a}ss", driver="ODBC Driver 18 for SQL Server")


@pytest.fixture
def almacen(tmp_path, monkeypatch):
    """Cada módulo que antes leía el .env obtiene un almacén aislado (sin tocar el real)."""
    store = CredentialStore(path=tmp_path / "connections.json", backend=FakeKeyring())
    for modulo in (offer_repository, agency_repository, vpn_check):
        monkeypatch.setattr(modulo, "CredentialStore", lambda: store)
    return store


@pytest.mark.parametrize("clase,host,base", [
    (offer_repository.OfferRepository, "PESOS_OFFER", "botDB"),
    (agency_repository.BotDbAgencyRepository, "PESOS_OFFER", "botDB"),
    (agency_repository.ChallengerRepository, "CHALLENGER", "Challenger_uat"),
])
def test_repositorio_conecta_con_las_credenciales_del_almacen(almacen, monkeypatch, clase, host, base):
    almacen.save_connection(host, CONEXION)
    cadenas = []
    monkeypatch.setattr("pyodbc.connect", lambda cadena, *a, **k: cadenas.append(cadena) or object())

    clase()._get_connection()

    assert cadenas == [CONEXION.connection_string(base)]
    assert "PWD={p;a}}ss};" in cadenas[0]


@pytest.mark.parametrize("clase", [
    offer_repository.OfferRepository, agency_repository.BotDbAgencyRepository,
    agency_repository.ChallengerRepository,
])
def test_repositorio_sin_host_configurado_lanza_credentials_missing(almacen, clase):
    with pytest.raises(CredentialsMissing):
        clase()


def test_repositorio_acepta_una_conexion_explicita(almacen):
    repo = offer_repository.OfferRepository(conexion=CONEXION)

    assert repo.conexion is CONEXION


def test_verificar_vpn_host_sin_configurar_lo_indica(almacen, monkeypatch):
    monkeypatch.setattr(vpn_check, "_alcanzable", lambda host, puerto: True)

    ok, problemas = vpn_check.verificar_vpn(requiere_bd=True)

    assert not ok
    assert "PESOS_OFFER" in problemas[0] and "Conexiones y estrellas" in problemas[0]


def test_verificar_vpn_comprueba_el_servidor_del_almacen(almacen, monkeypatch):
    almacen.save_connection("PESOS_OFFER", CONEXION)
    consultados = []
    monkeypatch.setattr(vpn_check, "_alcanzable", lambda host, puerto: consultados.append((host, puerto)) or host != "srv")

    ok, faltantes = vpn_check.verificar_vpn(requiere_bd=True)

    assert ("srv", 1433) in consultados
    assert not ok and faltantes == ["Base de datos botDB (srv:1433)"]


def test_verificar_vpn_sin_bd_no_consulta_el_almacen(almacen, monkeypatch):
    monkeypatch.setattr(vpn_check, "_alcanzable", lambda host, puerto: True)

    assert vpn_check.verificar_vpn(requiere_bd=False) == (True, [])
