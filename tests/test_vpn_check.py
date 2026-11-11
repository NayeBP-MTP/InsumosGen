"""Pruebas unitarias (sin red) de utils/vpn_check.py y del host de los repositorios de agencia."""
import socket
import urllib.error

from config.credentials import ConnectionSettings, CredentialsMissing
from services.connection_tester import Categoria, ResultadoConexion
from services.agency_repository import BotDbAgencyRepository, ChallengerRepository
from utils import vpn_check


class TestMotivoRed:
    def test_dns(self):
        m = vpn_check._motivo_red(socket.gaierror(11001, "getaddrinfo failed"), "portal.x")
        assert "no se resuelve (DNS)" in m and "portal.x" in m

    def test_timeout(self):
        assert "timeout" in vpn_check._motivo_red(socket.timeout("timed out"), "h")

    def test_rechazada(self):
        assert "rechazada" in vpn_check._motivo_red(ConnectionRefusedError(), "h")

    def test_desenvuelve_urlerror(self):
        assert "DNS" in vpn_check._motivo_red(urllib.error.URLError(socket.gaierror(11001, "x")), "h")

    def test_otro_oserror_trae_codigo_y_texto(self):
        assert "10051" in vpn_check._motivo_red(OSError(10051, "red inalcanzable"), "h")


class TestPortal:
    def test_http_menor_a_500_es_accesible(self, monkeypatch):
        def abrir(url, timeout):
            raise urllib.error.HTTPError(url, 403, "Forbidden", {}, None)
        monkeypatch.setattr(vpn_check.urllib.request, "urlopen", abrir)
        assert vpn_check._problema_portal("https://p.x/login") is None

    def test_http_500_se_reporta(self, monkeypatch):
        def abrir(url, timeout):
            raise urllib.error.HTTPError(url, 502, "Bad Gateway", {}, None)
        monkeypatch.setattr(vpn_check.urllib.request, "urlopen", abrir)
        assert "HTTP 502" in vpn_check._problema_portal("https://p.x/login")

    def test_falla_de_red_trae_la_causa(self, monkeypatch):
        def abrir(url, timeout):
            raise urllib.error.URLError(socket.gaierror(11001, "getaddrinfo failed"))
        monkeypatch.setattr(vpn_check.urllib.request, "urlopen", abrir)
        assert "DNS" in vpn_check._problema_portal("https://p.x/login")


class TestVerificarVpn:
    def _todo_bien(self, monkeypatch):
        monkeypatch.setattr(vpn_check, "_problema_portal", lambda url: None)
        revisadas = []
        monkeypatch.setattr(vpn_check, "_problema_base", lambda b: revisadas.append(b) or None)
        return revisadas

    def test_revisa_solo_las_bases_pedidas(self, monkeypatch):
        revisadas = self._todo_bien(monkeypatch)
        assert vpn_check.verificar_vpn(requiere_bd=True) == (True, [])
        assert revisadas == ["botDB"]
        revisadas.clear()
        vpn_check.verificar_vpn(requiere_bd=True, requiere_challenger=True, requiere_originacion=True, requiere_cnfs=True)
        assert sorted(revisadas) == ["CNFS_uat", "Challenger_uat", "Originacion", "botDB"]

    def test_cada_problema_nombra_que_falla_y_por_que(self, monkeypatch):
        monkeypatch.setattr(vpn_check, "_problema_portal", lambda url: "no se resuelve (DNS)")
        monkeypatch.setattr(vpn_check, "_problema_base", lambda b: "login timeout" if b == "CNFS_uat" else None)
        ok, problemas = vpn_check.verificar_vpn(requiere_bd=True, requiere_cnfs=True)
        assert not ok and problemas == [
            "Portal UAT de Provident: no se resuelve (DNS)",
            "Base de datos CNFS_uat: login timeout",
        ]


class TestProblemaBase:
    """`_problema_base` delega en ConnectionTester con las credenciales del almacén."""

    def _falsos(self, monkeypatch, credenciales, resultado=None):
        class RepoFalso:
            def __init__(self, base):
                self.base = base

            @property
            def credenciales(self):
                if isinstance(credenciales, Exception):
                    raise credenciales
                return credenciales

        class FalsoTester:
            def probar(self, conexion, base=None, tabla=None):
                FalsoTester.llamada = (conexion, base)
                return resultado

        monkeypatch.setattr(vpn_check, "SqlServerRepository", RepoFalso)
        monkeypatch.setattr(vpn_check, "ConnectionTester", FalsoTester)
        return FalsoTester

    def test_host_sin_configurar_se_reporta_con_su_nombre(self, monkeypatch):
        self._falsos(monkeypatch, CredentialsMissing("PESOS_OFFER"))
        assert "PESOS_OFFER" in vpn_check._problema_base("botDB")

    def test_conexion_correcta_no_reporta_problema(self, monkeypatch):
        conexion = ConnectionSettings("srv", "u", "p")
        tester = self._falsos(monkeypatch, conexion, ResultadoConexion(Categoria.OK, "Conexión correcta."))
        assert vpn_check._problema_base("botDB") is None
        assert tester.llamada == (conexion, "botDB")

    def test_falla_devuelve_el_mensaje_del_tester(self, monkeypatch):
        self._falsos(monkeypatch, ConnectionSettings("srv", "u", "p"),
                     ResultadoConexion(Categoria.LOGIN_RECHAZADO, "El servidor rechazó el usuario"))
        assert vpn_check._problema_base("botDB") == "El servidor rechazó el usuario"


class TestRepositoriosDeAgencia:
    def test_challenger_en_su_host(self):
        repo = ChallengerRepository()
        assert (repo.base, repo.host) == ("Challenger_uat", "CHALLENGER")

    def test_botdb_de_agencia_en_pesos_offer(self):
        repo = BotDbAgencyRepository()
        assert (repo.base, repo.host) == ("botDB", "PESOS_OFFER")
