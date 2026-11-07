"""Flujo de venta de Cliente Nuevo (CN). Movido de tests/test_login.py."""
import time

import allure

from config.settings import Settings
from flows.venta_comun import (
    flujo_beneficiario_a_finalizar,
    flujo_identidad_a_otp,
    flujo_metodo_entrega,
)
from pages.legalario_page import LegalarioPage
from pages.login_page import LoginPage
from pages.prestamo_personal_page import PrestamoPersonalPage
from services.network_interceptor import NetworkInterceptor


def ejecutar_venta_cn(driver, numero_ciclo: int) -> None:
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


def _flujo_identidad_y_venta(
    driver,
    login_page: LoginPage,
    legalario_page: LegalarioPage,
    interceptor: NetworkInterceptor,
    prestamo_personal_page: PrestamoPersonalPage,
) -> None:
    """Cliente Nuevo (CN): identidad → OTP → plazo/monto → método de entrega → beneficiario → firma."""
    flujo_identidad_a_otp(
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
    flujo_metodo_entrega(driver, login_page, interceptor, prestamo_personal_page)
    flujo_beneficiario_a_finalizar(driver, login_page, interceptor, prestamo_personal_page)
