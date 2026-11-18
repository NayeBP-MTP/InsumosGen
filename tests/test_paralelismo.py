import json
import os
import subprocess
import sys
import threading
import time
import tkinter as tk
from pathlib import Path

import run
from config.settings import Settings
from tests.test_primer_arranque import ui  # noqa: F401  (fixture: SelectorUI aislado)

RAIZ = Path(__file__).resolve().parents[1]


def _textos(widget) -> list:
    textos = []
    for hijo in widget.winfo_children():
        try:
            textos.append(str(hijo.cget("text")))
        except tk.TclError:
            pass
        textos += _textos(hijo)
    return textos


def test_el_paralelismo_esta_apagado():
    assert Settings.PARALELISMO_HABILITADO is False
    assert Settings.HEADLESS is False
    assert run.MAX_WORKERS_VENTAS == 1


def test_un_run_config_antiguo_con_headless_se_ignora(tmp_path):
    config = tmp_path / "run_config.json"
    config.write_text(json.dumps({"headless": True}), encoding="utf-8")

    salida = subprocess.run(
        [sys.executable, "-c", "from config.settings import Settings; print(Settings.HEADLESS)"],
        cwd=RAIZ, env={**os.environ, "PROVIDIGITAL_RUN_CONFIG_PATH": str(config)},
        capture_output=True, text=True, check=True,
    )

    assert salida.stdout.strip() == "False"


def test_la_ui_no_ofrece_el_navegador_invisible_pero_si_agregar_lotes(ui):  # noqa: F811
    textos = " | ".join(_textos(ui.root))

    assert "segundo plano" not in textos and "Navegador:" not in textos
    assert "+ Agregar lote de venta" in textos
    assert "+ Agregar oferta" in textos


def _slot(batch_id):
    return {"batch_id": batch_id, "config": {"agencia_label": f"Agencia {batch_id}"},
            "estado": "pendiente", "detalle": "", "intentos": 0}


def test_varios_lotes_se_ejecutan_en_secuencia(monkeypatch):
    activos, maximo, orden = [], [0], []
    candado = threading.Lock()

    def lote_falso(tipo, grupo, run_config, controller=None):
        with candado:
            activos.append(1)
            maximo[0] = max(maximo[0], len(activos))
            orden.append(grupo[0]["batch_id"])
        time.sleep(0.05)
        with candado:
            activos.pop()
        return [{"estado": "exitoso", "nombreCliente": "X"} for _ in grupo]

    monkeypatch.setattr(run, "_ejecutar_lote_venta", lote_falso)
    monkeypatch.setattr(run.RunHistory, "append", lambda registros: None)
    monkeypatch.setattr(run.Progress, "emit", lambda *a, **k: None)
    slots = {"CN": [_slot("a"), _slot("b"), _slot("c")]}
    tareas = [("CN", s) for s in slots["CN"]]

    run._ejecutar_ventas_en_paralelo(tareas, slots, {}, [], 1)

    assert maximo[0] == 1
    assert orden == ["a", "b", "c"]
    assert all(s["estado"] == "exitosa" for s in slots["CN"])


def test_un_lote_en_espera_no_arranca_si_se_aborto_la_corrida(monkeypatch):
    def no_debe_correr(*args, **kwargs):
        raise AssertionError("no debe lanzar otro pytest/Chrome tras abortar")

    monkeypatch.setattr(run, "_ejecutar_fase", no_debe_correr)
    controller = run.RunController()
    controller.abort()

    assert run._ejecutar_lote_venta("CN", [_slot("a")], {}, controller) == []
