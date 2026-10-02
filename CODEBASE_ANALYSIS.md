# Análisis del CodeBase: Providigital_Ventas

> **Fecha de análisis:** Mayo 2026  
> **Propósito:** Documentación técnica de referencia del framework de automatización de pruebas E2E para la plataforma Provident UAT.

---

## 1. Resumen General

Framework de automatización de pruebas end-to-end (E2E) construido sobre **Python + Selenium + Pytest + Allure Reports**. Automatiza el flujo completo de **registro de una venta de préstamo personal** en la plataforma `https://originacion-uat.providigital.com`, incluyendo verificación de identidad con el SDK de **Legalario** (facematch + OCR de INE), llenado de datos, firma electrónica y finalización de venta.

---

## 2. Stack Tecnológico

| Herramienta | Versión | Propósito |
|---|---|---|
| Python | 3.x | Lenguaje base |
| selenium | 4.33.0 | Automatización del navegador |
| pytest | 8.4.1 | Motor de pruebas |
| allure-pytest | 2.14.2 | Reportes enriquecidos con pasos y capturas |
| webdriver-manager | 4.0.2 | Gestión automática del ChromeDriver |
| python-dotenv | 1.1.1 | Variables de entorno desde `.env` |
| opencv-python | *(opcional)* | Generación de video fake para cámara |
| pillow + numpy | *(opcional)* | Procesamiento de imagen para video fake |

**Navegador:** Google Chrome (modo normal o headless). El driver se descarga automáticamente.

---

## 3. Estructura del Proyecto

```
Providigital_Ventas/
├── config/
│   └── settings.py               # Configuración centralizada (URL, credenciales, rutas de archivos)
├── pages/
│   ├── login_page.py             # POM: Login + navegación inicial hasta Legalario
│   ├── legalario_page.py         # POM: Interacción con el SDK de identidad Legalario
│   └── prestamo_personal_page.py # POM: Flujo completo de solicitud de préstamo personal
├── services/
│   ├── image_encoder.py          # Codificación de imágenes a base64 / data URL
│   ├── legalario_auth_resolver.py# Extrae Authorization header de requests capturadas
│   ├── legalario_uploader.py     # Re-envío de requests al API de Legalario vía JS fetch
│   └── network_interceptor.py    # Interceptor JS de fetch/XHR para mock de imágenes y captura de OTPs
├── tests/
│   └── test_login.py             # Caso de prueba principal E2E (único test file)
├── utils/
│   ├── allure_utils.py           # Captura de screenshots y adjunto a Allure
│   ├── birthdate_allocator.py    # Generador de fechas de nacimiento únicas (SQLite)
│   ├── generate_fake_camera_video.py # Genera selfie.y4m para cámara fake de Chrome
│   └── utils.py                  # Helpers genéricos (scroll, espera, save_base64_to_json)
├── data/                         # Archivos de datos requeridos en runtime (no incluidos en repo)
│   ├── ine_frente.jpeg
│   ├── ine_tras.jpeg
│   ├── selfie.jpeg
│   ├── selfie.y4m                # Generado con generate_fake_camera_video.py
│   └── comprobante.jpeg
├── screenshots/                  # Screenshots generados en cada ejecución (auto-creado)
├── conftest.py                   # Fixture del driver Chrome + hook de error screenshot
├── pytest.ini                    # Configuración de pytest (-s -v, convenciones de nombres)
├── requirements.txt              # Dependencias del proyecto
├── README.md                     # Guía de instalación y ejecución
└── README_FAKE_CAMERA.md         # Guía específica para la cámara fake de Legalario
```

---

## 4. Configuración (`config/settings.py`)

Todas las constantes están hardcodeadas en la clase `Settings`. **No usa `.env` en la práctica actual** (el README lo menciona como buena práctica, pero el código lee directamente de la clase).

| Parámetro | Valor | Descripción |
|---|---|---|
| `BASE_URL` | `https://originacion-uat.providigital.com/v1/app/login` | URL del sistema UAT |
| `ESTRELLA` | `2075000343335` | Usuario/número de estrella del asesor |
| `PASSWORD` | `Estrella1*` | Contraseña del asesor |
| `CELULAR` | `5513096751` | Teléfono celular del cliente de prueba |
| `USE_FAKE_CAMERA` | `True` | Activa cámara virtual para facematch desatendido |
| `HEADLESS` | `False` | Ejecuta Chrome visible (cambiar a `True` para CI) |
| `IMPLICIT_WAIT` | `10` segundos | Tiempo implícito global del driver |
| `LEGALARIO_ONBOARDING_ID` | `69e1305983beb98b360177f9` | ID de onboarding en Legalario |
| `LEGALARIO_ORGANIZATION_ID` | `6099a51598cfb21cf25ad42b` | ID de organización en Legalario |

> ⚠️ **Riesgo:** Credenciales y datos sensibles están en texto plano en el repositorio. Se recomienda migrar a variables de entorno o un vault de secretos.

---

## 5. Flujo de Prueba E2E (`tests/test_login.py`)

Un único caso de prueba: `TestLoginProvident::test_login_exitoso`. Cubre el flujo completo de venta en ~40 pasos de Allure.

### Fases del flujo

#### Fase 1 – Login y navegación inicial
1. Abrir URL de login
2. Ingresar estrella y contraseña
3. Click en "Ingresar"
4. Navegar: Ventas → Registrar Venta → Cliente nuevo → Registrar una venta
5. Iniciar proceso de identidad
6. Ingresar celular del cliente
7. Comenzar + aceptar aviso de privacidad
8. Confirmar modal de Legalario OK

#### Fase 2 – Verificación de identidad (SDK Legalario)
El interceptor de red se instala **antes** de las capturas para poder:
- Sustituir las imágenes reales por mocks locales (INE frente, INE trasera, selfie)
- Capturar los OTPs de las respuestas HTTP

| Paso | Endpoint Legalario interceptado | Archivo mock |
|---|---|---|
| INE Frontal | `sdk/onboarding/identify/front` | `data/ine_frente.jpeg` |
| INE Trasera | `sdk/onboarding/identify/reverse` | `data/ine_tras.jpeg` |
| Facematch | `sdk/onboarding/identify/facematch` | `data/selfie.jpeg` (+ `selfie.y4m` en cámara fake) |

Adicionalmente, después de la captura frontal se **modifica la fecha de nacimiento OCR** con una fecha única generada por `BirthdateAllocator` para evitar duplicados entre ejecuciones.

#### Fase 3 – Formulario de préstamo personal
- Subir comprobante de domicilio (`comprobante.jpeg`) x2 (domicilio + fachada)
- Confirmar dirección (selecciona la segunda opción del dropdown)
- Llenar datos personales (hardcodeados: teléfono, email, estado civil, dependientes, tipo vivienda, años/meses)
- Llenar datos laborales y financieros (tipo empleo, ocupación, antigüedad, ingresos, gastos, propósito, día de pago)
- Dirección diferente = "No"

#### Fase 4 – OTP Provident (SMS)
- Marcar checkbox de autorización y click en "Autorizo"
- El interceptor captura automáticamente la respuesta del endpoint `/v1/sendconfirmationsms`
- El OTP se extrae del campo `body.code` de la respuesta y se ingresa en el formulario

#### Fase 5 – Configuración del préstamo
- Seleccionar plazo (índice 1) y monto (índice 1 = $5,200 aprox)
- Orden de Pago BBVA → confirmar con "Sí"
- Llenar beneficiario: "Diego Alonso Sanchez", parentesco "Hijo/a"

#### Fase 6 – Contrato y firma electrónica (Legalario)
- Marcar 4 checkboxes de contrato (privacidad, confirmación, marketing, propietario)
- Enviar SMS Legalario → capturar OTP desde respuesta de `/sdk/invites/send-code` (campo `data.otp_code`)
- Ingresar OTP en 4 inputs individuales (`legalarioOtpInput1..4`)
- Aceptar contrato x2 con "Estoy de acuerdo"
- Dibujar firma en canvas mediante `PointerEvent` vía JavaScript (10 puntos predefinidos)
- Firmar x2 con `legalarioButtonNext`

#### Fase 7 – Finalizar venta
- Click en "Finalizar Venta"
- Click en "Aceptar" (confirmación final)

---

## 6. Page Object Model (POM)

### `LoginPage`
- Selectores XPath basados en `placeholder` y texto visible del botón para tolerancia a cambios del DOM.
- Métodos helper: `wait_until_visible()`, `wait_until_clickable()`, `scroll_to_bottom()`.
- Cubre también la navegación post-login y el inicio del flujo de Legalario.

### `LegalarioPage`
- Maneja los modales y botones del SDK embebido de Legalario.
- `click_continuar_legalario_ok()`: usa fallback a `execute_script` click para superar overlays del SDK.
- `cambiar_fecha_nacimiento_ocr()`: fuerza el valor del input readonly vía JS + dispatch de eventos `input/change/blur`.
- `prepare_mock_image()`: convierte imagen local a `data:image/jpeg;base64,...`.

### `PrestamoPersonalPage` (archivo más grande: ~987 líneas)
- Cubre toda la solicitud de préstamo personal.
- `safe_click()`: hace scroll al elemento antes del click, con fallback JS.
- Datos personales y laborales están **hardcodeados** dentro de los métodos (`llenar_datos_personales`, `llenar_datos_laborales_financieros`).
- `dibujar_firma_legalario()`: simula una firma en el canvas usando `PointerEvent` JavaScript con 10 coordenadas predefinidas.
- `ingresar_otp_legalario()`: valida que el OTP sea de 4 dígitos y llena cada input individualmente.

---

## 7. Servicios

### `NetworkInterceptor` (servicio más complejo: ~323 líneas)
Inyecta JavaScript en el navegador para interceptar `fetch` y `XMLHttpRequest` globalmente. Funcionalidades:
- **Mock de imágenes:** reemplaza el campo `image_content` (INE) o `selfie` (facematch) en el body de requests a Legalario por la imagen local configurada.
- **Captura de OTPs:** guarda en `window.__lastSmsOtpResponse` y `window.__lastLegalarioOtpResponse` las respuestas de los endpoints de código de confirmación.
- **Log de requests:** almacena todas las requests en `window.__capturedRequests` (URL, método, headers, body).
- Métodos Python: `get_last_sms_otp_code()` (ruta: `body.code`), `get_last_legalario_otp_code()` (ruta: `data.otp_code`).

### `ImageEncoder`
- `image_to_base64(path)` → string base64
- `image_to_data_url(path, mime)` → `data:image/jpeg;base64,...`

### `LegalarioAuthResolver`
- Extrae el header `Authorization` de las requests capturadas por el interceptor.
- Localiza la request al endpoint `sdk/onboarding/identify/front` para reutilizar su payload.

### `LegalarioUploader`
- Re-envía una request al API de Legalario usando el payload real capturado pero con imagen local sustituida.
- Usa `execute_async_script` para hacer `fetch` POST desde el contexto del navegador.
- **Nota:** Este servicio no se usa directamente en el test actual (infraestructura disponible para uso futuro).

---

## 8. Utilidades

### `allure_utils.py`
- `take_step_screenshot(driver, step_name, folder)`: guarda screenshot con timestamp y lo adjunta al reporte Allure.
- `ensure_dir(path)`: crea el directorio si no existe.

### `BirthdateAllocator`
- Genera fechas de nacimiento únicas para cada ejecución usando una base de datos **SQLite** local (`data/generated_birthdates.sqlite3`).
- Rango: desde `02/07/1995` con incremento diario, hasta 5000 fechas disponibles.
- Usa transacción `EXCLUSIVE` para soportar ejecuciones paralelas sin duplicados.
- Formato de salida: `dd/mm/yyyy`.

### `generate_fake_camera_video.py`
- Script standalone (no se ejecuta en el test, debe correrse manualmente previamente).
- Genera `data/selfie.y4m` (10 segundos, 30fps, 640x480) a partir de `data/selfie.jpeg`.
- Simula zoom progresivo: estable 0-5s → zoom suave 5-8s → zoom fuerte 8-10s para disparar el trigger de "acércate" del SDK de facematch.
- Requiere `opencv-python`, `pillow`, `numpy` (dependencias opcionales no incluidas en `requirements.txt`).

### `utils.py`
- Contiene versiones standalone (no de clase) de `wait_until_visible` y `scroll_to_bottom`.
- `save_base64_to_json(base64_str, file_path)`: guarda base64 en JSON para debugging.
- ⚠️ **Nota:** `scroll_to_bottom` en este archivo referencia `time.sleep` pero no importa `time`. Bug latente.

---

## 9. Fixture del Driver (`conftest.py`)

El fixture `driver` tiene scope de función y configura Chrome con:
- Maximizado, sin notificaciones, sin infobars
- Permisos automáticos de cámara, micrófono y geolocalización
- `--use-fake-ui-for-media-stream`: auto-acepta popup de permisos
- Si `USE_FAKE_CAMERA=True`: activa `--use-fake-device-for-media-stream` y apunta a `selfie.y4m`
- Si `HEADLESS=True`: activa `--headless=new` con flags adicionales para compatibilidad con cámara fake en CI
- Hook `pytest_runtest_makereport`: captura screenshot automático si un test falla

---

## 10. Ejecución

### Prerrequisitos
1. Python 3.x instalado con `Add Python to PATH`
2. Java JDK instalado (requerido por Allure)
3. Allure CLI instalado
4. Google Chrome instalado
5. Archivos de datos en `data/`:
   - `ine_frente.jpeg`, `ine_tras.jpeg`, `selfie.jpeg`, `comprobante.jpeg`
   - `selfie.y4m` (generado con `python utils/generate_fake_camera_video.py`)

### Instalación
```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
# Opcional, solo para generar selfie.y4m:
pip install opencv-python pillow numpy
```

### Comandos principales
```bash
# Ejecutar prueba con resultados Allure
pytest --alluredir=allure-results

# Ver reporte en navegador
allure serve allure-results

# Ejecutar y abrir reporte en un comando
pytest --alluredir=allure-results && allure serve allure-results
```

---

## 11. Hallazgos y Observaciones Técnicas

### ✅ Fortalezas
- **Interceptor de red avanzado:** La estrategia de monkey-patching de `fetch`/XHR en el navegador permite capturar OTPs directamente de las respuestas del servidor, eliminando la necesidad de acceso a SMS o base de datos.
- **Mock de imágenes transparente:** El reemplazo de imágenes en el body de requests Legalario es transparente para el SDK, permitiendo pruebas desatendidas de verificación de identidad.
- **`BirthdateAllocator`:** Solución elegante para evitar duplicados de clientes entre ejecuciones, con soporte para paralelismo mediante SQLite EXCLUSIVE transaction.
- **Cámara fake con zoom dinámico:** El video `.y4m` simula el comportamiento esperado por el SDK de facematch (acercamiento progresivo).
- **Allure totalmente integrado:** Cada acción genera un paso nombrado + screenshot adjunto en el reporte.

### ⚠️ Áreas de mejora / Riesgos
- **Credenciales hardcodeadas:** `Settings.py` expone estrella, contraseña, celular e IDs de Legalario en texto plano en el repo. Migrar a `.env` o variables de CI.
- **Datos de prueba hardcodeados en POM:** Teléfono, email, nombre del beneficiario, montos y opciones de selects están fijos en `PrestamoPersonalPage`. Dificultad para parametrizar escenarios.
- **Un único test case:** Todo el flujo es un único método monolítico de ~374 líneas. Si falla a mitad del flujo, no hay granularidad de reporte ni posibilidad de reanudar.
- **`time.sleep()` extensivo:** Hay 15+ llamadas a `time.sleep()` con valores fijos (hasta 30s en `click_tomar_foto`). Aumenta el tiempo de ejecución y es frágil ante variaciones de red.
- **Bug en `utils.py`:** `scroll_to_bottom` usa `time.sleep` sin importar `time`. Fallaría si se llamara.
- **`utils.py` duplica lógica de Page Objects:** `wait_until_visible` y `scroll_to_bottom` existen en `LoginPage` y en `utils.py` con implementaciones casi idénticas.
- **`LegalarioUploader` no usado en el test:** Infraestructura construida pero no integrada en el flujo actual.
- **`data/` no está en el repo:** Los archivos de imágenes deben proveerse manualmente. No hay documentación de qué requisitos deben cumplir las imágenes para que Legalario las acepte.
- **Sin fixtures parametrizables por ambiente:** No hay soporte para múltiples ambientes (UAT, staging, producción) sin modificar el código.

---

## 12. Posibles Extensiones (según README)

- Page Object Model más robusto con herencia de `BasePage`
- Datos externos desde Excel o CSV (parameterización)
- Evidencia en video con herramientas como `pytest-video`
- Ejecución en Edge o Firefox
- Integración con Jenkins / Azure DevOps / GitHub Actions
- Fixtures reutilizables por ambiente (`.env.uat`, `.env.staging`)
- Logs por ejecución con `logging`
- Múltiples casos de prueba: login fallido, cliente existente, distintos montos/plazos

---

## 13. Diagrama de Dependencias de Módulos

```
tests/test_login.py
    ├── config/settings.py
    ├── pages/login_page.py
    │       └── utils/allure_utils.py
    ├── pages/legalario_page.py
    │       ├── services/image_encoder.py
    │       └── utils/allure_utils.py
    ├── pages/prestamo_personal_page.py
    │       └── utils/allure_utils.py
    ├── services/network_interceptor.py
    └── utils/birthdate_allocator.py

conftest.py
    ├── config/settings.py
    └── utils/allure_utils.py
```

---

*Documento generado automáticamente mediante análisis estático del codebase. Última actualización: Mayo 2026.*
