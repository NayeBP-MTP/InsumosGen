USE [AVTs];

/*
================================================================================
PRUEBA INDIVIDUAL - CLIENTE DANI
================================================================================
Este script actualiza 1 oferta de prueba con configuración N3.

OFERTA:
- Cliente: 2173448 (YURIDIANA MARIA GALLEGOS BERNAL)
- OfferId: 34017351-8C65-486D-95C1-CCD21A474B97
- Estado Anterior: $8,000/32sem | N3 | Nuevo | Zacatecas (ya actualizado previamente)
- Estado Nuevo: $20,000/52sem | N3 Visible | Frecuente | SLP

Fecha: 2026-02-17
================================================================================
*/

-- Declaración de variables
DECLARE 
    @Branch_SLP UNIQUEIDENTIFIER = '1D0712B3-DBE1-4872-BB82-0879B123E7EC',
    @SaleType_Tradicional UNIQUEIDENTIFIER = 'F7049160-F367-438C-A0A8-0B63F6B03EBD',
    @CustomerType_Frecuente UNIQUEIDENTIFIER = '4819CA7D-5A32-4857-A6B2-12C99D5EA295',
    @Term_32sem UNIQUEIDENTIFIER = '403E89C5-B995-4AA1-8ADA-5B99E0267BB2',
    @Term_42sem UNIQUEIDENTIFIER = 'E2741F66-A665-491E-84AB-EB0DECDA3E8A',
    @Term_52sem UNIQUEIDENTIFIER = 'E1B43A01-C984-4D50-A468-A4E8FCDA1296',
    @PriceLevel_N3 UNIQUEIDENTIFIER = '0383C426-64C5-497E-9E90-779650EEF86C';

-- ============================================================================
-- PASO 1: CONSULTA ESTADO ACTUAL
-- ============================================================================

PRINT '';
PRINT '=== PASO 1: ESTADO ACTUAL DEL CLIENTE 2173448 ===';
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
WHERE O.Id = '34017351-8C65-486D-95C1-CCD21A474B97'
ORDER BY PT.Name DESC;

PRINT '';
PRINT 'Estado esperado ANTES (ya modificado previamente):';
PRINT '  - Amount: 8000';
PRINT '  - Term: 32 sem';
PRINT '  - PaymentTermType: N3';
PRINT '  - CustomerType: Cliente Nuevo';
PRINT '  - Branch: ZACATECAS';
PRINT '  - ShouldDisplay: 1';
PRINT '';

-- ============================================================================
-- PASO 2: BACKUP
-- ============================================================================

PRINT '=== PASO 2: CREANDO BACKUP ===';

IF OBJECT_ID('tempdb..#Backup_Offer') IS NOT NULL DROP TABLE #Backup_Offer;
SELECT * INTO #Backup_Offer FROM dbo.Offer 
WHERE Id = '34017351-8C65-486D-95C1-CCD21A474B97';
PRINT '✓ Backup Offer: ' + CAST(@@ROWCOUNT AS VARCHAR) + ' registro';

IF OBJECT_ID('tempdb..#Backup_Customer') IS NOT NULL DROP TABLE #Backup_Customer;
SELECT C.* INTO #Backup_Customer FROM dbo.Customer C
INNER JOIN dbo.Offer O ON C.Id = O.CustomerId 
WHERE O.Id = '34017351-8C65-486D-95C1-CCD21A474B97';
PRINT '✓ Backup Customer: ' + CAST(@@ROWCOUNT AS VARCHAR) + ' registro';

IF OBJECT_ID('tempdb..#Backup_AuthorizedAmountAndTerm') IS NOT NULL DROP TABLE #Backup_AuthorizedAmountAndTerm;
SELECT * INTO #Backup_AuthorizedAmountAndTerm FROM dbo.AuthorizedAmountAndTerm 
WHERE OfferId = '34017351-8C65-486D-95C1-CCD21A474B97';
PRINT '✓ Backup AuthorizedAmountAndTerm: ' + CAST(@@ROWCOUNT AS VARCHAR) + ' registros';
PRINT '';

-- ============================================================================
-- PASO 3: ACTUALIZACIÓN
-- ============================================================================

PRINT '=== PASO 3: ACTUALIZANDO CLIENTE 2173448 ===';
PRINT '';

-- Actualizar Offer
PRINT 'Actualizando tabla Offer...';
UPDATE dbo.Offer 
SET BranchId = @Branch_SLP,
    SalesTypeId = @SaleType_Tradicional,
    LastUpdate = GETDATE()
WHERE Id = '34017351-8C65-486D-95C1-CCD21A474B97';
PRINT '✓ Offer actualizada';

-- Actualizar Customer
PRINT 'Actualizando tipo de cliente...';
UPDATE dbo.Customer 
SET CatCustomerTypeId = @CustomerType_Frecuente
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '34017351-8C65-486D-95C1-CCD21A474B97');
PRINT '✓ Customer actualizado';

-- Actualizar oferta existente de 32 sem a $20,000/52sem (mantiene N3)
PRINT 'Actualizando oferta de $8,000/32sem a $20,000/52sem...';
UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 20000,
    CatPaymentTermId = @Term_52sem,
    CatPaymentTermTypeId = @PriceLevel_N3
WHERE OfferId = '34017351-8C65-486D-95C1-CCD21A474B97'
  AND CatPaymentTermId = @Term_32sem;
PRINT '✓ Oferta actualizada: $20,000/52sem/N3 (mantiene nivel N3)';
PRINT '';

-- ============================================================================
-- PASO 4: VALIDACIÓN
-- ============================================================================

PRINT '=== PASO 4: VALIDACIÓN POST-ACTUALIZACIÓN ===';
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
    CPTP.ShouldDisplay AS ShouldDisplay,
    O.LastUpdate
FROM dbo.Offer O
INNER JOIN dbo.Customer C ON O.CustomerId = C.Id
INNER JOIN dbo.CatSaleType ST ON O.SalesTypeId = ST.Id
INNER JOIN dbo.CatCustomerType CT ON C.CatCustomerTypeId = CT.Id
INNER JOIN dbo.Branch B ON O.BranchId = B.Id
LEFT JOIN dbo.AuthorizedAmountAndTerm AAT ON O.Id = AAT.OfferId
LEFT JOIN dbo.CatPaymentTerm PT ON AAT.CatPaymentTermId = PT.Id
LEFT JOIN dbo.CatPaymentTermType CPTP ON AAT.CatPaymentTermTypeId = CPTP.Id
WHERE O.Id = '34017351-8C65-486D-95C1-CCD21A474B97'
ORDER BY PT.Name DESC;

PRINT '';
PRINT '=== CHECKLIST DE VALIDACIÓN ===';
PRINT '';
PRINT 'Verificar que los valores sean:';
PRINT '✓ CustomerIdCS: 2173448';
PRINT '✓ CustomerNameCS: YURIDIANA MARIA GALLEGOS BERNAL';
PRINT '✓ SaleTypeCS: Home Credit';
PRINT '✓ CustomerTypeCS: Frecuente';
PRINT '✓ BranchName: San Luis Potosi 2';
PRINT '✓ Amount: 20000';
PRINT '✓ Term: 52 sem';
PRINT '✓ PaymentTermType: N3';
PRINT '✓ ShouldDisplay: 1';
PRINT '✓ Solo debe tener 1 registro (oferta de 42 sem eliminada)';
PRINT '';

-- ============================================================================
-- PASO 5 (OPCIONAL): ROLLBACK
-- ============================================================================

PRINT '=== ROLLBACK (EJECUTAR SOLO SI HAY PROBLEMAS) ===';
PRINT '';
PRINT 'Para revertir los cambios, ejecuta:';
PRINT '';

/*
-- Restaurar AuthorizedAmountAndTerm
DELETE FROM dbo.AuthorizedAmountAndTerm 
WHERE OfferId = '34017351-8C65-486D-95C1-CCD21A474B97';

INSERT INTO dbo.AuthorizedAmountAndTerm
SELECT * FROM #Backup_AuthorizedAmountAndTerm;

-- Restaurar Offer
UPDATE O
SET O.BranchId = B.BranchId,
    O.SalesTypeId = B.SalesTypeId,
    O.LastUpdate = B.LastUpdate
FROM dbo.Offer O
INNER JOIN #Backup_Offer B ON O.Id = B.Id;

-- Restaurar Customer
UPDATE C
SET C.CatCustomerTypeId = B.CatCustomerTypeId
FROM dbo.Customer C
INNER JOIN #Backup_Customer B ON C.Id = B.Id;

PRINT '✓ ROLLBACK completado';
*/

PRINT '';
PRINT '=== SCRIPT COMPLETADO ===';
PRINT '✓ Cliente 2173448 actualizado a $20,000/52sem con Etiqueta N3 Visible';
PRINT '✓ Backup disponible en tablas temporales para rollback';
PRINT '';

GO
