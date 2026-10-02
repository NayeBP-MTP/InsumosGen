USE [AVTs];

/*
================================================================================
VERIFICACIÓN DE TABLAS DE CARGO - DIAGNÓSTICO ESCENARIO 4
================================================================================
Este script verifica si los montos y plazos del Escenario 4 están configurados
en las tablas de cargo (pricing tables) para el tipo de seguro Integral.

PROBLEMA REPORTADO:
- Clientes 3930704 y 3974077 (Escenario 4)
- Configuración: $10,500/42sem + $5,000/12sem | Integral | Zacatecas
- Error Frontend: "No se encontraron montos de préstamo al cliente en las 
  tablas de cargo registradas"

OBJETIVO:
Verificar si estos montos/plazos existen en las tablas de cargo para:
- Tipo de Seguro: Integral (Negocio)
- Sucursal: Zacatecas
- Payment Term Type: N1

Fecha: 2026-02-17
================================================================================
*/

-- ============================================================================
-- PASO 1: VERIFICAR ESTADO ACTUAL DE LOS CLIENTES DEL ESCENARIO 4
-- ============================================================================

PRINT '';
PRINT '=== PASO 1: ESTADO ACTUAL DE CLIENTES ESCENARIO 4 ===';
PRINT '';

SELECT
    O.Id AS OfferId,
    CONVERT(NVARCHAR(20), O.DataSourceRecordId) AS CustomerIdCS,
    C.FullName AS CustomerNameCS,
    ST.Name AS SaleTypeCS,
    CT.Name AS CustomerTypeCS,
    B.Name AS BranchName,
    AAT.Amount AS Amount,
    PT.Name AS Term,
    CPTP.Name AS PaymentTermType,
    CPTP.ShouldDisplay AS ShouldDisplay
FROM dbo.Offer O
INNER JOIN dbo.Customer C ON O.CustomerId = C.Id
INNER JOIN dbo.CatSaleType ST ON O.SalesTypeId = ST.Id
INNER JOIN dbo.CatCustomerType CT ON C.CatCustomerTypeId = CT.Id
INNER JOIN dbo.Branch B ON O.BranchId = B.Id
LEFT JOIN dbo.AuthorizedAmountAndTerm AAT ON O.Id = AAT.OfferId
LEFT JOIN dbo.CatPaymentTerm PT ON AAT.CatPaymentTermId = PT.Id
LEFT JOIN dbo.CatPaymentTermType CPTP ON AAT.CatPaymentTermTypeId = CPTP.Id
WHERE O.Id IN ('0EA85C1D-B199-41AB-82E5-B4EAF8AA5F08', '7E02D10E-2698-415F-A7A7-B5D07478CB3A')
ORDER BY O.DataSourceRecordId, PT.Name DESC;

PRINT '';
PRINT 'Valores esperados:';
PRINT '  Cliente 3930704: $10,500/42sem + $5,000/12sem | Integral | N1 | Zacatecas';
PRINT '  Cliente 3974077: $10,500/42sem + $5,000/12sem | Integral | N1 | Zacatecas';
PRINT '';

-- ============================================================================
-- PASO 2: VERIFICAR TABLAS DE CARGO DISPONIBLES
-- ============================================================================

PRINT '=== PASO 2: VERIFICANDO TABLAS DE CARGO EN LA BASE DE DATOS ===';
PRINT '';

-- Listar todas las tablas que contienen "Pesos" o "Offer" en su nombre
SELECT 
    TABLE_SCHEMA,
    TABLE_NAME,
    TABLE_TYPE
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_NAME LIKE '%Pesos%' 
   OR TABLE_NAME LIKE '%Offer%'
   OR TABLE_NAME LIKE '%Pricing%'
   OR TABLE_NAME LIKE '%Cargo%'
ORDER BY TABLE_NAME;

PRINT '';

-- ============================================================================
-- PASO 3: VERIFICAR CONFIGURACIÓN EN Pesos_Offer (si existe)
-- ============================================================================

PRINT '=== PASO 3: VERIFICANDO CONFIGURACIÓN EN Pesos_Offer ===';
PRINT '';

IF OBJECT_ID('dbo.Pesos_Offer', 'U') IS NOT NULL
BEGIN
    PRINT 'Tabla Pesos_Offer encontrada. Consultando configuración...';
    PRINT '';
    
    -- Verificar estructura de la tabla
    PRINT '--- Estructura de Pesos_Offer ---';
    SELECT 
        COLUMN_NAME,
        DATA_TYPE,
        CHARACTER_MAXIMUM_LENGTH,
        IS_NULLABLE
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = 'Pesos_Offer'
    ORDER BY ORDINAL_POSITION;
    
    PRINT '';
    PRINT '--- Montos disponibles para Integral (Negocio) ---';
    
    -- Buscar configuración para tipo Integral/Negocio
    -- Nota: Ajustar nombres de columnas según la estructura real
    SELECT TOP 100 *
    FROM dbo.Pesos_Offer
    WHERE 1=1
    ORDER BY 1;
    
END
ELSE
BEGIN
    PRINT '⚠ Tabla Pesos_Offer NO encontrada';
    PRINT '';
END

-- ============================================================================
-- PASO 4: VERIFICAR CONFIGURACIÓN EN STAGE_Pesos_Offer (si existe)
-- ============================================================================

PRINT '=== PASO 4: VERIFICANDO CONFIGURACIÓN EN STAGE_Pesos_Offer ===';
PRINT '';

IF OBJECT_ID('dbo.STAGE_Pesos_Offer', 'U') IS NOT NULL
BEGIN
    PRINT 'Tabla STAGE_Pesos_Offer encontrada. Consultando configuración...';
    PRINT '';
    
    SELECT TOP 100 *
    FROM dbo.STAGE_Pesos_Offer
    ORDER BY 1;
    
END
ELSE
BEGIN
    PRINT '⚠ Tabla STAGE_Pesos_Offer NO encontrada';
    PRINT '';
END

-- ============================================================================
-- PASO 5: BUSCAR MONTOS ESPECÍFICOS DEL ESCENARIO 4
-- ============================================================================

PRINT '=== PASO 5: BUSCANDO MONTOS ESPECÍFICOS: $10,500 y $5,000 ===';
PRINT '';

-- Intentar buscar en Pesos_Offer si existe
IF OBJECT_ID('dbo.Pesos_Offer', 'U') IS NOT NULL
BEGIN
    PRINT '--- Buscando $10,500 en Pesos_Offer ---';
    
    DECLARE @sql1 NVARCHAR(MAX);
    SET @sql1 = '
    SELECT TOP 20 *
    FROM dbo.Pesos_Offer
    WHERE 1=1';
    
    -- Agregar filtros dinámicos según columnas disponibles
    IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Pesos_Offer' AND COLUMN_NAME LIKE '%Amount%')
    BEGIN
        SET @sql1 = @sql1 + ' AND (CAST(Amount AS DECIMAL(18,2)) = 10500 OR CAST(Amount AS DECIMAL(18,2)) = 5000)';
    END
    
    IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Pesos_Offer' AND COLUMN_NAME LIKE '%Monto%')
    BEGIN
        SET @sql1 = @sql1 + ' AND (CAST(Monto AS DECIMAL(18,2)) = 10500 OR CAST(Monto AS DECIMAL(18,2)) = 5000)';
    END
    
    EXEC sp_executesql @sql1;
    
    PRINT '';
    PRINT '--- Buscando plazos 42 sem y 12 sem en Pesos_Offer ---';
    
    DECLARE @sql2 NVARCHAR(MAX);
    SET @sql2 = '
    SELECT TOP 20 *
    FROM dbo.Pesos_Offer
    WHERE 1=1';
    
    IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Pesos_Offer' AND COLUMN_NAME LIKE '%Term%')
    BEGIN
        SET @sql2 = @sql2 + ' AND (Term LIKE ''%42%'' OR Term LIKE ''%12%'')';
    END
    
    IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Pesos_Offer' AND COLUMN_NAME LIKE '%Plazo%')
    BEGIN
        SET @sql2 = @sql2 + ' AND (Plazo LIKE ''%42%'' OR Plazo LIKE ''%12%'')';
    END
    
    EXEC sp_executesql @sql2;
END

PRINT '';

-- ============================================================================
-- PASO 6: VERIFICAR CATÁLOGOS RELACIONADOS
-- ============================================================================

PRINT '=== PASO 6: VERIFICANDO CATÁLOGOS RELACIONADOS ===';
PRINT '';

PRINT '--- CatSaleType (Tipos de Seguro) ---';
SELECT * FROM dbo.CatSaleType;

PRINT '';
PRINT '--- CatPaymentTerm (Plazos) ---';
SELECT * FROM dbo.CatPaymentTerm WHERE Name IN ('12 sem', '42 sem');

PRINT '';
PRINT '--- CatPaymentTermType (Niveles de Precio) ---';
SELECT * FROM dbo.CatPaymentTermType WHERE Name = 'N1';

PRINT '';

-- ============================================================================
-- PASO 7: RESUMEN Y RECOMENDACIONES
-- ============================================================================

PRINT '=== PASO 7: RESUMEN Y RECOMENDACIONES ===';
PRINT '';
PRINT 'ANÁLISIS COMPLETADO';
PRINT '';
PRINT 'Revisa los resultados anteriores para determinar:';
PRINT '';
PRINT '1. ¿Existen las tablas Pesos_Offer o STAGE_Pesos_Offer?';
PRINT '2. ¿Están configurados los montos $10,500 y $5,000 en las tablas de cargo?';
PRINT '3. ¿Están configurados los plazos 42 sem y 12 sem?';
PRINT '4. ¿Existe configuración específica para tipo Integral (Negocio)?';
PRINT '5. ¿Existe configuración específica para sucursal Zacatecas?';
PRINT '';
PRINT 'POSIBLES SOLUCIONES:';
PRINT '';
PRINT 'A) Si las tablas de cargo NO tienen estos montos/plazos:';
PRINT '   - Insertar configuración en las tablas de cargo';
PRINT '   - O cambiar los montos del Escenario 4 a valores existentes';
PRINT '';
PRINT 'B) Si las tablas de cargo existen pero no para tipo Integral:';
PRINT '   - Cambiar el tipo de seguro de Integral a Tradicional';
PRINT '   - O agregar configuración para Integral';
PRINT '';
PRINT 'C) Si el problema es con plazos diferentes (42 sem y 12 sem):';
PRINT '   - Cambiar a un solo plazo (ej: solo $10,500/42sem)';
PRINT '   - O verificar lógica del frontend para manejar múltiples plazos';
PRINT '';

GO
