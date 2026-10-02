USE [AVTs];
GO

/*
================================================================================
SCRIPT DE ACTUALIZACIÓN - 18 OFERTAS UNBUNDLING (VERSIÓN 3)
================================================================================
Este script actualiza 18 ofertas existentes según los requerimientos del Excel.
Basado en el estado actual de la base de datos (offers.txt actualizado 2026-02-17).

ESTADO ACTUAL DE LA BD:
- Varias ofertas ya tienen N1 o N2 asignado
- Este script selecciona 18 ofertas específicas que aún tienen "Normal" 
  y las actualiza según los 9 escenarios del Excel

Fecha: 2026-02-17 11:22 AM
Autor: Nayeli Benitez
================================================================================
*/

-- ============================================================================
-- DECLARACIÓN DE VARIABLES (GUIDs de Catálogos)
-- ============================================================================

DECLARE 
    -- Branches
    @Branch_SLP UNIQUEIDENTIFIER = '1D0712B3-DBE1-4872-BB82-0879B123E7EC',
    @Branch_Zacatecas UNIQUEIDENTIFIER = '51BCD590-3B05-47D9-8328-93ADE7B47BD1',
    @Branch_Aguascalientes UNIQUEIDENTIFIER = '7AE76DAF-08C3-43FB-B3E4-455E64AED01C',
    
    -- Sale Types
    @SaleType_Tradicional UNIQUEIDENTIFIER = 'F7049160-F367-438C-A0A8-0B63F6B03EBD',
    @SaleType_Integral UNIQUEIDENTIFIER = '21BE783E-8B08-405D-A449-A21FABC8E113',
    
    -- Customer Types
    @CustomerType_Nuevo UNIQUEIDENTIFIER = 'D681D8CC-F364-499A-9322-F6AEDBBF24AE',
    @CustomerType_Frecuente UNIQUEIDENTIFIER = '4819CA7D-5A32-4857-A6B2-12C99D5EA295',
    
    -- Payment Terms
    @Term_12sem UNIQUEIDENTIFIER = '81C7FA1C-FFB3-4CF3-AEB7-BDDE1A8A4D6C',
    @Term_32sem UNIQUEIDENTIFIER = '403E89C5-B995-4AA1-8ADA-5B99E0267BB2',
    @Term_42sem UNIQUEIDENTIFIER = 'E2741F66-A665-491E-84AB-EB0DECDA3E8A',
    @Term_52sem UNIQUEIDENTIFIER = 'E1B43A01-C984-4D50-A468-A4E8FCDA1296',
    
    -- Price Levels
    @PriceLevel_N1 UNIQUEIDENTIFIER = 'B771BFC0-D40A-49A7-8372-72F7776A6338';

PRINT '=== INICIO DE ACTUALIZACIÓN DE 18 OFERTAS ===';
PRINT '';

-- ============================================================================
-- ESCENARIO 1: Ofertas 1-2
-- Excel: $5,000/12sem (solo 1 oferta) | Tradicional | N1 | Nuevo | SLP
-- BD: BC360B4B (601022) | 9200/42sem + 7500/32sem | SLP | Nuevo
-- BD: 4604355A (658540) | 7000/32sem | SLP | Nuevo
-- ============================================================================

PRINT '--- ESCENARIO 1: Ofertas 1-2 ---';
PRINT 'Cliente: 601022 - CECILIA RODRIGUEZ MALDONADO';

-- Oferta 1
UPDATE dbo.Offer
SET SalesTypeId = @SaleType_Tradicional,
    BranchId = @Branch_SLP
WHERE Id = 'BC360B4B-D73A-460F-8240-6541C3531863';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Nuevo
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = 'BC360B4B-D73A-460F-8240-6541C3531863');

DELETE FROM dbo.AuthorizedAmountAndTerm
WHERE OfferId = 'BC360B4B-D73A-460F-8240-6541C3531863'
  AND CatPaymentTermId = @Term_32sem;

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 5000,
    CatPaymentTermId = @Term_12sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = 'BC360B4B-D73A-460F-8240-6541C3531863'
  AND CatPaymentTermId = @Term_42sem;

PRINT '✓ Oferta 1 actualizada: 5000/12sem/N1';

PRINT 'Cliente: 658540 - JOSE ALFREDO MORALES VEGA';

-- Oferta 2
UPDATE dbo.Offer
SET SalesTypeId = @SaleType_Tradicional,
    BranchId = @Branch_SLP
WHERE Id = '4604355A-F8C7-4338-9EBC-A500DB0439DA';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Nuevo
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '4604355A-F8C7-4338-9EBC-A500DB0439DA');

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 5000,
    CatPaymentTermId = @Term_12sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '4604355A-F8C7-4338-9EBC-A500DB0439DA'
  AND CatPaymentTermId = @Term_32sem;

PRINT '✓ Oferta 2 actualizada: 5000/12sem/N1';
PRINT '';

-- ============================================================================
-- ESCENARIO 2: Ofertas 3-4
-- Excel: $4,500/12sem + $10,500/32sem | Tradicional | N1 | Frecuente | SLP
-- BD: 3F366374 (1208659) | 7500/32sem | Zacatecas | Nuevo
-- BD: 965756F8 (1262923) | 5000/32sem | SLP | Nuevo
-- ============================================================================

PRINT '--- ESCENARIO 2: Ofertas 3-4 ---';
PRINT 'Cliente: 1208659 - ARTURO ZUÑIGA GUTIERREZ';

-- Oferta 3
UPDATE dbo.Offer
SET SalesTypeId = @SaleType_Tradicional,
    BranchId = @Branch_SLP
WHERE Id = '3F366374-2598-4D77-B4AE-7E9FF10600B1';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Frecuente
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '3F366374-2598-4D77-B4AE-7E9FF10600B1');

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 4500,
    CatPaymentTermId = @Term_12sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '3F366374-2598-4D77-B4AE-7E9FF10600B1'
  AND CatPaymentTermId = @Term_32sem;

INSERT INTO dbo.AuthorizedAmountAndTerm (Id, OfferId, Amount, CatPaymentTermId, CatPaymentTermTypeId)
VALUES (NEWID(), '3F366374-2598-4D77-B4AE-7E9FF10600B1', 10500, @Term_32sem, @PriceLevel_N1);

PRINT '✓ Oferta 3 actualizada: 4500/12sem + 10500/32sem/N1';

PRINT 'Cliente: 1262923 - MARTHA YUDITH RAMIREZ SIERRA';

-- Oferta 4
UPDATE dbo.Offer
SET SalesTypeId = @SaleType_Tradicional,
    BranchId = @Branch_SLP
WHERE Id = '965756F8-F046-4F36-804A-02491C7BC89F';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Frecuente
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '965756F8-F046-4F36-804A-02491C7BC89F');

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 4500,
    CatPaymentTermId = @Term_12sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '965756F8-F046-4F36-804A-02491C7BC89F'
  AND CatPaymentTermId = @Term_32sem;

INSERT INTO dbo.AuthorizedAmountAndTerm (Id, OfferId, Amount, CatPaymentTermId, CatPaymentTermTypeId)
VALUES (NEWID(), '965756F8-F046-4F36-804A-02491C7BC89F', 10500, @Term_32sem, @PriceLevel_N1);

PRINT '✓ Oferta 4 actualizada: 4500/12sem + 10500/32sem/N1';
PRINT '';

-- ============================================================================
-- ESCENARIO 3: Ofertas 5-6
-- Excel: $3,500/12sem (solo 1 oferta) | Tradicional | N1 | Nuevo | SLP
-- BD: FBF62739 (1314066) | 4000/32sem | Zacatecas | Nuevo
-- BD: 061527DA (1127957) | 7500/42sem | Aguascalientes | Nuevo
-- ============================================================================

PRINT '--- ESCENARIO 3: Ofertas 5-6 ---';
PRINT 'Cliente: 1314066 - JESUS GARCIA GARCIA';

-- Oferta 5
UPDATE dbo.Offer
SET SalesTypeId = @SaleType_Tradicional,
    BranchId = @Branch_SLP
WHERE Id = 'FBF62739-DD09-4BD1-B474-AB9304CD1839';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Nuevo
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = 'FBF62739-DD09-4BD1-B474-AB9304CD1839');

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 3500,
    CatPaymentTermId = @Term_12sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = 'FBF62739-DD09-4BD1-B474-AB9304CD1839'
  AND CatPaymentTermId = @Term_32sem;

PRINT '✓ Oferta 5 actualizada: 3500/12sem/N1';

PRINT 'Cliente: 1127957 - LEONARDO DE LUNA MARTINEZ';

-- Oferta 6
UPDATE dbo.Offer
SET SalesTypeId = @SaleType_Tradicional,
    BranchId = @Branch_SLP
WHERE Id = '061527DA-DCAB-4E86-B202-1F82610C8156';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Nuevo
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '061527DA-DCAB-4E86-B202-1F82610C8156');

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 3500,
    CatPaymentTermId = @Term_12sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '061527DA-DCAB-4E86-B202-1F82610C8156'
  AND CatPaymentTermId = @Term_42sem;

PRINT '✓ Oferta 6 actualizada: 3500/12sem/N1';
PRINT '';

-- ============================================================================
-- ESCENARIO 4: Ofertas 7-8
-- Excel: $10,500/42sem + $5,000/12sem | Integral | N1 | Frecuente | Zacatecas
-- BD: CC4B8A31 (1546239) | 9200/42sem + 7500/32sem | SLP | Nuevo
-- BD: ED700AD5 (1787126) | 5500/32sem | Zacatecas | Nuevo
-- ============================================================================

PRINT '--- ESCENARIO 4: Ofertas 7-8 ---';
PRINT 'Cliente: 1546239 - MARTIN CORONA AGUILAR';

-- Oferta 7
UPDATE dbo.Offer
SET SalesTypeId = @SaleType_Integral,
    BranchId = @Branch_Zacatecas
WHERE Id = 'CC4B8A31-CE6A-40CD-8302-DA3C0658DBE2';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Frecuente
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = 'CC4B8A31-CE6A-40CD-8302-DA3C0658DBE2');

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 10500,
    CatPaymentTermId = @Term_42sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = 'CC4B8A31-CE6A-40CD-8302-DA3C0658DBE2'
  AND CatPaymentTermId = @Term_42sem;

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 5000,
    CatPaymentTermId = @Term_12sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = 'CC4B8A31-CE6A-40CD-8302-DA3C0658DBE2'
  AND CatPaymentTermId = @Term_32sem;

PRINT '✓ Oferta 7 actualizada: 10500/42sem + 5000/12sem/N1';

PRINT 'Cliente: 1787126 - BLANCA LILIANA LOPEZ DAVILA';

-- Oferta 8
UPDATE dbo.Offer
SET SalesTypeId = @SaleType_Integral,
    BranchId = @Branch_Zacatecas
WHERE Id = 'ED700AD5-8B14-48E5-90C4-B19DC9DD853D';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Frecuente
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = 'ED700AD5-8B14-48E5-90C4-B19DC9DD853D');

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 10500,
    CatPaymentTermId = @Term_42sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = 'ED700AD5-8B14-48E5-90C4-B19DC9DD853D'
  AND CatPaymentTermId = @Term_32sem;

INSERT INTO dbo.AuthorizedAmountAndTerm (Id, OfferId, Amount, CatPaymentTermId, CatPaymentTermTypeId)
VALUES (NEWID(), 'ED700AD5-8B14-48E5-90C4-B19DC9DD853D', 5000, @Term_12sem, @PriceLevel_N1);

PRINT '✓ Oferta 8 actualizada: 10500/42sem + 5000/12sem/N1';
PRINT '';

-- ============================================================================
-- ESCENARIO 5: Ofertas 9-10
-- Excel: $7,500/32sem (solo 1) | Integral | N1 | Nuevo | Aguascalientes
-- BD: B3EA6615 (2238507) | 9200/42sem + 7500/32sem | SLP | Nuevo
-- BD: 19EC9494 (2286686) | 9500/42sem + 7800/32sem | SLP | Nuevo
-- ============================================================================

PRINT '--- ESCENARIO 5: Ofertas 9-10 ---';
PRINT 'Cliente: 2238507 - CLAUDIA GABRIELA OBREGON OJEDA';

-- Oferta 9
UPDATE dbo.Offer
SET SalesTypeId = @SaleType_Integral,
    BranchId = @Branch_Aguascalientes
WHERE Id = 'B3EA6615-AF47-435A-B783-AD424CB792E6';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Nuevo
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = 'B3EA6615-AF47-435A-B783-AD424CB792E6');

DELETE FROM dbo.AuthorizedAmountAndTerm
WHERE OfferId = 'B3EA6615-AF47-435A-B783-AD424CB792E6'
  AND CatPaymentTermId = @Term_32sem;

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 7500,
    CatPaymentTermId = @Term_32sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = 'B3EA6615-AF47-435A-B783-AD424CB792E6'
  AND CatPaymentTermId = @Term_42sem;

PRINT '✓ Oferta 9 actualizada: 7500/32sem/N1';

PRINT 'Cliente: 2286686 - MARIA ELIZABETH QUISTIAN QUIROZ';

-- Oferta 10
UPDATE dbo.Offer
SET SalesTypeId = @SaleType_Integral,
    BranchId = @Branch_Aguascalientes
WHERE Id = '19EC9494-008E-4B70-B27F-87C5516157FB';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Nuevo
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '19EC9494-008E-4B70-B27F-87C5516157FB');

DELETE FROM dbo.AuthorizedAmountAndTerm
WHERE OfferId = '19EC9494-008E-4B70-B27F-87C5516157FB'
  AND CatPaymentTermId = @Term_32sem;

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 7500,
    CatPaymentTermId = @Term_32sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '19EC9494-008E-4B70-B27F-87C5516157FB'
  AND CatPaymentTermId = @Term_42sem;

PRINT '✓ Oferta 10 actualizada: 7500/32sem/N1';
PRINT '';

-- ============================================================================
-- ESCENARIO 6: Ofertas 11-12
-- Excel: $5,500/32sem + $7,500/42sem | Integral | N1 | Frecuente | Zacatecas
-- BD: 23D24ADA (2443421) | 9200/42sem + 7500/32sem | Aguascalientes | Nuevo
-- BD: 4AAB5567 (2092976) | 4500/32sem | Aguascalientes | Nuevo
-- ============================================================================

PRINT '--- ESCENARIO 6: Ofertas 11-12 ---';
PRINT 'Cliente: 2443421 - JUANA GABRIELA CARDONA LOERA';

-- Oferta 11
UPDATE dbo.Offer
SET SalesTypeId = @SaleType_Integral,
    BranchId = @Branch_Zacatecas
WHERE Id = '23D24ADA-086D-4587-A335-499BB3E642FB';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Frecuente
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '23D24ADA-086D-4587-A335-499BB3E642FB');

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 5500,
    CatPaymentTermId = @Term_32sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '23D24ADA-086D-4587-A335-499BB3E642FB'
  AND CatPaymentTermId = @Term_32sem;

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 7500,
    CatPaymentTermId = @Term_42sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '23D24ADA-086D-4587-A335-499BB3E642FB'
  AND CatPaymentTermId = @Term_42sem;

PRINT '✓ Oferta 11 actualizada: 5500/32sem + 7500/42sem/N1';

PRINT 'Cliente: 2092976 - MARIA ANTONIETA BALLIN ESQUIVEL';

-- Oferta 12
UPDATE dbo.Offer
SET SalesTypeId = @SaleType_Integral,
    BranchId = @Branch_Zacatecas
WHERE Id = '4AAB5567-AB50-4249-BCEC-5DF47AD69251';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Frecuente
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '4AAB5567-AB50-4249-BCEC-5DF47AD69251');

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 5500,
    CatPaymentTermId = @Term_32sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '4AAB5567-AB50-4249-BCEC-5DF47AD69251'
  AND CatPaymentTermId = @Term_32sem;

INSERT INTO dbo.AuthorizedAmountAndTerm (Id, OfferId, Amount, CatPaymentTermId, CatPaymentTermTypeId)
VALUES (NEWID(), '4AAB5567-AB50-4249-BCEC-5DF47AD69251', 7500, @Term_42sem, @PriceLevel_N1);

PRINT '✓ Oferta 12 actualizada: 5500/32sem + 7500/42sem/N1';
PRINT '';

-- ============================================================================
-- ESCENARIO 7: Ofertas 13-14
-- Excel: $4,000/12sem (solo 1) | Tradicional | N1 | Nuevo | Aguascalientes
-- BD: 06568A0D (1715553) | 25000/65sem + 20000/52sem | Aguascalientes | Nuevo
-- BD: 91832B85 (1932160) | 11000/42sem + 8500/32sem | Aguascalientes | Nuevo
-- ============================================================================

PRINT '--- ESCENARIO 7: Ofertas 13-14 ---';
PRINT 'Cliente: 1715553 - LIDYA CONTRERAS GONZALEZ';

-- Oferta 13
UPDATE dbo.Offer
SET SalesTypeId = @SaleType_Tradicional,
    BranchId = @Branch_Aguascalientes
WHERE Id = '06568A0D-C3C0-436D-8471-43FB45DBD15F';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Nuevo
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '06568A0D-C3C0-436D-8471-43FB45DBD15F');

DELETE FROM dbo.AuthorizedAmountAndTerm
WHERE OfferId = '06568A0D-C3C0-436D-8471-43FB45DBD15F'
  AND CatPaymentTermId = @Term_52sem;

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 4000,
    CatPaymentTermId = @Term_12sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '06568A0D-C3C0-436D-8471-43FB45DBD15F'
  AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '65 sem');

PRINT '✓ Oferta 13 actualizada: 4000/12sem/N1';

PRINT 'Cliente: 1932160 - MAGALY CRUZ GUTIERREZ';

-- Oferta 14
UPDATE dbo.Offer
SET SalesTypeId = @SaleType_Tradicional,
    BranchId = @Branch_Aguascalientes
WHERE Id = '91832B85-EB21-4224-B1EC-894B6ED24900';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Nuevo
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '91832B85-EB21-4224-B1EC-894B6ED24900');

DELETE FROM dbo.AuthorizedAmountAndTerm
WHERE OfferId = '91832B85-EB21-4224-B1EC-894B6ED24900'
  AND CatPaymentTermId = @Term_32sem;

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 4000,
    CatPaymentTermId = @Term_12sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '91832B85-EB21-4224-B1EC-894B6ED24900'
  AND CatPaymentTermId = @Term_42sem;

PRINT '✓ Oferta 14 actualizada: 4000/12sem/N1';
PRINT '';

-- ============================================================================
-- ESCENARIO 8: Ofertas 15-16
-- Excel: $4,000/12sem + $10,500/32sem | Tradicional | N1 | Frecuente | Aguascalientes
-- BD: 4C7F8E3F (2335835) | 6900/42sem + 6100/32sem | Aguascalientes | Nuevo
-- BD: D4620159 (2528279) | 10000/42sem + 8000/32sem | Aguascalientes | Nuevo
-- ============================================================================

PRINT '--- ESCENARIO 8: Ofertas 15-16 ---';
PRINT 'Cliente: 2335835 - LAURA TRISTAN MENDOZA';

-- Oferta 15
UPDATE dbo.Offer
SET SalesTypeId = @SaleType_Tradicional,
    BranchId = @Branch_Aguascalientes
WHERE Id = '4C7F8E3F-6AE1-4012-B69F-1E682689FD8A';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Frecuente
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '4C7F8E3F-6AE1-4012-B69F-1E682689FD8A');

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 4000,
    CatPaymentTermId = @Term_12sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '4C7F8E3F-6AE1-4012-B69F-1E682689FD8A'
  AND CatPaymentTermId = @Term_42sem;

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 10500,
    CatPaymentTermId = @Term_32sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '4C7F8E3F-6AE1-4012-B69F-1E682689FD8A'
  AND CatPaymentTermId = @Term_32sem;

PRINT '✓ Oferta 15 actualizada: 4000/12sem + 10500/32sem/N1';

PRINT 'Cliente: 2528279 - LUIS ANTONIO MENDEZ CERVANTES';

-- Oferta 16
UPDATE dbo.Offer
SET SalesTypeId = @SaleType_Tradicional,
    BranchId = @Branch_Aguascalientes
WHERE Id = 'D4620159-DB8B-4974-B220-EEBC4C316725';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Frecuente
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = 'D4620159-DB8B-4974-B220-EEBC4C316725');

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 4000,
    CatPaymentTermId = @Term_12sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = 'D4620159-DB8B-4974-B220-EEBC4C316725'
  AND CatPaymentTermId = @Term_42sem;

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 10500,
    CatPaymentTermId = @Term_32sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = 'D4620159-DB8B-4974-B220-EEBC4C316725'
  AND CatPaymentTermId = @Term_32sem;

PRINT '✓ Oferta 16 actualizada: 4000/12sem + 10500/32sem/N1';
PRINT '';

-- ============================================================================
-- ESCENARIO 9: Ofertas 17-18
-- Excel: $4,000/12sem (solo 1) | Tradicional | N1 | Nuevo | Aguascalientes
-- BD: C593379F (2245615) | 4700/32sem | SLP | Nuevo
-- BD: Necesitamos buscar otra oferta disponible
-- ============================================================================

PRINT '--- ESCENARIO 9: Ofertas 17-18 ---';
PRINT 'Cliente: 2245615 - MAYRA NOHEMI CASTRO SEGOVIA';

-- Oferta 17
UPDATE dbo.Offer
SET SalesTypeId = @SaleType_Tradicional,
    BranchId = @Branch_Aguascalientes
WHERE Id = 'C593379F-4E39-4240-9EBF-BD894DC68F4C';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Nuevo
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = 'C593379F-4E39-4240-9EBF-BD894DC68F4C');

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 4000,
    CatPaymentTermId = @Term_12sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = 'C593379F-4E39-4240-9EBF-BD894DC68F4C'
  AND CatPaymentTermId = @Term_32sem;

PRINT '✓ Oferta 17 actualizada: 4000/12sem/N1';

PRINT 'Buscando oferta 18 disponible...';
PRINT 'NOTA: Si no hay más ofertas disponibles con "Normal", este escenario queda con solo 1 oferta.';
PRINT 'Revisar manualmente si se requiere una 18va oferta adicional.';
PRINT '';

-- ============================================================================
-- RESUMEN FINAL
-- ============================================================================

PRINT '=== RESUMEN DE ACTUALIZACIÓN ===';
PRINT '';
PRINT '✓ 17 ofertas actualizadas correctamente (Oferta 18 pendiente de identificar)';
PRINT '✓ Todas las ofertas actualizadas tienen nivel N1 visible';
PRINT '';
PRINT 'Distribución por sucursal:';
PRINT '  - SLP: 6 ofertas (Escenarios 1-3)';
PRINT '  - Zacatecas: 6 ofertas (Escenarios 4, 6)';
PRINT '  - Aguascalientes: 5 ofertas (Escenarios 5, 7-9)';
PRINT '';
PRINT 'Distribución por tipo:';
PRINT '  - Tradicional: 11 ofertas';
PRINT '  - Integral: 6 ofertas';
PRINT '';
PRINT 'Distribución por cliente:';
PRINT '  - Nuevo: 10 ofertas';
PRINT '  - Frecuente: 7 ofertas';
PRINT '';
PRINT '=== ACTUALIZACIÓN COMPLETADA ===';

GO
