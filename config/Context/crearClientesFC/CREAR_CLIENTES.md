# Crear clientes para la Mobile App de Provident (insumo CF y CN)

> **Estado: diseño. Aún no hay código implementado.** Se implementa en la rama `feat/recipes`
> (la rama `feat/parallelization` se deja de lado; sus cambios sin commitear siguen siendo la base).

Proceso técnico para generar un cliente que pueda registrarse en la **Mobile App de Provident**
a partir de una venta hecha con la automatización (o de una venta ya existente). El proceso se
define como **módulos** de grano medio (sección 2) que se **ponen y se quitan** según el caso de
uso (sección 3), porque QA pide variantes distintas del mismo insumo.

| Base.Tabla | Servidor | Rol |
|---|---|---|
| `Originacion.dbo.ExpedienteCliente` | Pesos_Offer | Datos de la venta (cliente, contrato, agencia, paso). También se **modifica**. |
| `Originacion.dbo.ExpedienteOferta` | Pesos_Offer | Montos/pagos de la venta (con o sin seguro). Solo lectura. |
| `CNFS_uat.NFS_DBO.Customer_Table` | CNFS | Destino: alta del cliente. |
| `CNFS_uat.NFS_DBO.Agreement_Table` | CNFS | Destino: alta del contrato. |
| `CNFS_uat.NFS_DBO.Customer_Address_Table` | CNFS | Destino: alta del domicilio. |

**Hosts de base de datos** (son 5; cada host aloja varias bases, y una base vive en un solo host):

| Host | Bases relevantes | Uso en este flujo |
|---|---|---|
| **Pesos_Offer** | `botDB`, `Originacion` | `Originacion` (expediente) y `botDB` (ofertas): **mismo host** |
| **CNFS** | `CNFS_uat` | Customer / Agreement / Customer_Address |
| **Challenger** | `Challenger_uat` | flujo de estructura de agencia (no se usa aquí) |
| **Customer_App** | — | no se usa en este flujo |
| **PaymentLink** | — | no se usa en este flujo |

Cada host tiene **una sola conexión** (un juego de variables `.env` con el nombre del host) y la
base se elige con nombre de tres partes (`Originacion.dbo.ExpedienteCliente`). El mapeo
base de datos → host vive en un solo lugar del código (`config/databases.py`), no en el `.env`:
así no se duplican credenciales ni conexiones. Ver decisión 4.

Plantillas SQL de referencia (en esta misma carpeta):

- [queryCustomerTable.sql](queryCustomerTable.sql)
- [queryAgreementTable.sql](queryAgreementTable.sql)
- [queryCustomerAddressTable.sql](queryCustomerAddressTable.sql)

Las plantillas son INSERTs con valores de ejemplo: solo se sustituyen los campos listados abajo;
el resto se deja tal como viene (excepto lo indicado en "Decisiones", punto 5).

---

## 1. Convenciones comunes

- **Fecha del día** = fecha en que se ejecuta el módulo (hoy). **Fecha + 7 días** = hoy + 7.
- **Semana actual** = semana de negocio Provident, formato `AAAASS` (ej. `202623`). **No sale de
  ninguna tabla.** Cambia los **miércoles**, no los lunes; usar `OfferIdAllocator.calcular_semana`
  (`utils/offer_id_allocator.py`), no `isocalendar()`. Ver `REGLAS_DE_NEGOCIO.md`.
- **Con seguro / sin seguro**: lo decide la UI (`Settings.CON_SEGURO`) si la automatización hace la
  venta; si la venta ya existe, es parámetro del caso de uso. Define qué columnas de
  `ExpedienteOferta` se leen.
- **Agencia** = `Agencia` de `ExpedienteCliente` (13 dígitos, ej. `2075000000335`).
  "4 primeros dígitos de la agencia" = `str(agencia)[:4]` (ej. `2075`).
- **`Customer_Status_Code`**: `CC` = CF, `AA` = CN.

---

## 2. Módulos

Un módulo hace **una etapa completa** del proceso (no un solo INSERT/UPDATE) y se combina con otros
en una receta. Contrato común:

- **Entrada/salida:** recibe un **`ContextoVenta`** (datos de la venta acumulados: `numero_contrato`,
  `id_expediente_cliente`, `cliente`, `agencia`, `fecha_nacimiento`, `nombre_cliente`, `rfc`,
  `domicilio`, `con_seguro`, montos…) y lo devuelve enriquecido para el siguiente módulo.
- **Carga perezosa del contexto:** localizar el expediente y leer `ExpedienteOferta` **no son
  módulos**, son ayudas internas del `ContextoVenta`: cualquier módulo que necesite esos datos los
  carga la primera vez. Así una receta no necesita pasos de "preparación".
- **Idempotente:** antes de escribir comprueba si el efecto ya existe y, si es así, lo omite.
- **Registra lo que escribe** (tabla + llave + valor anterior) en un log, para poder deshacer.
- **Independiente de la UI**; los módulos de venta usan Selenium, los demás solo SQL.

### 2.1 Módulos existentes (ya implementados)

| Módulo | Qué hace hoy | Archivo |
|---|---|---|
| **`OFERTA`** | Inserta y verifica la oferta en `botDB.dbo.Ofertas`. | `tests/test_oferta.py` |
| **`VENTA_CF`** | Venta de Cliente Frecuente; **incluye** `OFERTA` (inserta la oferta antes de vender). | `flows/venta_cf.py` |
| **`VENTA_CN`** | Venta de Cliente Nuevo, sin oferta previa. | `flows/venta_cn.py` |

Cambio requerido: `VENTA_CF` y `VENTA_CN` deben **devolver** `numeroContrato`, nombre de la INE,
hora de inicio de la venta, agencia y `con_seguro` para poblar el `ContextoVenta`.

### 2.2 Módulos nuevos

#### `RENOMBRAR_CLIENTE` — cambio de nombre/RFC en `ExpedienteCliente`
UPDATE en `ExpedienteCliente` (por `IdExpedienteCliente`):

1. `NombreCliente` ← nombre mexicano aleatorio (`MexicanNames.generar`, `utils/mexican_names.py`).
2. `RFCCliente` ← RFC coherente con el nuevo nombre y `FechaNacimiento` (`MexicanNames.rfc`). No se
   cambia la fecha de nacimiento.

Guarda el nombre/RFC originales en el log. El nombre nuevo es el que usan `Display_Name`,
`Forename` y `Surname` en `REGISTRO_CLIENTE`.

#### `CREAR_ID_CLIENTE` — creación del ID de cliente
Genera el número de cliente, lo escribe en `ExpedienteCliente.Cliente` y lo deja en el
contexto. Si `Cliente` ya tiene un valor distinto de `0` (CF), lo usa tal cual sin escribir nada.
Si está en `0` (CN), lo genera:

```
AA + MM + DD + CC + 02 + NNN
```

| Parte | Significado |
|---|---|
| `AA` | dos últimos dígitos del año |
| `MM` | dos dígitos del mes |
| `DD` | dos dígitos del día |
| `CC` | número de colaborador (2 dígitos; `Settings.NUMERO_COLABORADOR`, de los *Ajustes de usuario* de la UI) |
| `02` | fijo (UAT) |
| `NNN` | consecutivo de 3 dígitos (`001`, `002`, …) |

**Consecutivo `NNN`:** se consulta en BD el mayor `NNN` ya usado hoy con el mismo prefijo
`AAMMDD + CC + 02` (11 dígitos) y se usa ese + 1; si no hay ninguno, `001`. Ejemplo: 4-nov-2026,
colaborador `04`, primer cliente del día → `2611040402001`.

- Revisa **`ExpedienteCliente.Cliente` y `Customer_Table.Customer_Id`** (puede haber clientes
  creados solo en CNFS).
- **Concurrencia:** el número se reserva con un allocator local en SQLite con transacción
  `EXCLUSIVE` (mismo patrón que `utils/offer_id_allocator.py`), inicializado con el máximo de BD,
  para que ventas en paralelo no obtengan el mismo número.

#### `ACTUALIZAR_ID_CLIENTE` — actualización del ID en `ExpedienteCliente` y `Agreement_Table`
Propaga el `Cliente` del contexto (ya generado por `CREAR_ID_CLIENTE`) a:

1. `CNFS_uat.NFS_DBO.Agreement_Table.Customer_Id` (estaba en `0`), filtrando por
   `Agreement_Num = numeroContrato`.
2. `Originacion.dbo.ExpedienteCliente.Cliente` (por `IdExpedienteCliente`), solo si todavía no
   tiene ese valor (como `CREAR_ID_CLIENTE` ya lo escribió, normalmente se omite; se deja por
   idempotencia y por si se invoca con un `Cliente` dado a mano).

Se usa en las recetas donde `AGREEMENT` corrió **antes** de tener el número de cliente (1 y 3).
Requiere que `AGREEMENT` ya haya corrido.

#### `AGREEMENT` — registro en `Agreement_Table`
INSERT en `Agreement_Table` con [queryAgreementTable.sql](queryAgreementTable.sql). Sin
parámetros: `Customer_Id` toma `Cliente` del contexto si es distinto de `0`, y `0` si no. Carga el
contexto (expediente + montos de `ExpedienteOferta`):

| Valor lógico | Sin seguro | Con seguro |
|---|---|---|
| Monto del préstamo | `MontoTotal` | `MontoTotalSeguro` |
| Primer pago | `PrimerPagoSemanal` | `PrimerPagoSemanalSeguro` |
| Pago de cada semana | `PagoSubsecuente` | `PagoSubsecuenteSeguro` |

Si la columna elegida viene `NULL` o `0`, falla con mensaje claro (no inserta montos en cero).

| Campo destino | Valor |
|---|---|
| `Absolute_Arrears` | `0` |
| `Actual_Paid_Up_Date` | fecha de hoy |
| `Actual_Paid_Up_Week` | semana actual |
| `Agreement_Num` | `numeroContrato` |
| `Agreement_Status_Code` | `AC` |
| `Creation_Date` | fecha del día |
| `Customer_Id` | `Cliente` del contexto; `0` si aún no existe (CN antes de `CREAR_ID_CLIENTE`) |
| `Final_Instalment_Value` | pago de cada semana |
| `Total_Amount_Payable` | monto del préstamo |
| `Settlement_Balance` | monto del préstamo |
| `Last_Updated_Datetime` | fecha de hoy |
| `First_Instalment_Value_At_Issue` | primer pago |
| `Regular_Instalment_Value_At_Issue` | pago de cada semana |
| `Total_Amount_Payable_At_Issue` | monto del préstamo |
| `First_Instalment_Value` | primer pago *(aprobado: se alinea con la venta)* |
| `Regular_Instalment_Value` | pago de cada semana *(aprobado)* |
| `Final_Instalment_Value_At_Issue` | pago de cada semana *(aprobado)* |
| `Issue_Value` | monto del préstamo *(aprobado)* |
| `Outstanding_Balance` | monto del préstamo *(aprobado)* |

#### `REGISTRO_CLIENTE` — registro en `Customer_Table` y `Customer_Address_Table`
Sin parámetros: `Customer_Status_Code` sale del tipo de venta del contexto (`CC` si fue
`VENTA_CF`, `AA` si fue `VENTA_CN`). Dos INSERTs en **una sola transacción** (mismo servidor,
CNFS). Requiere `Cliente` distinto de `0` en el contexto.

`Customer_Table` ([queryCustomerTable.sql](queryCustomerTable.sql)):

| Campo destino | Valor |
|---|---|
| `Customer_Id` | `Cliente` |
| `Agency_Id` | `Agencia` |
| `Agency_Segment_Db_Id` | 4 primeros dígitos de la agencia (2025, 2075, etc.) |
| `Agency_Segment_Id` | 4 primeros dígitos de la agencia |
| `Birth_Date` | `FechaNacimiento` |
| `Creation_Date` | fecha del día |
| `Creation_Week` | semana actual |
| `Display_Name` | `NombreCliente` (ya renombrado, en CF) |
| `Disposable_Income_Date` | fecha de hoy + 7 días |
| `First_Agreement_Creation_Date` | fecha de hoy + 7 días |
| `Forename` | solo el nombre de pila de `NombreCliente` |
| `Nearest_Relative_Address` | `DomicilioCliente` |
| `Surname` | apellidos de `NombreCliente` |
| `Customer_Status_Code` | `CC` (CF) / `AA` (CN), según el tipo de venta |

`Customer_Address_Table` ([queryCustomerAddressTable.sql](queryCustomerAddressTable.sql)):

| Campo destino | Valor |
|---|---|
| `Customer_Id` | `Cliente` |
| `Full_Address` | `DomicilioCliente` |

#### `PASO_22_DISPERSADO` — cambio a paso 22 en `ExpedienteCliente`
UPDATE de `ExpedienteCliente.IdPaso` ← `22` (dispersado), por `IdExpedienteCliente`. Guarda el
`IdPaso` anterior en el log.

- **Precondición:** solo que exista el registro en `ExpedienteCliente`. `Cliente` puede estar en
  `0`, así que puede ir antes o después de `CREAR_ID_CLIENTE`; no requiere `AGREEMENT` ni
  `REGISTRO_CLIENTE`.
- **Alcance:** por ahora no cambia ningún otro dato.

### 2.3 Utilidades de la ejecución (no son módulos)

- **`PAUSA_QA`:** paso de la receta que detiene la ejecución hasta que QA confirme (sección 3.3).
- **Reanudar / deshacer:** ver sección 3.4.

> **Transaccionalidad:** `Originacion` y `botDB` están en el **mismo host** (Pesos_Offer), por lo
> que una sola conexión puede escribir en ambas bases en una transacción. `CNFS` es otro host: no
> hay transacción que cubra Pesos_Offer y CNFS. Cada módulo es atómico dentro de su host; entre
> hosts se confía en la idempotencia y en el log.

---

## 3. Casos de uso (recetas)

Una receta es una lista ordenada de módulos con sus parámetros, declarada como **datos** (no como
código), de modo que armar un caso nuevo es agregar una línea.

### 3.1 Recetas definidas

Seis recetas de creación de cliente, más los tres módulos existentes que siguen usándose solos
(`OFERTA`, `VENTA_CF`, `VENTA_CN`). El tipo de venta (CF/CN) viene del módulo de venta y define
`Customer_Status_Code` (`CC`/`AA`) en `REGISTRO_CLIENTE`.

| # | Receta | Módulos |
|---|---|---|
| 1 | **CN con registro intermedio** | `VENTA_CN` → `RENOMBRAR_CLIENTE` → `AGREEMENT` → (`PAUSA_QA`) → `CREAR_ID_CLIENTE` → `ACTUALIZAR_ID_CLIENTE` → `REGISTRO_CLIENTE` |
| 2 | **CN registrado** | `VENTA_CN` → `RENOMBRAR_CLIENTE` → `CREAR_ID_CLIENTE` → `AGREEMENT` → `REGISTRO_CLIENTE` |
| 3 | **CN con registro dispersado** | `VENTA_CN` → `RENOMBRAR_CLIENTE` → `PASO_22_DISPERSADO` → `AGREEMENT` → (`PAUSA_QA`) → `CREAR_ID_CLIENTE` → `ACTUALIZAR_ID_CLIENTE` → `REGISTRO_CLIENTE` |
| 4 | **CN registrado con dispersión** | `VENTA_CN` → `RENOMBRAR_CLIENTE` → `CREAR_ID_CLIENTE` → `PASO_22_DISPERSADO` → `AGREEMENT` → `REGISTRO_CLIENTE` |
| 5 | **CF dispersado** | `VENTA_CF` → `RENOMBRAR_CLIENTE` → `PASO_22_DISPERSADO` → `AGREEMENT` → `REGISTRO_CLIENTE` |
| 6 | **CF registrado** | `VENTA_CF` → `RENOMBRAR_CLIENTE` → `AGREEMENT` → `REGISTRO_CLIENTE` |

Notas sobre cómo encajan los módulos:

- **Recetas 1 y 3 (con `PAUSA_QA`):** `AGREEMENT` corre con `Customer_Id = 0` porque QA debe
  registrar al usuario con `numeroContrato` y fecha de nacimiento **antes** de que exista el número
  de cliente. Después `CREAR_ID_CLIENTE` genera el número y `ACTUALIZAR_ID_CLIENTE` lo propaga al
  contrato.
- **Recetas 2 y 4 (sin pausa):** `CREAR_ID_CLIENTE` va antes de `AGREEMENT`, que ya toma el
  `Cliente` y no necesita `ACTUALIZAR_ID_CLIENTE`.
- **Recetas CF (5 y 6):** el `Cliente` ya viene en `ExpedienteCliente`; no se usa
  `CREAR_ID_CLIENTE`.
- **`PAUSA_QA` entre paréntesis** = paso opcional de la receta. Las recetas 1 y 3 se pueden
  declarar sin él si QA no interviene.
- **Reanudar:** la parte de una receta posterior a `PAUSA_QA` (`CREAR_ID_CLIENTE` →
  `ACTUALIZAR_ID_CLIENTE` → `REGISTRO_CLIENTE`) es la que se ejecuta al confirmar QA.
- **Sin venta:** cada receta puede arrancar sin su módulo de venta si se da `numeroContrato` de una
  venta ya hecha (ver 3.2); el tipo (CF/CN) se toma entonces de un parámetro.

### 3.2 Cómo se identifica la venta cuando no la hizo la automatización
Las recetas sin su módulo de venta reciben `numeroContrato` (criterio más seguro) o `IdExpedienteCliente`.
Cuando la venta la acaba de hacer la automatización, el `ContextoVenta` ya trae `numeroContrato`
desde el módulo de venta; si no, se localiza por **nombre de la INE + `FechaFinalizacion`** (el
último registro posterior al inicio de la venta).

> **Riesgo:** el nombre de la INE es el mismo en todas las ventas de una corrida y puede haber
> ventas en paralelo. Esa búsqueda filtra además por **agencia** y descarta contratos que ya
> tengan fila en `Agreement_Table`.

### 3.3 Pausa para QA (`PAUSA_QA`)
La pausa es un **estado persistido**, no un hilo bloqueado: sobrevive a cerrar la ventana.

- Al llegar a `PAUSA_QA` guarda la operación en `data/insumos_pendientes.json` con estado
  `esperando_qa`, su `ContextoVenta` y el resto de la receta por ejecutar.
- `ProgressUI` muestra un panel "Esperando QA" con `numeroContrato` y fecha de nacimiento (lo que
  QA necesita para registrar al usuario) y el botón **"QA confirmó, continuar"** por operación.
- Al confirmar, se reanuda la receta desde el paso siguiente (la parte de la receta posterior a la pausa).
- Si se cierra la ventana, al abrir el asistente se ofrece "Retomar operaciones pendientes de QA".

### 3.4 Log, reanudar y deshacer

**Log siempre.** Cada módulo anota lo que escribe (host, base.tabla, llave, valor anterior) en un
archivo por operación en `data/`, antes de dar la operación por terminada. Registrar no toca la BD.

**Dos operaciones a demanda** sobre una operación incompleta o terminada (UI, línea de comandos
para QA o `rollback <numeroContrato>`):

| Operación | Qué hace | Prioridad |
|---|---|---|
| **Reanudar** | Vuelve a ejecutar la receta desde el primer módulo no completado. Posible porque los módulos son idempotentes. | **Primera opción**, se ofrece antes que borrar |
| **Deshacer** | Recorre el log en orden inverso: DELETE de lo insertado y UPDATE inverso de lo modificado (nombre/RFC, `Cliente`, `IdPaso`). | Cuando el usuario ya no quiere el insumo |

**Automático:** solo se deshace solo si la receta **falla antes de llegar a `PAUSA_QA` o a su último
módulo**, para no dejar datos huérfanos. Una vez pasada la pausa, o en el último módulo, el estado
parcial se conserva para reanudar. Un insumo terminado nunca se borra solo (QA puede necesitarlo
semanas).

---

## 4. Decisiones tomadas

1. **Número de colaborador:** de los *Ajustes de usuario* de la UI (`Settings.NUMERO_COLABORADOR`,
   2 dígitos, ya validado).
2. **Consecutivo `NNN`:** mayor `NNN` de hoy en BD con el mismo prefijo + 1; `001` si no hay
   ninguno. *Supuesto:* el prefijo incluye el colaborador (consecutivo por colaborador y día).
3. **Con / sin seguro:** de la UI (`con_seguro`), no se infiere de la BD.
4. **Conexiones, una por host, con el nombre del host (5 hosts):**
   - Variables `.env` por host: `<HOST>_SERVER`, `<HOST>_USER`, `<HOST>_PASSWORD`, `<HOST>_DRIVER`,
     con `<HOST>` ∈ `PESOS_OFFER`, `CNFS`, `CHALLENGER`, `CUSTOMER_APP`, `PAYMENTLINK`. No hay
     variables `*_DATABASE`: la base no es parte del host.
   - **Renombrar** las variables actuales: `BOTDB_*` → `PESOS_OFFER_*` (el nombre `BOTDB` es el de
     una base, no el del host); `CHALLENGER_*` y `CNFS_*` ya usan el nombre del host. Sin
     `ORIGINACION_*`: `Originacion` usa `PESOS_OFFER_*`.
   - **Mapeo base → host** en `config/databases.py` (único lugar donde se escribe el nombre de una
     base):

     | Base | Host |
     |---|---|
     | `botDB` | `PESOS_OFFER` |
     | `Originacion` | `PESOS_OFFER` |
     | `CNFS_uat` | `CNFS` |
     | `Challenger_uat` | `CHALLENGER` |

   - Los repositorios piden la conexión por **base** (`conexion("Originacion")`) y la clase base
     resuelve el host, así no se puede abrir una base con las credenciales del host equivocado.
   - A confirmar: que el usuario de Pesos_Offer tenga permisos sobre `Originacion`.
5. **Montos en `Agreement_Table` (aprobado):** además de los campos pedidos, se alinean con la
   venta `First_Instalment_Value`, `Regular_Instalment_Value`, `Final_Instalment_Value_At_Issue`,
   `Issue_Value` y `Outstanding_Balance`.
6. **Módulos de grano medio** que se ponen/quitan por receta (sección 2); localizar expediente y
   leer montos son ayudas internas del contexto, no módulos.

7. **Ajustes a los módulos (aprobados):** `CREAR_ID_CLIENTE` escribe `ExpedienteCliente.Cliente`;
   `ACTUALIZAR_ID_CLIENTE` propaga al contrato (y a `ExpedienteCliente` solo si falta);
   `AGREEMENT` y `REGISTRO_CLIENTE` no llevan parámetros (se deducen del contexto y del tipo de
   venta).

8. **Rollback:** log siempre; reanudar y deshacer a demanda (reanudar con prioridad); deshacer
   automático solo si la receta falla antes de `PAUSA_QA` o de su último módulo (sección 3.4).

9. **Valores de las plantillas que no están en las listas de campos** (fechas/semanas viejas,
   `Agreement_Db_Id`, `Customer_Address_Db_Id`, GUIDs): **se dejan tal como vienen**. No afectan la
   operación y no se conocen las implicaciones de cambiarlos. Riesgo a vigilar en la primera
   ejecución real: si alguno es parte de una llave única y se repite entre clientes, el INSERT
   fallará con un mensaje claro y se decidirá entonces.

## 5. Pendiente

- Confirmar permisos del usuario de Pesos_Offer sobre `Originacion`.
- Renombrar `BOTDB_*` → `PESOS_OFFER_*` en el `.env` local de cada quien (y agregar `CNFS_*`, que
  el `.env` local no tiene; su bloque "CNFS" repite `CHALLENGER_*`).
- Verificar con una venta real si `folio` = `numeroContrato` (ver sección 6, punto 4).
- `PASO_22_DISPERSADO`: por ahora solo cambia `IdPaso`; revisar si dispersar requiere más cambios
  cuando se use en un flujo real.

---

## 6. Ajustes previos a implementar el sistema de recetas (aprobados)

Cambios sobre lo existente que se hacen **antes** de los módulos nuevos, en la rama `feat/recipes`:

1. **Base de trabajo:** `feat/recipes` parte con los cambios sin commitear de
   `feat/parallelization` (son relevantes). Se commitean como primer paso para tener un punto de
   retorno.
2. **Conexiones por host + renombrar variables:**
   - Crear `config/databases.py` (mapeo base → host, decisión 4) y una clase base de conexión
     (`services/db.py`) con los reintentos que hoy solo tiene `OfferRepository`.
   - Migrar `OfferRepository` (`BOTDB_*`), `ChallengerRepository` (`CHALLENGER_*`),
     `utils/vpn_check.py` y cualquier otro uso de variables de BD a los nombres por host.
   - Actualizar `.env.example` y las referencias en `CLAUDE.md`, `Context.md`,
     `ESPECIFICACIONES.md` y `REGLAS_DE_NEGOCIO.md` (mencionan `BOTDB_*`).
3. **Sacar los flujos de venta de los archivos de test:** `_ejecutar_venta_cf` y los flujos
   compartidos viven en `tests/`, y `test_login_cf.py` importa de `test_login.py`. Moverlos a un
   módulo propio (p. ej. `flows/`) para que `VENTA_CF`/`VENTA_CN` sean invocables desde una receta.
   **Verificar que sigue funcionando** (ver abajo).
4. **Resultado de las ventas:** que devuelvan `numeroContrato`, nombre de la INE, inicio de la
   venta, agencia y `con_seguro`.
   - Hallazgo del código y de `data/run_results_*.json`: el `folio` sale del log de actividad
     (`useractivitylogger`, "Finalización — Exitoso <folio>") y **no es fiable**: en ventas CF
     exitosas ya quedó `null`, y el resultado de CN no lo incluye. No se asume `folio` =
     `numeroContrato` hasta comprobarlo.
   - Verificación: una venta real en UAT, y luego leer en `ExpedienteCliente` el `numeroContrato`
     de esa venta y compararlo con el folio capturado. Requiere VPN y que las variables
     `PESOS_OFFER_*` ya estén en el `.env` (depende del punto 2).
   - Si no coinciden o el folio falla, se localiza por nombre de la INE + `FechaFinalizacion`
     (sección 3.2).
5. **Reloj del servidor:** tomar la hora de inicio de la venta con `SYSDATETIME()` del host
   (Pesos_Offer), no con el reloj local, para comparar contra `FechaFinalizacion`.
6. **`run.py` genérico por tipo:** hoy el tipo (`OF`/`CF`/`CN`/`AGENCIA`) está fijo en
   `ORDEN_TIPOS`, `TEST_FILE_BY_TIPO_CLIENTE` y el diccionario de etiquetas de `_ejecutar_fase`.
   Se agrega un tipo `RECETA` con la receta como parámetro, y se generalizan resultados e historial.
7. **Plantillas como datos:** convertir los 3 INSERT en diccionarios columna → valor por defecto
   (los `.sql` quedan como referencia) y una prueba que verifique que coinciden en columnas.
8. **Modo de simulación (`dry_run`)** en los repositorios, para validar cada módulo sin escribir en
   UAT, y pruebas unitarias de la lógica pura (consecutivo `NNN`, semana, selección de montos con/sin
   seguro, nombre de pila/apellidos).
9. **Nombre/apellidos:** `RENOMBRAR_CLIENTE` corre en las 6 recetas, así que `Forename`/`Surname`
   se toman de las partes que devuelve `MexicanNames.generar`, no de partir el nombre completo
   (evita errores con nombres compuestos).

**Orden sugerido:** 1 → 2 → 3 (con verificación) → 4 → 5 → 7 → 8 → 9 → 6 → módulos nuevos.
