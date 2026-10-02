USE [AVTs];

/*
================================================================================
PRUEBA INICIAL - 9 OFERTAS (UNA POR ESCENARIO) - PARTE 1
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

-- Declaración de variables
DECLARE 
    @Branch_SLP UNIQUEIDENTIFIER = '1D0712B3-DBE1-4872-BB82-0879B123E7EC',
    @Branch_Zacatecas UNIQUEIDENTIFIER = '51BCD590-3B05-47D9-8328-93ADE7B47BD1',
    @Branch_Aguascalientes UNIQUEIDENTIFIER = '7AE76DAF-08C3-43FB-B3E4-455E64AED01C',
    @SaleType_Tradicional UNIQUEIDENTIFIER = 'F7049160-F367-438C-A0A8-0B63F6B03EBD',
    @SaleType_Integral UNIQUEIDENTIFIER = '21BE783E-8B08-405D-A449-A21FABC8E113',
    @CustomerType_Nuevo UNIQUEIDENTIFIER = 'D681D8CC-F364-499A-9322-F6AEDBBF24AE',
    @CustomerType_Frecuente UNIQUEIDENTIFIER = '4819CA7D-5A32-4857-A6B2-12C99D5EA295',
    @Term_12sem UNIQUEIDENTIFIER = '81C7FA1C-FFB3-4CF3-AEB7-BDDE1A8A4D6C',
    @Term_32sem UNIQUEIDENTIFIER = '403E89C5-B995-4AA1-8ADA-5B99E0267BB2',
    @Term_42sem UNIQUEIDENTIFIER = 'E2741F66-A665-491E-84AB-EB0DECDA3E8A',
    @PriceLevel_N1 UNIQUEIDENTIFIER = 'B771BFC0-D40A-49A7-8372-72F7776A6338';

-- ============================================================================
-- PASO 1: BACKUP
-- ============================================================================

PRINT '';
PRINT '=== PASO 1: CREANDO BACKUP DE 9 OFERTAS ===';

IF OBJECT_ID('tempdb..#Backup_Offer') IS NOT NULL DROP TABLE #Backup_Offer;
SELECT * INTO #Backup_Offer FROM dbo.Offer WHERE Id IN (
    '2D676E6C-C0A1-4715-99ED-9BBA0EDA816A', '8D619493-D6FA-4383-87A7-A05E6BAEEFD5',
    '1585343D-621F-46D9-A4D9-82A0DD687F45', '0EA85C1D-B199-41AB-82E5-B4EAF8AA5F08',
    '58E7CF45-6A85-4A83-AEF2-2C69E1E79DA2', '751DA029-64F4-409C-AA81-1FA8B8C554AB',
    '858672A0-5530-476F-AB96-D15CE71D68CE', '5ECB173F-71B5-41BE-96DD-0F76EE17A52C',
    '92F25F57-E32B-4AAB-BB8F-DF51C302A01E'
);
PRINT '✓ Backup Offer: ' + CAST(@@ROWCOUNT AS VARCHAR) + ' registros';

IF OBJECT_ID('tempdb..#Backup_Customer') IS NOT NULL DROP TABLE #Backup_Customer;
SELECT C.* INTO #Backup_Customer FROM dbo.Customer C
INNER JOIN dbo.Offer O ON C.Id = O.CustomerId WHERE O.Id IN (
    '2D676E6C-C0A1-4715-99ED-9BBA0EDA816A', '8D619493-D6FA-4383-87A7-A05E6BAEEFD5',
    '1585343D-621F-46D9-A4D9-82A0DD687F45', '0EA85C1D-B199-41AB-82E5-B4EAF8AA5F08',
    '58E7CF45-6A85-4A83-AEF2-2C69E1E79DA2', '751DA029-64F4-409C-AA81-1FA8B8C554AB',
    '858672A0-5530-476F-AB96-D15CE71D68CE', '5ECB173F-71B5-41BE-96DD-0F76EE17A52C',
    '92F25F57-E32B-4AAB-BB8F-DF51C302A01E'
);
PRINT '✓ Backup Customer: ' + CAST(@@ROWCOUNT AS VARCHAR) + ' registros';

IF OBJECT_ID('tempdb..#Backup_AuthorizedAmountAndTerm') IS NOT NULL DROP TABLE #Backup_AuthorizedAmountAndTerm;
SELECT * INTO #Backup_AuthorizedAmountAndTerm FROM dbo.AuthorizedAmountAndTerm WHERE OfferId IN (
    '2D676E6C-C0A1-4715-99ED-9BBA0EDA816A', '8D619493-D6FA-4383-87A7-A05E6BAEEFD5',
    '1585343D-621F-46D9-A4D9-82A0DD687F45', '0EA85C1D-B199-41AB-82E5-B4EAF8AA5F08',
    '58E7CF45-6A85-4A83-AEF2-2C69E1E79DA2', '751DA029-64F4-409C-AA81-1FA8B8C554AB',
    '858672A0-5530-476F-AB96-D15CE71D68CE', '5ECB173F-71B5-41BE-96DD-0F76EE17A52C',
    '92F25F57-E32B-4AAB-BB8F-DF51C302A01E'
);
PRINT '✓ Backup AuthorizedAmountAndTerm: ' + CAST(@@ROWCOUNT AS VARCHAR) + ' registros';
PRINT '';

-- ============================================================================
-- PASO 2: ACTUALIZACIONES
-- ============================================================================

PRINT '=== PASO 2: ACTUALIZANDO 9 OFERTAS ===';
PRINT '';

-- Escenario 1: Cliente 3911780
PRINT 'Escenario 1: Cliente 3911780...';
UPDATE dbo.Offer SET BranchId = @Branch_SLP, SalesTypeId = @SaleType_Tradicional, LastUpdate = GETDATE() WHERE Id = '2D676E6C-C0A1-4715-99ED-9BBA0EDA816A';
UPDATE dbo.Customer SET CatCustomerTypeId = @CustomerType_Nuevo WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '2D676E6C-C0A1-4715-99ED-9BBA0EDA816A');
UPDATE dbo.AuthorizedAmountAndTerm SET Amount = 5000, CatPaymentTermId = @Term_12sem, CatPaymentTermTypeId = @PriceLevel_N1 WHERE OfferId = '2D676E6C-C0A1-4715-99ED-9BBA0EDA816A';
PRINT '✓ Completado';

-- Escenario 2: Cliente 3915271
PRINT 'Escenario 2: Cliente 3915271...';
UPDATE dbo.Offer SET BranchId = @Branch_SLP, SalesTypeId = @SaleType_Tradicional, LastUpdate = GETDATE() WHERE Id = '8D619493-D6FA-4383-87A7-A05E6BAEEFD5';
UPDATE dbo.Customer SET CatCustomerTypeId = @CustomerType_Frecuente WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '8D619493-D6FA-4383-87A7-A05E6BAEEFD5');
DELETE FROM dbo.AuthorizedAmountAndTerm WHERE OfferId = '8D619493-D6FA-4383-87A7-A05E6BAEEFD5' AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '42 sem');
UPDATE dbo.AuthorizedAmountAndTerm SET Amount = 10500, CatPaymentTermTypeId = @PriceLevel_N1 WHERE OfferId = '8D619493-D6FA-4383-87A7-A05E6BAEEFD5' AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '32 sem');
INSERT INTO dbo.AuthorizedAmountAndTerm (Id, OfferId, Amount, CatPaymentTermId, CatPaymentTermTypeId) VALUES (NEWID(), '8D619493-D6FA-4383-87A7-A05E6BAEEFD5', 4500, @Term_12sem, @PriceLevel_N1);
PRINT '✓ Completado';

-- Escenario 3: Cliente 3935222
PRINT 'Escenario 3: Cliente 3935222...';
UPDATE dbo.Offer SET BranchId = @Branch_SLP, SalesTypeId = @SaleType_Tradicional, LastUpdate = GETDATE() WHERE Id = '1585343D-621F-46D9-A4D9-82A0DD687F45';
UPDATE dbo.Customer SET CatCustomerTypeId = @CustomerType_Nuevo WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '1585343D-621F-46D9-A4D9-82A0DD687F45');
UPDATE dbo.AuthorizedAmountAndTerm SET Amount = 3500, CatPaymentTermId = @Term_12sem, CatPaymentTermTypeId = @PriceLevel_N1 WHERE OfferId = '1585343D-621F-46D9-A4D9-82A0DD687F45' AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '32 sem');
PRINT '✓ Completado';

-- Escenario 4: Cliente 3930704
PRINT 'Escenario 4: Cliente 3930704...';
UPDATE dbo.Offer SET BranchId = @Branch_Zacatecas, SalesTypeId = @SaleType_Integral, LastUpdate = GETDATE() WHERE Id = '0EA85C1D-B199-41AB-82E5-B4EAF8AA5F08';
UPDATE dbo.Customer SET CatCustomerTypeId = @CustomerType_Frecuente WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '0EA85C1D-B199-41AB-82E5-B4EAF8AA5F08');
UPDATE dbo.AuthorizedAmountAndTerm SET Amount = 10500, CatPaymentTermId = @Term_42sem, CatPaymentTermTypeId = @PriceLevel_N1 WHERE OfferId = '0EA85C1D-B199-41AB-82E5-B4EAF8AA5F08' AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '42 sem');
UPDATE dbo.AuthorizedAmountAndTerm SET Amount = 5000, CatPaymentTermId = @Term_12sem, CatPaymentTermTypeId = @PriceLevel_N1 WHERE OfferId = '0EA85C1D-B199-41AB-82E5-B4EAF8AA5F08' AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '32 sem');
PRINT '✓ Completado';

-- Escenario 5: Cliente 533178
PRINT 'Escenario 5: Cliente 533178...';
UPDATE dbo.Offer SET BranchId = @Branch_Aguascalientes, SalesTypeId = @SaleType_Integral, LastUpdate = GETDATE() WHERE Id = '58E7CF45-6A85-4A83-AEF2-2C69E1E79DA2';
UPDATE dbo.Customer SET CatCustomerTypeId = @CustomerType_Nuevo WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '58E7CF45-6A85-4A83-AEF2-2C69E1E79DA2');
UPDATE dbo.AuthorizedAmountAndTerm SET Amount = 7500, CatPaymentTermTypeId = @PriceLevel_N1 WHERE OfferId = '58E7CF45-6A85-4A83-AEF2-2C69E1E79DA2' AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '32 sem');
PRINT '✓ Completado';

-- Escenario 6: Cliente 3911266
PRINT 'Escenario 6: Cliente 3911266...';
UPDATE dbo.Offer SET BranchId = @Branch_Zacatecas, SalesTypeId = @SaleType_Integral, LastUpdate = GETDATE() WHERE Id = '751DA029-64F4-409C-AA81-1FA8B8C554AB';
UPDATE dbo.Customer SET CatCustomerTypeId = @CustomerType_Frecuente WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '751DA029-64F4-409C-AA81-1FA8B8C554AB');
UPDATE dbo.AuthorizedAmountAndTerm SET Amount = 5500, CatPaymentTermId = @Term_32sem, CatPaymentTermTypeId = @PriceLevel_N1 WHERE OfferId = '751DA029-64F4-409C-AA81-1FA8B8C554AB' AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '32 sem');
UPDATE dbo.AuthorizedAmountAndTerm SET Amount = 7500, CatPaymentTermId = @Term_42sem, CatPaymentTermTypeId = @PriceLevel_N1 WHERE OfferId = '751DA029-64F4-409C-AA81-1FA8B8C554AB' AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '42 sem');
PRINT '✓ Completado';

-- Escenario 7: Cliente 3854562
PRINT 'Escenario 7: Cliente 3854562...';
UPDATE dbo.Offer SET BranchId = @Branch_Aguascalientes, SalesTypeId = @SaleType_Tradicional, LastUpdate = GETDATE() WHERE Id = '858672A0-5530-476F-AB96-D15CE71D68CE';
UPDATE dbo.Customer SET CatCustomerTypeId = @CustomerType_Nuevo WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '858672A0-5530-476F-AB96-D15CE71D68CE');
UPDATE dbo.AuthorizedAmountAndTerm SET Amount = 4000, CatPaymentTermId = @Term_12sem, CatPaymentTermTypeId = @PriceLevel_N1 WHERE OfferId = '858672A0-5530-476F-AB96-D15CE71D68CE' AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '32 sem');
PRINT '✓ Completado';

-- Escenario 8: Cliente 3966802
PRINT 'Escenario 8: Cliente 3966802...';
UPDATE dbo.Offer SET BranchId = @Branch_Aguascalientes, SalesTypeId = @SaleType_Tradicional, LastUpdate = GETDATE() WHERE Id = '5ECB173F-71B5-41BE-96DD-0F76EE17A52C';
UPDATE dbo.Customer SET CatCustomerTypeId = @CustomerType_Frecuente WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '5ECB173F-71B5-41BE-96DD-0F76EE17A52C');
DELETE FROM dbo.AuthorizedAmountAndTerm WHERE OfferId = '5ECB173F-71B5-41BE-96DD-0F76EE17A52C' AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '42 sem');
UPDATE dbo.AuthorizedAmountAndTerm SET Amount = 10500, CatPaymentTermTypeId = @PriceLevel_N1 WHERE OfferId = '5ECB173F-71B5-41BE-96DD-0F76EE17A52C' AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '32 sem');
INSERT INTO dbo.AuthorizedAmountAndTerm (Id, OfferId, Amount, CatPaymentTermId, CatPaymentTermTypeId) VALUES (NEWID(), '5ECB173F-71B5-41BE-96DD-0F76EE17A52C', 4000, @Term_12sem, @PriceLevel_N1);
PRINT '✓ Completado';

-- Escenario 9: Cliente 3954461
PRINT 'Escenario 9: Cliente 3954461...';
UPDATE dbo.Offer SET BranchId = @Branch_Aguascalientes, SalesTypeId = @SaleType_Tradicional, LastUpdate = GETDATE() WHERE Id = '92F25F57-E32B-4AAB-BB8F-DF51C302A01E';
UPDATE dbo.Customer SET CatCustomerTypeId = @CustomerType_Nuevo WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '92F25F57-E32B-4AAB-BB8F-DF51C302A01E');
UPDATE dbo.AuthorizedAmountAndTerm SET Amount = 4000, CatPaymentTermTypeId = @PriceLevel_N1 WHERE OfferId = '92F25F57-E32B-4AAB-BB8F-DF51C302A01E' AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '12 sem');
PRINT '✓ Completado';

PRINT '';

-- ============================================================================
-- PASO 3: VALIDACIÓN
-- ============================================================================

PRINT '=== PASO 3: VALIDACIÓN DE 9 OFERTAS ===';
PRINT '';

SELECT 
    O.Id AS OfferId,
    CONVERT(NVARCHAR(20), O.DataSourceRecordId) AS CustomerIdCS,
    C.FullName AS CustomerNameCS,
    ST.Name AS SaleTypeCS,
    CT.Name AS CustomerTypeCS,
    B.Name AS BranchName,
    AAT1.Amount AS Amount1,
    PT1.Name AS Term1,
    AAT2.Amount AS Amount2,
    PT2.Name AS Term2,
    CPTP.Name AS PaymentTermType,
    CPTP.ShouldDisplay AS ShouldDisplay
FROM dbo.Offer O
INNER JOIN dbo.Customer C ON O.CustomerId = C.Id
INNER JOIN dbo.CatSaleType ST ON O.SalesTypeId = ST.Id
INNER JOIN dbo.CatCustomerType CT ON C.CatCustomerTypeId = CT.Id
INNER JOIN dbo.Branch B ON O.BranchId = B.Id
LEFT JOIN (
    SELECT OfferId, Amount, CatPaymentTermId, CatPaymentTermTypeId,
           ROW_NUMBER() OVER (PARTITION BY OfferId ORDER BY CatPaymentTermId DESC) AS rn
    FROM dbo.AuthorizedAmountAndTerm
) AAT1 ON O.Id = AAT1.OfferId AND AAT1.rn = 1
LEFT JOIN dbo.CatPaymentTerm PT1 ON AAT1.CatPaymentTermId = PT1.Id
LEFT JOIN (
    SELECT OfferId, Amount, CatPaymentTermId,
           ROW_NUMBER() OVER (PARTITION BY OfferId ORDER BY CatPaymentTermId ASC) AS rn
    FROM dbo.AuthorizedAmountAndTerm
) AAT2 ON O.Id = AAT2.OfferId AND AAT2.rn = 1 AND AAT2.CatPaymentTermId <> AAT1.CatPaymentTermId
LEFT JOIN dbo.CatPaymentTerm PT2 ON AAT2.CatPaymentTermId = PT2.Id
LEFT JOIN dbo.CatPaymentTermType CPTP ON AAT1.CatPaymentTermTypeId = CPTP.Id
WHERE O.Id IN (
    '2D676E6C-C0A1-4715-99ED-9BBA0EDA816A', '8D619493-D6FA-4383-87A7-A05E6BAEEFD5',
    '1585343D-621F-46D9-A4D9-82A0DD687F45', '0EA85C1D-B199-41AB-82E5-B4EAF8AA5F08',
    '58E7CF45-6A85-4A83-AEF2-2C69E1E79DA2', '751DA029-64F4-409C-AA81-1FA8B8C554AB',
    '858672A0-5530-476F-AB96-D15CE71D68CE', '5ECB173F-71B5-41BE-96DD-0F76EE17A52C',
    '92F25F57-E32B-4AAB-BB8F-DF51C302A01E'
)
ORDER BY O.DataSourceRecordId;

PRINT '';
PRINT '✓ Validación completada';
PRINT '';
PRINT 'NOTA: Tablas de backup disponibles para rollback: #Backup_Offer, #Backup_Customer, #Backup_AuthorizedAmountAndTerm';
PRINT '';

GO
