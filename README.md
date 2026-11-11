# 🚀 InsumosGen - Automatización web con Python, Selenium y Allure

> **InsumosGen** automatiza el flujo de venta y ofertas del portal **Provident UAT**, ejecutándolo desde **Visual Studio Code** con **Python + Selenium + Pytest + Allure Reports** y capturas de pantalla en cada paso.

---

## ✨ ¿Qué incluye este proyecto?

- Estructura simple y ordenada.
- Prueba automatizada de login.
- Captura de pantalla en cada paso importante.
- Evidencia automática en el reporte de **Allure**.
- Configuración pensada para ejecutarse localmente.
- Guía paso a paso para personas técnicas y no técnicas.

---

## 🗂️ Estructura del proyecto

```bash
InsumosGen/
├── config/
│   └── settings.py
├── data/
│   ├── ine_frente.jpeg        # INE frontal (requerida)
│   ├── ine_tras.jpeg          # INE trasera (requerida)
│   ├── selfie.jpeg            # Selfie base para generar cámara fake (requerida)
│   ├── selfie.y4m             # Video generado para cámara fake (generado)
│   └── comprobante.jpeg       # Comprobante de domicilio (requerido)
├── pages/
│   ├── login_page.py
│   ├── legalario_page.py
│   └── prestamo_personal_page.py
├── services/
│   ├── image_encoder.py
│   ├── legalario_auth_resolver.py
│   ├── legalario_uploader.py
│   └── network_interceptor.py
├── tests/
│   └── test_login.py
├── utils/
│   ├── allure_utils.py
│   ├── birthdate_allocator.py
│   ├── generate_fake_camera_video.py
│   └── utils.py
├── conftest.py
├── pytest.ini
├── requirements.txt
├── run.py
└── README.md
```

---

## ✅ Flujo automatizado

La prueba cubre el ciclo completo de venta de préstamo personal en UAT:

1. Login con credenciales de Estrella.
2. Navegación a **Ventas → Cliente nuevo**.
3. Flujo **Legalario**: carga de INE frente/trasera y facematch con cámara fake.
4. Captura y envío de datos personales y laborales.
5. Intercepción y uso automático del **OTP Provident** (vía red).
6. Selección de plazo, monto y beneficiario.
7. Firma de contrato y captura del **OTP Legalario** (vía red).
8. Finalización de la venta.

---

## 🧰 Herramientas necesarias

Antes de ejecutar este proyecto necesitas instalar lo siguiente:

### 1) Instalar Python
Descarga Python desde su sitio oficial.
Durante la instalación marca la opción:

- `Add Python to PATH`

Para validar la instalación, abre una terminal y ejecuta:

```bash
python --version
```

---

### 2) Instalar Visual Studio Code
Descarga e instala **Visual Studio Code**.
Después instala la extensión oficial de **Python** dentro de VS Code.

---

### 3) Instalar Java (requerido para Allure)
Allure necesita Java para generar y abrir reportes.
Instala una versión LTS de Java y valida con:

```bash
java -version
```

---

### 4) Instalar Allure
Puedes instalar Allure de distintas formas. La más común es con un gestor de paquetes del sistema.
Una vez instalado, valida con:

```bash
allure --version
```

> Si Allure no abre, normalmente el problema es que **Java no está instalado** o no está configurado en el PATH.

---

## 📥 Descarga del proyecto

Guarda o copia esta carpeta en tu equipo, por ejemplo en:

```bash
C:\automatizacion\framework_provident
```

Luego ábrela en **Visual Studio Code**.

---

## ⚙️ Configuración del proyecto

### 1) Crear entorno virtual
Desde la terminal de VS Code, ubicándote en la carpeta del proyecto, ejecuta:

### Windows
```bash
python -m venv .venv
.venv\Scripts\activate
```

### Mac / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 2) Instalar dependencias
Con el entorno virtual activado ejecuta:

```bash
pip install -r requirements.txt
```

---

### 3) Preparar archivos en `data/`

Coloca los siguientes archivos dentro de la carpeta `data/` antes de ejecutar:

| Archivo | Descripción |
|---|---|
| `ine_frente.jpeg` | Foto frontal de la INE del cliente |
| `ine_tras.jpeg` | Foto trasera de la INE del cliente |
| `selfie.jpeg` | Selfie del cliente (base para generar la cámara fake) |
| `comprobante.jpeg` | Comprobante de domicilio |

Luego genera el video de cámara fake:

```bash
python utils/generate_fake_camera_video.py
```

Esto crea `data/selfie.y4m` automáticamente.

---

### 4) Configurar credenciales

El proyecto lee la configuración desde `data/run_config.json`.
La forma más sencilla es ejecutar el asistente de configuración:

```bash
python run.py
```

Esto abre una interfaz donde ingresas la Estrella, contraseña y demás parámetros,
y guarda `data/run_config.json` automáticamente antes de lanzar la prueba.

> Si prefieres editar manualmente, crea `data/run_config.json` con la siguiente estructura:

```json
{
  "focus_id": "tu_numero_estrella",
  "password": "tu_contrasena",
  "agencia_label": "Izcalli 335",
  "metodo_entrega": "BBVA",
  "ciclos": 1
}
```

#### Conexiones a bases de datos

Los flujos de oferta, cliente frecuente y agencias consultan SQL Server (`botDB`, `Challenger_uat`).
Captura esas conexiones desde la UI, con el botón 🔌 **Conexiones**: servidor, usuario, contraseña y
driver ODBC por host, con un botón **Probar** que indica la causa exacta si falla (VPN, usuario o
contraseña, driver, permisos). La contraseña se guarda cifrada en el Administrador de credenciales de
Windows y el resto en `data/connections.json` (ignorado por git). Si falta una conexión al iniciar una
ejecución, la UI abre el diálogo sola. Ya no se usa `.env`: si tienes uno, la app lo importa la primera
vez y te ofrece borrarlo.

---

## ▶️ Cómo ejecutar la prueba

### Opción A — Recomendada (con asistente de configuración)

```bash
python run.py
```

Abre la interfaz de selección, guarda `data/run_config.json` y lanza pytest automáticamente.

### Opción B — Directa (si ya existe `data/run_config.json`)

```bash
pytest --alluredir=allure-results
```

Esto hará lo siguiente:

- Abrirá el navegador Chrome.
- Ejecutará el flujo completo de venta de préstamo personal.
- Guardará capturas de pantalla por paso.
- Generará resultados para Allure.

---

## 📸 Evidencias

Las capturas se generan automáticamente en cada paso importante del flujo y se adjuntan al reporte de Allure:

- Login y navegación inicial.
- Cada paso del flujo Legalario (INE, facematch).
- Captura de datos personales y laborales.
- Intercepción de OTPs.
- Firma de contrato.
- Captura automática en caso de error.

---

## 📊 Cómo abrir el reporte de Allure

Después de ejecutar la prueba, lanza:

```bash
# Corridas lanzadas con run.py / la UI (en desarrollo; instalada: %LOCALAPPDATA%\InsumosGen\allure-results)
allure serve data/allure-results
# Corridas de pytest directo con --alluredir=allure-results
allure serve allure-results
```

Esto abrirá el reporte en el navegador.

Ahí podrás ver:

- Estado de la ejecución.
- Tiempo de prueba.
- Pasos ejecutados.
- Capturas adjuntas en cada paso.
- Error detallado si algo falla.

---

## 🧠 Recomendaciones importantes

### 1) Chrome debe estar instalado
Este proyecto usa **Google Chrome**.
El driver se descarga automáticamente con `webdriver-manager`.

### 2) Ambiente UAT
Si el sitio cambia de diseño, nombre de campos o botones, puede ser necesario ajustar los selectores del archivo:

```bash
pages/login_page.py
```

### 3) Certificados, VPN o acceso corporativo
Si la URL solo funciona dentro de red corporativa o mediante VPN, primero asegúrate de tener acceso manual desde el navegador.

---

## 🛠️ Posibles mejoras futuras

Este framework se puede extender fácilmente con:

- Page Object Model más robusto.
- Logs por ejecución.
- Evidencia en video.
- Ejecución en Edge o Firefox.
- Integración con Jenkins / Azure DevOps / GitHub Actions.
- Datos externos desde Excel o CSV.
- Fixtures reutilizables por ambiente.

---

## 📌 Notas técnicas

- Se usa `pytest` como motor de pruebas.
- Se usa `allure-pytest` para reportes.
- Se usa `webdriver-manager` para evitar descargar manualmente el ChromeDriver.
- Los selectores del login fueron diseñados de forma flexible para tolerar cambios menores del DOM.

---

## 🎯 Comando completo recomendado

```bash
pytest --alluredir=allure-results && allure serve allure-results
```

O desde el asistente de configuración:

```bash
python run.py
```

---

## 🙌 Resultado esperado

Al finalizar, tendrás:

- Una automatización funcional del ciclo completo de venta de préstamo personal.
- Evidencia visual por cada paso.
- Un reporte profesional en Allure.
- Una base lista para crecer hacia más escenarios.

---

## 👨‍💻 Sugerencia final

Si al ejecutar ves que un campo no es localizado correctamente, abre la página manualmente, inspecciona el elemento y ajusta el selector dentro de `pages/login_page.py`.

Eso es normal en proyectos UAT donde algunos identificadores pueden cambiar.
