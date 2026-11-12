import pytest

from config.credentials import ConnectionSettings, CredentialStore
from services import connection_gate as gate
from services.connection_tester import Categoria, ResultadoConexion
from tests.test_credentials import FakeKeyring


CONEXION = ConnectionSettings(server="srv,1433", user="sa", password="secreta", driver="ODBC Driver 18 for SQL Server")


@pytest.fixture
def store(tmp_path):
    return CredentialStore(path=tmp_path / "connections.json", backend=FakeKeyring())


class FalsoTester:
    def __init__(self, resultados):
        self.resultados = resultados
        self.llamadas = []

    def probar(self, conexion, base=None, tabla=None):
        self.llamadas.append((conexion.server, base, tabla))
        return self.resultados[base]


def test_agencia_requiere_tambien_challenger():
    assert gate.hosts_requeridos("OF") == ["PESOS_OFFER"]
    assert gate.hosts_requeridos("VENTA") == ["PESOS_OFFER"]
    assert gate.hosts_requeridos("AGENCIA") == ["PESOS_OFFER", "CHALLENGER"]


def test_hosts_sin_configurar(store):
    store.save_connection("PESOS_OFFER", CONEXION)

    assert gate.hosts_sin_configurar(store, ["PESOS_OFFER", "CHALLENGER"]) == ["CHALLENGER"]
    assert gate.hosts_sin_configurar(store, ["PESOS_OFFER"]) == []


def test_probar_hosts_usa_la_base_y_tabla_de_cada_host(store):
    store.save_connection("PESOS_OFFER", CONEXION)
    store.save_connection("CHALLENGER", CONEXION)
    ok = ResultadoConexion(Categoria.OK, "ok")
    mal = ResultadoConexion(Categoria.LOGIN_RECHAZADO, "no")
    tester = FalsoTester({"botDB": ok, "Challenger_uat": mal})

    resultados = gate.probar_hosts(store, ["PESOS_OFFER", "CHALLENGER"], tester)

    assert resultados == {"PESOS_OFFER": ok, "CHALLENGER": mal}
    assert sorted(tester.llamadas) == [
        ("srv,1433", "Challenger_uat", "dbo.AgencyStructure"),
        ("srv,1433", "botDB", "dbo.Ofertas"),
    ]


def test_probar_hosts_vacio(store):
    assert gate.probar_hosts(store, [], FalsoTester({})) == {}


def test_formulario_nuevo_exige_contrasena(store):
    with pytest.raises(ValueError, match="contraseña"):
        gate.conexion_de_formulario(store, "PESOS_OFFER", "srv", "sa", "", "")


def test_formulario_con_contrasena_vacia_conserva_la_guardada(store):
    store.save_connection("PESOS_OFFER", CONEXION)

    c = gate.conexion_de_formulario(store, "PESOS_OFFER", " otro,1433 ", " sa2 ", "", "")

    assert (c.server, c.user, c.password) == ("otro,1433", "sa2", "secreta")
    assert c.driver  # vacío -> el de por defecto


def test_formulario_con_contrasena_nueva_la_usa(store):
    store.save_connection("PESOS_OFFER", CONEXION)

    assert gate.conexion_de_formulario(store, "PESOS_OFFER", "srv", "sa", "nueva", "X").password == "nueva"


@pytest.mark.parametrize("server,user", [("", "sa"), ("srv", " ")])
def test_formulario_exige_servidor_y_usuario(store, server, user):
    with pytest.raises(ValueError, match="servidor y usuario"):
        gate.conexion_de_formulario(store, "PESOS_OFFER", server, user, "p", "")


def test_driver_sugerido():
    assert gate.driver_sugerido(["ODBC Driver 17 for SQL Server", "ODBC Driver 18 for SQL Server"]) == "ODBC Driver 17 for SQL Server"
    assert gate.driver_sugerido(["ODBC Driver 18 for SQL Server"]) == "ODBC Driver 18 for SQL Server"
    assert gate.driver_sugerido([]) == "ODBC Driver 17 for SQL Server"
