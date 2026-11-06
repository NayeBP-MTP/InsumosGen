"""Pruebas unitarias (sin red ni BD) del mapeo base -> host y de la clase base de conexión."""
import pyodbc
import pytest

from config import databases
from services import db
from services.db import SqlServerRepository, credenciales_de_host


def _env_host(monkeypatch, host, server="srv", user="usr", password="pwd", driver=None):
    monkeypatch.setenv(f"{host}_SERVER", server)
    monkeypatch.setenv(f"{host}_USER", user)
    monkeypatch.setenv(f"{host}_PASSWORD", password)
    if driver:
        monkeypatch.setenv(f"{host}_DRIVER", driver)
    else:
        monkeypatch.delenv(f"{host}_DRIVER", raising=False)


class TestMapeoBaseHost:
    @pytest.mark.parametrize("base,host", [
        ("botDB", "PESOS_OFFER"),
        ("Originacion", "PESOS_OFFER"),
        ("CNFS_uat", "CNFS"),
        ("Challenger_uat", "CHALLENGER"),
    ])
    def test_cada_base_resuelve_su_host(self, base, host):
        assert databases.host_de(base) == host

    def test_todo_host_mapeado_es_un_host_conocido(self):
        assert set(databases.DATABASE_HOSTS.values()) <= set(databases.HOSTS)

    def test_base_desconocida_falla_con_mensaje_claro(self):
        with pytest.raises(ValueError, match="sin host asignado.*Bases conocidas.*Originacion"):
            databases.host_de("NoExiste")


class TestCredenciales:
    def test_lee_variables_del_host(self, monkeypatch):
        _env_host(monkeypatch, "CNFS", "10.0.0.1", "u", "p", "Mi Driver")
        c = credenciales_de_host("CNFS")
        assert (c.server, c.user, c.password, c.driver) == ("10.0.0.1", "u", "p", "Mi Driver")

    def test_driver_por_defecto(self, monkeypatch):
        _env_host(monkeypatch, "CNFS")
        assert credenciales_de_host("CNFS").driver == db.DRIVER_POR_DEFECTO

    def test_faltantes_nombra_las_variables(self, monkeypatch):
        for campo in ("SERVER", "USER", "PASSWORD"):
            monkeypatch.delenv(f"PESOS_OFFER_{campo}", raising=False)
        with pytest.raises(EnvironmentError) as exc:
            credenciales_de_host("PESOS_OFFER")
        for campo in ("SERVER", "USER", "PASSWORD"):
            assert f"PESOS_OFFER_{campo}" in str(exc.value)

    def test_host_desconocido(self):
        with pytest.raises(ValueError, match="desconocido"):
            credenciales_de_host("OTRO")


class TestSqlServerRepository:
    def test_construir_no_exige_env(self, monkeypatch):
        monkeypatch.delenv("PESOS_OFFER_SERVER", raising=False)
        repo = SqlServerRepository("Originacion")
        assert repo.host == "PESOS_OFFER"

    def test_base_desconocida_falla_al_construir(self):
        with pytest.raises(ValueError):
            SqlServerRepository("NoExiste")

    def test_cadena_usa_credenciales_del_host_y_la_base(self, monkeypatch):
        _env_host(monkeypatch, "PESOS_OFFER", "srv-po", "u-po", "p-po", "DRV")
        _env_host(monkeypatch, "CNFS", "srv-cnfs", "u-cnfs", "p-cnfs", "DRV")
        po = SqlServerRepository("Originacion")._connection_string()
        cnfs = SqlServerRepository("CNFS_uat")._connection_string()
        assert "SERVER=srv-po" in po and "DATABASE=Originacion" in po and "UID=u-po" in po
        assert "SERVER=srv-cnfs" in cnfs and "DATABASE=CNFS_uat" in cnfs and "UID=u-cnfs" in cnfs
        # botDB y Originacion comparten host (mismas credenciales), distinta base
        bot = SqlServerRepository("botDB")._connection_string()
        assert "SERVER=srv-po" in bot and "DATABASE=botDB" in bot

    def test_reintenta_ante_error_transitorio(self, monkeypatch):
        _env_host(monkeypatch, "CNFS")
        monkeypatch.setattr(db.time, "sleep", lambda s: None)
        llamadas = []

        def connect(cadena):
            llamadas.append(cadena)
            if len(llamadas) < 3:
                raise pyodbc.Error("08001", "pipe")
            return "conexion"

        monkeypatch.setattr(db.pyodbc, "connect", connect)
        assert SqlServerRepository("CNFS_uat")._get_connection() == "conexion"
        assert len(llamadas) == 3

    def test_no_reintenta_error_no_transitorio(self, monkeypatch):
        _env_host(monkeypatch, "CNFS")
        llamadas = []

        def connect(cadena):
            llamadas.append(cadena)
            raise pyodbc.Error("28000", "login failed")

        monkeypatch.setattr(db.pyodbc, "connect", connect)
        with pytest.raises(pyodbc.Error):
            SqlServerRepository("CNFS_uat")._get_connection()
        assert len(llamadas) == 1

    def test_agota_reintentos_y_relanza(self, monkeypatch):
        _env_host(monkeypatch, "CNFS")
        monkeypatch.setattr(db.time, "sleep", lambda s: None)
        monkeypatch.setattr(
            db.pyodbc, "connect", lambda c: (_ for _ in ()).throw(pyodbc.Error("08S01", "x"))
        )
        with pytest.raises(pyodbc.Error):
            SqlServerRepository("CNFS_uat")._get_connection(intentos=2)

    def test_dry_run_no_conecta_y_registra(self, monkeypatch):
        def conectar(*a, **k):
            raise AssertionError("dry_run no debe conectar")

        monkeypatch.setattr(db.pyodbc, "connect", conectar)
        repo = SqlServerRepository("CNFS_uat", dry_run=True)
        repo._escribir("UPDATE t SET a = ? WHERE b = ?", (1, 2))
        assert repo.dry_run_log == [("UPDATE t SET a = ? WHERE b = ?", (1, 2))]

    def test_escribir_real_ejecuta_y_hace_commit(self, monkeypatch):
        _env_host(monkeypatch, "CNFS")
        eventos = []

        class Cursor:
            def execute(self, sql, params):
                eventos.append(("execute", sql, params))

        class Conn:
            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            def cursor(self):
                return Cursor()

            def commit(self):
                eventos.append(("commit",))

        monkeypatch.setattr(db.pyodbc, "connect", lambda c: Conn())
        SqlServerRepository("CNFS_uat")._escribir("DELETE FROM t WHERE a = ?", (7,))
        assert eventos == [("execute", "DELETE FROM t WHERE a = ?", (7,)), ("commit",)]
