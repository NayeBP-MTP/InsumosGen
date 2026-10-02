# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Qué es este repositorio

Framework de automatización E2E (Python + Selenium + Pytest + Allure) del flujo de venta de
préstamo personal en el portal UAT de Provident (`originacion-uat.providigital.com`, base `botDB`).
Automatiza tres tipos de operación:

- **CN (Cliente Nuevo)** — `tests/test_login.py`: flujo completo desde cero (identidad → docs →
  datos → OTP Provident → plazo/monto → método de entrega → beneficiario).
- **CF (Cliente Frecuente)** — `tests/test_login_cf.py`: inserta una oferta preautorizada en
  `botDB.dbo.Ofertas` y luego vende sobre ella (orden distinto a CN: oferta → método de entrega →
  identidad → docs → datos → beneficiario; sin OTP Provident; con consentimiento de geolocalización).
- **OF (Oferta)** — `tests/test_oferta.py`: solo inserta y verifica la oferta en `botDB`, sin
  ejecutar la venta en el navegador.

`tests/test_login_cf.py` reutiliza los flujos compartidos definidos en `tests/test_login.py`
(`_flujo_metodo_entrega`, `_flujo_identidad_a_otp`, `_flujo_beneficiario_a_finalizar`); `test_oferta.py`
reutiliza `_insertar_oferta_cf` de `test_login_cf.py`. Las diferencias de negocio entre CN y CF están
documentadas en `Context.md` y `config/Context/REGLAS_DE_NEGOCIO.md`.

## Comandos

```bash
# Instalar dependencias (entorno virtual recomendado)
pip install -r requirements.txt

# Generar el video de cámara fake requerido por Legalario (una vez, o si cambia data/selfie.jpeg)
python utils/generate_fake_camera_video.py

# Ejecutar vía el asistente interactivo (recomendado): pide agencia, tipo(s) de cliente,
# método de entrega, ciclos por tipo; escribe data/run_config.json y orquesta las fases
# OF → CF → CN en subprocesos pytest independientes
python run.py

# Ejecutar un flujo directamente (requiere data/run_config.json ya generado)
pytest tests/test_login.py --alluredir=allure-results       # CN
pytest tests/test_login_cf.py --alluredir=allure-results    # CF
pytest tests/test_oferta.py --alluredir=allure-results      # OF (solo inserta oferta)

# Un solo test (cada archivo define una única clase/test end-to-end)
pytest tests/test_login_cf.py::TestLoginProvidentCF::test_login_exitoso_cf -s -v

# Ver el reporte
allure serve allure-results
```

No hay linter ni type-checker configurado en el proyecto.

### Antes de correr contra botDB (flujos CF/OF)

Se requiere VPN/red corporativa activa y un `.env` (copiado de `.env.example`) con
`BOTDB_SERVER`, `BOTDB_DATABASE`, `BOTDB_USER`, `BOTDB_PASSWORD`, `BOTDB_DRIVER`. `utils/vpn_check.py`
verifica alcanzabilidad del portal UAT y del SQL Server antes de correr; `run.py` la invoca desde la UI.

## Arquitectura

### Configuración en cascada

`config/settings.py` define `Settings` con defaults hardcodeados, pero los **sobreescribe** con lo
que encuentre en `data/run_config.json` al importarse (se relee en cada subproceso pytest). `run.py`
genera ese `run_config.json` desde la UI interactiva (`ui/selector_ui.py`) antes de lanzar cada fase,
y lo reescribe por fase (`tipo_cliente`, `ciclos`) en `_ejecutar_fase`. Las credenciales de botDB
viven aparte, en `.env`, y las lee `services/offer_repository.py` vía `python-dotenv` — nunca desde
`Settings`.

### Orquestación de una corrida (`run.py`)

`run.py` no ejecuta pytest directamente sobre todo: por cada tipo de cliente pendiente (orden fijo
`OF → CF → CN`, en `ORDEN_TIPOS`) lanza un **subproceso pytest independiente** (`_ejecutar_fase`),
lee su archivo de resultados (`data/run_results_{cf,of}.json` / `run_results.json`), actualiza
`slots` (estado por operación) y acumula el historial en `RunHistory` (`utils/run_history.py`).
Si una fase CF falla a mitad de venta, la oferta insertada en `botDB` queda huérfana; `run.py` la
detecta comparando IDs antes/después vía `utils/offer_id_allocator.py` y la borra con
`OfferRepository.delete_offer` al iniciar la siguiente ronda (`_borrar_ofertas_fallidas`). La UI
completa vive en `ui/` (`SelectorUI`, `ProgressUI`, `ResultsUI`, `history_ui.py`) y se comunica con
los subprocesos pytest vía el archivo/canal de `utils/progress.py` (`Progress.emit`, también
enganchado a `allure.step` en `conftest.py`).

### Verificación de oferta antes de abrir el navegador (flujo CF)

Antes de tocar Selenium, el flujo CF inserta la oferta en `botDB.dbo.Ofertas`
(`OfferRepository`) y hace un `SELECT` de verificación con reintentos
(`OfferRepository.verify_offer_inserted`, hasta 5 intentos / 2s) comparando los campos clave. Si no
aparece o difiere, el test falla con un mensaje claro sin haber abierto Chrome. Antes del insert se
ajusta `semana` a la más reciente de la tabla, o el front no listaría la oferta.

### Interceptor de red para Legalario (identidad/OTP)

`services/network_interceptor.py` inyecta JS para interceptar `fetch`/`XHR` globalmente en el
navegador, antes de iniciar el flujo de identidad. Dos funciones separadas y no relacionadas viven
en el mismo mecanismo:

- **Mock de imágenes**: sustituye `image_content`/`selfie` en los requests al SDK de Legalario por
  las imágenes locales de `data/` (`services/image_encoder.py` las convierte a base64/data URL).
- **Captura de OTPs**: guarda las respuestas de los endpoints de confirmación en variables globales
  del navegador; `NetworkInterceptor.get_last_sms_otp_code()` (OTP Provident, `body.code`) y
  `get_last_legalario_otp_code()` (OTP Legalario, `data.otp_code`) las leen desde Python.

`services/legalario_auth_resolver.py` y `services/legalario_uploader.py` son infraestructura
adicional para reenviar requests reales de Legalario con imagen sustituida (no integrados en el
flujo actual de los tests).

### Cámara fake para facematch desatendido

Legalario requiere una cámara real para el facematch; `utils/generate_fake_camera_video.py` genera
`data/selfie.y4m` a partir de `data/selfie.jpeg` (con zoom progresivo para disparar el trigger de
"acércate" del SDK). `conftest.py` monta Chrome con `--use-fake-device-for-media-stream` apuntando a
ese archivo cuando `Settings.USE_FAKE_CAMERA=True`. Debe regenerarse si cambia `selfie.jpeg`.

### Unicidad de datos generados entre corridas

Tres generadores con SQLite local en `data/` evitan colisiones entre ejecuciones (incluidas
paralelas, vía transacción `EXCLUSIVE`):

- `utils/birthdate_allocator.py` (`generated_birthdates.sqlite3`) — fechas de nacimiento únicas.
- `utils/offer_id_allocator.py` (`generated_offer_ids.sqlite3`) — `idOferta` únicos para CF/OF.
- `utils/mexican_names.py` — nombres/RFC coherentes para clientes de prueba.
- `utils/catalog_db.py` (`data/catalog.sqlite3`) — catálogos (agencias, etc.) usados por la UI y los tests.

### Reglas de negocio y contexto — dónde viven

El comportamiento del portal y las reglas de negocio **no están solo en el código**; antes de tocar
un flujo, revisa:

- **`Context.md`** — estado de la automatización CF, orden real validado en UAT, diferencias CN/CF,
  reglas de negocio y datos observados (montos por agencia, métodos de entrega, etc.).
- **`ESPECIFICACIONES.md`** — diseño del flujo CN y CF a nivel de pantallas/componentes.
- **`config/Context/REGLAS_DE_NEGOCIO.md`** — qué significa cada cosa y por qué (conceptual, no de
  automatización); plantilla SQL de referencia en `config/Context/offers.sql`.
- **`InsumosGen/`** — contenido copiado del repo hermano `InsumosGen` (contexto para generar
  insumos de prueba; ver siguiente sección).

Cuando una regla de negocio cambie o se descubra algo nuevo validando contra UAT, actualiza el
documento correspondiente — estos archivos son la fuente de verdad para quien retome el trabajo
después, no solo comentarios en código.

### `InsumosGen/` — generación de insumos de base de datos

Carpeta con contexto y generadores SQL para poblar `botDB`/`CNFS_NFS_DBO` con datos de prueba
(ofertas, contratos, agencias, representantes, recibos de pago), separados de la lógica de
automatización:

- `InsumosGen/schema/` — modelo DBML completo (`InsumosProvident.dbml`) y su documentación curada
  por dominio en `schema/mapping/` (núcleo NFS, productos/eventos, org, apps satélite, relaciones).
- `InsumosGen/negocio/` — `onboarding_po.md` es la **fuente de verdad de negocio** (roles, jerarquía
  organizacional, niveles de precio N1/N2/N3, folios, bundling); `onboarding_po.txt` es el borrador
  de trabajo con trazabilidad (no subir a un Gem/LLM externo); `gem_tecnico.md` es el resumen técnico
  curado para ese propósito.
- `InsumosGen/generadores/` — scripts `.sql` de generación por dominio (`Ofertas/`, `Contratos/`,
  `Users/`, `transactions/`, `AppScoring/`, `Unbundling/`) más utilitarios sueltos
  (`agenciesGenerator.sql`, `caClientGenerator.sql`, `folioGenerator.sql`).
- `InsumosGen/output/` — resultados ya generados y listos para ejecutar en SQL Server (nombre de
  archivo con fecha embebida; no hay una versión "vigente" marcada, revisa la fecha).
- `InsumosGen/CONTEXT.md` explica el dominio (NFS/CNFS, llaves compuestas, esquemas satélite) y las
  convenciones de generación de ofertas (formato `idOferta`, `semana`, `descOferta`, etc.) con más
  detalle técnico que este archivo.

**Convención de negocio vs. técnica**: cuando `InsumosGen/CONTEXT.md` y `InsumosGen/negocio/onboarding_po.*`
discrepen en un tema de negocio, prevalece la fuente de negocio (`onboarding_po.txt`/`.md`).

### Skills de Claude Code sobre InsumosGen (`.claude/skills/`)

- **`insumo-creator`** — workflow para generar insumos de BD (hoy: representantes en BotDB y
  Challenger) con INSERT + rollback en `InsumosGen/output/`. Usa el esquema de `InsumosGen/schema/`.
- **`payment-receipt-generator`** — genera recibos de pago (Customer → Agreement → Agreement_Transaction
  → Agreement_Transaction_Receipt) en `CNFS_uat.NFS_DBO`, con reglas y tabla de cargo ya extraídas en
  `references/`.
- **`skill-creator`** — meta-skill para crear/iterar otras skills (no específica de este dominio).

Si mueves o renombras carpetas dentro de `InsumosGen/`, revisa las rutas hardcodeadas en los
`SKILL.md`/`README.md` de estas skills — no se actualizan solas.

## Riesgos conocidos (no los repitas al tocar código nuevo)

- Credenciales de portal (`ESTRELLA`, `PASSWORD`) tienen defaults hardcodeados en `config/settings.py`
  como fallback si no hay `run_config.json`; las de `botDB` sí están correctamente en `.env`.
- Datos personales/laborales del formulario de préstamo están hardcodeados dentro de
  `pages/prestamo_personal_page.py` (`llenar_datos_personales`, `llenar_datos_laborales_financieros`).
- `utils/utils.py` duplica helpers (`wait_until_visible`, `scroll_to_bottom`) que también existen en
  los Page Objects — no lo uses como base para código nuevo.
