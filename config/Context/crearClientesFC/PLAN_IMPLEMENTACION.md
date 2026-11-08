# Plan de implementación — sistema de recetas (rama `feat/recipes`)

Diseño y decisiones: [CREAR_CLIENTES.md](CREAR_CLIENTES.md). Este documento es el **checklist de
trabajo**: se avanza **un paso a la vez**, y cada paso se cierra con su verificación y su review
antes de pasar al siguiente.

Cada paso tiene tres casillas:

- **Impl.** — el código/documento está escrito.
- **Verif.** — se comprobó que funciona (comando o prueba indicada en el paso).
- **Review** — la persona que revisa dio el visto bueno.

**Flujo por paso:** implementar → verificar → **la persona hace el review** → **recién entonces se
commitea** → se empieza el siguiente paso. Nunca se commitea antes del review ni se avanza sin él.

Reglas de trabajo: **los commits y PRs no llevan atribución a Claude Code** (ni `Co-Authored-By`
ni "Generated with Claude Code"; ver `CLAUDE.md`, "Convenciones de git"); **los mensajes de
commit van en inglés**; un commit por paso (mensaje con el número de paso); ningún paso rompe lo ya
existente (ventas CN/CF, ofertas y agencia siguen funcionando); las pruebas contra UAT se indican
en cada paso y requieren VPN.

---

## Fase 0 — Punto de partida

### 0.1 Rama y base
- [x] Rama `feat/recipes` creada; lo de `feat/parallelization` ya está commiteado.
- [x] **Commit de los documentos de diseño** (`config/Context/crearClientesFC/`, `CLAUDE.md`,
  `REGLAS_DE_NEGOCIO.md`, `.env.example`) como primer commit de la rama (`59a5ea7`; el feature de
  ajustes de usuario de `SelectorUI`, también sin commitear, fue `3b2da83`).

---

## Fase 1 — Infraestructura sobre lo existente

### 1.1 Mapeo base → host y clase base de conexión
- **Qué:** `config/databases.py` (mapeo base → host, decisión 4) y `services/db.py` (clase base que
  resuelve host por base, lee `<HOST>_SERVER/USER/PASSWORD/DRIVER` y reintenta ante `08001`/`08S01`
  como hoy hace `OfferRepository`). Incluye `dry_run`.
- **Verificación:** prueba unitaria del mapeo (cada base resuelve su host; una base desconocida
  falla con mensaje claro).
- **Hecho:** `config/databases.py`, `services/db.py` (`SqlServerRepository`, `credenciales_de_host`,
  reintentos, `_escribir` con `dry_run`) y `tests/test_databases.py` (18 pruebas, sin red:
  `python -m pytest tests/test_databases.py`). Aún nada usa la clase base (eso es el 1.2 y 1.3).
- [x] Impl. · [x] Verif. · [x] Review

### 1.2 Migrar `OfferRepository`
- **Qué:** `services/offer_repository.py` hereda de la clase base y usa `PESOS_OFFER_*` (base
  `botDB`). Sin cambios de comportamiento.
- **Verificación:** `python -m services.offer_repository` conecta; `tests/test_oferta.py` inserta y
  verifica una oferta (UAT).
- **Hecho:** `OfferRepository` hereda de `SqlServerRepository` (base `botDB`, host `PESOS_OFFER`);
  se quitaron su `__init__` con `BOTDB_*`, `_get_connection` y `test_connection` propios;
  `insert_offer` y `delete_offer` pasan por `_escribir` (ahora soportan `dry_run`). API pública
  sin cambios (`OfferRepository()` sigue funcionando). Pruebas: `tests/test_offer_repository.py`.
- **Verificado:** 21 pruebas unitarias; `python -m services.offer_repository` conecta a UAT;
  `get_max_semana()` = 202645; `tests/test_oferta.py` con una oferta real (config temporal fuera
  de `data/`) insertó y verificó `idOferta=26110019`, que se borró después con `delete_offer`
  (comprobado que ya no existe).
- **Aviso:** `agency_repository.py` (clase que usa `BOTDB_*`), `vpn_check.py` y el `.env` actual
  (sin `BOTDB_*`) hacen que el chequeo de VPN de `run.py` y el flujo de agencia fallen hasta el 1.3.
- [x] Impl. · [x] Verif. · [x] Review (el commit `98b2125` se hizo antes del review; error de flujo)

### 1.3 Migrar `ChallengerRepository` y `utils/vpn_check.py`
- **Qué:** `services/agency_repository.py` y `utils/vpn_check.py` usan la clase base y los nombres
  por host (`CHALLENGER_*`, `PESOS_OFFER_*`). Revisar cualquier otro `os.environ[...]` de BD.
- **Verificación:** `tests/test_agencia_structure.py` (o su ejecución desde `run.py`) y el chequeo
  de VPN de `run.py` siguen funcionando (UAT).
- **Hecho:**
  - `ChallengerRepository` (base `Challenger_uat`, host `CHALLENGER`) y `BotDbAgencyRepository`
    (base `botDB`, host `PESOS_OFFER`) heredan de `SqlServerRepository`; se quitaron sus
    `__init__` con variables, `_get_connection` y `test_connection` propios (ahora con reintentos).
    Sus constructores no aceptan `dry_run`: sus escrituras aún no pasan por `_escribir`.
  - `utils/vpn_check.py`: `_host_puerto(host)` único (lee `<HOST>_SERVER`) en lugar de dos
    funciones por base; `verificar_vpn(requiere_bd, requiere_challenger)` conserva su firma.
  - Pruebas: `tests/test_vpn_check.py`.
- **Verificado:** 30 pruebas unitarias; en UAT solo lectura: `python -m services.agency_repository`
  (conecta; siguientes DM/AM Izcalli 64/4351), `verificar_vpn(True, True)` = `(True, [])`,
  `get_dm_am_combos(2075)` = 11 combos, `BotDbAgencyRepository().test_connection()` OK.
  **No** se ejecutó el alta completa de una agencia (`test_agencia_structure.py`): inserta en dos
  hosts y no cambió ninguna sentencia SQL, solo la conexión; se puede correr con rollback
  (`eliminar_agencia`) si se quiere.
- [x] Impl. · [x] Verif. · [x] Review

### 1.4 `.env.example` y referencias documentales
- **Qué:** `.env.example` con los nombres por host (sin `*_DATABASE`); actualizar las menciones de
  `BOTDB_*` en `CLAUDE.md`, `Context.md`, `ESPECIFICACIONES.md` y `REGLAS_DE_NEGOCIO.md`.
- **Verificación:** `grep -rn "BOTDB_" .` no devuelve nada fuera de `InsumosGen/`, del historial git
  y de los documentos de `crearClientesFC/` (que lo citan solo para describir el renombrado).
- **Hecho:**
  - `.env.example`: nombres por host desde `59a5ea7` (sin `*_DATABASE`); ahora incluye **los 5
    hosts** (Customer_App y PaymentLink dejaron de ir comentados). Las variables de los 3 hosts en
    uso coinciden con las del `.env` real (solo cambia el orden de los bloques).
  - Referencias a `BOTDB_*` actualizadas a `PESOS_OFFER_*` en `CLAUDE.md` (hosts, `services/db.py`
    y "Antes de correr contra botDB"), `ESPECIFICACIONES.md` (conexión y `OfferRepository`),
    `Context.md` y `REGLAS_DE_NEGOCIO.md`.
- **Verificado:** el `grep` de arriba no devuelve nada fuera de las exclusiones; tampoco quedan
  `*_DATABASE` en el código ni en los documentos.
- [x] Impl. · [x] Verif. · [x] Review

### 1.5a Flujos compartidos y de CN a `flows/`
- **Qué:** mover de `tests/test_login.py` a `flows/` los flujos compartidos
  (`flows/venta_comun.py`: `flujo_identidad_a_otp`, `flujo_metodo_entrega`,
  `flujo_beneficiario_a_finalizar`, `esperar_request_foto`, `obtener_folio_finalizacion` y sus
  constantes de espera) y el de CN (`flows/venta_cn.py`: `ejecutar_venta_cn`). `test_login.py`
  queda con la clase de test (ciclos, resumen y `run_results.json`). Movimiento **mecánico**: el
  cuerpo de las funciones no cambia; solo pierden el guion bajo inicial las que ahora cruzan
  módulos. `test_login_cf.py` ya no importa de `tests.test_login`, sino de `flows.venta_comun`.
- **Verificación:** AST de las 9 funciones igual al original salvo renombres, sin imports sin usar
  ni nombres sin definir; los dos tests se recolectan; una venta **CN** real en UAT con el mismo
  resultado que antes.
- **Hecho:** `flows/__init__.py`, `flows/venta_comun.py` (885 líneas), `flows/venta_cn.py` (93);
  `tests/test_login.py` pasó de 1050 a 98 líneas; `test_login_cf.py` importa de
  `flows.venta_comun`. Renombres: `_flujo_identidad_a_otp` → `flujo_identidad_a_otp`,
  `_flujo_metodo_entrega` → `flujo_metodo_entrega`,
  `_flujo_beneficiario_a_finalizar` → `flujo_beneficiario_a_finalizar`,
  `_esperar_request_foto` → `esperar_request_foto`, `_obtener_folio_finalizacion` →
  `obtener_folio_finalizacion`, `_ejecutar_venta` → `ejecutar_venta_cn`.
- **Verificado:** las 9 funciones tienen el mismo AST que en el original salvo los renombres; sin
  imports sin usar ni nombres sin definir; los 2 tests se recolectan; 30 pruebas unitarias OK.
- **Venta CN real en UAT: investigada y resuelta.** Al principio no se podía completar ni con el
  código original (3 corridas fallaban igual en `Obtener OTP Legalario`). Causas encontradas
  (detalle en `Context.md` sección 10):
  1. Legalario cambió el SDK a `/sdk/invites/send-code-new`, que ya no devuelve `data.otp_code`.
     Arreglo: `NetworkInterceptor.solicitar_otp_legalario()` lo pide al endpoint anterior
     (`/sdk/invites/send-code`, que sigue devolviéndolo). Pruebas: `tests/test_network_interceptor.py`.
  2. En "Revisa tus documentos" un segundo click inmediato en "Estoy de acuerdo" se perdía.
     Arreglo: esperar a que el primer documento diga "Revisado" (`_esperar_documentos_revisados`).
  - Resultado: 3 ventas CN completas seguidas (Izcalli 335, BBVA, con seguro); la última con el
    código final y sin sondas. El `folio` sigue `None` en CN (pendiente para el 1.6).
  - Estos arreglos van en el mismo commit que el movimiento (tocan `flows/venta_comun.py` y
    `services/network_interceptor.py`); se pueden separar si se prefiere.
- [x] Impl. · [x] Verif. · [ ] Review

### 1.5b Flujo de CF a `flows/`
- **Qué:** mover `_ejecutar_venta_cf`, `_insertar_oferta_cf`, `_construir_oferta_cf`,
  `_limite_monto_agencia`, `_monto_para_agencia` y `_capturar_diagnostico_falla` de
  `tests/test_login_cf.py` a `flows/` (`venta_cf.py` y `oferta_cf.py`); `test_login_cf.py` y
  `test_oferta.py` quedan como envoltorios delgados (`test_oferta.py` ya no importa de otro test).
- **Verificación:** igual que 1.5a, con una venta **CF** real y `test_oferta` en UAT.
- **Resultado:** movido sin cambiar el cuerpo de las funciones (AST idéntico, 7 funciones/clases;
  renombradas sin guion bajo). Nuevos: `flows/oferta_cf.py` y `flows/venta_cf.py`.
  Verificado en UAT: venta CF completa (Izcalli 335, BBVA, oferta 26110020, 392 s) y `test_oferta`
  (oferta 26110021 insertada y verificada, luego borrada). El `folio` sigue `None` también en CF.
- [x] Impl. · [x] Verif. · [x] Review

### 1.6 Resultado de las ventas
- **Qué:** `VENTA_CN` y `VENTA_CF` devuelven nombre de la INE, agencia, `con_seguro`, hora de
  inicio (tomada con `SYSDATETIME()` del host Pesos_Offer, no del reloj local) y `numeroContrato`.
- **Verificación (UAT):** con una venta real, comparar el `folio` capturado contra el
  `numeroContrato` que aparece en `ExpedienteCliente`. Resultado anotado en `CREAR_CLIENTES.md`
  (sección 6, punto 4): si el folio es fiable se usa; si no, se localiza por nombre de la INE +
  `FechaFinalizacion`.
- **Resultado:** `ejecutar_venta_cn` ahora devuelve un `ResultadoVenta` y `ejecutar_venta_cf` suma
  esos campos a su dict (`flows/resultado_venta.py`, `services/originacion_repository.py`; los
  resultados `run_results*.json` los incluyen: `numero_contrato`, `nombre_ine`, `inicio`,
  `agencia_label`, `con_seguro`, `id_expediente`...). La hora de inicio y la localización son
  *best effort*: sin BD la venta no falla, solo queda `numero_contrato = None`.
  Verificado en UAT: CN (contrato 240021110) y CF (240021111, folio capturado = contrato); la primera
  CF falló por el facematch intermitente (oferta huérfana 26110022 borrada). Pruebas:
  `tests/test_resultado_venta.py`. Decisión y hallazgo del folio en `CREAR_CLIENTES.md` §6.4.
- [x] Impl. · [x] Verif. · [x] Review

---

## Fase 2 — Módulos de insumo

### 2.1 Plantillas como datos
- **Qué:** los tres INSERT (`Customer_Table`, `Agreement_Table`, `Customer_Address_Table`) como
  diccionarios columna → valor por defecto; los `.sql` quedan como referencia.
- **Verificación:** prueba que compara las columnas de cada diccionario contra las del `.sql`.
- **Resultado:** `insumos/plantillas.py` con `CUSTOMER` (155 columnas), `AGREEMENT` y
  `CUSTOMER_ADDRESS` (dict columna → valor por defecto, en el orden del INSERT) más el nombre
  completo de cada tabla (`*_TABLA`). Se generó leyendo los `.sql`, que quedan como referencia; los
  comentarios `** ...` de los `.sql` (qué campos son "de la venta") se conservaron como comentarios
  de línea. `tests/test_plantillas.py` compara columnas y orden contra cada `.sql`.
- [x] Impl. · [x] Verif. · [x] Review

### 2.2 `ContextoVenta`, interfaz de módulo y log de operaciones
- **Qué:** dataclass `ContextoVenta` (con carga perezosa de expediente y montos), interfaz común de
  módulo (idempotente, `dry_run`), y el log por operación en `data/` (host, tabla, llave, valor
  anterior).
- **Verificación:** pruebas unitarias del contexto (con/sin seguro, montos en `NULL`/`0` fallan) y
  del log.
- **Resultado:** `insumos/contexto.py` (`ContextoVenta` con carga perezosa vía una `fuente`
  inyectable, `elegir_montos`, `ErrorContexto`), `insumos/modulo.py` (clase abstracta `Modulo`) e
  `insumos/log_operacion.py` (`LogOperacion`: un `data/insumos/<contrato>.jsonl` por operación, con
  marcas `modulo_iniciado`/`modulo_completado` para reanudar y escrituras `insert`/`update`/`delete`
  que se recorren al revés para deshacer). `data/` ya está en `.gitignore`.
  `ContextoVenta.desde_resultado_venta` arranca desde el `ResultadoVenta` del 1.6.
- **Pendiente de validar en el 2.3** (la VPN estaba caída al hacer el 2.2): los nombres de columna
  de `ExpedienteOferta` y la llave `ExpedienteCliente.IdExpedienteOferta` están tomados del diseño;
  se comprueban con lecturas reales cuando exista la `fuente` en `OriginacionRepository`.
- [x] Impl. · [x] Verif. · [x] Review

### 2.3 Repositorios `Originacion` y `CNFS`
- **Qué:** `OriginacionRepository` (localizar expediente por contrato / id / nombre de la INE +
  fecha, leer `ExpedienteOferta`, actualizar nombre/RFC, `Cliente`, `IdPaso`) y `CnfsRepository`
  (inserts/updates de Customer, Agreement y Address; las tres altas de CNFS en una transacción).
- **Verificación:** lecturas reales en UAT; escrituras en `dry_run`.
- **Resultado:** `OriginacionRepository` (`services/originacion_repository.py`): `leer_expediente`
  (por contrato o id), `buscar_por_nombre_ine`, `buscar_venta_finalizada`, `leer_montos`,
  `max_cliente_con_prefijo`, `actualizar_nombre_rfc` / `actualizar_cliente` / `actualizar_id_paso`
  (con `dry_run`); es la `fuente` de `ContextoVenta`. `CnfsRepository` (`services/cnfs_repository.py`):
  `agreement_existe`, `customer_id_de_agreement`, `customer_existe`, `max_customer_id_con_prefijo`,
  `insertar_agreement`, `insertar_cliente_y_direccion` (Customer + Address en una transacción, vía
  el nuevo `SqlServerRepository._escribir_transaccion`) y `actualizar_customer_id_agreement`. Los
  INSERT se arman de las plantillas del 2.1 (`sentencia_insert`).
- **Hallazgos de las lecturas reales (UAT, 07/11/2026):**
  - `ExpedienteCliente.IdExpedienteOferta` es **NULL en las 7206 filas**; el vínculo es
    `ExpedienteOferta.IdExpedienteCliente` (casi siempre una fila; se toma la más reciente). Se
    corrigió `ContextoVenta` y la `fuente` (`leer_montos(id_expediente)`). Los nombres de columna de
    montos del diseño son correctos.
  - Montos leídos para dos ventas reales con/sin seguro (p. ej. contrato 240021110: 11028.61 /
    10520.39 de monto, 589.36 / 562.26 de primer pago, 336.75 / 321.23 de pago semanal).
  - En una venta **CF** el expediente trae el nombre de la INE (`NAYELI BENITEZ PEREZ`) con el RFC y
    la fecha de nacimiento de la oferta (`GURC...`, 1996-09-07): justo lo que corrige
    `RENOMBRAR_CLIENTE`. En CN el RFC sí coincide con la INE.
  - `max_cliente_con_prefijo` / `max_customer_id_con_prefijo` funcionan (CF de hoy: `2075261100023`;
    sin clientes CN de hoy: `None` → `001`). Contratos de las ventas nuevas: no existen en
    `Agreement_Table` (`agreement_existe` = False); uno histórico sí, con `Customer_Id = 0`.
  - `FechaFinalizacion` es `datetime` (redondea a 3.3 ms): buscar con `desde` igual a la hora exacta
    de un expediente lo deja fuera; usar la hora de inicio de la venta.
- **Verificación:** lecturas reales en UAT (arriba) + `tests/test_repositorios_insumos.py`
  (escrituras en `dry_run`, 79 pruebas unitarias pasan). Ninguna escritura real en este paso.
- [x] Impl. · [x] Verif. · [x] Review

### 2.4 Módulo `RENOMBRAR_CLIENTE`
- **Qué:** nombre mexicano aleatorio + RFC coherente (partes de `MexicanNames.generar`, no partir
  el nombre completo).
- **Verificación:** unitaria (RFC coincide con nombre y fecha de nacimiento); UAT sobre un
  expediente de prueba, con log y verificación del valor anterior.
- **Resultado:** `insumos/modulos/renombrar_cliente.py` (`RenombrarCliente`). Genera la persona con
  `MexicanNames.generar`, deriva el RFC de sus partes y de `FechaNacimiento` (no se toca), anota en
  el log el valor anterior y el nuevo (incluida la `persona`, que `REGISTRO_CLIENTE` usará para
  `Forename`/`Surname`) **antes** de escribir, y deja `ctx.persona`. Idempotente: si el log ya trae
  un renombrado y el expediente conserva ese nombre, lo omite y recupera la `persona` del log.
  `Modulo._es_dry_run` obliga a que `dry_run` del módulo y de sus repositorios coincidan (un módulo
  en dry_run con repositorio real escribiría de verdad). En dry_run no se escribe el log.
- **Verificación:** `tests/test_renombrar_cliente.py` (RFC coherente con nombre y fecha,
  idempotencia, dry_run, log) y UAT real sobre el expediente de prueba 7331 (venta CF
  240021111): `NAYELI BENITEZ PEREZ / GURC9609067WA` → `JOSÉ LUIS PÉREZ RODRÍGUEZ / PERJ960907EL7`
  (RFC con la fecha 960907, solo cambiaron nombre y RFC), segunda ejecución sin cambios, y
  restauración al valor original usando solo el log. El expediente quedó como estaba.
- [x] Impl. · [x] Verif. · [x] Review

### 2.5 Módulo `CREAR_ID_CLIENTE`
- **Qué:** número de 13 dígitos (`AAMMDD + colaborador + 02 + NNN`), consecutivo = mayor de hoy en
  BD + 1 (revisa `ExpedienteCliente.Cliente` y `Customer_Table.Customer_Id`), reservado con un
  allocator SQLite; escribe `ExpedienteCliente.Cliente`.
- **Verificación:** unitaria del formato y del consecutivo (`001` si no hay); prueba de
  concurrencia (dos reservas simultáneas no repiten); UAT.
- **Resultado:** `insumos/modulos/crear_id_cliente.py` (`CrearIdCliente`, `prefijo_cliente`) y
  `utils/cliente_id_allocator.py` (`ClienteIdAllocator`, SQLite `data/generated_cliente_ids.sqlite3`,
  transacción `EXCLUSIVE`). `NNN` = mayor entre `ExpedienteCliente.Cliente`, `Customer_Table.Customer_Id`
  y lo ya reservado + 1 (`001` si no hay; tope 999 por colaborador y día). Si el expediente ya trae
  `Cliente` ≠ 0 (CF, o CN ya procesado) lo usa sin escribir ni reservar. Registra en el log el `Cliente`
  anterior (0) antes de escribir. En `dry_run` calcula el número sin reservarlo ni loguear.
  El colaborador sale de `Settings.NUMERO_COLABORADOR` (1 o 2 dígitos; se rellena a 2); si falta,
  falla con un mensaje claro antes de reservar o escribir. **`data/run_config.json` no tiene
  `numero_colaborador` hoy: hay que capturarlo en los Ajustes de usuario de la UI.**
- **Corrección al diseño y al 2.3:** el prefijo `AAMMDD + CC + 02` tiene **10** dígitos (el diseño decía
  11). Las consultas `max_cliente_con_prefijo` / `max_customer_id_con_prefijo` del 2.3 usaban
  `prefijo × 100`; ahora usan `prefijo × 1000 .. + 999` (con prueba). Documentos corregidos.
- **Verificación:** `tests/test_crear_id_cliente.py` (formato, `001`, mayor entre las dos tablas,
  CF sin escribir, concurrencia con 6 hilos × 10 reservas sin repetir, `dry_run`, colaborador
  inválido). UAT real sobre el expediente de prueba 7329 (CN, `Cliente = 0`), con un allocator
  temporal y colaborador `04`: generó `2611070402001`, lo escribió, una segunda ejecución lo
  reconoció sin escribir, y se restauró a `0` solo con el log. Consultas de prefijo comprobadas
  contra datos reales (`2075261100` → `2075261100023`; `2101655328` → `2101655328900`).
- [x] Impl. · [x] Verif. · [x] Review

### 2.6 Módulo `AGREEMENT`
- **Qué:** INSERT en `Agreement_Table` con los campos de la sección 2.2 del diseño (incluidos los
  cinco montos alineados con la venta).
- **Verificación:** `dry_run` imprime el INSERT esperado para venta con y sin seguro; UAT con un
  contrato de prueba.
- **Resultado:** `insumos/modulos/agreement.py` (`Agreement`, `construir_agreement`). Parte de la
  plantilla de 76 columnas y sobrescribe solo los campos de la tabla del diseño (los cinco montos
  alineados con la venta incluidos); el resto queda como la plantilla. Fechas `AAAA-MM-DD 00:00:00`
  de hoy, `Actual_Paid_Up_Week` con `OfferIdAllocator.calcular_semana` (corte en miércoles),
  `Customer_Id` = `Cliente` del contexto o `0`. Idempotente: si el contrato ya está en
  `Agreement_Table` no inserta. Anota el INSERT en el log (`Agreement_Num`) antes de escribir.
- **Verificación:** `tests/test_agreement.py` (columnas y orden, valores con/sin seguro, fechas y
  semana, plantilla intacta, montos en cero fallan sin insertar, `dry_run`, idempotencia). UAT con el
  contrato de prueba 240021110: `dry_run` con y sin seguro (p. ej. 10520.39 / 11028.61 de monto,
  562.26 / 589.36 de primer pago, 321.23 / 336.75 de pago semanal), INSERT real con seguro leído de
  vuelta en `CNFS_uat` (`Customer_Id = 0`, `AC`, semana 202645), segunda ejecución omitida y borrado
  de la fila usando solo el log. `Agreement_Table` quedó sin el contrato.
- [x] Impl. · [x] Verif. · [x] Review

### 2.7 Módulo `REGISTRO_CLIENTE`
- **Qué:** INSERT en `Customer_Table` y `Customer_Address_Table` en una transacción;
  `Customer_Status_Code` `CC`/`AA` según el tipo de venta.
- **Verificación:** `dry_run` para CF y CN; UAT.
- **Resultado:** `insumos/modulos/registro_cliente.py` (`RegistroCliente`, `construir_customer`,
  `construir_direccion`, `persona_del_log`). Parte de las plantillas (155 y 27 columnas) y sobrescribe
  los campos de la tabla del diseño (`Forename`/`Surname` salen de `ctx.persona`, no de partir el
  nombre; segmento = 4 primeros dígitos de la agencia; fechas de ingreso +7 días;
  `Customer_Status_Code` `CC`/`AA`). Si el expediente no trae domicilio se conserva el de la plantilla.
  Customer y Address se insertan en **una transacción** (`insertar_cliente_y_direccion`); en el log
  quedan en orden de alta, así que deshacer borra primero la dirección y luego el cliente. Requiere
  `Cliente` ≠ 0 y la `persona` (del contexto o, al reanudar en otro proceso, del log de
  `RENOMBRAR_CLIENTE`); si falta cualquiera, falla pidiendo el módulo que corresponde. Idempotente:
  si el cliente ya está en `Customer_Table` no inserta.
- **Verificación:** `tests/test_registro_cliente.py` (14 casos: columnas, valores, CF/CN, sin
  domicilio, plantillas intactas, transacción, log y orden de deshacer, precondiciones, recuperar la
  persona del log, idempotencia, `dry_run`). UAT con la venta CF de prueba (expediente 7331,
  `Cliente 2075261100023`): `dry_run` CF y CN (`CC`/`AA`), alta real leída de vuelta en
  `Customer_Table` y `Customer_Address_Table` (segmento 2075, semana 202645, domicilio del
  expediente), segunda ejecución omitida, y borrado de ambas filas usando solo el log.
- [x] Impl. · [x] Verif. · [x] Review

### 2.8 Módulo `ACTUALIZAR_ID_CLIENTE`
- **Qué:** propaga `Cliente` a `Agreement_Table.Customer_Id` (y a `ExpedienteCliente` solo si
  falta).
- **Verificación:** `dry_run`; UAT sobre un contrato creado con `Customer_Id = 0`.
- **Resultado:** `insumos/modulos/actualizar_id_cliente.py` (`ActualizarIdCliente`). Pone el
  `Cliente` del contexto en `Agreement_Table.Customer_Id` (CNFS) y, solo si todavía no lo tiene, en
  `ExpedienteCliente.Cliente` (Pesos_Offer); el expediente se relee de la BD porque `ctx.cliente` puede
  venir de CREAR_ID_CLIENTE o de un valor dado a mano. Anota cada update (valor anterior 0) antes de
  escribir. Requiere `Cliente` ≠ 0 y que AGREEMENT ya haya corrido; si no, falla pidiendo el módulo.
  **No pisa** un valor distinto de 0: si el contrato o el expediente ya traen otro cliente falla
  **antes de escribir nada** (las dos comprobaciones preceden a la primera escritura, así no queda
  una mitad actualizada). Idempotente.
- **Verificación:** `tests/test_actualizar_id_cliente.py` (10 casos: ambos updates, log, solo agreement
  cuando CREAR_ID ya escribió el expediente, idempotencia, precondiciones, no pisar sin escribir
  nada, `dry_run`). UAT sobre el contrato de prueba 240021110 (CN): sin AGREEMENT lo rechaza;
  AGREEMENT real con `Customer_Id = 0`; `Cliente` dado a mano → quedaron `Customer_Id` y `Cliente` en
  `2611080402001`; segunda ejecución sin escrituras; un cliente distinto se rechaza sin tocar nada; y
  se deshizo todo desde el log (fila de Agreement borrada, expediente de vuelta a `Cliente = 0`).
- [x] Impl. · [x] Verif. · [x] Review

### 2.9 Módulo `PASO_22_DISPERSADO`
- **Qué:** `ExpedienteCliente.IdPaso` ← `22`, guardando el valor anterior.
- **Verificación:** `dry_run`; UAT (con `Cliente` en `0` y con valor).
- **Resultado:** `insumos/modulos/paso_22_dispersado.py` (`Paso22Dispersado`). UPDATE de
  `ExpedienteCliente.IdPaso` a 22; el `IdPaso` anterior se lee de la BD en cada ejecución (cambia con
  el avance de la venta) y se anota en el log antes de escribir. Solo exige que exista el expediente
  (`Cliente` puede ser 0). No cambia ningún otro dato. Idempotente: si ya está en 22 no escribe.
- **Verificación:** `tests/test_paso_22_dispersado.py` (7 casos: con `Cliente` 0 y con valor, log del
  paso anterior, solo `IdPaso`, idempotencia, `dry_run`). UAT sobre las ventas de prueba 7329 (CN,
  `Cliente = 0`) y 7331 (CF, `Cliente 2075261100023`): `IdPaso` 30 → 22 sin cambiar ningún otro dato
  del expediente, segunda ejecución omitida, y restauración a 30 usando solo el log.
  *(Las ventas terminan en `IdPaso = 30`; el diseño pendiente de revisar si dispersar requiere más
  cambios sigue en `CREAR_CLIENTES.md`, sección 6.)*
- [x] Impl. · [x] Verif. · [x] Review

---

## Fase 3 — Recetas y ejecución

### 3.1 Runner de recetas
- **Qué:** las 6 recetas declaradas como datos; ejecución módulo a módulo con el `ContextoVenta`;
  `PAUSA_QA` como estado persistido (`data/insumos_pendientes.json`).
- **Verificación:** recetas ejecutadas en `dry_run` de punta a punta (sin venta, con
  `numeroContrato` dado).
- **Resultado:**
  - `insumos/recetas.py`: `Receta` (inmutable) y `RECETAS` con las seis recetas como datos
    (`CN_REGISTRO_INTERMEDIO`, `CN_REGISTRADO`, `CN_REGISTRO_DISPERSADO`, `CN_REGISTRADO_DISPERSION`,
    `CF_DISPERSADO`, `CF_REGISTRADO`); `PAUSA_QA` es un paso más y `sin_pausa_qa()` devuelve la misma
    receta sin él.
  - `insumos/runner.py`: `RunnerRecetas.ejecutar(receta, ctx)` corre los módulos en orden anotando en el
    log `modulo_iniciado`/`modulo_completado`; siempre arranca en el primer paso no completado, así que
    volver a llamarlo retoma una operación a medias. Valida que el tipo de la receta coincida con la
    venta (CN/CF) y que el contexto traiga `numero_contrato`. Una falla se guarda (`fallida`, módulo y
    mensaje) y detiene la receta. `fabrica_por_defecto(dry_run)` arma los módulos con repositorios que
    comparten `dry_run`.
  - `insumos/pendientes.py`: `PendientesStore` (`data/insumos_pendientes.json`, escritura atómica) con los
    estados `en_curso`/`esperando_qa`/`fallida`/`completada`; `pendientes()` devuelve los retomables.
  - **`PAUSA_QA` es un estado persistido:** la receta termina con `esperando_qa` guardando lo que QA
    necesita (`numero_contrato`, fecha de nacimiento y nombre); `continuar_tras_qa(operacion_id)` marca la
    pausa cumplida en el log y sigue desde el paso siguiente, también desde un proceso nuevo (el contexto
    se reconstruye con `ContextoVenta.a_dict`/`desde_dict` y lo demás se recarga de la BD).
  - Se agregó `ContextoVenta.simulado`: en `dry_run` AGREEMENT marca que "hizo" su alta para que
    ACTUALIZAR_ID_CLIENTE no exija un contrato que solo se simuló (fuera de `dry_run` no cuenta).
  - En `dry_run` no se persiste nada (ni log ni pendientes) y la pausa se atraviesa para ver la receta
    completa. Artefacto esperado: en las recetas 1 y 3 el `dry_run` lista dos UPDATE de `Cliente` (de
    CREAR_ID y de ACTUALIZAR) porque el primero no se escribe de verdad; en una ejecución real
    ACTUALIZAR lo encuentra ya escrito y solo toca `Agreement_Table`.
- **Verificación:** `tests/test_runner_recetas.py` (21 casos: las seis recetas contra el diseño, orden y
  log, tipo y contrato, pausa y su persistencia, retomar tras QA desde un runner nuevo sin repetir lo
  anterior, falla y reanudación en el módulo que falló, `dry_run` sin persistencia, almacén) y las 172
  pruebas unitarias. UAT: las seis recetas en `dry_run` de punta a punta con módulos reales y lecturas
  reales (CN sobre el contrato 240021110 y CF sobre 240021111, con `numeroContrato` dado y sin venta),
  todas `completada` con las sentencias esperadas (de 4 a 8 por receta), y la BD idéntica antes y después
  (nombre, RFC, `Cliente`, `IdPaso`, contratos y cliente en CNFS). La ejecución real de punta a punta con
  pausa y fallas forzadas queda para el 3.2.
- [x] Impl. · [x] Verif. · [x] Review

### 3.2 Reanudar y deshacer
- **Qué:** reanudar desde el primer módulo no completado (prioridad); deshacer recorriendo el log
  en orden inverso; deshacer automático solo si falla antes de `PAUSA_QA` o del último módulo.
- **Verificación:** forzar una falla en cada módulo y comprobar reanudar y deshacer (UAT).
- **Resultado:**
  - **Reanudar** (prioridad): `RunnerRecetas.reanudar(operacion_id)` (o `ejecutar` otra vez) retoma en el primer
    módulo no completado; no repite nada porque los módulos son idempotentes. Una operación deshecha no se
    reanuda: pide ejecutar la receta desde el principio.
  - **Deshacer** (`insumos/deshacer.py`, `Deshacedor`; `RunnerRecetas.deshacer`): recorre el log vigente en
    orden inverso. `insert` → DELETE (si ya no existe, se omite); `update` → vuelve al valor anterior
    **solo si la BD aún tiene el valor que escribió el módulo**; si alguien más lo cambió (p. ej. QA) no
    se pisa y queda como `conflicto` en el resultado. Es idempotente, falla ante una tabla desconocida
    (no la ignora) y en `dry_run` solo informa. Al terminar anota la marca `deshecho` en el log
    (`LogOperacion.vigentes()`: el historial nunca se borra, solo cuenta lo posterior a la última marca),
    de modo que la receta puede ejecutarse de nuevo desde cero. Estado `deshecha` en el almacén (no se
    ofrece para retomar). Nuevos en `CnfsRepository`: `address_existe`, `borrar_agreement`,
    `borrar_customer`, `borrar_address`.
  - **Deshacer automático** (`auto_deshacer`, activado por defecto): solo si la falla ocurre **antes de
    `PAUSA_QA`** (o antes del último módulo en las recetas sin pausa). Pasada la pausa, o en el último
    módulo, el estado parcial se conserva (`fallida`, retomable). Un insumo terminado nunca se borra solo.
  - `fabrica_por_defecto` acepta repositorios y allocator inyectados (para pruebas).
- **Verificación:** `tests/test_deshacer.py` (27 casos con los módulos reales sobre una BD en memoria: falla
  forzada en cada módulo antes y después de su efecto, deshacer automático antes de la pausa, conservar y
  reanudar tras la pausa sin duplicar nada, recetas sin pausa, deshacer a demanda, orden inverso,
  idempotencia, conflicto, `dry_run`, tabla desconocida) y las 199 pruebas unitarias. **UAT real** (módulos y
  BD reales, contratos de prueba 240021110 CN y 240021111 CF, restaurando y comprobando la BD tras cada caso):
  - CN con pausa, falla en cada uno de los 3 módulos **previos** a la pausa, antes y después de su efecto
    (6 casos): se deshizo sola y la BD quedó idéntica a la original.
  - CN, falla en cada uno de los 3 módulos **posteriores** a la pausa, antes y después del efecto (6
    casos): estado parcial conservado, `reanudar` la completó y quedó consistente (`Cliente` de 13 dígitos
    igual en expediente y `Agreement_Table`, cliente y dirección en CNFS, `IdPaso` 22), y `deshacer` dejó la
    BD como estaba sin omisiones.
  - CF sin pausa: falla en `AGREEMENT` (deshecha sola) y en `REGISTRO_CLIENTE` (conservada y reanudada), antes
    y después del efecto (4 casos).
  - Operación completa con pausa persistida (nombre, contrato y fecha de nacimiento para QA) y retomada desde
    un runner nuevo; `deshacer` revirtió 6 escrituras y una segunda vez no encontró nada; se volvió a ejecutar
    la receta desde cero. Estado final == original.
- [x] Impl. · [x] Verif. · [x] Review

### 3.3 Línea de comandos
- **Qué:** ejecutar una receta, reanudar o deshacer sin la UI (para QA), p. ej.
  `python -m recetas <receta> --contrato N`, `... reanudar`, `... deshacer`.
- **Verificación:** las 6 recetas desde la terminal contra un contrato de prueba (UAT).
- [ ] Impl. · [ ] Verif. · [ ] Review

### 3.4 `run.py`: tipo `RECETA`
- **Qué:** generalizar `ORDEN_TIPOS`, `TEST_FILE_BY_TIPO_CLIENTE` y las etiquetas de
  `_ejecutar_fase`; test delgado de recetas; resultados e historial.
- **Verificación:** una receta de punta a punta (venta + insumo) desde `run.py`; los tipos
  `OF`/`CF`/`CN`/`AGENCIA` siguen igual.
- [ ] Impl. · [ ] Verif. · [ ] Review

### 3.5 UI
- **Qué:** panel de recetas en `SelectorUI`; panel "Esperando QA" con botón "QA confirmó,
  continuar" en `ProgressUI`; "Retomar operaciones pendientes" al abrir; acciones de deshacer.
- **Verificación:** flujo completo con pausa: cerrar la ventana en pausa, reabrir y retomar.
- [ ] Impl. · [ ] Verif. · [ ] Review

### 3.6 Cierre documental
- **Qué:** actualizar `Context.md`, `ESPECIFICACIONES.md` y `CLAUDE.md` (arquitectura, comandos,
  recetas); marcar el diseño como implementado en `CREAR_CLIENTES.md`.
- [ ] Impl. · [ ] Review
