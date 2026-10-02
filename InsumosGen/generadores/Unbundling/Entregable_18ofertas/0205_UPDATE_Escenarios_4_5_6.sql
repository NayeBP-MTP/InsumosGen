USE [AVTs];

/*
================================================================================
ACTUALIZACIÓN DE ESCENARIOS 4, 5 Y 6 - CLIENTES VÍRGENES
================================================================================
Este script actualiza 6 ofertas (2 por escenario) con clientes completamente nuevos
que NO han sido usados en ninguno de los 18 escenarios anteriores.

ESCENARIO 4: $10,500/42sem + $5,000/12sem | Integral | N1 | Frecuente | Zacatecas
- Cliente 4042947 (MARIANA VALENZUELA VALERIO) - OfferId: C627F2BD-C0A0-46AE-918C-03AFA8C8CBA4
- Cliente 4057044 (RUTH LILIANA DELGADO RODRIGUEZ) - OfferId: BA298162-FDE6-4F46-AEF2-0521309810F6

ESCENARIO 5: $7,500/32sem | Integral | N1 | Nuevo | Aguascalientes
- Cliente 329738 (NADIA MIREYA PALENCIA GARCIA) - OfferId: FC52C50C-A522-4051-9F5B-C77FFBFF5C66
- Cliente 3989204 (MA GUADALUPE CASTRO GUTIERREZ) - OfferId: 0DE49E04-1118-40B8-8715-DF9ED566208F

ESCENARIO 6: $5,500/32sem + $7,500/42sem | Integral | N1 | Frecuente | Zacatecas
- Cliente 4066719 (ARIZDEY ALEJANDRA DE AVILA MORENO) - OfferId: 0BA33CF7-78EA-472D-9AC1-7A87EEF10283
- Cliente 4066750 (ARACELI CERVANTES SALAZAR) - OfferId: 3C3200D7-EBCD-4563-9CDF-93892F943985

Fecha: 2026-02-17
================================================================================
*/

-- Declaración de variables
DECLARE 
    @Branch_Aguascalientes UNIQUEIDENTIFIER = '7AE76DAF-08C3-43FB-B3E4-455E64AED01C',
    @Branch_Zacatecas UNIQUEIDENTIFIER = '51BCD590-3B05-47D9-8328-93ADE7B47BD1',
    @Branch_SLP UNIQUEIDENTIFIER = '1D0712B3-DBE1-4872-BB82-0879B123E7EC',
    @SaleType_Integral UNIQUEIDENTIFIER = '21BE783E-8B08-405D-A449-A21FABC8E113',
    @CustomerType_Nuevo UNIQUEIDENTIFIER = 'D681D8CC-F364-499A-9322-F6AEDBBF24AE',
    @CustomerType_Frecuente UNIQUEIDENTIFIER = '4819CA7D-5A32-4857-A6B2-12C99D5EA295',
    @Term_12sem UNIQUEIDENTIFIER = '81C7FA1C-FFB3-4CF3-AEB7-BDDE1A8A4D6C',
    @Term_32sem UNIQUEIDENTIFIER = '403E89C5-B995-4AA1-8ADA-5B99E0267BB2',
    @Term_42sem UNIQUEIDENTIFIER = 'E2741F66-A665-491E-84AB-EB0DECDA3E8A',
    @PriceLevel_N1 UNIQUEIDENTIFIER = 'B771BFC0-D40A-49A7-8372-72F7776A6338';

-- ============================================================================
-- PASO 1: BACKUP DE DATOS ORIGINALES
-- ============================================================================

PRINT '';
PRINT '=== PASO 1: CREANDO BACKUP DE DATOS ORIGINALES ===';

IF OBJECT_ID('tempdb..#Backup_Offer') IS NOT NULL DROP TABLE #Backup_Offer;
SELECT * INTO #Backup_Offer FROM dbo.Offer WHERE Id IN (
    'C627F2BD-C0A0-46AE-918C-03AFA8C8CBA4', 'BA298162-FDE6-4F46-AEF2-0521309810F6',
    'FC52C50C-A522-4051-9F5B-C77FFBFF5C66', '0DE49E04-1118-40B8-8715-DF9ED566208F',
    '0BA33CF7-78EA-472D-9AC1-7A87EEF10283', '3C3200D7-EBCD-4563-9CDF-93892F943985'
);
PRINT '✓ Backup de Offer: ' + CAST(@@ROWCOUNT AS VARCHAR) + ' registros';

IF OBJECT_ID('tempdb..#Backup_Customer') IS NOT NULL DROP TABLE #Backup_Customer;
SELECT C.* INTO #Backup_Customer FROM dbo.Customer C
INNER JOIN dbo.Offer O ON C.Id = O.CustomerId 
WHERE O.Id IN (
    'C627F2BD-C0A0-46AE-918C-03AFA8C8CBA4', 'BA298162-FDE6-4F46-AEF2-0521309810F6',
    'FC52C50C-A522-4051-9F5B-C77FFBFF5C66', '0DE49E04-1118-40B8-8715-DF9ED566208F',
    '0BA33CF7-78EA-472D-9AC1-7A87EEF10283', '3C3200D7-EBCD-4563-9CDF-93892F943985'
);
PRINT '✓ Backup de Customer: ' + CAST(@@ROWCOUNT AS VARCHAR) + ' registros';

IF OBJECT_ID('tempdb..#Backup_AuthorizedAmountAndTerm') IS NOT NULL DROP TABLE #Backup_AuthorizedAmountAndTerm;
SELECT * INTO #Backup_AuthorizedAmountAndTerm FROM dbo.AuthorizedAmountAndTerm 
WHERE OfferId IN (
    'C627F2BD-C0A0-46AE-918C-03AFA8C8CBA4', 'BA298162-FDE6-4F46-AEF2-0521309810F6',
    'FC52C50C-A522-4051-9F5B-C77FFBFF5C66', '0DE49E04-1118-40B8-8715-DF9ED566208F',
    '0BA33CF7-78EA-472D-9AC1-7A87EEF10283', '3C3200D7-EBCD-4563-9CDF-93892F943985'
);
PRINT '✓ Backup de AuthorizedAmountAndTerm: ' + CAST(@@ROWCOUNT AS VARCHAR) + ' registros';
PRINT '';

-- ============================================================================
-- PASO 2: ACTUALIZACIÓN DE OFERTAS
-- ============================================================================

PRINT '=== PASO 2: ACTUALIZANDO OFERTAS ===';
PRINT '';

-- ============================================================================
-- ESCENARIO 4: Ofertas 1-2
-- Excel: $10,500/42sem + $5,000/12sem | Integral | N1 | Frecuente | Zacatecas
-- ============================================================================

PRINT 'Actualizando Escenario 4 (Ofertas 1-2)...';

-- Oferta 1: C627F2BD-C0A0-46AE-918C-03AFA8C8CBA4 (Cliente 4042947)
PRINT '  Cliente 4042947 (MARIANA VALENZUELA VALERIO)...';
UPDATE dbo.Offer
SET BranchId = @Branch_Zacatecas,
    SalesTypeId = @SaleType_Integral,
    LastUpdate = GETDATE()
WHERE Id = 'C627F2BD-C0A0-46AE-918C-03AFA8C8CBA4';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Frecuente
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = 'C627F2BD-C0A0-46AE-918C-03AFA8C8CBA4');

-- Actualizar oferta de 42 sem a $10,500
UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 10500,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = 'C627F2BD-C0A0-46AE-918C-03AFA8C8CBA4'
  AND CatPaymentTermId = @Term_42sem;

-- Actualizar oferta de 32 sem a $5,000/12sem
UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 5000,
    CatPaymentTermId = @Term_12sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = 'C627F2BD-C0A0-46AE-918C-03AFA8C8CBA4'
  AND CatPaymentTermId = @Term_32sem;

PRINT '  ✓ Cliente 4042947 actualizado';

-- Oferta 2: BA298162-FDE6-4F46-AEF2-0521309810F6 (Cliente 4057044)
PRINT '  Cliente 4057044 (RUTH LILIANA DELGADO RODRIGUEZ)...';
UPDATE dbo.Offer
SET BranchId = @Branch_Zacatecas,
    SalesTypeId = @SaleType_Integral,
    LastUpdate = GETDATE()
WHERE Id = 'BA298162-FDE6-4F46-AEF2-0521309810F6';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Frecuente
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = 'BA298162-FDE6-4F46-AEF2-0521309810F6');

-- Actualizar oferta de 42 sem a $10,500
UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 10500,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = 'BA298162-FDE6-4F46-AEF2-0521309810F6'
  AND CatPaymentTermId = @Term_42sem;

-- Actualizar oferta de 32 sem a $5,000/12sem
UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 5000,
    CatPaymentTermId = @Term_12sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = 'BA298162-FDE6-4F46-AEF2-0521309810F6'
  AND CatPaymentTermId = @Term_32sem;

PRINT '  ✓ Cliente 4057044 actualizado';
PRINT '✓ Escenario 4 completado';
PRINT '';

-- ============================================================================
-- ESCENARIO 5: Ofertas 3-4
-- Excel: $7,500/32sem | Integral | N1 | Nuevo | Aguascalientes
-- ============================================================================

PRINT 'Actualizando Escenario 5 (Ofertas 3-4)...';

-- Oferta 3: FC52C50C-A522-4051-9F5B-C77FFBFF5C66 (Cliente 329738)
PRINT '  Cliente 329738 (NADIA MIREYA PALENCIA GARCIA)...';
UPDATE dbo.Offer
SET BranchId = @Branch_Aguascalientes,
    SalesTypeId = @SaleType_Integral,
    LastUpdate = GETDATE()
WHERE Id = 'FC52C50C-A522-4051-9F5B-C77FFBFF5C66';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Nuevo
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = 'FC52C50C-A522-4051-9F5B-C77FFBFF5C66');

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 7500,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = 'FC52C50C-A522-4051-9F5B-C77FFBFF5C66'
  AND CatPaymentTermId = @Term_32sem;

PRINT '  ✓ Cliente 329738 actualizado';

-- Oferta 4: 0DE49E04-1118-40B8-8715-DF9ED566208F (Cliente 3989204)
PRINT '  Cliente 3989204 (MA GUADALUPE CASTRO GUTIERREZ)...';
UPDATE dbo.Offer
SET BranchId = @Branch_Aguascalientes,
    SalesTypeId = @SaleType_Integral,
    LastUpdate = GETDATE()
WHERE Id = '0DE49E04-1118-40B8-8715-DF9ED566208F';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Nuevo
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '0DE49E04-1118-40B8-8715-DF9ED566208F');

-- Esta oferta ya tiene 32 sem, solo actualizar monto
UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 7500,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '0DE49E04-1118-40B8-8715-DF9ED566208F'
  AND CatPaymentTermId = @Term_32sem;

PRINT '  ✓ Cliente 3989204 actualizado';
PRINT '✓ Escenario 5 completado';
PRINT '';

-- ============================================================================
-- ESCENARIO 6: Ofertas 5-6
-- Excel: $5,500/32sem + $7,500/42sem | Integral | N1 | Frecuente | Zacatecas
-- ============================================================================

PRINT 'Actualizando Escenario 6 (Ofertas 5-6)...';

-- Oferta 5: 0BA33CF7-78EA-472D-9AC1-7A87EEF10283 (Cliente 4066719)
PRINT '  Cliente 4066719 (ARIZDEY ALEJANDRA DE AVILA MORENO)...';
UPDATE dbo.Offer
SET BranchId = @Branch_Zacatecas,
    SalesTypeId = @SaleType_Integral,
    LastUpdate = GETDATE()
WHERE Id = '0BA33CF7-78EA-472D-9AC1-7A87EEF10283';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Frecuente
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '0BA33CF7-78EA-472D-9AC1-7A87EEF10283');

-- Actualizar oferta de 42 sem a $7,500
UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 7500,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '0BA33CF7-78EA-472D-9AC1-7A87EEF10283'
  AND CatPaymentTermId = @Term_42sem;

-- Actualizar oferta de 32 sem a $5,500
UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 5500,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '0BA33CF7-78EA-472D-9AC1-7A87EEF10283'
  AND CatPaymentTermId = @Term_32sem;

PRINT '  ✓ Cliente 4066719 actualizado';

-- Oferta 6: 3C3200D7-EBCD-4563-9CDF-93892F943985 (Cliente 4066750)
PRINT '  Cliente 4066750 (ARACELI CERVANTES SALAZAR)...';
UPDATE dbo.Offer
SET BranchId = @Branch_Zacatecas,
    SalesTypeId = @SaleType_Integral,
    LastUpdate = GETDATE()
WHERE Id = '3C3200D7-EBCD-4563-9CDF-93892F943985';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Frecuente
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '3C3200D7-EBCD-4563-9CDF-93892F943985');

-- Actualizar oferta de 42 sem a $7,500
UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 7500,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '3C3200D7-EBCD-4563-9CDF-93892F943985'
  AND CatPaymentTermId = @Term_42sem;

-- Actualizar oferta de 32 sem a $5,500
UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 5500,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '3C3200D7-EBCD-4563-9CDF-93892F943985'
  AND CatPaymentTermId = @Term_32sem;

PRINT '  ✓ Cliente 4066750 actualizado';
PRINT '✓ Escenario 6 completado';
PRINT '';

-- ============================================================================
-- PASO 3: VALIDACIÓN DE CAMBIOS
-- ============================================================================

PRINT '=== PASO 3: VALIDACIÓN DE CAMBIOS ===';
PRINT '';

SELECT
    O.Id AS OfferId,
    CONVERT(NVARCHAR(20), O.DataSourceRecordId) AS CustomerIdCS,
    C.FullName AS CustomerNameCS,
    ST.Name AS SaleTypeCS,
    CT.Name AS CustomerTypeCS,
    B.Name AS BranchName,
    AAT.Amount AS AuthorizedAmount,
    PT.Name AS AuthorizedTerm,
    CPTP.Name AS CatPaymentTermTypeName,
    CPTP.ShouldDisplay AS CatPaymentTermTypeShouldDisplay,
    O.LastUpdate
FROM dbo.Offer O
INNER JOIN dbo.Customer C ON O.CustomerId = C.Id
INNER JOIN dbo.CatSaleType ST ON O.SalesTypeId = ST.Id
INNER JOIN dbo.CatCustomerType CT ON C.CatCustomerTypeId = CT.Id
INNER JOIN dbo.Branch B ON O.BranchId = B.Id
LEFT JOIN dbo.AuthorizedAmountAndTerm AAT ON O.Id = AAT.OfferId
LEFT JOIN dbo.CatPaymentTerm PT ON AAT.CatPaymentTermId = PT.Id
LEFT JOIN dbo.CatPaymentTermType CPTP ON AAT.CatPaymentTermTypeId = CPTP.Id
WHERE O.Id IN (
    'C627F2BD-C0A0-46AE-918C-03AFA8C8CBA4', 'BA298162-FDE6-4F46-AEF2-0521309810F6',
    'FC52C50C-A522-4051-9F5B-C77FFBFF5C66', '0DE49E04-1118-40B8-8715-DF9ED566208F',
    '0BA33CF7-78EA-472D-9AC1-7A87EEF10283', '3C3200D7-EBCD-4563-9CDF-93892F943985'
)
ORDER BY O.DataSourceRecordId, PT.Name DESC;

PRINT '';
PRINT '=== VERIFICACIÓN DE VALORES ESPERADOS ===';
PRINT '';
PRINT 'ESCENARIO 4 (Integral | Frecuente | Zacatecas):';
PRINT '  Cliente 4042947: $10,500/42sem + $5,000/12sem | N1';
PRINT '  Cliente 4057044: $10,500/42sem + $5,000/12sem | N1';
PRINT '';
PRINT 'ESCENARIO 5 (Integral | Nuevo | Aguascalientes):';
PRINT '  Cliente 329738: $7,500/32sem | N1';
PRINT '  Cliente 3989204: $7,500/32sem | N1';
PRINT '';
PRINT 'ESCENARIO 6 (Integral | Frecuente | Zacatecas):';
PRINT '  Cliente 4066719: $7,500/42sem + $5,500/32sem | N1';
PRINT '  Cliente 4066750: $7,500/42sem + $5,500/32sem | N1';
PRINT '';

-- ============================================================================
-- PASO 4 (OPCIONAL): ROLLBACK
-- ============================================================================

PRINT '=== ROLLBACK (EJECUTAR SOLO SI HAY PROBLEMAS) ===';
PRINT '';
PRINT 'Para revertir los cambios, ejecuta:';
PRINT '';

/*
-- Restaurar AuthorizedAmountAndTerm
DELETE FROM dbo.AuthorizedAmountAndTerm 
WHERE OfferId IN (
    'C627F2BD-C0A0-46AE-918C-03AFA8C8CBA4', 'BA298162-FDE6-4F46-AEF2-0521309810F6',
    'FC52C50C-A522-4051-9F5B-C77FFBFF5C66', '0DE49E04-1118-40B8-8715-DF9ED566208F',
    '0BA33CF7-78EA-472D-9AC1-7A87EEF10283', '3C3200D7-EBCD-4563-9CDF-93892F943985'
);

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
PRINT '✓ 6 ofertas actualizadas con clientes VÍRGENES (no usados previamente)';
PRINT '✓ Escenarios 4, 5 y 6 regenerados completamente';
PRINT '✓ Backup disponible en tablas temporales para rollback';
PRINT '';

GO
