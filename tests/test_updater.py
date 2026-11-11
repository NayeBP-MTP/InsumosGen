import hashlib
import io
import json
import zipfile
from urllib.error import HTTPError

import pytest

from installer import update
from tests.test_primer_arranque import ui  # noqa: F401  (fixture: SelectorUI aislado)
from ui import selector_ui
from utils import updater


class Respuesta(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def _release(tag="v1.1.0", assets=None, cuerpo="Notas"):
    version = tag.lstrip("v")
    if assets is None:
        assets = [f"InsumosGen-{version}.zip", f"InsumosGen-{version}.zip.sha256", f"InsumosGen-Setup-{version}.exe"]
    return {
        "tag_name": tag, "body": cuerpo, "html_url": f"https://github.com/x/y/releases/tag/{tag}",
        "assets": [{"name": n, "browser_download_url": f"https://dl/{n}"} for n in assets],
    }


def _abrir_con(datos):
    return lambda url: Respuesta(json.dumps(datos).encode("utf-8"))


def _abrir_falla(excepcion):
    def abrir(url):
        raise excepcion
    return abrir


def test_con_una_version_mas_nueva_trae_notas_y_enlaces():
    res = updater.comprobar("1.0.0", abrir=_abrir_con(_release("v1.1.0")))

    assert res.hay_nueva and res.version_nueva == "1.1.0" and res.notas == "Notas"
    assert res.url_zip == "https://dl/InsumosGen-1.1.0.zip"
    assert res.url_sha256 == "https://dl/InsumosGen-1.1.0.zip.sha256"
    assert res.url_setup == "https://dl/InsumosGen-Setup-1.1.0.exe"


def test_con_la_misma_version_o_una_mas_vieja_esta_al_dia():
    assert updater.comprobar("1.1.0", abrir=_abrir_con(_release("v1.1.0"))).estado == updater.ESTADO_AL_DIA
    assert updater.comprobar("1.2.0", abrir=_abrir_con(_release("v1.1.0"))).estado == updater.ESTADO_AL_DIA


def test_la_comparacion_es_numerica_no_de_texto():
    assert updater.comprobar("1.9.0", abrir=_abrir_con(_release("v1.10.0"))).hay_nueva


def test_una_prerelease_candidata_es_menor_que_su_version_final():
    assert updater.comprobar("1.0.0-rc.1", abrir=_abrir_con(_release("v1.0.0"))).hay_nueva


@pytest.mark.parametrize("codigo", [403, 429])
def test_el_limite_de_github_se_reporta_sin_lanzar(codigo):
    res = updater.comprobar("1.0.0", abrir=_abrir_falla(HTTPError("u", codigo, "x", {}, None)))

    assert res.estado == updater.ESTADO_ERROR and "limit" in res.mensaje


def test_sin_red_no_lanza():
    res = updater.comprobar("1.0.0", abrir=_abrir_falla(OSError("sin red")))

    assert res.estado == updater.ESTADO_ERROR and res.mensaje


def test_sin_releases_publicados_es_un_error_legible():
    res = updater.comprobar("1.0.0", abrir=_abrir_falla(HTTPError("u", 404, "x", {}, None)))

    assert res.estado == updater.ESTADO_ERROR and "ning" in res.mensaje


def test_una_etiqueta_invalida_es_un_error():
    assert updater.comprobar("1.0.0", abrir=_abrir_con(_release("version-rara"))).estado == updater.ESTADO_ERROR


def test_la_consulta_automatica_solo_ocurre_una_vez_por_arranque(monkeypatch):
    monkeypatch.setattr(updater, "_comprobado_al_arrancar", False)
    abrir = _abrir_con(_release("v1.1.0"))

    assert updater.comprobar_al_arrancar(version_actual="1.0.0", abrir=abrir) is not None
    assert updater.comprobar_al_arrancar(version_actual="1.0.0", abrir=abrir) is None


# --- Descarga ---------------------------------------------------------------------------------------------

def _zip_release(bootstrap_serie="(3, 13)"):
    memoria = io.BytesIO()
    with zipfile.ZipFile(memoria, "w") as zf:
        zf.writestr("requirements.txt", "selenium==4.33.0\r\n")
        zf.writestr("version.py", '__version__ = "1.1.0"\n')
        zf.writestr("installer/bootstrap.ps1", f"$PythonSerie   = @{bootstrap_serie}\r\n")
    return memoria.getvalue()


def _resultado(monkeypatch):
    monkeypatch.setattr(updater, "app_instalada", lambda: True)
    return updater.comprobar("1.0.0", abrir=_abrir_con(_release("v1.1.0")))


def _abrir_descargas(contenido, sha=None):
    sha = sha or hashlib.sha256(contenido).hexdigest()

    def abrir(url):
        if url.endswith(".sha256"):
            return Respuesta(f"{sha}  InsumosGen-1.1.0.zip\n".encode())
        return Respuesta(contenido)
    return abrir


def test_la_descarga_se_verifica_y_se_extrae_a_app_new(tmp_path, monkeypatch):
    res = _resultado(monkeypatch)

    nueva = updater.descargar_actualizacion(res, tmp_path, abrir=_abrir_descargas(_zip_release()))

    assert nueva == tmp_path / "app.new"
    assert (nueva / "requirements.txt").is_file()


def test_un_hash_que_no_coincide_no_se_extrae(tmp_path, monkeypatch):
    res = _resultado(monkeypatch)

    with pytest.raises(updater.ActualizacionError, match="SHA-256"):
        updater.descargar_actualizacion(res, tmp_path, abrir=_abrir_descargas(_zip_release(), sha="0" * 64))

    assert not (tmp_path / "app.new").exists()


def test_un_release_que_cambia_la_serie_de_python_solo_ofrece_el_setup(tmp_path, monkeypatch):
    res = _resultado(monkeypatch)

    with pytest.raises(updater.PythonNuevoError, match="3.99"):
        updater.descargar_actualizacion(res, tmp_path, abrir=_abrir_descargas(_zip_release("(3, 99)")))

    assert not (tmp_path / "app.new").exists()


def test_un_zip_con_rutas_fuera_de_la_carpeta_se_rechaza(tmp_path, monkeypatch):
    memoria = io.BytesIO()
    with zipfile.ZipFile(memoria, "w") as zf:
        zf.writestr("../afuera.txt", "x")
    res = _resultado(monkeypatch)

    with pytest.raises(updater.ActualizacionError):
        updater.descargar_actualizacion(res, tmp_path, abrir=_abrir_descargas(memoria.getvalue()))

    assert not (tmp_path.parent / "afuera.txt").exists()


def test_sin_instalacion_no_se_actualiza_sola(monkeypatch):
    monkeypatch.setattr(updater, "app_instalada", lambda: False)
    res = updater.comprobar("1.0.0", abrir=_abrir_con(_release("v1.1.0")))

    assert res.hay_nueva and not res.puede_actualizar_solo


def test_si_el_release_no_trae_zip_solo_se_ofrece_la_pagina(monkeypatch):
    monkeypatch.setattr(updater, "app_instalada", lambda: True)
    res = updater.comprobar("1.0.0", abrir=_abrir_con(_release("v1.1.0", assets=[])))

    assert res.hay_nueva and not res.puede_actualizar_solo


# --- update.py (helper) -----------------------------------------------------------------------------------

def _instalacion(tmp_path, requirements_viejo="a==1\n", requirements_nuevo="a==1\n"):
    (tmp_path / "app").mkdir()
    (tmp_path / "app" / "requirements.txt").write_bytes(requirements_viejo.encode())
    (tmp_path / "app" / "version.py").write_text('__version__ = "1.0.0"\n')
    (tmp_path / "app.new").mkdir()
    (tmp_path / "app.new" / "requirements.txt").write_bytes(requirements_nuevo.encode())
    (tmp_path / "app.new" / "version.py").write_text('__version__ = "1.1.0"\n')
    (tmp_path / "runtime").mkdir()
    estado = {"appVersion": "1.0.0", "requirementsSha256": hashlib.sha256(requirements_viejo.encode()).hexdigest()}
    (tmp_path / "runtime" / "state.json").write_text(json.dumps(estado))
    return tmp_path


def test_sin_cambios_en_requirements_no_se_corre_pip(tmp_path):
    instalacion = _instalacion(tmp_path)
    llamadas = []

    res = update.aplicar(instalacion, pip=lambda *a: llamadas.append(a) or True)

    assert res["ok"] and res["version"] == "1.1.0" and llamadas == []
    assert (instalacion / "app" / "version.py").read_text().strip().endswith('"1.1.0"')
    assert (instalacion / "app.old" / "version.py").is_file()
    assert not (instalacion / "app.new").exists()
    assert json.loads((instalacion / "runtime" / "state.json").read_text())["appVersion"] == "1.1.0"


def test_con_requirements_nuevos_se_corre_pip_y_se_guarda_el_hash(tmp_path):
    instalacion = _instalacion(tmp_path, requirements_nuevo="a==2\n")
    llamadas = []

    res = update.aplicar(instalacion, pip=lambda python, req, reg: llamadas.append(req.read_bytes().decode()) or True)

    assert res["ok"] and llamadas == ["a==2\n"]
    estado = json.loads((instalacion / "runtime" / "state.json").read_text())
    assert estado["requirementsSha256"] == hashlib.sha256(b"a==2\n").hexdigest()


def test_si_pip_falla_se_restaura_la_version_anterior(tmp_path):
    instalacion = _instalacion(tmp_path, requirements_nuevo="a==2\n")
    resultados = iter([False, True])  # el pip de la actualización falla; el de la restauración funciona

    with pytest.raises(update.UpdateError, match="versión anterior"):
        update.aplicar(instalacion, pip=lambda *a: next(resultados))

    assert (instalacion / "app" / "version.py").read_text().strip().endswith('"1.0.0"')
    assert not (instalacion / "app.old").exists()
    assert json.loads((instalacion / "runtime" / "state.json").read_text())["appVersion"] == "1.0.0"


def test_sin_app_new_no_se_toca_nada(tmp_path):
    instalacion = _instalacion(tmp_path)
    (instalacion / "app.new" / "requirements.txt").unlink()

    with pytest.raises(update.UpdateError):
        update.aplicar(instalacion, pip=lambda *a: True)

    assert (instalacion / "app" / "version.py").is_file()


def test_tras_arrancar_se_borra_app_old_y_se_entrega_el_resultado_una_vez(tmp_path):
    (tmp_path / "app.old").mkdir()
    (tmp_path / "runtime").mkdir()
    (tmp_path / "runtime" / "update_result.json").write_text(json.dumps({"ok": True, "version": "1.1.0"}))

    assert updater.cerrar_actualizacion(tmp_path) == {"ok": True, "version": "1.1.0"}
    assert not (tmp_path / "app.old").exists()
    assert updater.cerrar_actualizacion(tmp_path) is None


# --- Integración con la UI --------------------------------------------------------------------------------

def _nueva(url_zip="https://dl/z.zip", url_sha="https://dl/z.sha256"):
    return updater.Resultado(updater.ESTADO_NUEVA, "1.0.0", version_nueva="1.1.0", notas="Cosas nuevas",
                             url_zip=url_zip, url_sha256=url_sha, url_setup="https://dl/setup.exe")


def test_el_titulo_de_la_ventana_trae_la_version(ui):
    assert selector_ui.__version__ in ui.root.title()


def test_aceptar_el_aviso_instala_la_actualizacion(ui, monkeypatch):
    monkeypatch.setattr(updater, "app_instalada", lambda: True)
    monkeypatch.setattr(selector_ui.messagebox, "askyesno", lambda *a, **k: True)
    instaladas = []
    monkeypatch.setattr(ui, "_instalar_actualizacion", lambda res, parent: instaladas.append(res))

    ui._ofrecer_actualizacion(_nueva(), ui.root)

    assert len(instaladas) == 1


def test_rechazar_el_aviso_no_instala_nada(ui, monkeypatch):
    monkeypatch.setattr(updater, "app_instalada", lambda: True)
    monkeypatch.setattr(selector_ui.messagebox, "askyesno", lambda *a, **k: False)
    monkeypatch.setattr(ui, "_instalar_actualizacion", lambda *a: pytest.fail("no debía instalar"))

    ui._ofrecer_actualizacion(_nueva(), ui.root)


def test_sin_instalacion_el_aviso_abre_la_descarga(ui, monkeypatch):
    monkeypatch.setattr(updater, "app_instalada", lambda: False)
    monkeypatch.setattr(selector_ui.messagebox, "askyesno", lambda *a, **k: True)
    abiertas = []
    monkeypatch.setattr(selector_ui.webbrowser, "open", abiertas.append)

    ui._ofrecer_actualizacion(_nueva(), ui.root)

    assert abiertas == ["https://dl/setup.exe"]


def test_el_aviso_de_arranque_espera_a_que_cierren_las_ventanas_de_primer_arranque(ui, monkeypatch):
    ofrecidas = []
    monkeypatch.setattr(ui, "_ofrecer_actualizacion", lambda res, parent: ofrecidas.append(res))
    ui._resultado_arranque, ui._comprobacion_lista = _nueva(), True

    ui._dialogos_arranque = True
    ui._esperar_comprobacion_arranque()
    assert ofrecidas == []

    ui._dialogos_arranque = False
    ui._esperar_comprobacion_arranque()
    assert len(ofrecidas) == 1


def test_el_aviso_de_arranque_no_sale_si_ya_esta_al_dia(ui, monkeypatch):
    monkeypatch.setattr(ui, "_ofrecer_actualizacion", lambda *a: pytest.fail("no debía avisar"))
    ui._resultado_arranque = updater.Resultado(updater.ESTADO_AL_DIA, "1.0.0")
    ui._comprobacion_lista, ui._dialogos_arranque = True, False

    ui._esperar_comprobacion_arranque()


@pytest.mark.parametrize("ok, funcion", [(True, "showinfo"), (False, "showwarning")])
def test_tras_actualizar_se_avisa_del_resultado(ui, monkeypatch, ok, funcion):
    monkeypatch.setattr(updater, "cerrar_actualizacion", lambda: {"ok": ok, "mensaje": "texto"})
    avisos = []
    monkeypatch.setattr(selector_ui.messagebox, funcion, lambda titulo, texto, **k: avisos.append(texto))

    ui._tras_actualizar()

    assert avisos and "texto" in avisos[0]
