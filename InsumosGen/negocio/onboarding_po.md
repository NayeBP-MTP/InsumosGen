# Onboarding de Negocio — Provident México

> **Source of truth de negocio** para Provipedia y para el repositorio InsumosGen. Cubre estructura organizacional, aplicaciones de campo (MyProvi/MyCollections/MyTeams), cobranza, folios, niveles de precio, originación de ventas y ciclo de vida de clientes.

## Índice

1. [Estructura organizacional y roles](#1-estructura-organizacional-y-roles)
2. [Aplicaciones y acceso](#2-aplicaciones-y-acceso)
3. [Arquitectura de datos: LNFS, Focus y Freud](#3-arquitectura-de-datos-lnfs-focus-y-freud)
4. [Sincronización y modo offline](#4-sincronización-y-modo-offline)
5. [Clip, descarga y cierre de semana](#5-clip-descarga-y-cierre-de-semana)
6. [Registro de cobranza, tipos de pago y folios](#6-registro-de-cobranza-tipos-de-pago-y-folios)
7. [Comportamiento por rol y asignaciones](#7-comportamiento-por-rol-y-asignaciones)
8. [Autonomía](#8-autonomía)
9. [Customer APP](#9-customer-app)
10. [Ofertas, bundling y niveles de precio (N1/N2/N3)](#10-ofertas-bundling-y-niveles-de-precio-n1n2n3)
11. [Originación de leads y ventas](#11-originación-de-leads-y-ventas)
12. [Clientes eliminados, Profil y rehabilitación](#12-clientes-eliminados-profil-y-rehabilitación)

---

## 1. Estructura organizacional y roles

### 1.1 Jerarquía de territorios y roles — Préstamo Personal

| Territorio | Roles (Personal / Negocio) | Significado | Ejemplo de ID / identificación |
|---|---|---|---|
| Macro región | **CBO** | **Comercial Business Owner** — dueño del negocio comercial de la macro región | ej. Bajío |
| Región | **RSSM** | Regional Sales and Service Manager — Gerente regional de ventas y servicio | ej. Guanajuato |
| Sucursal | **CL / BL** | Comercial Leader — Líder comercial (a nivel sucursal) | ej. 2100 |
| Grupo | **AM / BL** | Area Manager / Business Leader — Gerente de área / Líder de negocio | ej. 2100000000043 (Grupo 1) |
| Sección | **DM / BRM** | Development Manager / Business Relationship Manager — Gerente de desarrollo / Gerente de relación de negocio | ej. 2100000000023 (2100G-G) |
| Agencia | **Estrella** | Star — Comisionista independiente | ej. 2100000000001 (2100000000005) |

> ⚠️ **CBO = "Comercial Business Owner"**, no "Chief Business Officer".

### 1.2 Definiciones por rol (Préstamo Personal)

- **Estrella**: posición operativa más baja; siempre pertenece a una **agencia**. Realiza cobranza y venta en campo.
- **Agencia**: unidad territorial/de clientes asignada a una estrella. Siempre existe como registro en Focus, aunque no tenga estrella asignada (ver [agencia vacante](#33-agencia-vacante---cómo-se-ve-en-los-datos)).
- **DM** (Gerente de Desarrollo / Development Manager): jefe de estrellas, con varias estrellas/agencias a su cargo; pertenece a una sola **sección**.
- **AM** (Gerente de Área / Area Manager): puede tener varios DMs (y por tanto muchas estrellas); pertenece a un solo **grupo**. **BL (Business Leader) es el mismo nivel jerárquico que AM.**
- **DOM** (Gerente Divisional): nivel jerárquico inmediatamente arriba de AM/BL (entre el Grupo y la Región).
- **Gerente Regional**: tiene a su cargo la región (varios DOM/sucursales).
- **Director**: nivel superior a Gerente Regional, antes de CBO.

**Jerarquía resumida (Préstamo Personal):**
`Estrella (Agencia) → DM/BRM (Sección) → AM/BL (Grupo) → DOM (Sucursal) → Gerente Regional (Región) → Director → CBO (Macro región)`

> ⚠️ **Pendiente de confirmar con Negocio**: la tabla 1.1 ubica a **CL/BL** en el nivel Sucursal, mientras que esta jerarquía resumida ubica a **DOM** en Sucursal. Todavía no está confirmado cuál es el nivel exacto de cada rol; ante preguntas sobre este punto, indica que está pendiente de confirmar.

- **Acceso a MyProvi**: solo estrellas, DMs y AMs tienen acceso a la aplicación; posiciones superiores (DOM, Gerente Regional, Director, CBO) no tienen acceso por dependencias de sistema.

### 1.3 Estructura especial de Tijuana

- Usa **BRM** en lugar de DM y **BL (Business Leader)** en lugar de AM; en Tijuana no existe el puesto de AM, el BL realiza esas funciones.
- **Estrella y Asesor son el mismo nivel jerárquico** (el más bajo, operativo en campo); se diferencian únicamente por línea de producto: **Estrella** = Préstamo Personal, **Asesor** = Préstamo Negocio.
- Jerarquía de Tijuana: `Estrella/Asesor → BRM → BL → BO → Director`.
- Para efectos de MyProvi, BRM y BL tienen exactamente las mismas actividades/permisos que DM y AM respectivamente.
- Nota para insumos: la estructura de ventas y servicio (agencia, sección, grupo, sucursal) es distinta entre Tijuana y el resto de sucursales; importante considerarlo al crear estructuras de prueba.

### 1.4 Línea "Préstamo Negocio" (crédito a negocios/comercial)

Misma estructura corporativa, distinto producto:

- **BO** (Business Owner): posición más alta de la línea de negocio (equivalente a "Director" de Préstamo Personal). También existe en la estructura de Tijuana.
- **BL** (Business Leader): mismo nivel que AM, para la línea de negocio (también es el nombre usado para AM en Tijuana).
- **GCN** (Gerente de Crédito Negocio): rol propio de la línea de crédito a negocio.

**Jerarquía resumida (Préstamo Negocio):** `Asesor → GCN → BL → BO → Director`

### 1.5 Línea "Administración"

- **FAM** (Gerente de Administración): cabeza del área de Administración en sucursal ("Head de Administración").
- **OM** (Gerente de Oficina): reporta a FAM.
- **Clerk** (Analista de Administración): reporta dentro del área de Administración.

**Jerarquía resumida:** `Head de Administración → FAM → OM → Clerk`

### 1.6 Línea "Prevención de Pérdidas" (seguridad y servicio al cliente)

- **RSM** (Gerente Regional de Seguridad), **ASM** (Gerente de Área de Seguridad), **SM** (Gerente de Seguridad): jerarquía de seguridad/prevención de pérdidas.
- **CSAM** (Gerente de Área Servicio al Cliente), **TLAC** (Team Leader AC), **AC** (Administrador de Crédito): jerarquía de administración de crédito/servicio al cliente, agrupada bajo el mismo "Head de Prevención de Pérdidas".

**Jerarquía resumida:** `Head de Prevención de Pérdidas → RSM → ASM → SM` (seguridad) y `→ CSAM → TLAC → AC` (crédito/servicio al cliente)

---

## 2. Aplicaciones y acceso

- **MyProvi**: aplicación de grupo usada en 9 países del Grupo IPF. Soporta el proceso de cobranza y es accesible para roles operativos (estrellas, DMs, AMs dependiendo de la estructura y sucursal).
- **MyCollections**: 100% del proceso de cobranza, incluye modo offline.
- **MyTeams**: uso restringido a ciertas posiciones para asignaciones/segmentación de clip; permite al DM asignar el clip completo de una agencia vacante a una estrella, o dividir/segmentar el clip entre varias estrellas.
- **Compatibilidad**: MyProvi se instala en Android; el registro inicial se hace en myprovi.online con ID Focus (13 dígitos) y número celular coincidente (SMS para verificación). Durante el registro se solicita creación de NIP.
- **Restricciones de instalación**: MyCollections se liga a equipo/número; es necesario confirmar desinstalación del equipo anterior para instalar en un nuevo dispositivo; pérdida del equipo puede bloquear acceso hasta acciones administrativas.

---

## 3. Arquitectura de datos: LNFS, Focus y Freud

- **LNFS** (base de datos local por sucursal): cada sucursal tiene su propia base de datos LNFS, identificada con los mismos 4 dígitos que el número de sucursal. Las bases LNFS de las distintas sucursales no están conectadas entre sí.
- Todo lo que se registra durante el día (ventas, cobranza) vive primero en el LNFS de la sucursal correspondiente.
- Por la noche corre un proceso de réplica: se extrae la información de cada LNFS, se concentra y se copia a **Freud** (la réplica/espejo de Focus a nivel consolidado). Por eso comprobantes tipo OP y HC, ofertas, contratos, etc. que dependen de Freud suelen reflejarse hasta el día siguiente.

### 3.1 Reglas de numeración (ID Focus / número de cliente)

Tanto el Focus ID de las estrellas como el número de cliente inician con los 4 dígitos de la sucursal a la que pertenecen.

- **Excepción — clientes transferidos**: si un cliente se dio de alta en la sucursal 2001 (ej. Puebla Dorada) y luego se muda/transfiere a Tijuana (2093), el cliente conserva su número original iniciado en 2001; no se le genera un número nuevo.
- **Estrellas que cambian de sucursal**: a diferencia de los clientes, si una estrella se da de baja de la sucursal 2001 y se da de alta en Tijuana (2093), se le asigna un Focus ID nuevo que inicia con 2093.

### 3.2 Agencia vacante — cómo se ve en los datos

En Focus no existe literalmente la palabra "vacante"; cuando una agencia o sección no tiene responsable asignado, el campo correspondiente simplemente viene vacío/nulo (o en cero). La palabra "vacante" es una traducción que agregan los microservicios cuando detectan ese campo vacío, no un valor que exista así en la base de datos.

---

## 4. Sincronización y modo offline

- MyCollections permite trabajo offline (modo avión). Para que la cobranza registrada en dispositivo llegue a Focus es **obligatorio ejecutar la sincronización**: sin ello, los pagos quedan "atrapados" en el dispositivo.
- **Diferencia de fechas en base de datos**: MyCollections guarda fecha de creación (registro en dispositivo) y Focus guarda fecha de transacción/inserción (cuando sincroniza). Ejemplo: pago registrado a las 16:00 en modo offline y sincronizado a las 16:15, ambas fechas aparecerán distintas.
- Se debe recordar periódicamente a los equipos de campo sincronizar para reflejar avances en reportes corporativos; la barra en la app muestra "última sincronización" (día/hora).
- **Actualización de saldo tras un pago**: para transacciones fuera de clip (DM/AM), el sistema recalcula el nuevo saldo casi de inmediato. Para la estrella normal (con clip), el saldo/balance actualizado en la app solo se refleja hasta el siguiente cambio de semana; mientras tanto, las estrellas llevan manualmente un **"tarjetón"** (hojita física) donde anotan cada semana el folio del pago registrado y van restando manualmente el saldo que el cliente aún debe, hasta que coincide con el balance del sistema en el cambio de semana.

---

## 5. Clip, descarga y cierre de semana

- **Clip**: listado de clientes que la estrella debe descargar (resumen con monto, número de clientes, avance señalado en verde). Incluye no solo la cartera existente sino también las nuevas ventas/transacciones generadas con clientes nuevos y clientes frecuentes desde el cierre/inicio de semana anterior. Descarga requerida al inicio/cambio de semana para ver información actualizada.
- Si la estrella no descarga el clip (por ejemplo en agencia vacante), puede trabajar con el clip anterior pero sin datos actualizados.
- **Botón "Cerrar semana"**: al confirmar impide ingresar más pagos en la aplicación para esa semana (recomendación: cuidado al usarlo). Cierre de semana detona procesos en Provi Digital (mensajes de pesos) y afecta recepción/actualización.
- Al cerrar semana/clip, Focus asigna automáticamente **cero** como cobranza a todos los clientes que no registraron pago (aparecen con cobranza en $0, equivalente a "no pago"); por eso ya no se recomienda usar el botón "No pago" para registrar visitas.

---

## 6. Registro de cobranza, tipos de pago y folios

- **Tipos de botones en cobranza**: pago esperado (tarifa/contrato), último pago, pago manual (permite ingresar mayor o menor monto que el esperado) y no pago (uso restringido: ya no se debe usar "no pago" para registrar visitas por temas en Focus).
- **Folio/recibo**: cada pago genera un número de recibo único e irrepetible (legislación y transparencia). Folio y estructura se generan igual para estrella, DM o AM; la diferencia visible es el identificador de tipo de pago (CO, OP, HC), no el folio en sí.

### 6.1 Clasificación de transacciones (`Agreement_Transaction_Type_Code`)

| Código | Significado |
|---|---|
| **CO** | Cobranza — pagos de estrella vía MyCollections, incluyendo los que un DM/AM cobra por segmentación/asignación de clip de otra agencia (siguen viéndose como CO 100%) |
| **OP** | Pago de oficina — transacción fuera de clip de DM/AM |
| **HC** | Home Credit — créditos otorgados, entregados y cobrados directamente en el domicilio del cliente |

> **"Home Credit" no es solo una etiqueta técnica interna**: es el nombre con el que la empresa matriz de Provident (International Personal Finance) denomina, a nivel internacional, su modelo de negocio principal de crédito puerta a puerta ("crédito a domicilio"). Está pensado principalmente para personas no bancarizadas o que buscan financiamiento rápido sin trámites complicados. El código `HC` en `Agreement_Transaction_Type_Code` hereda ese nombre porque identifica transacciones de ese modelo.

> El prefijo **`RC-`** que se ve en Customer APP **no** es específico de un tipo de transacción — es el formato estándar del campo `Receipt_Reference` (`RC-{Agreement_Transaction_Id}`), aplicable a **cualquier** tipo de transacción (CO, HC u OP). No existe ningún prefijo "TH1".

- **Mapeo técnico de plazo**: `Product_Version_Id` 112 = 12 semanas, 106 = 42 semanas, 131 = 65 semanas.
- **Transacción fuera de clip** (DM/AM): permite buscar cliente por número de cliente (13 dígitos) o número de contrato (9 dígitos). La búsqueda por contrato suele ser más rápida.

---

## 7. Comportamiento por rol y asignaciones

- Roles con acceso pleno a MyProvi/MyCollections: estrella, DMs y AMs (según estructura); líderes comerciales/regionales/CBO no siempre tienen acceso por dependencias sistémicas.
- **Agencia vacante**: el DM puede segmentar o asignar clip desde MyTeams, permitiendo que una estrella cobre clientes de otra agencia; esos registros se visualizan como CO 100% aunque la estrella registre el cobro. El folio conserva su estructura; lo que cambia es el identificador (ej. OP).

---

## 8. Autonomía

Beneficio que permite a algunas estrellas prestar por encima del monto sugerido por el "mensaje de pesos", según su categoría de desempeño y el riesgo del cliente.

- **Categorías de estrella** (de menor a mayor, según cómo manejan su territorio: cuánto venden y cobran): **mini, inter, mega, ultra**.
- Se combina con el grado de riesgo del cliente (categorías **A, B, C, D, E**, siendo A el de menor riesgo).
- Ejemplo: si el cliente tiene riesgo A y la estrella es categoría "ultra", puede prestar más de lo que indica el mensaje de pesos (ej. mensaje dice $5,000, con autonomía podría prestar hasta $10,000).

---

## 9. Customer APP

- Obtiene comprobantes de MyCollections → Focus → tópico (mensaje inmediato cuando llega un pago); los recibos **CO** se ven minutos después si MyCollections sincroniza con Focus.
- Comprobantes tipo **OP y HC**: proceso batch diurno (Focus replica a Freud en la noche; Customer APP consulta Freud al día siguiente para generar el comprobante PDF) — por eso OP y HC pueden verse hasta el día siguiente.
- **Contrato electrónico y estados de cuenta**: el comportamiento esperado es que el contrato electrónico se muestre de inmediato al entrar a Customer APP y dar clic en "contrato electrónico" (la app consulta directo el repositorio donde vive el contrato); no debería depender de ningún proceso batch. Aplica solo a ventas cerradas de forma digital (Provi Digital), no a ventas en papel. Se observó en pruebas que a veces solo aparecía tras disparar el batch de estados de cuenta — posible error a validar, no comportamiento esperado.
- **Referencias de pago**: cuando el cliente consulta su referencia de pago desde Customer APP, la app llama al servicio **Agreement**, que expone un endpoint de "referencias". La referencia se genera con base en el número de sucursal, el número de contrato y un algoritmo que varía según el medio de pago (OXXO o banco).

---

## 10. Ofertas, bundling y niveles de precio (N1/N2/N3)

### 10.1 Ofertas — comportamiento esperado en Customer APP

Customer APP **no** utiliza el "micro de calculadora" para mostrar ofertas (ese micro originalmente traía comportamiento tipo "primera oferta" y causó problemas en pruebas previas). En su lugar, Customer APP consulta directo la tabla/base de datos de ofertas y debe traer siempre la **última oferta vigente**, sin importar el nivel.

### 10.2 Bundling — reglas generales

Estrategia lanzada en **marzo de 2026**. Antes de bundling, Provident no cobraba interés/cargo moratorio por incumplimiento (si el cliente no pagaba una semana, seguía debiendo el mismo monto, sin recargo). Bundling introduce 3 cambios:

1. Cargo moratorio si el cliente deja de pagar.
2. Rebate/descuento por liquidación anticipada.
3. Posibilidad de un nivel de precio más favorable para clientes frecuentes.

- **Cargo por servicio**: Provident cobra un cargo por servicio fijo sobre el préstamo (ej. si el cliente pide $2,000, con un cargo por servicio de $2,100, el total a deber sería $4,100); esta es la base sobre la que luego se calculan descuento/cargo moratorio.
- **Descuento por pago anticipado**: si el saldo total es $4,000, liquidar anticipadamente puede mostrar $3,600 (descuento de $400). El descuento existe desde que se genera el contrato y va disminuyendo semana a semana. El monto se calcula automáticamente por Focus/GDS y se muestra en un banner verde (las reglas/porcentaje exactos no están detallados; sería tema de Riesgos/Créditos).

### 10.3 Niveles de precio N1/N2/N3 — regla completa (⚠️ crítica, no simplificar)

Los niveles de precio dependen de la combinación de: tipo de cliente (Cliente Frecuente **CF** vs. Cliente Nuevo **CN**) y si la sucursal está dentro de la estrategia **Unbundling**. **No son exclusivos de CF** — un cliente nuevo sí puede calificar para algunos niveles, bajo condiciones específicas. Dentro de la escala, **N3 es siempre el mejor precio**.

| Nivel | ¿Aplica a CF? | ¿Aplica a CN (cliente nuevo)? | Condición |
|---|---|---|---|
| **N1** | Sí | **Sí — automático** | Se otorga a **cualquier cliente (CF o CN)** con solo solicitar su crédito en una sucursal dentro de Unbundling. No requiere historial de préstamos. |
| **N2** | Sí | **Sí — solo caso LTPU** | CF: por historial de préstamos (ej. ~4 préstamos). CN: únicamente si el cliente tiene estatus **LTPU** (liquidó un préstamo previo siendo buen pagador) y regresa a solicitar crédito después de cierto tiempo de inactividad — el tiempo exacto está **pendiente de confirmar**. |
| **N3** | Sí | No | Exclusivo de CF con historial de préstamos suficiente; requiere sucursal Unbundling. |

En todos los casos, si la sucursal **no** está dentro de Unbundling, no se otorga ningún nivel N1/N2/N3, sin importar si el cliente es CF o CN.

### 10.4 Sucursales dentro de Unbundling (vigente al 26 de agosto de 2026)

- Aguascalientes
- Zacatecas
- San Luis Potosí II
- Texcoco
- León II
- San Juan del Río
- Chihuahua

> Esta lista puede cambiar conforme se agreguen sucursales al programa. Si la sucursal del cliente no está en esta lista, sus CF **no** deben llevar nivel N1/N2/N3.

---

## 11. Originación de leads y ventas

### 11.1 Leads digitales y en papel

- **Canales de leads digitales**: Facebook y TikTok (formularios de interés), afiliados (empresas que comparten datos de personas interesadas en un préstamo), y **Creditea rejects** (Creditea es una empresa hermana de Provident enfocada en el sector **bancarizado**, mientras Provident atiende al sector **no bancarizado**; cuando Creditea rechaza a un cliente, comparte esos datos con Provident, que evalúa y, si genera una preoferta, se la muestra al prospecto). Toda esta información cae en la **API Lead Management** y, si aprueba reglas, va a CRM para contacto por call center.
- **CRM → Provi Digital**: call center contacta al prospecto, confirma interés y "enviar a campo" crea el lead en Provi Digital (gestión de visitas por estrella). Hasta que no se concrete la venta, el prospecto no es cliente (no tiene número de cliente en Focus).
- **Leads en papel**: para estrellas/sucursales sin acceso a Provi Digital (por falta de internet), el call center notifica el lead por WhatsApp directamente a la estrella (dirección y datos básicos); la venta se genera como cualquier venta en papel.

### 11.2 Ventas en papel vs. Provi Digital

La venta en papel representa aproximadamente el 15-20% del total de ventas (Provi Digital cubre el 80-85% restante).

- **Papel**: la estrella visita al cliente con la hojita **CIS** impresa, llena la solicitud y recaba copia de INE y comprobante de domicilio para armar el expediente. Entrega el expediente a su DM, quien lo entrega a administración de la sucursal. El personal de administración (**OEM/Clerks**) captura el expediente en el sistema **Application Scoring**, que evalúa si se puede prestar al cliente. Si aprueba, se imprime una hojita con la oferta (monto y plazo), se avisa al DM, se genera el contrato (sistema **ABT**) y la estrella entrega al cliente el contrato físico y el dinero. **Los contratos en papel no se digitalizan, por lo que nunca aparecen en Customer APP.**
- **Provi Digital**: flujo 100% digital (fotos de INE, comprobante, scoring, consulta a **Círculo de Crédito** para revisar historial crediticio del prospecto, prueba de vida, GDS). Si la venta se cierra digital, se registra en Focus, se asigna número de cliente y sí aparece en Customer APP.

### 11.3 Formas de entrega del dinero en Provi Digital

- **Orden de pago**: la estrella visita una sola vez al cliente y completa toda la venta (se genera el contrato y llega a Portal Admin).
- **Cheque**: requiere **2 visitas** — en la primera se captura la información y se selecciona recibir por cheque, el flujo se detiene en Provi Digital y pasa a revisión en Portal Admin; si Portal Admin aprueba, el flujo regresa a Provi Digital y la estrella hace una segunda visita para terminar la venta. Es decir, la opción cheque "parte a la mitad" el flujo de venta.

### 11.4 CRM / Dynamics

- **CRM también se conoce como Dynamics** (nombre oficial del sistema). Es donde el call center captura información para generar leads. Muestra un estatus de validación (aprobado/rechazado); si el lead fue rechazado, se habilita una sección con quién lo rechazó y el motivo — útil para que call center dé seguimiento.
- **Tipificación**: clasificación de los leads dentro de CRM (ej. lead de cliente nuevo, lead de cliente frecuente, o "no interesó").
- **Disparadores/notificaciones entre sistemas**: cuando una venta termina en Provi Digital (cliente firma contrato), se notifica a CRM que la venta concluyó. Portal Admin notifica ciertos estatus del expediente; Portal Tesorería notifica si el préstamo ya se dispersó o si fue cancelado; los "portales gerentes" también reciben notificaciones.

---

## 12. Clientes eliminados, Profil y rehabilitación

- **Clientes eliminados (write-off)**: clientes con **más de 17 semanas consecutivas sin pago**. Se les da de baja en Focus (estatus "eliminado") y la información se traspasa mediante carga semanal (equipo de BI) al sistema **Profil**, donde se gestiona la recuperación de cartera.
- **Profil** es utilizado por el call center de recuperación de cartera / cobranza temprana (equipo distinto al call center de ventas). Toda la información sobre si estos clientes eliminados pagan o no vive en Profil.
- **Acceso Customer APP**: los clientes eliminados **no** están visibles en Customer APP, porque su información vive en Profil, sistema no conectado a Customer APP.

### 12.1 Cómo un cliente eliminado vuelve al flujo

1. **Solicita un nuevo préstamo por iniciativa propia**: Provi Digital detecta el estatus "eliminado", pero si tiene el subestatus **PU (pagó)**, lo deja continuar y lo trata como cliente nuevo — se revisa su historial en Círculo de Crédito y, si aplica, se le genera un mensaje de pesos normal.
2. **Campañas especiales del equipo de Crédito y Riesgo**: se "rehabilita" al cliente de forma manual y se le ofrecen mensajes de pesos con características particulares (posiblemente montos menores), generados manualmente.

### 12.2 LTPU

Estatus para clientes con **más de 27 semanas sin tener un préstamo activo**. Ejemplo: un cliente termina de pagar su préstamo; durante 26 semanas el GDS de clientes frecuentes puede seguir generándole mensajes de pesos (si fue buen pagador); si no toma un nuevo préstamo en ese periodo, Focus deja de emitir mensajes; a la semana 28 sin préstamo activo, si solicita un nuevo préstamo, ya no tiene mensaje de cliente frecuente y se trata como cliente nuevo, pasando a estatus **LTPU**.

> ⚠️ Los estatus **LTPU/STPU son, en esencia, un estatus de evaluación de clientes nuevos**; no forman parte de la escala de niveles de precio ni definen por sí solos un nivel. La única intersección es que un cliente nuevo con estatus LTPU que regresa tras un periodo de inactividad puede calificar para **N2** (ver [sección 10.3](#103-niveles-de-precio-n1n2n3--regla-completa--crítica-no-simplificar)). Fuera de ese caso, LTPU/STPU no influyen en N1/N2/N3.
