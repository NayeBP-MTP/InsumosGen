import os
import subprocess
import sys
from pathlib import Path

import pytest

from config.settings import Settings
from ui.selector_ui import SelectorUI
from utils import paths


@pytest.fixture
def rutas(tmp_path, monkeypatch):
    """Apunta las rutas de imágenes de Settings a una carpeta temporal vacía."""
    nombres = {
        "LEGALARIO_SELFIE_IMAGE_PATH": "selfie.jpeg",
        "LEGALARIO_FRONT_IMAGE_PATH": "ine_frente.jpeg",
        "LEGALARIO_BACK_IMAGE_PATH": "ine_tras.jpeg",
        "COMPROBANTE_DOMICILIO_PATH": "comprobante.jpeg",
        "LEGALARIO_SELFIE_VIDEO_PATH": "selfie.y4m",
    }
    for atributo, nombre in nombres.items():
        monkeypatch.setattr(Settings, atributo, str(tmp_path / nombre))
    return tmp_path


def _crear(carpeta, nombre, mtime=None):
    ruta = carpeta / nombre
    ruta.write_bytes(b"x")
    if mtime is not None:
        os.utime(ruta, (mtime, mtime))
    return ruta


def _estado():
    return {etiqueta.split()[0]: (ok, detalle) for etiqueta, ok, detalle in SelectorUI._estado_archivos()}


def test_sin_imagenes_todo_esta_pendiente(rutas):
    estado = SelectorUI._estado_archivos()

    assert [ok for _, ok, _ in estado] == [False, False, False, False]
    assert "Requiere primero la foto de frente" in estado[3][2]


def test_con_todo_cargado_y_video_al_dia_no_falta_nada(rutas):
    for nombre in ("selfie.jpeg", "ine_frente.jpeg", "ine_tras.jpeg", "comprobante.jpeg"):
        _crear(rutas, nombre, mtime=1000)
    _crear(rutas, "selfie.y4m", mtime=2000)

    assert all(ok for _, ok, _ in SelectorUI._estado_archivos())


def test_el_comprobante_es_obligatorio(rutas):
    for nombre in ("selfie.jpeg", "ine_frente.jpeg", "ine_tras.jpeg"):
        _crear(rutas, nombre, mtime=1000)
    _crear(rutas, "selfie.y4m", mtime=2000)

    estado = SelectorUI._estado_archivos()

    assert [ok for _, ok, _ in estado] == [True, True, False, True]


def test_el_detalle_de_la_ine_dice_que_lado_falta(rutas):
    _crear(rutas, "ine_frente.jpeg")

    detalle_ine = SelectorUI._estado_archivos()[1][2]

    assert detalle_ine == "Falta la INE trasera"


def test_un_video_anterior_a_la_selfie_pide_regenerarlo(rutas):
    _crear(rutas, "selfie.y4m", mtime=1000)
    _crear(rutas, "selfie.jpeg", mtime=2000)

    ok, detalle = SelectorUI._estado_archivos()[3][1:]

    assert not ok and "vuelve a generarlo" in detalle


def test_los_textos_ya_no_mencionan_rutas_ni_comandos(rutas):
    textos = " ".join(f"{etiqueta} {detalle}" for etiqueta, _, detalle in SelectorUI._estado_archivos())

    assert "data/" not in textos and "python " not in textos


@pytest.fixture
def datos(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "app_data_dir", lambda: tmp_path)
    return tmp_path


def test_imagenes_dir_es_la_subcarpeta_images_de_los_datos(datos):
    assert paths.imagenes_dir() == datos / "images"
    assert (datos / "images").is_dir()


def test_imagenes_dir_mueve_una_sola_vez_los_archivos_del_esquema_anterior(datos):
    (datos / "selfie.jpeg").write_bytes(b"viejo")
    (datos / "otro.txt").write_bytes(b"no es una imagen de prueba")

    carpeta = paths.imagenes_dir()

    assert (carpeta / "selfie.jpeg").read_bytes() == b"viejo"
    assert not (datos / "selfie.jpeg").exists()
    assert (datos / "otro.txt").exists()


def test_imagenes_dir_no_pisa_lo_que_ya_hay_en_images(datos):
    (datos / "images").mkdir()
    (datos / "images" / "selfie.jpeg").write_bytes(b"nuevo")
    (datos / "selfie.jpeg").write_bytes(b"viejo")

    carpeta = paths.imagenes_dir()

    assert (carpeta / "selfie.jpeg").read_bytes() == b"nuevo"
    assert (datos / "selfie.jpeg").read_bytes() == b"viejo"


def test_el_script_del_video_arranca_como_lo_lanza_ajustes(tmp_path):
    # Ajustes lo ejecuta como script (sys.path[0] = utils/, donde utils/utils.py tapaba al paquete `utils`).
    # Sin selfie debe fallar por la falta de la imagen, no por un error de importación.
    entorno = {**os.environ, "INSUMOSGEN_INSTALADO": "1", "LOCALAPPDATA": str(tmp_path)}
    script = Path(__file__).resolve().parents[1] / "utils" / "generate_fake_camera_video.py"

    proceso = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, env=entorno,
                             cwd=script.parents[1])

    assert proceso.returncode != 0
    assert "ModuleNotFoundError" not in proceso.stderr
    assert "No existe la imagen base" in proceso.stderr
