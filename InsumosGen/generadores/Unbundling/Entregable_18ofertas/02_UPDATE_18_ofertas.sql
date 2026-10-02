USE [AVTs];
GO

/*
================================================================================
SCRIPT DE ACTUALIZACIÓN - 18 OFERTAS SEGÚN EXCEL
================================================================================
Proyecto: Unbundling - Ajuste de ofertas para pruebas
Fecha: 16 Feb 2026
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
-- ESCENARIO 1: Ofertas 1-2
-- Excel: $5,000/12sem (solo 1 oferta) | Tradicional | N1 | Nuevo | SLP
-- ============================================================================

PRINT 'Actualizando Escenario 1 (Ofertas 1-2)...';

-- Oferta 1: 25DCA8C7-560E-4025-AF7C-E56413FA1A48
-- Cambiar sucursal a SLP, tipo cliente a Nuevo, tipo seguro a Tradicional
UPDATE dbo.Offer
SET BranchId = @Branch_SLP,
    SalesTypeId = @SaleType_Tradicional,
    LastUpdate = GETDATE()
WHERE Id = '25DCA8C7-560E-4025-AF7C-E56413FA1A48';

-- Actualizar tipo de cliente
UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Nuevo
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '25DCA8C7-560E-4025-AF7C-E56413FA1A48');

-- Eliminar segunda oferta autorizada (solo debe tener 1)
DELETE FROM dbo.AuthorizedAmountAndTerm
WHERE OfferId = '25DCA8C7-560E-4025-AF7C-E56413FA1A48'
  AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '42 sem');

-- Actualizar primera oferta (5000/12sem)
UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 5000,
    CatPaymentTermId = @Term_12sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '25DCA8C7-560E-4025-AF7C-E56413FA1A48'
  AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '52 sem');

-- Oferta 2: BC360B4B-D73A-460F-8240-6541C3531863 (ya está en SLP)
UPDATE dbo.Offer
SET SalesTypeId = @SaleType_Tradicional,
    LastUpdate = GETDATE()
WHERE Id = 'BC360B4B-D73A-460F-8240-6541C3531863';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Nuevo
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = 'BC360B4B-D73A-460F-8240-6541C3531863');

-- Eliminar segunda oferta autorizada
DELETE FROM dbo.AuthorizedAmountAndTerm
WHERE OfferId = 'BC360B4B-D73A-460F-8240-6541C3531863'
  AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '32 sem');

-- Actualizar primera oferta (5000/12sem)
UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 5000,
    CatPaymentTermId = @Term_12sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = 'BC360B4B-D73A-460F-8240-6541C3531863'
  AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '42 sem');

-- ============================================================================
-- ESCENARIO 2: Ofertas 3-4
-- Excel: $4,500/12sem + $10,500/32sem | Tradicional | N1 | Frecuente | SLP
-- ============================================================================

PRINT 'Actualizando Escenario 2 (Ofertas 3-4)...';

-- Oferta 3: 3F366374-2598-4D77-B4AE-7E9FF10600B1 (cambiar de Zacatecas a SLP)
UPDATE dbo.Offer
SET BranchId = @Branch_SLP,
    SalesTypeId = @SaleType_Tradicional,
    LastUpdate = GETDATE()
WHERE Id = '3F366374-2598-4D77-B4AE-7E9FF10600B1';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Frecuente
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '3F366374-2598-4D77-B4AE-7E9FF10600B1');

-- Esta oferta solo tiene 1 AuthorizedAmountAndTerm, necesitamos agregar otra
-- Primero actualizamos la existente
UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 4500,
    CatPaymentTermId = @Term_12sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '3F366374-2598-4D77-B4AE-7E9FF10600B1';

-- Insertamos la segunda oferta
INSERT INTO dbo.AuthorizedAmountAndTerm (Id, OfferId, Amount, CatPaymentTermId, CatPaymentTermTypeId)
VALUES (NEWID(), '3F366374-2598-4D77-B4AE-7E9FF10600B1', 10500, @Term_32sem, @PriceLevel_N1);

-- Oferta 4: 965756F8-F046-4F36-804A-02491C7BC89F (ya está en SLP)
UPDATE dbo.Offer
SET SalesTypeId = @SaleType_Tradicional,
    LastUpdate = GETDATE()
WHERE Id = '965756F8-F046-4F36-804A-02491C7BC89F';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Frecuente
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '965756F8-F046-4F36-804A-02491C7BC89F');

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 4500,
    CatPaymentTermId = @Term_12sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '965756F8-F046-4F36-804A-02491C7BC89F';

INSERT INTO dbo.AuthorizedAmountAndTerm (Id, OfferId, Amount, CatPaymentTermId, CatPaymentTermTypeId)
VALUES (NEWID(), '965756F8-F046-4F36-804A-02491C7BC89F', 10500, @Term_32sem, @PriceLevel_N1);

-- ============================================================================
-- ESCENARIO 3: Ofertas 5-6
-- Excel: $3,500/12sem (solo 1 oferta) | Tradicional | N1 | Nuevo | SLP
-- ============================================================================

PRINT 'Actualizando Escenario 3 (Ofertas 5-6)...';

-- Oferta 5: 91BDB477-89AE-455B-AA06-8F9CF3B3A530 (cambiar de Aguascalientes a SLP)
UPDATE dbo.Offer
SET BranchId = @Branch_SLP,
    SalesTypeId = @SaleType_Tradicional,
    LastUpdate = GETDATE()
WHERE Id = '91BDB477-89AE-455B-AA06-8F9CF3B3A530';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Nuevo
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '91BDB477-89AE-455B-AA06-8F9CF3B3A530');

-- Eliminar la segunda oferta y ajustar la primera
DELETE FROM dbo.AuthorizedAmountAndTerm
WHERE OfferId = '91BDB477-89AE-455B-AA06-8F9CF3B3A530'
  AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '42 sem');

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 3500,
    CatPaymentTermId = @Term_12sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '91BDB477-89AE-455B-AA06-8F9CF3B3A530';

-- Oferta 6: 771D10AC-677A-4EE4-836F-138AE0471EDF (ya está en SLP)
UPDATE dbo.Offer
SET SalesTypeId = @SaleType_Tradicional,
    LastUpdate = GETDATE()
WHERE Id = '771D10AC-677A-4EE4-836F-138AE0471EDF';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Nuevo
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '771D10AC-677A-4EE4-836F-138AE0471EDF');

DELETE FROM dbo.AuthorizedAmountAndTerm
WHERE OfferId = '771D10AC-677A-4EE4-836F-138AE0471EDF'
  AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '32 sem');

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 3500,
    CatPaymentTermId = @Term_12sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '771D10AC-677A-4EE4-836F-138AE0471EDF';

-- ============================================================================
-- ESCENARIO 4: Ofertas 7-8
-- Excel: $10,500/42sem + $5,000/12sem | Integral | N1 | Frecuente | Zacatecas
-- ============================================================================

PRINT 'Actualizando Escenario 4 (Ofertas 7-8)...';

-- Oferta 7: CC4B8A31-CE6A-40CD-8302-DA3C0658DBE2 (cambiar de SLP a Zacatecas)
UPDATE dbo.Offer
SET BranchId = @Branch_Zacatecas,
    SalesTypeId = @SaleType_Integral,
    LastUpdate = GETDATE()
WHERE Id = 'CC4B8A31-CE6A-40CD-8302-DA3C0658DBE2';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Frecuente
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = 'CC4B8A31-CE6A-40CD-8302-DA3C0658DBE2');

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 10500,
    CatPaymentTermId = @Term_42sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = 'CC4B8A31-CE6A-40CD-8302-DA3C0658DBE2'
  AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '42 sem');

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 5000,
    CatPaymentTermId = @Term_12sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = 'CC4B8A31-CE6A-40CD-8302-DA3C0658DBE2'
  AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '32 sem');

-- Oferta 8: 4AAB5567-AB50-4249-BCEC-5DF47AD69251 (cambiar de Aguascalientes a Zacatecas)
UPDATE dbo.Offer
SET BranchId = @Branch_Zacatecas,
    SalesTypeId = @SaleType_Integral,
    LastUpdate = GETDATE()
WHERE Id = '4AAB5567-AB50-4249-BCEC-5DF47AD69251';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Frecuente
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '4AAB5567-AB50-4249-BCEC-5DF47AD69251');

-- Esta oferta solo tiene 1, necesitamos agregar otra
UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 10500,
    CatPaymentTermId = @Term_42sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '4AAB5567-AB50-4249-BCEC-5DF47AD69251';

INSERT INTO dbo.AuthorizedAmountAndTerm (Id, OfferId, Amount, CatPaymentTermId, CatPaymentTermTypeId)
VALUES (NEWID(), '4AAB5567-AB50-4249-BCEC-5DF47AD69251', 5000, @Term_12sem, @PriceLevel_N1);

-- ============================================================================
-- ESCENARIO 5: Ofertas 9-10
-- Excel: $7,500/32sem (solo 1) | Integral | N1 | Nuevo | Aguascalientes
-- ============================================================================

PRINT 'Actualizando Escenario 5 (Ofertas 9-10)...';

-- Oferta 9: B3EA6615-AF47-435A-B783-AD424CB792E6 (cambiar de SLP a Aguascalientes)
UPDATE dbo.Offer
SET BranchId = @Branch_Aguascalientes,
    SalesTypeId = @SaleType_Integral,
    LastUpdate = GETDATE()
WHERE Id = 'B3EA6615-AF47-435A-B783-AD424CB792E6';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Nuevo
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = 'B3EA6615-AF47-435A-B783-AD424CB792E6');

DELETE FROM dbo.AuthorizedAmountAndTerm
WHERE OfferId = 'B3EA6615-AF47-435A-B783-AD424CB792E6'
  AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '42 sem');

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 7500,
    CatPaymentTermId = @Term_32sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = 'B3EA6615-AF47-435A-B783-AD424CB792E6';

-- Oferta 10: 19EC9494-008E-4B70-B27F-87C5516157FB (cambiar de SLP a Aguascalientes)
UPDATE dbo.Offer
SET BranchId = @Branch_Aguascalientes,
    SalesTypeId = @SaleType_Integral,
    LastUpdate = GETDATE()
WHERE Id = '19EC9494-008E-4B70-B27F-87C5516157FB';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Nuevo
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '19EC9494-008E-4B70-B27F-87C5516157FB');

DELETE FROM dbo.AuthorizedAmountAndTerm
WHERE OfferId = '19EC9494-008E-4B70-B27F-87C5516157FB'
  AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '42 sem');

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 7500,
    CatPaymentTermId = @Term_32sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '19EC9494-008E-4B70-B27F-87C5516157FB';

-- ============================================================================
-- ESCENARIO 6: Ofertas 11-12
-- Excel: $5,500/32sem + $7,500/42sem | Integral | N1 | Frecuente | Zacatecas
-- ============================================================================

PRINT 'Actualizando Escenario 6 (Ofertas 11-12)...';

-- Oferta 11: 23D24ADA-086D-4587-A335-499BB3E642FB (cambiar de Aguascalientes a Zacatecas)
UPDATE dbo.Offer
SET BranchId = @Branch_Zacatecas,
    SalesTypeId = @SaleType_Integral,
    LastUpdate = GETDATE()
WHERE Id = '23D24ADA-086D-4587-A335-499BB3E642FB';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Frecuente
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '23D24ADA-086D-4587-A335-499BB3E642FB');

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 5500,
    CatPaymentTermId = @Term_32sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '23D24ADA-086D-4587-A335-499BB3E642FB'
  AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '32 sem');

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 7500,
    CatPaymentTermId = @Term_42sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '23D24ADA-086D-4587-A335-499BB3E642FB'
  AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '42 sem');

-- Oferta 12: 8385BEAD-EC91-4F5D-BC23-7896751FC341 (cambiar de SLP a Zacatecas)
UPDATE dbo.Offer
SET BranchId = @Branch_Zacatecas,
    SalesTypeId = @SaleType_Integral,
    LastUpdate = GETDATE()
WHERE Id = '8385BEAD-EC91-4F5D-BC23-7896751FC341';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Frecuente
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '8385BEAD-EC91-4F5D-BC23-7896751FC341');

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 5500,
    CatPaymentTermId = @Term_32sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '8385BEAD-EC91-4F5D-BC23-7896751FC341'
  AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '32 sem');

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 7500,
    CatPaymentTermId = @Term_42sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '8385BEAD-EC91-4F5D-BC23-7896751FC341'
  AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '42 sem');

-- ============================================================================
-- ESCENARIO 7: Ofertas 13-14
-- Excel: $4,000/12sem (solo 1) | Tradicional | N1 | Nuevo | Aguascalientes
-- ============================================================================

PRINT 'Actualizando Escenario 7 (Ofertas 13-14)...';

-- Oferta 13: 907B8C9E-9026-47E2-88C4-6A80F107F36E (ya está en Aguascalientes)
UPDATE dbo.Offer
SET SalesTypeId = @SaleType_Tradicional,
    LastUpdate = GETDATE()
WHERE Id = '907B8C9E-9026-47E2-88C4-6A80F107F36E';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Nuevo
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '907B8C9E-9026-47E2-88C4-6A80F107F36E');

DELETE FROM dbo.AuthorizedAmountAndTerm
WHERE OfferId = '907B8C9E-9026-47E2-88C4-6A80F107F36E'
  AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '32 sem');

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 4000,
    CatPaymentTermId = @Term_12sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '907B8C9E-9026-47E2-88C4-6A80F107F36E';

-- Oferta 14: D08987BA-89B2-430F-99D9-1E3E5C4A3BCD (cambiar de SLP a Aguascalientes)
UPDATE dbo.Offer
SET BranchId = @Branch_Aguascalientes,
    SalesTypeId = @SaleType_Tradicional,
    LastUpdate = GETDATE()
WHERE Id = 'D08987BA-89B2-430F-99D9-1E3E5C4A3BCD';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Nuevo
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = 'D08987BA-89B2-430F-99D9-1E3E5C4A3BCD');

DELETE FROM dbo.AuthorizedAmountAndTerm
WHERE OfferId = 'D08987BA-89B2-430F-99D9-1E3E5C4A3BCD'
  AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '32 sem');

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 4000,
    CatPaymentTermId = @Term_12sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = 'D08987BA-89B2-430F-99D9-1E3E5C4A3BCD';

-- ============================================================================
-- ESCENARIO 8: Ofertas 15-16
-- Excel: $4,000/12sem + $10,500/32sem | Tradicional | N1 | Frecuente | Aguascalientes
-- ============================================================================

PRINT 'Actualizando Escenario 8 (Ofertas 15-16)...';

-- Oferta 15: D2453662-E539-4C26-B980-3DB9A3A45664 (cambiar de SLP a Aguascalientes)
UPDATE dbo.Offer
SET BranchId = @Branch_Aguascalientes,
    SalesTypeId = @SaleType_Tradicional,
    LastUpdate = GETDATE()
WHERE Id = 'D2453662-E539-4C26-B980-3DB9A3A45664';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Frecuente
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = 'D2453662-E539-4C26-B980-3DB9A3A45664');

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 4000,
    CatPaymentTermId = @Term_12sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = 'D2453662-E539-4C26-B980-3DB9A3A45664'
  AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '52 sem');

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 10500,
    CatPaymentTermId = @Term_32sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = 'D2453662-E539-4C26-B980-3DB9A3A45664'
  AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '42 sem');

-- Oferta 16: 802591C9-6455-44ED-938E-EBAC665EA38D (ya está en Aguascalientes)
UPDATE dbo.Offer
SET SalesTypeId = @SaleType_Tradicional,
    LastUpdate = GETDATE()
WHERE Id = '802591C9-6455-44ED-938E-EBAC665EA38D';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Frecuente
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '802591C9-6455-44ED-938E-EBAC665EA38D');

-- Esta oferta solo tiene 1, necesitamos agregar otra
UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 4000,
    CatPaymentTermId = @Term_12sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '802591C9-6455-44ED-938E-EBAC665EA38D';

INSERT INTO dbo.AuthorizedAmountAndTerm (Id, OfferId, Amount, CatPaymentTermId, CatPaymentTermTypeId)
VALUES (NEWID(), '802591C9-6455-44ED-938E-EBAC665EA38D', 10500, @Term_32sem, @PriceLevel_N1);

-- ============================================================================
-- ESCENARIO 9: Ofertas 17-18
-- Excel: $4,000/12sem (solo 1) | Tradicional | N1 | Nuevo | Aguascalientes
-- ============================================================================

PRINT 'Actualizando Escenario 9 (Ofertas 17-18)...';

-- Oferta 17: 03BECF9D-205C-43D1-A70B-F10EF0610DA0 (cambiar de SLP a Aguascalientes)
UPDATE dbo.Offer
SET BranchId = @Branch_Aguascalientes,
    SalesTypeId = @SaleType_Tradicional,
    LastUpdate = GETDATE()
WHERE Id = '03BECF9D-205C-43D1-A70B-F10EF0610DA0';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Nuevo
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '03BECF9D-205C-43D1-A70B-F10EF0610DA0');

DELETE FROM dbo.AuthorizedAmountAndTerm
WHERE OfferId = '03BECF9D-205C-43D1-A70B-F10EF0610DA0'
  AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '42 sem');

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 4000,
    CatPaymentTermId = @Term_12sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '03BECF9D-205C-43D1-A70B-F10EF0610DA0';

-- Oferta 18: F845C707-7A22-4E26-AE8E-936390E2664E (ya está en Aguascalientes)
UPDATE dbo.Offer
SET SalesTypeId = @SaleType_Tradicional,
    LastUpdate = GETDATE()
WHERE Id = 'F845C707-7A22-4E26-AE8E-936390E2664E';

UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Nuevo
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = 'F845C707-7A22-4E26-AE8E-936390E2664E');

UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 4000,
    CatPaymentTermId = @Term_12sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = 'F845C707-7A22-4E26-AE8E-936390E2664E';

-- ============================================================================
-- FIN DEL SCRIPT
-- ============================================================================

PRINT 'Actualización completada. Ejecutar query de validación (03_validacion.sql)';
GO
