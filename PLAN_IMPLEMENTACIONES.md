# Plan de Implementaciones — Providigital_Ventas

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
- Desde v1.0.0, cada release se publica con un tag `vX.Y.Z` y lo construye el pipeline (5.9); no se sube nada a mano.
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
| Repo | Público (`NayeBP-MTP/Providigital_Ventas`, nombre final) → el updater llama a la API de GitHub sin token |
| Instalación | Por usuario (`%LOCALAPPDATA%\Programs\ProvidigitalVentas`), sin admin |
| Dependencias externas (Chrome, ODBC Driver for SQL Server) | No se empaquetan. La app las detecta y muestra el enlace de descarga; quien no tenga admin debe pedirlas a TI (fuera de alcance) |
| Red | No hay VPN corporativa; solo la VPN del cliente (donde corren las consultas). El updater **no debe bloquear la app** si GitHub no es alcanzable: timeout corto, falla en silencio y ofrece enlace manual |
| Empaquetado | PyInstaller **onedir** + instalador Inno Setup (un único `Setup.exe` para el usuario) |
| UI futura | pywebview (host Python) + frontend Vite/Svelte; Node solo en tiempo de build |
| Datos de usuario | Fuera de la carpeta de instalación, en `%LOCALAPPDATA%\ProvidigitalVentas\` (sobreviven a updates y desinstalación); en desarrollo (sin congelar) apuntan a `<repo>/data` |
| Secretos | Contraseñas en el Administrador de credenciales de Windows (vía `keyring`); el resto en `connections.json`. Nunca en texto plano en disco ni en el repo |
| Hosts de BD | El almacén se indexa por los nombres de host de `feat/recipes` (`PESOS_OFFER`, `CNFS`, `CHALLENGER`, `CUSTOMER_APP`, `PAYMENTLINK`); en `dev` se importa `BOTDB_*` → `PESOS_OFFER` |
| Estrellas del portal | Varias, con alias; las corridas referencian la estrella por alias (nunca guardan su contraseña). Futuras funciones venderán/ofertarán con estrellas específicas |

---

## Implementación 0.9 — Credenciales y estrellas administradas desde la app  (0.9.0 → 0.9.1)

**Objetivo:** Eliminar `.env` y `python-dotenv`. El usuario captura, edita y **prueba** las
conexiones a las BD y las credenciales de las estrellas del portal desde la UI, sin editores
externos ni CLI. Queda fuera de `run_config.json` y del código cualquier contraseña (incluidos
los defaults hardcodeados de `config/settings.py`, que hoy están expuestos en el repo público).

### Diseño

**Almacenamiento (`config/credentials.py`, clase `CredentialStore`)**

| Dato | Dónde |
|---|---|
| Contraseñas (hosts de BD y estrellas) | Administrador de credenciales de Windows vía `keyring` (DPAPI por usuario, sin admin). Servicio `ProvidigitalVentas`; usuario `host:<HOST>` o `estrella:<alias>` |
| Campos no secretos (servidor, usuario, driver, alias, ID de estrella) | `connections.json` en `app_data_dir()` |

API independiente de la UI (la usan hoy tkinter y mañana pywebview):
- Hosts: `get_connection(host)` (lanza `CredentialsMissing(host)` si falta), `save_connection`, `delete_connection`, `list_hosts`.
- Estrellas: `list_estrellas()`, `get_estrella(alias)` → `(id, contraseña)`, `save_estrella`, `delete_estrella`.
- Las corridas guardan en `run_config.json` solo el **alias** de la estrella; `Settings.ESTRELLA/PASSWORD` se resuelven desde el almacén al importarse.
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

**UI (tkinter, dentro de la UI actual)**: diálogo "Conexiones y estrellas" accesible desde el selector. Se abre solo cuando falta algo que la corrida necesita. Tarjeta por host (servidor, usuario, contraseña enmascarada con botón mostrar, driver como lista de `pyodbc.drivers()`, botón Probar con resultado verde/rojo y motivo) y lista de estrellas (alias, ID, contraseña). El selector reemplaza los campos de estrella/contraseña por una lista de alias. La pantalla definitiva se rehace en v2.0.0 sobre este mismo backend.

### Pasos — 0.9.0 (rama `feat/credentials`, desde `dev`)

- [ ] **0.9.1** `utils/paths.py` con `app_data_dir()` (`%LOCALAPPDATA%\ProvidigitalVentas` si `sys.frozen`; `<repo>/data` si no) — solo este helper; el resto de rutas se migra en 5.2. Más `config/credentials.py` (`CredentialStore`) con pruebas usando un backend `keyring` falso. Decidir con una prueba en un equipo restringido qué pasa si el Administrador de credenciales no está disponible (ver riesgos).
- [ ] **0.9.2** `services/connection_tester.py` con las categorías de error y el saneo de mensajes; pruebas con `pyodbc` simulado para cada categoría. Escape de valores en la cadena de conexión.
- [ ] **0.9.3** Cambiar los consumidores en `dev`: `services/offer_repository.py` y `services/agency_repository.py` (constructores), `utils/vpn_check.py` (servidor/puerto por host desde el almacén), `config/settings.py` (quitar defaults hardcodeados de estrella/contraseña; resolver por alias) y `run.py`/`ui/selector_ui.py` (pasar alias, no contraseña).
- [ ] **0.9.4** Diálogo "Conexiones y estrellas" en tkinter + compuerta previa a la corrida + apertura automática cuando faltan datos.
- [ ] **0.9.5** Importación única de lo existente al almacén (`.env`: `BOTDB_*`→`PESOS_OFFER`, `CHALLENGER_*`, `CNFS_*`; `run_config.json`: `focus_id`/`password`→estrella con alias) y oferta de borrar el `.env`. Después: quitar `python-dotenv` y los `load_dotenv()`, borrar `.env.example`, y actualizar `CLAUDE.md`, `README.md`, `Context.md` y los mensajes que mencionan `.env`.
- [ ] **0.9.6** Revisión → merge a `dev`. Hito interno **0.9.0** (sin tag ni release).

### Pasos — 0.9.1 (portar a `feat/recipes`)

Precondición: la rama `feat/recipes` debe tener su árbol de trabajo limpio (commitear antes sus cambios pendientes en `run.py` y `ui/*`).

- [ ] **0.9.7** Mergear `feat/credentials` dentro de `feat/recipes` (merge, no cherry-pick: así el futuro `merge dev` de 5b.1 no vuelve a conflictuar con estos commits).
- [ ] **0.9.8** Adaptar lo propio de recetas: `services/db.py` (`SqlServerRepository` lee del almacén con `get_connection(host_de(base))` en lugar de `<HOST>_*` del entorno; es el único punto de lectura), `utils/vpn_check.py` (la versión de recetas ya valida por host y mapea errores: unificarla con `ConnectionTester` en lugar de duplicar), docstrings de `config/databases.py`, `services/*_repository.py`, y el mensaje de `ui/selector_ui.py` que dice "revisa tu .env".
- [ ] **0.9.9** Tarjetas para los hosts `CNFS`, `CUSTOMER_APP` y `PAYMENTLINK` en el diálogo; definir qué hosts requiere cada tipo de corrida y cada receta para la compuerta previa.
- [ ] **0.9.10** Adaptar las pruebas de recetas que dependían del entorno (`tests/test_vpn_check.py`, `tests/test_offer_repository.py`, `tests/test_repositorios_insumos.py`, …) para usar un almacén falso. Revisión → hito interno **0.9.1** (sin tag).

### Riesgos

- **Almacén no disponible** (política corporativa que bloquea el Administrador de credenciales): no se cae a texto plano. Opciones a decidir en 0.9.1: credenciales solo en memoria durante la sesión (los subprocesos las reciben por entorno desde `run.py`) o bloquear con un mensaje claro.
- **Contraseña del portal ya expuesta** en el historial de git público (defaults de `config/settings.py`): quitarla del código no la borra del historial; avisar a quien administre esa cuenta para rotarla.
- **Divergencia dev ↔ recetas** en `vpn_check.py` y los repositorios: por eso 0.9.1 se hace con merge y adaptación explícita, no copiando archivos.

---

## Implementación 5 — Empaquetado, instalador y auto-update  (v1.0.0 → v1.0.x)

**Objetivo:** Que un colega descargue un `Setup.exe`, lo instale sin admin, y reciba las
versiones futuras automáticamente. **No cambia la UI** (sigue tkinter) ni el comportamiento
de los flujos CN/CF/OF.

**Base:** rama `dev` (con 0.9.0). Mantener los diffs en archivos compartidos con
`feat/recipes` (`run.py`, `conftest.py`, `config/settings.py`, `ui/*`) lo más chicos posible:
la lógica nueva va en módulos nuevos (`utils/paths.py`, `utils/updater.py`, …) y los archivos
existentes solo cambian en el punto de uso. Ver riesgos al final.

### Pasos

- [ ] **5.1** `version.py` con `__version__ = "1.0.0"` (única fuente; la leen el updater, la ventana y el instalador).
- [ ] **5.2** Migrar el resto de rutas escribibles a `app_data_dir()` (el helper ya existe desde 0.9.1) y añadir `resource_path(rel)` → `sys._MEIPASS/rel` si `sys.frozen`, ruta del repo si no (assets de solo lectura: `selfie.jpeg`, semilla del catálogo, `pytest.ini`).
  - Rutas a migrar: `run_config.json`, `run_results*.json`, las SQLite (`catalog`, `generated_*`), `allure-results`, `screenshots`, logs.
  - Archivos a tocar (confirmar con `grep`): `config/settings.py`, `utils/progress.py`, `utils/*_allocator.py`, `utils/catalog_db.py`, `utils/run_history.py`, `conftest.py`, `run.py`.
- [ ] **5.3** Lanzador de fases a prueba de congelado (`run.py`, hoy `sys.executable -m pytest`):
  - Frozen: el exe se relanza a sí mismo con `--run-pytest <args>`; al inicio de `main()`, si ese flag está presente, llama `pytest.main(args)` y termina con su código de salida.
  - No frozen: queda igual.
  - Conservar subproceso por fase, `Progress` por archivo y la muerte del árbol de procesos (abortar desde la UI).
  - Pasar a pytest `-c` (`pytest.ini` vía `resource_path`) y `--rootdir`; asegurar que `tests/`, `flows/`, `pages/` se importen.
- [ ] **5.4** Verificación de prerrequisitos (`utils/prereqs.py`): Chrome (registro `App Paths\chrome.exe`) y ODBC Driver 17/18 for SQL Server (`pyodbc.drivers()`). Si falta algo: mensaje con el enlace oficial de descarga y no se permite iniciar la corrida. Se integra al arranque de `run.py` junto a la compuerta de 0.9.
- [ ] **5.5** Quitar `webdriver-manager` y usar Selenium Manager (incluido en Selenium 4.33): en `conftest.py` pasar a `webdriver.Chrome(options=...)`. Validar que funciona con la red del cliente (descarga el driver la primera vez); si no, documentar el fallback.
- [ ] **5.6** `ProvidigitalVentas.spec` (PyInstaller, **onedir**):
  - `datas`: `data/selfie.jpeg`, `selfie.y4m` (o generarlo en el primer arranque a `app_data_dir()`), `pytest.ini`, semilla del catálogo.
  - `hiddenimports`: `tests.*`, `flows.*`, `pages.*`, `allure_pytest`, `pyodbc`, `keyring.backends.Windows`; `collect_all` de `selenium`, `allure_commons`, `cv2`.
  - Excluir lo que solo es del repo: `InsumosGen/`, logs, `captured_requests_*.json`, `debug_*.json`, docs.
  - Evaluar si `cv2` es necesario en runtime (si solo genera el video de la cámara, generarlo en build y quitar la dependencia para reducir tamaño).
  - **Criterio de aceptación:** en una VM/máquina limpia, una corrida OF, una CF y una CN completan (incluyendo capturar credenciales desde el diálogo de 0.9); abortar desde la UI mata Chrome/chromedriver.
- [ ] **5.7** `installer.iss` (Inno Setup): instalación por usuario (`PrivilegesRequired=lowest`), `AppId` fijo (instala encima), accesos directos, desinstalador, no toca `%LOCALAPPDATA%\ProvidigitalVentas\` ni el Administrador de credenciales. Salida: `ProvidigitalVentas-Setup-X.Y.Z.exe`.
- [ ] **5.8** `utils/updater.py` + integración mínima en la UI actual:
  - Al iniciar, en hilo aparte: `GET /repos/NayeBP-MTP/Providigital_Ventas/releases/latest`, timeout corto, todo en `try/except` (sin red / bloqueado por la VPN del cliente → continúa sin avisar).
  - Comparar `tag_name` con `__version__` (`packaging.version`). Si hay una más nueva: aviso con notas del release y botón **Actualizar**.
  - Descargar el `Setup.exe` a `%TEMP%`, verificar SHA-256 (archivo `.sha256` del release), lanzarlo con `/VERYSILENT /CLOSEAPPLICATIONS /RESTARTAPPLICATIONS` y cerrar la app.
  - Máx. una consulta por arranque (la API sin autenticar permite 60/h por IP); entrada "Buscar actualizaciones" y versión visible en el título.
  - Mantener el módulo **simple**: un updater roto no puede publicarse a sí mismo; el respaldo es siempre descargar el `Setup.exe` manualmente.
- [ ] **5.9** `.github/workflows/release.yml` (`windows-latest`, al hacer push de tag `v*`): instalar deps → PyInstaller → Inno Setup → SHA-256 → publicar `Setup.exe` + `.sha256` con `softprops/action-gh-release`.
- [ ] **5.10** Publicar **v1.0.0**. Revisar SmartScreen/antivirus con el exe real (sin firma es probable el aviso; si bloquea, pedir a TI que permita el hash/publisher o evaluar firma de código).
- [ ] **5.11** Publicar **v1.0.1** (cambio trivial, p. ej. nota en README) solo para **probar el auto-update de punta a punta**: instalar v1.0.0 en una máquina limpia y ver que detecta, descarga, instala y relanza v1.0.1. Hasta que esto pase, no se anuncia a los colegas.
- [ ] **5.12** Documentar en `README.md`: instalación, prerrequisitos, dónde están los datos del usuario y las credenciales, cómo publicar un release (`version.py` → commit → `git tag vX.Y.Z` → `git push --tags`).

### Riesgos

- **Conflictos con `feat/recipes`** (74 archivos, +9.6k/−1.6k vs `dev`; reescribe `tests/test_login*.py`, `run.py`, `conftest.py`, `ui/*`). Mitigación: diffs mínimos en archivos compartidos (5.2/5.3), y al terminar v1.0.x hacer `git merge dev` dentro de `feat/recipes` **antes** de mergear a `dev` (v1.1.0).
- **Antivirus/SmartScreen** pueden bloquear un exe PyInstaller sin firmar; probar temprano (5.10), no al final.
- **`/*.json` y `/data/*` están en `.gitignore`**: lo que deba empaquetarse desde `data/` se genera en build o se agrega con `git add -f`.
- **Rutas hardcodeadas no detectadas** en 5.2 aparecerán solo al correr congelado; por eso el criterio de 5.6 exige una corrida real en máquina limpia.

---

## Implementación 5b — Release de recetas  (v1.1.0)

**Objetivo:** Entregar `feat/recipes` (recetas de insumos, runner con pausa QA, UI de recetas, `run.py` con tipo receta) a los colegas **a través del auto-update**, que es la primera entrega real por ese canal.

**Precondición:** v1.0.x estable (5.11 aprobado). Las credenciales ya están portadas (0.9.1).

### Pasos

- [ ] **5b.1** Mergear `dev` dentro de `feat/recipes` y resolver conflictos (esperados en `run.py`, `conftest.py`, `config/settings.py`, `tests/test_login*.py`, `ui/*`). Nada nuevo se funcionaliza en este paso.
- [ ] **5b.2** Auditoría de congelado de lo que trae la rama: toda ruta escribible nueva pasa por `app_data_dir()` (pendientes de QA, SQLite de `cliente_id_allocator`, resultados de recetas, plantillas SQL leídas con `resource_path`); `insumos/*` y sus plantillas en `hiddenimports`/`datas`; revisar `requirements.txt` por dependencias nuevas.
- [ ] **5b.3** Confirmar que los tests de recetas corren también congelados donde aplique, y que los hosts de recetas (`CNFS`, `CUSTOMER_APP`, `PAYMENTLINK`) se pueden capturar y probar desde el diálogo de 0.9.
- [ ] **5b.4** Revisión de la persona → merge a `dev` → bump a `1.1.0` → tag → el pipeline publica → verificar que una instalación de v1.0.x se actualiza sola.

---

## Implementación 6 — Reescritura de la UI  (v2.0.0)

**Objetivo:** Reemplazar tkinter por una UI moderna (movimiento, UX cuidada, modo oscuro) sin cambiar la lógica de negocio ni el empaquetado.

**Base:** `dev` después de v1.1.0. **Decisión:** pywebview (WebView2) + frontend Vite/Svelte; Node solo en build.

### Pasos

- [ ] **6.1** *Spike descartable* (rama aparte, no se mergea): solo la pantalla de progreso en pywebview + Svelte con eventos reales de `Progress`; congelarla con PyInstaller y medir tamaño/arranque. Si falla, se evalúa Electron con lo aprendido.
- [ ] **6.2** Inversión de control en `run.py`: la UI pasa a ser el bucle principal y `run.py` expone un controlador con API (`get_catalog`, `check_prereqs`, `start_run`, `abort`, `get_history`, conexiones/estrellas vía `CredentialStore` y `ConnectionTester`, recetas: listar/ejecutar/reanudar/deshacer) y eventos hacia la UI (`phase_started`, `step`, `slot_result`, `run_finished`). `_ejecutar_fase`, slots e historial no cambian.
- [ ] **6.3** Andamiaje del frontend (`ui_web/`: Vite + Svelte + Motion), build a `ui_web/dist` incluido vía `datas` en el spec; el pipeline (5.9) instala Node y ejecuta el build.
- [ ] **6.4** Pantallas, en este orden: primer arranque y prerrequisitos (conexiones, estrellas y enlaces de descarga, sobre el backend de 0.9) → progreso → resultados → selector (dividir los ~1.4k líneas de `selector_ui.py` en pasos) → historial → recetas (pausa QA, reanudar, deshacer).
- [ ] **6.5** Migrar a la nueva UI el aviso/progreso de actualización (5.8) y la comprobación de WebView2 como prerrequisito.
- [ ] **6.6** Eliminar `ui/*.py` (tkinter) y sus dependencias; actualizar tests de UI (`tests/test_recetas_ui.py`, …).
- [ ] **6.7** Pre-releases `v2.0.0-beta.N` a probadores; después `v2.0.0`.

### Riesgos

- Mantener dos lenguajes (Python + TypeScript): mantener el frontend pequeño y con pocas dependencias.
- WebView2 en Windows 10 antiguo: tratarlo como prerrequisito detectable.
- 6.2 toca el corazón de `run.py`; hacerlo con la UI tkinter aún funcionando detrás de la misma API para poder comparar.
