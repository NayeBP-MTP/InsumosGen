"""Flujo de venta de Cliente Frecuente (CF). Movido de tests/test_login_cf.py."""
import allure
from pathlib import Path
from config.settings import Settings
from pages.login_page import LoginPage
from pages.prestamo_personal_page import PrestamoPersonalPage
from pages.ofertas_listado_page import OfertasListadoPage
from services.network_interceptor import NetworkInterceptor
from services.offer_repository import OfferRepository
from pages.legalario_page import LegalarioPage
from flows.venta_comun import (
    flujo_beneficiario_a_finalizar,
    flujo_identidad_a_otp,
    flujo_metodo_entrega,
)
from flows.oferta_cf import (
    insertar_oferta_cf,
    limite_monto_agencia,
)


def capturar_diagnostico_falla(driver, ciclo: int) -> None:
    """Guarda screenshot, URL y HTML del punto de falla en data/diagnostico_cf/."""
    try:
        out = Path("data/diagnostico_cf")
        out.mkdir(parents=True, exist_ok=True)
        driver.save_screenshot(str(out / f"ciclo{ciclo}_falla.png"))
        (out / f"ciclo{ciclo}_falla.html").write_text(driver.page_source, encoding="utf-8")
        (out / f"ciclo{ciclo}_falla_url.txt").write_text(driver.current_url, encoding="utf-8")
        interceptor = NetworkInterceptor(driver)
        interceptor.save_to_file(
            interceptor.get_captured_requests(), str(out / f"ciclo{ciclo}_falla_requests.json")
        )
        interceptor.save_to_file(
            {"legalario_otp": interceptor.get_last_legalario_otp_response()},
            str(out / f"ciclo{ciclo}_falla_otp_legalario.json"),
        )
    except Exception as exc:
        print(f"No se pudo capturar diagnóstico: {exc}")


def ejecutar_venta_cf(driver, numero_ciclo: int, contexto_falla: dict = None) -> dict:
    """
    Flujo completo de venta para Cliente Frecuente (CF).

    Orden validado en UAT: oferta preautorizada → método de entrega →
    identidad Legalario → documentos (+ consentimiento de geolocalización) →
    datos personales (sin OTP Provident) → beneficiario → contrato/firma →
    finalizar venta. Ver ESPECIFICACIONES.md.

    `contexto_falla` (opcional): dict mutable donde se anota el `idOferta` recién
    insertado en cuanto se conoce, antes de tocar el navegador. Así, si el resto
    del flujo falla, quien llama puede saber qué oferta quedó huérfana en botDB
    sin depender de comparar snapshots de la tabla de IDs (que no es seguro
    cuando hay varias ventas CF corriendo en paralelo).
    """
    login_page = LoginPage(driver)
    interceptor = NetworkInterceptor(driver)
    prestamo_personal_page = PrestamoPersonalPage(driver)
    legalario_page = LegalarioPage(driver)
    ofertas_listado_page = OfertasListadoPage(driver)

    repo = OfferRepository()
    oferta = insertar_oferta_cf(repo, numero_ciclo)
    if contexto_falla is not None:
        contexto_falla["idOferta"] = oferta.idOferta

    # =========================
    # LOGIN Y FLUJO INICIAL (específico de Cliente Frecuente)
    # =========================
    with allure.step("Abrir la página de login"):
        login_page.open(Settings.BASE_URL)

    with allure.step("Ingresar estrella correcta"):
        login_page.enter_estrella(Settings.ESTRELLA)

    with allure.step("Ingresar contraseña correcta"):
        login_page.enter_password(Settings.PASSWORD)

    with allure.step("Enviar formulario"):
        login_page.click_login()

    with allure.step("Instalar interceptor de red (para OTP Legalario del contrato)"):
        interceptor.install_network_interceptor()
        interceptor.clear_captured_requests()
        interceptor.clear_all_otp_responses()

    with allure.step("Presionar 'Ventas'"):
        login_page.click_ventas()

    with allure.step("Presionar 'Registrar Venta'"):
        login_page.click_registrar_ventas()

    with allure.step("Presionar 'Cliente frecuente'"):
        login_page.click_cliente_frecuente()

    with allure.step(f"Buscar y seleccionar cliente: {oferta.nombreCliente}"):
        try:
            ofertas_listado_page.seleccionar_cliente(oferta.nombreCliente)
        except Exception as exc:
            semana_tabla = repo.get_max_semana()
            raise AssertionError(
                f"La oferta {oferta.idOferta} ('{oferta.nombreCliente}') está en botDB con "
                f"semana={oferta.semana} pero no apareció en el listado del front. Semana más "
                f"reciente en la tabla: {semana_tabla}. El front solo lista la semana más "
                f"reciente; revisa que la oferta la tenga. Detalle: {exc}"
            ) from exc

    with allure.step("Confirmar oferta preautorizada (plazo y monto)"):
        prestamo_personal_page.confirmar_oferta_cf(
            monto_maximo_exclusivo=limite_monto_agencia(Settings.AGENCIA_LABEL)
        )

    flujo_metodo_entrega(driver, login_page, interceptor, prestamo_personal_page)

    flujo_identidad_a_otp(
        driver, login_page, legalario_page, interceptor, prestamo_personal_page,
        incluir_otp_provident=False,
    )

    folio = flujo_beneficiario_a_finalizar(
        driver, login_page, interceptor, prestamo_personal_page
    )

    return {
        "idOferta": oferta.idOferta,
        "nombreCliente": oferta.nombreCliente,
        "folio": folio,
    }
