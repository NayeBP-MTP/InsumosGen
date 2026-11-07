# Especificaciones del flujo E2E automatizado — Providigital Ventas

**Fecha de validación CN:** 22/09/2026  
**Fecha de validación CF:** 23/09/2026  
**Estado:** ✅ Funcionando (~318s por ciclo)  
**Stack:** Python 3.13 + Selenium 4.33 + Pytest 8.4 + Allure + ChromeDriver + Tkinter (UI)

> **Alcance de este documento:** flujos, pantallas y cómo se conforman los componentes.
> Las **reglas de negocio y la teoría** (tipos de cliente, columnas de la oferta, reglas por
> agencia, métodos de entrega, datos de prueba) están en
> [config/Context/REGLAS_DE_NEGOCIO.md](config/Context/REGLAS_DE_NEGOCIO.md).

---

## Descripción general

Automatización E2E del proceso completo de venta de préstamo personal en el portal UAT de Providigital. El test cubre desde el login del asesor hasta el cierre de sesión, pasando por verificación de identidad con Legalario SDK, captura de datos, firma de contrato y finalización de venta. Existen dos flujos: **Cliente Nuevo (CN)** y **Cliente Frecuente (CF)**, que pueden combinarse en una misma corrida desde el menú de inicio.

---

## Estructura del proyecto

```
Providigital_Ventas/
├── config/
│   ├── settings.py             # Credenciales, URLs, rutas de imágenes, selección de la UI (lee data/run_config.json)
│   └── Context/
│       ├── REGLAS_DE_NEGOCIO.md   # Reglas de negocio y contexto teórico
│       └── offers.sql             # Plantilla SQL de una oferta (referencia)
├── pages/
│   ├── login_page.py           # LoginPage (POM)
│   ├── legalario_page.py       # LegalarioPage (POM)
│   ├── prestamo_personal_page.py  # PrestamoPersonalPage (POM)
│   └── ofertas_listado_page.py # OfertasListadoPage (POM, listado de ofertas CF)
├── services/
│   ├── network_interceptor.py  # Intercepción fetch/XHR, mock de imágenes, captura de OTPs y facematch
│   ├── image_encoder.py        # Conversión imagen → base64 / data URI
│   ├── legalario_uploader.py   # Subida de documentos a Legalario
│   ├── legalario_auth_resolver.py
│   └── offer_repository.py     # Acceso a botDB.dbo.Ofertas (OfferData / OfferRepository)
├── ui/
│   ├── selector_ui.py          # Menú de inicio (agencia, método, ventas CF/CN, ajustes, historial)
│   ├── results_ui.py           # Pantalla de resultado de la ejecución (reintentar pendientes)
│   └── history_ui.py           # Ventana de historial de intentos
├── utils/
│   ├── allure_utils.py         # Screenshots en pasos Allure
│   ├── birthdate_allocator.py  # SQLite para asignar fechas de nacimiento únicas por ciclo
│   ├── offer_id_allocator.py   # SQLite para idOferta / Customer_Id / Agreement_Num / semana únicos
│   ├── mexican_names.py        # Generador de nombres y RFC realistas (ficticios) para ofertas CF
│   ├── catalog_db.py           # Catálogo local de agencias y métodos de entrega
│   ├── run_history.py          # Historial persistente de intentos (data/historial_ventas.json)
│   ├── generate_fake_camera_video.py  # Genera video .y4m para cámara fake (facematch)
│   └── utils.py
├── data/
│   ├── selfie.y4m              # Video de cámara fake para el SDK de Legalario
│   ├── run_config.json         # Selección hecha en el menú (la escribe la UI / run.py)
│   ├── run_results.json        # Resultados de la fase CN
│   ├── run_results_cf.json     # Resultados de la fase CF
│   ├── historial_ventas.json   # Historial de todos los intentos
│   └── diagnostico_cf/         # Captura de la falla de un ciclo CF
├── tests/
│   ├── test_login.py           # Test CN (envoltorio)
│   ├── test_login_cf.py        # Test CF (envoltorio)
│   └── test_oferta.py          # Test OF (solo inserta la oferta)
├── flows/
│   ├── venta_comun.py          # Tramos compartidos CN/CF (flujo_*)
│   ├── venta_cn.py             # Flujo de venta CN
│   ├── venta_cf.py             # Flujo de venta CF
│   └── oferta_cf.py            # Construcción/inserción de la oferta
└── run.py                      # Entry point: menú → fases CF/CN → pantalla de resultados
```

---

## Configuración inicial (`config/settings.py`)

`Settings` lee `data/run_config.json` al importarse; por eso cada fase de `run.py` corre en un
subproceso pytest propio.

| Parámetro | Descripción |
|---|---|
| `BASE_URL` | URL del portal UAT de Providigital |
| `ESTRELLA` | Usuario del asesor (`focus_id` de la agencia elegida) |
| `PASSWORD` | Contraseña del asesor |
| `CELULAR` / `CORREO` | Celular y correo del cliente de prueba (Ajustes del menú) |
| `TIPO_CLIENTE` | `CN` / `CF` — lo fija `run.py` en cada fase |
| `AGENCIA_LABEL` | Nombre de la agencia elegida en el menú |
| `METODO_ENTREGA` | `BBVA` / `HSBC` / `FINABIEN` / `EFECTIVO` / `CHEQUE` |
| `CICLOS` | Número de ventas de la fase — lo fija `run.py` |
| `MONTO_OFERTA` | Monto opcional de la oferta CF (`monto` en `run_config.json`); si no, aleatorio |
| `MONTO_MAXIMO_CF_POR_AGENCIA` | Tope exclusivo de monto CF por agencia (regla en el documento de contexto) |
| `UBICACION_OFICINA_POSTAL_POR_AGENCIA` | (estado, ciudad) para buscar la oficina postal de Finabien |
| `LEGALARIO_ONBOARDING_ID` | ID del onboarding en Legalario sandbox |
| `LEGALARIO_FRONT_IMAGE_PATH` | Ruta a imagen mock de INE frontal |
| `LEGALARIO_BACK_IMAGE_PATH` | Ruta a imagen mock de INE trasera |
| `LEGALARIO_SELFIE_IMAGE_PATH` | Ruta a imagen mock de selfie |
| `COMPROBANTE_DOMICILIO_PATH` | Ruta a imagen mock de comprobante de domicilio |

---

## Flujo completo paso a paso (Cliente Nuevo — CN)

### 1. Login y flujo inicial
1. Abrir `BASE_URL`
2. Ingresar estrella y contraseña → click Login
3. Click **Ventas** → **Registrar Venta** → **Cliente nuevo** → **Registrar una venta**
4. Click **Iniciar proceso de identidad**
5. Ingresar celular → **Comenzar**
6. Marcar check de privacidad → **Continuar**
7. Click **Continuar Legalario OK** (primer modal de instrucciones)

### 2. Interceptor de red
- Se instala `NetworkInterceptor` que sobreescribe `fetch` y `XMLHttpRequest` globalmente
- Permite: mock de `image_content` en requests de Legalario, captura de OTPs en responses, captura de tokens de autenticación

### 3. INE Frontal (Legalario SDK)
1. Preparar imagen mock frontal como data URI (`data:image/jpeg;base64,...`)
2. Configurar interceptor para reemplazar `image_content` con la imagen mock
3. Click **Tomar Foto** → el SDK captura y envía a `sdk/onboarding/identify/front`
4. Esperar 5s y validar que se capturó al menos 1 request a Legalario
5. Asignar fecha de nacimiento única (SQLite BirthdateAllocator) → cambiar en el OCR del SDK
6. Click **Continuar** (dos veces para avanzar a la pantalla de trasera)

### 4. INE Trasera (Legalario SDK)
1. Limpiar requests anteriores
2. Preparar imagen mock trasera → configurar interceptor
3. Click **Tomar Foto** → SDK envía a `sdk/onboarding/identify/reverse`
4. Esperar 5s y validar requests
5. Guardar token de autenticación Legalario (Authorization header) para uso en fallback
6. Click **Continuar** hacia facematch

### 5. Facematch (Legalario SDK + fallback)
1. Limpiar requests → preparar imagen mock selfie → configurar interceptor
2. El video `data/selfie.y4m` se usa como cámara fake en Chrome (`--use-file-for-fake-video-capture`)
3. Esperar hasta 60s que el SDK complete facematch automáticamente (detectado en `sdk/onboarding/identify/facematch`)
4. **Si el SDK no completa en 60s** → fallback forzado:
   - Enviar POST a `{base_url}/sdk/onboarding/identify/facematch` con:
     - `onboarding_id`: desde `Settings.LEGALARIO_ONBOARDING_ID`
     - `front`: data URI completo de la imagen de INE frontal
     - `selfie`: base64 limpio de la selfie
     - `happy`: data URI de la selfie
     - `blink`: data URI de la selfie
     - `video`: `data:video/mp4;base64,{base64_selfie}`
   - Authorization: Bearer token capturado de requests anteriores
5. Esperar 15s post-facematch → click **Continuar** (intentando `legalarioModalButtonOk` o JS click)
6. Click **Continuar** adicional para salir del SDK

> **Nota:** El fallback puede retornar HTTP 400 (AWS Rekognition InvalidParameterException por imagen sintética), pero el flujo continúa porque el SDK permite avanzar igualmente vía el botón Firmar con JS click.

### 6. Préstamo Personal — documentos
1. Click **Continuar** en pantalla de préstamo personal
2. Subir comprobante de domicilio (archivo imagen desde `COMPROBANTE_DOMICILIO_PATH`)
3. Click **Subir comprobante** → **Continuar modal**
4. Subir fachada de domicilio (mismo archivo)
5. Click **Subir fotografía** → **Continuar modal**
6. Click **Acepto** (confirmación de documentos)
7. Esperar página `Confirmar dirección` → click **Confirmar dirección**

### 7. Datos personales y laborales
1. **Seleccionar dirección actual** (segunda opción de la lista)
2. **Llenar datos personales** (hardcodeados en `PrestamoPersonalPage`)
3. Click **Continuar**
4. **Llenar datos laborales y financieros** (hardcodeados)
5. Click **Continuar**
6. **Seleccionar dirección diferente** → Click **Continuar**

### 8. OTP Provident
1. Click checkbox de autorización
2. Click **Autorizo** → el sistema envía SMS
3. El interceptor captura el OTP desde el response de `/v1/sendconfirmationsms` (campo `body.code`)
4. Ingresar OTP en los campos → Click **Continuar**
5. Esperar 10s para que cargue la pantalla de monto

### 9. Plazo, monto y método de entrega
1. **Seleccionar plazo y monto** (según configuración en POM)
2. Click **Continuar préstamo**
3. Esperar 3s → detectar pantalla opcional `/singleoffer`:
   - Si aparece: scroll al fondo → click **No aceptar oferta** → esperar salida
   - Fallback: click **Continuar** si "No aceptar" no funciona
4. **Seleccionar método de entrega** según `Settings.METODO_ENTREGA`:
   - `BBVA` / `HSBC` / `EFECTIVO` / `CHEQUE`: click directo en el botón correspondiente
   - `FINABIEN`: click en botón Finabien → modal adicional (ver sección siguiente)
5. Click **Sí** en modal de confirmación del método

#### Modal de Oficina Postal (solo FINABIEN)
El modal tiene 3 `<select>` dependientes entre sí (Angular):

```
Estado → Ciudad → Oficina Postal → [Confirmar Oficina Postal]
```

**Técnica de selección para Angular:**
```javascript
// Se usa native setter para que Angular detecte el cambio
var nativeSetter = Object.getOwnPropertyDescriptor(
    window.HTMLSelectElement.prototype, 'value'
).set;
nativeSetter.call(selectElement, value);
selectElement.dispatchEvent(new Event('input',  {bubbles: true}));
selectElement.dispatchEvent(new Event('change', {bubbles: true}));
```

Pasos:
1. Esperar modal → seleccionar **Estado** (por defecto Puebla; según agencia, ver `Settings.UBICACION_OFICINA_POSTAL_POR_AGENCIA`; búsqueda por texto, fallback a primera opción)
2. Esperar que Ciudad cargue opciones → seleccionar **Ciudad** (por defecto PUEBLA, o primera disponible)
3. Esperar que Oficina Postal cargue → seleccionar **primera opción disponible**
4. Click **Confirmar Oficina Postal**
5. Modal de confirmación final → click **Confirmar** (verde)

### 10. Beneficiario
1. Llenar datos de beneficiario (hardcodeados en POM)
2. Click **Continuar**

### 11. Contrato y firma Legalario
1. Marcar checks del contrato
2. Click **Continuar**
3. Click **Enviar SMS** → el SDK usa `/sdk/invites/send-code-new` (sin código en la respuesta); el
   código se pide a `/sdk/invites/send-code` (campo `data.otp_code`) con
   `NetworkInterceptor.solicitar_otp_legalario()`. Ver `Context.md` sección 10.
4. Esperar inputs OTP → ingresar OTP de 4 dígitos
5. Click **Estoy de acuerdo** (dos veces, para dos documentos)
6. **Dibujar firma** en canvas vía JavaScript (simulación de trazo)
7. Click **Firmar** (JS click ignorando estado `disabled`)
8. Esperar 5s → click **Firmar** de nuevo (confirmación)
9. Modal "firma completada" → click **Continuar**

### 12. Finalizar venta
1. Click **Finalizar venta**
2. Esperar 5s → Click **Aceptar**
3. Esperar 10s → **Cerrar sesión**

---

## Mecanismos técnicos clave

### Interceptor de red
```python
interceptor.install_network_interceptor()
interceptor.set_mock_image_content(data_url)   # reemplaza image_content en requests
interceptor.get_last_sms_otp_code()            # OTP de Provident SMS
interceptor.get_last_legalario_otp_code()      # OTP de Legalario
interceptor.get_legalario_requests_by_endpoint("sdk/onboarding/identify/facematch")
```

### Cámara fake para Legalario SDK
- Chrome se lanza con `--use-file-for-fake-video-capture=data/selfie.y4m`
- El `.y4m` es un video YUV4MPEG2 con fases de zoom (1.0x → 2.5x) para simular liveness
- Generado por `utils/generate_fake_camera_video.py`

### Fechas de nacimiento únicas
- `BirthdateAllocator` usa SQLite para garantizar que cada ciclo use una fecha distinta
- Evita el error "cliente ya registrado" en runs consecutivos

### Resultados
- CN: `data/run_results.json`; CF: `data/run_results_cf.json`. Ambos con detalle por ciclo (exitoso/fallido/error). En CF cada ciclo exitoso incluye `idOferta`, `nombreCliente` y `folio`.
- `data/historial_ventas.json` acumula todos los intentos (ver "Menú de inicio y ejecución combinada").

---

## Ejecución

```bash
python run.py
```

### Menú de inicio y ejecución combinada

`run.py` abre el menú (`ui/selector_ui.py`) donde se elige:

- **¿Qué deseas realizar?** (desplegable): **Oferta** (solo inserción en `botDB`, sin abrir navegador) o **Venta (CN / CF)**. Cada opción muestra su propio panel.
  - Panel **Oferta**: agencia, cantidad de ofertas y **Tipo de oferta** (`Agregar` / `Refin`, `Settings.TIPO_OFERTA`) — controla tanto la palabra que lleva `descOferta` como el valor de `tipoDeOferta` (`AD` / `RE`; ver [documento de contexto](config/Context/REGLAS_DE_NEGOCIO.md#2-la-oferta-botdbdboofertas)). No hay control de seguro en este panel: no aplica, la Oferta solo inserta en BD y no abre el navegador.
  - Panel **Venta**: agencia, método de entrega, ¿con seguro?, celular/correo y **Ventas a realizar por tipo** — un contador para **Cliente frecuente (CF)** y otro para **Cliente nuevo (CN)** (0–50 cada uno, mínimo 1 venta en total). Ej.: CF=2 y CN=1.
- **⚙ Ajustes:** celular y correo por defecto del cliente de prueba (se guardan en `data/user_settings.json`)
- **📋 Historial:** abre la lista de todos los intentos registrados

> Nota: esta sección no cubre todos los controles del menú actual (p. ej. la verificación de VPN antes de confirmar). Se documenta aquí solo lo relevante al flujo de oferta/venta.

Al confirmar se guarda `data/run_config.json` con `ventas: {"CF": n, "CN": m}` y el resto de la selección.

**Ejecución por fases** (`run.py`):

```
[Menú] → run_config.json
   ↓
Ronda N:
   1. Borra de botDB las ofertas CF de intentos fallidos anteriores
   2. Fase CF (si hay pendientes) → pytest tests/test_login_cf.py   (run_config con tipo_cliente=CF, ciclos=pendientes CF)
   3. Fase CN (si hay pendientes) → pytest tests/test_login.py      (run_config con tipo_cliente=CN, ciclos=pendientes CN)
   4. Lee run_results*.json, actualiza el estado de cada venta y registra cada intento en data/historial_ventas.json
   5. Restaura run_config.json con la selección original
   ↓
[Pantalla de resultado]  →  Reintentar pendientes → nueva ronda (solo lo que falta)
                            Nueva configuración   → vuelve al menú
                            Historial             → ventana de historial
                            Cerrar                → sale (código 0 si todo pasó, 1 si no)
```

- El orden es siempre **CF primero, luego CN**.
- Cada fase corre en su propio pytest (y su propio Chrome, con login nuevo).
- Antes de cada fase se elimina el archivo de resultados anterior para no leer datos viejos.
- Los ids de ofertas huérfanas se detectan comparando los `idOferta` que registró `offer_id_allocator` antes/después de la fase CF, menos los de ventas exitosas.

**Pantalla de resultado** (`ui/results_ui.py`): una fila por venta pedida con tipo, número, estado (✔ Exitosa / ✖ Pendiente), intentos y último resultado (nombre + folio si pasó; primera línea del error si falló).

**Historial** (`ui/history_ui.py` + `utils/run_history.py`): cada intento se guarda con fecha, agencia, método, tipo, ronda, estado y resultado; se muestra del más reciente al más antiguo, con totales de exitosos/fallidos. Persiste entre ejecuciones.

Para correr una fase sin menú:

```bash
python -m pytest tests/test_login_cf.py --alluredir=allure-results -s -v
python -m pytest tests/test_login.py    --alluredir=allure-results -s -v
```

(usan lo que haya en `data/run_config.json`).

### Flags de Chrome relevantes
```
--use-fake-device-for-media-stream
--use-file-for-fake-video-capture=data/selfie.y4m
--allow-file-access-from-files
--disable-web-security
```

---

## Problemas conocidos y soluciones

| Problema | Solución |
|---|---|
| Angular no detecta cambio en `<select>` con Selenium `Select` | Usar native setter JS + `dispatchEvent('input')` + `dispatchEvent('change')` |
| Botón **Firmar** disabled por facematch incompleto | JS click con `presence_of_element_located` (ignora disabled) |
| Facematch fallback requiere campo `front` | Pasar `front_data_url=mock_image_data_url_1` (data URI de INE frontal) |
| ChromeDriver crash con `GetHandleVerifier` sin mensaje | Era stale element en `(//select)[N]` — resuelto con `find_elements` fresco antes de cada operación |
| Pantalla singleoffer opcional | Detectar por URL, click "No aceptar oferta", esperar cambio de URL |
| OTP Legalario en formato de 4 dígitos | Pedirlo a `/sdk/invites/send-code` (`data.otp_code`, entero → `zfill(4)`); el SDK ahora usa `send-code-new`, que no lo devuelve |
| Modal "firma completada" bloquea avance | Detectar botón "Continuar" con timeout 15s y JS click |
| Tras un ciclo fallido la sesión queda abierta y el siguiente ciclo falla en el login | `LoginPage.recuperar_sesion_tras_fallo()` (ver "Recuperación entre ciclos") |
| El botón del método de entrega no existe en `paymenttypepage` (p. ej. Finabien) | El ciclo falla tras 30s de espera; la recuperación abre el menú hamburguesa y "Salir". No es un bug del código: ver observación en el documento de contexto |

---

## Flujo Cliente Frecuente (CF)

**Estado:** ✅ Implementado y validado en UAT (23/09/2026). Este flujo se diseñó a partir de las
reglas de negocio del documento de contexto (ver [§1 y §2](config/Context/REGLAS_DE_NEGOCIO.md)).

### Visión general

```
[Insertar oferta en botDB.dbo.Ofertas]
        ↓
[Login asesor] → [Ventas] → [Registrar Venta]
        ↓
[Pantalla "Selecciona el tipo de cliente"] → click en botón "Cliente frecuente"
        ↓
[Pantalla offerpage (listado de ofertas)] → escribir nombre en "Buscar" → click en tarjeta/botón de estatus
        ↓
[Misma pantalla offerpage, ahora en modo "confirmar oferta" — plazo y monto ya definidos por la oferta]
        ↓
[... identidad, documentos, datos, firma, finalizar venta (ver flujo real abajo) ...]
```

### Paso 0: Inserción automatizada de la oferta

Paso previo de preparación de datos: el test se conecta directamente a SQL Server (`botDB`) e
inserta el registro en `dbo.Ofertas` **antes de abrir el navegador** (se ejecuta dentro de
`ejecutar_venta_cf`).

#### Conexión a base de datos
- Dependencia: `pyodbc`. Credenciales y cadena de conexión **vía variables de entorno** (no hardcodear ni commitear):
  - `PESOS_OFFER_SERVER`
  - `PESOS_OFFER_USER`
  - `PESOS_OFFER_PASSWORD`
  - Opcional: `PESOS_OFFER_DRIVER` (default `ODBC Driver 17 for SQL Server`)
  - Las variables llevan el nombre del **host** (Pesos_Offer, que aloja `botDB` y `Originacion`),
    no el de la base; la base (`botDB`) y su host se mapean en `config/databases.py`.
- Se cargan con `python-dotenv` desde `.env` (ignorado por git; plantilla en `.env.example`).
- Módulo: `services/offer_repository.py` (sobre `services/db.py`, clase base común de conexión).

#### Construcción de la oferta
`construir_oferta_cf(numero_ciclo)` en `flows/oferta_cf.py`:
1. Resuelve la agencia configurada (`Settings.AGENCIA_LABEL`) contra `utils/catalog_db.py`: `agenciaCliente` = código de 13 dígitos, `branchOferta` = sus primeros 4.
2. `OfferIdAllocator.get_unique_ids(branch)` → `idOferta`, `Customer_Id`, `Agreement_Num`, `semana`.
3. `BirthdateAllocator.get_unique_birthdate()` → `FechaNacimiento` (se convierte a formato SQL).
4. `monto_para_agencia()` → monto (de `run_config.json` o aleatorio; valida el tope por agencia).
5. `MexicanNames.generar()` / `MexicanNames.rfc()` → nombre completo y RFC.
6. `descOferta = "TARIFA MÁX {monto} AGREGAR {plazo1}/{tasa1} A"` con plazo/tasa fijos (`14000/65`).
7. Devuelve un `OfferData` con los valores fijos por defecto (`Customer_Status_Code='CC'`, `Agreement_Status_Code='AC'`, `idEstatusOferta=1`, etc.). Las reglas de cada columna están en el documento de contexto.

#### Ejecución del insert
1. El nombre de cliente generado se usa directamente para **buscar la tarjeta en el front** (el test lo conserva en `oferta.nombreCliente`).
2. Si el insert falla (conexión, constraint, etc.), el ciclo falla antes de abrir el navegador — no tiene sentido correr Selenium sin una oferta visible.

### Paso 1: Selección del cliente en el listado

1. Login del asesor (igual que CN).
2. Click **Ventas** → click **Registrar Venta**.
3. En la pantalla **"Selecciona el tipo de cliente"** → click en **"Cliente frecuente"** (`BTN_CLIENTE_FRECUENTE`, hermano de `BTN_CLIENTE_NUEVO`, método `click_cliente_frecuente()` en `pages/login_page.py`).
4. En la pantalla de listado de ofertas (`offerpage` en modo listado):
   - Escribir el `nombreCliente` en el input **Buscar**.
   - Esperar a que el listado filtre y localizar la tarjeta correspondiente.
   - Click en el botón de estatus de la tarjeta (ej. **"Sin estatus"**) para iniciar la venta sobre ese cliente.

### Paso 2 en adelante: flujo CF real (validado en UAT, 23/09/2026)

Flujo confirmado punta a punta:

```
[Listado offerpage] → buscar nombre → click "Sin estatus"
   ↓
[Confirmar oferta: plazo y monto]        (confirmar_oferta_cf)
   ↓
[Método de entrega] → botón según Settings.METODO_ENTREGA → "Sí"
   ↓
[Iniciar Proceso de Identidad] → celular → INE frente/reverso → facematch (Legalario)
   ↓
[Documentos] comprobante + fachada → "Acepto"
   ↓
[Consentimiento de geolocalización]  (locationpage: "No Acepto"/"Acepto")  ← solo CF
   ↓
[Confirmar dirección] → datos personales → datos laborales → dirección diferente
   ↓                          (SIN OTP Provident en CF)
[Consentimientos legales: beneficiario] → checks de contrato
   ↓
[Enviar SMS] → OTP Legalario → "Estoy de acuerdo" x2 → firma → modal "firma completada"
   ↓
[Finalizar Venta]  → el portal se queda en la misma pantalla (contador de contrato de 2 min)
   ↓                  (SIN modal "Aceptar" en CF)
[Cerrar sesión]
```

Las diferencias entre CF y CN (tabla comparativa) están en el
[documento de contexto](config/Context/REGLAS_DE_NEGOCIO.md#1-tipos-de-cliente).

**Validación de finalización en CF:** el test valida la request `postlegalario` (`FinProceso`) y guarda el folio en `data/run_results_cf.json` (campo `folio`).

El código reutiliza funciones compartidas de `tests/test_login.py`: `_flujo_metodo_entrega`, `_flujo_identidad_a_otp` (con `incluir_otp_provident=False` en CF) y `_flujo_beneficiario_a_finalizar`.

### Trabajo pendiente para CF

- [x] Confirmar label exacto de los botones "Cliente nuevo" / "Cliente frecuente" en la pantalla "Selecciona el tipo de cliente".
- [x] Implementar `services/offer_repository.py` (conexión pyodbc + insert parametrizado).
- [x] Implementar generación de `idOferta`, `Customer_Id`, `Agreement_Num`, `semana` con persistencia anti-colisión (`utils/offer_id_allocator.py`).
- [x] Implementar `pages/ofertas_listado_page.py` (búsqueda y selección de tarjeta).
- [x] Agregar `BTN_CLIENTE_FRECUENTE` (y su método `click_cliente_frecuente()`) a `pages/login_page.py`.
- [ ] Confirmar template exacto de `descOferta` y reglas de `plazo`/`tasa` según tipo de oferta (regla de negocio — ver documento de contexto).
- [x] Selectores de `pages/ofertas_listado_page.py` validados contra UAT (búsqueda y click en tarjeta funcionan).
- [x] Pantalla posterior a "Sí" en método de entrega para CF: es "Iniciar Proceso de Identidad" (CF sí repite identidad).
- [x] Test CF (`tests/test_login_cf.py`): generar ids → insert de oferta → login → búsqueda → venta.
- [x] Integrar CF (y la mezcla CF+CN) a `python run.py`.
- [ ] Validar comportamiento cuando la oferta insertada no aparece en el listado (timeout de sincronización front↔DB).

### Generador de identificadores únicos — implementado

`utils/offer_id_allocator.py` (`OfferIdAllocator`), mismo patrón que `utils/birthdate_allocator.py`: SQLite en `data/generated_offer_ids.sqlite3` (tabla `used_offer_ids`), transacción `EXCLUSIVE` para ser seguro entre ejecuciones paralelas.

- `calcular_semana(hoy)`: semana `AAAASS` con corte cada miércoles (se desplaza la fecha 2 días atrás antes de calcular la semana ISO estándar).
- `get_unique_ids(branch, hoy)`: retorna `{idOferta, Customer_Id, Agreement_Num, semana}` únicos para el mes actual, iterando `persona` (0-9) y `consecutivo` (1-999) hasta encontrar una combinación libre. Las fórmulas de cada id están en el documento de contexto.
- **Validado:** dos llamadas consecutivas a `get_unique_ids(branch=2025)` el 22/09/2026 devolvieron `idOferta=26090001` / `26090002` (consecutivo incrementado correctamente, sin colisión) y `semana=202638` en ambos casos.

#### Lógica de generación (pseudocódigo original de diseño)

```python
def construir_oferta(agencia: str, monto: float, es_refin: bool, nombre_cliente: str) -> OfferData:
    hoy = datetime.now()
    aamm = hoy.strftime("%y%m")
    id_persona = generar_id_persona()
    consecutivo = generar_consecutivo(id_persona)
    branch = agencia[:4]
    id_oferta = int(f"{aamm}{id_persona}{consecutivo}")
    customer_id = int(f"{branch}{aamm}{id_persona}{consecutivo}")
    agreement_num = int(f"{aamm}{id_persona}{consecutivo}")
    ...
```

> El diseño original derivaba `tipoDeOferta` de "REFIN" y ponía `Agreement_Num` en `descOferta`; la implementación real usa las correcciones observadas (ver documento de contexto).

### Page Object del listado de ofertas — implementado

`pages/ofertas_listado_page.py` (`OfertasListadoPage`):
- `buscar_cliente(nombre_cliente)`: escribe en el input **Buscar** y espera a que el listado filtre.
- `esperar_tarjeta_cliente(nombre_cliente)` / `click_tarjeta_cliente(nombre_cliente)`: localizan la tarjeta por el texto del nombre y hacen click en su botón de estatus (con fallback a JS click, igual que el resto de páginas).
- `seleccionar_cliente(nombre_cliente)`: encadena ambos pasos.

Los XPaths siguen el patrón "buscar el texto del nombre y subir al ancestro más cercano que tenga un botón"; se validaron contra UAT (búsqueda y click en tarjeta funcionan).

### Test end-to-end CF — implementado

Los tramos comunes a ambos flujos viven en `flows/venta_comun.py` (`flujo_metodo_entrega`, `flujo_identidad_a_otp`, `flujo_beneficiario_a_finalizar`). **`flows/oferta_cf.py`**, **`flows/venta_cf.py`** y **`tests/test_login_cf.py`** contienen:

- `construir_oferta_cf(numero_ciclo)` (ver "Construcción de la oferta").
- `ejecutar_venta_cf(driver, numero_ciclo)`: inserta la oferta vía `OfferRepository`, hace login, navega **Ventas → Registrar Venta → Cliente frecuente**, busca y selecciona la tarjeta con `OfertasListadoPage.seleccionar_cliente()`, confirma la oferta con `PrestamoPersonalPage.confirmar_oferta_cf()` y continúa con el flujo compartido. Devuelve `idOferta`, `nombreCliente` y `folio`.
- `capturar_diagnostico_falla(driver, ciclo)`: guarda screenshot, HTML, URL y requests del punto de falla en `data/diagnostico_cf/`.
- `TestLoginProvidentCF.test_login_exitoso_cf`: ciclos/resumen igual que el test CN, guardando resultados en `data/run_results_cf.json`.

**Estado (23/09/2026):** el flujo CF llegó hasta finalizar la venta en UAT (folio generado). Los fallos intermedios encontrados y corregidos: pantalla de OTP Provident inexistente en CF, consentimiento de geolocalización, espera larga del facematch y modal "Aceptar" ausente al finalizar. Pendiente: una corrida completa sin intervención con el código final, y ciclos múltiples.

#### Validado sin abrir navegador
- `construir_oferta_cf()` genera una `OfferData` completa y consistente (ids únicos, agencia resuelta, `descOferta` con formato esperado).
- `pytest --collect-only` recolecta correctamente tanto `tests/test_login.py` como `tests/test_login_cf.py` sin errores de import.

#### Recuperación entre ciclos
Si un ciclo falla, `LoginPage.recuperar_sesion_tras_fallo()` intenta cerrar sesión desde la UI (menú hamburguesa → "Salir") y, si no puede, borra cookies y storage, para que el siguiente ciclo pueda hacer login (antes un fallo dejaba la sesión abierta y los ciclos siguientes fallaban en el login). Aplica a CN y CF. En CF además se guarda diagnóstico de la falla en `data/diagnostico_cf/`. Tras finalizar la venta se usa `cerrar_sesion_local()` (borra cookies/storage y recarga el login) en lugar de "Salir".

### Módulo de conexión a botDB — implementado

`services/offer_repository.py`:

- **`OfferData`** (`dataclass`): representa una fila de `dbo.Ofertas`, con los campos fijos/`NULL` ya con su valor por defecto, y `FechaActualizacion` autogenerado en `__post_init__` si no se provee.
- **`OfferRepository`**: hereda de `SqlServerRepository` (base `botDB`, host Pesos_Offer; lee `PESOS_OFFER_*` del `.env`).
  - `test_connection()`: valida la conexión (`SELECT 1`).
  - `insert_offer(offer: OfferData)`: construye el `INSERT` dinámicamente a partir de los campos del dataclass y ejecuta con parámetros (`?`) — nunca por interpolación de strings, para evitar inyección SQL.
  - `offer_exists(id_oferta)`: chequeo de duplicados antes de insertar.
  - `delete_offer(id_oferta)`: borrado por `idOferta`; lo usa `run.py` para limpiar ofertas de intentos fallidos antes de cada reintento (y sirve para limpieza manual).
- Dependencia: `pyodbc==5.3.0` en `requirements.txt`. Drivers disponibles en la máquina de pruebas: `ODBC Driver 17/18 for SQL Server`.
- **Validado end-to-end (22/09/2026):** con `.env` real configurado, se confirmó `test_connection()` → conexión exitosa; `insert_offer()` con una oferta de prueba (`idOferta=90000001`, `nombreCliente='TEST DEVIN AUTOMATION'`) → fila insertada, confirmada con `offer_exists()`; `delete_offer()` → limpieza confirmada con `offer_exists()` retornando `False`.

### Generador de nombres y RFC — implementado

`utils/mexican_names.py` (`MexicanNames`):
- `generar()`: devuelve `nombre`, `apellido_paterno`, `apellido_materno` y `nombre_completo` a partir de pools de nombres (hombre/mujer) y apellidos mexicanos comunes.
- `rfc(persona, fecha_ddmmyyyy)`: RFC con forma de persona física derivado del nombre y la fecha de nacimiento de la oferta (reglas en el documento de contexto).
