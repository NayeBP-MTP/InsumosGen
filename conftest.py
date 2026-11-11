import atexit
import os
import signal
import subprocess
import sys
import threading
from datetime import datetime

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import allure

from config.settings import Settings
from utils.allure_utils import ensure_dir, take_step_screenshot
from utils.progress import Progress
from utils.paths import app_data_dir


# Cada `with allure.step("...")` también se reporta a la ventana de progreso.
_allure_step_original = allure.step


def _allure_step_con_progreso(title, *args, **kwargs):
    if isinstance(title, str):
        Progress.emit(title)
    return _allure_step_original(title, *args, **kwargs)


allure.step = _allure_step_con_progreso


# ---------------------------------------------------------------------------
# Cierre garantizado de Chrome/chromedriver
# ---------------------------------------------------------------------------
_CHROMEDRIVER_PIDS = set()


def _kill_process_tree(pid) -> None:
    """Mata un proceso y todos sus hijos (chromedriver → Chrome). Nunca lanza."""
    if not pid:
        return
    try:
        if sys.platform == "win32":
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(pid)],
                capture_output=True, timeout=30,
            )
        else:
            os.kill(int(pid), signal.SIGKILL)
    except Exception:
        pass


def _kill_all_tracked() -> None:
    for pid in list(_CHROMEDRIVER_PIDS):
        _kill_process_tree(pid)
    _CHROMEDRIVER_PIDS.clear()


def _cleanup_orphan_browsers() -> None:
    """
    Al iniciar, cierra restos de corridas anteriores: chromedriver y Chrome de
    automatización (user-data-dir temporal 'scoped_dir') cuyo proceso padre ya no
    existe. No toca el Chrome normal del usuario ni corridas que sigan vivas.
    """
    if sys.platform != "win32":
        return
    script = (
        "$alive = @{}; Get-Process | ForEach-Object { $alive[$_.Id] = $true };"
        "Get-CimInstance Win32_Process | Where-Object {"
        " (($_.Name -eq 'chromedriver.exe') -or"
        "  ($_.Name -eq 'chrome.exe' -and $_.CommandLine -match 'scoped_dir'"
        "   -and $_.CommandLine -notmatch '--type='))"
        " -and -not $alive.ContainsKey([int]$_.ParentProcessId) } |"
        " ForEach-Object { taskkill /F /T /PID $_.ProcessId | Out-Null }"
    )
    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", script],
            capture_output=True, timeout=60,
        )
    except Exception:
        pass


def _on_termination_signal(signum, frame):
    _kill_all_tracked()
    sys.exit(1)


atexit.register(_kill_all_tracked)
for _sig in ("SIGTERM", "SIGBREAK"):
    if hasattr(signal, _sig):
        try:
            signal.signal(getattr(signal, _sig), _on_termination_signal)
        except Exception:
            pass


@pytest.fixture(scope="session")
def screenshots_dir():
    # PID en el nombre evita que dos subprocesos pytest lanzados en el mismo
    # segundo (p. ej. lotes de venta ejecutados uno detrás de otro muy rápido,
    # o en paralelo a futuro) comparan la misma carpeta de screenshots.
    folder = os.path.join(
        str(app_data_dir()),
        "screenshots",
        datetime.now().strftime("run_%Y%m%d_%H%M%S") + f"_{os.getpid()}"
    )
    ensure_dir(folder)
    return folder


@pytest.fixture(scope="session")
def driver(request, screenshots_dir):
    chrome_options = Options()

    # Argumentos existentes
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--remote-allow-origins=*")

    # Permisos de cámara y micrófono
    prefs = {
        "profile.default_content_setting_values.media_stream_camera": 1,
        "profile.default_content_setting_values.media_stream_mic": 1,
        "profile.default_content_setting_values.notifications": 1,

        # Geolocalización
        "profile.default_content_setting_values.geolocation": 1
    }
    chrome_options.add_experimental_option("prefs", prefs)

    # Auto-aceptar popup de permisos
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    chrome_options.add_argument("--enable-geolocation")

    # Evita que Chrome reduzca la prioridad de esta ventana cuando otra la tapa o está
    # en segundo plano (la corrida se hace en un escritorio en uso): el SDK de Legalario
    # detecta el rostro en JS y, throttleado, la cámara fake tardaba en inicializar o el
    # SDK no validaba la cara a tiempo.
    chrome_options.add_argument("--disable-renderer-backgrounding")
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    chrome_options.add_argument("--disable-features=CalculateNativeWinOcclusion")

    # Estabilidad WebRTC con cámara fake en Windows
    # NOTA: NO usar --disable-gpu en Windows con display real, causa crashes
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-webrtc-hw-encoding")
    chrome_options.add_argument("--disable-webrtc-hw-decoding")
    chrome_options.add_argument("--force-webrtc-ip-handling-policy=default_public_interface_only")

    # Cámara fake para flujos desatendidos como Legalario facematch.
    # Chrome requiere archivo .y4m, no acepta .jpg/.jpeg directamente.
    fake_video_path = os.path.abspath(Settings.LEGALARIO_SELFIE_VIDEO_PATH)

    if Settings.USE_FAKE_CAMERA:
        if os.path.exists(fake_video_path):
            chrome_options.add_argument(
                f"--use-file-for-fake-video-capture={fake_video_path}"
            )
            chrome_options.add_argument("--use-fake-device-for-media-stream")
        else:
            raise FileNotFoundError(
                "USE_FAKE_CAMERA=True pero no existe el archivo de cámara fake: "
                f"{fake_video_path}. Genera el video desde Ajustes (⚙ → Generar video) antes de correr la prueba."
            )

    if Settings.HEADLESS:
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--window-size=1920,1080")

        # Recomendado para cámara fake en headless/CI.
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

    _cleanup_orphan_browsers()

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    if service.process:
        _CHROMEDRIVER_PIDS.add(service.process.pid)

    driver.implicitly_wait(Settings.IMPLICIT_WAIT)
    # El default de Selenium (~30s) se queda corto para execute_async_script en
    # force_facematch_request cuando el sandbox de Legalario responde lento (más
    # aún con varias corridas en paralelo compitiendo por el mismo sandbox/VPN).
    driver.set_script_timeout(90)

    request.node.screenshots_dir = screenshots_dir
    try:
        yield driver
    finally:
        # driver.quit() puede colgarse si el navegador quedó congelado: se intenta en
        # un hilo con límite de 15s y, pase lo que pase, se mata el árbol de procesos
        # (chromedriver + todas las ventanas de Chrome).
        quitter = threading.Thread(target=lambda: driver.quit(), daemon=True)
        quitter.start()
        quitter.join(timeout=15)
        if quitter.is_alive():
            print("driver.quit() no respondió en 15s — forzando cierre de Chrome")
        _kill_all_tracked()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        driver = item.funcargs.get("driver")
        screenshots_dir = getattr(item, "screenshots_dir", str(app_data_dir() / "screenshots"))
        if driver:
            try:
                take_step_screenshot(driver, f"error_{item.name}", screenshots_dir, force=True)
            except Exception as exc:
                # Si el navegador ya murió, no abortar la sesión de pytest
                print(f"No se pudo tomar screenshot de error: {exc}")
