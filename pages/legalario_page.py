import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from services.image_encoder import ImageEncoder
from utils.allure_utils import take_step_screenshot


class LegalarioPage:
    BTN_LEGALARIO_OK = (By.XPATH, "//button[@id='legalarioModalButtonOk']")
    BTN_LEGALARIO_CAPTURE_PHOTO = (By.XPATH, "//button[@id='legalarioButtonCapturePhoto']")
    BTN_COMENZAR_GRABAR = (By.XPATH, "//button[contains(.,'Comenzar a grabar') or contains(.,'Comenzar grabar')]")
    INPUT_FECHA_NACIMIENTO_OCR = (
        By.ID,
        "nacimiento_ocr"
    )

    def __init__(self, driver, timeout: int = 15):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def wait_until_clickable(self, locator, timeout=None):
        try:
            wait = self.wait if timeout is None else WebDriverWait(self.driver, timeout)
            return wait.until(EC.element_to_be_clickable(locator))
        except Exception as exc:
            raise Exception(f"Elemento no clickable: {locator}") from exc

    def click_continuar_legalario_ok(self) -> None:
        button = self.wait_until_clickable(self.BTN_LEGALARIO_OK)

        # Esperar pequeño tiempo para transición del SDK
        self.driver.implicitly_wait(0)

        try:
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});",
                button
            )
        except Exception:
            pass

        take_step_screenshot(self.driver, "legalario_modal_ok")

        try:
            button.click()
        except Exception:
            # Fallback robusto para overlays/transiciones Legalario
            self.driver.execute_script("arguments[0].click();", button)

        self.driver.implicitly_wait(10)

    def click_tomar_foto(self) -> None:
        button = self.wait_until_clickable(self.BTN_LEGALARIO_CAPTURE_PHOTO)
        take_step_screenshot(self.driver, "legalario_antes_tomar_foto")
        button.click()

    def click_comenzar_grabar(self) -> None:
        """Click en el botón 'Comenzar a grabar' que aparece antes del facematch."""
        import time as _time
        try:
            button = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located(self.BTN_COMENZAR_GRABAR)
            )
            take_step_screenshot(self.driver, "legalario_comenzar_grabar")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
            _time.sleep(0.3)
            self.driver.execute_script("arguments[0].click();", button)
        except Exception as e:
            print(f"Botón 'Comenzar a grabar' no encontrado (puede no aparecer): {e}")

    def prepare_mock_image(self, image_path: str) -> str:
        with allure.step("Preparar imagen mock en base64 para Legalario"):
            return ImageEncoder.image_to_data_url(image_path)

    def prepare_mock_front_image(self, image_path: str) -> str:
        # Se mantiene por compatibilidad con llamadas existentes.
        return self.prepare_mock_image(image_path)

    def extract_base64_from_data_url(self, data_url: str) -> str:
        return data_url.split(",", 1)[1]
    
    def cambiar_fecha_nacimiento_ocr(self, fecha: str) -> None:
        with allure.step(f"Cambiar fecha nacimiento OCR: {fecha}"):

            input_fecha = self.wait.until(
                EC.presence_of_element_located(
                    self.INPUT_FECHA_NACIMIENTO_OCR
                )
            )

            self.driver.execute_script("""
                const input = arguments[0];
                const value = arguments[1];

                input.removeAttribute('readonly');
                input.value = value;

                input.dispatchEvent(new Event('input', { bubbles: true }));
                input.dispatchEvent(new Event('change', { bubbles: true }));
                input.dispatchEvent(new Event('blur', { bubbles: true }));
            """, input_fecha, fecha)

            take_step_screenshot(
                self.driver,
                "legalario_fecha_nacimiento_ocr_modificada"
            )
