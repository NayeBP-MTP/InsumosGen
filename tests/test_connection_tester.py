import socket

import pyodbc
import pytest

from config.credentials import ConnectionSettings
from services.connection_tester import Categoria, ConnectionTester, host_puerto, sanear


CONEXION = ConnectionSettings(server="srv,1433", user="sa", password="p;a}ss", driver="ODBC Driver 18 for SQL Server")


class SocketFalso:
    def __init__(self, error=None):
        self.error = error
        self.destino = None

    def __call__(self, destino, timeout):
        self.destino = destino
        if self.error:
            raise self.error
        return self

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class ConexionFalsa:
    def __init__(self, falla_en=None):
        self.falla_en = falla_en
        self.consultas = []
        self.cerrada = False

    def execute(self, sql):
        self.consultas.append(sql)
        if self.falla_en and self.falla_en in sql:
            raise pyodbc.Error("42000", "[42000] The SELECT permission was denied on the object 'Ofertas' (229)")
        return self

    def fetchone(self):
        return (1,)

    def close(self):
        self.cerrada = True


def conectar_ok(cnx):
    registro = {}

    def conectar(cadena, timeout):
        registro["cadena"], registro["timeout"] = cadena, timeout
        return cnx

    return conectar, registro


def conectar_falla(*args_error):
    def conectar(cadena, timeout):
        raise pyodbc.Error(*args_error)

    return conectar


def tester(conectar, abrir_socket=None):
    return ConnectionTester(conectar=conectar, abrir_socket=abrir_socket or SocketFalso())


def test_conexion_correcta_cierra_la_conexion():
    cnx = ConexionFalsa()
    conectar, registro = conectar_ok(cnx)

    r = tester(conectar).probar(CONEXION, base="botDB")

    assert r.ok and r.categoria is Categoria.OK
    assert cnx.consultas == ["SELECT 1"] and cnx.cerrada
    assert "DATABASE={botDB}" in registro["cadena"]


def test_la_contrasena_se_escapa_en_la_cadena_de_conexion():
    conectar, registro = conectar_ok(ConexionFalsa())

    tester(conectar).probar(CONEXION)

    assert "PWD={p;a}}ss};" in registro["cadena"]
    assert "UID={sa};" in registro["cadena"]


def test_host_inalcanzable_no_intenta_el_login():
    llamado = []

    def conectar(cadena, timeout):
        llamado.append(1)

    r = tester(conectar, SocketFalso(socket.timeout())).probar(CONEXION)

    assert r.categoria is Categoria.HOST_INALCANZABLE
    assert "VPN" in r.mensaje and "srv:1433" in r.mensaje
    assert not llamado


def test_dns_no_resuelto_se_distingue_del_timeout():
    r = tester(conectar_falla(), SocketFalso(socket.gaierror())).probar(CONEXION)

    assert r.categoria is Categoria.HOST_INALCANZABLE
    assert "DNS" in r.mensaje


def test_driver_ausente_incluye_el_enlace_de_descarga():
    r = tester(conectar_falla("IM002", "[IM002] Data source name not found")).probar(CONEXION)

    assert r.categoria is Categoria.DRIVER_AUSENTE
    assert "learn.microsoft.com" in r.mensaje and "ODBC Driver 18" in r.mensaje


def test_login_rechazado():
    r = tester(conectar_falla("28000", "[28000] Login failed for user 'sa'. (18456)")).probar(CONEXION)

    assert r.categoria is Categoria.LOGIN_RECHAZADO
    assert "'sa'" in r.mensaje


def test_base_inaccesible():
    r = tester(conectar_falla("42000", "Cannot open database \"botDB\" requested by the login. (4060)")).probar(
        CONEXION, base="botDB")

    assert r.categoria is Categoria.BASE_INACCESIBLE
    assert "botDB" in r.mensaje


def test_timeout_de_login():
    r = tester(conectar_falla("HYT00", "[HYT00] Login timeout expired")).probar(CONEXION)

    assert r.categoria is Categoria.TIMEOUT


def test_error_desconocido_conserva_sqlstate():
    r = tester(conectar_falla("HY000", "algo raro")).probar(CONEXION)

    assert r.categoria is Categoria.ERROR
    assert "HY000" in r.mensaje


def test_el_mensaje_de_error_no_filtra_la_contrasena():
    r = tester(conectar_falla("08001", "falló con DRIVER={x};UID={sa};PWD={p;a}}ss}; y p;a}ss")).probar(CONEXION)

    assert "p;a}" not in r.mensaje
    assert "ss}" not in r.mensaje


def test_sondeo_de_tabla_correcto():
    cnx = ConexionFalsa()
    conectar, _ = conectar_ok(cnx)

    r = tester(conectar).probar(CONEXION, base="botDB", tabla="dbo.Ofertas")

    assert r.ok
    assert cnx.consultas == ["SELECT 1", "SELECT TOP 1 1 FROM dbo.Ofertas"]


def test_login_ok_pero_sin_permiso_en_la_tabla():
    cnx = ConexionFalsa(falla_en="TOP 1")
    conectar, _ = conectar_ok(cnx)

    r = tester(conectar).probar(CONEXION, base="botDB", tabla="dbo.Ofertas")

    assert r.categoria is Categoria.SIN_PERMISOS
    assert "dbo.Ofertas" in r.mensaje
    assert cnx.cerrada


@pytest.mark.parametrize("tabla", ["dbo.Ofertas; DROP TABLE x", "a b", "x--"])
def test_rechaza_nombres_de_tabla_sospechosos(tabla):
    r = tester(conectar_falla()).probar(CONEXION, tabla=tabla)

    assert r.categoria is Categoria.ERROR


@pytest.mark.parametrize("server", ["a;b", "a{b", "a}b"])
def test_rechaza_servidores_con_caracteres_de_cadena(server):
    r = tester(conectar_falla()).probar(ConnectionSettings(server, "u", "p"))

    assert r.categoria is Categoria.SERVIDOR_INVALIDO


def test_instancia_con_nombre_sin_puerto_omite_el_chequeo_tcp():
    socket_falso = SocketFalso(socket.timeout())
    conectar, _ = conectar_ok(ConexionFalsa())

    r = tester(conectar, socket_falso).probar(ConnectionSettings(r"srv\SQLEXPRESS", "u", "p"))

    assert r.ok and socket_falso.destino is None


@pytest.mark.parametrize("server,esperado", [
    ("srv", ("srv", 1433)),
    ("srv,1500", ("srv", 1500)),
    ("tcp:srv,1500", ("srv", 1500)),
    (r"srv\inst,1500", ("srv", 1500)),
    (r"srv\inst", None),
])
def test_host_puerto(server, esperado):
    assert host_puerto(server) == esperado


def test_sanear_oculta_pwd_con_y_sin_llaves():
    assert "secreto" not in sanear("PWD=secreto;UID=x")
    assert "ss}" not in sanear("PWD={p;a}}ss};UID=x")
