# Contexto Técnico — Bases de Datos e Insumos (Provident México)

> Referencia técnica sobre esquema de bases de datos y convenciones para generar insumos SQL de prueba. **No define reglas de negocio** (roles, niveles de precio, tipos de pago, originación, etc.): para eso prevalece siempre la documentación de onboarding de negocio.

## 1. Sistema core: NFS / CNFS

El **NFS (National Field System)** es el sistema operativo principal de Provident.

| Entidad | Descripción | Tabla principal |
|---------|-------------|-----------------|
| Customer | Cliente | `Customer_Table` |
| Representative | Asesor/agente de campo | `Representative_Table` |
| Agency | Agencia/sección | `Agency_Table` |
| Agreement | Contrato de crédito | `Agreement_Table` |
| Agreement Transaction | Movimientos del contrato (pagos, cargos) | `Agreement_Transaction_Table` |
| Role | Rol organizacional | `Role_Table` |
| Location | Ubicación física (sucursal) | `Location_Table` |
| Product / Product Version | Productos de crédito y versiones | `Product_Table`, `Product_Version_Table` |
| Element | Componentes del contrato (principal, interés, seguro) | `Element_Table` |
| Event | Eventos que afectan contratos | `Event_Table` |

### Llaves compuestas
La mayoría de entidades usan llaves compuestas `(Id, Db_Id)` para soportar bases distribuidas (ej. `Agreement_Table (Agreement_Id, Agreement_Db_Id)`). **Excepciones**: `Customer_Table` usa solo `Customer_Id` (bigint) y `Representative_Table` usa solo `Representative_Id` (bigint).

### Columnas de auditoría estándar (todas las tablas de `CNFS_NFS_DBO`)
| Columna | Tipo | Propósito |
|---------|------|-----------|
| `Dt_Generation_Id` | int | ID de generación |
| `Dt_Transaction_Id` | uniqueidentifier | ID de transacción de negocio |
| `Dt_Write_Bln` | bit | Flag de escritura distribuida |
| `Last_Updated_Datetime` | smalldatetime | Fecha de última actualización |
| `Last_Updated_Id` | bigint | Quién actualizó |
| `Last_Updated_Timestamp` | timestamp | Versión de fila |

### Tipos de datos custom (T_*)
`T_Id` = int · `T_Db_Id` = smallint · `T_Nfs_Person_Id` = bigint · `T_Code` = varchar(2-4) · `T_Amount` = numeric · `T_Boolean` = tinyint · `T_Delete_Flag` = tinyint (soft delete)

### Mapeo técnico de plazo (`Product_Version_Id`)
112 = 12 semanas · 106 = 42 semanas · 131 = 65 semanas.

### Transacciones y folios (técnico)
- `Agreement_Transaction_Type_Code`: `CO`, `OP`, `HC` (significado de negocio en la documentación de onboarding).
- El campo `Receipt_Reference` (`Agreement_Transaction_Receipt_Table`) tiene formato `RC-{Agreement_Transaction_Id}` y aplica a cualquier tipo de transacción.
- Los folios de **contrato** (prefijo de 2 letras por sucursal, ej. `PR`, `GS`, `EF`) son un concepto distinto e independiente del tipo de transacción de pago.

## 2. Esquemas de aplicaciones satélite

- **Customer_App_jwtprovident**: autenticación JWT de la app de clientes. Tablas `arq_*` (framework: usuarios, roles, servicios REST, tokens) y `jwt_*` (específicas de la app). `arq_usuario.num_cliente_contrato` vincula con NFS.
- **Customer_App_pagosprovident**: recibos de pago. Tabla principal `AgreementPayments` (incluye PDF del recibo); vincula con `Customer_Id`, `Agreement_Id`, `Representative_Id`.
- **Pesos_Offer_Originacion**: flujo de originación digital. Tabla principal `ExpedienteClienteVacio` (caso/expediente, desde lead hasta dispersión: KYC, documentos, scoring, aprobaciones). Incluye `AgenciaVacante`.
- **Pesos_Offer_LeadsDigitales**: captura de leads digitales. Tabla principal `tblLeadsDigitales`; integración con scoring GDS y asignación a sucursales por código postal.
- **Pesos_Offer_FloatControlDB**: control de flotante de efectivo y referencias bancarias.
- **Pesos_Offer_CognitoRoleAuthorizations**: tabla `Roles` con los roles del sistema (incluye OM, Clerk, AC, TL, CSAM además de Estrella/DM/AM, etc.).

## 3. Convenciones para generar ofertas (`botDB.dbo.Ofertas`)

Siempre usar el nombre completo `[botDB].[dbo].[Ofertas]` en los INSERT para evitar el error 208.

| Campo | Formato / regla | Ejemplo |
|-------|-----------------|---------|
| `idOferta` | AAMMM + consecutivo de 3 dígitos | 26024001 |
| `semana` | YYYYSS (cambia los miércoles) | 202610 |
| `FechaActualizacion` | Fecha del día de generación | 2026-03-04 |
| `Customer_Id` | 4 primeros dígitos de agencia + 4 + AAMM + últimos 4 dígitos de idOferta (único) | 207540260241001 |
| `Agreement_Num` | Solo para RE (REFIN): 510 + AA + 4 + últimos 3 dígitos de idOferta | 51026004001 |
| `branchOferta` | 4 primeros dígitos de `agenciaCliente` | 2075 |
| `RFC` | Debe coincidir con nombre y fecha de nacimiento | XAXX010101000 |
| `FechaNacimiento` | Aleatoria pero coherente con el RFC | 2001-01-01 |
| `nombreCliente` | Aleatorio, único por INSERT | Juan Pérez García |
| `porcentajeCalidadCliente` | Entre 76 y 85 | 82 |

**Sucursales de prueba**

| Tipo | Agencia | Sección | Branch |
|------|---------|---------|--------|
| Sucursal normal | 2075000000335 | R | 2075 |
| Sucursal fronteriza | 2093000000111 | A | 2093 |

**Montos**: para plazos `/12`, `montoOferta <= 5000`. `montoOferta` debe coincidir con el monto principal de `descOferta`.

**Formato de `descOferta` (mensaje de pesos)**

```
TARIFA MÁX <CapacidadPago> <AGREGAR/REFIN! {Contrato}> <monto>/<plazo> [ó <monto>/<plazo>] [nvlRiesgo] [S] [semCredOrig] [PP20/PP25 | N1/N2/N3]
```

- `CapacidadPago`: 82–1445. `monto/plazo` debe ser < 50% de la capacidad de pago.
- Plazos válidos: 12, 32, 42, 52, 65.
- `nvlRiesgo`: A (preferente), B, C, D, E, R.
- `S`: indica seguro (se omite si no lleva).
- `semCredOrig`: semana del crédito original (solo AGREGAR, rango 1–23).
- `PP20/PP25` y `N1/N2/N3` son **exclusivos** entre sí. Sin nivel = ni PP ni N en el mensaje.
- Qué nivel (N1/N2/N3) corresponde a cada cliente lo define la regla de negocio de niveles de precio (requiere sucursal Unbundling); no se deduce de este documento.

Ejemplo: `TARIFA MÁX 1200 AGREGAR 4500/52 A S N1`

## 4. Buenas prácticas al generar scripts SQL

- Generar siempre un script de rollback, sobre todo para inserts de entidades core.
- Validar unicidad de `Customer_Id`, `Agreement_Num` e `idOferta`.
- Respetar FKs: verificar que las entidades referenciadas existan.
- Mantener coherencia de fechas: RFC, fecha de nacimiento y semana contable.

## 5. Glosario técnico

| Término | Significado |
|---------|-------------|
| **NFS** | National Field System (sistema operativo core) |
| **YFOS** | Sistema de campo (app móvil para asesores) |
| **AVTs** | Sistema de ventas y contratos |
| **Pesos_Offer** | Familia de esquemas de ofertas en pesos |
| **TCis** | Tabla de clientes/prospectos en scoring |
| **DecMessageText** | Mensaje de decisión del motor de scoring |
| **Agreement** | Contrato de crédito |
| **Element** | Componente del contrato (principal, interés, seguro) |
| **Event** | Evento que afecta un contrato (pago, cargo, etc.) |
| **KYC** | Know Your Customer (verificación de identidad) |
| **Expediente** | Caso/archivo de originación digital |
