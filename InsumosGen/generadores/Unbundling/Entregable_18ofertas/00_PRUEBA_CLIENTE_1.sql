USE [AVTs];
GO

/*
================================================================================
PRUEBA CON 1 CLIENTE - ANTES DE EJECUTAR LAS 18 OFERTAS
================================================================================
Este script actualiza SOLO LA PRIMERA OFERTA como prueba piloto.
Cliente: 85120 (OfferId: 25DCA8C7-560E-4025-AF7C-E56413FA1A48)

Escenario 1 del Excel:
- Monto/Plazo: $5,000/12sem (solo 1 oferta)
- Tipo de Seguro: Tradicional (Home Credit)
- Nivel: N1
- Tipo Cliente: Nuevo
- Sucursal: San Luis Potosí 2
================================================================================
*/

-- ============================================================================
-- PASO 1: CONSULTAR ESTADO ACTUAL (ANTES DEL CAMBIO)
-- ============================================================================

PRINT '=== PASO 1: ESTADO ACTUAL DE LA OFERTA ===';
PRINT '';

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
    cptp.name as PaymentTermTypeName,
    cptp.shouldDisplay as ShouldDisplay
FROM Offer O
JOIN Branch B ON O.BranchId = B.Id
JOIN Customer C ON O.CustomerId = C.Id
JOIN CatCustomerType CT ON C.CatCustomerTypeId = CT.Id
JOIN CatSaleType ST ON O.SalesTypeId = ST.Id
LEFT JOIN AuthorizedAmountAndTerm AAT ON O.Id = AAT.OfferId
LEFT JOIN CatPaymentTerm PT ON PT.Id = AAT.CatPaymentTermId
LEFT JOIN CatPaymentTermType cptp ON cptp.Id = AAT.CatPaymentTermTypeId
WHERE O.Id = '25DCA8C7-560E-4025-AF7C-E56413FA1A48'
ORDER BY PT.Name DESC;

PRINT '';
PRINT 'Valores actuales esperados:';
PRINT '- CustomerIdCS: 85120';
PRINT '- SaleTypeCS: Negocio (debe cambiar a Home Credit)';
PRINT '- CustomerTypeCS: Frecuente (debe cambiar a Cliente Nuevo)';
PRINT '- BranchName: San Luis Potosi 2 (correcto, no cambia)';
PRINT '- Amount: 10000 y 7500 (deben cambiar a 5000 solamente, eliminar segunda oferta)';
PRINT '- Term: 52 sem y 42 sem (debe cambiar a 12 sem solamente)';
PRINT '- PaymentTermTypeName: Normal (debe cambiar a N1)';
PRINT '- ShouldDisplay: 0 (debe cambiar a 1)';
PRINT '';

-- ============================================================================
-- PASO 2: HACER BACKUP DE ESTE CLIENTE ESPECÍFICO
-- ============================================================================

PRINT '=== PASO 2: BACKUP DEL CLIENTE ===';
PRINT '';

-- Backup de la oferta
IF OBJECT_ID('tempdb..#Offer_Backup_Cliente1') IS NOT NULL DROP TABLE #Offer_Backup_Cliente1;
SELECT * INTO #Offer_Backup_Cliente1 FROM dbo.Offer WHERE Id = '25DCA8C7-560E-4025-AF7C-E56413FA1A48';

-- Backup de AuthorizedAmountAndTerm
IF OBJECT_ID('tempdb..#AAT_Backup_Cliente1') IS NOT NULL DROP TABLE #AAT_Backup_Cliente1;
SELECT * INTO #AAT_Backup_Cliente1 FROM dbo.AuthorizedAmountAndTerm WHERE OfferId = '25DCA8C7-560E-4025-AF7C-E56413FA1A48';

-- Backup del Customer
IF OBJECT_ID('tempdb..#Customer_Backup_Cliente1') IS NOT NULL DROP TABLE #Customer_Backup_Cliente1;
SELECT * INTO #Customer_Backup_Cliente1 
FROM dbo.Customer 
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '25DCA8C7-560E-4025-AF7C-E56413FA1A48');

PRINT 'Backup completado en tablas temporales:';
PRINT '- #Offer_Backup_Cliente1';
PRINT '- #AAT_Backup_Cliente1';
PRINT '- #Customer_Backup_Cliente1';
PRINT '';

-- ============================================================================
-- PASO 3: DECLARAR VARIABLES (IDs de Catálogos)
-- ============================================================================

PRINT '=== PASO 3: DECLARACIÓN DE VARIABLES ===';
PRINT '';

DECLARE 
    -- Sucursales
    @Branch_SLP UNIQUEIDENTIFIER = '1D0712B3-DBE1-4872-BB82-0879B123E7EC',
    
    -- Tipos de Seguro
    @SaleType_Tradicional UNIQUEIDENTIFIER = 'F7049160-F367-438C-A0A8-0B63F6B03EBD', -- Home Credit
    
    -- Tipos de Cliente
    @CustomerType_Nuevo UNIQUEIDENTIFIER = 'D681D8CC-F364-499A-9322-F6AEDBBF24AE',
    
    -- Plazos
    @Term_12sem UNIQUEIDENTIFIER = '81C7FA1C-FFB3-4CF3-AEB7-BDDE1A8A4D6C',
    @Term_32sem UNIQUEIDENTIFIER = '403E89C5-B995-4AA1-8ADA-5B99E0267BB2',
    
    -- Niveles de Precio
    @PriceLevel_N1 UNIQUEIDENTIFIER = 'B771BFC0-D40A-49A7-8372-72F7776A6338';

PRINT 'Variables declaradas correctamente.';
PRINT '';

-- ============================================================================
-- PASO 4: EJECUTAR ACTUALIZACIONES
-- ============================================================================

PRINT '=== PASO 4: EJECUTANDO ACTUALIZACIONES ===';
PRINT '';

-- 4.1: Actualizar tabla Offer (Sucursal y Tipo de Seguro)
PRINT '4.1 - Actualizando tabla Offer...';
UPDATE dbo.Offer
SET BranchId = @Branch_SLP,
    SalesTypeId = @SaleType_Tradicional,
    LastUpdate = GETDATE()
WHERE Id = '25DCA8C7-560E-4025-AF7C-E56413FA1A48';
PRINT '    ✓ Oferta actualizada: Sucursal=SLP, TipoSeguro=Tradicional';
PRINT '';

-- 4.2: Actualizar tipo de cliente
PRINT '4.2 - Actualizando tipo de cliente...';
UPDATE dbo.Customer
SET CatCustomerTypeId = @CustomerType_Nuevo
WHERE Id = (SELECT CustomerId FROM dbo.Offer WHERE Id = '25DCA8C7-560E-4025-AF7C-E56413FA1A48');
PRINT '    ✓ Cliente actualizado: TipoCliente=Nuevo';
PRINT '';

-- 4.3: Eliminar segunda oferta autorizada (solo debe tener 1)
PRINT '4.3 - Eliminando segunda oferta autorizada...';
DELETE FROM dbo.AuthorizedAmountAndTerm
WHERE OfferId = '25DCA8C7-560E-4025-AF7C-E56413FA1A48'
  AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '42 sem');
PRINT '    ✓ Segunda oferta eliminada';
PRINT '';

-- 4.4: Actualizar primera oferta (5000/12sem)
PRINT '4.4 - Actualizando primera oferta autorizada (5000/12sem)...';
UPDATE dbo.AuthorizedAmountAndTerm
SET Amount = 5000,
    CatPaymentTermId = @Term_12sem,
    CatPaymentTermTypeId = @PriceLevel_N1
WHERE OfferId = '25DCA8C7-560E-4025-AF7C-E56413FA1A48'
  AND CatPaymentTermId = (SELECT Id FROM dbo.CatPaymentTerm WHERE Name = '52 sem');
PRINT '    ✓ Primera oferta actualizada: 5000/12sem/N1';
PRINT '';

-- ============================================================================
-- PASO 5: VALIDAR CAMBIOS (DESPUÉS DE LA ACTUALIZACIÓN)
-- ============================================================================

PRINT '=== PASO 5: VALIDACIÓN POST-ACTUALIZACIÓN ===';
PRINT '';

SELECT
    O.Id AS OfferId,
    CONVERT(NVARCHAR(20), O.DataSourceRecordId) AS CustomerIdCS,
    ST.Name AS SaleTypeCS,
    CT.Name AS CustomerTypeCS,
    C.FullName AS CustomerNameCS,
    B.Number AS BranchNumber,
    B.Name AS BranchName,
    CONVERT(NVARCHAR(16), AAT.Amount) AS AuthorizedAmount1CS,
    PT.Name AS AuthorizedTerm1CS,
    CONVERT(NVARCHAR(16),
        (CASE WHEN (SELECT COUNT(AAT.ID) FROM AuthorizedAmountAndTerm AAT
                    WHERE AAT.OfferId = O.Id) = 1 
                THEN NULL
                ELSE AAT2.Amount
        END)) AS AuthorizedAmount2CS,
    (CASE WHEN (SELECT COUNT(AAT.ID) FROM AuthorizedAmountAndTerm AAT
                    WHERE AAT.OfferId = O.Id) = 1 
                THEN NULL
                ELSE PT2.Name
        END) AS AuthorizedTerm2CS,
    cptp.id as CatPaymentTermTypeId,
    cptp.name as CatPaymentTermTypeName,
    cptp.shouldDisplay as CatPaymentTermTypeShouldDisplay
FROM Offer O WITH (NOLOCK)
JOIN Branch B WITH (NOLOCK) ON O.BranchId = B.Id
JOIN Customer C WITH (NOLOCK) ON O.CustomerId = C.Id
JOIN CatCustomerType CT WITH (NOLOCK) ON C.CatCustomerTypeId = CT.Id
JOIN CatSaleType ST WITH (NOLOCK) ON O.SalesTypeId = ST.Id
LEFT JOIN AuthorizedAmountAndTerm AAT WITH (NOLOCK) ON O.Id = AAT.OfferId
LEFT JOIN CatPaymentTerm PT WITH (NOLOCK) ON PT.Id = AAT.CatPaymentTermId
LEFT JOIN AuthorizedAmountAndTerm AAT2 WITH (NOLOCK) ON O.Id = AAT2.OfferId
LEFT JOIN CatPaymentTerm PT2 WITH (NOLOCK) ON PT2.Id = AAT2.CatPaymentTermId
LEFT JOIN CatPaymentTermType cptp ON cptp.Id = AAT.CatPaymentTermTypeId
WHERE O.Id = '25DCA8C7-560E-4025-AF7C-E56413FA1A48'
  AND PT.Name = (SELECT MAX(PT.Name) 
                FROM Offer O2
                JOIN AuthorizedAmountAndTerm AAT ON O2.Id = AAT.OfferId
                JOIN CatPaymentTerm PT ON PT.Id = AAT.CatPaymentTermId
                WHERE O2.Id = O.Id
                GROUP BY O2.Id)
  AND PT2.Name = (SELECT MIN(PT.Name) 
                FROM Offer O2
                JOIN AuthorizedAmountAndTerm AAT ON O2.Id = AAT.OfferId
                JOIN CatPaymentTerm PT ON PT.Id = AAT.CatPaymentTermId
                WHERE O2.Id = O.Id
                GROUP BY O2.Id);

PRINT '';
PRINT '=== CHECKLIST DE VALIDACIÓN ===';
PRINT '';
PRINT 'Verificar que los valores sean:';
PRINT '✓ CustomerIdCS: 85120';
PRINT '✓ SaleTypeCS: Home Credit';
PRINT '✓ CustomerTypeCS: Cliente Nuevo';
PRINT '✓ BranchName: San Luis Potosi 2';
PRINT '✓ AuthorizedAmount1CS: 5000';
PRINT '✓ AuthorizedTerm1CS: 12 sem';
PRINT '✓ AuthorizedAmount2CS: NULL (solo 1 oferta)';
PRINT '✓ AuthorizedTerm2CS: NULL';
PRINT '✓ CatPaymentTermTypeName: N1';
PRINT '✓ CatPaymentTermTypeShouldDisplay: 1';
PRINT '';

-- ============================================================================
-- PASO 6: ROLLBACK (SOLO SI ALGO SALIÓ MAL)
-- ============================================================================

PRINT '=== PASO 6: ROLLBACK (EJECUTAR SOLO SI ALGO SALIÓ MAL) ===';
PRINT '';
PRINT 'Si necesitas revertir los cambios, ejecuta el siguiente bloque:';
PRINT '';
PRINT '/*';
PRINT '-- Restaurar Offer';
PRINT 'UPDATE O';
PRINT 'SET O.BranchId = B.BranchId,';
PRINT '    O.SalesTypeId = B.SalesTypeId,';
PRINT '    O.LastUpdate = B.LastUpdate';
PRINT 'FROM dbo.Offer O';
PRINT 'JOIN #Offer_Backup_Cliente1 B ON O.Id = B.Id;';
PRINT '';
PRINT '-- Restaurar Customer';
PRINT 'UPDATE C';
PRINT 'SET C.CatCustomerTypeId = BC.CatCustomerTypeId';
PRINT 'FROM dbo.Customer C';
PRINT 'JOIN #Customer_Backup_Cliente1 BC ON C.Id = BC.Id;';
PRINT '';
PRINT '-- Restaurar AuthorizedAmountAndTerm';
PRINT 'DELETE FROM dbo.AuthorizedAmountAndTerm';
PRINT 'WHERE OfferId = ''25DCA8C7-560E-4025-AF7C-E56413FA1A48'';';
PRINT '';
PRINT 'INSERT INTO dbo.AuthorizedAmountAndTerm';
PRINT 'SELECT * FROM #AAT_Backup_Cliente1;';
PRINT '*/';
PRINT '';

-- ============================================================================
-- RESUMEN FINAL
-- ============================================================================

PRINT '=== RESUMEN FINAL ===';
PRINT '';
PRINT 'Si la validación es correcta:';
PRINT '1. ✓ La oferta del cliente 85120 está actualizada correctamente';
PRINT '2. ✓ El frontend mostrará la etiqueta N1 visible';
PRINT '3. ✓ El monto es $5,000 en 12 semanas (solo 1 oferta)';
PRINT '4. ✓ La segunda oferta fue eliminada correctamente';
PRINT '';
PRINT 'Siguiente paso:';
PRINT '→ Ejecutar el script completo 02_UPDATE_18_ofertas.sql para las 18 ofertas';
PRINT '';

GO
