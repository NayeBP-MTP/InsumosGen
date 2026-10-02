USE [AVTs];

/*
================================================================================
SCRIPT DE ACTUALIZACIÓN - 18 OFERTAS SEGÚN EXCEL
================================================================================
Proyecto: Unbundling - Ajuste de ofertas para pruebas
Fecha: 17 Feb 2026
Autor: Cascade AI

IMPORTANTE: 
- Este script actualiza 18 ofertas existentes según especificaciones del Excel
- Ejecutar en ambiente de QA/DEV primero
- Hacer backup antes de ejecutar en producción
- Validar con el query de verificación después de ejecutar

CAMBIOS PRINCIPALES:
1. Ajustar montos y plazos (AuthorizedAmountAndTerm)
2. Cambiar nivel de precio a N1 (CatPaymentTermType)
3. Ajustar tipo de cliente (Nuevo/Frecuente)
4. Cambiar tipo de seguro (Tradicional/Integral)
5. Ajustar sucursales según Excel
================================================================================
*/

-- ============================================================================
-- DECLARACIÓN DE VARIABLES (IDs de Catálogos)
-- ============================================================================

DECLARE 
    -- Sucursales
    @Branch_SLP UNIQUEIDENTIFIER = '1D0712B3-DBE1-4872-BB82-0879B123E7EC',
    @Branch_Zacatecas UNIQUEIDENTIFIER = '51BCD590-3B05-47D9-8328-93ADE7B47BD1',
    @Branch_Aguascalientes UNIQUEIDENTIFIER = '7AE76DAF-08C3-43FB-B3E4-455E64AED01C',
    
    -- Tipos de Seguro
    @SaleType_Tradicional UNIQUEIDENTIFIER = 'F7049160-F367-438C-A0A8-0B63F6B03EBD', -- Home Credit
    @SaleType_Integral UNIQUEIDENTIFIER = '21BE783E-8B08-405D-A449-A21FABC8E113', -- Negocio
    
    -- Tipos de Cliente
    @CustomerType_Nuevo UNIQUEIDENTIFIER = 'D681D8CC-F364-499A-9322-F6AEDBBF24AE',
    @CustomerType_Frecuente UNIQUEIDENTIFIER = '4819CA7D-5A32-4857-A6B2-12C99D5EA295',
    
    -- Plazos
    @Term_12sem UNIQUEIDENTIFIER = '81C7FA1C-FFB3-4CF3-AEB7-BDDE1A8A4D6C',
    @Term_32sem UNIQUEIDENTIFIER = '403E89C5-B995-4AA1-8ADA-5B99E0267BB2',
    @Term_42sem UNIQUEIDENTIFIER = 'E2741F66-A665-491E-84AB-EB0DECDA3E8A',
    @Term_52sem UNIQUEIDENTIFIER = 'E1B43A01-C984-4D50-A468-A4E8FCDA1296',
    
    -- Niveles de Precio
    @PriceLevel_N1 UNIQUEIDENTIFIER = 'B771BFC0-D40A-49A7-8372-72F7776A6338';

-- ============================================================================
-- PASO 1: BACKUP DE DATOS ORIGINALES
-- ============================================================================

PRINT '';
PRINT '=== PASO 1: CREANDO BACKUP DE DATOS ORIGINALES ===';

-- Crear tabla temporal para backup de Offer
IF OBJECT_ID('tempdb..#Backup_Offer') IS NOT NULL DROP TABLE #Backup_Offer;
SELECT * INTO #Backup_Offer FROM dbo.Offer WHERE Id IN (
    '2D676E6C-C0A1-4715-99ED-9BBA0EDA816A', 'FAB7A814-ED3E-4EF4-907E-EDD004ACC6C9',
    '8D619493-D6FA-4383-87A7-A05E6BAEEFD5', 'B9EADADE-17F0-45D5-A372-5225587117C8',
    '1585343D-621F-46D9-A4D9-82A0DD687F45', 'C24D3C96-1CEC-4A4F-94CC-244055C7C066',
    '0EA85C1D-B199-41AB-82E5-B4EAF8AA5F08', '7E02D10E-2698-415F-A7A7-B5D07478CB3A',
    '58E7CF45-6A85-4A83-AEF2-2C69E1E79DA2', '1F6B6374-AFC1-4A92-829A-E5206DB5724A',
    '751DA029-64F4-409C-AA81-1FA8B8C554AB', '6C6BE2C9-0284-4E59-A9F0-B607505D5202',
    '858672A0-5530-476F-AB96-D15CE71D68CE', '357E0A2A-7EAA-46E6-8B6B-B43533F4E794',
    '5ECB173F-71B5-41BE-96DD-0F76EE17A52C', '3BFCCE94-9C37-4DB6-8E27-8C904FABC6CF',
    '92F25F57-E32B-4AAB-BB8F-DF51C302A01E', '469655B4-4126-4E4A-A6E4-1E19D3B11A28'
);
PRINT '✓ Backup de Offer: ' + CAST(@@ROWCOUNT AS VARCHAR) + ' registros';

-- Crear tabla temporal para backup de Customer
IF OBJECT_ID('tempdb..#Backup_Customer') IS NOT NULL DROP TABLE #Backup_Customer;
SELECT C.* INTO #Backup_Customer FROM dbo.Customer C
INNER JOIN dbo.Offer O ON C.Id = O.CustomerId
WHERE O.Id IN (
    '2D676E6C-C0A1-4715-99ED-9BBA0EDA816A', 'FAB7A814-ED3E-4EF4-907E-EDD004ACC6C9',
    '8D619493-D6FA-4383-87A7-A05E6BAEEFD5', 'B9EADADE-17F0-45D5-A372-5225587117C8',
    '1585343D-621F-46D9-A4D9-82A0DD687F45', 'C24D3C96-1CEC-4A4F-94CC-244055C7C066',
    '0EA85C1D-B199-41AB-82E5-B4EAF8AA5F08', '7E02D10E-2698-415F-A7A7-B5D07478CB3A',
    '58E7CF45-6A85-4A83-AEF2-2C69E1E79DA2', '1F6B6374-AFC1-4A92-829A-E5206DB5724A',
    '751DA029-64F4-409C-AA81-1FA8B8C554AB', '6C6BE2C9-0284-4E59-A9F0-B607505D5202',
    '858672A0-5530-476F-AB96-D15CE71D68CE', '357E0A2A-7EAA-46E6-8B6B-B43533F4E794',
    '5ECB173F-71B5-41BE-96DD-0F76EE17A52C', '3BFCCE94-9C37-4DB6-8E27-8C904FABC6CF',
    '92F25F57-E32B-4AAB-BB8F-DF51C302A01E', '469655B4-4126-4E4A-A6E4-1E19D3B11A28'
);
PRINT '✓ Backup de Customer: ' + CAST(@@ROWCOUNT AS VARCHAR) + ' registros';

-- Crear tabla temporal para backup de AuthorizedAmountAndTerm
IF OBJECT_ID('tempdb..#Backup_AuthorizedAmountAndTerm') IS NOT NULL DROP TABLE #Backup_AuthorizedAmountAndTerm;
SELECT * INTO #Backup_AuthorizedAmountAndTerm FROM dbo.AuthorizedAmountAndTerm WHERE OfferId IN (
    '2D676E6C-C0A1-4715-99ED-9BBA0EDA816A', 'FAB7A814-ED3E-4EF4-907E-EDD004ACC6C9',
    '8D619493-D6FA-4383-87A7-A05E6BAEEFD5', 'B9EADADE-17F0-45D5-A372-5225587117C8',
    '1585343D-621F-46D9-A4D9-82A0DD687F45', 'C24D3C96-1CEC-4A4F-94CC-244055C7C066',
    '0EA85C1D-B199-41AB-82E5-B4EAF8AA5F08', '7E02D10E-2698-415F-A7A7-B5D07478CB3A',
    '58E7CF45-6A85-4A83-AEF2-2C69E1E79DA2', '1F6B6374-AFC1-4A92-829A-E5206DB5724A',
    '751DA029-64F4-409C-AA81-1FA8B8C554AB', '6C6BE2C9-0284-4E59-A9F0-B607505D5202',
    '858672A0-5530-476F-AB96-D15CE71D68CE', '357E0A2A-7EAA-46E6-8B6B-B43533F4E794',
    '5ECB173F-71B5-41BE-96DD-0F76EE17A52C', '3BFCCE94-9C37-4DB6-8E27-8C904FABC6CF',
    '92F25F57-E32B-4AAB-BB8F-DF51C302A01E', '469655B4-4126-4E4A-A6E4-1E19D3B11A28'
);
PRINT '✓ Backup de AuthorizedAmountAndTerm: ' + CAST(@@ROWCOUNT AS VARCHAR) + ' registros';

PRINT '✓ Backup completado exitosamente';
PRINT '';

-- ============================================================================
-- PASO 2: ACTUALIZACIÓN DE 18 OFERTAS
-- ============================================================================

PRINT '=== PASO 2: ACTUALIZANDO 18 OFERTAS ===';
PRINT '';

-- ============================================================================
-- ESCENARIO 1: Ofertas 1-2
-- Excel: $5,000/12sem (solo 1 oferta) | Tradicional | N1 | Nuevo | SLP
-- ============================================================================

PRINT 'Actualizando Escenario 1 (Ofertas 1-2)...';

-- Oferta 1: 2D676E6C-C0A1-4715-99ED-9BBA0EDA816A (Cliente 3911780)
-- Cambiar a SLP, tipo cliente a Nuevo, tipo seguro a Tradicional
UPDATE dbo.Offer
SET BranchId = @Branch_SLP,
    SalesTypeId = @SaleType_Tradicional,
    LastUpdate = GETDATE()
WHERE Id = '2D676E6C-C0A1-4715-99ED-9BBA0EDA816A';

-- Actualizar tipo de cliente
UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Nuevo
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '2D676E6C-C0A1-4715-99ED-9BBA0EDA816A');

-- Actualizar oferta (5000/12sem)
UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 5000,
    CatPaymentTermId = @Term_12sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '2D676E6C-C0A1-4715-99ED-9BBA0EDA816A';

-- Oferta 2: FAB7A814-ED3E-4EF4-907E-EDD004ACC6C9 (Cliente 3927593)
UPDATE dbo.Offer
SET BranchId = @Branch_SLP,
    SalesTypeId = @SaleType_Tradicional,
    LastUpdate = GETDATE()
WHERE Id = 'FAB7A814-ED3E-4EF4-907E-EDD004ACC6C9';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Nuevo
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = 'FAB7A814-ED3E-4EF4-907E-EDD004ACC6C9');

-- Actualizar oferta (5000/12sem)
UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 5000,
    CatPaymentTermId = @Term_12sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = 'FAB7A814-ED3E-4EF4-907E-EDD004ACC6C9'
  AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '32 sem');

-- ============================================================================
-- ESCENARIO 2: Ofertas 3-4
-- Excel: $4,500/12sem + $10,500/32sem | Tradicional | N1 | Frecuente | SLP
-- ============================================================================

PRINT 'Actualizando Escenario 2 (Ofertas 3-4)...';

-- Oferta 3: 8D619493-D6FA-4383-87A7-A05E6BAEEFD5 (Cliente 3915271)
UPDATE dbo.Offer
SET BranchId = @Branch_SLP,
    SalesTypeId = @SaleType_Tradicional,
    LastUpdate = GETDATE()
WHERE Id = '8D619493-D6FA-4383-87A7-A05E6BAEEFD5';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Frecuente
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '8D619493-D6FA-4383-87A7-A05E6BAEEFD5');

-- Eliminar oferta de 42 sem
DELETE FROM dbo.AuthorizedAmountAndTerm
WHERE OfferId = '8D619493-D6FA-4383-87A7-A05E6BAEEFD5'
  AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '42 sem');

-- Actualizar oferta de 32 sem
UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 10500,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '8D619493-D6FA-4383-87A7-A05E6BAEEFD5'
  AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '32 sem');

-- Insertar nueva oferta de 12 sem
INSERT INTO dbo.AuthorizedAmountAndTerm (Id, OfferId, Amount, CatPaymentTermId, CatPaymentTermTypeId)
VALUES (NEWID(), '8D619493-D6FA-4383-87A7-A05E6BAEEFD5', 4500, @Term_12sem, @PriceLevel_N1);

-- Oferta 4: B9EADADE-17F0-45D5-A372-5225587117C8 (Cliente 3924823)
UPDATE dbo.Offer
SET BranchId = @Branch_SLP,
    SalesTypeId = @SaleType_Tradicional,
    LastUpdate = GETDATE()
WHERE Id = 'B9EADADE-17F0-45D5-A372-5225587117C8';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Frecuente
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = 'B9EADADE-17F0-45D5-A372-5225587117C8');

-- Eliminar oferta de 42 sem
DELETE FROM dbo.AuthorizedAmountAndTerm
WHERE OfferId = 'B9EADADE-17F0-45D5-A372-5225587117C8'
  AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '42 sem');

-- Actualizar oferta de 32 sem
UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 10500,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = 'B9EADADE-17F0-45D5-A372-5225587117C8'
  AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '32 sem');

-- Insertar nueva oferta de 12 sem
INSERT INTO dbo.AuthorizedAmountAndTerm (Id, OfferId, Amount, CatPaymentTermId, CatPaymentTermTypeId)
VALUES (NEWID(), 'B9EADADE-17F0-45D5-A372-5225587117C8', 4500, @Term_12sem, @PriceLevel_N1);

-- ============================================================================
-- ESCENARIO 3: Ofertas 5-6
-- Excel: $3,500/12sem (solo 1 oferta) | Tradicional | N1 | Nuevo | SLP
-- ============================================================================

PRINT 'Actualizando Escenario 3 (Ofertas 5-6)...';

-- Oferta 5: 1585343D-621F-46D9-A4D9-82A0DD687F45 (Cliente 3935222)
UPDATE dbo.Offer
SET BranchId = @Branch_SLP,
    SalesTypeId = @SaleType_Tradicional,
    LastUpdate = GETDATE()
WHERE Id = '1585343D-621F-46D9-A4D9-82A0DD687F45';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Nuevo
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '1585343D-621F-46D9-A4D9-82A0DD687F45');

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 3500,
    CatPaymentTermId = @Term_12sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '1585343D-621F-46D9-A4D9-82A0DD687F45'
  AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '32 sem');

-- Oferta 6: C24D3C96-1CEC-4A4F-94CC-244055C7C066 (Cliente 3942020)
UPDATE dbo.Offer
SET BranchId = @Branch_SLP,
    SalesTypeId = @SaleType_Tradicional,
    LastUpdate = GETDATE()
WHERE Id = 'C24D3C96-1CEC-4A4F-94CC-244055C7C066';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Nuevo
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = 'C24D3C96-1CEC-4A4F-94CC-244055C7C066');

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 3500,
    CatPaymentTermId = @Term_12sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = 'C24D3C96-1CEC-4A4F-94CC-244055C7C066'
  AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '32 sem');

-- ============================================================================
-- ESCENARIO 4: Ofertas 7-8
-- Excel: $10,500/42sem + $5,000/12sem | Integral | N1 | Frecuente | Zacatecas
-- ============================================================================

PRINT 'Actualizando Escenario 4 (Ofertas 7-8)...';

-- Oferta 7: 0EA85C1D-B199-41AB-82E5-B4EAF8AA5F08 (Cliente 3930704)
UPDATE dbo.Offer
SET BranchId = @Branch_Zacatecas,
    SalesTypeId = @SaleType_Integral,
    LastUpdate = GETDATE()
WHERE Id = '0EA85C1D-B199-41AB-82E5-B4EAF8AA5F08';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Frecuente
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '0EA85C1D-B199-41AB-82E5-B4EAF8AA5F08');

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 10500,
    CatPaymentTermId = @Term_42sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '0EA85C1D-B199-41AB-82E5-B4EAF8AA5F08'
  AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '42 sem');

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 5000,
    CatPaymentTermId = @Term_12sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '0EA85C1D-B199-41AB-82E5-B4EAF8AA5F08'
  AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '32 sem');

-- Oferta 8: 7E02D10E-2698-415F-A7A7-B5D07478CB3A (Cliente 3974077)
UPDATE dbo.Offer
SET BranchId = @Branch_Zacatecas,
    SalesTypeId = @SaleType_Integral,
    LastUpdate = GETDATE()
WHERE Id = '7E02D10E-2698-415F-A7A7-B5D07478CB3A';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Frecuente
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '7E02D10E-2698-415F-A7A7-B5D07478CB3A');

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 10500,
    CatPaymentTermId = @Term_42sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '7E02D10E-2698-415F-A7A7-B5D07478CB3A'
  AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '42 sem');

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 5000,
    CatPaymentTermId = @Term_12sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '7E02D10E-2698-415F-A7A7-B5D07478CB3A'
  AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '32 sem');

-- ============================================================================
-- ESCENARIO 5: Ofertas 9-10
-- Excel: $7,500/32sem (solo 1) | Integral | N1 | Nuevo | Aguascalientes
-- ============================================================================

PRINT 'Actualizando Escenario 5 (Ofertas 9-10)...';

-- Oferta 9: 58E7CF45-6A85-4A83-AEF2-2C69E1E79DA2 (Cliente 533178 - cambio N2 a N1)
UPDATE dbo.Offer
SET BranchId = @Branch_Aguascalientes,
    SalesTypeId = @SaleType_Integral,
    LastUpdate = GETDATE()
WHERE Id = '58E7CF45-6A85-4A83-AEF2-2C69E1E79DA2';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Nuevo
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '58E7CF45-6A85-4A83-AEF2-2C69E1E79DA2');

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 7500,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '58E7CF45-6A85-4A83-AEF2-2C69E1E79DA2'
  AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '32 sem');

-- Oferta 10: 1F6B6374-AFC1-4A92-829A-E5206DB5724A (Cliente 3971693 - cambio N2 a N1)
UPDATE dbo.Offer
SET BranchId = @Branch_Aguascalientes,
    SalesTypeId = @SaleType_Integral,
    LastUpdate = GETDATE()
WHERE Id = '1F6B6374-AFC1-4A92-829A-E5206DB5724A';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Nuevo
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '1F6B6374-AFC1-4A92-829A-E5206DB5724A');

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 7500,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '1F6B6374-AFC1-4A92-829A-E5206DB5724A'
  AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '32 sem');

-- ============================================================================
-- ESCENARIO 6: Ofertas 11-12
-- Excel: $5,500/32sem + $7,500/42sem | Integral | N1 | Frecuente | Zacatecas
-- ============================================================================

PRINT 'Actualizando Escenario 6 (Ofertas 11-12)...';

-- Oferta 11: 751DA029-64F4-409C-AA81-1FA8B8C554AB (Cliente 3911266)
UPDATE dbo.Offer
SET BranchId = @Branch_Zacatecas,
    SalesTypeId = @SaleType_Integral,
    LastUpdate = GETDATE()
WHERE Id = '751DA029-64F4-409C-AA81-1FA8B8C554AB';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Frecuente
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '751DA029-64F4-409C-AA81-1FA8B8C554AB');

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 5500,
    CatPaymentTermId = @Term_32sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '751DA029-64F4-409C-AA81-1FA8B8C554AB'
  AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '32 sem');

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 7500,
    CatPaymentTermId = @Term_42sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '751DA029-64F4-409C-AA81-1FA8B8C554AB'
  AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '42 sem');

-- Oferta 12: 6C6BE2C9-0284-4E59-A9F0-B607505D5202 (Cliente 3977635)
UPDATE dbo.Offer
SET BranchId = @Branch_Zacatecas,
    SalesTypeId = @SaleType_Integral,
    LastUpdate = GETDATE()
WHERE Id = '6C6BE2C9-0284-4E59-A9F0-B607505D5202';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Frecuente
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '6C6BE2C9-0284-4E59-A9F0-B607505D5202');

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 5500,
    CatPaymentTermId = @Term_32sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '6C6BE2C9-0284-4E59-A9F0-B607505D5202'
  AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '32 sem');

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 7500,
    CatPaymentTermId = @Term_42sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '6C6BE2C9-0284-4E59-A9F0-B607505D5202'
  AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '42 sem');

-- ============================================================================
-- ESCENARIO 7: Ofertas 13-14
-- Excel: $4,000/12sem (solo 1) | Tradicional | N1 | Nuevo | Aguascalientes
-- ============================================================================

PRINT 'Actualizando Escenario 7 (Ofertas 13-14)...';

-- Oferta 13: 858672A0-5530-476F-AB96-D15CE71D68CE (Cliente 3854562)
UPDATE dbo.Offer
SET BranchId = @Branch_Aguascalientes,
    SalesTypeId = @SaleType_Tradicional,
    LastUpdate = GETDATE()
WHERE Id = '858672A0-5530-476F-AB96-D15CE71D68CE';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Nuevo
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '858672A0-5530-476F-AB96-D15CE71D68CE');

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 4000,
    CatPaymentTermId = @Term_12sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '858672A0-5530-476F-AB96-D15CE71D68CE'
  AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '32 sem');

-- Oferta 14: 357E0A2A-7EAA-46E6-8B6B-B43533F4E794 (Cliente 3941669)
UPDATE dbo.Offer
SET BranchId = @Branch_Aguascalientes,
    SalesTypeId = @SaleType_Tradicional,
    LastUpdate = GETDATE()
WHERE Id = '357E0A2A-7EAA-46E6-8B6B-B43533F4E794';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Nuevo
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '357E0A2A-7EAA-46E6-8B6B-B43533F4E794');

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 4000,
    CatPaymentTermId = @Term_12sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '357E0A2A-7EAA-46E6-8B6B-B43533F4E794'
  AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '32 sem');

-- ============================================================================
-- ESCENARIO 8: Ofertas 15-16
-- Excel: $4,000/12sem + $10,500/32sem | Tradicional | N1 | Frecuente | Aguascalientes
-- ============================================================================

PRINT 'Actualizando Escenario 8 (Ofertas 15-16)...';

-- Oferta 15: 5ECB173F-71B5-41BE-96DD-0F76EE17A52C (Cliente 3966802)
UPDATE dbo.Offer
SET BranchId = @Branch_Aguascalientes,
    SalesTypeId = @SaleType_Tradicional,
    LastUpdate = GETDATE()
WHERE Id = '5ECB173F-71B5-41BE-96DD-0F76EE17A52C';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Frecuente
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '5ECB173F-71B5-41BE-96DD-0F76EE17A52C');

-- Eliminar oferta de 42 sem
DELETE FROM dbo.AuthorizedAmountAndTerm
WHERE OfferId = '5ECB173F-71B5-41BE-96DD-0F76EE17A52C'
  AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '42 sem');

-- Actualizar oferta de 32 sem
UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 10500,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '5ECB173F-71B5-41BE-96DD-0F76EE17A52C'
  AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '32 sem');

-- Insertar nueva oferta de 12 sem
INSERT INTO dbo.AuthorizedAmountAndTerm (Id, OfferId, Amount, CatPaymentTermId, CatPaymentTermTypeId)
VALUES (NEWID(), '5ECB173F-71B5-41BE-96DD-0F76EE17A52C', 4000, @Term_12sem, @PriceLevel_N1);

-- Oferta 16: 3BFCCE94-9C37-4DB6-8E27-8C904FABC6CF (Cliente 3996996)
UPDATE dbo.Offer
SET BranchId = @Branch_Aguascalientes,
    SalesTypeId = @SaleType_Tradicional,
    LastUpdate = GETDATE()
WHERE Id = '3BFCCE94-9C37-4DB6-8E27-8C904FABC6CF';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Frecuente
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '3BFCCE94-9C37-4DB6-8E27-8C904FABC6CF');

-- Eliminar oferta de 42 sem
DELETE FROM dbo.AuthorizedAmountAndTerm
WHERE OfferId = '3BFCCE94-9C37-4DB6-8E27-8C904FABC6CF'
  AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '42 sem');

-- Actualizar oferta de 32 sem
UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 10500,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '3BFCCE94-9C37-4DB6-8E27-8C904FABC6CF'
  AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '32 sem');

-- Insertar nueva oferta de 12 sem
INSERT INTO dbo.AuthorizedAmountAndTerm (Id, OfferId, Amount, CatPaymentTermId, CatPaymentTermTypeId)
VALUES (NEWID(), '3BFCCE94-9C37-4DB6-8E27-8C904FABC6CF', 4000, @Term_12sem, @PriceLevel_N1);

-- ============================================================================
-- ESCENARIO 9: Ofertas 17-18
-- Excel: $4,000/12sem (solo 1) | Tradicional | N1 | Nuevo | Aguascalientes
-- ============================================================================

PRINT 'Actualizando Escenario 9 (Ofertas 17-18)...';

-- Oferta 17: 92F25F57-E32B-4AAB-BB8F-DF51C302A01E (Cliente 3954461)
UPDATE dbo.Offer
SET BranchId = @Branch_Aguascalientes,
    SalesTypeId = @SaleType_Tradicional,
    LastUpdate = GETDATE()
WHERE Id = '92F25F57-E32B-4AAB-BB8F-DF51C302A01E';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Nuevo
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '92F25F57-E32B-4AAB-BB8F-DF51C302A01E');

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 4000,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '92F25F57-E32B-4AAB-BB8F-DF51C302A01E'
  AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '12 sem');

-- Oferta 18: 469655B4-4126-4E4A-A6E4-1E19D3B11A28 (Cliente 3974085)
UPDATE dbo.Offer
SET BranchId = @Branch_Aguascalientes,
    SalesTypeId = @SaleType_Tradicional,
    LastUpdate = GETDATE()
WHERE Id = '469655B4-4126-4E4A-A6E4-1E19D3B11A28';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Nuevo
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '469655B4-4126-4E4A-A6E4-1E19D3B11A28');

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 4000,
    CatPaymentTermId = @Term_12sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '469655B4-4126-4E4A-A6E4-1E19D3B11A28'
  AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '32 sem');

-- ============================================================================
-- PASO 3: VALIDACIÓN DE CAMBIOS
-- ============================================================================

PRINT '';
PRINT '=== PASO 3: VALIDANDO CAMBIOS ===';
PRINT '';

-- Validar las 18 ofertas actualizadas
SELECT 
    O.Id AS OfferId,
    CONVERT(NVARCHAR(20), O.DataSourceRecordId) AS CustomerIdCS,
    C.FullName AS CustomerNameCS,
    ST.Name AS SaleTypeCS,
    CT.Name AS CustomerTypeCS,
    B.Name AS BranchName,
    AAT1.Amount AS AuthorizedAmount1CS,
    PT1.Name AS AuthorizedTerm1CS,
    AAT2.Amount AS AuthorizedAmount2CS,
    PT2.Name AS AuthorizedTerm2CS,
    CPTP.Name AS CatPaymentTermTypeName,
    CPTP.ShouldDisplay AS CatPaymentTermTypeShouldDisplay,
    O.LastUpdate
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
    '2D676E6C-C0A1-4715-99ED-9BBA0EDA816A', 'FAB7A814-ED3E-4EF4-907E-EDD004ACC6C9',
    '8D619493-D6FA-4383-87A7-A05E6BAEEFD5', 'B9EADADE-17F0-45D5-A372-5225587117C8',
    '1585343D-621F-46D9-A4D9-82A0DD687F45', 'C24D3C96-1CEC-4A4F-94CC-244055C7C066',
    '0EA85C1D-B199-41AB-82E5-B4EAF8AA5F08', '7E02D10E-2698-415F-A7A7-B5D07478CB3A',
    '58E7CF45-6A85-4A83-AEF2-2C69E1E79DA2', '1F6B6374-AFC1-4A92-829A-E5206DB5724A',
    '751DA029-64F4-409C-AA81-1FA8B8C554AB', '6C6BE2C9-0284-4E59-A9F0-B607505D5202',
    '858672A0-5530-476F-AB96-D15CE71D68CE', '357E0A2A-7EAA-46E6-8B6B-B43533F4E794',
    '5ECB173F-71B5-41BE-96DD-0F76EE17A52C', '3BFCCE94-9C37-4DB6-8E27-8C904FABC6CF',
    '92F25F57-E32B-4AAB-BB8F-DF51C302A01E', '469655B4-4126-4E4A-A6E4-1E19D3B11A28'
)
ORDER BY O.DataSourceRecordId;

PRINT '';
PRINT '✓ Validación completada. Revisar resultados arriba.';
PRINT '';

-- ============================================================================
-- PASO 4 (OPCIONAL): ROLLBACK - SOLO EJECUTAR SI HAY PROBLEMAS
-- ============================================================================
/*
PRINT '=== ROLLBACK: RESTAURANDO DATOS ORIGINALES ===';

-- Restaurar Offer
UPDATE O
SET O.BranchId = B.BranchId,
    O.SalesTypeId = B.SalesTypeId,
    O.LastUpdate = B.LastUpdate
FROM dbo.Offer O
INNER JOIN #Backup_Offer B ON O.Id = B.Id;
PRINT '✓ Offer restaurado';

-- Restaurar Customer
UPDATE C
SET C.CatCustomerTypeId = B.CatCustomerTypeId
FROM dbo.Customer C
INNER JOIN #Backup_Customer B ON C.Id = B.Id;
PRINT '✓ Customer restaurado';

-- Restaurar AuthorizedAmountAndTerm (eliminar nuevos e insertar originales)
DELETE FROM dbo.AuthorizedAmountAndTerm WHERE OfferId IN (
    SELECT DISTINCT OfferId FROM #Backup_AuthorizedAmountAndTerm
);
INSERT INTO dbo.AuthorizedAmountAndTerm
SELECT * FROM #Backup_AuthorizedAmountAndTerm;
PRINT '✓ AuthorizedAmountAndTerm restaurado';

PRINT '✓ ROLLBACK completado. Datos restaurados a su estado original.';
*/

-- ============================================================================
-- FIN DEL SCRIPT
-- ============================================================================

PRINT '';
PRINT '=== SCRIPT COMPLETADO EXITOSAMENTE ===';
PRINT '✓ Backup creado en tablas temporales (#Backup_*)';
PRINT '✓ 18 ofertas actualizadas según Excel';
PRINT '✓ Validación ejecutada';
PRINT '';
PRINT 'NOTA: Las tablas de backup (#Backup_*) permanecerán disponibles';
PRINT '      durante esta sesión para rollback si es necesario.';
PRINT '';
GO

