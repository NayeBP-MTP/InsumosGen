# Reglas de negocio y contexto teórico — Providigital Ventas

Este documento reúne **qué significa cada cosa y por qué**: reglas de negocio, conceptos y
comportamientos observados del portal. **Cómo se automatiza** (flujos, pantallas, componentes)
está en [ESPECIFICACIONES.md](../../ESPECIFICACIONES.md). Plantilla SQL de referencia:
[offers.sql](offers.sql).

---

## 1. Tipos de cliente

### Cliente Nuevo (CN)
Arranca en **Registrar Venta → Cliente nuevo → Registrar una venta**, sin datos previos del
cliente: todo se captura durante el proceso (INE, selfie, domicilio, etc.).

### Cliente Frecuente (CF)
Vende sobre un cliente que **ya tiene una oferta preautorizada** cargada en la base de datos
`botDB`. Antes de poder ejecutar la venta es necesario:

1. **Insertar una oferta** en la tabla `botDB.dbo.Ofertas` (plantilla en [offers.sql](offers.sql)).
2. Esa oferta aparece en el listado del front (pantalla de "Ofertas"/clientes con estatus
   `Sin estatus` / `Visita Acordada`, etc.).
3. **Buscar y seleccionar** la tarjeta del cliente recién insertado usando el campo **Buscar**
   (por `nombreCliente`).
4. Dar click sobre la tarjeta (botón de estatus, p. ej. "Sin estatus") para entrar al flujo de
   venta de ese cliente. El monto/plazo ofertado ya viene definido por la oferta insertada
   (pantalla `offerpage`).

**CF NO es idéntico a CN** (validado en UAT, 23/09/2026):

| Punto | CN | CF |
|---|---|---|
| Orden | identidad → docs → datos → OTP Provident → plazo/monto → método de entrega → beneficiario | oferta → método de entrega → identidad → docs → datos → beneficiario |
| Plazo/monto | tras OTP Provident | al confirmar la oferta preautorizada |
| OTP Provident (SMS) | sí | **no** |
| Consentimiento de geolocalización | no | **sí** (`locationpage`) |
| Modal "Aceptar" al finalizar | sí | **no** |
| Verificación de identidad Legalario | sí | sí (CF **sí** repite identidad) |

### Pantalla "Selecciona el tipo de cliente"
Después de **Ventas → Registrar Venta** se muestra con dos botones: **"Cliente nuevo"** y
**"Cliente frecuente"**. Ambos navegan a la misma ruta `.../v1/app/offerpage`, pero la SPA la
renderiza en dos modos:

- **Modo listado** (sin cliente seleccionado): input **Buscar** y tarjetas de todas las ofertas
  pendientes (`Número de cliente`, `Nombre del cliente`, `Oferta realizada`, botón de estatus
  a la derecha — `Sin estatus`, `Visita Acordada`, etc.).
- **Modo confirmación** (tras click en una tarjeta): texto "El cliente **{nombre}** tiene un
  préstamo autorizado por: {descOferta}" y los `<select>` de plazo/monto — igual a la pantalla
  de oferta de CN, pero con valores acotados por la oferta insertada.

No se identificaron pasos intermedios adicionales antes de este punto.

### Confirmación de finalización en CF
Al pulsar "Finalizar Venta" el portal envía `postlegalario` (`FinProceso`) y registra en
`useractivitylogger` la acción "Finalización" con detalle `Exitoso <folio>`. Esa es la señal de
que la venta CF terminó (no hay modal "Aceptar").

---

## 2. La oferta (`botDB.dbo.Ofertas`)

### Reglas de cada columna

| Columna | Origen | Regla |
|---|---|---|
| `idOferta` | Generado | `AAMM` (año+mes a 2 dígitos) + identificador único de 1 dígito por persona + consecutivo de 3 dígitos. Ej. `26094007` = `26`(año)+`09`(mes)+`4`(id persona)+`007`(consecutivo) |
| `nombreCliente` | Generado | Nombre único por ejecución, para poder buscarlo en el front. Ver §5 (nombres) |
| `porcentajeCalidadCliente` | Variable | Originalmente fijo `80.0`; la automatización usa un valor entre 60 y 95 |
| `montoOferta` | Parametrizable | Monto de la oferta (`8500` en la plantilla). Sujeto al tope por agencia (§3) |
| `tipoDeOferta` | Observado | Ver "Correcciones observadas" abajo |
| `telefonoCliente1` / `telefonoCliente2` | Fijo | `NULL` |
| `direccionCliente` | Fijo/parametrizable | Dirección de prueba |
| `agenciaCliente` | Parametrizable | Depende de la agencia a la que se asigna la venta (13 dígitos, ej. `2025000001234`) |
| `seccionCliente` | Parametrizable | Depende de la agencia. Ver "Correcciones observadas" |
| `amOferta` | Fijo | Constante (`'amOferta'`) |
| `branchOferta` | Derivado | Primeros 4 dígitos de `agenciaCliente` (ej. `2025000001234` → `2025`) |
| `idEstatusOferta` | Fijo | `1` |
| `EstatusComentario` | Fijo | `NULL` |
| `descOferta` | Generado | Texto de negocio: `TARIFA MÁX {monto} {AGREGAR\|REFIN!} {plazo1}/{tasa1} A`. La palabra AGREGAR/REFIN! la elige el usuario en el menú (panel "Oferta" → Tipo de oferta, `Settings.TIPO_OFERTA`). Ejemplo de plantilla completa (con `Agreement_Num` y segundo plazo, no reproducido por la automatización): `TARIFA MÁX 700 REFIN! 260010111 21000/65 D` |
| `semana` | Generado | Semana ISO del año actual, con corte cada **miércoles** (formato `AAAASS`, ej. `202633`) |
| `Customer_Id` | Generado | `branchOferta`(4) + `AAMM`(4) + id-persona(1) + consecutivo(4) |
| `Agreement_Num` | Generado | `AAMM`(4) + id-persona(1) + consecutivo(4) |
| `Agreement_Id` | Fijo/`NULL` | `NULL` salvo caso específico |
| `Agreement_Db_Id` | Fijo/`NULL` | `NULL` salvo caso específico |
| `Agreement_Balance` | Parametrizable | Saldo del contrato (Settlement_Balance), puede ser `NULL` |
| `FechaNacimiento` | Generado | Fecha de nacimiento de prueba, única (mismo patrón que `BirthdateAllocator`) |
| `RFC` | Generado | RFC de prueba coherente con nombre y fecha de nacimiento |
| `Customer_Status_Code` | Fijo | `'CC'` |
| `Agreement_Status_Code` | Fijo | `'AC'` (del nuevo registro) |
| `DireccionCobranzaCliente` | Fijo | `NULL` |
| `VendidaProvidigital` | Fijo | `NULL` |
| `FechaActualizacion` | Generado | Fecha/hora actual del sistema al momento del insert |
| `EarlySettlementRebateValue` | Fijo | `NULL` |
| `Outstanding_Balance` | Fijo | `NULL` |

### Correcciones observadas contra registros reales de QA
La plantilla original de `offers.sql` planteaba hipótesis que los registros reales contradijeron:

- **`tipoDeOferta`**: `'RE'` si la oferta es **REFIN**, `'AD'` si es **AGREGAR** (confirmado en
  `InsumosGen/CONTEXT.md`). Una hipótesis intermedia, tomada de una muestra de registros reales
  de QA que salieron todos `'RE'`, asumía que el campo era siempre `'RE'` para Cliente Frecuente
  sin relación con el texto de `descOferta`; se descarta: la automatización solo generaba ofertas
  AGREGAR con `descOferta` en texto "AGREGAR" pero `tipoDeOferta` fijo en `'RE'`, un desajuste que
  pasó desapercibido porque nunca se había generado una oferta REFIN. Ahora el tipo lo elige el
  usuario en el menú (panel "Oferta" → Tipo de oferta) y `tipoDeOferta` cambia con él.
- **`seccionCliente`**: la plantilla usaba `'S'`. No es un valor fijo por sucursal "normal vs.
  fronteriza" como se pensó al principio: al revisar decenas de INSERTs reales en `InsumosGen/`
  (generadores y `output/`) la sección resultó **específica de cada agencia**, sin un patrón
  simple, y con letras distintas por agencia (`R`, `A`, `B`, `Q`, `S`, `T`, `C`…). El catálogo
  local (`utils/catalog_db.py`, columna `seccion`) guarda la sección observada por agencia; las
  ofertas la usan si está definida, y si no, caen a `'R'` (el valor con más muestras). Nivel de
  confianza por agencia — ver la tabla siguiente.
- **`Agreement_Num`**: solo se rellena cuando la oferta es **REFIN** (para AGREGAR se mantiene
  `NULL`, como en los registros reales de QA observados). Fórmula confirmada contra
  `InsumosGen/CONTEXT.md` **y** un INSERT real (`InsumosGen/output/Ofertas240826.sql`, ejemplo
  `idOferta=26084052` → `Agreement_Num=510264052`, visible también dentro de `descOferta`:
  `TARIFA MÁX 700 REFIN! 510264052 9000/32 A S`):
  `'510' + AA (2 primeros dígitos de idOferta) + últimos 4 dígitos de idOferta (persona+consecutivo)`.
  Ese mismo número se repite en `descOferta` justo después de `REFIN!`. **Nota:** esta fórmula no
  tiene relación con la que trae `utils/offer_id_allocator.py` en su docstring
  (`AAMM + persona + consecutivo`, para dar unicidad interna); ese valor del allocator no se
  escribe en `dbo.Ofertas.Agreement_Num` — el campo real se calcula aparte a partir de `idOferta`.

#### Sección observada por agencia (nivel de confianza)

| Agencia | `agenciaCliente` | Sección | Muestras en `InsumosGen/` |
|---|---|---|---|
| Izcalli 335 | `2075000000335` | `R` | Muchas (docenas), consistente. Una sola fila aislada en `OfertasLupita2.sql` trae `A`, tratada como error de captura (contradice todo lo demás, incluido un comentario explícito "Sucursal Normal, Seccion R") |
| Tijuana 111 | `2093000000111` | `A` | Varias |
| Tijuana 0002 | `2093000000002` | `B` | 1 |
| Aguascalientes 234 | `2025000001234` | `S` | 1 |
| Zacatecas 238 | `2060000001238` | `B` | 1 |
| Zacatecas 239 | `2060000001239` | `Q` | 1 |
| Izcalli 009 / 010, Tijuana 123 / 0003, San Luis Potosí 234 | — | sin evidencia | 0 — usan el fallback `'R'` |

Las agencias con **1 sola muestra** vienen de archivos de generación de insumos (`InsumosGen/generadores/`), no de una fuente validada contra UAT; conviene confirmarlas antes de depender de ellas para una venta real.

### Reglas de los identificadores únicos
- `idOferta` = `AAMM(4) + persona(1) + consecutivo(3)` → 8 dígitos
- `Customer_Id` = `branch(4) + AAMM(4) + persona(1) + consecutivo(4)` → 13 dígitos
- `persona` (0-9) y `consecutivo` (1-999) identifican de forma única la oferta dentro del mes.
- `Agreement_Num` real de `dbo.Ofertas` **no** usa esta pareja persona/consecutivo por separado:
  se deriva directo de `idOferta` con la fórmula de la sección anterior
  (`'510' + AA + últimos 4 dígitos de idOferta`), y solo aplica a ofertas REFIN.
- **Semana:** `AAAASS` = año ISO + semana ISO de 2 dígitos, pero la semana avanza cada
  **miércoles** en lugar del lunes de ISO 8601 (de lunes a martes sigue siendo la semana
  anterior; el cambio ocurre al llegar el miércoles). Implementado en
  `OfferIdAllocator.calcular_semana` (`utils/offer_id_allocator.py`).
  ⚠ Importante: `_insertar_oferta_cf` (`tests/test_login_cf.py`) usa
  `max(semana_calculada, semana_tabla)` — la semana MÁS RECIENTE ya presente en
  `botDB.dbo.Ofertas` — porque el listado del front solo muestra ofertas de la semana
  más reciente de la tabla. Esto significa que si la tabla ya tiene registros en la
  semana nueva (insertados por otra fuente, otro ambiente, o un reloj desfasado) antes
  de que llegue el miércoles real, las inserciones de la automatización "saltan"
  a esa semana más alta aunque el cálculo por fecha todavía diera la semana anterior.
  No es un bug de `calcular_semana`: es el comportamiento esperado de ese `max()`.
- Los identificadores **no deben repetirse entre ejecuciones**, ni en paralelo (mismo motivo por
  el que las fechas de nacimiento son únicas: evitar "cliente ya registrado").
- Los ids de prueba manual usan prefijo `9` (p. ej. `90000001`) para no colisionar con el
  patrón real `AAMM...`.

### Pendientes de validar con negocio
- Template exacto de `descOferta`: si además de AGREGAR/REFIN! debe incluir `Agreement_Num`,
  un segundo `{plazo}/{tasa}` y el sufijo `A N{n}` de la plantilla original, y reglas de
  `plazo`/`tasa` según el tipo de oferta.
- Si `id_persona`/`consecutivo` deben ser thread-safe entre corridas paralelas (hoy lo son
  por SQLite con transacción `EXCLUSIVE`, igual que `BirthdateAllocator`).
- Confirmar la sección de las agencias con una sola muestra (Tijuana 0002, Aguascalientes 234,
  Zacatecas 238/239) y llenar las que no tienen ninguna evidencia (Izcalli 009/010, Tijuana
  123/0003, San Luis Potosí 234) — ver tabla de arriba.

---

## 3. Reglas por agencia

- **Tope de monto CF:** en **Tijuana** el monto de una oferta CF debe ser **menor a 10,000**
  (10,000 no es válido). El límite es EXCLUSIVO y se aplica por prefijo del nombre de agencia.
- **Oficina postal Finabien:** el estado/ciudad donde se busca la oficina postal depende de la
  agencia (Tijuana → Baja California/Tijuana, Izcalli → Estado de México/Cuautitlán Izcalli,
  Zacatecas, Aguascalientes, San Luis Potosí). Agencias no listadas usan Puebla/Puebla.
- `agenciaCliente` es el código de 13 dígitos de la agencia; `branchOferta` son sus primeros 4.
- `seccionCliente` depende de la agencia.

---

## 4. Métodos de entrega

Métodos disponibles en el portal: **BBVA**, **HSBC**, **Finabien**, **Efectivo**, **Cheque**.

- Los botones se muestran en la pantalla `paymenttypepage`; **no todos aparecen siempre**.
- **Observación (23/09/2026):** con **Tijuana 111** en un flujo CF, la pantalla ofreció solo
  **Cheque, Orden de pago HSBC y Orden de Pago BBVA** (sin Finabien). Se desconoce qué habilita
  el botón de Finabien (agencia, estado del cliente o tipo de oferta): pendiente de confirmar
  con negocio. En CN con **Tijuana 0003** sí se completó una venta con Finabien.
- **Finabien** exige además elegir una **oficina postal** (Estado → Ciudad → Oficina Postal) y
  confirmar en un segundo modal.

---

## 5. Datos de prueba

- Los nombres de cliente CF son **realistas pero ficticios** (nombre + dos apellidos
  mexicanos comunes, hombre/mujer). No se usan personas reales.
- El **RFC** de prueba tiene la forma real de persona física (4 letras derivadas de los apellidos
  y nombre + `AAMMDD` de la fecha de nacimiento + 3 de homoclave). La homoclave es aleatoria y
  no hay dígito verificador real.
- La **fecha de nacimiento** es única por ciclo para evitar "cliente ya registrado".
- El **monto** (1500, 2000, 2500 o 3000 por defecto) y `porcentajeCalidadCliente` (60–95) varían
  entre ofertas; plazo/tasa (`14000/65`) y tipo (`RE`) se mantienen fijos porque se desconocen
  los rangos válidos de negocio.
- **Validación de identidad:** en UAT no importa que el nombre de la oferta no coincida con el
  del INE mock; solo se valida la imagen.
- **Limpieza de ofertas:** originalmente las ofertas insertadas no se borraban al terminar
  (para poder revisarlas en BD). Ahora, si un intento CF **no termina en venta**, su oferta se
  elimina de `botDB` antes de generar la siguiente. Las ofertas de ventas exitosas se conservan.
- Un intento fallido de **CN** no deja nada en `botDB` que borrar.

---

## 6. Conceptos técnicos de contexto

- **Legalario:** proveedor de verificación de identidad (INE frente/reverso + facematch) y de
  firma del contrato. Se usa su **sandbox** (`sandbox-api.legalario.com`) en UAT.
- **Facematch:** comparación de la selfie contra la foto de la INE. Con imágenes sintéticas el
  fallback puede responder HTTP 400 (AWS Rekognition `InvalidParameterException`), pero el SDK
  permite avanzar igualmente vía el botón Firmar con JS click.
- **OTP Provident** (SMS, `/v1/sendconfirmationsms`, campo `body.code`) vs **OTP Legalario**
  (`/sdk/invites/send-code`, campo `data.otp_code`, 4 dígitos; el SDK envía el SMS con
  `send-code-new`, que no devuelve el código, ver `Context.md` sección 10): son dos OTP distintos;
  CF solo usa el de Legalario.
- **Pantalla `singleoffer`:** oferta opcional que a veces aparece tras confirmar plazo/monto; se
  omite con "No aceptar oferta".
- **Contador de contrato:** tras "Finalizar Venta" en CF el portal permanece en la misma pantalla
  con un contador de contrato de 2 minutos.
- **Portal UAT:** `https://originacion-uat.providigital.com/v1/app/login`. Salir con "Salir"
  tras finalizar la venta dispara un bucle de recarga que cuelga chromedriver; por eso se cierra
  la sesión del lado del cliente (cookies + storage).
- **Requisito de red:** `botDB` solo es accesible con red/VPN corporativa (`PESOS_OFFER_SERVER:1433`).
  Sin acceso, el ciclo CF falla en el insert antes de abrir el navegador.

## 7. Insumo "cliente para la Mobile App" (clientes creados tras una venta)

Diseño completo y módulos en `config/Context/crearClientesFC/CREAR_CLIENTES.md`. Reglas de negocio:

- **Tipo de cliente en CNFS:** `Customer_Table.Customer_Status_Code` = `CC` para un CF y `AA` para
  un CN.
- **Número de cliente de un CN** (`ExpedienteCliente.Cliente`, 13 dígitos):
  `AA + MM + DD + colaborador (2) + 02 (UAT) + consecutivo (3)`. En un CN recién vendido `Cliente`
  está en `0`; en un CF ya viene con valor.
- **CN: registro por QA.** QA registra al usuario en la Mobile App con `numeroContrato` y fecha de
  nacimiento, **antes** de que exista el número de cliente; por eso el contrato se da de alta con
  `Customer_Id = 0` y el número se asigna después.
- **Dispersado:** `ExpedienteCliente.IdPaso = 22`.
- **Montos del contrato:** dependen de si la venta fue con o sin seguro (columnas `*Seguro` de
  `ExpedienteOferta`).

