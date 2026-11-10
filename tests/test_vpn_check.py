"""Pruebas unitarias (sin red) de utils/vpn_check.py y del host de los repositorios de agencia."""
import socket
import urllib.error

import pyodbc

from services.agency_repository import BotDbAgencyRepository, ChallengerRepository
from utils import vpn_check


class TestHostPuerto:
    def test_host_sin_puerto_usa_1433(self, monkeypatch):
        monkeypatch.setenv("PESOS_OFFER_SERVER", "10.0.0.5")
        assert vpn_check._host_puerto("PESOS_OFFER") == ("10.0.0.5", 1433)

    def test_host_con_puerto_prefijo_tcp_e_instancia(self, monkeypatch):
        monkeypatch.setenv("CHALLENGER_SERVER", r"tcp:srv\inst,1500")
        assert vpn_check._host_puerto("CHALLENGER") == ("srv", 1500)

    def test_sin_variable_devuelve_none(self, monkeypatch):
        monkeypatch.delenv("CNFS_SERVER", raising=False)
        assert vpn_check._host_puerto("CNFS") is None


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


class TestMotivoLogin:
    def test_driver_faltante(self):
        e = pyodbc.Error("IM002", "[IM002] Data source name not found")
        assert "driver ODBC 'D17'" in vpn_check._motivo_login(e, "botDB", "D17")

    def test_credenciales(self):
        e = pyodbc.Error("28000", "Login failed for user 'x'")
        assert "usuario/contraseña" in vpn_check._motivo_login(e, "botDB", "d")

    def test_login_timeout_dice_que_el_puerto_si_responde(self):
        e = pyodbc.Error("HYT00", "Login timeout expired")
        m = vpn_check._motivo_login(e, "CNFS_uat", "d")
        assert "login timeout" in m and "puerto responde" in m

    def test_base_inexistente(self):
        e = pyodbc.Error("42000", "Cannot open database \"X\" requested by the login")
        assert "no existe" in vpn_check._motivo_login(e, "X", "d")

    def test_otro_error_conserva_estado_y_texto(self):
        e = pyodbc.Error("08001", "algo raro")
        assert vpn_check._motivo_login(e, "b", "d") == "[08001] algo raro"


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

    def test_variables_faltantes_del_env_se_reportan_con_su_nombre(self, monkeypatch):
        monkeypatch.setattr(vpn_check, "_problema_portal", lambda url: None)
        for v in ("PESOS_OFFER_SERVER", "PESOS_OFFER_USER", "PESOS_OFFER_PASSWORD"):
            monkeypatch.delenv(v, raising=False)
        ok, problemas = vpn_check.verificar_vpn(requiere_bd=True)
        assert not ok and "Faltan variables de entorno para el host PESOS_OFFER" in problemas[0]

    def test_servidor_sql_inalcanzable_dice_la_causa_de_red(self, monkeypatch):
        monkeypatch.setenv("PESOS_OFFER_SERVER", "srv-po")
        monkeypatch.setenv("PESOS_OFFER_USER", "u")
        monkeypatch.setenv("PESOS_OFFER_PASSWORD", "p")
        monkeypatch.setattr(vpn_check, "_problema_tcp", lambda h, p: "no hubo respuesta en 4s (timeout)")
        m = vpn_check._problema_base("botDB")
        assert "srv-po:1433" in m and "timeout" in m


class TestRepositoriosDeAgencia:
    def test_challenger_en_su_host(self):
        repo = ChallengerRepository()
        assert (repo.base, repo.host) == ("Challenger_uat", "CHALLENGER")

    def test_botdb_de_agencia_en_pesos_offer(self):
        repo = BotDbAgencyRepository()
        assert (repo.base, repo.host) == ("botDB", "PESOS_OFFER")
