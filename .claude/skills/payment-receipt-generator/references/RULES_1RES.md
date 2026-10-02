# Resumen Ejecutivo - Sesión de Entendimiento de Negocio Provident

**Fecha:** 20 de abril de 2026  
**Duración:** 117 minutos  
**Objetivo:** Transferencia de conocimiento sobre procesos de cobranza, pagos, ventas y estructura organizacional de Provident

---

## 1. PROCESO DE COBRANZA - MyProvi

### 1.1 Aplicaciones del Ecosistema MyProvi
- **MyProvi**: Conjunto de aplicaciones para el proceso de cobranza a nivel grupo (9 países)
- **MyCollections**: Aplicación donde se ejecuta 100% el proceso de cobranza
- **MyTeams**: Aplicación para ciertas posiciones gerenciales

### 1.2 Usuarios con Acceso
- **Estrellas**: Agentes de campo que realizan cobranza
- **DM (Development Manager)**: Gerentes de desarrollo
- **AM (Area Manager)**: Gerentes de área
- **Equivalencias Tijuana**: BRM y BL (mismas funciones que DM y AM)

### 1.3 Características Técnicas
- **Plataforma**: Android únicamente
- **Registro**: Requiere ID Focus (13 dígitos) y número celular actualizado
- **Sincronización**: Automática con Wi-Fi o manual
- **Modo offline**: Permite trabajar sin conexión, pero requiere sincronización posterior
- **NIP**: Se requiere crear un NIP para interactuar con la aplicación

### 1.4 Proceso de Cobranza - CLIP

**CLIP (Listado de Clientes)**
- Se descarga al inicio de cada semana
- Contiene clientes nuevos, frecuentes y transacciones de cobranza
- Requiere conexión a Internet para descarga
- Muestra: monto de cobranza, número de clientes, avance semanal

**Cierre de Semana**
- Botón crítico que bloquea el ingreso de nuevos pagos
- Detona la generación de mensajes de pesos en Provi Digital
- Focus asigna automáticamente "cero" a clientes sin pago registrado (no pago)

### 1.5 Registro de Pagos

**Opciones de Pago (Estrella)**
1. Pago de la semana anterior
2. Pago esperado (tarifa/contrato)
3. Pago manual (monto personalizado)
4. No pago (ya no se utiliza por restricciones de Focus)

**Transacción Fuera de CLIP**
- Solo para DM y AM
- Búsqueda por número de cliente (13 dígitos) o contrato (9 dígitos)
- Búsqueda por contrato es más rápida

### 1.6 Folios y Recibos

**Características del Folio**
- Único e irrepetible por usuario y pago
- Se genera automáticamente al registrar el pago
- Requiere firma del cliente
- Información incluida: monto, usuario, fecha y hora

**Sincronización de Datos**
- **Fecha de creación**: Cuando se registra en MyCollections
- **Fecha de transacción**: Cuando se sincroniza con Focus
- Puede haber diferencia entre ambas fechas si no se sincroniza inmediatamente

---

## 2. TIPOS DE PAGO Y COMPROBANTES

### 2.1 Clasificación de Pagos

| Tipo | Código | Descripción | Proceso |
|------|--------|-------------|---------|
| Cobranza Electrónica | CEO | Pagos registrados en MyCollections | Inmediato (minutos) |
| Pago de Oficina | PO | Pagos en sucursal | Día siguiente (D+1) |
| Home Credit | HC | Créditos otorgados/realizados en el domicilio del cliente (no es "cobranza electrónica") | Día siguiente (D+1) |

### 2.2 Generación de Comprobantes

**CEO (MyCollections)**
- Conexión directa: MyCollections → Focus → Customer App
- Generación inmediata (minutos después de sincronización)
- Requiere que la estrella sincronice primero

**PO y HC**
- Proceso batch diario que consulta Freud
- Freud replica información de Focus a día vencido (D+1)
- Customer App genera recibo al detectar nuevo pago en Freud
- Réplica de Focus a Freud ocurre en las noches

### 2.3 Identificadores de Folio
- **CEO**: Identificador específico (pendiente confirmar estructura)
- **PO**: Inicia con RC + consecutivo (pendiente confirmar)
- **HC**: Folios largos, requieren ajuste en comprobante (pendiente confirmar estructura exacta)

---

## 3. ARQUITECTURA DE DATOS

### 3.1 Sistema Focus y LNFS

**LNFS (Local New File System)**
- Cada sucursal tiene su propia base de datos LNFS
- Formato: 4 dígitos de sucursal (ej: 2001, 2093)
- No están conectadas entre sí en tiempo real
- Réplica nocturna consolida información en Freud

**Proceso de Réplica**
1. Durante el día: Datos viven en LNFS de cada sucursal
2. En la noche: Proceso extrae información de cada LNFS
3. Se consolida toda la información en Freud
4. Freud queda disponible al día siguiente (D+1)

### 3.2 Conexiones de Sistemas

**MyProvi → Focus**
- Única aplicación que escribe directamente en Focus
- Conexión en tiempo real

**Customer App → Tópico**
- Customer App se conecta a un tópico
- Genera recibo al detectar nuevo pago
- Para PO y HC: consulta diaria a Freud

---

## 4. ESTRUCTURA ORGANIZACIONAL

### 4.1 Jerarquía de Ventas y Servicio (Sucursales Normales)

```
Estrella → Agencia → DM → AM → Líder Comercial → Regional → CBEO
```

**Relaciones Clave**
- Una estrella siempre debe pertenecer a una agencia
- Una agencia puede estar vacante
- DM y AM no tienen acceso a MyProvi si están en posiciones superiores

### 4.2 Estructura Tijuana (Fronteriza)

**Equivalencias**
- DM = BRM (Branch Relationship Manager)
- AM = BL (Branch Leader)
- Mismas funcionalidades, nomenclatura diferente

### 4.3 Identificadores Focus

**Formato ID Focus**
- Inicia con 4 dígitos de sucursal
- Estrellas: ID siempre corresponde a sucursal actual
- Clientes: Conservan ID original si se transfieren de sucursal

**Ejemplo**
- Cliente nace en sucursal 2001 (Puebla)
- Se transfiere a sucursal 2093 (Tijuana)
- Conserva ID iniciando con 2001

---

## 5. PROCESO DE VENTAS - PROVI DIGITAL

### 5.1 Flujo de Leads (CRM/Dynamics)

**Origen de Leads**
- Call Center genera leads en CRM
- Se envían a Provi Digital para procesamiento
- CRM recibe actualizaciones de estatus del lead

**Estatus de Lead**
- En validación
- Aprobado
- Rechazado (incluye motivo y usuario que rechazó)
- Cancelado

### 5.2 Tipificación en CRM

**Clasificación de Leads**
- Cliente nuevo
- Cliente frecuente
- Motivo de rechazo
- Información de seguimiento para Call Center

### 5.3 Métodos de Entrega de Dinero

**Orden de Pago**
- Proceso completo en una visita
- Venta se completa inmediatamente
- Contrato se genera y llega a Portal Admin

**Cheque**
- Requiere 2 visitas de la estrella
- Primera visita: Genera información, selecciona cheque
- Flujo se detiene y pasa a Portal Admin para revisión
- Si Admin aprueba: Regresa a Provi Digital
- Segunda visita: Estrella completa la venta

### 5.4 Notificaciones entre Sistemas

**Provi Digital → CRM**
- Al finalizar venta (firma de contrato)
- Actualización de estatus

**Portal Admin**
- Notifica estatus de aprobación/rechazo
- Información de dispersión

**Portal Tezo**
- Notifica si préstamo fue dispersado o cancelado

---

## 6. CONTRATOS Y CUSTOMER APP

### 6.1 Contrato Electrónico

**Disponibilidad**
- Visible inmediatamente si venta fue en Provi Digital
- Se almacena en repositorio de contratos
- Cliente puede verlo en Customer App al ingresar
- Contratos en papel nunca estarán disponibles electrónicamente

### 6.2 Estado de Cuenta

**Generación**
- Proceso batch construye estado de cuenta
- No es inmediato como el contrato electrónico
- Requiere que proceso se ejecute para visualización

---

## 7. ESTRATEGIA UNBUNDLING

### 7.1 Características Principales

**Fecha de Implementación**: Marzo 2026

**Componentes**
1. **Penalización**: Cargo moratorio por no pago
2. **Beneficio 1**: Descuento por liquidación anticipada
3. **Beneficio 2**: Nivel de precio más bajo para clientes frecuentes

### 7.2 Descuento por Liquidación Anticipada

**Funcionamiento**
- Descuento calculado automáticamente por Focus
- Se genera desde el momento de creación del contrato
- Disminuye cada semana conforme avanza el préstamo
- Visible en Customer App (banner verde - Early Settlement Balance)
- Campo en base de datos: `rebate_value`

**Ejemplo**
- Préstamo: $2,000
- Cargo por servicio: $2,100
- Total a deber: $4,100
- Con descuento liquidación: $3,600 (descuento de $500)

### 7.3 Niveles de Precio (Pricing)

**N1, N2, N3**
- N3 es el nivel más alto (paga menos)
- Asignado según número de préstamos del cliente
- N2: Clientes frecuentes con ~4 préstamos
- Generado automáticamente por GDS de Focus

### 7.4 Visualización en MyProvi

**Sucursales con Unbundling**
- Muestran saldo total por pago anticipado
- Balance total (sin descuento)
- Cargo moratorio (línea adicional)
- Suma: pago esperado + tarifa + cargo moratorio

---

## 8. AUTONOMÍA DE ESTRELLAS

### 8.1 Concepto

**Definición**: Beneficio que permite a estrellas prestar más del mensaje de pesos según su categoría

### 8.2 Factores que Determinan Autonomía

**Categoría de Estrella**
- Ultra (más alta)
- Mega
- Inter
- Mini
- Basada en: ventas, monto vendido, cobranza

**Grado de Riesgo del Cliente**
- A: Menor riesgo (preferente)
- B, C, D, E
- R: Riesgo alto

### 8.3 Aplicación

**Ejemplo**
- Mensaje de pesos: $5,000
- Cliente con riesgo A + Estrella categoría Ultra
- Autonomía permite prestar: $10,000

**Relevancia para Insumos**
- Solo importante si se va a probar funcionalidad de autonomía
- Si no se prueba autonomía: grado de riesgo no es relevante

---

## 9. CLIENTES ELIMINADOS Y WRITE-OFF

### 9.1 Definición de Cliente Eliminado

**Criterio**: 17+ semanas consecutivas sin pago

**Proceso**
1. Cliente deja de pagar por 17 semanas
2. Focus le asigna estatus "Eliminado" (Write-off)
3. Información se transfiere a sistema Profil
4. Equipo de recuperación de cartera gestiona en Profil

### 9.2 Sistema Profil

**Características**
- Sistema de recuperación de cartera
- Utilizado por Call Center de recuperación
- No es el mismo Call Center de ventas
- Provident no tiene acceso directo actualmente

### 9.3 Rehabilitación de Clientes

**Opción 1: Solicitud Nueva**
- Cliente solicita nuevo préstamo
- Provi Digital detecta estatus eliminado
- Si tiene subestatus "PU" (Paid Up - pagó): permite continuar
- Se trata como cliente nuevo
- Se consulta círculo de crédito
- Se genera nuevo mensaje de pesos

**Opción 2: Campaña Especial**
- Equipo de Crédito y Riesgo genera campaña
- Mensajes de pesos con características especiales
- Montos limitados (ej: $3,000)
- Generación manual
- No llegan por base de datos de Bot TV

### 9.4 Consideraciones para Insumos

**Customer App**
- No muestra información de clientes eliminados
- Información vive en Profil (sistema no conectado)
- Cliente eliminado no puede ingresar a Customer App

**Adeudo Visible**
- Es correcto que cliente eliminado muestre adeudo
- No es un error de datos
- Cliente puede tener oferta aun con deuda pendiente

---

## 10. ESTATUS LTPU Y STPU

### 10.1 Definición LTPU (Long-Term Past User)

**Criterio**: 27+ semanas sin préstamo activo

**Proceso**
1. Cliente termina de pagar préstamo
2. Durante 26 semanas: GDS genera mensajes de pesos como cliente frecuente
3. Si no acepta en 26 semanas: GDS deja de generar mensajes
4. Semana 28+: Cliente pasa a estatus LTPU
5. Si solicita nuevo préstamo: se trata como cliente nuevo

### 10.2 Aplicación

**Uso Principal**: Evaluación de clientes nuevos
- No relacionado con nivel de precio
- Importante para flujo de cliente nuevo
- Cliente LTPU pierde mensajes de cliente frecuente

---

## 11. REGLAS DE NEGOCIO CLAVE

### 11.1 Asignación de CLIP

**Segmentación**
- DM puede asignar CLIP completo a estrella de otra agencia
- DM puede dividir CLIP entre múltiples estrellas
- Todos los pagos de estrella con CLIP asignado se registran como CEO
- Folio mantiene misma estructura independiente de posición

### 11.2 Actualización de Saldos

**Para Estrellas (con CLIP)**
- Actualización semanal al cambio de semana
- Tarjetón manual para seguimiento entre semanas
- Estrella anota folio y calcula saldo manualmente

**Para DM/AM (Transacción fuera de CLIP)**
- Actualización inmediata del saldo (cambio reciente por Unbundling)
- Anteriormente también era semanal

### 11.3 Resumen de Cliente

**Información Mostrada**
- Múltiples contratos activos (si aplica)
- Atrasos consecutivos (no pagos)
- Acuerdos de pago registrados
- Fecha inicio/fin de contrato
- Tarifa en contrato (sumatoria si hay múltiples)
- Pago total esperado (sumatoria si hay múltiples)

---

## 12. CONSIDERACIONES TÉCNICAS PARA EQUIPO DE INSUMOS

### 12.1 Fechas en Base de Datos

**Dos Fechas Importantes**
- **Fecha de creación**: Registro en MyCollections (4:00 PM)
- **Fecha de transacción**: Inserción en Focus (4:15 PM)
- Diferencia causada por sincronización

### 12.2 Estructura de Sucursales

**Sucursal Normal**
- Agencia: 2075000000335
- Sección: R
- Branch: 2075

**Sucursal Fronteriza (Tijuana)**
- Agencia: 2093000000111
- Sección: A
- Branch: 2093

### 12.3 Validaciones Importantes

**Contratos**
- Verificar si venta fue en Provi Digital (contrato electrónico disponible)
- Contratos en papel nunca estarán en Customer App

**Comprobantes**
- CEO: Inmediato tras sincronización
- PO/HC: Día siguiente (D+1)
- Verificar proceso batch para estado de cuenta

### 12.4 Clientes Transferidos

**Escenario Común**
- Cliente conserva ID original de sucursal de origen
- ID no cambia al transferirse
- Puede causar inconsistencia entre ID y sucursal actual

---

## 13. PENDIENTES Y SEGUIMIENTOS

### 13.1 Información por Confirmar

1. **Estructura exacta de folios**
   - Patrón para PO (¿inicia con RC?)
   - Patrón para HC (folios largos)
   - Contacto: Emma Montufar (acceso a bases de datos)

2. **Nivel de Precio - Reglas Detalladas**
   - Tabla de asignación N1, N2, N3
   - Número exacto de préstamos por nivel
   - Contacto: Yadi (experta en pricing)

3. **Cálculo de Descuento Unbundling**
   - Fórmula exacta de cálculo
   - Reglas de negocio específicas
   - Generado automáticamente por Focus

### 13.2 Dudas Técnicas Pendientes

1. **Proceso de Estado de Cuenta**
   - Horarios exactos de ejecución batch
   - Contacto: Emmanuel, Erick (DevOps)

2. **Réplica Focus → Freud**
   - Horarios específicos de réplica nocturna
   - Contacto: Emma Montufar, Paco

3. **Tabla LTPU**
   - Nombre exacto: GDS Customer Data (confirmar)
   - Estructura y campos disponibles

---

## 14. CONTACTOS CLAVE

| Área | Contacto | Especialidad |
|------|----------|--------------|
| Negocio - Cobranza | Liliana Galicia | Procesos generales, estructura |
| Negocio - Cobranza | Prisma Sanchez | MyProvi, MyCollections |
| Negocio - Cobranza | Marisol Barrera | Procesos de pago |
| Pricing/Ofertas | Yadi | Niveles de precio, estrategias |
| Técnico - Bases de Datos | Emma Montufar | Estructura de datos, folios |
| Técnico - DevOps | Emmanuel, Erick | Procesos batch, réplicas |
| Customer App | Core Morales | Funcionalidad, validaciones |

---

## 15. GLOSARIO DE TÉRMINOS

| Término | Definición |
|---------|------------|
| CLIP | Listado de clientes para cobranza semanal |
| CEO | Cobranza Electrónica (MyCollections) |
| PO | Pago de Oficina (sucursal) |
| HC | Home Credit — créditos otorgados/realizados en el domicilio del cliente |
| LNFS | Local New File System - Base de datos por sucursal |
| Freud | Sistema de réplica consolidada de Focus |
| GDS | Sistema generador de mensajes de pesos |
| Profil | Sistema de recuperación de cartera |
| Unbundling | Estrategia con cargos moratorios y descuentos |
| LTPU | Long-Term Past User (27+ semanas sin préstamo) |
| Write-off | Cliente eliminado (17+ semanas sin pago) |
| PU | Paid Up - Cliente que pagó su deuda |
| DM | Development Manager |
| AM | Area Manager |
| BRM | Branch Relationship Manager (equivalente DM en Tijuana) |
| BL | Branch Leader (equivalente AM en Tijuana) |

---

**Documento generado:** 21 de abril de 2026  
**Fuente:** Transcripción de sesión de entendimiento de negocio (20/04/2026)  
**Equipo:** Insumos, QA, Arquitectura, Negocio Provident
