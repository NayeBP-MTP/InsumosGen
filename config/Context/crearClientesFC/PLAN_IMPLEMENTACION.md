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
- [ ] Impl. · [ ] Verif. · [ ] Review

### 1.4 `.env.example` y referencias documentales
- **Qué:** `.env.example` con los nombres por host (sin `*_DATABASE`); actualizar las menciones de
  `BOTDB_*` en `CLAUDE.md`, `Context.md`, `ESPECIFICACIONES.md` y `REGLAS_DE_NEGOCIO.md`.
- **Verificación:** `grep -rn "BOTDB_" .` no devuelve nada fuera de `InsumosGen/`/historial git.
- [ ] Impl. · [ ] Verif. · [ ] Review

### 1.5 Sacar los flujos de venta de `tests/`
- **Qué:** mover los flujos compartidos (`_flujo_metodo_entrega`, `_flujo_identidad_a_otp`,
  `_flujo_beneficiario_a_finalizar`, `_ejecutar_venta`, `_ejecutar_venta_cf`, `_insertar_oferta_cf`
  y auxiliares) a un módulo propio (`flows/`). `test_login.py`, `test_login_cf.py` y
  `test_oferta.py` quedan como envoltorios delgados; ya no se importa de un test a otro.
- **Verificación (UAT):** una venta **CN** y una **CF** completas desde `run.py` con el mismo
  resultado que antes; `test_oferta` sin cambios.
- [ ] Impl. · [ ] Verif. · [ ] Review

### 1.6 Resultado de las ventas
- **Qué:** `VENTA_CN` y `VENTA_CF` devuelven nombre de la INE, agencia, `con_seguro`, hora de
  inicio (tomada con `SYSDATETIME()` del host Pesos_Offer, no del reloj local) y `numeroContrato`.
- **Verificación (UAT):** con una venta real, comparar el `folio` capturado contra el
  `numeroContrato` que aparece en `ExpedienteCliente`. Resultado anotado en `CREAR_CLIENTES.md`
  (sección 6, punto 4): si el folio es fiable se usa; si no, se localiza por nombre de la INE +
  `FechaFinalizacion`.
- [ ] Impl. · [ ] Verif. · [ ] Review

---

## Fase 2 — Módulos de insumo

### 2.1 Plantillas como datos
- **Qué:** los tres INSERT (`Customer_Table`, `Agreement_Table`, `Customer_Address_Table`) como
  diccionarios columna → valor por defecto; los `.sql` quedan como referencia.
- **Verificación:** prueba que compara las columnas de cada diccionario contra las del `.sql`.
- [ ] Impl. · [ ] Verif. · [ ] Review

### 2.2 `ContextoVenta`, interfaz de módulo y log de operaciones
- **Qué:** dataclass `ContextoVenta` (con carga perezosa de expediente y montos), interfaz común de
  módulo (idempotente, `dry_run`), y el log por operación en `data/` (host, tabla, llave, valor
  anterior).
- **Verificación:** pruebas unitarias del contexto (con/sin seguro, montos en `NULL`/`0` fallan) y
  del log.
- [ ] Impl. · [ ] Verif. · [ ] Review

### 2.3 Repositorios `Originacion` y `CNFS`
- **Qué:** `OriginacionRepository` (localizar expediente por contrato / id / nombre de la INE +
  fecha, leer `ExpedienteOferta`, actualizar nombre/RFC, `Cliente`, `IdPaso`) y `CnfsRepository`
  (inserts/updates de Customer, Agreement y Address; las tres altas de CNFS en una transacción).
- **Verificación:** lecturas reales en UAT; escrituras en `dry_run`.
- [ ] Impl. · [ ] Verif. · [ ] Review

### 2.4 Módulo `RENOMBRAR_CLIENTE`
- **Qué:** nombre mexicano aleatorio + RFC coherente (partes de `MexicanNames.generar`, no partir
  el nombre completo).
- **Verificación:** unitaria (RFC coincide con nombre y fecha de nacimiento); UAT sobre un
  expediente de prueba, con log y verificación del valor anterior.
- [ ] Impl. · [ ] Verif. · [ ] Review

### 2.5 Módulo `CREAR_ID_CLIENTE`
- **Qué:** número de 13 dígitos (`AAMMDD + colaborador + 02 + NNN`), consecutivo = mayor de hoy en
  BD + 1 (revisa `ExpedienteCliente.Cliente` y `Customer_Table.Customer_Id`), reservado con un
  allocator SQLite; escribe `ExpedienteCliente.Cliente`.
- **Verificación:** unitaria del formato y del consecutivo (`001` si no hay); prueba de
  concurrencia (dos reservas simultáneas no repiten); UAT.
- [ ] Impl. · [ ] Verif. · [ ] Review

### 2.6 Módulo `AGREEMENT`
- **Qué:** INSERT en `Agreement_Table` con los campos de la sección 2.2 del diseño (incluidos los
  cinco montos alineados con la venta).
- **Verificación:** `dry_run` imprime el INSERT esperado para venta con y sin seguro; UAT con un
  contrato de prueba.
- [ ] Impl. · [ ] Verif. · [ ] Review

### 2.7 Módulo `REGISTRO_CLIENTE`
- **Qué:** INSERT en `Customer_Table` y `Customer_Address_Table` en una transacción;
  `Customer_Status_Code` `CC`/`AA` según el tipo de venta.
- **Verificación:** `dry_run` para CF y CN; UAT.
- [ ] Impl. · [ ] Verif. · [ ] Review

### 2.8 Módulo `ACTUALIZAR_ID_CLIENTE`
- **Qué:** propaga `Cliente` a `Agreement_Table.Customer_Id` (y a `ExpedienteCliente` solo si
  falta).
- **Verificación:** `dry_run`; UAT sobre un contrato creado con `Customer_Id = 0`.
- [ ] Impl. · [ ] Verif. · [ ] Review

### 2.9 Módulo `PASO_22_DISPERSADO`
- **Qué:** `ExpedienteCliente.IdPaso` ← `22`, guardando el valor anterior.
- **Verificación:** `dry_run`; UAT (con `Cliente` en `0` y con valor).
- [ ] Impl. · [ ] Verif. · [ ] Review

---

## Fase 3 — Recetas y ejecución

### 3.1 Runner de recetas
- **Qué:** las 6 recetas declaradas como datos; ejecución módulo a módulo con el `ContextoVenta`;
  `PAUSA_QA` como estado persistido (`data/insumos_pendientes.json`).
- **Verificación:** recetas ejecutadas en `dry_run` de punta a punta (sin venta, con
  `numeroContrato` dado).
- [ ] Impl. · [ ] Verif. · [ ] Review

### 3.2 Reanudar y deshacer
- **Qué:** reanudar desde el primer módulo no completado (prioridad); deshacer recorriendo el log
  en orden inverso; deshacer automático solo si falla antes de `PAUSA_QA` o del último módulo.
- **Verificación:** forzar una falla en cada módulo y comprobar reanudar y deshacer (UAT).
- [ ] Impl. · [ ] Verif. · [ ] Review

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
