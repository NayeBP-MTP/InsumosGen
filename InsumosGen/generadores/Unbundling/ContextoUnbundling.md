# Contexto del Proyecto Unbundling - Provident

## 📋 Resumen Ejecutivo

**Proyecto**: Implementación de estrategia de precios diferenciados (Unbundling)  
**Empresa**: Provident (crédito al consumo puerta a puerta)  
**Objetivo**: Segmentar ofertas de crédito en 3 niveles de precio (N1, N2, N3) basados en scoring crediticio

---

## 🎯 Propósito Funcional

### ¿Qué hace este proyecto?

1. **Diferencia precios por riesgo crediticio**: 
   - N1 = Mejor precio (bajo riesgo)
   - N2 = Precio medio (riesgo moderado)
   - N3 = Precio estándar (riesgo alto o sin clasificación)

2. **Propaga la clasificación Unbundling** a través de todo el ciclo de vida del crédito:
   - Scoring inicial → Ofertas → Contratos

3. **Controla visibilidad**: Flag `ShouldDisplay` permite ocultar/mostrar niveles según reglas de negocio

---

## 🗂️ Estructura de Bases de Datos

### 1. BD `AVTs` (Sistema de Ventas y Contratos)

#### Archivos:
- `Alter_CatPeymentTermType_&_Inserts.sql`
- `Alter_[spCustomerSearch].sql`
- `Alter_[spRetrieveContractInfo].sql`
- `Alter_[spRetrieveEmptyContractInfo].sql`

#### Cambios Principales:

**Tabla `CatPaymentTermType`**:
```sql
ADD ShouldDisplay BIT NOT NULL DEFAULT (0)
INSERT: N'N1', N'Nivel de precio 1', ShouldDisplay=1
INSERT: N'N2', N'Nivel de precio 2', ShouldDisplay=1
INSERT: N'N3', N'Nivel de precio 3', ShouldDisplay=1
```

**SP `spCustomerSearch`**:
- Retorna nivel de precio (N1/N2/N3) asociado a cada oferta
- Permite al asesor ver qué condición comercial se autorizó
- JOIN con `CatPaymentTermType` (línea 99)

**SP `spRetrieveContractInfo`**:
- Incluye `PricingLevel` en datos de contrato
- Lógica: Si `ShouldDisplay=1` muestra nombre, sino cadena vacía
- JOIN con `CatPaymentTermType` (línea 149)

---

### 2. BD `Application_Score` (Motor de Scoring)

#### Archivos:
- `Alter_Application_Score.sql`
- `Alter_[sp_Insert_Score_Results]_AppScoring.sql`
- `Alter_[dbo].[spCopyProspects]_AppScoring.sql`

#### Cambios Principales:

**Tabla `TCis`**:
```sql
ADD DecMessageText NVARCHAR(MAX) NULL
```
- Almacena mensaje de decisión del motor de scoring
- Ejemplo: "Aprobado N1", "Aprobado N2", "Aprobado"

**Tabla `TEMPValidatedProspects`**:
```sql
ADD Unbundling NVARCHAR(MAX) NULL
```
- Campo temporal para propagar clasificación

**SP `sp_Insert_Score_Results`**:
- Nuevo parámetro: `@DecMessageText`
- Actualiza `TCis.DecMessageText` con mensaje de decisión

**SP `spCopyProspects`** (CRÍTICO):
```sql
-- Lógica de parseo:
,[Unbundling] = CASE 
    WHEN TC.DecMessageText LIKE '%N1%' THEN 'N1'
    WHEN TC.DecMessageText LIKE '%N2%' THEN 'N2'
    ELSE NULL 
END
```
- Copia prospectos de `Application_Score` a `Geocoverage_YFOS`
- Parsea `DecMessageText` para extraer nivel de precio
- Procesa solo prospectos modificados en últimas 24 horas

---

### 3. BD `Geocoverage_YFOS` (Ofertas y Campañas)

#### Archivos:
- `Alter_Geocoverage_YFOS.sql`
- `Alter_[CargaDatos_ofertas_YFos]_Unbundling.sql`

#### Cambios Principales:

**Tablas modificadas** (todas agregan `Unbundling VARCHAR(25)`):
- `STAGE_Pesos_Offer` (staging de BI)
- `Pesos_Offer` (tabla activa para YFOS)
- `Pesos_Offer_Historic` (histórico)
- `ValiadtedProspects` (prospectos aprobados)
- `ValiadtedProspects_Historic` (histórico)

**SP `CargaDatos_ofertas_YFos`** (ETL diario):
1. Mueve `Pesos_Offer` → `Pesos_Offer_Historic` (registros > 7 días)
2. Limpia `Pesos_Offer` (registros > 7 días)
3. Carga `STAGE_Pesos_Offer` → `Pesos_Offer` (datos frescos)
4. Propaga `Unbundling` en todos los movimientos

---

## 🔄 Flujo Completo del Proceso

```
1. PROSPECTO SOLICITA CRÉDITO
   ↓
2. MOTOR DE SCORING EVALÚA
   → Genera DecMessageText: "Aprobado N1" / "Aprobado N2" / "Aprobado"
   → sp_Insert_Score_Results guarda en TCis
   ↓
3. COPIA A GEOCOVERAGE (job diario)
   → spCopyProspects parsea DecMessageText
   → Extrae 'N1', 'N2' o NULL
   → Inserta en TEMPValidatedProspects → ValiadtedProspects
   ↓
4. CARGA DE OFERTAS (job diario)
   → CargaDatos_ofertas_YFos mueve datos
   → STAGE_Pesos_Offer → Pesos_Offer (con Unbundling)
   ↓
5. ASESOR BUSCA CLIENTE
   → spCustomerSearch retorna ofertas con nivel de precio
   → Ve N1/N2/N3 en la interfaz
   ↓
6. GENERACIÓN DE CONTRATO
   → spRetrieveContractInfo incluye PricingLevel
   → Se imprime contrato con nivel de precio (si ShouldDisplay=1)
```

---

## 📊 Tablas y SPs Modificados

### Resumen de Cambios

| Base de Datos | Objeto | Tipo | Cambio |
|---------------|--------|------|--------|
| AVTs | `CatPaymentTermType` | Tabla | +`ShouldDisplay` BIT, +3 registros (N1,N2,N3) |
| AVTs | `spCustomerSearch` | SP | Retorna nivel de precio |
| AVTs | `spRetrieveContractInfo` | SP | Incluye `PricingLevel` |
| Application_Score | `TCis` | Tabla | +`DecMessageText` NVARCHAR(MAX) |
| Application_Score | `TEMPValidatedProspects` | Tabla | +`Unbundling` NVARCHAR(MAX) |
| Application_Score | `sp_Insert_Score_Results` | SP | Guarda `DecMessageText` |
| Application_Score | `spCopyProspects` | SP | Parsea mensaje y extrae N1/N2 |
| Geocoverage_YFOS | `STAGE_Pesos_Offer` | Tabla | +`Unbundling` VARCHAR(25) |
| Geocoverage_YFOS | `Pesos_Offer` | Tabla | +`Unbundling` VARCHAR(25) |
| Geocoverage_YFOS | `Pesos_Offer_Historic` | Tabla | +`Unbundling` VARCHAR(25) |
| Geocoverage_YFOS | `ValiadtedProspects` | Tabla | +`Unbundling` VARCHAR(25) |
| Geocoverage_YFOS | `ValiadtedProspects_Historic` | Tabla | +`Unbundling` VARCHAR(25) |
| Geocoverage_YFOS | `CargaDatos_ofertas_YFos` | SP | Propaga `Unbundling` en ETL |

---

## 💡 Puntos Clave para Desarrollo

### Lógica de Clasificación
```sql
-- En spCopyProspects:
CASE 
    WHEN DecMessageText LIKE '%N1%' THEN 'N1'
    WHEN DecMessageText LIKE '%N2%' THEN 'N2'
    ELSE NULL 
END
```
⚠️ **Importante**: Si `DecMessageText` no contiene "N1" o "N2", se asigna NULL (se asume N3 o precio estándar)

### Control de Visibilidad
```sql
-- En spRetrieveContractInfo:
CASE 
    WHEN cptt.ShouldDisplay = 1 THEN cptt.Name 
    ELSE '' 
END AS [PricingLevel]
```
- `ShouldDisplay=1`: Muestra nivel en contrato
- `ShouldDisplay=0`: Oculta nivel (retorna cadena vacía)

### Jobs Diarios Requeridos
1. **spCopyProspects**: Copia prospectos de Application_Score a Geocoverage_YFOS
2. **CargaDatos_ofertas_YFos**: ETL de ofertas (STAGE → Pesos_Offer)

---

## 🎯 Implicaciones de Negocio

### Ventajas
- ✅ Pricing basado en riesgo crediticio
- ✅ Flexibilidad comercial (activar/desactivar niveles)
- ✅ Trazabilidad completa (históricos)
- ✅ Integración end-to-end (scoring → contrato)

### Riesgos/Consideraciones
- ⚠️ Lógica de parseo frágil (`LIKE '%N1%'`)
- ⚠️ Datos NULL si mensaje no contiene N1/N2
- ⚠️ Dependencia de jobs diarios
- ⚠️ Impacto en reporteo (actualizar dashboards)

---

## 📁 Ubicación de Archivos

```
c:\Users\nayeli.benitez\Desktop\Objetos Base Datos Avts_Unbundling 1\
└── Objetos Base Datos Avts_Unbundling\
    ├── Avts\
    │   ├── Alter_CatPeymentTermType_&_Inserts.sql
    │   ├── Alter_[spCustomerSearch].sql
    │   ├── Alter_[spRetrieveContractInfo].sql
    │   └── Alter_[spRetrieveEmptyContractInfo].sql
    ├── App_Scoring\
    │   ├── Alter_Application_Score.sql
    │   ├── Alter_[sp_Insert_Score_Results]_AppScoring.sql
    │   └── Alter_[spCopyProspects]_AppScoring.sql
    └── Geocoverage\
        ├── Alter_Geocoverage_YFOS.sql
        └── Alter_[CargaDatos_ofertas_YFos]_Unbundling.sql
```

---

## 🔍 Glosario Provident

- **YFOS**: Sistema de campo (app móvil para asesores)
- **AVTs**: Sistema de ventas y contratos
- **Pesos_Offer**: Ofertas en pesos mexicanos
- **TCis**: Tabla de clientes/prospectos en scoring
- **DecMessageText**: Mensaje de decisión del motor de scoring
- **ShouldDisplay**: Flag para controlar visibilidad de niveles
- **Unbundling**: Clasificación de nivel de precio (N1/N2/NULL)

---

**Fecha de análisis**: 12 de febrero de 2026  
**Analista**: Cascade AI  
**Versión**: 1.0
