import pytest

from config.credentials import ConnectionSettings, CredentialStore
from config.legacy_env import importar_env, leer_env
from tests.test_credentials import FakeKeyring


@pytest.fixture
def store(tmp_path):
    return CredentialStore(path=tmp_path / "connections.json", backend=FakeKeyring())


def _env(tmp_path, texto):
    ruta = tmp_path / ".env"
    ruta.write_text(texto, encoding="utf-8")
    return ruta


def test_leer_env_ignora_comentarios_export_y_comillas(tmp_path):
    ruta = _env(tmp_path, "# nota\n\nA=1\nexport B = \"dos\"\nC='tres'\nD=con=igual\nsin_igual\n")

    assert leer_env(ruta) == {"A": "1", "B": "dos", "C": "tres", "D": "con=igual"}


def test_importa_botdb_como_pesos_offer_y_el_resto_por_su_nombre(tmp_path, store):
    ruta = _env(tmp_path, (
        "BOTDB_SERVER=srv1,1433\nBOTDB_USER=u1\nBOTDB_PASSWORD=p;1\nBOTDB_DRIVER=ODBC Driver 18 for SQL Server\n"
        "CHALLENGER_SERVER=srv2\nCHALLENGER_USER=u2\nCHALLENGER_PASSWORD=p2\n"
        "ESTRELLA=123\nPASSWORD=no_se_importa\n"
    ))

    assert importar_env(store, ruta) == ["PESOS_OFFER", "CHALLENGER"]

    c = store.get_connection("PESOS_OFFER")
    assert (c.server, c.user, c.password, c.driver) == ("srv1,1433", "u1", "p;1", "ODBC Driver 18 for SQL Server")
    assert store.get_connection("CHALLENGER").driver == "ODBC Driver 17 for SQL Server"
    assert store.list_hosts() == ["CHALLENGER", "PESOS_OFFER"]


def test_acepta_los_nombres_de_host_de_recetas(tmp_path, store):
    ruta = _env(tmp_path, "PESOS_OFFER_SERVER=s\nPESOS_OFFER_USER=u\nPESOS_OFFER_PASSWORD=p\n"
                          "CNFS_SERVER=s\nCNFS_USER=u\nCNFS_PASSWORD=p\n")

    assert importar_env(store, ruta) == ["PESOS_OFFER", "CNFS"]


def test_no_pisa_un_host_ya_configurado(tmp_path, store):
    store.save_connection("PESOS_OFFER", ConnectionSettings("viejo", "u", "pviejo"))
    ruta = _env(tmp_path, "BOTDB_SERVER=nuevo\nBOTDB_USER=u\nBOTDB_PASSWORD=pnueva\n")

    assert importar_env(store, ruta) == []
    assert store.get_connection("PESOS_OFFER").server == "viejo"


def test_omite_hosts_incompletos(tmp_path, store):
    ruta = _env(tmp_path, "BOTDB_SERVER=s\nBOTDB_USER=u\n")  # sin contraseña

    assert importar_env(store, ruta) == []
    assert store.list_hosts() == []


def test_segunda_importacion_no_hace_nada(tmp_path, store):
    ruta = _env(tmp_path, "BOTDB_SERVER=s\nBOTDB_USER=u\nBOTDB_PASSWORD=p\n")

    assert importar_env(store, ruta) == ["PESOS_OFFER"]
    assert importar_env(store, ruta) == []
