# Plan de Implementaciones — InsumosGen

> **Actualizado:** Noviembre 2026
> **Objetivo:** Distribuir el proyecto como app de Windows instalable, con actualizaciones
> automáticas desde GitHub Releases y credenciales administradas desde la UI, y después
> modernizar la UI **sin mezclar cambios grandes en un mismo release**.

## Historial — Implementaciones 1 a 4 (completadas, Mayo 2026)

Ya están en el código; se conservan aquí solo como referencia.

| # | Qué se hizo | Dónde vive |
|---|---|---|
| 1 | Cerrar sesión al finalizar el flujo | `pages/login_page.py` (`cerrar_sesion`) |
| 2 | BD SQLite local de catálogos (agencias, métodos de entrega) | `utils/catalog_db.py`, `data/catalog.sqlite3` |
| 3 | UI de selección previa a la ejecución y punto de entrada único | `ui/selector_ui.py`, `run.py`, `data/run_config.json` |
| 4 | Ejecución en N ciclos con resumen de resultados | `run.py`, `data/run_results*.json` |

Los demás cambios posteriores (CF, OF, paralelización, historial, recetas) están documentados
en `Context.md`, `CLAUDE.md` y `config/Context/crearClientesFC/PLAN_IMPLEMENTACION.md`.

---

## Versionado y orden de entrega

SemVer `MAJOR.MINOR.PATCH`. El número fija el **orden**. Los hitos `0.9.x` son internos
(no se publican ni se etiquetan); desde `v1.0.0` cada versión es un release de GitHub.

| Versión | Contenido | Rama de trabajo | Base |
|---|---|---|---|
| **0.9.0** (interno) | Implementación 0.9: credenciales y estrellas administradas desde la app, sin `.env` | `feat/credentials` | `dev` |
| **0.9.1** (interno) | Misma implementación portada a `feat/recipes` | `feat/recipes` | `feat/recipes` + merge de `feat/credentials` |
| **v1.0.0** | Implementación 5: empaquetado, instalador y auto-update | `feat/packaging` | `dev` |
| **v1.0.1** | Release mínimo solo para **probar el auto-update** (ver 5.11). Sin cambios funcionales | `fix/update-smoke-test` | `dev` |
| **v1.0.x** | Fixes de empaquetado/updater que surjan en campo | `fix/*` | `dev` |
| **v1.1.0** | Implementación 5b: `feat/recipes` mergeada a `dev` | `feat/recipes` | `dev` tras v1.0.x |
| **v2.0.0** | Implementación 6: reescritura de la UI (pywebview + frontend web) | `feat/ui-rewrite` | `dev` tras v1.1.0 |
| v2.0.0-beta.N | Pre-releases de la UI para probadores (*pre-release* en GitHub; `releases/latest` los ignora, así que los colegas no los reciben) | `feat/ui-rewrite` | — |

Reglas:
- Desde v1.0.0, cada release se publica **solo**: al mergear a `main` el pipeline (5.9) lee `version.py`, y si esa versión aún no tiene release crea el tag `vX.Y.Z`, construye y publica. Las ramas de trabajo se integran en `dev`; `dev` → `main` (con la versión ya subida) es lo que dispara el release. No se sube nada a mano.
- Un paso del plan = un commit, **después** de la revisión (ver `CLAUDE.md`, convenciones de git).
- Los mensajes de commit van en inglés; los documentos en español.

```
0.9.0 (dev) → 0.9.1 (recipes) → v1.0.0 → v1.0.1 → [v1.0.x] → v1.1.0 (recetas) → v2.0.0 (UI)
```

> Credenciales primero: el empaquetado no puede depender de editar `.env` a mano.
> Empaquetado antes que recetas y UI: todo lo demás se entrega con él.
> Recetas antes que la UI: la UI nueva debe cubrir también las pantallas de recetas.

## Decisiones tomadas

| Tema | Decisión |
|---|---|
| Nombre | **InsumosGen** en todas partes (app, carpetas, repo, servicio del almacén de credenciales, documentos). El nombre `Providigital_Ventas` / `ProvidigitalVentas` se elimina; no hay migración (nada se había publicado) |
| Repo | Público (`NayeBP-MTP/InsumosGen`, nombre final) → el updater llama a la API de GitHub sin token |
| Instalación | Por usuario (`%LOCALAPPDATA%\Programs\InsumosGen`), **solo sin admin**: sin opciones ni diálogo de elevación |
| Dependencias externas (Chrome, ODBC Driver for SQL Server) | No se empaquetan. La app las detecta y muestra el enlace de descarga; quien no tenga admin debe pedirlas a TI (fuera de alcance) |
| Red | No hay VPN corporativa; solo la VPN del cliente (donde corren las consultas). El updater **no debe bloquear la app** si GitHub no es alcanzable: timeout corto, falla en silencio y ofrece enlace manual |
| Empaquetado | **Sin PyInstaller.** Un `Setup.exe` mínimo (Inno Setup) copia el código fuente de la app (un `.zip` por versión) y prepara en la máquina del usuario un entorno virtual con las dependencias (`pip install -r requirements.txt`). Se usa el Python 3.13 que el usuario ya tenga (validado); si no hay uno válido, se descarga el instalador oficial al instalar. Todo lo que pueda instalarse después de la instalación, se instala después |
| UI futura | pywebview (host Python) + frontend Vite/Svelte; Node solo en tiempo de build |
| Datos de usuario | Fuera de la carpeta de instalación, en `%LOCALAPPDATA%\InsumosGen\` (sobreviven a updates y desinstalación); en desarrollo apuntan a `<repo>/data`. La app instalada lo sabe por la variable de entorno `INSUMOSGEN_INSTALADO=1` que fija su lanzador |
| Imágenes de prueba | **No se entregan por defecto.** El usuario aporta todas (selfie, INE frente y reverso, comprobante) desde la pantalla de ajustes, que bloquea la operación hasta tenerlas, y genera el video de la cámara fake en su máquina (`cv2` va en las dependencias). Viven en `%LOCALAPPDATA%\InsumosGen\images\` |
| Actualizaciones | Dos niveles: (1) **código**: se baja el `.zip` del release y se reemplaza la carpeta `app\`, sin ejecutar el instalador; (2) **librerías**: si cambia el hash de `requirements.txt`, se ejecuta `pip install -r` en el mismo paso. Solo un cambio de versión de Python exige bajar un `Setup.exe` nuevo. Las librerías no se quedan viejas porque cada release fija sus versiones y Dependabot propone los cambios |
| Secretos | Contraseñas en el Administrador de credenciales de Windows (vía `keyring`); el resto en `connections.json`. Nunca en texto plano en disco ni en el repo |
| Hosts de BD | El almacén se indexa por los nombres de host de `feat/recipes` (`PESOS_OFFER`, `CNFS`, `CHALLENGER`, `CUSTOMER_APP`, `PAYMENTLINK`); en `dev` se importa `BOTDB_*` → `PESOS_OFFER` |
| Estrellas del portal | **Siguen en el catálogo** (`agencias` en `catalog.sqlite3`, sembrado desde `AGENCIAS_SEED` en `utils/catalog_db.py`): cada agencia trae su estrella. Decisión: las contraseñas de estrellas de UAT se siguen sembrando desde el código (el repo es público; se acepta). `CredentialStore` ya soporta estrellas con alias (`save/get/list/delete_estrella`) para futuras funciones que vendan u oferten con estrellas específicas, pero hoy ningún flujo las usa |

---

## Implementación 0.9 — Credenciales y estrellas administradas desde la app  (0.9.0 → 0.9.1)

**Objetivo:** Eliminar `.env` y `python-dotenv`. El usuario captura, edita y **prueba** las
conexiones a las BD y las credenciales de las estrellas del portal desde la UI, sin editores
externos ni CLI. Alcance: credenciales de **bases de datos**. Las estrellas del portal quedan fuera por
decisión (siguen en el catálogo, ver Decisiones); el almacén ya las soporta para futuras funciones.

### Diseño

**Almacenamiento (`config/credentials.py`, clase `CredentialStore`)**

| Dato | Dónde |
|---|---|
| Contraseñas (hosts de BD y estrellas) | Administrador de credenciales de Windows vía `keyring` (DPAPI por usuario, sin admin). Servicio `InsumosGen`; usuario `host:<HOST>` o `estrella:<alias>` |
| Campos no secretos (servidor, usuario, driver, alias, ID de estrella) | `connections.json` en `app_data_dir()` |

API independiente de la UI (la usan hoy tkinter y mañana pywebview):
- Hosts: `get_connection(host)` (lanza `CredentialsMissing(host)` si falta), `save_connection`, `delete_connection`, `list_hosts`.
- Estrellas: `list_estrellas()`, `get_estrella(alias)` → `(id, contraseña)`, `save_estrella`, `delete_estrella`.
- Hoy ningún flujo usa la API de estrellas: las corridas siguen tomando `focus_id`/`password` del catálogo vía `run_config.json`. Queda lista para cuando se agreguen funciones por estrella.
- Los subprocesos pytest corren con el mismo usuario de Windows y leen el almacén directamente; solo el proceso de la UI escribe.

**Probador de conexiones (`services/connection_tester.py`, clase `ConnectionTester`)**

Devuelve un resultado estructurado (`ok`, categoría, mensaje accionable):
1. Prueba TCP al puerto SQL → "host inalcanzable: ¿está activa la VPN del cliente?".
2. `pyodbc.connect(..., timeout=5)` + `SELECT 1`; categorías por SQLSTATE/error nativo: `IM002` driver ODBC ausente (con enlace de descarga), `28000`/18456 usuario o contraseña rechazados, `08001` servidor inalcanzable, 4060 base inexistente o sin acceso.
3. Sondeo opcional de lectura de la tabla esperada (p. ej. `botDB.dbo.Ofertas`) para detectar "login ok pero sin permisos".
4. Se sanean los mensajes de error antes de mostrarlos o registrarlos (pyodbc puede reflejar la cadena de conexión con la contraseña).
5. La cadena de conexión escapa valores con `{...}` (`}` → `}}`): ahora los usuarios teclean contraseñas con `;`, `{`, `=`.
6. Estrellas del portal: solo se verifica alcanzabilidad del portal; la contraseña se valida en el primer login (no se maneja el navegador desde el probador).

Cuándo corre:
- Botón **Probar** por host en el diálogo.
- **Compuerta previa a la corrida:** prueba solo los hosts que necesita el tipo de corrida (p. ej. CF/OF → `PESOS_OFFER`; generación de agencias → también `CHALLENGER`), reemplazando los mensajes de `.env` de `verificar_vpn`.
- Nunca al arrancar la app para todos los hosts (bloquearía con la VPN del cliente apagada).

**UI (tkinter, dentro de la UI actual)**: diálogo "Conexiones y estrellas" accesible desde el selector. Se abre solo cuando falta algo que la corrida necesita. Tarjeta por host (servidor, usuario, contraseña enmascarada con botón mostrar, driver como lista de `pyodbc.drivers()`, botón Probar con resultado verde/rojo y motivo) (la gestión de estrellas en la UI se difiere hasta que algún flujo las use). La pantalla definitiva se rehace en v2.0.0 sobre este mismo backend.

### Pasos — 0.9.0 (rama `feat/credentials`, desde `dev`)

- [x] **0.9.1** `utils/paths.py` con `app_data_dir()` (`%LOCALAPPDATA%\InsumosGen` si la app está instalada; `<repo>/data` si no) — solo este helper; el resto de rutas se migra en 5.2. Más `config/credentials.py` (`CredentialStore`) con pruebas usando un backend `keyring` falso. Decidir con una prueba en un equipo restringido qué pasa si el Administrador de credenciales no está disponible (ver riesgos).
- [x] **0.9.2** `services/connection_tester.py` con las categorías de error y el saneo de mensajes; pruebas con `pyodbc` simulado para cada categoría. Escape de valores en la cadena de conexión.
- [x] **0.9.3** Cambiar los consumidores en `dev`: `services/offer_repository.py` y `services/agency_repository.py` (constructores), `utils/vpn_check.py` (servidor/puerto por host desde el almacén), sin más cambios en `settings.py`/`run.py`/`selector_ui.py` (las estrellas siguen en el catálogo).
- [x] **0.9.4** Diálogo "Conexiones y estrellas" en tkinter + compuerta previa a la corrida + apertura automática cuando faltan datos.
- [x] **0.9.5** Importación única de lo existente al almacén (`.env`: `BOTDB_*`→`PESOS_OFFER`, `CHALLENGER_*`, `CNFS_*`) y oferta de borrar el `.env`. Después: quitar `python-dotenv` y los `load_dotenv()`, borrar `.env.example`, y actualizar `CLAUDE.md`, `README.md`, `Context.md` y los mensajes que mencionan `.env`.
- [ ] **0.9.6** Revisión → merge a `dev`. Hito interno **0.9.0** (sin tag ni release).

### Pasos — 0.9.1 (portar a `feat/recipes`)

Precondición: la rama `feat/recipes` debe tener su árbol de trabajo limpio (commitear antes sus cambios pendientes en `run.py` y `ui/*`).

- [ ] **0.9.7** Mergear `feat/credentials` dentro de `feat/recipes` (merge, no cherry-pick: así el futuro `merge dev` de 5b.1 no vuelve a conflictuar con estos commits).
- [ ] **0.9.8** Adaptar lo propio de recetas: `services/db.py` (`SqlServerRepository` lee del almacén con `get_connection(host_de(base))` en lugar de `<HOST>_*` del entorno; es el único punto de lectura), `utils/vpn_check.py` (la versión de recetas ya valida por host y mapea errores: unificarla con `ConnectionTester` en lugar de duplicar), docstrings de `config/databases.py`, `services/*_repository.py`, y el mensaje de `ui/selector_ui.py` que dice "revisa tu .env".
- [ ] **0.9.9** Tarjetas para los hosts `CNFS`, `CUSTOMER_APP` y `PAYMENTLINK` en el diálogo; definir qué hosts requiere cada tipo de corrida y cada receta para la compuerta previa.
- [ ] **0.9.10** Adaptar las pruebas de recetas que dependían del entorno (`tests/test_vpn_check.py`, `tests/test_offer_repository.py`, `tests/test_repositorios_insumos.py`, …) para usar un almacén falso. Revisión → hito interno **0.9.1** (sin tag).

### Riesgos

- **Almacén no disponible** (política corporativa que bloquea el Administrador de credenciales): no se cae a texto plano. Opciones a decidir en 0.9.1: credenciales solo en memoria durante la sesión (los subprocesos las reciben por entorno desde `run.py`) o bloquear con un mensaje claro.
- **Contraseñas de estrellas UAT en el repo público** (`AGENCIAS_SEED` en `utils/catalog_db.py` y defaults de `config/settings.py`): se acepta por decisión del equipo; no reutilizar esas contraseñas fuera de UAT.
- **Divergencia dev ↔ recetas** en `vpn_check.py` y los repositorios: por eso 0.9.1 se hace con merge y adaptación explícita, no copiando archivos.

---

## Implementación 5 — Empaquetado, instalador y auto-update  (v1.0.0 → v1.0.x)

**Objetivo:** Que un colega descargue un `Setup.exe` pequeño, lo instale sin admin, y reciba las
versiones futuras (código y librerías) automáticamente. **No cambia la UI** (sigue tkinter) ni el
comportamiento de los flujos CN/CF/OF.

**Base:** rama `feat/packaging`, creada desde `dev` (con 0.9.0), **no** desde `feat/recipes`.
Mantener los diffs en archivos compartidos con `feat/recipes` (`run.py`, `conftest.py`,
`config/settings.py`, `ui/*`) lo más chicos posible: la lógica nueva va en módulos nuevos
(`utils/paths.py`, `utils/updater.py`, `utils/prereqs.py`, `packaging/*`) y los archivos existentes
solo cambian en el punto de uso. Ver riesgos al final.

### Arquitectura

```
%LOCALAPPDATA%\Programs\InsumosGen\          (instalación; se reemplaza en cada update)
  app\                  código fuente de la versión instalada (zip del release) + requirements.txt
  runtime\
    venv\               entorno virtual con las dependencias
    python\             solo si hubo que instalar Python (no había uno válido)
    state.json          versión de la app, versión de Python, hash de requirements.txt
%LOCALAPPDATA%\InsumosGen\                   (datos del usuario; sobreviven a updates y desinstalación)
  images\  selfie.y4m  catalog.sqlite3  connections.json  historial…  allure-results\  screenshots\
Administrador de credenciales de Windows     contraseñas (servicio `InsumosGen`)
```

- **Python.** Se acepta un Python **3.13.x de 64 bits** que ya esté instalado (registro PEP 514 en
  HKCU/HKLM, `py -3.13`, o PATH) **solo si** `import tkinter, venv, ensurepip` funciona. Si no hay
  ninguno válido, se descarga el instalador oficial de python.org (versión y SHA-256 fijos en el
  script) y se instala en silencio solo para el usuario (`InstallAllUsers=0 PrependPath=0
  Include_launcher=0 TargetDir=...\runtime\python`): sin admin y sin tocar el Python del sistema.
- **Entorno.** `python -m venv runtime\venv` y `pip install -r app\requirements.txt` (con reintentos
  y mensajes claros si PyPI no es alcanzable). Chrome y el ODBC Driver siguen siendo externos (5.4).
- **Lanzador.** Los accesos directos ejecutan `runtime\venv\Scripts\pythonw.exe app\launch.pyw`;
  `launch.pyw` fija `INSUMOSGEN_INSTALADO=1`, el directorio de trabajo y abre la UI. Los subprocesos
  pytest lo heredan.
- **Contrato del release con el updater** (si algo de esto cambia, el updater deja de ver la versión):
  - Repo público `NayeBP-MTP/InsumosGen`; el updater consulta `GET /repos/NayeBP-MTP/InsumosGen/releases/latest`, que **solo devuelve el último release publicado y que no sea borrador ni pre-release**. Por eso los `v2.0.0-beta.N` y los `-rc` se marcan como *pre-release* y los colegas no los reciben.
  - Tag `vX.Y.Z`, igual a `__version__` de `version.py`; **lo crea el pipeline** sobre el commit de `main` (el updater quita la `v` y compara con `packaging.version`). El tag no se mueve ni se reutiliza; si un release sale malo, se publica el siguiente parche (o se borra el release para que `latest` vuelva al anterior).
  - Nombres de assets exactos: `InsumosGen-X.Y.Z.zip`, `InsumosGen-X.Y.Z.zip.sha256`, `InsumosGen-Setup-X.Y.Z.exe`, `InsumosGen-Setup-X.Y.Z.exe.sha256` (el `.sha256` trae `<hash>  <archivo>`). Se descargan por `browser_download_url`, sin token.
  - El cuerpo del release (notas, en español y pensadas para el usuario final) es lo que muestra el aviso de actualización.
  - La API sin autenticar permite 60 consultas/hora por IP (una oficina entera comparte IP): si responde 403/429 el updater lo trata como "no se pudo comprobar", nunca como error.
- **Qué se entrega en el release:** `InsumosGen-X.Y.Z.zip` (código) y `InsumosGen-Setup-X.Y.Z.exe`
  (instalador pequeño con el zip dentro), cada uno con su `.sha256`.

### Pasos

- [x] **5.0** Renombrar a **InsumosGen** en todo el repo (un solo commit, antes de lo demás):
  - Código: `utils/paths.py` (`APP_NAME`), `config/credentials.py` (`SERVICE`). Las contraseñas guardadas por los probadores con el nombre viejo quedan huérfanas: se vuelven a capturar una vez (aceptado).
  - Documentos: título y árbol de carpetas de `README.md`, `CODEBASE_ANALYSIS.md`, `ESPECIFICACIONES.md`, `config/Context/REGLAS_DE_NEGOCIO.md`, `PLAN_IMPLEMENTACIONES.md` y `CLAUDE.md` si aplica.
  - Comprobar con `grep -rIn "Providigital_Ventas\|ProvidigitalVentas\|Providigital Ventas"` que no queda nada (la carpeta `InsumosGen/` del repo, con los generadores SQL, no tiene relación con el nombre de la app). Renombrar la carpeta local del clon es opcional.
- [x] **5.1** `version.py` con `__version__ = "1.0.0"` (única fuente; la leen el updater, la ventana, el script de build y el instalador).
- [x] **5.2** Rutas y modo instalado:
  - `app_data_dir()` (ya existe) pasa de `sys.frozen` a la variable `INSUMOSGEN_INSTALADO`; en desarrollo sigue siendo `<repo>/data`.
  - Migrar el resto de rutas escribibles a `app_data_dir()`: `run_config*.json`, `run_results*.json`, `run_progress*.jsonl`, `user_settings.json`, las SQLite (`catalog`, `generated_*`), historial, `allure-results`, `screenshots`, `diag_comprobante.html`.
  - Archivos a tocar (lista de `grep -rn '"data/\|Path("data'`): `config/settings.py`, `run.py`, `ui/selector_ui.py`, `utils/progress.py`, `utils/run_history.py`, `utils/catalog_db.py`, `utils/*_allocator.py`, `conftest.py`, `pages/prestamo_personal_page.py`.
  - No hace falta `resource_path`: el código instalado tiene la misma estructura que el repo.
- [x] **5.2b** Traer de `feat/recipes` la pantalla de ajustes con selectores de imagen y generación del video: `git cherry-pick 3b2da83` (toca solo `ui/selector_ui.py` y `config/settings.py`; esperar un conflicto menor porque `dev` ya cambió `selector_ui.py` con 0.9). Después adaptar:
  - Las rutas de selfie, INE frente/reverso, comprobante y `selfie.y4m` apuntan a `app_data_dir()/images`; el selector copia ahí la imagen elegida.
  - Sin imágenes por defecto: la compuerta de ajustes ya obliga a cargarlas antes de operar y abre el diálogo en el primer arranque.
  - Los textos que dicen `data/selfie.jpeg` o `python utils/generate_fake_camera_video.py` cambian; el video se genera desde la UI (en proceso, con `cv2`), sin comandos.
  - Quitar de `.gitignore`/docs cualquier referencia a imágenes dentro de `data/`.
- [x] **5.2c** Primer arranque ordenado: cada vez que se abre la app, si falta algo obligatorio se abren **en este orden** (una ventana modal tras otra, sin tener que buscarlas):
  1. **Conexiones** (`ui/conexiones_ui.py`) si falta alguna de las que toda corrida necesita al arrancar (`PESOS_OFFER`: botDB y Originacion; el resto —`CNFS`, `CHALLENGER`— se exige al elegir el insumo, como hoy con `_asegurar_conexiones`). Antes se ejecuta la importación del `.env` legado.
  2. **Ajustes** (`_open_settings_dialog`) si falta cualquier ajuste de usuario, imagen o el video de la cámara fake.
  - La pantalla principal sigue bloqueada (compuerta de `_actualizar_gate_ajustes`) mientras falte algo, con un aviso que diga qué (conexiones y/o ajustes); si el usuario cierra una ventana sin completarla, la siguiente se abre igual y las dos se pueden reabrir desde sus botones.
  - Pruebas: la compuerta devuelve qué falta (conexiones, campos, imágenes, video) y el orden de apertura, sin abrir ventanas reales.
- [x] **5.2d** Ocultar (no borrar) lo que está incompleto de la paralelización, a la espera de retomarlo:
  - **Navegador invisible:** quitar de la UI el selector "Navegador" (opción *headless*, `selector_ui.py` ~436-450) y forzar `headless: False` en la configuración que se escribe.
  - **Ventas en paralelo:** `+ Agregar lote de venta` y `+ Agregar oferta` **se quedan visibles y funcionales**: se pueden crear varios lotes y ofertas, que se ejecutan **de forma secuencial** (uno tras otro). Solo se apaga el paralelismo: `MAX_WORKERS_VENTAS = 1` en `run.py` cuando `PARALELISMO_HABILITADO` es `False`. Criterio de aceptación: en UAT, una corrida con 2 lotes (agencias distintas) completa los dos en orden y el panel de progreso se ve coherente; el camino de código de varios lotes se pensó para paralelo y no se ha probado con un solo hilo.
  - Todo detrás de una constante (`PARALELISMO_HABILITADO = False` en `config/settings.py`: controla el selector de navegador y el máximo de lotes simultáneos), para reactivarlo después cambiando un valor, sin tocar la lógica. Diffs mínimos en `ui/selector_ui.py` y `run.py` por los conflictos con `feat/recipes`.
- [x] **5.3** Lanzador de fases (`run.py`, hoy `sys.executable -m pytest`): ya funciona con el venv; solo hay que usar `python.exe` (no `pythonw.exe`) para los subprocesos, con `CREATE_NO_WINDOW`, y conservar subproceso por fase, `Progress` por archivo y la muerte del árbol de procesos al abortar.
- [ ] **5.4** `utils/prereqs.py`: Chrome (registro `App Paths\chrome.exe`) y ODBC Driver 17/18 for SQL Server (`pyodbc.drivers()`). Si falta algo: mensaje con el enlace oficial y no se permite iniciar la corrida. Se integra al arranque junto a la compuerta de conexiones de 0.9.
- [ ] **5.5** Quitar `webdriver-manager` y usar Selenium Manager (incluido en Selenium 4.33): `webdriver.Chrome(options=...)` en `conftest.py`. Validar que funciona con la red del cliente (descarga el driver la primera vez); si no, documentar el fallback.
- [ ] **5.6** Build y aprovisionamiento (sustituye al `.spec` de PyInstaller):
  - `packaging/build_release.py`: genera `InsumosGen-X.Y.Z.zip` a partir de los archivos versionados (sin `InsumosGen/`, logs, `captured_requests_*.json`, `debug_*.json`, documentos salvo `README.md`), con `requirements.txt` **con versiones fijas**.
  - `packaging/bootstrap.ps1` (corre antes de que exista Python, por eso es PowerShell con `-ExecutionPolicy Bypass` solo para ese proceso): detecta o descarga Python (ver arquitectura), crea el venv, instala dependencias con progreso/reintentos y escribe `runtime\state.json`. Es idempotente: sirve también como **"Reparar entorno"** (entrada en la UI) si el venv se rompe, por ejemplo si el usuario desinstala el Python en el que se basaba.
  - **Criterio de aceptación:** en una máquina limpia, una corrida OF, una CF y una CN completan (incluyendo cargar imágenes, generar el video y capturar credenciales desde el diálogo de 0.9); abortar desde la UI mata Chrome/chromedriver. Probar además: sin Python / con Python 3.13 / solo con otra versión (p. ej. 3.11) / sin acceso a PyPI (el error debe ser claro y permitir reintentar).
- [ ] **5.7** `packaging/installer.iss` (Inno Setup): `PrivilegesRequired=lowest` (sin opción de elevar), `AppId` fijo (instala encima), carpeta por usuario, accesos directos al lanzador, desinstalador que borra `Programs\InsumosGen` pero **no** `%LOCALAPPDATA%\InsumosGen\` ni el Administrador de credenciales. Último paso de la instalación: ejecutar `bootstrap.ps1` con ventana de progreso visible. Salida: `InsumosGen-Setup-X.Y.Z.exe`.
- [ ] **5.8** `utils/updater.py` + `packaging/update.py` + integración mínima en la UI actual:
  - Al iniciar, en hilo aparte: `GET /repos/NayeBP-MTP/InsumosGen/releases/latest`, timeout corto, todo en `try/except` (sin red / bloqueado por la VPN del cliente → continúa sin avisar). Una consulta automática por arranque; la versión también va en el título de la ventana.
  - **Página de ajustes:** muestra la versión instalada (`InsumosGen vX.Y.Z`) junto a un botón **Buscar actualizaciones** que ejecuta la misma comprobación a demanda. Respuesta visible en el propio diálogo: *estás al día*, *hay una versión nueva* (notas + **Actualizar**) o *no se pudo comprobar* (sin red / límite de GitHub, con el enlace a la página de releases). El aviso de arranque, en cambio, solo aparece si hay una versión nueva.
  - La lógica vive en `utils/updater.py` (`comprobar()` devuelve estado, versión y notas) y las dos entradas —arranque y botón— la llaman; la UI no consulta GitHub por su cuenta.
  - Comparar `tag_name` con `__version__` (`packaging.version`). Si hay una más nueva: aviso con las notas y botón **Actualizar**.
  - Nivel 1 (código): bajar `InsumosGen-X.Y.Z.zip`, verificar SHA-256 (`.sha256` del release), extraer a `app.new`.
  - Nivel 2 (librerías): comparar el hash del `requirements.txt` nuevo con el de `state.json`.
  - La app se cierra y lanza `update.py` (solo biblioteca estándar, copiado a `%TEMP%`; no puede correr desde la carpeta que va a reemplazar ni con `.pyd` cargados): intercambia `app` ↔ `app.old`, ejecuta `pip install -r` solo si cambió el hash, y relanza la app. **Si pip falla, restaura `app.old`** y avisa; borra `app.old` tras un arranque correcto.
  - Si el release cambia la versión de Python fijada, la app solo ofrece el enlace al `Setup.exe` nuevo.
  - Mantener el módulo **simple**: un updater roto no puede publicarse a sí mismo; el respaldo es siempre bajar el `Setup.exe` a mano.
- [ ] **5.9** `.github/workflows/release.yml` — release automático al mergear a `main`:
  - **Disparador:** `push` a `main` (un PR mergeado es un push). `concurrency: release` (sin cancelar) para que dos merges seguidos no publiquen a la vez; `permissions: contents: write`.
  - **Paso 1, decidir:** leer `__version__` de `version.py`. Si el tag `v<versión>` ya existe, el merge no trae versión nueva: el job termina en verde con un aviso (`::warning::`) y **no publica nada** (así un merge de documentación no rompe ni duplica releases). Si no existe, sigue.
  - **Paso 2, validar:** debe existir `release-notes/<versión>.md` (notas en español para el usuario final; el job falla si falta, para no publicar sin notas) y las pruebas unitarias deben pasar (las de `tests/` que no necesitan portal ni VPN; las e2e quedan fuera).
  - **Paso 3, construir (`windows-latest`, Python 3.13 fijo):** `pip install -r requirements.txt` → `packaging/build_release.py` (zip) → Inno Setup (`choco install innosetup`) → SHA-256 de ambos archivos.
  - **Paso 4, publicar:** `softprops/action-gh-release` con `tag_name: v<versión>`, `target_commitish: ${{ github.sha }}` (crea el tag), el cuerpo desde `release-notes/<versión>.md`, los 4 assets, y `prerelease: true` si la versión lleva `-` (p. ej. `1.0.0-rc.1`, para probar el pipeline sin que `latest` lo vea).
  - Un release creado con el `GITHUB_TOKEN` no dispara otros workflows; no importa aquí porque todo vive en este solo workflow.
  - Proteger `main` en GitHub (Settings → Branches): exigir PR y que el workflow de pruebas pase antes de mergear.
  - Añadir `.github/dependabot.yml` (ecosistema `pip`, mensual) para que las librerías fijadas no se queden viejas.
- [ ] **5.10** Publicar **v1.0.0** con un primer release de prueba `1.0.0-rc.1` (pre-release) para validar el pipeline, y luego mergear `dev` → `main` con `version.py` en `1.0.0`. Revisar SmartScreen/antivirus con el `Setup.exe` real (sin firma es probable el aviso; si bloquea, pedir a TI que permita el hash/publisher o evaluar firma de código).
- [ ] **5.11** Publicar **v1.0.1** solo para **probar el auto-update de punta a punta**, en dos pasadas: (a) cambio solo de código (no debe ejecutar pip); (b) cambio de una versión fijada en `requirements.txt` (debe ejecutar pip y relanzar), y una vez forzando un fallo de pip para ver la restauración. Hasta que pase, no se anuncia a los colegas.
- [ ] **5.12** Documentar en `README.md`: instalación, prerrequisitos, qué es "Reparar entorno", dónde están los datos de usuario y las credenciales, cómo publicar un release (subir `version.py`, escribir `release-notes/X.Y.Z.md`, mergear `dev` → `main` por PR, y comprobar en Actions que el workflow termina y en Releases que están los 4 assets y que **no** es pre-release ni borrador) y cómo subir una librería (cambiar la versión fijada en `requirements.txt`).

### Riesgos

- **PyPI inalcanzable** al instalar o actualizar (proxy, VPN del cliente activa): reintentos, mensaje claro y "Reparar entorno"; si resulta frecuente, valorar incluir las ruedas (`wheelhouse`) en el release.
- **El venv depende del Python base** si se reutilizó uno del usuario: si lo desinstala, la app no abre. Cubierto con "Reparar entorno"; el arranque detecta el `pyvenv.cfg` roto y lo ofrece.
- **Tamaño en disco** mayor que un exe empaquetado (~500 MB con `cv2`/`numpy`); aceptado a cambio de un instalador pequeño y de poder actualizar librerías.
- **Primera instalación lenta** (varios minutos descargando ruedas): mostrar progreso.
- **Conflictos con `feat/recipes`** (reescribe `tests/test_login*.py`, `run.py`, `conftest.py`, `ui/*`). Mitigación: diffs mínimos en archivos compartidos (5.2/5.3) y el cherry-pick de 5.2b que ya coincide con la rama; al terminar v1.0.x hacer `git merge dev` dentro de `feat/recipes` **antes** de mergear a `dev` (v1.1.0).
- **SmartScreen/antivirus** pueden marcar el `Setup.exe` sin firmar; probar temprano (5.10), no al final.
- **Rutas hardcodeadas no detectadas** en 5.2 aparecerán solo con la app instalada; por eso el criterio de 5.6 exige una corrida real en máquina limpia.

---

## Implementación 5b — Release de recetas  (v1.1.0)

**Objetivo:** Entregar `feat/recipes` (recetas de insumos, runner con pausa QA, UI de recetas, `run.py` con tipo receta) a los colegas **a través del auto-update**, que es la primera entrega real por ese canal.

**Precondición:** v1.0.x estable (5.11 aprobado). Las credenciales ya están portadas (0.9.1).

### Pasos

- [ ] **5b.1** Mergear `dev` dentro de `feat/recipes` y resolver conflictos (esperados en `run.py`, `conftest.py`, `config/settings.py`, `tests/test_login*.py`, `ui/*`). Nada nuevo se funcionaliza en este paso.
- [ ] **5b.2** Auditoría de instalación de lo que trae la rama: toda ruta escribible nueva pasa por `app_data_dir()` (pendientes de QA, SQLite de `cliente_id_allocator`, resultados de recetas); las plantillas SQL de `insumos/` viajan dentro del zip de código; revisar `requirements.txt` por dependencias nuevas (el updater las instalará solo).
- [ ] **5b.3** Confirmar que las recetas corren con la app instalada, y que los hosts de recetas (`CNFS`, `CUSTOMER_APP`, `PAYMENTLINK`) se pueden capturar y probar desde el diálogo de 0.9.
- [ ] **5b.4** Revisión de la persona → merge a `dev` → bump a `1.1.0` → tag → el pipeline publica → verificar que una instalación de v1.0.x se actualiza sola.

---

## Implementación 6 — Reescritura de la UI  (v2.0.0)

**Objetivo:** Reemplazar tkinter por una UI moderna (movimiento, UX cuidada, modo oscuro) sin cambiar la lógica de negocio ni el empaquetado.

**Base:** `dev` después de v1.1.0. **Decisión:** pywebview (WebView2) + frontend Vite/Svelte; Node solo en build.

### Pasos

- [ ] **6.1** *Spike descartable* (rama aparte, no se mergea): solo la pantalla de progreso en pywebview + Svelte con eventos reales de `Progress`; empaquetarla con el instalador de la Implementación 5 y medir tamaño/arranque. Si falla, se evalúa Electron con lo aprendido.
- [ ] **6.2** Inversión de control en `run.py`: la UI pasa a ser el bucle principal y `run.py` expone un controlador con API (`get_catalog`, `check_prereqs`, `start_run`, `abort`, `get_history`, conexiones/estrellas vía `CredentialStore` y `ConnectionTester`, recetas: listar/ejecutar/reanudar/deshacer) y eventos hacia la UI (`phase_started`, `step`, `slot_result`, `run_finished`). `_ejecutar_fase`, slots e historial no cambian.
- [ ] **6.3** Andamiaje del frontend (`ui_web/`: Vite + Svelte + Motion), build a `ui_web/dist` incluido en el zip del release (`build_release.py`); el pipeline (5.9) instala Node y ejecuta el build.
- [ ] **6.4** Pantallas, en este orden: primer arranque y prerrequisitos (conexiones, estrellas y enlaces de descarga, sobre el backend de 0.9) → progreso → resultados → selector (dividir los ~1.4k líneas de `selector_ui.py` en pasos) → historial → recetas (pausa QA, reanudar, deshacer).
- [ ] **6.5** Migrar a la nueva UI el aviso/progreso de actualización (5.8) y la comprobación de WebView2 como prerrequisito (pywebview entra en `requirements.txt` y el updater lo instala).
- [ ] **6.6** Eliminar `ui/*.py` (tkinter) y sus dependencias; actualizar tests de UI (`tests/test_recetas_ui.py`, …).
- [ ] **6.7** Pre-releases `v2.0.0-beta.N` a probadores; después `v2.0.0`.

### Riesgos

- Mantener dos lenguajes (Python + TypeScript): mantener el frontend pequeño y con pocas dependencias.
- WebView2 en Windows 10 antiguo: tratarlo como prerrequisito detectable.
- 6.2 toca el corazón de `run.py`; hacerlo con la UI tkinter aún funcionando detrás de la misma API para poder comparar.
