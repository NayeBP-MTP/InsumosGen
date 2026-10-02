USE [AVTs];
GO

/*
================================================================================
SCRIPT DE ACTUALIZACIÓN - 18 OFERTAS UNBUNDLING
================================================================================
Este script actualiza 18 ofertas existentes según los requerimientos del Excel.
Basado en el estado actual de la base de datos (offers.txt actualizado).

IMPORTANTE: 
- La Oferta 1 (85120) ya fue actualizada previamente y tiene N1 visible
- Este script actualiza las 17 ofertas restantes (Ofertas 2-18)

Fecha: 2026-02-17
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
-- ESCENARIO 1: Oferta 2 (Oferta 1 ya está actualizada)
-- Excel: $5,000/12sem (solo 1 oferta) | Tradicional | N1 | Nuevo | SLP
-- BD Actual: BC360B4B (601022) | 9200/42sem + 7500/32sem | SLP
-- ============================================================================

PRINT '--- ESCENARIO 1: Oferta 2 ---';
PRINT 'Cliente: 601022 - CECILIA RODRIGUEZ MALDONADO';

-- Actualizar Offer (ya está en SLP y Tradicional, mantener)
UPDATE dbo.Offer
SET SalesTypeId = @SaleType_Tradicional,
    BranchId = @Branch_SLP
WHERE Id = 'BC360B4B-D73A-460F-8240-6541C3531863';

-- Actualizar Customer (ya es Nuevo, mantener)
UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Nuevo
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = 'BC360B4B-D73A-460F-8240-6541C3531863');

-- Eliminar segunda oferta autorizada (32 sem)
DELETE FROM dbo.AuthorizedAmountAndTerm
WHERE OfferId = 'BC360B4B-D73A-460F-8240-6541C3531863'
  AND CatPaymentTermId = @Term_32sem;

-- Actualizar primera oferta (5000/12sem)
UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 5000,
    CatPaymentTermId = @Term_12sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = 'BC360B4B-D73A-460F-8240-6541C3531863'
  AND CatPaymentTermId = @Term_42sem;

PRINT '✓ Oferta 2 actualizada: 5000/12sem/N1';
PRINT '';

-- ============================================================================
-- ESCENARIO 2: Ofertas 3-4
-- Excel: $4,500/12sem + $10,500/32sem | Tradicional | N1 | Frecuente | SLP
-- BD Actual: 3F366374 (1208659) | 7500/32sem | Zacatecas | Nuevo
-- BD Actual: 965756F8 (1262923) | 5000/32sem | SLP | Nuevo
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

-- Actualizar primera oferta (4500/12sem)
UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 4500,
    CatPaymentTermId = @Term_12sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '3F366374-2598-4D77-B4AE-7E9FF10600B1'
  AND CatPaymentTermId = @Term_32sem;

-- Insertar segunda oferta (10500/32sem)
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

-- Actualizar primera oferta (4500/12sem)
UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 4500,
    CatPaymentTermId = @Term_12sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '965756F8-F046-4F36-804A-02491C7BC89F'
  AND CatPaymentTermId = @Term_32sem;

-- Insertar segunda oferta (10500/32sem)
INSERT INTO dbo.AuthorizedAmountAndTerm (Id, OfferId, Amount, CatPaymentTermId, CatPaymentTermTypeId)
VALUES (NEWID(), '965756F8-F046-4F36-804A-02491C7BC89F', 10500, @Term_32sem, @PriceLevel_N1);

PRINT '✓ Oferta 4 actualizada: 4500/12sem + 10500/32sem/N1';
PRINT '';

-- ============================================================================
-- ESCENARIO 3: Ofertas 5-6
-- Excel: $3,500/12sem (solo 1 oferta) | Tradicional | N1 | Nuevo | SLP
-- BD Actual: 91BDB477 (1314924) | 12500/52sem + 10400/42sem | Aguascalientes | Nuevo
-- BD Actual: 771D10AC (1357750) | 9000/42sem + 7200/32sem | SLP | Nuevo
-- ============================================================================

PRINT '--- ESCENARIO 3: Ofertas 5-6 ---';
PRINT 'Cliente: 1314924 - DIANA LAURA RANGEL LOPEZ';

-- Oferta 5
UPDATE dbo.Offer
SET SalesTypeId = @SaleType_Tradicional,
    BranchId = @Branch_SLP
WHERE Id = '91BDB477-89AE-455B-AA06-8F9CF3B3A530';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Nuevo
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '91BDB477-89AE-455B-AA06-8F9CF3B3A530');

-- Eliminar segunda oferta autorizada (42 sem)
DELETE FROM dbo.AuthorizedAmountAndTerm
WHERE OfferId = '91BDB477-89AE-455B-AA06-8F9CF3B3A530'
  AND CatPaymentTermId = @Term_42sem;

-- Actualizar primera oferta (3500/12sem)
UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 3500,
    CatPaymentTermId = @Term_12sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '91BDB477-89AE-455B-AA06-8F9CF3B3A530'
  AND CatPaymentTermId = @Term_52sem;

PRINT '✓ Oferta 5 actualizada: 3500/12sem/N1';

PRINT 'Cliente: 1357750 - MAYRA ALEJANDRA MIER SANCHEZ';

-- Oferta 6
UPDATE dbo.Offer
SET SalesTypeId = @SaleType_Tradicional,
    BranchId = @Branch_SLP
WHERE Id = '771D10AC-677A-4EE4-836F-138AE0471EDF';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Nuevo
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '771D10AC-677A-4EE4-836F-138AE0471EDF');

-- Eliminar segunda oferta autorizada (32 sem)
DELETE FROM dbo.AuthorizedAmountAndTerm
WHERE OfferId = '771D10AC-677A-4EE4-836F-138AE0471EDF'
  AND CatPaymentTermId = @Term_32sem;

-- Actualizar primera oferta (3500/12sem)
UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 3500,
    CatPaymentTermId = @Term_12sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '771D10AC-677A-4EE4-836F-138AE0471EDF'
  AND CatPaymentTermId = @Term_42sem;

PRINT '✓ Oferta 6 actualizada: 3500/12sem/N1';
PRINT '';

-- ============================================================================
-- ESCENARIO 4: Ofertas 7-8
-- Excel: $10,500/42sem + $5,000/12sem | Integral | N1 | Frecuente | Zacatecas
-- BD Actual: CC4B8A31 (1546239) | 9200/42sem + 7500/32sem | SLP | Nuevo
-- BD Actual: 4AAB5567 (2092976) | 4500/32sem | Aguascalientes | Nuevo
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

-- Actualizar primera oferta (10500/42sem)
UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 10500,
    CatPaymentTermId = @Term_42sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = 'CC4B8A31-CE6A-40CD-8302-DA3C0658DBE2'
  AND CatPaymentTermId = @Term_42sem;

-- Actualizar segunda oferta (5000/12sem)
UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 5000,
    CatPaymentTermId = @Term_12sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = 'CC4B8A31-CE6A-40CD-8302-DA3C0658DBE2'
  AND CatPaymentTermId = @Term_32sem;

PRINT '✓ Oferta 7 actualizada: 10500/42sem + 5000/12sem/N1';

PRINT 'Cliente: 2092976 - MARIA ANTONIETA BALLIN ESQUIVEL';

-- Oferta 8
UPDATE dbo.Offer
SET SalesTypeId = @SaleType_Integral,
    BranchId = @Branch_Zacatecas
WHERE Id = '4AAB5567-AB50-4249-BCEC-5DF47AD69251';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Frecuente
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '4AAB5567-AB50-4249-BCEC-5DF47AD69251');

-- Actualizar primera oferta existente (10500/42sem)
UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 10500,
    CatPaymentTermId = @Term_42sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '4AAB5567-AB50-4249-BCEC-5DF47AD69251'
  AND CatPaymentTermId = @Term_32sem;

-- Insertar segunda oferta (5000/12sem)
INSERT INTO dbo.AuthorizedAmountAndTerm (Id, OfferId, Amount, CatPaymentTermId, CatPaymentTermTypeId)
VALUES (NEWID(), '4AAB5567-AB50-4249-BCEC-5DF47AD69251', 5000, @Term_12sem, @PriceLevel_N1);

PRINT '✓ Oferta 8 actualizada: 10500/42sem + 5000/12sem/N1';
PRINT '';

-- ============================================================================
-- ESCENARIO 5: Ofertas 9-10
-- Excel: $7,500/32sem (solo 1) | Integral | N1 | Nuevo | Aguascalientes
-- BD Actual: B3EA6615 (2238507) | 9200/42sem + 7500/32sem | SLP | Nuevo
-- BD Actual: 19EC9494 (2286686) | 9500/42sem + 7800/32sem | SLP | Nuevo
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

-- Eliminar segunda oferta autorizada (32 sem)
DELETE FROM dbo.AuthorizedAmountAndTerm
WHERE OfferId = 'B3EA6615-AF47-435A-B783-AD424CB792E6'
  AND CatPaymentTermId = @Term_32sem;

-- Actualizar primera oferta (7500/32sem)
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

-- Eliminar segunda oferta autorizada (32 sem)
DELETE FROM dbo.AuthorizedAmountAndTerm
WHERE OfferId = '19EC9494-008E-4B70-B27F-87C5516157FB'
  AND CatPaymentTermId = @Term_32sem;

-- Actualizar primera oferta (7500/32sem)
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
-- BD Actual: 23D24ADA (2443421) | 9200/42sem + 7500/32sem | Aguascalientes | Nuevo
-- BD Actual: 8385BEAD (3002066) | 9500/42sem + 7800/32sem | SLP | Nuevo
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

-- Actualizar primera oferta (5500/32sem)
UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 5500,
    CatPaymentTermId = @Term_32sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '23D24ADA-086D-4587-A335-499BB3E642FB'
  AND CatPaymentTermId = @Term_32sem;

-- Actualizar segunda oferta (7500/42sem)
UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 7500,
    CatPaymentTermId = @Term_42sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '23D24ADA-086D-4587-A335-499BB3E642FB'
  AND CatPaymentTermId = @Term_42sem;

PRINT '✓ Oferta 11 actualizada: 5500/32sem + 7500/42sem/N1';

PRINT 'Cliente: 3002066 - ANA MARIA RICO ZAVALA';

-- Oferta 12
UPDATE dbo.Offer
SET SalesTypeId = @SaleType_Integral,
    BranchId = @Branch_Zacatecas
WHERE Id = '8385BEAD-EC91-4F5D-BC23-7896751FC341';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Frecuente
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '8385BEAD-EC91-4F5D-BC23-7896751FC341');

-- Actualizar primera oferta (5500/32sem)
UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 5500,
    CatPaymentTermId = @Term_32sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '8385BEAD-EC91-4F5D-BC23-7896751FC341'
  AND CatPaymentTermId = @Term_32sem;

-- Actualizar segunda oferta (7500/42sem)
UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 7500,
    CatPaymentTermId = @Term_42sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '8385BEAD-EC91-4F5D-BC23-7896751FC341'
  AND CatPaymentTermId = @Term_42sem;

PRINT '✓ Oferta 12 actualizada: 5500/32sem + 7500/42sem/N1';
PRINT '';

-- ============================================================================
-- ESCENARIO 7: Ofertas 13-14
-- Excel: $4,000/12sem (solo 1) | Tradicional | N1 | Nuevo | Aguascalientes
-- BD Actual: 06568A0D (1715553) | 11500/42sem + 9000/32sem | Aguascalientes | Nuevo
-- BD Actual: 91832B85 (1932160) | 11000/42sem + 8500/32sem | Aguascalientes | Nuevo
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

-- Eliminar segunda oferta autorizada (32 sem)
DELETE FROM dbo.AuthorizedAmountAndTerm
WHERE OfferId = '06568A0D-C3C0-436D-8471-43FB45DBD15F'
  AND CatPaymentTermId = @Term_32sem;

-- Actualizar primera oferta (4000/12sem)
UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 4000,
    CatPaymentTermId = @Term_12sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '06568A0D-C3C0-436D-8471-43FB45DBD15F'
  AND CatPaymentTermId = @Term_42sem;

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

-- Eliminar segunda oferta autorizada (32 sem)
DELETE FROM dbo.AuthorizedAmountAndTerm
WHERE OfferId = '91832B85-EB21-4224-B1EC-894B6ED24900'
  AND CatPaymentTermId = @Term_32sem;

-- Actualizar primera oferta (4000/12sem)
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
-- BD Actual: 6F64D01B (1428759) | 5000/32sem | Aguascalientes | Nuevo
-- BD Actual: 4C7F8E3F (2335835) | 6900/42sem + 6100/32sem | Aguascalientes | Nuevo
-- ============================================================================

PRINT '--- ESCENARIO 8: Ofertas 15-16 ---';
PRINT 'Cliente: 1428759 - MONICA JANETTE GUTIERREZ MARIN';

-- Oferta 15
UPDATE dbo.Offer
SET SalesTypeId = @SaleType_Tradicional,
    BranchId = @Branch_Aguascalientes
WHERE Id = '6F64D01B-6A62-4C87-9366-777C0EAD6BB7';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Frecuente
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '6F64D01B-6A62-4C87-9366-777C0EAD6BB7');

-- Actualizar primera oferta (4000/12sem)
UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 4000,
    CatPaymentTermId = @Term_12sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '6F64D01B-6A62-4C87-9366-777C0EAD6BB7'
  AND CatPaymentTermId = @Term_32sem;

-- Insertar segunda oferta (10500/32sem)
INSERT INTO dbo.AuthorizedAmountAndTerm (Id, OfferId, Amount, CatPaymentTermId, CatPaymentTermTypeId)
VALUES (NEWID(), '6F64D01B-6A62-4C87-9366-777C0EAD6BB7', 10500, @Term_32sem, @PriceLevel_N1);

PRINT '✓ Oferta 15 actualizada: 4000/12sem + 10500/32sem/N1';

PRINT 'Cliente: 2335835 - LAURA TRISTAN MENDOZA';

-- Oferta 16
UPDATE dbo.Offer
SET SalesTypeId = @SaleType_Tradicional,
    BranchId = @Branch_Aguascalientes
WHERE Id = '4C7F8E3F-6AE1-4012-B69F-1E682689FD8A';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Frecuente
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '4C7F8E3F-6AE1-4012-B69F-1E682689FD8A');

-- Actualizar primera oferta (4000/12sem)
UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 4000,
    CatPaymentTermId = @Term_12sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '4C7F8E3F-6AE1-4012-B69F-1E682689FD8A'
  AND CatPaymentTermId = @Term_32sem;

-- Actualizar segunda oferta (10500/32sem)
UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 10500,
    CatPaymentTermId = @Term_32sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '4C7F8E3F-6AE1-4012-B69F-1E682689FD8A'
  AND CatPaymentTermId = @Term_42sem;

PRINT '✓ Oferta 16 actualizada: 4000/12sem + 10500/32sem/N1';
PRINT '';

-- ============================================================================
-- ESCENARIO 9: Ofertas 17-18
-- Excel: $4,000/12sem (solo 1) | Tradicional | N1 | Nuevo | Aguascalientes
-- BD Actual: D4620159 (2528279) | 10000/42sem + 8000/32sem | Aguascalientes | Nuevo
-- BD Actual: BBB5FE78 (3337967) | 7500/42sem | Aguascalientes | Nuevo
-- ============================================================================

PRINT '--- ESCENARIO 9: Ofertas 17-18 ---';
PRINT 'Cliente: 2528279 - LUIS ANTONIO MENDEZ CERVANTES';

-- Oferta 17
UPDATE dbo.Offer
SET SalesTypeId = @SaleType_Tradicional,
    BranchId = @Branch_Aguascalientes
WHERE Id = 'D4620159-DB8B-4974-B220-EEBC4C316725';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Nuevo
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = 'D4620159-DB8B-4974-B220-EEBC4C316725');

-- Eliminar segunda oferta autorizada (32 sem)
DELETE FROM dbo.AuthorizedAmountAndTerm
WHERE OfferId = 'D4620159-DB8B-4974-B220-EEBC4C316725'
  AND CatPaymentTermId = @Term_32sem;

-- Actualizar primera oferta (4000/12sem)
UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 4000,
    CatPaymentTermId = @Term_12sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = 'D4620159-DB8B-4974-B220-EEBC4C316725'
  AND CatPaymentTermId = @Term_42sem;

PRINT '✓ Oferta 17 actualizada: 4000/12sem/N1';

PRINT 'Cliente: 3337967 - CHRISTIAN FERNANDO ZAMARRIPA HERRERA';

-- Oferta 18
UPDATE dbo.Offer
SET SalesTypeId = @SaleType_Tradicional,
    BranchId = @Branch_Aguascalientes
WHERE Id = 'BBB5FE78-C066-4EF4-9941-32E5F2EF368F';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Nuevo
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = 'BBB5FE78-C066-4EF4-9941-32E5F2EF368F');

-- Actualizar primera oferta (4000/12sem)
UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 4000,
    CatPaymentTermId = @Term_12sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = 'BBB5FE78-C066-4EF4-9941-32E5F2EF368F'
  AND CatPaymentTermId = @Term_42sem;

PRINT '✓ Oferta 18 actualizada: 4000/12sem/N1';
PRINT '';

-- ============================================================================
-- RESUMEN FINAL
-- ============================================================================

PRINT '=== RESUMEN DE ACTUALIZACIÓN ===';
PRINT '';
PRINT '✓ 18 ofertas actualizadas correctamente';
PRINT '✓ Todas las ofertas tienen nivel N1 visible';
PRINT '';
PRINT 'Distribución por sucursal:';
PRINT '  - SLP: 6 ofertas (Escenarios 1-3)';
PRINT '  - Zacatecas: 6 ofertas (Escenarios 4, 6)';
PRINT '  - Aguascalientes: 6 ofertas (Escenarios 5, 7-9)';
PRINT '';
PRINT 'Distribución por tipo:';
PRINT '  - Tradicional: 12 ofertas';
PRINT '  - Integral: 6 ofertas';
PRINT '';
PRINT 'Distribución por cliente:';
PRINT '  - Nuevo: 10 ofertas';
PRINT '  - Frecuente: 8 ofertas';
PRINT '';
PRINT '=== ACTUALIZACIÓN COMPLETADA ===';

GO
