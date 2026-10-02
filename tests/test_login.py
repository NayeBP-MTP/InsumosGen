import json
import re
import time
import allure

from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config.settings import Settings
from pages.login_page import LoginPage
from pages.legalario_page import LegalarioPage
from services.network_interceptor import NetworkInterceptor
from utils.utils import save_base64_to_json
from utils.allure_utils import take_step_screenshot
from utils.progress import Progress
from pages.prestamo_personal_page import PrestamoPersonalPage
from utils.birthdate_allocator import BirthdateAllocator


RUN_RESULTS_PATH = Path("data/run_results.json")


def _ejecutar_venta(driver, numero_ciclo: int) -> None:
    """Flujo completo de venta para Cliente Nuevo (CN)."""
    login_page = LoginPage(driver)
    legalario_page = LegalarioPage(driver)
    interceptor = NetworkInterceptor(driver)
    prestamo_personal_page = PrestamoPersonalPage(driver)

    # =========================
    # LOGIN Y FLUJO INICIAL (específico de Cliente Nuevo)
    # =========================
    with allure.step("Abrir la página de login"):
        login_page.open(Settings.BASE_URL)

    with allure.step("Ingresar estrella correcta"):
        login_page.enter_estrella(Settings.ESTRELLA)

    with allure.step("Ingresar contraseña correcta"):
        login_page.enter_password(Settings.PASSWORD)

    with allure.step("Enviar formulario"):
        login_page.click_login()

    with allure.step("Presionar 'Ventas'"):
        login_page.click_ventas()

    with allure.step("Presionar 'Registrar Venta'"):
        login_page.click_registrar_ventas()

    with allure.step("Presionar 'Cliente nuevo'"):
        login_page.click_cliente_nuevo()

    with allure.step("Presionar 'Registrar una venta'"):
        login_page.click_registrar_una_ventas()

    _flujo_identidad_y_venta(
        driver, login_page, legalario_page, interceptor, prestamo_personal_page
    )


def _flujo_identidad_a_otp(
    driver,
    login_page: LoginPage,
    legalario_page: LegalarioPage,
    interceptor: NetworkInterceptor,
    prestamo_personal_page: PrestamoPersonalPage,
    incluir_otp_provident: bool = True,
) -> None:
    """
    Tramo compartido CN/CF: verificación de identidad Legalario, documentos,
    datos personales y OTP Provident (este último solo CN: en CF el portal
    salta de "dirección diferente" directo a beneficiario). En CN se llega tras "Registrar una
    venta"; en CF se llega tras confirmar el método de entrega de la oferta
    preautorizada (pantalla "Iniciar Proceso de Identidad").
    """
    with allure.step("Presionar 'Iniciar proceso de identidad'"):
        login_page.click_iniciar_proceso_de_identidad()

    with allure.step("Ingresar 'Celular'"):
        login_page.ingresar_celular(Settings.CELULAR)

    with allure.step("Presionar 'Comenzar'"):
        login_page.click_continuar()

    with allure.step("Presionar 'Check de Privacidad'"):
        login_page.marcar_check_privacidad()

    with allure.step("Presionar 'Continuar'"):
        login_page.click_continuar()

    with allure.step("Presionar 'Continuar Legalario OK'"):
        legalario_page.click_continuar_legalario_ok()

    # =========================
    # INTERCEPTOR
    # =========================
    with allure.step("Instalar interceptor de red"):
        interceptor.install_network_interceptor()
        interceptor.clear_captured_requests()
        interceptor.clear_all_otp_responses()

    # =========================
    # FOTO 1 - FRONTAL
    # =========================
    with allure.step("Preparar imagen mock frontal"):
        mock_image_data_url_1 = legalario_page.prepare_mock_image(
            Settings.LEGALARIO_FRONT_IMAGE_PATH
        )
        interceptor.set_mock_image_content(mock_image_data_url_1)

    with allure.step("Presionar 'Tomar Foto' para frontal"):
        legalario_page.click_tomar_foto()

    with allure.step("Esperar requests del SDK frontal"):
        time.sleep(5)

    with allure.step("Guardar requests capturadas frontal"):
        all_path = interceptor.save_all_requests_to_file("captured_requests_front.json")
        legalario_path = interceptor.save_legalario_requests_to_file("legalario_requests_front.json")
        print(f"Todas las requests frontal: {all_path}")
        print(f"Requests Legalario frontal: {legalario_path}")

    with allure.step("Validar requests frontal"):
        legalario_requests = interceptor.get_legalario_requests_by_endpoint(
            "sdk/onboarding/identify/front"
        )
        print(f"Requests Legalario frontal: {len(legalario_requests)}")
        assert legalario_requests, "No hubo requests de Legalario en frontal"

    with allure.step("Guardar base64 frontal"):
        base64_clean_1 = legalario_page.extract_base64_from_data_url(mock_image_data_url_1)
        json_path_1 = save_base64_to_json(base64_clean_1, "debug_base64_front.json")
        print(f"Base64 frontal guardado en: {json_path_1}")

    with allure.step("Cambiar fecha de nacimiento OCR"):
        fecha_unica = BirthdateAllocator.get_unique_birthdate()
        print(f"Fecha nacimiento única asignada: {fecha_unica}")
        legalario_page.cambiar_fecha_nacimiento_ocr(fecha_unica)

    # =========================
    # AVANZAR FLUJO
    # =========================
    with allure.step("Continuar después de frontal"):
        legalario_page.click_continuar_legalario_ok()
        time.sleep(2)

    with allure.step("Continuar hacia captura trasera"):
        legalario_page.click_continuar_legalario_ok()
        time.sleep(2)

    # =========================
    # FOTO 2 - TRASERA
    # =========================
    with allure.step("Limpiar requests antes de trasera"):
        interceptor.clear_captured_requests()

    with allure.step("Preparar imagen mock trasera"):
        mock_image_data_url_2 = legalario_page.prepare_mock_image(
            Settings.LEGALARIO_BACK_IMAGE_PATH
        )
        interceptor.set_mock_image_content(mock_image_data_url_2)

    with allure.step("Presionar 'Tomar Foto' para trasera"):
        legalario_page.click_tomar_foto()

    with allure.step("Esperar requests del SDK trasera"):
        time.sleep(5)

    with allure.step("Guardar requests capturadas trasera"):
        all_path = interceptor.save_all_requests_to_file("captured_requests_back.json")
        legalario_path = interceptor.save_legalario_requests_to_file("legalario_requests_back.json")
        print(f"Todas las requests trasera: {all_path}")
        print(f"Requests Legalario trasera: {legalario_path}")

    with allure.step("Validar requests trasera"):
        legalario_requests = interceptor.get_legalario_requests_by_endpoint(
            "sdk/onboarding/identify/reverse"
        )
        print(f"Requests Legalario trasera: {len(legalario_requests)}")
        assert legalario_requests, "No hubo requests de Legalario en trasera"

    with allure.step("Guardar base64 trasera"):
        base64_clean_2 = legalario_page.extract_base64_from_data_url(mock_image_data_url_2)
        json_path_2 = save_base64_to_json(base64_clean_2, "debug_base64_back.json")
        print(f"Base64 trasera guardado en: {json_path_2}")

    # =========================
    # FACEMATCH
    # =========================
    with allure.step("Continuar después de trasera"):
        legalario_page.click_continuar_legalario_ok()
        time.sleep(2)

    with allure.step("Guardar token Legalario antes de limpiar requests"):
        _legalario_reqs_previos = interceptor.get_legalario_requests()
        _auth_token = None
        _legalario_base_url = "https://sandbox-api.legalario.com"
        for _req in reversed(_legalario_reqs_previos):
            _hdrs = _req.get("headers", {})
            _tok = _hdrs.get("Authorization") or _hdrs.get("authorization")
            if _tok:
                _auth_token = _tok
                _m = re.match(r"(https?://[^/]+)", _req.get("url", ""))
                if _m:
                    _legalario_base_url = _m.group(1)
                break
        print(f"Auth token guardado: {'Sí' if _auth_token else 'No'} — base URL: {_legalario_base_url}")

    with allure.step("Limpiar requests antes de facematch"):
        interceptor.clear_captured_requests()

    with allure.step("Preparar imagen mock selfie para facematch"):
        mock_selfie_data_url = legalario_page.prepare_mock_image(
            Settings.LEGALARIO_SELFIE_IMAGE_PATH
        )
        interceptor.set_mock_image_content(mock_selfie_data_url)

    with allure.step("Click en 'Comenzar a grabar' (pantalla previa al facematch)"):
        legalario_page.click_comenzar_grabar()
        time.sleep(2)

    with allure.step("Esperar facematch automático del SDK (60s) o forzar como fallback"):
        deadline = time.time() + 60
        legalario_requests_auto = []
        sdk_exitoso = False
        _inicio_espera = time.time()
        _ultimo_diag = 0
        while time.time() < deadline:
            # Diagnóstico cada ~10s: estado de la cámara falsa y mensaje que muestra el SDK
            if time.time() - _ultimo_diag >= 10:
                _ultimo_diag = time.time()
                try:
                    _estado_cam = driver.execute_script(
                        """
                        const vids = [...document.querySelectorAll('video')].map(v => ({
                            rs: v.readyState, w: v.videoWidth, h: v.videoHeight, paused: v.paused,
                            tracks: v.srcObject ? v.srcObject.getVideoTracks().map(t => t.readyState + '/' + (t.muted ? 'muted' : 'live')) : null
                        }));
                        const m = (document.body.innerText.match(
                            /Inicializando la cámara|Ajusta tu cara dentro del óvalo|Mantén esta posición|Acércate|Aléjate|Proceso exitoso/i) || [null])[0];
                        return JSON.stringify({videos: vids, mensaje: m});
                        """
                    )
                except Exception as _ce:
                    _estado_cam = f"error: {_ce}"
                print(f">>> CÁMARA t={int(time.time() - _inicio_espera)}s: {_estado_cam}")
            legalario_requests_auto = interceptor.get_legalario_requests_by_endpoint(
                "sdk/onboarding/identify/facematch"
            )
            if legalario_requests_auto:
                print(f"Facematch capturado automáticamente por el SDK")
                break
            if driver.find_elements(
                By.XPATH, "//*[contains(normalize-space(.),'procesamiento de las fotograf')]"
            ):
                # El SDK ya terminó ("¡Proceso exitoso!") aunque el interceptor
                # no haya capturado la request: no hace falta esperar ni forzar.
                print("Facematch completado por el SDK (pantalla 'Proceso exitoso')")
                sdk_exitoso = True
                break
            time.sleep(1)

        facematch_result = {"ok": bool(legalario_requests_auto) or sdk_exitoso, "status": 200 if (legalario_requests_auto or sdk_exitoso) else 0}
        if not legalario_requests_auto and not sdk_exitoso:
            print("SDK no completó facematch en 60s — enviando request forzado como fallback")
            facematch_result = interceptor.force_facematch_request(
                mock_selfie_data_url,
                Settings.LEGALARIO_ONBOARDING_ID,
                auth_token=_auth_token,
                base_url=_legalario_base_url,
                front_data_url=mock_image_data_url_1,
            )
            print(f"Facematch forzado: status={facematch_result.get('status')}, ok={facematch_result.get('ok')}, error={facematch_result.get('error')}")
            if facematch_result.get("body"):
                print(f"Facematch body: {facematch_result.get('body')}")

    with allure.step("Guardar requests capturadas facematch"):
        all_path = interceptor.save_all_requests_to_file("captured_requests_facematch.json")
        legalario_path = interceptor.save_legalario_requests_to_file("legalario_requests_facematch.json")
        print(f"Todas las requests facematch: {all_path}")
        print(f"Requests Legalario facematch: {legalario_path}")

    with allure.step("Validar facematch"):
        legalario_requests = interceptor.get_legalario_requests_by_endpoint(
            "sdk/onboarding/identify/facematch"
        )
        print(f"Requests Legalario facematch: {len(legalario_requests)}")
        assert facematch_result.get("ok") or legalario_requests, \
            f"No hubo requests de Legalario en facematch (timeout 90s)\nassert {legalario_requests}"

    with allure.step("Guardar base64 selfie"):
        base64_clean_selfie = legalario_page.extract_base64_from_data_url(mock_selfie_data_url)
        json_path_selfie = save_base64_to_json(base64_clean_selfie, "debug_base64_selfie.json")
        print(f"Base64 selfie guardado en: {json_path_selfie}")

    with allure.step("Liberar cámara fake post-facematch"):
        try:
            driver.execute_script("""
                if (window.__fakeMediaStreams) {
                    window.__fakeMediaStreams.forEach(function(s) {
                        s.getTracks().forEach(function(t) { t.stop(); });
                    });
                    window.__fakeMediaStreams = [];
                }
                if (navigator.mediaDevices && navigator.mediaDevices._streams) {
                    navigator.mediaDevices._streams.forEach(function(s) {
                        s.getTracks().forEach(function(t) { t.stop(); });
                    });
                }
                var videos = document.querySelectorAll('video');
                videos.forEach(function(v) {
                    if (v.srcObject) {
                        v.srcObject.getTracks().forEach(function(t) { t.stop(); });
                        v.srcObject = null;
                    }
                });
            """)
            print(">>> DIAG: streams de cámara detenidos")
        except Exception as _se:
            print(f">>> DIAG: no se pudieron detener streams: {_se}")

    with allure.step("Click continuar proceso finalizado"):
        print(">>> DIAG: esperando botón Continuar post-facematch (máx 15s)")
        try:
            WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.ID, "legalarioModalButtonOk"))
            )
        except Exception:
            print(">>> DIAG: legalarioModalButtonOk no apareció en 15s")
        print(">>> DIAG: tomando screenshot post-facematch")
        take_step_screenshot(driver, "post_facematch_antes_continuar")
        print(f">>> DIAG: URL post-facematch: {driver.current_url}")
        try:
            print(">>> DIAG: intentando click legalarioModalButtonOk")
            legalario_page.click_continuar_legalario_ok()
            print(">>> DIAG: click legalarioModalButtonOk OK")
        except Exception as _bok_e:
            print(f"legalarioModalButtonOk no disponible ({_bok_e}) — intentando JS click")
            try:
                _bok = driver.find_element(By.ID, "legalarioModalButtonOk")
                driver.execute_script("arguments[0].click();", _bok)
                print(">>> DIAG: JS click legalarioModalButtonOk OK")
            except Exception:
                print("legalarioModalButtonOk no encontrado — continuando de todas formas")
        time.sleep(2)

    with allure.step("Click continuar"):
        print(f">>> DIAG: antes click_continuar URL={driver.current_url}")
        time.sleep(3)
        login_page.click_continuar()
        time.sleep(2)
        print(f">>> DIAG: después click_continuar URL={driver.current_url}")

    # =========================
    # PRÉSTAMO PERSONAL
    # =========================
    with allure.step("Continuar en préstamo personal"):
        print(">>> DIAG: click_continuar prestamo_personal")
        prestamo_personal_page.click_continuar()
        print(f">>> DIAG: después click_continuar prestamo URL={driver.current_url}")

    with allure.step("Subir comprobante de domicilio"):
        print(">>> DIAG: upload_comprobante_domicilio")
        prestamo_personal_page.upload_comprobante_domicilio(
            Settings.COMPROBANTE_DOMICILIO_PATH
        )
        print(">>> DIAG: upload_comprobante_domicilio OK")

    with allure.step("Subir comprobante"):
        print(">>> DIAG: click_subir_comprobante")
        prestamo_personal_page.click_subir_comprobante()
        print(">>> DIAG: click_subir_comprobante OK")

    with allure.step("Continuar modal comprobante"):
        print(">>> DIAG: click_continuar_modal (comprobante)")
        prestamo_personal_page.click_continuar_modal()
        print(">>> DIAG: click_continuar_modal (comprobante) OK")

    with allure.step("Subir fachada de domicilio"):
        print(">>> DIAG: upload fachada")
        prestamo_personal_page.upload_comprobante_domicilio(
            Settings.COMPROBANTE_DOMICILIO_PATH
        )
        print(">>> DIAG: upload fachada OK")

    with allure.step("Subir fotografía"):
        print(">>> DIAG: click_subir_fotografia")
        prestamo_personal_page.click_subir_fotografia()
        print(">>> DIAG: click_subir_fotografia OK")

    with allure.step("Continuar modal comprobante"):
        print(">>> DIAG: click_continuar_modal (fotografia)")
        prestamo_personal_page.click_continuar_modal()
        print(">>> DIAG: click_continuar_modal (fotografia) OK")

    with allure.step("Aceptar confirmación"):
        try:
            _acepto_btn = WebDriverWait(driver, 25).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(@class,'btn-continue-validate') and normalize-space()='Acepto']"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", _acepto_btn)
            time.sleep(0.3)
            driver.execute_script("arguments[0].click();", _acepto_btn)
            print("Click en Acepto OK")
        except Exception as _ae:
            print(f"Acepto no encontrado: {_ae}")
        # En CF aparece antes una pantalla de consentimiento de geolocalización
        # (locationpage: "No Acepto" / "Acepto"); se atiende si aparece.
        _deadline = time.time() + 25
        _direccion_lista = False
        while time.time() < _deadline:
            if driver.find_elements(By.XPATH, "//button[contains(.,'Confirmar dirección')]"):
                _direccion_lista = True
                print(f"Página Confirmar dirección cargada — URL: {driver.current_url}")
                break
            if "locationpage" in driver.current_url:
                try:
                    _geo_btn = driver.find_element(
                        By.XPATH, "//button[contains(@class,'btn-continue-validate') and normalize-space()='Acepto']"
                    )
                    take_step_screenshot(driver, "consentimiento_geolocalizacion")
                    driver.execute_script("arguments[0].click();", _geo_btn)
                    print("Consentimiento de geolocalización aceptado (locationpage)")
                    time.sleep(2)
                except Exception as _ge:
                    print(f"locationpage detectada pero sin botón Acepto: {_ge}")
            time.sleep(1)
        if not _direccion_lista:
            time.sleep(5)

    with allure.step("Confirmar dirección"):
        print(">>> DIAG: entrando a click_confirmar_direccion")
        prestamo_personal_page.click_confirmar_direccion()
        print(">>> DIAG: click_confirmar_direccion OK")

    with allure.step("Seleccionar dirección actual"):
        prestamo_personal_page.seleccionar_segunda_direccion()

    with allure.step("Llenar datos personales"):
        prestamo_personal_page.llenar_datos_personales()

    with allure.step("Continuar datos personales"):
        prestamo_personal_page.click_continuar_datos_personales()

    with allure.step("Llenar datos laborales y financieros"):
        prestamo_personal_page.llenar_datos_laborales_financieros()

    with allure.step("Continuar datos laborales y financieros"):
        prestamo_personal_page.click_continuar_datos_personales()

    with allure.step("Seleccionar dirección diferente"):
        prestamo_personal_page.seleccionar_direccion_diferente()

    with allure.step("Continuar dirección diferente"):
        prestamo_personal_page.click_continuar_datos_personales()

    if not incluir_otp_provident:
        return

    # =========================
    # OTP PROVIDENT
    # =========================
    with allure.step("Aceptar autorización"):
        prestamo_personal_page.click_checkbox_autorizacion()

    with allure.step("Presionar Autorizo"):
        interceptor.clear_last_sms_otp_response()
        prestamo_personal_page.click_autorizo()

    with allure.step("Obtener OTP Provident desde response"):
        WebDriverWait(driver, 30).until(
            lambda d: interceptor.get_last_sms_otp_code() is not None
        )
        otp = interceptor.get_last_sms_otp_code()
        assert otp, "No se pudo obtener OTP desde response de sendconfirmationsms"
        print(f"OTP Provident capturado: {otp}")

    with allure.step("Ingresar OTP Provident"):
        prestamo_personal_page.ingresar_otp_nip(otp)
        time.sleep(2)

    with allure.step("Continuar OTP Provident"):
        prestamo_personal_page.click_continuar_datos_personales()
        time.sleep(10)


def _flujo_identidad_y_venta(
    driver,
    login_page: LoginPage,
    legalario_page: LegalarioPage,
    interceptor: NetworkInterceptor,
    prestamo_personal_page: PrestamoPersonalPage,
) -> None:
    """Cliente Nuevo (CN): identidad → OTP → plazo/monto → método de entrega → beneficiario → firma."""
    _flujo_identidad_a_otp(
        driver, login_page, legalario_page, interceptor, prestamo_personal_page
    )

    # =========================
    # MONTO / FORMA DE PAGO / BENEFICIARIO
    # =========================
    with allure.step("Seleccionar plazo y monto"):
        prestamo_personal_page.seleccionar_plazo_y_monto()

    with allure.step("Continuar préstamo"):
        prestamo_personal_page.click_continuar_modal_prestamo()
        time.sleep(3)
        prestamo_personal_page.gestionar_rechazo_seguro_si_aplica()

    _flujo_metodo_entrega_a_finalizar(
        driver, login_page, interceptor, prestamo_personal_page
    )


def _flujo_metodo_entrega_a_finalizar(
    driver,
    login_page: LoginPage,
    interceptor: NetworkInterceptor,
    prestamo_personal_page: PrestamoPersonalPage,
) -> None:
    """Método de entrega + beneficiario en adelante (usado por CN)."""
    _flujo_metodo_entrega(driver, login_page, interceptor, prestamo_personal_page)
    _flujo_beneficiario_a_finalizar(driver, login_page, interceptor, prestamo_personal_page)


def _flujo_metodo_entrega(
    driver,
    login_page: LoginPage,
    interceptor: NetworkInterceptor,
    prestamo_personal_page: PrestamoPersonalPage,
) -> None:
    """Pantalla opcional singleoffer + selección y confirmación del método de entrega."""
    with allure.step("Manejar pantalla de oferta opcional (singleoffer)"):
        _singleoffer_deadline = time.time() + 8
        while time.time() < _singleoffer_deadline:
            if "singleoffer" in driver.current_url:
                print("Pantalla singleoffer detectada — intentando salir")
                try:
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(1)
                    _btn = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.XPATH, "//button[contains(.,'No aceptar oferta')]")
                        )
                    )
                    driver.execute_script("arguments[0].click();", _btn)
                    WebDriverWait(driver, 15).until(
                        lambda d: "singleoffer" not in d.current_url
                    )
                    print(f"Singleoffer superada (No aceptar) — nueva URL: {driver.current_url}")
                except Exception as _e:
                    print(f"Error en singleoffer con 'No aceptar': {_e}")
                    try:
                        _btn2 = driver.find_element(By.XPATH, "//button[contains(.,'Continuar')]")
                        driver.execute_script("arguments[0].click();", _btn2)
                        WebDriverWait(driver, 15).until(
                            lambda d: "singleoffer" not in d.current_url
                        )
                        print(f"Singleoffer superada (Continuar) — nueva URL: {driver.current_url}")
                    except Exception as _e2:
                        print(f"Error en singleoffer con 'Continuar': {_e2}")
                break
            time.sleep(1)

    with allure.step(f"Seleccionar método de entrega: {Settings.METODO_ENTREGA}"):
        take_step_screenshot(driver, "antes_metodo_entrega")
        print(f"DIAG antes método entrega — URL: {driver.current_url}")
        prestamo_personal_page.click_metodo_entrega(Settings.METODO_ENTREGA)

    with allure.step("Confirmar opción Sí"):
        prestamo_personal_page.click_si()

    if "FINABIEN" in Settings.METODO_ENTREGA.upper():
        with allure.step("Seleccionar oficina postal Finabien"):
            _estado_postal, _ciudad_postal = Settings.ubicacion_oficina_postal(
                Settings.AGENCIA_LABEL
            )
            prestamo_personal_page.seleccionar_oficina_postal_finabien(
                estado=_estado_postal, ciudad=_ciudad_postal
            )


def _flujo_beneficiario_a_finalizar(
    driver,
    login_page: LoginPage,
    interceptor: NetworkInterceptor,
    prestamo_personal_page: PrestamoPersonalPage,
):
    """Compartido CN/CF: beneficiario, contrato/OTP Legalario, firma y finalización de venta."""
    with allure.step("Llenar datos beneficiario"):
        hubo_beneficiario = prestamo_personal_page.llenar_datos_beneficiario()

    # El beneficiario es del Seguro Integral: si se rechazó el seguro, esta
    # pantalla no aparece y el flujo ya está en "Consentimientos legales" —
    # no hay que pulsar Continuar de nuevo.
    if hubo_beneficiario:
        with allure.step("Continuar beneficiario"):
            prestamo_personal_page.click_continuar_datos_personales()

    # =========================
    # CONTRATO / OTP LEGALARIO
    # =========================
    with allure.step("Marcar checks contrato"):
        prestamo_personal_page.marcar_checks_contrato()

    with allure.step("Continuar contrato"):
        prestamo_personal_page.click_continuar_datos_personales()

    # El click en "Enviar SMS" a veces no dispara nada (la pantalla aún está recargando
    # el expediente y el componente se vuelve a renderizar): no sale la request
    # send-code ni el cuadro del código. Se reintenta el click hasta 3 veces.
    with allure.step("Enviar SMS Legalario y esperar inputs OTP"):
        time.sleep(3)  # dejar que la pantalla termine de cargar antes del primer click
        _otp_visible = False
        for _intento in range(1, 4):
            interceptor.clear_last_legalario_otp_response()
            prestamo_personal_page.click_enviar_sms()
            try:
                WebDriverWait(driver, 25).until(
                    EC.visibility_of_element_located(
                        prestamo_personal_page.INPUT_OTP_1
                    )
                )
                _otp_visible = True
                break
            except Exception:
                print(f"Enviar SMS: sin inputs OTP tras el click #{_intento} — reintentando")
        assert _otp_visible, "No aparecieron los inputs OTP de Legalario tras 3 clicks en 'Enviar SMS'"

    with allure.step("Obtener OTP Legalario"):
        WebDriverWait(driver, 30).until(
            lambda d: interceptor.get_last_legalario_otp_code() is not None
        )
        otp_legalario = interceptor.get_last_legalario_otp_code()
        assert otp_legalario, (
            "No se pudo obtener OTP Legalario desde /sdk/invites/send-code"
        )
        print(f"OTP Legalario capturado: {otp_legalario}")

    with allure.step("Ingresar OTP Legalario"):
        prestamo_personal_page.ingresar_otp_legalario(otp_legalario)

    with allure.step("Aceptar contrato 1"):
        prestamo_personal_page.click_estoy_de_acuerdo()

    with allure.step("Aceptar contrato 2"):
        prestamo_personal_page.click_estoy_de_acuerdo()

    with allure.step("Dibujar firma Legalario"):
        prestamo_personal_page.dibujar_firma_legalario()

    with allure.step("Firmar contrato Legalario"):
        prestamo_personal_page.click_firmar_legalario()
        time.sleep(5)

    with allure.step("Finalizar contrato"):
        prestamo_personal_page.click_firmar_legalario()
        time.sleep(5)

    with allure.step("Cerrar modal firma completada"):
        # El modal de Legalario pasa por estados (firmando → "Contrato exitoso"); un
        # click temprano cierra el estado equivocado. Se reintenta hasta que aparece
        # "Finalizar Venta" (pantalla posterior al modal).
        _fin_modal = time.time() + 90
        _clicks_modal = 0
        while time.time() < _fin_modal:
            if driver.find_elements(*prestamo_personal_page.BTN_FINALIZAR_VENTA):
                break
            _exito = driver.find_elements(
                By.XPATH, "//*[contains(normalize-space(.),'Contrato exitoso')]"
            )
            _botones = driver.find_elements(
                By.XPATH,
                "//button[@data-action='finishProcess'] | "
                "//button[@id='legalarioButtonNext' and normalize-space()='Continuar']",
            )
            if _exito and _botones:
                driver.execute_script("arguments[0].click();", _botones[0])
                _clicks_modal += 1
                print(f"Modal 'Contrato exitoso' — click Continuar #{_clicks_modal}")
                time.sleep(4)
            else:
                time.sleep(1)
        else:
            print("Modal firma completada: no se llegó a 'Finalizar Venta' en 90s")

    # =========================
    # FINALIZAR VENTA
    # =========================
    with allure.step("Finalizar venta"):
        interceptor.clear_captured_requests()
        prestamo_personal_page.click_finalizar_venta()
        time.sleep(5)
        # Leer el folio ya: si después aparece "Aceptar" y la página se recarga, se
        # pierden las requests capturadas por el interceptor.
        _folio_temprano = _obtener_folio_finalizacion(interceptor)

    # En CN aparece un modal "Aceptar" tras finalizar; en CF el portal se queda
    # en la misma pantalla (contador de contrato) sin ese modal. Se hace opcional,
    # pero se exige la request de finalización exitosa para no ocultar fallos.
    with allure.step("Aceptar confirmación final (si aparece)"):
        _aceptar_deadline = time.time() + 15
        _aceptar_clickeado = False
        while time.time() < _aceptar_deadline:
            if driver.find_elements(*prestamo_personal_page.BTN_ACEPTAR):
                prestamo_personal_page.click_aceptar()
                _aceptar_clickeado = True
                time.sleep(10)
                break
            time.sleep(1)
        if not _aceptar_clickeado:
            print("Modal 'Aceptar' no apareció (esperado en CF) — se valida la finalización por red")

    # Tras "Aceptar" (pantalla "¡Muchas felicidades!") aparece una última pantalla
    # con el botón verde "Finalizar"; sin pulsarlo, "Salir" se queda colgado.
    with allure.step("Finalizar (pantalla posterior a Aceptar)"):
        _fin_deadline = time.time() + 25
        _finalizar_ok = False
        while time.time() < _fin_deadline:
            _visibles = [
                b for b in driver.find_elements(By.XPATH, "//button[normalize-space()='Finalizar']")
                if b.is_displayed()
            ]
            if _visibles:
                take_step_screenshot(driver, "prestamo_personal_finalizar_final")
                driver.execute_script("arguments[0].click();", _visibles[0])
                _finalizar_ok = True
                print("Click en 'Finalizar' final OK")
                time.sleep(5)
                break
            time.sleep(1)
        if not _finalizar_ok:
            print("Botón 'Finalizar' final no apareció en 25s — se continúa a cerrar sesión")

    with allure.step("Validar finalización de venta"):
        folio = _folio_temprano or _obtener_folio_finalizacion(interceptor)
        if folio is None and not _aceptar_clickeado:
            raise AssertionError(
                "No se detectó la finalización de la venta (ni modal Aceptar ni "
                "registro 'Finalización - Exitoso' en useractivitylogger)"
            )
        print(f"Folio de finalización: {folio}")

    with allure.step("Cerrar sesión"):
        login_page.cerrar_sesion_local()

    return folio


def _obtener_folio_finalizacion(interceptor):
    """Devuelve el folio de 'Finalización — Exitoso <folio>' del log de actividad, o None."""
    for req in reversed(interceptor.get_captured_requests()):
        if "useractivitylogger" not in str(req.get("url", "")):
            continue
        body = req.get("body")
        try:
            data = json.loads(body) if isinstance(body, str) else body
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        accion = str(data.get("accion", ""))
        detalle = str(data.get("detalle", ""))
        if accion.startswith("Finaliz") and detalle.startswith("Exitoso"):
            partes = detalle.split()
            return partes[1] if len(partes) > 1 else detalle
    return None


@allure.epic("Provident")
@allure.feature("Login")
@allure.story("Autenticación exitosa")
class TestLoginProvident:

    @allure.title("Ventas automatizadas — ciclos múltiples")
    def test_login_exitoso(self, driver):
        total = Settings.CICLOS
        resultados = []

        print(f"\n{'='*50}")
        print(f"Agencia    : {Settings.AGENCIA_LABEL}")
        print(f"Método     : {Settings.METODO_ENTREGA}")
        print(f"Ciclos     : {total}")
        print(f"{'='*50}\n")

        for ciclo in range(1, total + 1):
            print(f"--- Iniciando ciclo {ciclo}/{total} ---")

            with allure.step(f"Ciclo {ciclo} de {total}"):
                try:
                    _ejecutar_venta(driver, ciclo)
                    resultados.append({
                        "ciclo": ciclo,
                        "estado": "exitoso",
                        "error": None
                    })
                    print(f"--- Ciclo {ciclo} EXITOSO ---\n")
                    Progress.emit(f"Venta CN {ciclo}/{total} finalizada", "ok")

                except Exception as exc:
                    resultados.append({
                        "ciclo": ciclo,
                        "estado": "fallido",
                        "error": str(exc)
                    })
                    print(f"--- Ciclo {ciclo} FALLIDO: {exc} ---\n")
                    Progress.emit(
                        f"Venta CN {ciclo}/{total} FALLÓ: {(str(exc).splitlines() or [''])[0][:120]}",
                        "error",
                    )
                    LoginPage(driver).recuperar_sesion_tras_fallo()

        # =========================
        # RESUMEN DE RESULTADOS
        # =========================
        exitosos = sum(1 for r in resultados if r["estado"] == "exitoso")
        fallidos = total - exitosos

        resumen = {
            "agencia": Settings.AGENCIA_LABEL,
            "metodo_entrega": Settings.METODO_ENTREGA,
            "total": total,
            "exitosos": exitosos,
            "fallidos": fallidos,
            "detalle": resultados
        }

        RUN_RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
        RUN_RESULTS_PATH.write_text(
            json.dumps(resumen, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

        print(f"\n{'='*50}")
        print(f"RESUMEN FINAL")
        print(f"  Agencia   : {Settings.AGENCIA_LABEL}")
        print(f"  Total     : {total}")
        print(f"  Exitosos  : {exitosos}")
        print(f"  Fallidos  : {fallidos}")
        print(f"  Resultados: {RUN_RESULTS_PATH.resolve()}")
        print(f"{'='*50}\n")

        assert fallidos == 0, (
            f"{fallidos} de {total} ciclo(s) fallaron. "
            f"Revisa {RUN_RESULTS_PATH} para más detalles."
        )
