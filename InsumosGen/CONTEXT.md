# CONTEXT — InsumosGen

> ⚠️ **Source of truth de negocio**: para definiciones de negocio (roles, jerarquía organizacional, aplicaciones MyProvi/MyCollections, tipos de pago, folios, bundling, originación, clientes eliminados, etc.), el documento **`negocio/onboarding_po.txt`** es la fuente autoritativa de trabajo (incluye trazabilidad de quién confirmó cada dato). Su versión curada y sin metadatos de reunión, lista para subir como Knowledge del Gem, es **`negocio/onboarding_po.md`**. Este `CONTEXT.md` documenta principalmente el **esquema técnico de bases de datos** y las convenciones de generación de insumos; cuando haya conflicto entre este archivo y `onboarding_po.txt`/`onboarding_po.md` en temas de negocio, **prevalece la fuente de negocio** (ver sección "⚠️ Discrepancias detectadas" al final).

## 📋 Propósito del Repositorio

Este repositorio contiene artefactos para **generación y mantenimiento de insumos** (principalmente scripts SQL) relacionados con datos/estructuras de **Provident** (empresa de crédito al consumo puerta a puerta), con foco en:

- **Generación de datos de prueba**: Inserción de ofertas, contratos, agencias, representantes, clientes.
- **Documentación de esquemas**: Mapeo completo de bases de datos vía DBML y documentación derivada.
- **Niveles de precio (N1/N2/N3 / Unbundling)**: Generación de ofertas/mensajes de pesos con niveles de precio. La regla de negocio vive solo en `negocio/onboarding_po.md` (sección 10).
- **Scripts de rollback**: Capacidad de revertir cambios en bases de datos.

**Output típico**: Archivos `.sql` listos para ejecutarse en SQL Server desde DBeaver/SSMS. Las corridas ya generadas se guardan en `output/` (nombre de archivo con fecha embebida, ej. `ofertas140926.sql`); no hay una versión "vigente" marcada — revisa la fecha en el nombre para saber cuál es la más reciente de cada tipo.

Las skills de Claude Code que operan sobre este contexto (generación de representantes, recibos de pago, etc.) viven en `../.claude/skills/` (raíz del repo `Providigital_Ventas`), no dentro de esta carpeta.

---

## 🗂️ Estructura del Repositorio

```
InsumosGen/
├── schema/                            # Documentación de esquemas y mapeo de BD
│   ├── InsumosProvident.dbml          # Modelo DBML completo (497KB, 15,617 líneas)
│   └── mapping/                       # Documentación curada del DBML
│       ├── 00_overview.md             # Resumen de esquemas y tipos
│       ├── 01_CNFS_NFS_DBO_core.md    # Entidades core (Agreement, Customer, Rep, Agency)
│       ├── 02_CNFS_NFS_DBO_products_events.md
│       ├── 03_CNFS_NFS_DBO_reference_data.md
│       ├── 04_CNFS_NFS_DBO_org_structure.md
│       ├── 05_app_schemas.md          # Customer App, Pesos Offer, Originación
│       └── 06_relationships.md        # Relaciones FK explícitas e implícitas
│
├── negocio/                           # Fuente de verdad de reglas de negocio
│   ├── onboarding_po.md               # Versión curada, source of truth (subir al Gem)
│   ├── onboarding_po.txt              # Borrador de trabajo con trazabilidad (NO subir al Gem)
│   ├── onboarding_po_call.txt         # Transcripción cruda de la llamada de onboarding (NO subir)
│   ├── gem_tecnico.md                 # Contexto técnico curado para el Gem (esquema + convenciones)
│   └── Tablas de cargo Personal TPB-MK-06 2 (1).pdf   # Disclosure regulatorio CONDUSEF (CAT, amortización)
│
├── generadores/                       # Scripts de generación de datos de prueba
│   ├── Ofertas/                       # Generación de ofertas (múltiples variantes por autor)
│   │   ├── Ofertas.sql
│   │   ├── OfertasUlises.sql
│   │   ├── OfertasLiliana.sql
│   │   ├── Generated/                 # Ofertas generadas ad-hoc
│   │   └── ...
│   ├── Contratos/                     # Generación de contratos
│   │   ├── ContratosLiliana.sql
│   │   └── Generate.sql
│   ├── Users/                         # Generación de usuarios/clientes
│   ├── transactions/                  # Generación de transacciones y recibos de pago
│   ├── AppScoring/                    # Scripts de scoring (Alter_*.sql)
│   ├── Unbundling/                    # Entregable de niveles de precio N1/N2/N3 (histórico)
│   ├── Star Creator.txt               # Generación de estructura organizacional (estrellas/roles)
│   ├── agenciesGenerator.sql
│   ├── caClientGenerator.sql
│   └── folioGenerator.sql
│
├── output/                            # Resultados ya generados, listos para ejecutar (con fecha en el nombre)
├── docs/                              # (vacío - reservado)
│
├── CONTEXT.md                         # Este documento
├── CASCADE.md, GEM_INSTRUCTIONS.md, PROVIPEDIA_TEST_SET.md, SEGURIDAD_GEM.md, instruccionesProvipedia.md
```

---

## 🎯 Dominio y Conceptos Clave

### 1. NFS / CNFS (Sistema Operativo Core)

El DBML documenta el **NFS (National Field System)**, sistema operativo principal de Provident con las siguientes entidades core:

#### Entidades Principales

| Entidad | Descripción | Tabla Principal |
|---------|-------------|-----------------|
| **Customer** | Cliente | `Customer_Table` |
| **Representative** | Asesor/agente de campo | `Representative_Table` |
| **Agency** | Agencia/sección | `Agency_Table` |
| **Agreement** | Contrato de crédito | `Agreement_Table` |
| **Agreement Transaction** | Movimientos del contrato (pagos, cargos) | `Agreement_Transaction_Table` |
| **Role** | Rol organizacional (AM, DM, Star, etc.) | `Role_Table` |
| **Location** | Ubicación física (sucursal) | `Location_Table` |
| **Product / Product Version** | Productos de crédito y versiones | `Product_Table`, `Product_Version_Table` |
| **Element** | Elementos del contrato (principal, interés, seguro) | `Element_Table` |
| **Event** | Eventos que afectan contratos | `Event_Table` |

#### Patrón de Llaves Compuestas

**CRÍTICO**: La mayoría de entidades usan llaves compuestas `(Id, Db_Id)` para soportar bases de datos distribuidas:

```sql
-- Ejemplo:
Agreement_Table (Agreement_Id, Agreement_Db_Id)
Customer_Table (Customer_Id)  -- Excepción: usa solo Customer_Id (bigint)
Representative_Table (Representative_Id)  -- Excepción: usa solo Representative_Id (bigint)
```

#### Columnas de Auditoría Estándar

Todas las tablas en `CNFS_NFS_DBO` incluyen:

| Columna | Tipo | Propósito |
|---------|------|-----------|
| `Dt_Generation_Id` | int | ID de generación |
| `Dt_Transaction_Id` | uniqueidentifier | ID de transacción de negocio |
| `Dt_Write_Bln` | bit | Flag de escritura distribuida |
| `Last_Updated_Datetime` | smalldatetime | Fecha de última actualización |
| `Last_Updated_Id` | bigint | Quién actualizó |
| `Last_Updated_Timestamp` | timestamp | Versión de fila |

**Referencia**: `schema/mapping/00_overview.md`

---

### 2. Esquemas Adicionales (Apps Satélite)

Además del core NFS, existen esquemas para aplicaciones complementarias:

#### Customer_App_jwtprovident
Framework de autenticación JWT para app móvil de clientes.

- **Tablas `arq_*`**: Framework de arquitectura (usuarios, roles, servicios REST, tokens)
- **Tablas `jwt_*`**: Implementación específica de la app
- **Clave**: `arq_usuario.num_cliente_contrato` vincula con NFS

#### Customer_App_pagosprovident
Almacenamiento de recibos de pago.

- **Tabla principal**: `AgreementPayments` (incluye PDF de recibos)
- Vincula con: `Customer_Id`, `Agreement_Id`, `Representative_Id`

#### Pesos_Offer_Originacion
Flujo de originación digital de créditos.

- **Tabla principal**: `ExpedienteClienteVacio` (caso/expediente de originación)
- Tracking completo: desde lead digital hasta dispersión
- Incluye: KYC, documentos, scoring, aprobaciones

#### Pesos_Offer_LeadsDigitales
Captura de leads digitales (web/marketing).

- **Tabla principal**: `tblLeadsDigitales`
- Integración con scoring GDS
- Asignación a sucursales por código postal

#### Pesos_Offer_FloatControlDB
Control de flotante de efectivo y referencias bancarias.

**Referencia**: `schema/mapping/05_app_schemas.md`

---

### 3. Niveles de Precio N1/N2/N3 (Unbundling)

> La regla completa (quién califica a cada nivel, condición LTPU, lista de sucursales Unbundling) vive **únicamente** en `negocio/onboarding_po.md`, secciones 10.3 y 10.4. No se repite aquí para evitar desincronización; consúltala antes de generar insumos con nivel de precio.

Resumen operativo para generación: la sucursal siempre debe estar en la lista Unbundling; sin eso, la oferta no lleva ningún N1/N2/N3.

---

## 🔧 Convenciones y Reglas de Generación

### Reglas Generales para Ofertas (botDB.dbo.Ofertas)

**IMPORTANTE**: Estas reglas están almacenadas en memoria del sistema y deben seguirse al generar ofertas.

#### Formato de INSERT
```sql
INSERT INTO [botDB].[dbo].[Ofertas] ...
```
⚠️ **Siempre usar nombre completo** `[botDB].[dbo].[Ofertas]` para evitar error 208.

#### Campos Clave

| Campo | Formato/Regla | Ejemplo |
|-------|---------------|---------|
| `idOferta` | AAMMM + consecutivo 3 dígitos | 26024001 (año 2026, mes 02, semana 4, consecutivo 001) |
| `semana` | YYYYSS (cambia los MIÉRCOLES) | 202610 (año 2026, semana 10) |
| `FechaActualizacion` | Fecha del día de generación | 2026-03-04 |
| `Customer_Id` | Primeros 4 dígitos agencia + 4 + AAMM + últimos 4 dígitos idOferta (ÚNICO) | 207540260241001 |
| `Agreement_Num` | Solo para RE (REFIN): 510 + AA + 4 + últimos 3 dígitos idOferta | 51026004001 |
| `branchOferta` | Primeros 4 dígitos de agenciaCliente | 2075 |
| `RFC` | Debe coincidir con nombre y fecha de nacimiento | XAXX010101000 |
| `FechaNacimiento` | Aleatoria pero coherente con RFC | 2001-01-01 |
| `nombreCliente` | Aleatorio, único por INSERT | Juan Pérez García |
| `porcentajeCalidadCliente` | Valor entre 76 y 85 | 82 |

#### Sucursales por Tipo

| Tipo | Agencia | Sección | Branch |
|------|---------|---------|--------|
| **SUCURSAL NORMAL** | 2075000000335 | R | 2075 |
| **SUCURSAL FRONTERIZA** | 2093000000111 | A | 2093 |

#### Reglas de Montos

- Para plazos `/12`: `montoOferta <= 5000`
- `montoOferta` debe coincidir con el monto principal en `descOferta`

#### Formato descOferta (mensaje de pesos)

```
TARIFA MÁX <CapacidadPago> <AGREGAR/REFIN! {Contrato}> <monto>/<plazo> [ó <monto>/<plazo>] [nvlRiesgo] [S] [semCredOrig] [PP20/PP25 | N1/N2/N3]
```

**Componentes**:
- `CapacidadPago`: 82-1445 (aleatorio)
- `monto/plazo`: debe ser < 50% de CapacidadPago
- **Plazos válidos**: 12, 32, 42, 52, 65
- `nvlRiesgo`: A (preferente), B, C, D, E, R
- `S`: indica seguro (se omite si no lleva)
- `semCredOrig`: semana crédito original (solo AGREGAR, rango 1-23)
- `PP20/PP25` o `N1/N2/N3`: son **exclusivos** entre sí
- Sin nivel = sin PP ni N en el mensaje

**Ejemplo**:
```
TARIFA MÁX 1200 AGREGAR 4500/52 A S N1
```

---

## 📚 Cómo Navegar el Repositorio

### Para entender esquemas de BD

1. **Inicio rápido**: `schema/mapping/00_overview.md`
2. **Entidades core**: `schema/mapping/01_CNFS_NFS_DBO_core.md`
3. **Relaciones**: `schema/mapping/06_relationships.md`
4. **Apps satélite**: `schema/mapping/05_app_schemas.md`
5. **DBML completo**: `schema/InsumosProvident.dbml` (usar con herramienta DBML o buscar con grep)

### Para generar datos

1. **Ofertas**: Ver ejemplos en `generadores/Ofertas/`
   - `Ofertas.sql`: plantilla base
   - `OfertasUlises.sql`, `OfertasLiliana.sql`: variantes por autor
   - Seguir reglas documentadas en memoria del sistema

2. **Contratos**: Ver `generadores/Contratos/`
   - `ContratosLiliana.sql`: ejemplo completo
   - `Generate.sql`: utilitario

3. **Agencias**: `generadores/agenciesGenerator.sql`

4. **Representantes**: usar la skill de Claude Code `insumo-creator` (`../.claude/skills/insumo-creator/`), que genera el INSERT y su rollback en `output/` (`representative_insert_*.sql` / `representative_rollback_*.sql`, con timestamp).

---

## 🎯 Casos de Uso Comunes

### Generar ofertas de prueba para una sucursal

1. Identificar tipo de sucursal (normal/fronteriza)
2. Usar script base de `generadores/Ofertas/Ofertas.sql`
3. Aplicar reglas de formato (idOferta, Customer_Id, semana)
4. Generar descOferta con formato correcto
5. Ejecutar en DBeaver contra `botDB.dbo.Ofertas`

### Agregar nivel de precio (N1/N2/N3) a una oferta

1. Consultar `negocio/onboarding_po.md` (sección 10) para validar sucursal Unbundling y qué nivel corresponde al tipo de cliente.
2. Incluir el nivel directamente en el mensaje de pesos siguiendo el formato `descOferta` (ver "Formato descOferta"). Es exclusivo con PP20/PP25.

### Crear nueva agencia con representantes

1. Usar `generadores/agenciesGenerator.sql` como base
2. Generar `Agency_Id` único
3. Crear representantes con la skill `insumo-creator` (genera INSERT + rollback en `output/`)
4. Vincular con `Representative_Role_Table`

---

## ⚠️ Advertencias y Consideraciones

### Al trabajar con el DBML

- **Archivo grande**: 497KB, 15,617 líneas
- **Usar herramientas**: dbdiagram.io o buscar con grep/find
- **Preferir mapping/**: documentación curada más fácil de leer

### Al generar scripts SQL

- **Siempre generar rollback**: especialmente para inserts de entidades core
- **Validar unicidad**: `Customer_Id`, `Agreement_Num`, `idOferta` deben ser únicos
- **Respetar FKs**: verificar que entidades referenciadas existen
- **Fechas coherentes**: RFC, fecha de nacimiento, semana contable deben ser consistentes

### Tipos de datos comunes (T_*)

El DBML usa tipos custom definidos en el esquema. Referencia rápida:

- `T_Id` = int
- `T_Db_Id` = smallint
- `T_Nfs_Person_Id` = bigint
- `T_Code` = varchar(2-4)
- `T_Amount` = numeric (montos)
- `T_Boolean` = tinyint
- `T_Delete_Flag` = tinyint (soft delete)

**Ver lista completa**: `schema/mapping/00_overview.md` (líneas 43-79)

---

## 🔗 Referencias Rápidas

| Documento | Ubicación | Propósito |
|-----------|-----------|-----------|
| **DBML completo** | `schema/InsumosProvident.dbml` | Modelo de datos completo |
| **Overview esquemas** | `schema/mapping/00_overview.md` | Resumen de esquemas y tipos |
| **Entidades core** | `schema/mapping/01_CNFS_NFS_DBO_core.md` | Agreement, Customer, Rep, Agency |
| **Relaciones** | `schema/mapping/06_relationships.md` | FKs y relaciones implícitas |
| **Apps satélite** | `schema/mapping/05_app_schemas.md` | Customer App, Pesos Offer, etc. |
| **Ejemplos ofertas** | `generadores/Ofertas/*.sql` | Scripts de generación |
| **Ejemplos contratos** | `generadores/Contratos/*.sql` | Scripts de generación |

---

## 📝 Glosario Provident

> Definiciones completas y con más contexto de negocio en `negocio/onboarding_po.txt` (source of truth). Este glosario es un resumen rápido para navegar el repo técnico.

| Término | Significado |
|---------|-------------|
| **YFOS** | Sistema de campo (app móvil para asesores) |
| **AVTs** | Sistema de ventas y contratos |
| **NFS** | National Field System (sistema operativo core) |
| **Pesos_Offer** | Ofertas en pesos mexicanos |
| **TCis** | Tabla de clientes/prospectos en scoring |
| **DecMessageText** | Mensaje de decisión del motor de scoring |
| **Agreement** | Contrato de crédito |
| **Element** | Componente del contrato (principal, interés, seguro) |
| **Event** | Evento que afecta un contrato (pago, cargo, etc.) |
| **Representative** | Asesor/agente de campo |
| **Agency** | Agencia/sección de venta; siempre existe en Focus aunque no tenga estrella asignada ("agencia vacante" = campo responsable vacío/nulo) |
| **Role** | Rol organizacional — ver tabla completa de jerarquía de territorios/roles en `onboarding_po.txt` (Estrella, DM, AM, DOM, Gerente Regional, Director, CBO; más las líneas de Negocio, Administración y Prevención de Pérdidas) |
| **OM** | Gerente de Oficina, dentro del área de Administración de la sucursal (reporta a FAM) |
| **Clerk** | Analista de Administración, dentro del área de Administración de la sucursal |
| **Estrella / Star** | Posición operativa más baja; realiza venta y cobranza en campo; siempre pertenece a una agencia |
| **DM** | Development Manager (Gerente de Desarrollo) — jefe de estrellas; pertenece a una sección. Equivalente de negocio: BRM |
| **AM** | Area Manager (Gerente de Área) — jefe de DMs; pertenece a un grupo. Mismo nivel que BL (Business Leader) |
| **DOM** | Gerente Divisional — nivel inmediatamente arriba de AM/BL (entre Grupo y Región) |
| **CBO** | Comercial Business Owner — "dueño" del negocio comercial a nivel Macro región (⚠️ no es "Chief Business Officer") |
| **BRM / BL** | Equivalentes de DM/AM en la estructura especial de Tijuana y en la línea de "Préstamo Negocio" (Business Leader hace las funciones de AM). En Tijuana, Estrella y Asesor son el mismo nivel (operativo en campo), diferenciados solo por línea de producto: Estrella = Préstamo Personal, Asesor = Préstamo Negocio |
| **BO** | Business Owner — posición más alta de la línea "Préstamo Negocio" (equivalente a Director en Préstamo Personal); también existe en Tijuana |
| **GCN** | Gerente de Crédito Negocio — rol propio de la línea de crédito a negocio |
| **FAM** | Gerente de Administración — cabeza del área de Administración en sucursal |
| **RSM / ASM / SM** | Jerarquía de seguridad/prevención de pérdidas (Regional / Área / Gerente de Seguridad) |
| **CSAM / TLAC / AC** | Jerarquía de administración de crédito y servicio al cliente (Gerente de Área Servicio al Cliente / Team Leader AC / Administrador de Crédito) |
| **Autonomía** | Beneficio que permite a estrellas de categoría alta (mini/inter/mega/ultra) prestar más del monto sugerido por el mensaje de pesos, combinado con el riesgo del cliente (A-E) |
| **Clip** | Listado de clientes (cartera + nuevas ventas) que la estrella/DM descarga cada semana en MyCollections para cobranza |
| **LNFS** | Base de datos local por sucursal (4 dígitos = número de sucursal); se replica de noche a Freud |
| **Freud** | Réplica/consolidado nocturno de las bases LNFS/Focus |
| **Profil** | Sistema de gestión de recuperación de cartera para clientes eliminados (write-off), alimentado por cargas semanales de BI |
| **LTPU** | Estatus de cliente con más de 27 semanas sin préstamo activo. Su relación con niveles de precio está en `onboarding_po.md` (secciones 10.3 y 12.2) |
| **GDS** | Sistema de scoring crediticio; el GDS de clientes frecuentes genera mensajes de pesos con niveles de precio (reglas en `onboarding_po.md`, sección 10) |
| **KYC** | Know Your Customer (verificación de identidad) |
| **Expediente** | Caso/archivo de originación digital |
| **CIS** | Hoja de solicitud usada en ventas en papel |
| **Dynamics / CRM** | Sistema donde call center gestiona y tipifica leads (mismo sistema, "Dynamics" es el nombre oficial) |

---

## 📌 Confirmaciones cruzadas (documentación técnica alineada con onboarding_po.txt)

- **✅ Roles adicionales (antes punto abierto, ya resuelto — corregido 26-ago-2026)**: la tabla `Roles` (`Pesos_Offer_CognitoRoleAuthorizations`) y `Star Creator.txt` listan roles adicionales — `OM`, `Clerk`, `AC`, `TL`, `CSAM`. Con el "Glosario de Posiciones en Campo" de negocio se confirmó que **sí son roles reales** (no "nunca usados" como se dijo inicialmente): **OM** = Gerente de Oficina y **Clerk** = Analista de Administración (línea Administración); **AC** = Administrador de Crédito y **CSAM** = Gerente de Área Servicio al Cliente (línea Prevención de Pérdidas, junto con el nuevo rol **TLAC** = Team Leader AC). Ver jerarquía completa en `onboarding_po.txt`.
- **⚠️ Corrección de definición — CBO**: `onboarding_po.txt` originalmente definía CBO como "Chief Business Officer"; el glosario oficial de negocio lo define como **"Comercial Business Owner"** (dueño del negocio comercial a nivel Macro región). Ya corregido en `onboarding_po.txt` y en el glosario de este documento.
- **Nueva línea organizacional documentada — "Préstamo Negocio"**: además de la línea de Préstamo Personal (Estrella/DM/AM/DOM), existe una línea paralela para crédito a negocios con roles **BO (Business Owner)**, **BL (Business Leader, mismo nivel que AM)** y **GCN (Gerente de Crédito Negocio)**. Ver `onboarding_po.txt`.
- **Categorías de estrella**: la categoría `ULTRA` (y `GdsCategory`) mencionada en `onboarding_po.txt` (sección Autonomía) se confirma en `agenciesGenerator.sql` (tabla `P_ESTRELLAS_MENSUAL_CATEGORIAS`), consistente con las categorías mini/inter/mega/ultra descritas en la llamada.
- **Agencia vacante**: existe la tabla `AgenciaVacante` en el esquema `Pesos_Offer_Originacion`, consistente con lo explicado en `onboarding_po.txt` (el campo vive vacío/nulo en Focus y el microservicio traduce a "vacante").
- **✅ Nomenclatura de folios/tipo de transacción (antes punto abierto, ya resuelto)**: los scripts `transactions/agreement_transaction_insert.sql`, `transactions/tabla_transacciones_insert.sql` y el skill `payment-receipt-generator` confirman que `Agreement_Transaction_Type_Code` usa **'OP'** (no "PO") para pago de oficina, y **'HC'** para **Home Credit** — créditos otorgados/realizados en el domicilio del cliente (corregido 15-sep-2026: no es "cobranza electrónica" como se documentó originalmente). "Home Credit" es además el nombre que la empresa matriz de Provident (International Personal Finance) usa a nivel internacional para el modelo de negocio de crédito puerta a puerta que opera Provident México — no es solo una etiqueta técnica interna. El prefijo `RC-` visto en Customer APP corresponde al campo `Receipt_Reference` (`Agreement_Transaction_Receipt_Table`), con formato `RC-{Agreement_Transaction_Id}`, aplicable a cualquier tipo de transacción — no es exclusivo de un tipo ni existe el prefijo "TH1". `folioGenerator.sql` maneja folios de **contrato** (prefijo de 2 letras por sucursal, ej. `PR`, `GS`, `EF`), que es un concepto distinto e independiente del tipo de transacción de pago.
- **Tabla de cargo oficial (`Tablas de cargo Personal TPB-MK-06 2 (1).pdf`)**: documento de disclosure regulatorio (CONDUSEF) vigente 1-mar-2025 a 28-feb-2026, con el CAT y la tabla de amortización (préstamo, cargo por servicio, total a pagar, cuotas) por plazo: 12 semanas (CAT ~2139.4%, monto mínimo $1,500), 32/42/52 semanas (CAT 839.6% / 512.9% / 378.7% según plazo, monto desde $2,000), y 65 semanas ("Provident 65", CAT 255.3%, producto para "buen cliente"/CF). Confirma el mecanismo de "cargo por servicio" fijo descrito en `onboarding_po.txt`. Útil como referencia de validación de montos/plazos al generar ofertas, pero no se transcribió completo por ser una tabla numérica extensa (14 páginas).
- **Mapeo técnico de plazo (`Product_Version_Id`)**: 112 = 12 semanas, 106 = 42 semanas, 131 = 65 semanas (confirmado en scripts de `transactions/` y skill `payment-receipt-generator`).

---

**Fecha de creación**: 6 de abril de 2026  
**Última revisión de consistencia con onboarding_po.txt**: 26 de agosto de 2026  
**Versión**: 1.2  
**Mantenido por**: Equipo de Insumos Provident
