from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.allure_utils import take_step_screenshot

import time


class OfertasListadoPage:
    """
    Page Object de la pantalla `offerpage` en modo listado (flujo Cliente
    Frecuente): buscador de clientes + tarjetas con "Número de cliente",
    "Nombre del cliente", "Oferta realizada" y un botón de estatus a la
    derecha (ej. "Sin estatus", "Visita Acordada").

    NOTA: los selectores de la tarjeta se basan en el texto visible del
    nombre del cliente (no hay acceso al DOM real todavía), por lo que es
    posible que necesiten ajuste fino una vez validados contra el HTML
    real del portal UAT.
    """

    INPUT_BUSCAR = (By.XPATH, "//input[@placeholder = 'Buscar']")

    def __init__(self, driver, timeout: int = 15):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def wait_until_visible(self, locator, timeout=None):
        try:
            wait = self.wait if timeout is None else WebDriverWait(self.driver, timeout)
            element = wait.until(EC.visibility_of_element_located(locator))
            time.sleep(1)
            return element
        except Exception as exc:
            raise Exception(f"Elemento no visible: {locator}") from exc

    def wait_until_clickable(self, locator, timeout=None):
        try:
            wait = self.wait if timeout is None else WebDriverWait(self.driver, timeout)
            element = wait.until(EC.element_to_be_clickable(locator))
            time.sleep(1)
            return element
        except Exception as exc:
            raise Exception(f"Elemento no clickable: {locator}") from exc

    def buscar_cliente(self, nombre_cliente: str) -> None:
        """Escribe el nombre del cliente en el input Buscar, presiona Enter y espera a que filtre el listado."""
        campo = self.wait_until_visible(self.INPUT_BUSCAR)
        campo.clear()
        campo.send_keys(nombre_cliente)
        take_step_screenshot(self.driver, "ofertas_listado_buscar_cliente_texto")
        campo.send_keys(Keys.ENTER)
        time.sleep(3)  # dar tiempo a que el backend/Angular filtre el listado
        take_step_screenshot(self.driver, "ofertas_listado_buscar_cliente_resultado")

    def _locator_tarjeta(self, nombre_cliente: str, estatus_texto: str = "Sin estatus"):
        """
        Ubica el contenedor de la tarjeta completa (columna de info + recuadro
        de estatus) a partir del texto del nombre del cliente, subiendo al
        ancestro más cercano que contenga TANTO "Oferta realizada" (columna de
        info) COMO el texto de estatus (recuadro derecho). Exigir ambos evita
        quedarse en un ancestro demasiado angosto que solo envuelva la columna
        de info (sin el recuadro de estatus) — visto en la primera versión de
        este selector. Tampoco se ancla por "//button" porque el recuadro de
        estatus no es necesariamente un <button> real.
        """
        return (
            By.XPATH,
            f"//*[contains(normalize-space(text()), '{nombre_cliente}')]"
            f"/ancestor::*[.//*[contains(text(), 'Oferta realizada')] "
            f"and .//*[contains(normalize-space(.), '{estatus_texto}')]][1]"
        )

    def esperar_tarjeta_cliente(self, nombre_cliente: str, estatus_texto: str = "Sin estatus", timeout: int = 20):
        """Espera hasta que la tarjeta del cliente buscado aparezca en el listado filtrado."""
        return self.wait_until_visible(
            self._locator_tarjeta(nombre_cliente, estatus_texto), timeout=timeout
        )

    def click_tarjeta_cliente(self, nombre_cliente: str, estatus_texto: str = "Sin estatus") -> None:
        """
        Da click en el recuadro de estatus de la tarjeta del cliente.
        Por defecto busca el texto 'Sin estatus' (estatus de una oferta recién
        insertada, idEstatusOferta=1).
        """
        tarjeta = self.esperar_tarjeta_cliente(nombre_cliente, estatus_texto)

        boton = tarjeta.find_element(
            By.XPATH, f".//*[contains(normalize-space(.), '{estatus_texto}')]"
        )

        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton)
        take_step_screenshot(self.driver, "ofertas_listado_antes_click_tarjeta")

        try:
            boton.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", boton)

    def seleccionar_cliente(self, nombre_cliente: str, estatus_texto: str = "Sin estatus") -> None:
        """Flujo completo: buscar por nombre y hacer click en su tarjeta."""
        self.buscar_cliente(nombre_cliente)
        self.click_tarjeta_cliente(nombre_cliente, estatus_texto=estatus_texto)
