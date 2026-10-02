USE [AVTs];

/*
================================================================================
PRUEBA INICIAL - 9 OFERTAS (UNA POR ESCENARIO)
================================================================================
Este script actualiza 9 ofertas (la primera de cada escenario) como prueba.

OFERTAS INCLUIDAS:
1. Escenario 1: Cliente 3911780 - $5,000/12sem | Tradicional | Nuevo | SLP
2. Escenario 2: Cliente 3915271 - $4,500/12sem + $10,500/32sem | Tradicional | Frecuente | SLP
3. Escenario 3: Cliente 3935222 - $3,500/12sem | Tradicional | Nuevo | SLP
4. Escenario 4: Cliente 3930704 - $10,500/42sem + $5,000/12sem | Integral | Frecuente | Zacatecas
5. Escenario 5: Cliente 533178 - $7,500/32sem | Integral | Nuevo | Aguascalientes
6. Escenario 6: Cliente 3911266 - $5,500/32sem + $7,500/42sem | Integral | Frecuente | Zacatecas
7. Escenario 7: Cliente 3854562 - $4,000/12sem | Tradicional | Nuevo | Aguascalientes
8. Escenario 8: Cliente 3966802 - $4,000/12sem + $10,500/32sem | Tradicional | Frecuente | Aguascalientes
9. Escenario 9: Cliente 3954461 - $4,000/12sem | Tradicional | Nuevo | Aguascalientes

Fecha: 2026-02-17
================================================================================
*/

-- ============================================================================
-- PASO 1: BACKUP DE DATOS ORIGINALES
-- ============================================================================

PRINT '';
PRINT '=== PASO 1: CREANDO BACKUP DE 9 OFERTAS ===';
PRINT '';

PRINT 'Oferta 1 - Cliente 601022:';
SELECT
    O.Id AS OfferId,
    CONVERT(NVARCHAR(20), O.DataSourceRecordId) AS CustomerIdCS,
    ST.Name AS SaleTypeCS,
    CT.Name AS CustomerTypeCS,
    C.FullName AS CustomerNameCS,
    B.Number AS BranchNumber,
    B.Name AS BranchName,
    AAT.Amount AS Amount,
    PT.Name AS Term,
    cptp.name AS CatPaymentTermTypeName,
    cptp.shouldDisplay AS CatPaymentTermTypeShouldDisplay
FROM Offer O WITH (NOLOCK)
JOIN Branch B WITH (NOLOCK) ON O.BranchId = B.Id
JOIN Customer C WITH (NOLOCK) ON O.CustomerId = C.Id
JOIN CatCustomerType CT WITH (NOLOCK) ON C.CatCustomerTypeId = CT.Id
JOIN CatSaleType ST WITH (NOLOCK) ON O.SalesTypeId = ST.Id
LEFT JOIN AuthorizedAmountAndTerm AAT WITH (NOLOCK) ON O.Id = AAT.OfferId
LEFT JOIN CatPaymentTerm PT WITH (NOLOCK) ON PT.Id = AAT.CatPaymentTermId
LEFT JOIN CatPaymentTermType cptp ON cptp.Id = AAT.CatPaymentTermTypeId
WHERE O.Id = 'BC360B4B-D73A-460F-8240-6541C3531863'
ORDER BY PT.Name DESC;

PRINT '';
PRINT 'Oferta 2 - Cliente 658540:';
SELECT
    O.Id AS OfferId,
    CONVERT(NVARCHAR(20), O.DataSourceRecordId) AS CustomerIdCS,
    ST.Name AS SaleTypeCS,
    CT.Name AS CustomerTypeCS,
    C.FullName AS CustomerNameCS,
    B.Number AS BranchNumber,
    B.Name AS BranchName,
    AAT.Amount AS Amount,
    PT.Name AS Term,
    cptp.name AS CatPaymentTermTypeName,
    cptp.shouldDisplay AS CatPaymentTermTypeShouldDisplay
FROM Offer O WITH (NOLOCK)
JOIN Branch B WITH (NOLOCK) ON O.BranchId = B.Id
JOIN Customer C WITH (NOLOCK) ON O.CustomerId = C.Id
JOIN CatCustomerType CT WITH (NOLOCK) ON C.CatCustomerTypeId = CT.Id
JOIN CatSaleType ST WITH (NOLOCK) ON O.SalesTypeId = ST.Id
LEFT JOIN AuthorizedAmountAndTerm AAT WITH (NOLOCK) ON O.Id = AAT.OfferId
LEFT JOIN CatPaymentTerm PT WITH (NOLOCK) ON PT.Id = AAT.CatPaymentTermId
LEFT JOIN CatPaymentTermType cptp ON cptp.Id = AAT.CatPaymentTermTypeId
WHERE O.Id = '4604355A-F8C7-4338-9EBC-A500DB0439DA'
ORDER BY PT.Name DESC;

PRINT '';
PRINT 'Valores actuales esperados:';
PRINT 'Oferta 1 (601022):';
PRINT '  - Amount: 9200 y 7500 (deben cambiar a 5000 solamente)';
PRINT '  - Term: 42 sem y 32 sem (debe cambiar a 12 sem solamente)';
PRINT '  - PaymentTermTypeName: Normal (debe cambiar a N1)';
PRINT '  - ShouldDisplay: 0 (debe cambiar a 1)';
PRINT '';
PRINT 'Oferta 2 (658540):';
PRINT '  - Amount: 7000 (debe cambiar a 5000)';
PRINT '  - Term: 32 sem (debe cambiar a 12 sem)';
PRINT '  - PaymentTermTypeName: Normal (debe cambiar a N1)';
PRINT '  - ShouldDisplay: 0 (debe cambiar a 1)';
PRINT '';

-- ============================================================================
-- PASO 2: HACER BACKUP DE ESTOS 2 CLIENTES ESPECÍFICOS
-- ============================================================================

PRINT '=== PASO 2: BACKUP DE LOS 2 CLIENTES ===';
PRINT '';

-- Backup de Offer
SELECT * INTO #Backup_Offer
FROM dbo.Offer
WHERE Id IN ('BC360B4B-D73A-460F-8240-6541C3531863', '4604355A-F8C7-4338-9EBC-A500DB0439DA');

-- Backup de AuthorizedAmountAndTerm
SELECT * INTO #Backup_AuthorizedAmountAndTerm
FROM dbo.AuthorizedAmountAndTerm
WHERE OfferId IN ('BC360B4B-D73A-460F-8240-6541C3531863', '4604355A-F8C7-4338-9EBC-A500DB0439DA');

-- Backup de Customer
SELECT C.* INTO #Backup_Customer
FROM dbo.Customer C
JOIN dbo.Offer O ON C.Id = O.CustomerId
WHERE O.Id IN ('BC360B4B-D73A-460F-8240-6541C3531863', '4604355A-F8C7-4338-9EBC-A500DB0439DA');

PRINT '✓ Backup creado en tablas temporales:';
PRINT '  - #Backup_Offer';
PRINT '  - #Backup_AuthorizedAmountAndTerm';
PRINT '  - #Backup_Customer';
PRINT '';

-- ============================================================================
-- PASO 3: DECLARAR VARIABLES
-- ============================================================================

PRINT '=== PASO 3: DECLARACIÓN DE VARIABLES ===';
PRINT '';

DECLARE 
    @Branch_SLP UNIQUEIDENTIFIER = '1D0712B3-DBE1-4872-BB82-0879B123E7EC',
    @SaleType_Tradicional UNIQUEIDENTIFIER = 'F7049160-F367-438C-A0A8-0B63F6B03EBD',
    @CustomerType_Nuevo UNIQUEIDENTIFIER = 'D681D8CC-F364-499A-9322-F6AEDBBF24AE',
    @Term_12sem UNIQUEIDENTIFIER = '81C7FA1C-FFB3-4CF3-AEB7-BDDE1A8A4D6C',
    @Term_32sem UNIQUEIDENTIFIER = '403E89C5-B995-4AA1-8ADA-5B99E0267BB2',
    @Term_42sem UNIQUEIDENTIFIER = 'E2741F66-A665-491E-84AB-EB0DECDA3E8A',
    @PriceLevel_N1 UNIQUEIDENTIFIER = 'B771BFC0-D40A-49A7-8372-72F7776A6338';

PRINT '✓ Variables declaradas correctamente';
PRINT '';

-- ============================================================================
-- PASO 4: APLICAR CAMBIOS A LAS 2 OFERTAS
-- ============================================================================

PRINT '=== PASO 4: APLICANDO CAMBIOS ===';
PRINT '';

-- ============================================================================
-- OFERTA 1: Cliente 601022
-- ============================================================================

PRINT '--- OFERTA 1: Cliente 601022 - CECILIA RODRIGUEZ MALDONADO ---';

-- 4.1: Actualizar Offer
PRINT '4.1 - Actualizando tabla Offer...';
UPDATE dbo.Offer
SET SalesTypeId = @SaleType_Tradicional,
    BranchId = @Branch_SLP
WHERE Id = 'BC360B4B-D73A-460F-8240-6541C3531863';
PRINT '    ✓ Offer actualizada: SaleType=Tradicional, Branch=SLP';
PRINT '';

-- 4.2: Actualizar tipo de cliente
PRINT '4.2 - Actualizando tipo de cliente...';
UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Nuevo
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = 'BC360B4B-D73A-460F-8240-6541C3531863');
PRINT '    ✓ Cliente actualizado: TipoCliente=Nuevo';
PRINT '';

-- 4.3: Eliminar segunda oferta autorizada (32 sem)
PRINT '4.3 - Eliminando segunda oferta autorizada (32 sem)...';
DELETE FROM dbo.AuthorizedAmountAndTerm
WHERE OfferId = 'BC360B4B-D73A-460F-8240-6541C3531863'
  AND CatPaymentTermId = @Term_32sem;
PRINT '    ✓ Segunda oferta eliminada';
PRINT '';

-- 4.4: Actualizar primera oferta (5000/12sem)
PRINT '4.4 - Actualizando primera oferta autorizada (5000/12sem)...';
UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 5000,
    CatPaymentTermId = @Term_12sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = 'BC360B4B-D73A-460F-8240-6541C3531863'
  AND CatPaymentTermId = @Term_42sem;
PRINT '    ✓ Primera oferta actualizada: 5000/12sem/N1';
PRINT '';

-- ============================================================================
-- OFERTA 2: Cliente 658540
-- ============================================================================

PRINT '--- OFERTA 2: Cliente 658540 - JOSE ALFREDO MORALES VEGA ---';

-- 4.5: Actualizar Offer
PRINT '4.5 - Actualizando tabla Offer...';
UPDATE dbo.Offer
SET SalesTypeId = @SaleType_Tradicional,
    BranchId = @Branch_SLP
WHERE Id = '4604355A-F8C7-4338-9EBC-A500DB0439DA';
PRINT '    ✓ Offer actualizada: SaleType=Tradicional, Branch=SLP';
PRINT '';

-- 4.6: Actualizar tipo de cliente
PRINT '4.6 - Actualizando tipo de cliente...';
UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Nuevo
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '4604355A-F8C7-4338-9EBC-A500DB0439DA');
PRINT '    ✓ Cliente actualizado: TipoCliente=Nuevo';
PRINT '';

-- 4.7: Actualizar oferta (5000/12sem)
PRINT '4.7 - Actualizando oferta autorizada (5000/12sem)...';
UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 5000,
    CatPaymentTermId = @Term_12sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '4604355A-F8C7-4338-9EBC-A500DB0439DA'
  AND CatPaymentTermId = @Term_32sem;
PRINT '    ✓ Oferta actualizada: 5000/12sem/N1';
PRINT '';

-- ============================================================================
-- PASO 5: VALIDAR CAMBIOS (DESPUÉS DE LA ACTUALIZACIÓN)
-- ============================================================================

PRINT '=== PASO 5: VALIDACIÓN POST-ACTUALIZACIÓN ===';
PRINT '';

PRINT 'Oferta 1 - Cliente 601022 (después de cambios):';
SELECT
    O.Id AS OfferId,
    CONVERT(NVARCHAR(20), O.DataSourceRecordId) AS CustomerIdCS,
    ST.Name AS SaleTypeCS,
    CT.Name AS CustomerTypeCS,
    C.FullName AS CustomerNameCS,
    B.Number AS BranchNumber,
    B.Name AS BranchName,
    AAT.Amount AS AuthorizedAmount1CS,
    PT.Name AS AuthorizedTerm1CS,
    cptp.name AS CatPaymentTermTypeName,
    cptp.shouldDisplay AS CatPaymentTermTypeShouldDisplay
FROM Offer O WITH (NOLOCK)
JOIN Branch B WITH (NOLOCK) ON O.BranchId = B.Id
JOIN Customer C WITH (NOLOCK) ON O.CustomerId = C.Id
JOIN CatCustomerType CT WITH (NOLOCK) ON C.CatCustomerTypeId = CT.Id
JOIN CatSaleType ST WITH (NOLOCK) ON O.SalesTypeId = ST.Id
LEFT JOIN AuthorizedAmountAndTerm AAT WITH (NOLOCK) ON O.Id = AAT.OfferId
LEFT JOIN CatPaymentTerm PT WITH (NOLOCK) ON PT.Id = AAT.CatPaymentTermId
LEFT JOIN CatPaymentTermType cptp ON cptp.Id = AAT.CatPaymentTermTypeId
WHERE O.Id = 'BC360B4B-D73A-460F-8240-6541C3531863'
ORDER BY PT.Name DESC;

PRINT '';
PRINT 'Oferta 2 - Cliente 658540 (después de cambios):';
SELECT
    O.Id AS OfferId,
    CONVERT(NVARCHAR(20), O.DataSourceRecordId) AS CustomerIdCS,
    ST.Name AS SaleTypeCS,
    CT.Name AS CustomerTypeCS,
    C.FullName AS CustomerNameCS,
    B.Number AS BranchNumber,
    B.Name AS BranchName,
    AAT.Amount AS AuthorizedAmount1CS,
    PT.Name AS AuthorizedTerm1CS,
    cptp.name AS CatPaymentTermTypeName,
    cptp.shouldDisplay AS CatPaymentTermTypeShouldDisplay
FROM Offer O WITH (NOLOCK)
JOIN Branch B WITH (NOLOCK) ON O.BranchId = B.Id
JOIN Customer C WITH (NOLOCK) ON O.CustomerId = C.Id
JOIN CatCustomerType CT WITH (NOLOCK) ON C.CatCustomerTypeId = CT.Id
JOIN CatSaleType ST WITH (NOLOCK) ON O.SalesTypeId = ST.Id
LEFT JOIN AuthorizedAmountAndTerm AAT WITH (NOLOCK) ON O.Id = AAT.OfferId
LEFT JOIN CatPaymentTerm PT WITH (NOLOCK) ON PT.Id = AAT.CatPaymentTermId
LEFT JOIN CatPaymentTermType cptp ON cptp.Id = AAT.CatPaymentTermTypeId
WHERE O.Id = '4604355A-F8C7-4338-9EBC-A500DB0439DA'
ORDER BY PT.Name DESC;

PRINT '';
PRINT '=== CHECKLIST DE VALIDACIÓN ===';
PRINT '';
PRINT 'Verificar que los valores sean:';
PRINT '';
PRINT 'OFERTA 1 (601022):';
PRINT '✓ CustomerIdCS: 601022';
PRINT '✓ SaleTypeCS: Home Credit';
PRINT '✓ CustomerTypeCS: Cliente Nuevo';
PRINT '✓ BranchName: San Luis Potosi 2';
PRINT '✓ AuthorizedAmount1CS: 5000';
PRINT '✓ AuthorizedTerm1CS: 12 sem';
PRINT '✓ CatPaymentTermTypeName: N1';
PRINT '✓ CatPaymentTermTypeShouldDisplay: 1';
PRINT '✓ Solo debe tener 1 registro (segunda oferta eliminada)';
PRINT '';
PRINT 'OFERTA 2 (658540):';
PRINT '✓ CustomerIdCS: 658540';
PRINT '✓ SaleTypeCS: Home Credit';
PRINT '✓ CustomerTypeCS: Cliente Nuevo';
PRINT '✓ BranchName: San Luis Potosi 2';
PRINT '✓ AuthorizedAmount1CS: 5000';
PRINT '✓ AuthorizedTerm1CS: 12 sem';
PRINT '✓ CatPaymentTermTypeName: N1';
PRINT '✓ CatPaymentTermTypeShouldDisplay: 1';
PRINT '';

-- ============================================================================
-- PASO 6: ROLLBACK (SOLO SI ALGO SALIÓ MAL)
-- ============================================================================

PRINT '=== PASO 6: ROLLBACK (EJECUTAR SOLO SI ALGO SALIÓ MAL) ===';
PRINT '';
PRINT 'Si necesitas revertir los cambios, ejecuta los siguientes comandos:';
PRINT '';
PRINT '-- Restaurar AuthorizedAmountAndTerm';
PRINT 'DELETE FROM dbo.AuthorizedAmountAndTerm';
PRINT 'WHERE OfferId IN (''BC360B4B-D73A-460F-8240-6541C3531863'', ''4604355A-F8C7-4338-9EBC-A500DB0439DA'');';
PRINT '';
PRINT 'INSERT INTO dbo.AuthorizedAmountAndTerm';
PRINT 'SELECT * FROM #Backup_AuthorizedAmountAndTerm;';
PRINT '';
PRINT '-- Restaurar Offer';
PRINT 'UPDATE O';
PRINT 'SET O.SalesTypeId = B.SalesTypeId,';
PRINT '    O.BranchId = B.BranchId';
PRINT 'FROM dbo.Offer O';
PRINT 'JOIN #Backup_Offer B ON O.Id = B.Id;';
PRINT '';
PRINT '-- Restaurar Customer';
PRINT 'UPDATE C';
PRINT 'SET C.CatCustomerTypeId = B.CatCustomerTypeId';
PRINT 'FROM dbo.Customer C';
PRINT 'JOIN #Backup_Customer B ON C.Id = B.Id;';
PRINT '';

-- ============================================================================
-- RESUMEN FINAL
-- ============================================================================

PRINT '=== RESUMEN FINAL ===';
PRINT '';
PRINT 'Si la validación es correcta:';
PRINT '1. ✓ Las 2 ofertas del Escenario 1 están actualizadas correctamente';
PRINT '2. ✓ El frontend mostrará la etiqueta N1 visible para ambas';
PRINT '3. ✓ Los montos son $5,000 en 12 semanas (solo 1 oferta cada uno)';
PRINT '4. ✓ Ambas ofertas eliminaron sus segundas ofertas autorizadas';
PRINT '';
PRINT 'Siguiente paso:';
PRINT '→ Si todo está correcto, ejecutar el script completo 0203_UPDATE_18_Ofertas.sql';
PRINT '';

GO
