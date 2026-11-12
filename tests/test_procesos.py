import os
import subprocess
import sys
import time

import pytest

import run
from utils import procesos


@pytest.fixture
def datos(tmp_path, monkeypatch):
    monkeypatch.setattr(procesos, "app_data_dir", lambda: tmp_path)
    return tmp_path


def test_con_pythonw_los_subprocesos_usan_el_python_exe_hermano(tmp_path, monkeypatch):
    (tmp_path / "pythonw.exe").write_bytes(b"")
    (tmp_path / "python.exe").write_bytes(b"")
    monkeypatch.setattr(sys, "executable", str(tmp_path / "pythonw.exe"))

    assert procesos.python_ejecutable() == str(tmp_path / "python.exe")


def test_si_no_hay_python_exe_hermano_se_queda_con_el_actual(tmp_path, monkeypatch):
    (tmp_path / "pythonw.exe").write_bytes(b"")
    monkeypatch.setattr(sys, "executable", str(tmp_path / "pythonw.exe"))

    assert procesos.python_ejecutable() == str(tmp_path / "pythonw.exe")


def test_con_python_normal_no_cambia_el_interprete():
    assert procesos.python_ejecutable() == sys.executable


def test_con_consola_no_hay_log_ni_opciones_extra(datos, monkeypatch):
    monkeypatch.setattr(procesos, "sin_consola", lambda: False)

    assert procesos.abrir_log("x") is None
    assert procesos.opciones_subproceso(None) == {}


def test_sin_consola_la_salida_va_a_un_log_y_la_ventana_se_oculta(datos, monkeypatch):
    monkeypatch.setattr(procesos, "sin_consola", lambda: True)

    log = procesos.abrir_log("run_123")
    try:
        opciones = procesos.opciones_subproceso(log)
    finally:
        log.close()

    assert (datos / "logs" / "run_123.log").is_file()
    assert opciones["stdout"] is log and opciones["stderr"] == subprocess.STDOUT
    assert opciones["creationflags"] == getattr(subprocess, "CREATE_NO_WINDOW", 0)


def test_limpiar_logs_solo_borra_los_viejos(datos):
    carpeta = datos / "logs"
    carpeta.mkdir()
    viejo, reciente = carpeta / "viejo.log", carpeta / "reciente.log"
    viejo.write_text("x")
    reciente.write_text("x")
    hace_un_mes = time.time() - 30 * 86400
    os.utime(viejo, (hace_un_mes, hace_un_mes))

    assert procesos.limpiar_logs(dias=14) == 1
    assert not viejo.exists() and reciente.exists()


def test_limpiar_logs_sin_carpeta_no_falla(datos):
    assert procesos.limpiar_logs() == 0


class _ProcFalso:
    pid = 1

    def wait(self):
        return 0


def _lanzar_fase(monkeypatch, tmp_path, sin_consola):
    llamadas = []
    monkeypatch.setattr(run, "app_data_dir", lambda: tmp_path)
    monkeypatch.setattr(procesos, "app_data_dir", lambda: tmp_path)
    monkeypatch.setattr(procesos, "sin_consola", lambda: sin_consola)
    monkeypatch.setattr(run.Progress, "emit", lambda *a, **k: None)
    monkeypatch.setattr(
        run.subprocess, "Popen", lambda args, **kw: llamadas.append((args, kw)) or _ProcFalso())

    run._ejecutar_fase("OF", 1, {}, ofertas_cfg=[], run_id="t1")
    return llamadas[0]


def test_la_fase_lanza_pytest_con_el_interprete_de_consola(monkeypatch, tmp_path):
    monkeypatch.setattr(run, "python_ejecutable", lambda: "C:/runtime/python.exe")

    args, _ = _lanzar_fase(monkeypatch, tmp_path, sin_consola=False)

    assert args[:3] == ["C:/runtime/python.exe", "-m", "pytest"]


def test_la_fase_instalada_oculta_la_ventana_y_registra_la_salida(monkeypatch, tmp_path):
    _, kwargs = _lanzar_fase(monkeypatch, tmp_path, sin_consola=True)

    assert kwargs["stderr"] == subprocess.STDOUT
    assert kwargs["creationflags"] == getattr(subprocess, "CREATE_NO_WINDOW", 0)
    assert kwargs["stdout"].closed  # el log se cierra al terminar la fase
    assert list((tmp_path / "logs").glob("run_*.log"))


def test_la_fase_desde_consola_no_cambia_la_salida(monkeypatch, tmp_path):
    _, kwargs = _lanzar_fase(monkeypatch, tmp_path, sin_consola=False)

    assert "stdout" not in kwargs and "creationflags" not in kwargs
