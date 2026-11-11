import pytest

from config.credentials import ConnectionSettings, CredentialsMissing, CredentialStore
from services import agency_repository, db, offer_repository
from tests.test_credentials import FakeKeyring


CONEXION = ConnectionSettings(server="srv,1433", user="sa", password="p;a}ss", driver="ODBC Driver 18 for SQL Server")


@pytest.fixture
def almacen(tmp_path, monkeypatch):
    """`services.db` (único punto de lectura de las conexiones) obtiene un almacén aislado."""
    store = CredentialStore(path=tmp_path / "connections.json", backend=FakeKeyring())
    monkeypatch.setattr(db, "CredentialStore", lambda: store)
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
def test_repositorio_sin_host_configurado_falla_al_conectar_no_al_construir(almacen, clase):
    repo = clase()

    with pytest.raises(CredentialsMissing):
        repo._get_connection()


def test_repositorio_acepta_un_almacen_explicito(almacen):
    almacen.save_connection("PESOS_OFFER", CONEXION)

    repo = db.SqlServerRepository("botDB", store=almacen)

    assert repo.credenciales == CONEXION
