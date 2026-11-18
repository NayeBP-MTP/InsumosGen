import winreg

from utils import prereqs


def _registro(valores):
    """Lector de registro falso: {(raiz, vista): ruta}."""
    return lambda raiz, vista=0: valores.get((raiz, vista))


HKCU = (winreg.HKEY_CURRENT_USER, 0)
HKLM64 = (winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_64KEY)
HKLM32 = (winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_32KEY)


def test_chrome_se_encuentra_por_el_registro():
    ruta = prereqs.ruta_chrome(
        leer_clave=_registro({HKLM64: r"C:\Chrome\chrome.exe"}), existe=lambda r: True, entorno={})

    assert ruta == r"C:\Chrome\chrome.exe"


def test_el_registro_tiene_prioridad_para_el_usuario_actual():
    ruta = prereqs.ruta_chrome(
        leer_clave=_registro({HKCU: r"C:\Usuario\chrome.exe", HKLM64: r"C:\Sistema\chrome.exe"}),
        existe=lambda r: True, entorno={})

    assert ruta == r"C:\Usuario\chrome.exe"


def test_una_ruta_del_registro_que_ya_no_existe_se_ignora():
    ruta = prereqs.ruta_chrome(
        leer_clave=_registro({HKLM64: r"C:\Borrado\chrome.exe"}), existe=lambda r: False, entorno={})

    assert ruta is None


def test_sin_registro_se_buscan_las_carpetas_habituales():
    esperada = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

    ruta = prereqs.ruta_chrome(
        leer_clave=_registro({}), existe=lambda r: r == esperada,
        entorno={"PROGRAMFILES": r"C:\Program Files"})

    assert ruta == esperada


def test_instalacion_por_usuario_en_localappdata():
    esperada = r"C:\Users\x\AppData\Local\Google\Chrome\Application\chrome.exe"

    ruta = prereqs.ruta_chrome(
        leer_clave=_registro({}), existe=lambda r: r == esperada,
        entorno={"LOCALAPPDATA": r"C:\Users\x\AppData\Local"})

    assert ruta == esperada


def test_sin_chrome_no_hay_ruta():
    assert prereqs.ruta_chrome(leer_clave=_registro({}), existe=lambda r: False, entorno={}) is None


def test_solo_cuentan_los_drivers_17_y_18_de_sql_server():
    listar = lambda: ["SQL Server", "ODBC Driver 18 for SQL Server", "ODBC Driver 13 for SQL Server",
                      "ODBC Driver 17 for SQL Server", "Microsoft Access Driver"]

    assert prereqs.drivers_odbc_instalados(listar) == [
        "ODBC Driver 17 for SQL Server", "ODBC Driver 18 for SQL Server"]


def test_con_todo_instalado_no_falta_nada():
    estado = prereqs.verificar(chrome=lambda: "chrome.exe", drivers=lambda: ["ODBC Driver 18 for SQL Server"])

    assert all(p.ok for p in estado)
    assert prereqs.faltantes(chrome=lambda: "chrome.exe", drivers=lambda: ["ODBC Driver 18 for SQL Server"]) == []


def test_lo_que_falta_trae_su_enlace_de_descarga():
    faltan = prereqs.faltantes(chrome=lambda: None, drivers=lambda: [])

    assert [p.nombre for p in faltan] == ["Google Chrome", "ODBC Driver 17 o 18 for SQL Server"]
    assert faltan[0].url == prereqs.URL_CHROME
    assert faltan[1].url.startswith("https://learn.microsoft.com/")
    assert "TI" in faltan[1].detalle


def test_solo_falta_el_driver():
    faltan = prereqs.faltantes(chrome=lambda: "chrome.exe", drivers=lambda: [])

    assert [p.nombre for p in faltan] == ["ODBC Driver 17 o 18 for SQL Server"]
