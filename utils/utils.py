from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from utils.allure_utils import take_step_screenshot

import json
import os


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
            return element

        except Exception as exc:
            raise Exception(f"Elemento no visible: {locator}") from exc
    
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

def save_base64_to_json(base64_str: str, file_path: str = "base64_image.json") -> str:
    data = {
        "base64": base64_str
    }

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return os.path.abspath(file_path)