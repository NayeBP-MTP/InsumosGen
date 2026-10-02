import re
import unicodedata
import time

import allure
import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from config.settings import Settings
from utils.allure_utils import take_step_screenshot


class PrestamoPersonalPage:

    BTN_CONTINUAR = (
        By.XPATH,
        "//button[contains(@class,'btn-continue-validate') and contains(.,'Continuar')]"
    )

    BTN_TOMA_UNA_FOTO = (
        By.XPATH,
        "//button[contains(@class,'btn-continue-validate') and contains(.,'Toma una foto')]"
    )

    INPUT_COMPROBANTE_DOMICILIO = (
        By.XPATH,
        "//input[@type='file' and contains(@class,'inpFile')]"
    )

    BTN_SUBIR_COMPROBANTE = (
        By.XPATH,
        "//button[contains(@class,'btn-continue-validate') and contains(.,'Subir comprobante')]"
    )

    BTN_CONTINUAR_MODAL = (
        By.XPATH,
        "//button[@type='button' and @data-dismiss='modal' and contains(.,'Continuar')]"
    )

    BTN_SUBIR_FOTOGRAFIA = (
        By.XPATH,
        "//button[contains(@class,'btn-continue-validate') and contains(.,'Subir fotografía')]"
    )

    BTN_ACEPTO = (
        By.XPATH,
        "//button[contains(@class,'btn-continue-validate') and normalize-space()='Acepto']"
    )

    BTN_CONFIRMAR_DIRECCION = (
        By.XPATH,
        "//button[contains(@class,'btn-continue-validate') and contains(.,'Confirmar dirección')]"
    )

    SELECT_DIRECCION = (
        By.XPATH,
        "//select[@formcontrolname='address']"
    )

    INPUT_TELEFONO_FIJO = (
        By.XPATH,
        "//input[@formcontrolname='landline']"
    )

    INPUT_EMAIL = (
        By.XPATH,
        "//input[@formcontrolname='email']"
    )

    SELECT_ESTADO_CIVIL = (
        By.XPATH,
        "//select[@formcontrolname='maritalStatus']"
    )

    SELECT_DEPENDIENTES = (
        By.XPATH,
        "//select[@formcontrolname='numberOfDependents']"
    )

    SELECT_TIPO_VIVIENDA = (
        By.XPATH,
        "//select[@formcontrolname='householdType']"
    )

    SELECT_ANIOS_VIVIENDA = (
        By.XPATH,
        "//select[@formcontrolname='yearsLivingOnHousehold']"
    )

    SELECT_MESES_VIVIENDA = (
        By.XPATH,
        "//select[@formcontrolname='monthsLivingOnHousehold']"
    )

    BTN_CONTINUAR_DATOS = (
        By.XPATH,
        "//button[contains(@class,'btn-continue-validate') and contains(.,'Continuar')]"
    )

    SELECT_TIPO_EMPLEO = (By.XPATH, "//select[@formcontrolname='jobType']")
    SELECT_OCUPACION = (By.XPATH, "//select[@formcontrolname='ocupation']")
    SELECT_ANTIGUEDAD_ANIOS = (By.XPATH, "//select[@formcontrolname='jobTenureYears']")
    SELECT_ANTIGUEDAD_MESES = (By.XPATH, "//select[@formcontrolname='jobTenureMonths']")
    SELECT_PERIODICIDAD_INGRESO = (By.XPATH, "//select[@formcontrolname='incomeFrequency']")
    INPUT_INGRESO_MENSUAL = (By.XPATH, "//input[@formcontrolname='monthlyIncome']")
    INPUT_GASTOS_MENSUALES = (By.XPATH, "//input[@formcontrolname='monthlyExpenses']")
    INPUT_EFECTIVO_DISPONIBLE = (By.XPATH, "//input[@formcontrolname='availableMonthlyCash']")
    SELECT_PROPOSITO_PRESTAMO = (By.XPATH, "//select[@formcontrolname='loanPurpose']")
    SELECT_DIA_PAGO = (By.XPATH, "//select[@formcontrolname='payDay']")

    SELECT_DIRECCION_DIFERENTE = (
        By.XPATH,
        "//select[@formcontrolname='isAddressDifferent']"
    )

    CHECKBOX_AUTORIZACION = (
        By.XPATH,
        "//input[@type='checkbox' and contains(@class,'form-check-input')]"
    )

    BTN_AUTORIZO = (
        By.XPATH,
        "//button[contains(@class,'btn-continue-validate') and contains(.,'Autorizo')]"
    )

    INPUT_OTP_NIP = (
        By.XPATH,
        "//input[@formcontrolname='Nip']"
    )

    SELECT_PLAZO = (
        By.XPATH,
        "(//select[contains(@class,'modal-content-select')])[1]"
    )

    SELECT_MONTO = (
        By.XPATH,
        "(//select[contains(@class,'modal-content-select')])[2]"
    )

    BTN_CONTINUAR_MODAL_PRESTAMO = (
        By.XPATH,
        "//button[contains(@class,'btn-primary') and contains(.,'Continuar')]"
    )

    BTN_ORDEN_PAGO_BBVA = (
        By.XPATH,
        "//button[contains(@class,'btn-continue-validate') and contains(.,'Orden de Pago BBVA')]"
    )

    BTN_ORDEN_PAGO_HSBC = (
        By.XPATH,
        "//button[contains(@class,'btn-continue-validate') and contains(.,'Orden de pago HSBC')]"
    )

    BTN_ORDEN_PAGO_FINABIEN = (
        By.XPATH,
        "//button[contains(@class,'btn-continue-validate') and contains(.,'FINABIEN')]"
    )

    BTN_EFECTIVO = (
        By.XPATH,
        "//button[contains(@class,'btn-continue-validate') and normalize-space()='Efectivo']"
    )

    BTN_CHEQUE = (
        By.XPATH,
        "//button[contains(@class,'btn-continue-validate') and normalize-space()='Cheque']"
    )

    BTN_SI = (
        By.XPATH,
        "//button[normalize-space()='Si' or normalize-space()='Sí']"
    )

    INPUT_BENEFICIARIO = (
        By.XPATH,
        "//input[@formcontrolname='beneficiary']"
    )

    SELECT_PARENTESCO = (
        By.XPATH,
        "//select[@formcontrolname='relationship']"
    )

    CHECK_ACCEPT_PRIVACY_POLICY = (
        By.XPATH,
        "//input[@formcontrolname='acceptPrivacyPolicy']"
    )

    CHECK_CONFIRM = (
        By.XPATH,
        "//input[@formcontrolname='confirm']"
    )

    CHECK_ACCEPT_MKT = (
        By.XPATH,
        "//input[@formcontrolname='acceptMkt']"
    )

    CHECK_OWNER = (
        By.XPATH,
        "//input[@formcontrolname='owner']"
    )

    BTN_ENVIAR_SMS = (
        By.XPATH,
        "//button[contains(@class,'btn-continue-validate') and contains(.,'Enviar SMS')]"
    )

    BTN_ESTOY_DE_ACUERDO = (
        By.ID,
        "legalarioButtonDocumentAccept"
    )

    CANVAS_FIRMA_LEGALARIO = (
        By.ID,
        "legalarioSignatureCanvas"
    )

    BTN_FIRMAR_LEGALARIO = (
        By.ID,
        "legalarioButtonNext"
    )

    BTN_FINALIZAR_VENTA = (
        By.XPATH,
        "//button[contains(@class,'btn-continue-validate') and contains(.,'Finalizar Venta')]"
    )

    BTN_ACEPTAR = (
        By.XPATH,
        "//button[contains(@class,'btn-continue-validate') and normalize-space()='Aceptar']"
    )

    INPUT_OTP_1 = (By.ID, "legalarioOtpInput1")
    INPUT_OTP_2 = (By.ID, "legalarioOtpInput2")
    INPUT_OTP_3 = (By.ID, "legalarioOtpInput3")
    INPUT_OTP_4 = (By.ID, "legalarioOtpInput4")

    def __init__(self, driver, timeout: int = 20):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def wait_until_clickable(self, locator, timeout=None):
        try:
            wait = self.wait if timeout is None else WebDriverWait(self.driver, timeout)
            return wait.until(EC.element_to_be_clickable(locator))
        except Exception as exc:
            raise Exception(f"Elemento no clickable: {locator}") from exc

    def safe_click(self, element):
        try:
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});",
                element
            )
        except Exception:
            pass

        try:
            element.click()
        except Exception:
            self.driver.execute_script(
                "arguments[0].click();",
                element
            )

    def click_continuar(self) -> None:
        with allure.step("Click en botón Continuar de préstamo personal"):
            button = self.wait_until_clickable(self.BTN_CONTINUAR)

            take_step_screenshot(
                self.driver,
                "prestamo_personal_click_continuar"
            )

            self.safe_click(button)

    def click_toma_una_foto(self) -> None:
        with allure.step("Click en botón Toma una foto"):

            # Espera natural mientras desaparece loader
            button = self.wait_until_clickable(
                self.BTN_TOMA_UNA_FOTO,
                timeout=25
            )

            take_step_screenshot(
                self.driver,
                "prestamo_personal_toma_una_foto"
            )

            self.safe_click(button)
    
    def upload_comprobante_domicilio(self, file_path: str) -> None:
        with allure.step("Subir comprobante de domicilio"):

            if not os.path.exists(file_path):
                raise FileNotFoundError(
                    f"No existe el archivo: {file_path}"
                )

            input_file = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located(self.INPUT_COMPROBANTE_DOMICILIO)
            )

            take_step_screenshot(
                self.driver,
                "upload_comprobante_domicilio"
            )

            input_file.send_keys(os.path.abspath(file_path))
    
    def click_subir_comprobante(self) -> None:
        with allure.step("Click en botón Subir comprobante"):

            button = self.wait_until_clickable(
                self.BTN_SUBIR_COMPROBANTE,
                timeout=25
            )

            take_step_screenshot(
                self.driver,
                "prestamo_personal_subir_comprobante"
            )

            self.safe_click(button)
    
    def click_continuar_modal(self) -> None:
        with allure.step("Click en botón Continuar del modal"):

            button = self.wait_until_clickable(
                self.BTN_CONTINUAR_MODAL,
                timeout=25
            )

            take_step_screenshot(
                self.driver,
                "prestamo_personal_continuar_modal"
            )

            self.safe_click(button)

    def click_subir_fotografia(self) -> None:
        with allure.step("Click en botón Subir fotografía"):

            button = self.wait_until_clickable(
                self.BTN_SUBIR_FOTOGRAFIA,
                timeout=25
            )

            take_step_screenshot(
                self.driver,
                "prestamo_personal_subir_fotografia"
            )

            self.safe_click(button)

    def click_acepto(self) -> None:
        with allure.step("Click en botón Acepto"):

            button = self.wait_until_clickable(
                self.BTN_ACEPTO,
                timeout=25
            )

            take_step_screenshot(
                self.driver,
                "prestamo_personal_acepto"
            )

            self.safe_click(button)
    
    def click_confirmar_direccion(self) -> None:
        with allure.step("Click en botón Confirmar dirección"):
            import time as _time

            WebDriverWait(self.driver, 45).until(
                EC.presence_of_element_located(self.BTN_CONFIRMAR_DIRECCION)
            )
            _time.sleep(2)

            button = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located(self.BTN_CONFIRMAR_DIRECCION)
            )

            take_step_screenshot(
                self.driver,
                "prestamo_personal_confirmar_direccion"
            )

            self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
            _time.sleep(0.5)

            for _intento in range(3):
                try:
                    self.driver.execute_script("arguments[0].click();", button)
                    _time.sleep(1)
                    break
                except Exception:
                    _time.sleep(1)
                    button = self.driver.find_element(*self.BTN_CONFIRMAR_DIRECCION)
    
    def seleccionar_segunda_direccion(self) -> None:
        with allure.step("Seleccionar segunda dirección"):

            select_element = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located(self.SELECT_DIRECCION)
            )

            take_step_screenshot(
                self.driver,
                "prestamo_personal_select_direccion"
            )

            select = Select(select_element)

            # Índice 0 = placeholder
            # Índice 1 = opción #1
            # Índice 2 = opción #2
            select.select_by_index(2)
    
    def llenar_datos_personales(self) -> None:
        with allure.step("Llenar datos personales"):

            # =========================
            # TELÉFONO FIJO
            # =========================
            telefono = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable(self.INPUT_TELEFONO_FIJO)
            )
            telefono.clear()
            telefono.send_keys("5513096751")
            time.sleep(2)

            # =========================
            # EMAIL
            # =========================
            email = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable(self.INPUT_EMAIL)
            )
            email.clear()
            email.send_keys(Settings.CORREO)
            time.sleep(2)

            # =========================
            # ESTADO CIVIL
            # =========================
            select_estado_civil = Select(
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located(self.SELECT_ESTADO_CIVIL)
                )
            )
            select_estado_civil.select_by_visible_text("Soltero")
            time.sleep(2)

            # =========================
            # DEPENDIENTES
            # =========================
            select_dependientes = Select(
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located(self.SELECT_DEPENDIENTES)
                )
            )
            select_dependientes.select_by_visible_text("1")
            time.sleep(2)

            # =========================
            # TIPO VIVIENDA
            # =========================
            select_tipo_vivienda = Select(
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located(self.SELECT_TIPO_VIVIENDA)
                )
            )
            select_tipo_vivienda.select_by_visible_text("Dueño/Propio")
            time.sleep(2)

            # =========================
            # AÑOS VIVIENDA
            # =========================
            select_anios = Select(
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located(self.SELECT_ANIOS_VIVIENDA)
                )
            )
            select_anios.select_by_visible_text("6")
            time.sleep(2)

            # =========================
            # MESES VIVIENDA
            # =========================
            select_meses = Select(
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located(self.SELECT_MESES_VIVIENDA)
                )
            )
            select_meses.select_by_visible_text("11")
            time.sleep(2)

            take_step_screenshot(
                self.driver,
                "prestamo_personal_datos_personales"
            )
    
    def click_continuar_datos_personales(self) -> None:
        with allure.step("Click en Continuar datos personales"):

            button = self.wait_until_clickable(
                self.BTN_CONTINUAR_DATOS,
                timeout=30
            )

            take_step_screenshot(
                self.driver,
                "prestamo_personal_continuar_datos"
            )

            self.safe_click(button)

    def llenar_datos_laborales_financieros(self) -> None:
        with allure.step("Llenar datos laborales y financieros"):

            Select(WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located(self.SELECT_TIPO_EMPLEO)
            )).select_by_visible_text("Tiempo Completo")
            time.sleep(2)

            Select(WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located(self.SELECT_OCUPACION)
            )).select_by_visible_text("Ventas")
            time.sleep(2)

            Select(WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located(self.SELECT_ANTIGUEDAD_ANIOS)
            )).select_by_visible_text("7")
            time.sleep(2)

            Select(WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located(self.SELECT_ANTIGUEDAD_MESES)
            )).select_by_visible_text("11")
            time.sleep(2)

            Select(WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located(self.SELECT_PERIODICIDAD_INGRESO)
            )).select_by_visible_text("Quincenal")
            time.sleep(2)

            ingreso = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable(self.INPUT_INGRESO_MENSUAL)
            )
            ingreso.clear()
            ingreso.send_keys("25000")
            time.sleep(2)

            gastos = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable(self.INPUT_GASTOS_MENSUALES)
            )
            gastos.clear()
            gastos.send_keys("20000")
            time.sleep(2)

            """
            # Este campo viene readonly, normalmente se calcula solo.
            # Intentamos setearlo por JS solo si la app no lo calcula.
            efectivo = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located(self.INPUT_EFECTIVO_DISPONIBLE)
            )
            self.driver.execute_script(
                arguments[0].removeAttribute('readonly');
                arguments[0].value = '5000';
                arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            , efectivo)
            """

            Select(WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located(self.SELECT_PROPOSITO_PRESTAMO)
            )).select_by_visible_text("Educación")
            time.sleep(2)

            Select(WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located(self.SELECT_DIA_PAGO)
            )).select_by_visible_text("Viernes")
            time.sleep(2)

            take_step_screenshot(
                self.driver,
                "prestamo_personal_datos_laborales_financieros"
            )

    def seleccionar_direccion_diferente(self) -> None:
        with allure.step("Seleccionar dirección diferente = No"):

            select = Select(
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located(
                        self.SELECT_DIRECCION_DIFERENTE
                    )
                )
            )

            select.select_by_visible_text("No")

            take_step_screenshot(
                self.driver,
                "prestamo_personal_direccion_diferente"
            )

    def click_checkbox_autorizacion(self) -> None:
        with allure.step("Seleccionar checkbox de autorización"):

            checkbox = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable(
                    self.CHECKBOX_AUTORIZACION
                )
            )

            take_step_screenshot(
                self.driver,
                "prestamo_personal_checkbox_autorizacion"
            )

            try:
                checkbox.click()
            except Exception:
                self.driver.execute_script(
                    "arguments[0].click();",
                    checkbox
                )

    def click_autorizo(self) -> None:
        with allure.step("Click en botón Autorizo"):

            button = self.wait_until_clickable(
                self.BTN_AUTORIZO,
                timeout=30
            )

            take_step_screenshot(
                self.driver,
                "prestamo_personal_autorizo"
            )

            self.safe_click(button)
    
    def ingresar_otp_nip(self, otp: str = "12345") -> None:
        with allure.step(f"Ingresar OTP/NIP: {otp}"):

            input_otp = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable(
                    self.INPUT_OTP_NIP
                )
            )

            input_otp.clear()
            input_otp.send_keys(otp)

            take_step_screenshot(
                self.driver,
                "prestamo_personal_otp_ingresado"
            )
    
    @staticmethod
    def _valor_monto(texto: str):
        """Extrae el número de una opción como '$13400' o '$13,400.00'; None si no aplica."""
        limpio = re.sub(r"[^\d.]", "", (texto or "").replace(",", ""))
        try:
            return float(limpio) if limpio else None
        except ValueError:
            return None

    def seleccionar_plazo_y_monto(self, monto_maximo_exclusivo: float = None) -> None:
        """
        Selecciona plazo y monto. Sin límite: primera opción válida de cada select
        (comportamiento original de CN). Con `monto_maximo_exclusivo` (p. ej. 10000
        para CF en Tijuana): elige el monto más alto ESTRICTAMENTE menor al límite,
        probando otros plazos si el plazo elegido no ofrece ninguno.
        """
        with allure.step("Seleccionar plazo y monto del préstamo"):

            select_plazo_el = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located(self.SELECT_PLAZO)
            )
            WebDriverWait(self.driver, 30).until(
                lambda d: len(Select(select_plazo_el).options) > 1
            )
            total_plazos = len(Select(select_plazo_el).options)

            opciones_vistas = {}
            for indice_plazo in range(1, total_plazos):
                # Re-buscar los selects en cada vuelta (Angular los re-renderiza)
                select_plazo_el = self.driver.find_element(*self.SELECT_PLAZO)
                select_plazo = Select(select_plazo_el)
                select_plazo.select_by_index(indice_plazo)
                nombre_plazo = select_plazo.first_selected_option.text.strip()
                time.sleep(2)

                select_monto_el = WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located(self.SELECT_MONTO)
                )
                WebDriverWait(self.driver, 30).until(
                    lambda d: len(Select(select_monto_el).options) > 1
                )
                select_monto = Select(self.driver.find_element(*self.SELECT_MONTO))
                opciones = [
                    (i, o.text.strip(), self._valor_monto(o.text))
                    for i, o in enumerate(select_monto.options) if i > 0
                ]
                opciones_vistas[nombre_plazo] = [t for _, t, _ in opciones]

                if monto_maximo_exclusivo is None:
                    select_monto.select_by_index(1)  # primera opción válida
                    elegido = opciones[0][1] if opciones else "?"
                    break

                validas = [
                    (i, t, v) for i, t, v in opciones
                    if v is not None and v < monto_maximo_exclusivo
                ]
                if validas:
                    i, elegido, _ = max(validas, key=lambda x: x[2])
                    select_monto.select_by_index(i)
                    break
            else:
                raise AssertionError(
                    f"Ningún monto menor a {monto_maximo_exclusivo:,.0f} disponible en la "
                    f"oferta. Opciones por plazo: {opciones_vistas}"
                )

            print(f"Plazo/monto seleccionados: {nombre_plazo} / {elegido}"
                  + (f" (límite < {monto_maximo_exclusivo:,.0f})" if monto_maximo_exclusivo else ""))
            time.sleep(2)

            take_step_screenshot(
                self.driver,
                "prestamo_personal_plazo_monto"
            )

        self.gestionar_seguro()

    # El toggle del Seguro Integral reusa la misma etiqueta para sus dos estados:
    # "Acepto los beneficios del Seguro Integral" (ON = con seguro) y "Renuncio a
    # los beneficios del Seguro Integral" (OFF = sin seguro). Se ancla en el texto
    # común a ambos estados (confirmado por captura de pantalla real).
    TEXTO_SEGURO_ANCLA = "beneficios del Seguro Integral"

    LOCATOR_LABEL_SEGURO = (
        By.XPATH,
        f"//*[contains(normalize-space(.), '{TEXTO_SEGURO_ANCLA}') "
        f"and not(.//*[contains(normalize-space(.), '{TEXTO_SEGURO_ANCLA}')])]"
    )

    def _leer_estado_seguro(self, timeout: int = 20):
        """Devuelve (elemento_etiqueta, con_seguro_actual) leyendo el texto vigente."""
        label = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(self.LOCATOR_LABEL_SEGURO)
        )
        texto = (label.text or "").strip().lower()
        return label, texto.startswith("acepto")

    def _localizar_toggle_seguro(self, label):
        """
        Busca el control clickeable del toggle junto a la etiqueta del seguro.
        Se prueban varios patrones porque no se confirmó el markup exacto: un
        <input type="checkbox">, un elemento con role="switch", un <label>/<span>
        con clase 'switch'/'toggle', o el propio texto "ON"/"OFF" visible dentro
        del interruptor (visto en la captura real).
        """
        candidatos_xpath = [
            "./following::input[@type='checkbox'][1]",
            "./following::*[@role='switch'][1]",
            "./following::label[contains(@class,'switch') or contains(@class,'toggle')][1]",
            "./following::*[contains(@class,'switch') or contains(@class,'toggle')][1]",
            "./following::*[normalize-space(.)='ON' or normalize-space(.)='OFF'][1]",
        ]
        for xp in candidatos_xpath:
            try:
                elemento = label.find_element(By.XPATH, xp)
                if elemento:
                    return elemento
            except Exception:
                continue
        return None

    # Al rechazar el Seguro Integral aparece(n) pantalla(s) de confirmación por
    # cada beneficio incluido (p. ej. "Reembolso de Gastos Médicos por
    # Accidentes"), cada una con este combo + botón Continuar (confirmado por
    # captura de pantalla real).
    TEXTO_MOTIVO_RECHAZO_SEGURO = "Indica el motivo por el cual el cliente NO lo acepta"

    # Ancla en el nodo más INTERNO que contiene el texto (ver TEXTO_SEGURO_ANCLA más
    # arriba): sin el filtro not(.//*[...]), find_element devolvería el ancestro más
    # externo que lo contiene (p. ej. <body>) y ".../following::select[1]" apuntaría
    # al primer <select> de todo el documento, no al de esta pantalla.
    LOCATOR_LABEL_MOTIVO_RECHAZO_SEGURO = (
        By.XPATH,
        f"//*[contains(normalize-space(.), '{TEXTO_MOTIVO_RECHAZO_SEGURO}') "
        f"and not(.//*[contains(normalize-space(.), '{TEXTO_MOTIVO_RECHAZO_SEGURO}')])]"
    )

    LOCATOR_SELECT_MOTIVO_RECHAZO_SEGURO = (
        By.XPATH,
        f"//*[contains(normalize-space(.), '{TEXTO_MOTIVO_RECHAZO_SEGURO}') "
        f"and not(.//*[contains(normalize-space(.), '{TEXTO_MOTIVO_RECHAZO_SEGURO}')])]"
        "/following::select[1]"
    )

    BTN_CONTINUAR_MOTIVO_RECHAZO_SEGURO = (
        By.XPATH,
        "//button[normalize-space()='Continuar']"
    )

    def _gestionar_pantallas_rechazo_seguro(self, intentos_maximos: int = 5) -> None:
        """
        Resuelve, una tras otra, las pantallas "Indica el motivo por el cual el
        cliente NO lo acepta" que aparecen tras rechazar el Seguro Integral (una
        por cada beneficio incluido). En cada una elige la primera opción real
        del combo y pulsa Continuar, hasta que la pantalla deje de aparecer.
        """
        for intento in range(1, intentos_maximos + 1):
            try:
                select_el = WebDriverWait(self.driver, 6).until(
                    EC.presence_of_element_located(self.LOCATOR_SELECT_MOTIVO_RECHAZO_SEGURO)
                )
            except Exception:
                return  # ya no hay más pantallas de este tipo

            with allure.step(f"Indicar motivo de rechazo de beneficio del seguro ({intento})"):
                take_step_screenshot(self.driver, f"seguro_motivo_rechazo_{intento}_antes")

                select = Select(select_el)
                opciones_validas = [
                    i for i, o in enumerate(select.options)
                    if (o.get_attribute("value") or "").strip() not in ("", "0")
                ]
                if not opciones_validas:
                    raise AssertionError(
                        "El combo 'Indica el motivo por el cual el cliente NO lo acepta' no "
                        "tiene opciones seleccionables."
                    )
                select.select_by_index(opciones_validas[0])
                print(f"Motivo de rechazo del seguro ({intento}): {select.first_selected_option.text.strip()}")
                time.sleep(1)

                # Acotado al <select> de ESTA pantalla (no un XPath global), para no
                # atrapar un botón "Continuar" de otra parte del DOM.
                try:
                    boton = select_el.find_element(
                        By.XPATH, "./following::button[normalize-space()='Continuar'][1]"
                    )
                except Exception:
                    boton = WebDriverWait(self.driver, 15).until(
                        EC.element_to_be_clickable(self.BTN_CONTINUAR_MOTIVO_RECHAZO_SEGURO)
                    )
                take_step_screenshot(self.driver, f"seguro_motivo_rechazo_{intento}_seleccionado")
                self.safe_click(boton)
                time.sleep(1.5)
        else:
            raise AssertionError(
                f"Se alcanzó el máximo de {intentos_maximos} pantallas de motivo de rechazo "
                "del seguro sin que dejaran de aparecer; revisa si el flujo real tiene más."
            )

    def gestionar_seguro(self, con_seguro: bool = None) -> None:
        """
        En el modal de oferta (plazo/monto) hay un toggle de Seguro Integral que
        empieza en ON (con seguro, "Acepto los beneficios..."). Deja el toggle en
        el estado pedido por `con_seguro` (o Settings.CON_SEGURO si no se pasa),
        haciendo click solo si el estado actual no coincide.
        """
        if con_seguro is None:
            con_seguro = Settings.CON_SEGURO

        with allure.step(
            f"Confirmar Seguro Integral: {'con seguro' if con_seguro else 'sin seguro'}"
        ):
            label, con_seguro_actual = self._leer_estado_seguro()
            print(
                f"Seguro Integral — estado actual: "
                f"{'con seguro (Acepto)' if con_seguro_actual else 'sin seguro (Renuncio)'}, "
                f"pedido: {'con seguro' if con_seguro else 'sin seguro'}"
            )
            if con_seguro_actual == con_seguro:
                return  # ya está en el estado pedido, no se toca

            toggle = self._localizar_toggle_seguro(label)
            if toggle is None:
                take_step_screenshot(self.driver, "seguro_toggle_no_encontrado")
                raise AssertionError(
                    f"No se encontró el toggle de Seguro Integral junto a "
                    f"'{self.TEXTO_SEGURO_ANCLA}' en el modal de oferta para dejarlo en "
                    f"{'con seguro' if con_seguro else 'sin seguro'}. Inspecciona el DOM "
                    "real (F12) y actualiza PrestamoPersonalPage._localizar_toggle_seguro()."
                )

            take_step_screenshot(self.driver, "seguro_antes_click")
            self.safe_click(toggle)
            time.sleep(1)
            take_step_screenshot(self.driver, "seguro_despues_click")

            _, con_seguro_final = self._leer_estado_seguro(timeout=10)
            if con_seguro_final != con_seguro:
                take_step_screenshot(self.driver, "seguro_estado_no_confirmado")
                raise AssertionError(
                    f"Se pidió dejar el Seguro Integral en "
                    f"'{'con seguro' if con_seguro else 'sin seguro'}', pero tras el click "
                    f"sigue en '{'con seguro' if con_seguro_final else 'sin seguro'}'. "
                    "Revisa la captura 'seguro_estado_no_confirmado'."
                )
            print(f"Seguro Integral confirmado: {'con seguro' if con_seguro else 'sin seguro'}")

    def gestionar_rechazo_seguro_si_aplica(self, con_seguro: bool = None) -> None:
        """
        Debe llamarse justo después de click_continuar_modal_prestamo() cuando se
        pidió la venta sin seguro: ahí aparecen las pantallas "Indica el motivo
        por el cual el cliente NO lo acepta" (una por cada beneficio del seguro,
        p. ej. Reembolso de Gastos Médicos). No hace nada si `con_seguro` (o
        Settings.CON_SEGURO si no se pasa) es True.
        """
        if con_seguro is None:
            con_seguro = Settings.CON_SEGURO
        if con_seguro:
            return
        self._gestionar_pantallas_rechazo_seguro()

    # Segundo toggle de Seguro Integral, en la pantalla "Consentimientos legales"
    # (sección Términos y condiciones, URL .../legalconsentpage, paso 1 de 3).
    # A diferencia del toggle del modal de oferta, aquí la etiqueta NO cambia de
    # texto con el estado — el propio control muestra "SI"/"NO" — confirmado por
    # captura de pantalla real.
    TEXTO_CONSENTIMIENTO_SEGURO = "Acepto contar con los beneficios que me brinda el Seguro Integral"

    LOCATOR_LABEL_CONSENTIMIENTO_SEGURO = (
        By.XPATH,
        f"//*[contains(normalize-space(.), '{TEXTO_CONSENTIMIENTO_SEGURO}') "
        f"and not(.//*[contains(normalize-space(.), '{TEXTO_CONSENTIMIENTO_SEGURO}')])]"
    )

    def _leer_estado_consentimiento_seguro(self, timeout: int = 20):
        """Devuelve (label, toggle, con_seguro_actual). toggle/con_seguro_actual son None si no se encontró el control."""
        label = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(self.LOCATOR_LABEL_CONSENTIMIENTO_SEGURO)
        )
        toggle = self._localizar_toggle_seguro(label)
        if toggle is None:
            return label, None, None
        texto_toggle = (toggle.text or "").strip().upper()
        con_seguro_actual = texto_toggle in ("SI", "SÍ")
        return label, toggle, con_seguro_actual

    def gestionar_consentimiento_seguro(self, con_seguro: bool = None) -> None:
        """
        En "Consentimientos legales" (Términos y condiciones) a veces aparece otro
        toggle de Seguro Integral, independiente del modal de oferta — pero no
        siempre: si el estado ya es el que corresponde por defecto, la app salta
        directo al paso 2 (checks de contrato) sin mostrarlo. Por eso la espera
        inicial es corta y best-effort: si la pantalla no aparece, se asume que
        no aplica y se continúa sin tocar nada.
        """
        if con_seguro is None:
            con_seguro = Settings.CON_SEGURO

        with allure.step(
            f"Consentimiento legal Seguro Integral: {'con seguro' if con_seguro else 'sin seguro'}"
        ):
            try:
                label, toggle, con_seguro_actual = self._leer_estado_consentimiento_seguro(timeout=8)
            except Exception:
                print(
                    "Pantalla de consentimiento del Seguro Integral no apareció — se omite "
                    f"(URL actual: {self.driver.current_url})"
                )
                return
            if toggle is None:
                take_step_screenshot(self.driver, "consentimiento_seguro_toggle_no_encontrado")
                raise AssertionError(
                    f"No se encontró el toggle de Seguro Integral junto a "
                    f"'{self.TEXTO_CONSENTIMIENTO_SEGURO}' en Consentimientos legales. "
                    "Inspecciona el DOM real (F12) y actualiza "
                    "PrestamoPersonalPage._localizar_toggle_seguro()."
                )
            print(
                f"Consentimiento Seguro Integral — estado actual: "
                f"{'con seguro (SI)' if con_seguro_actual else 'sin seguro (NO)'}, "
                f"pedido: {'con seguro' if con_seguro else 'sin seguro'}"
            )
            if con_seguro_actual == con_seguro:
                if not con_seguro:
                    self._gestionar_pantallas_rechazo_seguro()
                return

            take_step_screenshot(self.driver, "consentimiento_seguro_antes_click")
            self.safe_click(toggle)
            time.sleep(1)
            take_step_screenshot(self.driver, "consentimiento_seguro_despues_click")

            _, _, con_seguro_final = self._leer_estado_consentimiento_seguro(timeout=10)
            if con_seguro_final != con_seguro:
                take_step_screenshot(self.driver, "consentimiento_seguro_estado_no_confirmado")
                raise AssertionError(
                    f"Se pidió dejar el consentimiento del Seguro Integral en "
                    f"'{'con seguro' if con_seguro else 'sin seguro'}', pero tras el click "
                    f"sigue en '{'con seguro' if con_seguro_final else 'sin seguro'}'. "
                    "Revisa la captura 'consentimiento_seguro_estado_no_confirmado'."
                )
            print(f"Consentimiento Seguro Integral confirmado: {'con seguro' if con_seguro else 'sin seguro'}")

            if not con_seguro:
                self._gestionar_pantallas_rechazo_seguro()

    def confirmar_oferta_cf(self, monto_maximo_exclusivo: float = None) -> None:
        """
        Pantalla `offerpage` en modo confirmación (flujo Cliente Frecuente):
        el plazo/monto ya viene acotado por la oferta insertada en botDB, solo
        hay que confirmarlos y continuar. Reutiliza los mismos selectores que
        el modal de plazo/monto de Cliente Nuevo (SELECT_PLAZO/SELECT_MONTO),
        ya que ambos parecen ser la misma pantalla `offerpage` en distintos
        puntos del flujo. Pendiente de validar contra el DOM real.
        """
        with allure.step("Confirmar oferta preautorizada (plazo y monto)"):
            self.seleccionar_plazo_y_monto(monto_maximo_exclusivo)
            self.click_continuar_modal_prestamo()
            self.gestionar_rechazo_seguro_si_aplica()

    def click_continuar_modal_prestamo(self) -> None:
        with allure.step("Click en continuar modal préstamo"):

            button = self.wait_until_clickable(
                self.BTN_CONTINUAR_MODAL_PRESTAMO,
                timeout=30
            )

            take_step_screenshot(
                self.driver,
                "prestamo_personal_continuar_modal_prestamo"
            )

            self.safe_click(button)
    
    def click_orden_pago_bbva(self) -> None:
        with allure.step("Click en Orden de Pago BBVA"):

            button = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located(self.BTN_ORDEN_PAGO_BBVA)
            )

            take_step_screenshot(
                self.driver,
                "prestamo_personal_orden_pago_bbva"
            )

            self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
            self.driver.execute_script("arguments[0].click();", button)

    def click_metodo_entrega(self, metodo: str) -> None:
        import time as _time
        _metodo = metodo.strip().upper()
        if "BBVA" in _metodo:
            locator = self.BTN_ORDEN_PAGO_BBVA
            label = "BBVA"
        elif "HSBC" in _metodo:
            locator = self.BTN_ORDEN_PAGO_HSBC
            label = "HSBC"
        elif "FINABIEN" in _metodo:
            locator = self.BTN_ORDEN_PAGO_FINABIEN
            label = "Finabien"
        elif "EFECTIVO" in _metodo:
            locator = self.BTN_EFECTIVO
            label = "Efectivo"
        elif "CHEQUE" in _metodo:
            locator = self.BTN_CHEQUE
            label = "Cheque"
        else:
            locator = (
                By.XPATH,
                f"//button[contains(@class,'btn-continue-validate') and contains(.,'{metodo}')]"
            )
            label = metodo

        with allure.step(f"Click en método de entrega: {label}"):
            button = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located(locator)
            )
            take_step_screenshot(self.driver, f"metodo_entrega_{label.lower()}")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
            _time.sleep(0.3)
            self.driver.execute_script("arguments[0].click();", button)

    def seleccionar_oficina_postal_finabien(
        self,
        estado="Puebla",
        ciudad=None,
    ) -> None:
        """
        Selecciona Estado → Ciudad → primera Oficina Postal y confirma. `estado` y
        `ciudad` pueden ser un texto o una tupla de candidatos (sin acentos ni
        mayúsculas). Si no se encuentra el estado o la ciudad pedidos, falla listando
        las opciones (no se elige otra en silencio: sería una oficina de otro lugar).
        """
        import time as _time
        from selenium.webdriver.support.ui import Select as _Select

        with allure.step("Seleccionar oficina postal Finabien"):
            from selenium.webdriver.support.ui import Select as _Select

            def _norm(texto):
                base = unicodedata.normalize("NFKD", texto or "")
                return "".join(c for c in base if not unicodedata.combining(c)).lower().strip()

            def _angular_select(select_el, keyword=None, use_index=None, etiqueta="opción"):
                """Selecciona una opción y dispara eventos para Angular."""
                sel = _Select(select_el)
                opts = [o for o in sel.options if o.get_attribute("value") not in ("", "0", None, "undefined")]
                if not opts:
                    return
                if keyword:
                    candidatos = [keyword] if isinstance(keyword, str) else list(keyword)
                    target = None
                    # 1) coincidencia exacta, 2) el texto contiene el candidato
                    for modo in ("exacta", "contiene"):
                        for cand in candidatos:
                            c = _norm(cand)
                            target = next(
                                (o for o in opts
                                 if (_norm(o.text) == c if modo == "exacta" else c in _norm(o.text))),
                                None,
                            )
                            if target:
                                break
                        if target:
                            break
                    if target is None:
                        raise AssertionError(
                            f"No se encontró {etiqueta} {candidatos} en las opciones del portal: "
                            f"{[o.text.strip() for o in opts]}"
                        )
                elif use_index is not None:
                    target = opts[use_index] if use_index < len(opts) else opts[0]
                else:
                    target = opts[0]
                print(f"Oficina postal — {etiqueta}: {target.text.strip()}")
                val = target.get_attribute("value")
                # Cambiar value vía JS nativo para que Angular lo detecte
                self.driver.execute_script(
                    """
                    var sel = arguments[0], val = arguments[1];
                    var nativeSetter = Object.getOwnPropertyDescriptor(
                        window.HTMLSelectElement.prototype, 'value'
                    ).set;
                    nativeSetter.call(sel, val);
                    sel.dispatchEvent(new Event('input',  {bubbles:true}));
                    sel.dispatchEvent(new Event('change', {bubbles:true}));
                    """,
                    select_el, val
                )

            # --- Esperar modal ---
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//button[contains(.,'Confirmar')]")
                )
            )
            _time.sleep(0.8)

            # --- Estado ---
            selects = self.driver.find_elements(By.XPATH, "//select")
            _angular_select(selects[0], keyword=estado, etiqueta="estado")
            _time.sleep(2.0)

            # --- Ciudad (por defecto, la misma que el estado) ---
            WebDriverWait(self.driver, 15).until(
                lambda d: len(
                    [o for o in _Select(d.find_elements(By.XPATH, "//select")[1]).options
                     if o.get_attribute("value") not in ("", "0", None, "undefined")]
                ) > 0
            )
            selects = self.driver.find_elements(By.XPATH, "//select")
            _angular_select(selects[1], keyword=ciudad or estado, etiqueta="ciudad")
            _time.sleep(2.0)

            # --- Oficina Postal: primera disponible ---
            WebDriverWait(self.driver, 15).until(
                lambda d: len(
                    [o for o in _Select(d.find_elements(By.XPATH, "//select")[2]).options
                     if o.get_attribute("value") not in ("", "0", None, "undefined")]
                ) > 0
            )
            selects = self.driver.find_elements(By.XPATH, "//select")
            _angular_select(selects[2], use_index=0)
            _time.sleep(0.5)

            # --- Confirmar Oficina Postal ---
            btn_confirmar = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//button[normalize-space()='Confirmar Oficina Postal' or normalize-space()='Confirmar oficina postal']")
                )
            )
            take_step_screenshot(self.driver, "finabien_oficina_postal")
            self.driver.execute_script("arguments[0].click();", btn_confirmar)
            _time.sleep(1.5)

            # --- Modal de confirmación final ("Confirmar" verde) ---
            try:
                btn_confirmar_final = WebDriverWait(self.driver, 8).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//button[normalize-space()='Confirmar']")
                    )
                )
                take_step_screenshot(self.driver, "finabien_confirmar_final")
                self.driver.execute_script("arguments[0].click();", btn_confirmar_final)
                _time.sleep(1)
            except Exception:
                pass

    def click_si(self) -> None:
        with allure.step("Click en botón Sí"):

            button = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located(self.BTN_SI)
            )

            take_step_screenshot(
                self.driver,
                "prestamo_personal_btn_si"
            )

            self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
            self.driver.execute_script("arguments[0].click();", button)
            time.sleep(2)
            take_step_screenshot(self.driver, "prestamo_personal_despues_btn_si")
            print(f"DIAG después de click Sí — URL: {self.driver.current_url}")

    def llenar_datos_beneficiario(self) -> bool:
        """
        El "beneficiario" es el beneficiario del Seguro Integral (quien cobra en
        caso de siniestro), no del préstamo. Cuando la venta es sin seguro, esta
        pantalla NO aparece y el flujo salta directo a "Consentimientos legales"
        (confirmado por captura real: tras confirmar el método de entrega, con
        seguro rechazado se aterriza ya en esa pantalla). Por eso esto es
        best-effort: espera poco y, si no aparece, se asume que se omitió y
        devuelve False en vez de fallar.
        """
        with allure.step("Llenar datos de beneficiario (si aplica)"):
            take_step_screenshot(self.driver, "prestamo_personal_antes_beneficiario")

            timeout = 30 if Settings.CON_SEGURO else 8
            try:
                beneficiario = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable(
                        self.INPUT_BENEFICIARIO
                    )
                )
            except Exception:
                if not Settings.CON_SEGURO:
                    print(
                        "Pantalla de beneficiario no apareció (venta sin seguro: se omite, "
                        f"URL actual: {self.driver.current_url})"
                    )
                    take_step_screenshot(self.driver, "prestamo_personal_beneficiario_omitido")
                    return False
                take_step_screenshot(self.driver, "prestamo_personal_beneficiario_timeout")
                print(f"DIAG beneficiario timeout — URL: {self.driver.current_url}")
                raise

            beneficiario.clear()
            beneficiario.send_keys("Diego Alonso Sanchez")
            time.sleep(2)

            parentesco = Select(
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located(
                        self.SELECT_PARENTESCO
                    )
                )
            )

            parentesco.select_by_visible_text("Hijo/a")
            time.sleep(2)

            take_step_screenshot(
                self.driver,
                "prestamo_personal_beneficiario"
            )
            return True

    def marcar_checks_contrato(self) -> None:
        # "Consentimientos legales" es el paso 1 de 3 de Términos y condiciones:
        # trae su propio toggle de Seguro Integral, independiente del de la
        # pantalla de oferta.
        self.gestionar_consentimiento_seguro()

        with allure.step("Marcar checks de contrato"):

            checks = [
                self.CHECK_ACCEPT_PRIVACY_POLICY,
                self.CHECK_CONFIRM,
                self.CHECK_ACCEPT_MKT,
                self.CHECK_OWNER
            ]

            for locator in checks:

                checkbox = WebDriverWait(self.driver, 30).until(
                    EC.element_to_be_clickable(locator)
                )

                try:
                    self.driver.execute_script(
                        "arguments[0].scrollIntoView({block: 'center'});",
                        checkbox
                    )
                except Exception:
                    pass

                # Marcar y verificar: el click nativo a veces no registra (p. ej. si
                # el checkbox queda bajo otro elemento); se reintenta por JS.
                for intento in range(3):
                    try:
                        if not checkbox.is_selected():
                            if intento == 0:
                                checkbox.click()
                            else:
                                self.driver.execute_script(
                                    "arguments[0].click();", checkbox
                                )
                    except Exception:
                        self.driver.execute_script(
                            "arguments[0].click();", checkbox
                        )
                    time.sleep(0.5)
                    if checkbox.is_selected():
                        break
                else:
                    raise AssertionError(f"No se pudo marcar el checkbox: {locator}")

            take_step_screenshot(
                self.driver,
                "prestamo_personal_checks_contrato"
            )

    def click_enviar_sms(self) -> None:
        with allure.step("Click en botón Enviar SMS"):

            button = self.wait_until_clickable(
                self.BTN_ENVIAR_SMS,
                timeout=30
            )

            take_step_screenshot(
                self.driver,
                "prestamo_personal_enviar_sms"
            )

            self.safe_click(button)
    
    def ingresar_otp_legalario(self, otp: str) -> None:
        with allure.step(f"Ingresar OTP Legalario: {otp}"):

            if len(str(otp)) != 4:
                raise ValueError(
                    f"OTP Legalario inválido: {otp}"
                )

            # =========================
            # ESPERAR INPUT OTP #1
            # =========================
            otp_input_1 = WebDriverWait(self.driver, 60).until(
                EC.element_to_be_clickable(
                    self.INPUT_OTP_1
                )
            )

            # Espera pequeña para garantizar
            # que ya llegó el response del OTP
            time.sleep(3)

            otp_digits = list(str(otp))

            otp_input_1.clear()
            otp_input_1.send_keys(otp_digits[0])
            time.sleep(1)

            otp_input_2 = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    self.INPUT_OTP_2
                )
            )
            otp_input_2.clear()
            otp_input_2.send_keys(otp_digits[1])
            time.sleep(1)

            otp_input_3 = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    self.INPUT_OTP_3
                )
            )
            otp_input_3.clear()
            otp_input_3.send_keys(otp_digits[2])
            time.sleep(1)

            otp_input_4 = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    self.INPUT_OTP_4
                )
            )
            otp_input_4.clear()
            otp_input_4.send_keys(otp_digits[3])

            take_step_screenshot(
                self.driver,
                "legalario_otp_ingresado"
            )
        
    def click_estoy_de_acuerdo(self) -> None:
        with allure.step("Click en botón Estoy de acuerdo"):

            button = self.wait_until_clickable(
                self.BTN_ESTOY_DE_ACUERDO,
                timeout=120
            )

            take_step_screenshot(
                self.driver,
                "prestamo_personal_estoy_de_acuerdo"
            )

            self.safe_click(button)
    
    def dibujar_firma_legalario(self) -> None:
        with allure.step("Dibujar firma en canvas Legalario"):

            canvas = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located(
                    self.CANVAS_FIRMA_LEGALARIO
                )
            )

            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});",
                canvas
            )

            take_step_screenshot(
                self.driver,
                "legalario_canvas_antes_firma"
            )

            self.driver.execute_script(
                """
                const canvas = arguments[0];
                const rect = canvas.getBoundingClientRect();

                function firePointer(type, x, y) {
                    const event = new PointerEvent(type, {
                        bubbles: true,
                        cancelable: true,
                        pointerId: 1,
                        pointerType: 'mouse',
                        isPrimary: true,
                        clientX: rect.left + x,
                        clientY: rect.top + y,
                        pressure: type === 'pointerup' ? 0 : 0.5,
                        buttons: type === 'pointerup' ? 0 : 1
                    });
                    canvas.dispatchEvent(event);
                }

                const points = [
                    [120, 360],
                    [180, 300],
                    [250, 390],
                    [330, 280],
                    [430, 370],
                    [520, 310],
                    [620, 355],
                    [720, 300],
                    [820, 340],
                    [930, 315]
                ];

                firePointer('pointerdown', points[0][0], points[0][1]);

                for (let i = 1; i < points.length; i++) {
                    firePointer('pointermove', points[i][0], points[i][1]);
                }

                firePointer(
                    'pointerup',
                    points[points.length - 1][0],
                    points[points.length - 1][1]
                );

                canvas.dispatchEvent(new Event('change', { bubbles: true }));
                canvas.dispatchEvent(new Event('input', { bubbles: true }));
                """,
                canvas
            )

            take_step_screenshot(
                self.driver,
                "legalario_canvas_firma_dibujada"
            )

    def click_firmar_legalario(self) -> None:
        with allure.step("Click en botón Firmar Legalario"):

            button = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located(self.BTN_FIRMAR_LEGALARIO)
            )

            take_step_screenshot(
                self.driver,
                "legalario_click_firmar"
            )

            self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
            self.driver.execute_script("arguments[0].click();", button)

    def click_finalizar_venta(self) -> None:
        with allure.step("Click en botón Finalizar Venta"):

            button = WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located(self.BTN_FINALIZAR_VENTA)
            )

            take_step_screenshot(
                self.driver,
                "prestamo_personal_finalizar_venta"
            )

            self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
            self.driver.execute_script("arguments[0].click();", button)
    
    def click_aceptar(self) -> None:
        with allure.step("Click en botón Aceptar"):

            button = self.wait_until_clickable(
                self.BTN_ACEPTAR,
                timeout=30
            )

            take_step_screenshot(
                self.driver,
                "prestamo_personal_btn_aceptar"
            )

            self.safe_click(button)