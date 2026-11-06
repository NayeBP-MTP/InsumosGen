"""Pruebas unitarias (sin red) de utils/vpn_check.py y del host de los repositorios de agencia."""
from services.agency_repository import BotDbAgencyRepository, ChallengerRepository
from utils import vpn_check


class TestHostPuerto:
    def test_host_sin_puerto_usa_1433(self, monkeypatch):
        monkeypatch.setenv("PESOS_OFFER_SERVER", "10.0.0.5")
        assert vpn_check._host_puerto("PESOS_OFFER") == ("10.0.0.5", 1433)

    def test_host_con_puerto_prefijo_tcp_e_instancia(self, monkeypatch):
        monkeypatch.setenv("CHALLENGER_SERVER", "tcp:srv\\inst,1500")
        assert vpn_check._host_puerto("CHALLENGER") == ("srv", 1500)

    def test_sin_variable_devuelve_none(self, monkeypatch):
        monkeypatch.delenv("CNFS_SERVER", raising=False)
        assert vpn_check._host_puerto("CNFS") is None


class TestVerificarVpn:
    def test_variable_faltante_nombra_el_host(self, monkeypatch):
        monkeypatch.delenv("PESOS_OFFER_SERVER", raising=False)
        ok, faltantes = vpn_check.verificar_vpn(requiere_bd=True)
        assert not ok and faltantes == ["Variable PESOS_OFFER_SERVER no configurada en .env"]

    def test_challenger_faltante(self, monkeypatch):
        monkeypatch.setenv("PESOS_OFFER_SERVER", "srv-po")
        monkeypatch.delenv("CHALLENGER_SERVER", raising=False)
        ok, faltantes = vpn_check.verificar_vpn(requiere_bd=True, requiere_challenger=True)
        assert not ok and faltantes == ["Variable CHALLENGER_SERVER no configurada en .env"]

    def test_revisa_cada_host_requerido(self, monkeypatch):
        monkeypatch.setenv("PESOS_OFFER_SERVER", "srv-po,1433")
        monkeypatch.setenv("CHALLENGER_SERVER", "srv-ch,1444")
        revisados = []
        monkeypatch.setattr(vpn_check, "_alcanzable", lambda h, p: revisados.append((h, p)) or True)
        ok, faltantes = vpn_check.verificar_vpn(requiere_bd=True, requiere_challenger=True)
        assert ok and faltantes == []
        assert ("srv-po", 1433) in revisados and ("srv-ch", 1444) in revisados

    def test_reporta_los_inalcanzables(self, monkeypatch):
        monkeypatch.setenv("PESOS_OFFER_SERVER", "srv-po")
        monkeypatch.setattr(vpn_check, "_alcanzable", lambda h, p: h != "srv-po")
        ok, faltantes = vpn_check.verificar_vpn(requiere_bd=True)
        assert not ok and faltantes == ["Base de datos botDB (srv-po:1433)"]


class TestRepositoriosDeAgencia:
    def test_challenger_en_su_host(self):
        repo = ChallengerRepository()
        assert (repo.base, repo.host) == ("Challenger_uat", "CHALLENGER")

    def test_botdb_de_agencia_en_pesos_offer(self):
        repo = BotDbAgencyRepository()
        assert (repo.base, repo.host) == ("botDB", "PESOS_OFFER")
