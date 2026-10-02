import os
from datetime import datetime
import allure

from config.settings import Settings


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def take_step_screenshot(driver, step_name: str, folder: str = "screenshots", force: bool = False) -> str:
    if not force and not Settings.TOMAR_CAPTURAS:
        return ""
    ensure_dir(folder)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    safe_name = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in step_name.lower())
    file_path = os.path.join(folder, f"{timestamp}_{safe_name}.png")
    driver.save_screenshot(file_path)
    allure.attach.file(
        file_path,
        name=step_name,
        attachment_type=allure.attachment_type.PNG,
    )
    return file_path
