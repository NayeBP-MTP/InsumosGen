USE [AVTs];

/*
================================================================================
PRUEBA INDIVIDUAL - CLIENTE NUEVO (DIFERENTE A LAS 19 OFERTAS ANTERIORES)
================================================================================
Este script actualiza 1 oferta de prueba con configuración N1 Integral.

OFERTA:
- Cliente: 891736 (JOSE LUIS MARTINEZ CONTRERAS)
- OfferId: 1C607A40-B6FD-4E45-97A6-EDC8DD6A2CB8
- Estado Actual: $2,500/12sem | N2 | Nuevo | Aguascalientes
- Estado Deseado: $3,500-$7,500/32sem | N1 Visible | Nuevo | Aguascalientes | Integral

Fecha: 2026-02-17
================================================================================
*/

-- Declaración de variables
DECLARE 
    @Branch_Aguascalientes UNIQUEIDENTIFIER = '7AE76DAF-08C3-43FB-B3E4-455E64AED01C',
    @SaleType_Integral UNIQUEIDENTIFIER = '21BE783E-8B08-405D-A449-A21FABC8E113',
    @CustomerType_Nuevo UNIQUEIDENTIFIER = 'D681D8CC-F364-499A-9322-F6AEDBBF24AE',
    @Term_12sem UNIQUEIDENTIFIER = '81C7FA1C-FFB3-4CF3-AEB7-BDDE1A8A4D6C',
    @Term_32sem UNIQUEIDENTIFIER = '403E89C5-B995-4AA1-8ADA-5B99E0267BB2',
    @PriceLevel_N1 UNIQUEIDENTIFIER = 'B771BFC0-D40A-49A7-8372-72F7776A6338';

-- ============================================================================
-- PASO 1: CONSULTA ESTADO ACTUAL
-- ============================================================================

PRINT '';
PRINT '=== PASO 1: ESTADO ACTUAL DEL CLIENTE 891736 ===';
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
WHERE O.Id = '1C607A40-B6FD-4E45-97A6-EDC8DD6A2CB8'
ORDER BY PT.Name DESC;

PRINT '';
PRINT 'Estado esperado ANTES:';
PRINT '  - Amount: 2500';
PRINT '  - Term: 12 sem';
PRINT '  - PaymentTermType: N2';
PRINT '  - CustomerType: Cliente Nuevo';
PRINT '  - Branch: AGUASCALIENTES 1';
PRINT '  - SaleType: Home Credit';
PRINT '  - ShouldDisplay: 1';
PRINT '';

-- ============================================================================
-- PASO 2: BACKUP
-- ============================================================================

PRINT '=== PASO 2: CREANDO BACKUP ===';

IF OBJECT_ID('tempdb..#Backup_Offer') IS NOT NULL DROP TABLE #Backup_Offer;
SELECT * INTO #Backup_Offer FROM dbo.Offer 
WHERE Id = '1C607A40-B6FD-4E45-97A6-EDC8DD6A2CB8';
PRINT '✓ Backup Offer: ' + CAST(@@ROWCOUNT AS VARCHAR) + ' registro';

IF OBJECT_ID('tempdb..#Backup_Customer') IS NOT NULL DROP TABLE #Backup_Customer;
SELECT C.* INTO #Backup_Customer FROM dbo.Customer C
INNER JOIN dbo.Offer O ON C.Id = O.CustomerId 
WHERE O.Id = '1C607A40-B6FD-4E45-97A6-EDC8DD6A2CB8';
PRINT '✓ Backup Customer: ' + CAST(@@ROWCOUNT AS VARCHAR) + ' registro';

IF OBJECT_ID('tempdb..#Backup_AuthorizedAmountAndTerm') IS NOT NULL DROP TABLE #Backup_AuthorizedAmountAndTerm;
SELECT * INTO #Backup_AuthorizedAmountAndTerm FROM dbo.AuthorizedAmountAndTerm 
WHERE OfferId = '1C607A40-B6FD-4E45-97A6-EDC8DD6A2CB8';
PRINT '✓ Backup AuthorizedAmountAndTerm: ' + CAST(@@ROWCOUNT AS VARCHAR) + ' registros';
PRINT '';

-- ============================================================================
-- PASO 3: ACTUALIZACIÓN
-- ============================================================================

PRINT '=== PASO 3: ACTUALIZANDO CLIENTE 891736 ===';
PRINT '';

-- Actualizar Offer
PRINT 'Actualizando tabla Offer...';
UPDATE dbo.Offer 
SET BranchId = @Branch_Aguascalientes,
    SalesTypeId = @SaleType_Integral,
    LastUpdate = GETDATE()
WHERE Id = '1C607A40-B6FD-4E45-97A6-EDC8DD6A2CB8';
PRINT '✓ Offer actualizada: Branch=Aguascalientes, SaleType=Integral';

-- Actualizar Customer (mantiene Nuevo)
PRINT 'Actualizando tipo de cliente...';
UPDATE dbo.Customer 
SET CatCustomerTypeId = @CustomerType_Nuevo
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '1C607A40-B6FD-4E45-97A6-EDC8DD6A2CB8');
PRINT '✓ Customer actualizado: TipoCliente=Nuevo';

-- Actualizar oferta de 12 sem a $7,500/32sem con N1
PRINT 'Actualizando oferta de $2,500/12sem a $7,500/32sem con N1...';
UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 7500,
    CatPaymentTermId = @Term_32sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '1C607A40-B6FD-4E45-97A6-EDC8DD6A2CB8'
  AND CatPaymentTermId = @Term_12sem;
PRINT '✓ Oferta actualizada: $7,500/32sem/N1';

-- Insertar segunda oferta de $3,500/32sem con N1
PRINT 'Insertando segunda oferta de $3,500/32sem con N1...';
INSERT INTO dbo.AuthorizedAmountAndTerm (Id, OfferId, Amount, CatPaymentTermId, CatPaymentTermTypeId)
VALUES (NEWID(), '1C607A40-B6FD-4E45-97A6-EDC8DD6A2CB8', 3500, @Term_32sem, @PriceLevel_N1);
PRINT '✓ Segunda oferta insertada: $3,500/32sem/N1';
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
WHERE O.Id = '1C607A40-B6FD-4E45-97A6-EDC8DD6A2CB8'
ORDER BY AAT.Amount DESC;

PRINT '';
PRINT '=== CHECKLIST DE VALIDACIÓN ===';
PRINT '';
PRINT 'Verificar que los valores sean:';
PRINT '✓ CustomerIdCS: 891736';
PRINT '✓ CustomerNameCS: JOSE LUIS MARTINEZ  CONTRERAS';
PRINT '✓ SaleTypeCS: Negocio (Integral)';
PRINT '✓ CustomerTypeCS: Cliente Nuevo';
PRINT '✓ BranchName: AGUASCALIENTES 1';
PRINT '✓ Amount: 7500 y 3500 (2 registros)';
PRINT '✓ Term: 32 sem (ambos)';
PRINT '✓ PaymentTermType: N1 (ambos)';
PRINT '✓ ShouldDisplay: 1 (ambos)';
PRINT '✓ Debe tener 2 registros con el mismo plazo pero diferentes montos';
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
WHERE OfferId = '1C607A40-B6FD-4E45-97A6-EDC8DD6A2CB8';

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
PRINT '✓ Cliente 891736 actualizado a $3,500-$7,500/32sem con Etiqueta N1 Visible';
PRINT '✓ Tipo de seguro cambiado a Integral (Negocio)';
PRINT '✓ Backup disponible en tablas temporales para rollback';
PRINT '';

GO
