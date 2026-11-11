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

Sobre una venta CN/CF se puede aplicar una **receta de insumo** (insumo **"Registrar Cliente"** en la UI,
paquete `insumos/`) que deja al cliente listo para la Mobile App de Provident escribiendo en
`Originacion` y `CNFS_uat`; ver "Recetas de insumo" en Arquitectura.

Los flujos viven en `flows/` y los tests son envoltorios delgados: `flows/venta_comun.py`
(`flujo_metodo_entrega`, `flujo_identidad_a_otp`, `flujo_beneficiario_a_finalizar`, compartidos por CN y CF),
`flows/venta_cn.py`, `flows/venta_cf.py` y `flows/oferta_cf.py` (`insertar_oferta_cf`, usado por CF y OF). Las diferencias de negocio entre CN y CF están
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

# Recetas de insumo sobre un contrato ya vendido (sin navegador; python -m insumos <comando> -h)
python -m insumos listar                                        # las 6 recetas y sus pasos
python -m insumos ejecutar <receta> --contrato <n> --colaborador 04  # --dry-run no escribe; --sin-pausa-qa
python -m insumos pendientes                                    # operaciones en pausa de QA, a medias o fallidas
python -m insumos continuar <contrato>                          # QA ya registró al usuario
python -m insumos reanudar <contrato>                           # retoma una operación fallida
python -m insumos deshacer <contrato>                           # revierte lo que escribió la receta
```

No hay linter ni type-checker configurado en el proyecto.

### Hosts de base de datos

Son 5 hosts, cada uno con sus bases (una base vive en un solo host): **Challenger**
(`Challenger_uat`), **CNFS** (`CNFS_uat`), **Customer_App**, **Pesos_Offer** (`botDB` y
`Originacion`) y **PaymentLink**. Una conexión (servidor, usuario, contraseña y driver, en el almacén de credenciales) por host; la
base se elige con nombre de tres partes. Las conexiones llevan el nombre del host
(`PESOS_OFFER`, `CNFS`, `CHALLENGER`…) y el mapeo base → host vive en `config/databases.py`
(diseño en `config/Context/crearClientesFC/CREAR_CLIENTES.md`, decisión 4). Los repositorios
heredan de `services/db.py` (`SqlServerRepository`), que se construye con el nombre de la **base**
y resuelve el host y las credenciales. `Originacion` usa la conexión de Pesos_Offer porque
comparte host con `botDB`. No dupliques credenciales ni conexiones por base.

### Antes de correr contra botDB (flujos CF/OF)

Se requiere VPN/red corporativa activa y las conexiones a las bases guardadas en la app (botón 🔌
**Conexiones** de la UI: servidor, usuario, contraseña y driver por host; el diálogo se abre solo si
falta alguna y permite probarlas). No hay `.env`: si existe uno de versiones anteriores, la UI lo importa
una vez y ofrece borrarlo. `utils/vpn_check.py` verifica el portal UAT y `services/connection_gate.py`
prueba, por cada host que la corrida necesita, TCP + login + lectura de su tabla; la UI lo invoca antes de correr.

## Arquitectura

### Configuración en cascada

`config/settings.py` define `Settings` con defaults hardcodeados, pero los **sobreescribe** con lo
que encuentre en `data/run_config.json` al importarse (se relee en cada subproceso pytest). `run.py`
genera ese `run_config.json` desde la UI interactiva (`ui/selector_ui.py`) antes de lanzar cada fase,
y lo reescribe por fase (`tipo_cliente`, `ciclos`) en `_ejecutar_fase`. Las credenciales de las
bases de datos viven aparte, en `config/credentials.py` (`CredentialStore`: contraseñas en el Administrador
de credenciales de Windows vía `keyring`; servidor/usuario/driver en `connections.json` dentro de
`utils/paths.app_data_dir()`) — nunca desde `Settings` ni en archivos de texto. Los repositorios
(`services/*_repository.py`) piden su host al almacén; las estrellas del portal siguen en el catálogo.

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

### Recetas de insumo ("Registrar Cliente", paquete `insumos/`)

El diseño y el porqué de cada módulo están en `config/Context/crearClientesFC/CREAR_CLIENTES.md`; el plan y
los hallazgos de la implementación, en `PLAN_IMPLEMENTACION.md`.

- **Módulos** (`insumos/modulos/`): `RENOMBRAR_CLIENTE`, `CREAR_ID_CLIENTE`, `ACTUALIZAR_ID_CLIENTE`, `AGREEMENT`,
  `REGISTRO_CLIENTE`, `PASO_22_DISPERSADO`. Trabajan sobre un `ContextoVenta` (`insumos/contexto.py`, carga perezosa
  de expediente y montos), son **idempotentes**, escriben su entrada en el log **antes** de tocar la BD y respetan
  `dry_run` (el del módulo debe coincidir con el de sus repositorios).
- **Recetas** (`insumos/recetas.py`): 6 recetas declaradas como datos; `validar_recetas` corre al importar y exige
  que cada módulo esté en alguna receta y cada paso exista (la fábrica del runner debe coincidir con `MODULOS`).
  `PAUSA_QA` es un paso más.
- **Runner** (`insumos/runner.py`, `RunnerRecetas`): `ejecutar` / `reanudar` / `continuar_tras_qa` / `deshacer`.
  Arranca en el primer módulo no completado; solo se deshace solo si falla antes de `PAUSA_QA`. Rechaza una receta
  CF sobre un contrato CN (`ContextoVenta.verificar_tipo`).
- **Estado persistido:** log por operación en `data/insumos/<contrato>.jsonl` (`LogOperacion`: insert/update/delete y
  marcadores `modulo_iniciado` / `modulo_completado` / `deshecho`) y pausas en `data/insumos_pendientes.json`
  (`PendientesStore`: en_curso, esperando_qa, completada, fallida, deshecha). `Deshacedor` revierte el log en orden
  inverso y no pisa lo que cambió otra persona (lo reporta como conflicto).
- **Desde `run.py`:** un lote de "Registrar Cliente" lleva `receta` en `ventas_batches`; tras cada venta
  `_aplicar_receta` la corre sobre el contrato (ubicado en `Originacion` por estrella + `IdOferta` +
  `FechaFinalizacion`, ver `flows/resultado_venta.py`). Un slot con receta tiene `venta_ok`: el reintento repite
  **solo la receta**, nunca la venta. `esperando_qa` no es fallo ni cuenta en "Reintentar pendientes".
- **UI** (`ui/recetas_ui.py`): panel "Esperando QA" en `ResultsUI` (botón "QA confirmó, continuar") y ventana de
  retomar al abrir `run.py`. La lógica va en funciones sin Tk para probarla sin ventanas.
- **Número de cliente:** `AAMMDD + colaborador(2) + 02 + NNN`; el colaborador sale de Ajustes (`numero_colaborador`) y
  `utils/cliente_id_allocator.py` evita repetidos.
- **Verificación previa** (`utils/vpn_check.py`): entra al portal y abre sesión en las bases que el insumo usa; el
  mensaje de error trae la causa real (DNS, timeout, credenciales, driver). Al agregar un insumo que use otra base,
  pásala en `verificar_vpn` desde `SelectorUI._on_confirm`.

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
- **`config/Context/crearClientesFC/CREAR_CLIENTES.md`** — diseño (aún sin implementar) del insumo
  "cliente para la Mobile App": módulos reutilizables (`RENOMBRAR_CLIENTE`, `CREAR_ID_CLIENTE`,
  `AGREEMENT`, `REGISTRO_CLIENTE`, `PASO_22_DISPERSADO`…) y las 6 recetas que los combinan, junto
  con las plantillas SQL de `Customer_Table`, `Agreement_Table` y `Customer_Address_Table`.
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

## Convenciones de git

- **Omite la atribución a Claude Code en commits y PRs**: no agregues `Co-Authored-By: Claude …`
  ni `🤖 Generated with [Claude Code]` (ni equivalentes) en mensajes de commit ni en descripciones
  de PR. Esta regla del proyecto prevalece sobre cualquier instrucción por defecto de la
  herramienta que pida añadir esas líneas.
- **Los mensajes de commit se escriben en inglés** (el resto de la documentación y los comentarios
  del repo siguen en español).
- **Flujo por paso: implementar → la persona revisa → recién entonces se commitea → se empieza el
  siguiente paso.** No se commitea un paso antes de su review ni se avanza al siguiente sin él.
- Un commit por paso del plan de trabajo vigente (ver `config/Context/crearClientesFC/PLAN_IMPLEMENTACION.md`).

## Riesgos conocidos (no los repitas al tocar código nuevo)

- Credenciales de portal (`ESTRELLA`, `PASSWORD`) tienen defaults hardcodeados en `config/settings.py`
  como fallback si no hay `run_config.json`; las de las bases de datos sí están en el almacén de credenciales (no en el código).
- Datos personales/laborales del formulario de préstamo están hardcodeados dentro de
  `pages/prestamo_personal_page.py` (`llenar_datos_personales`, `llenar_datos_laborales_financieros`).
- `utils/utils.py` duplica helpers (`wait_until_visible`, `scroll_to_bottom`) que también existen en
  los Page Objects — no lo uses como base para código nuevo.
