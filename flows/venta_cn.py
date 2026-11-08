"""Flujo de venta de Cliente Nuevo (CN). Movido de tests/test_login.py."""
import time
from typing import Optional

import allure

from config.settings import Settings
from flows.resultado_venta import ResultadoVenta, hora_inicio_servidor, localizar_venta
from flows.venta_comun import (
    flujo_beneficiario_a_finalizar,
    flujo_identidad_a_otp,
    flujo_metodo_entrega,
)
from pages.legalario_page import LegalarioPage
from pages.login_page import LoginPage
from pages.prestamo_personal_page import PrestamoPersonalPage
from services.network_interceptor import NetworkInterceptor


def ejecutar_venta_cn(driver, numero_ciclo: int) -> ResultadoVenta:
    """Flujo completo de venta para Cliente Nuevo (CN). Devuelve el resultado localizado en la BD."""
    resultado = ResultadoVenta(
        tipo="CN", agencia_label=Settings.AGENCIA_LABEL, con_seguro=Settings.CON_SEGURO,
        inicio=hora_inicio_servidor(),
    )
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

    resultado.folio = _flujo_identidad_y_venta(
        driver, login_page, legalario_page, interceptor, prestamo_personal_page
    )
    return localizar_venta(resultado)


def _flujo_identidad_y_venta(
    driver,
    login_page: LoginPage,
    legalario_page: LegalarioPage,
    interceptor: NetworkInterceptor,
    prestamo_personal_page: PrestamoPersonalPage,
) -> Optional[str]:
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

    return _flujo_metodo_entrega_a_finalizar(
        driver, login_page, interceptor, prestamo_personal_page
    )


def _flujo_metodo_entrega_a_finalizar(
    driver,
    login_page: LoginPage,
    interceptor: NetworkInterceptor,
    prestamo_personal_page: PrestamoPersonalPage,
) -> Optional[str]:
    """Método de entrega + beneficiario en adelante (usado por CN). Devuelve el folio del front."""
    flujo_metodo_entrega(driver, login_page, interceptor, prestamo_personal_page)
    return flujo_beneficiario_a_finalizar(driver, login_page, interceptor, prestamo_personal_page)
