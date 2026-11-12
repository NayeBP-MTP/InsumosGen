from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException
from utils.allure_utils import take_step_screenshot

import time

from config.settings import Settings


class LoginPage:
    # Selectores flexibles para tolerar variaciones en UAT
    INPUT_ESTRELLA = (By.XPATH, "//input[@placeholder = 'Número de Estrella/Asesor']")
    INPUT_PASSWORD = (By.XPATH, "//input[@placeholder = 'Contraseña']")
    BTN_LOGIN = (By.XPATH, "//button[contains(., 'Ingresar')]")

    BTN_VENTAS = (By.XPATH, "//button[contains(., 'Ventas')]")
    BTN_REGISTRAR_VENTA = (By.XPATH, "//button[contains(., 'Registrar Venta')]")
    BTN_CLIENTE_NUEVO = (By.XPATH, "//button[contains(., 'Cliente nuevo')]")
    BTN_CLIENTE_FRECUENTE = (By.XPATH, "//button[contains(., 'Cliente frecuente')]")
    BTN_REGISTRAR_UNA_VENTA = (By.XPATH, "//button[contains(., 'Registrar una venta')]")

    BTN_INICIAR_PROCESO_DE_IDENTIDAD = (By.XPATH, "//button[contains(., 'Iniciar Proceso de Identidad')]")
    INPUT_CELULAR = (By.XPATH, "//input[@name = 'phone']")
    INPUT_CHECK_PRIVACY = (By.XPATH, "//input[@id = 'legalarioNoticePrivacyAccept']")
    BTN_CONTINUAR = (By.XPATH, "//button[@id = 'legalarioButtonNext']")
    BTN_LEGALARIO_OK = (By.XPATH, "//button[@id = 'legalarioModalButtonOk']")
    BTN_LEGALARIO_CAPTURE_PHOTO = (By.XPATH, "//button[@id = 'legalarioButtonCapturePhoto']")

    BTN_MENU_DROPDOWN = (By.CSS_SELECTOR, "body > app-root > div > app-menu > nav > button")
    BTN_SALIR = (By.CSS_SELECTOR, "#appNavigation > ul > li.nav-item.active > a")


    def __init__(self, driver, timeout: int = 15):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def open(self, url: str) -> None:
        self.driver.get(url)
        self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        take_step_screenshot(self.driver, "01_pagina_login_abierta")

    def wait_until_visible(self, locator, timeout=None):
        """
        Espera hasta que un elemento sea visible en pantalla.

        :param locator: tupla (By, locator)
        :param timeout: tiempo opcional (override del wait global)
        :return: WebElement
        """
        try:
            wait = self.wait if timeout is None else WebDriverWait(self.driver, timeout)

            element = wait.until(
                EC.visibility_of_element_located(locator)
            )
            time.sleep(1)
            return element

        except Exception as exc:
            raise Exception(f"Elemento no visible: {locator}") from exc
        
    def wait_until_clickable(self, locator, timeout=None):
        """
        Espera hasta que un elemento sea clickable.

        :param locator: tupla (By, locator)
        :param timeout: tiempo opcional
        :return: WebElement
        """
        try:
            wait = self.wait if timeout is None else WebDriverWait(self.driver, timeout)

            element = wait.until(
                EC.element_to_be_clickable(locator)
            )
            time.sleep(1)
            return element

        except Exception as exc:
            raise Exception(f"Elemento no clickable: {locator}") from exc
    
    def scroll_to_bottom(self, pause=1, max_attempts=10):
        """
        Hace scroll hasta el final de la página.

        :param pause: tiempo de espera entre scrolls
        :param max_attempts: número máximo de intentos
        """
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        for _ in range(max_attempts):
            # Scroll hasta abajo
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(pause)

            # Nueva altura
            new_height = self.driver.execute_script("return document.body.scrollHeight")

            # Si ya no crece, llegamos al final
            if new_height == last_height:
                break

            last_height = new_height

    def enter_estrella(self, estrella: str) -> None:
        field = self.wait_until_visible(self.INPUT_ESTRELLA)
        field.clear()
        field.send_keys(estrella)
        take_step_screenshot(self.driver, "02_estrella_capturada")

    def enter_password(self, password: str) -> None:
        field = self.wait_until_visible(self.INPUT_PASSWORD)
        field.clear()
        field.send_keys(password)
        take_step_screenshot(self.driver, "03_password_capturado")

    def click_login(self) -> None:
        self.scroll_to_bottom()
        button = self.wait_until_clickable(self.BTN_LOGIN)
        take_step_screenshot(self.driver, "04_antes_de_login")
        button.click()

    def _click_robusto(self, locator, screenshot: str) -> None:
        """
        Click que tolera un modal con `modal-backdrop` aún visible tras el login o una
        navegación (ElementClickInterceptedException): espera a que desaparezca y
        reintenta; como último recurso hace el click por JS.
        """
        button = self.wait_until_clickable(locator)
        take_step_screenshot(self.driver, screenshot)
        try:
            button.click()
            return
        except ElementClickInterceptedException:
            print(f"Click interceptado en {locator}: esperando a que se cierre el modal")
        try:
            WebDriverWait(self.driver, 20).until(
                lambda d: not any(
                    e.is_displayed() for e in d.find_elements(By.CSS_SELECTOR, ".modal-backdrop")
                )
            )
            self.wait_until_clickable(locator).click()
        except Exception:
            self.driver.execute_script(
                "arguments[0].click();", self.driver.find_element(*locator)
            )

    def click_ventas(self) -> None:
        self._click_robusto(self.BTN_VENTAS, "05_antes_de_dar_click")
    
    def click_registrar_ventas(self) -> None:
        self._click_robusto(self.BTN_REGISTRAR_VENTA, "06_antes_de_dar_click")

    def click_cliente_nuevo(self) -> None:
        self._click_robusto(self.BTN_CLIENTE_NUEVO, "07_antes_de_dar_click")

    def click_cliente_frecuente(self) -> None:
        self._click_robusto(self.BTN_CLIENTE_FRECUENTE, "07_antes_de_dar_click_cliente_frecuente")

    def click_registrar_una_ventas(self) -> None:
        button = self.wait_until_clickable(self.BTN_REGISTRAR_UNA_VENTA)
        take_step_screenshot(self.driver, "08_antes_de_dar_click")
        button.click()

    def click_iniciar_proceso_de_identidad(self) -> None:
        time.sleep(3)
        deadline = time.time() + 40
        ultimo_error = None

        while time.time() < deadline:
            try:
                elements = self.driver.find_elements(
                    *self.BTN_INICIAR_PROCESO_DE_IDENTIDAD
                )
                if not elements:
                    time.sleep(1)
                    continue

                btn = elements[0]
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});", btn
                )
                time.sleep(0.5)
                take_step_screenshot(self.driver, "09_antes_de_dar_click")
                self.driver.execute_script("arguments[0].click();", btn)
                return

            except Exception as exc:
                ultimo_error = exc
                time.sleep(1)

        raise Exception(
            f"No se pudo hacer click en 'Iniciar Proceso de Identidad' "
            f"después de 40s. Último error: {ultimo_error}"
        )

    def ingresar_celular(self, celular: str) -> None:
        field = self.wait_until_visible(self.INPUT_CELULAR)
        field.clear()
        field.send_keys(celular)
        take_step_screenshot(self.driver, "10_celular_capturado")

    def marcar_check_privacidad(self) -> None:
        button = self.wait_until_clickable(self.INPUT_CHECK_PRIVACY)
        button.click()

    def click_continuar(self) -> None:
        # Tras el modal de facematch a veces queda un overlay de biometría encima
        # (biometrics-overlay-container) unos segundos más de lo que tarda en
        # volverse "clickable" el botón: se da más margen y se reintenta con JS
        # click si el click nativo queda interceptado por ese overlay.
        button = self.wait_until_clickable(self.BTN_CONTINUAR, timeout=30)
        try:
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", button
            )
        except Exception:
            pass
        try:
            button.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", button)

    def click_continuar_legalario_ok(self) -> None:
        button = self.wait_until_clickable(self.BTN_LEGALARIO_OK)
        button.click()

    def click_tomar_foto(self) -> None:
        button = self.wait_until_clickable(self.BTN_LEGALARIO_CAPTURE_PHOTO)
        button.click()
        time.sleep(30)

    def recuperar_sesion_tras_fallo(self) -> None:
        """
        Deja el navegador en estado limpio tras un ciclo fallido para que el
        siguiente ciclo pueda hacer login: intenta cerrar sesión desde la UI y,
        si no es posible (pantalla intermedia, modal, etc.), borra cookies y
        storage. No lanza excepciones.
        """
        # Primero el cierre local (cookies + storage + volver al login): pulsar "Salir"
        # tras un fallo a mitad de flujo dejó chromedriver colgado varios minutos.
        try:
            self.cerrar_sesion_local()
            return
        except Exception as exc:
            print(f"Recuperación: cerrar_sesion_local falló ({exc}) — intentando 'Salir'")
        try:
            self.cerrar_sesion()
            return
        except Exception as exc:
            print(f"Recuperación: cerrar_sesion no disponible ({exc}) — limpiando cookies/storage")
        try:
            self.driver.delete_all_cookies()
            self.driver.execute_script("window.localStorage.clear(); window.sessionStorage.clear();")
        except Exception as exc:
            print(f"Recuperación: no se pudo limpiar storage ({exc})")

    def cerrar_sesion_local(self) -> None:
        """
        Cierra la sesión del lado del cliente (cookies + storage) y regresa al login,
        sin pulsar "Salir". Se usa tras finalizar la venta: en esas pantallas el click
        en "Salir" dispara un bucle de recarga en el portal que deja chromedriver
        colgado (ReadTimeout) y el navegador inutilizable para el siguiente ciclo.
        """
        take_step_screenshot(self.driver, "cerrar_sesion_local_antes")
        self.driver.delete_all_cookies()
        try:
            self.driver.execute_script(
                "window.localStorage.clear(); window.sessionStorage.clear();"
            )
        except Exception as exc:
            print(f"cerrar_sesion_local: no se pudo limpiar storage ({exc})")
        self.driver.get(Settings.BASE_URL)
        WebDriverWait(self.driver, 30).until(
            lambda d: d.find_elements(*self.INPUT_ESTRELLA)
        )
        take_step_screenshot(self.driver, "cerrar_sesion_local_login")

    def cerrar_sesion(self) -> None:
        menu = self.wait_until_clickable(self.BTN_MENU_DROPDOWN)
        take_step_screenshot(self.driver, "cerrar_sesion_menu_dropdown")
        menu.click()

        salir = self.wait_until_clickable(self.BTN_SALIR)
        take_step_screenshot(self.driver, "cerrar_sesion_click_salir")

        # chromedriver espera a que termine la navegación disparada por el click; si la
        # salida del portal no termina de cargar, el comando se cuelga 120s. Se limita
        # la espera y, si se excede, se corta la carga y se limpia la sesión a mano.
        self.driver.set_page_load_timeout(20)
        try:
            self.driver.execute_script("arguments[0].click();", salir)
        except Exception as exc:
            print(f"cerrar_sesion: la navegación de salida no terminó en 20s ({type(exc).__name__})")
            try:
                self.driver.execute_script("window.stop();")
            except Exception:
                pass
        finally:
            try:
                self.driver.set_page_load_timeout(300)
            except Exception:
                pass

        # Esperar la pantalla de login; aceptar un posible diálogo beforeunload
        deadline = time.time() + 15
        en_login = False
        while time.time() < deadline:
            try:
                self.driver.switch_to.alert.accept()
            except Exception:
                pass
            try:
                if self.driver.find_elements(*self.INPUT_ESTRELLA):
                    en_login = True
                    break
            except Exception:
                pass
            time.sleep(1)

        if not en_login:
            print("cerrar_sesion: sin pantalla de login — limpiando sesión y recargando login")
            self.driver.delete_all_cookies()
            try:
                self.driver.execute_script("window.localStorage.clear(); window.sessionStorage.clear();")
            except Exception:
                pass
            self.driver.get(Settings.BASE_URL)
        take_step_screenshot(self.driver, "cerrar_sesion_completado")

