USE [AVTs];

/*
================================================================================
PRUEBA FINAL - 9 OFERTAS (UNA POR ESCENARIO) - PARTE 2
================================================================================
Este script actualiza las otras 9 ofertas (la segunda de cada escenario).

OFERTAS INCLUIDAS:
1. Escenario 1: Cliente 3927593 - $5,000/12sem | Tradicional | Nuevo | SLP
2. Escenario 2: Cliente 3924823 - $4,500/12sem + $10,500/32sem | Tradicional | Frecuente | SLP
3. Escenario 3: Cliente 3942020 - $3,500/12sem | Tradicional | Nuevo | SLP
4. Escenario 4: Cliente 3974077 - $10,500/42sem + $5,000/12sem | Integral | Frecuente | Zacatecas
5. Escenario 5: Cliente 3971693 - $7,500/32sem | Integral | Nuevo | Aguascalientes
6. Escenario 6: Cliente 3977635 - $5,500/32sem + $7,500/42sem | Integral | Frecuente | Zacatecas
7. Escenario 7: Cliente 3941669 - $4,000/12sem | Tradicional | Nuevo | Aguascalientes
8. Escenario 8: Cliente 3996996 - $4,000/12sem + $10,500/32sem | Tradicional | Frecuente | Aguascalientes
9. Escenario 9: Cliente 3974085 - $4,000/12sem | Tradicional | Nuevo | Aguascalientes

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
    'FAB7A814-ED3E-4EF4-907E-EDD004ACC6C9', 'B9EADADE-17F0-45D5-A372-5225587117C8',
    'C24D3C96-1CEC-4A4F-94CC-244055C7C066', '7E02D10E-2698-415F-A7A7-B5D07478CB3A',
    '1F6B6374-AFC1-4A92-829A-E5206DB5724A', '6C6BE2C9-0284-4E59-A9F0-B607505D5202',
    '357E0A2A-7EAA-46E6-8B6B-B43533F4E794', '3BFCCE94-9C37-4DB6-8E27-8C904FABC6CF',
    '469655B4-4126-4E4A-A6E4-1E19D3B11A28'
);
PRINT '✓ Backup Offer: ' + CAST(@@ROWCOUNT AS VARCHAR) + ' registros';

IF OBJECT_ID('tempdb..#Backup_Customer') IS NOT NULL DROP TABLE #Backup_Customer;
SELECT C.* INTO #Backup_Customer FROM dbo.Customer C
INNER JOIN dbo.Offer O ON C.Id = O.CustomerId WHERE O.Id IN (
    'FAB7A814-ED3E-4EF4-907E-EDD004ACC6C9', 'B9EADADE-17F0-45D5-A372-5225587117C8',
    'C24D3C96-1CEC-4A4F-94CC-244055C7C066', '7E02D10E-2698-415F-A7A7-B5D07478CB3A',
    '1F6B6374-AFC1-4A92-829A-E5206DB5724A', '6C6BE2C9-0284-4E59-A9F0-B607505D5202',
    '357E0A2A-7EAA-46E6-8B6B-B43533F4E794', '3BFCCE94-9C37-4DB6-8E27-8C904FABC6CF',
    '469655B4-4126-4E4A-A6E4-1E19D3B11A28'
);
PRINT '✓ Backup Customer: ' + CAST(@@ROWCOUNT AS VARCHAR) + ' registros';

IF OBJECT_ID('tempdb..#Backup_AuthorizedAmountAndTerm') IS NOT NULL DROP TABLE #Backup_AuthorizedAmountAndTerm;
SELECT * INTO #Backup_AuthorizedAmountAndTerm FROM dbo.AuthorizedAmountAndTerm WHERE OfferId IN (
    'FAB7A814-ED3E-4EF4-907E-EDD004ACC6C9', 'B9EADADE-17F0-45D5-A372-5225587117C8',
    'C24D3C96-1CEC-4A4F-94CC-244055C7C066', '7E02D10E-2698-415F-A7A7-B5D07478CB3A',
    '1F6B6374-AFC1-4A92-829A-E5206DB5724A', '6C6BE2C9-0284-4E59-A9F0-B607505D5202',
    '357E0A2A-7EAA-46E6-8B6B-B43533F4E794', '3BFCCE94-9C37-4DB6-8E27-8C904FABC6CF',
    '469655B4-4126-4E4A-A6E4-1E19D3B11A28'
);
PRINT '✓ Backup AuthorizedAmountAndTerm: ' + CAST(@@ROWCOUNT AS VARCHAR) + ' registros';
PRINT '';

-- ============================================================================
-- PASO 2: ACTUALIZACIONES
-- ============================================================================

PRINT '=== PASO 2: ACTUALIZANDO 9 OFERTAS ===';
PRINT '';

-- Escenario 1: Cliente 3927593
PRINT 'Escenario 1: Cliente 3927593...';
UPDATE dbo.Offer SET BranchId = @Branch_SLP, SalesTypeId = @SaleType_Tradicional, LastUpdate = GETDATE() WHERE Id = 'FAB7A814-ED3E-4EF4-907E-EDD004ACC6C9';
UPDATE dbo.Customer SET CatCustomerTypeId = @CustomerType_Nuevo WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = 'FAB7A814-ED3E-4EF4-907E-EDD004ACC6C9');
UPDATE dbo.AuthorizedAmountAndTerm SET Amount = 5000, CatPaymentTermId = @Term_12sem, CatPaymentTermTypeId = @PriceLevel_N1 WHERE OfferId = 'FAB7A814-ED3E-4EF4-907E-EDD004ACC6C9' AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '32 sem');
PRINT '✓ Completado';

-- Escenario 2: Cliente 3924823
PRINT 'Escenario 2: Cliente 3924823...';
UPDATE dbo.Offer SET BranchId = @Branch_SLP, SalesTypeId = @SaleType_Tradicional, LastUpdate = GETDATE() WHERE Id = 'B9EADADE-17F0-45D5-A372-5225587117C8';
UPDATE dbo.Customer SET CatCustomerTypeId = @CustomerType_Frecuente WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = 'B9EADADE-17F0-45D5-A372-5225587117C8');
DELETE FROM dbo.AuthorizedAmountAndTerm WHERE OfferId = 'B9EADADE-17F0-45D5-A372-5225587117C8' AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '42 sem');
UPDATE dbo.AuthorizedAmountAndTerm SET Amount = 10500, CatPaymentTermTypeId = @PriceLevel_N1 WHERE OfferId = 'B9EADADE-17F0-45D5-A372-5225587117C8' AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '32 sem');
INSERT INTO dbo.AuthorizedAmountAndTerm (Id, OfferId, Amount, CatPaymentTermId, CatPaymentTermTypeId) VALUES (NEWID(), 'B9EADADE-17F0-45D5-A372-5225587117C8', 4500, @Term_12sem, @PriceLevel_N1);
PRINT '✓ Completado';

-- Escenario 3: Cliente 3942020
PRINT 'Escenario 3: Cliente 3942020...';
UPDATE dbo.Offer SET BranchId = @Branch_SLP, SalesTypeId = @SaleType_Tradicional, LastUpdate = GETDATE() WHERE Id = 'C24D3C96-1CEC-4A4F-94CC-244055C7C066';
UPDATE dbo.Customer SET CatCustomerTypeId = @CustomerType_Nuevo WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = 'C24D3C96-1CEC-4A4F-94CC-244055C7C066');
UPDATE dbo.AuthorizedAmountAndTerm SET Amount = 3500, CatPaymentTermId = @Term_12sem, CatPaymentTermTypeId = @PriceLevel_N1 WHERE OfferId = 'C24D3C96-1CEC-4A4F-94CC-244055C7C066' AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '32 sem');
PRINT '✓ Completado';

-- Escenario 4: Cliente 3974077
PRINT 'Escenario 4: Cliente 3974077...';
UPDATE dbo.Offer SET BranchId = @Branch_Zacatecas, SalesTypeId = @SaleType_Integral, LastUpdate = GETDATE() WHERE Id = '7E02D10E-2698-415F-A7A7-B5D07478CB3A';
UPDATE dbo.Customer SET CatCustomerTypeId = @CustomerType_Frecuente WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '7E02D10E-2698-415F-A7A7-B5D07478CB3A');
UPDATE dbo.AuthorizedAmountAndTerm SET Amount = 10500, CatPaymentTermId = @Term_42sem, CatPaymentTermTypeId = @PriceLevel_N1 WHERE OfferId = '7E02D10E-2698-415F-A7A7-B5D07478CB3A' AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '42 sem');
UPDATE dbo.AuthorizedAmountAndTerm SET Amount = 5000, CatPaymentTermId = @Term_12sem, CatPaymentTermTypeId = @PriceLevel_N1 WHERE OfferId = '7E02D10E-2698-415F-A7A7-B5D07478CB3A' AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '32 sem');
PRINT '✓ Completado';

-- Escenario 5: Cliente 3971693
PRINT 'Escenario 5: Cliente 3971693...';
UPDATE dbo.Offer SET BranchId = @Branch_Aguascalientes, SalesTypeId = @SaleType_Integral, LastUpdate = GETDATE() WHERE Id = '1F6B6374-AFC1-4A92-829A-E5206DB5724A';
UPDATE dbo.Customer SET CatCustomerTypeId = @CustomerType_Nuevo WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '1F6B6374-AFC1-4A92-829A-E5206DB5724A');
UPDATE dbo.AuthorizedAmountAndTerm SET Amount = 7500, CatPaymentTermTypeId = @PriceLevel_N1 WHERE OfferId = '1F6B6374-AFC1-4A92-829A-E5206DB5724A' AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '32 sem');
PRINT '✓ Completado';

-- Escenario 6: Cliente 3977635
PRINT 'Escenario 6: Cliente 3977635...';
UPDATE dbo.Offer SET BranchId = @Branch_Zacatecas, SalesTypeId = @SaleType_Integral, LastUpdate = GETDATE() WHERE Id = '6C6BE2C9-0284-4E59-A9F0-B607505D5202';
UPDATE dbo.Customer SET CatCustomerTypeId = @CustomerType_Frecuente WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '6C6BE2C9-0284-4E59-A9F0-B607505D5202');
UPDATE dbo.AuthorizedAmountAndTerm SET Amount = 5500, CatPaymentTermId = @Term_32sem, CatPaymentTermTypeId = @PriceLevel_N1 WHERE OfferId = '6C6BE2C9-0284-4E59-A9F0-B607505D5202' AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '32 sem');
UPDATE dbo.AuthorizedAmountAndTerm SET Amount = 7500, CatPaymentTermId = @Term_42sem, CatPaymentTermTypeId = @PriceLevel_N1 WHERE OfferId = '6C6BE2C9-0284-4E59-A9F0-B607505D5202' AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '42 sem');
PRINT '✓ Completado';

-- Escenario 7: Cliente 3941669
PRINT 'Escenario 7: Cliente 3941669...';
UPDATE dbo.Offer SET BranchId = @Branch_Aguascalientes, SalesTypeId = @SaleType_Tradicional, LastUpdate = GETDATE() WHERE Id = '357E0A2A-7EAA-46E6-8B6B-B43533F4E794';
UPDATE dbo.Customer SET CatCustomerTypeId = @CustomerType_Nuevo WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '357E0A2A-7EAA-46E6-8B6B-B43533F4E794');
UPDATE dbo.AuthorizedAmountAndTerm SET Amount = 4000, CatPaymentTermId = @Term_12sem, CatPaymentTermTypeId = @PriceLevel_N1 WHERE OfferId = '357E0A2A-7EAA-46E6-8B6B-B43533F4E794' AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '32 sem');
PRINT '✓ Completado';

-- Escenario 8: Cliente 3996996
PRINT 'Escenario 8: Cliente 3996996...';
UPDATE dbo.Offer SET BranchId = @Branch_Aguascalientes, SalesTypeId = @SaleType_Tradicional, LastUpdate = GETDATE() WHERE Id = '3BFCCE94-9C37-4DB6-8E27-8C904FABC6CF';
UPDATE dbo.Customer SET CatCustomerTypeId = @CustomerType_Frecuente WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '3BFCCE94-9C37-4DB6-8E27-8C904FABC6CF');
DELETE FROM dbo.AuthorizedAmountAndTerm WHERE OfferId = '3BFCCE94-9C37-4DB6-8E27-8C904FABC6CF' AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '42 sem');
UPDATE dbo.AuthorizedAmountAndTerm SET Amount = 10500, CatPaymentTermTypeId = @PriceLevel_N1 WHERE OfferId = '3BFCCE94-9C37-4DB6-8E27-8C904FABC6CF' AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '32 sem');
INSERT INTO dbo.AuthorizedAmountAndTerm (Id, OfferId, Amount, CatPaymentTermId, CatPaymentTermTypeId) VALUES (NEWID(), '3BFCCE94-9C37-4DB6-8E27-8C904FABC6CF', 4000, @Term_12sem, @PriceLevel_N1);
PRINT '✓ Completado';

-- Escenario 9: Cliente 3974085
PRINT 'Escenario 9: Cliente 3974085...';
UPDATE dbo.Offer SET BranchId = @Branch_Aguascalientes, SalesTypeId = @SaleType_Tradicional, LastUpdate = GETDATE() WHERE Id = '469655B4-4126-4E4A-A6E4-1E19D3B11A28';
UPDATE dbo.Customer SET CatCustomerTypeId = @CustomerType_Nuevo WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '469655B4-4126-4E4A-A6E4-1E19D3B11A28');
UPDATE dbo.AuthorizedAmountAndTerm SET Amount = 4000, CatPaymentTermId = @Term_12sem, CatPaymentTermTypeId = @PriceLevel_N1 WHERE OfferId = '469655B4-4126-4E4A-A6E4-1E19D3B11A28' AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '32 sem');
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
    'FAB7A814-ED3E-4EF4-907E-EDD004ACC6C9', 'B9EADADE-17F0-45D5-A372-5225587117C8',
    'C24D3C96-1CEC-4A4F-94CC-244055C7C066', '7E02D10E-2698-415F-A7A7-B5D07478CB3A',
    '1F6B6374-AFC1-4A92-829A-E5206DB5724A', '6C6BE2C9-0284-4E59-A9F0-B607505D5202',
    '357E0A2A-7EAA-46E6-8B6B-B43533F4E794', '3BFCCE94-9C37-4DB6-8E27-8C904FABC6CF',
    '469655B4-4126-4E4A-A6E4-1E19D3B11A28'
)
ORDER BY O.DataSourceRecordId;

PRINT '';
PRINT '✓ Validación completada';
PRINT '';
PRINT 'NOTA: Tablas de backup disponibles para rollback: #Backup_Offer, #Backup_Customer, #Backup_AuthorizedAmountAndTerm';
PRINT '';

GO
