import hashlib
import subprocess
import zipfile
from pathlib import Path

import pytest

from installer import build_release as br

RAIZ = Path(__file__).resolve().parents[1]


def test_entran_el_codigo_los_tests_y_los_archivos_de_instalacion():
    rutas = br.seleccionar([
        "run.py", "version.py", "launch.pyw", "requirements.txt", "pytest.ini", "README.md",
        "ui/selector_ui.py", "tests/test_login.py", "installer/bootstrap.ps1",
    ])

    assert len(rutas) == 9


@pytest.mark.parametrize("ruta", [
    "InsumosGen/CONTEXT.md", "InsumosGen/generadores/Ofertas/x.sql", ".claude/skills/x/SKILL.md",
    ".github/workflows/release.yml", "release-notes/1.0.0.md", "installer/installer.iss",
    "installer/build_release.py", "tests/test_build_release.py", "CLAUDE.md", "Context.md", "ESPECIFICACIONES.md", "Agreement_Table_Inserts.sql",
    "cf_test_output.log", "captured_requests_front.json", "debug_base64_back.json", "data/catalog.sqlite3",
    ".gitignore", "ui/__pycache__/x.pyc",
])
def test_no_entra_lo_que_no_es_de_la_app(ruta):
    assert br.seleccionar([ruta]) == []


def test_el_readme_si_entra_aunque_los_md_no():
    assert br.seleccionar(["README.md", "CLAUDE.md"]) == ["README.md"]


def test_el_zip_tiene_las_rutas_sin_carpeta_raiz_y_es_reproducible(tmp_path):
    (tmp_path / "ui").mkdir()
    (tmp_path / "run.py").write_text("print(1)")
    (tmp_path / "ui" / "a.py").write_text("x = 1")

    primero = br.construir_zip(["ui/a.py", "run.py"], tmp_path, tmp_path / "uno.zip")
    segundo = br.construir_zip(["run.py", "ui/a.py"], tmp_path, tmp_path / "dos.zip")

    with zipfile.ZipFile(primero) as zf:
        assert zf.namelist() == ["run.py", "ui/a.py"]
        assert zf.read("run.py") == b"print(1)"
    assert br.sha256_de(primero) == br.sha256_de(segundo)


def test_el_sha256_usa_el_formato_de_sha256sum(tmp_path):
    archivo = tmp_path / "InsumosGen-1.0.0.zip"
    archivo.write_bytes(b"contenido")

    destino = br.escribir_sha256(archivo)

    esperado = hashlib.sha256(b"contenido").hexdigest()
    assert destino.name == "InsumosGen-1.0.0.zip.sha256"
    assert destino.read_text(encoding="utf-8") == f"{esperado}  InsumosGen-1.0.0.zip\n"


def test_el_release_real_trae_lo_necesario_y_nada_de_mas(tmp_path):
    zip_ruta = br.construir(tmp_path, RAIZ, version="9.9.9")

    assert zip_ruta.name == "InsumosGen-9.9.9.zip"
    assert (tmp_path / "InsumosGen-9.9.9.zip.sha256").is_file()
    with zipfile.ZipFile(zip_ruta) as zf:
        nombres = set(zf.namelist())
    for requerido in ("run.py", "version.py", "launch.pyw", "requirements.txt", "pytest.ini", "conftest.py",
                      "installer/bootstrap.ps1", "tests/test_login.py", "tests/test_login_cf.py",
                      "tests/test_oferta.py", "ui/selector_ui.py", "pages/login_page.py"):
        assert requerido in nombres, requerido
    assert not [n for n in nombres if n.startswith(("InsumosGen/", ".claude/", ".github/", "data/", "release-notes/"))]
    assert not [n for n in nombres if n.endswith(".md") and n != "README.md"]


def test_el_zip_se_construye_sin_depender_del_directorio_actual(tmp_path):
    salida = subprocess.run(
        ["python", str(RAIZ / "installer" / "build_release.py"), "--salida", str(tmp_path)],
        cwd=tmp_path, capture_output=True, text=True, check=True,
    ).stdout

    assert "sha256:" in salida
    assert list(tmp_path.glob("InsumosGen-*.zip"))
