USE [AVTs];
GO

/*
================================================================================
QUERY DE VALIDACIÓN POST-UPDATE - 18 OFERTAS
================================================================================
Ejecutar DESPUÉS de aplicar el script 02_UPDATE_18_ofertas.sql
Este query replica la lógica de spCustomerSearch para verificar que los cambios
se reflejan correctamente en el frontend.
================================================================================
*/

-- ============================================================================
-- VALIDACIÓN: Réplica de spCustomerSearch para las 18 ofertas actualizadas
-- ============================================================================

DECLARE 
    @Branch_SLP UNIQUEIDENTIFIER = '1D0712B3-DBE1-4872-BB82-0879B123E7EC',
    @Branch_Zacatecas UNIQUEIDENTIFIER = '51BCD590-3B05-47D9-8328-93ADE7B47BD1',
    @Branch_Aguascalientes UNIQUEIDENTIFIER = '7AE76DAF-08C3-43FB-B3E4-455E64AED01C';

SELECT
    -- Identificadores
    O.Id AS OfferId,
    CONVERT(NVARCHAR(20), O.DataSourceRecordId) AS CustomerIdCS,
    
    -- Datos de la oferta
    ST.Name AS SaleTypeCS,
    CT.Name AS CustomerTypeCS,
    C.FullName AS CustomerNameCS,
    
    -- Montos y plazos autorizados
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
    
    -- Estatus y ubicación
    OS.Name AS StatusCS,
    S.Name AS SectionCS,
    B.Number AS BranchNumber,
    B.Name AS BranchName,
    
    -- Nivel de precio (CRÍTICO para validar Unbundling)
    cptp.id as [CatPaymentTermTypeId],
    cptp.name as [CatPaymentTermTypeName],
    cptp.shouldDisplay as [CatPaymentTermTypeShouldDisplay]
    
FROM Offer O WITH (NOLOCK)
JOIN Branch B WITH (NOLOCK) ON O.BranchId = B.Id
JOIN Customer C WITH (NOLOCK) ON O.CustomerId = C.Id
JOIN CatCustomerType CT WITH (NOLOCK) ON C.CatCustomerTypeId = CT.Id
JOIN CatSaleType ST WITH (NOLOCK) ON O.SalesTypeId = ST.Id
JOIN CatOfferStatus OS WITH (NOLOCK) ON O.StatusId = OS.Id
LEFT JOIN CatReason R WITH (NOLOCK) ON O.StatusReasonId = R.Id
LEFT JOIN CatSection S WITH (NOLOCK) ON O.SectionId = S.Id
LEFT JOIN AuthorizedAmountAndTerm AAT WITH (NOLOCK) ON O.Id = AAT.OfferId
LEFT JOIN CatPaymentTerm PT WITH (NOLOCK) ON PT.Id = AAT.CatPaymentTermId
LEFT JOIN AuthorizedAmountAndTerm AAT2 WITH (NOLOCK) ON O.Id = AAT2.OfferId
LEFT JOIN CatPaymentTerm PT2 WITH (NOLOCK) ON PT2.Id = AAT2.CatPaymentTermId
LEFT JOIN CatPaymentTermType cptp ON cptp.Id = AAT.CatPaymentTermTypeId

WHERE
    O.Id IN (
        '25DCA8C7-560E-4025-AF7C-E56413FA1A48',
        'BC360B4B-D73A-460F-8240-6541C3531863',
        '3F366374-2598-4D77-B4AE-7E9FF10600B1',
        '965756F8-F046-4F36-804A-02491C7BC89F',
        '91BDB477-89AE-455B-AA06-8F9CF3B3A530',
        '771D10AC-677A-4EE4-836F-138AE0471EDF',
        'CC4B8A31-CE6A-40CD-8302-DA3C0658DBE2',
        '4AAB5567-AB50-4249-BCEC-5DF47AD69251',
        'B3EA6615-AF47-435A-B783-AD424CB792E6',
        '19EC9494-008E-4B70-B27F-87C5516157FB',
        '23D24ADA-086D-4587-A335-499BB3E642FB',
        '8385BEAD-EC91-4F5D-BC23-7896751FC341',
        '907B8C9E-9026-47E2-88C4-6A80F107F36E',
        'D08987BA-89B2-430F-99D9-1E3E5C4A3BCD',
        'D2453662-E539-4C26-B980-3DB9A3A45664',
        '802591C9-6455-44ED-938E-EBAC665EA38D',
        '03BECF9D-205C-43D1-A70B-F10EF0610DA0',
        'F845C707-7A22-4E26-AE8E-936390E2664E'
    )
    AND B.IsActive = 1
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
                GROUP BY O2.Id)

ORDER BY O.DataSourceRecordId;

-- ============================================================================
-- VALIDACIÓN ADICIONAL: Conteo por sucursal y nivel de precio
-- ============================================================================

PRINT '';
PRINT '=== RESUMEN DE DISTRIBUCIÓN ===';

SELECT
    B.Name AS Sucursal,
    cptp.Name AS NivelPrecio,
    ST.Name AS TipoSeguro,
    CT.Name AS TipoCliente,
    COUNT(DISTINCT O.Id) AS CantidadOfertas
FROM Offer O
JOIN Branch B ON O.BranchId = B.Id
JOIN Customer C ON O.CustomerId = C.Id
JOIN CatCustomerType CT ON C.CatCustomerTypeId = CT.Id
JOIN CatSaleType ST ON O.SalesTypeId = ST.Id
LEFT JOIN AuthorizedAmountAndTerm AAT ON O.Id = AAT.OfferId
LEFT JOIN CatPaymentTermType cptp ON cptp.Id = AAT.CatPaymentTermTypeId
WHERE O.Id IN (
    '25DCA8C7-560E-4025-AF7C-E56413FA1A48',
    'BC360B4B-D73A-460F-8240-6541C3531863',
    '3F366374-2598-4D77-B4AE-7E9FF10600B1',
    '965756F8-F046-4F36-804A-02491C7BC89F',
    '91BDB477-89AE-455B-AA06-8F9CF3B3A530',
    '771D10AC-677A-4EE4-836F-138AE0471EDF',
    'CC4B8A31-CE6A-40CD-8302-DA3C0658DBE2',
    '4AAB5567-AB50-4249-BCEC-5DF47AD69251',
    'B3EA6615-AF47-435A-B783-AD424CB792E6',
    '19EC9494-008E-4B70-B27F-87C5516157FB',
    '23D24ADA-086D-4587-A335-499BB3E642FB',
    '8385BEAD-EC91-4F5D-BC23-7896751FC341',
    '907B8C9E-9026-47E2-88C4-6A80F107F36E',
    'D08987BA-89B2-430F-99D9-1E3E5C4A3BCD',
    'D2453662-E539-4C26-B980-3DB9A3A45664',
    '802591C9-6455-44ED-938E-EBAC665EA38D',
    '03BECF9D-205C-43D1-A70B-F10EF0610DA0',
    'F845C707-7A22-4E26-AE8E-936390E2664E'
)
GROUP BY B.Name, cptp.Name, ST.Name, CT.Name
ORDER BY B.Name, cptp.Name;

-- ============================================================================
-- CHECKLIST DE VALIDACIÓN
-- ============================================================================

PRINT '';
PRINT '=== CHECKLIST DE VALIDACIÓN ===';
PRINT '1. Todas las ofertas deben tener CatPaymentTermTypeName = ''N1''';
PRINT '2. CatPaymentTermTypeShouldDisplay debe ser = 1';
PRINT '3. Distribución esperada por sucursal:';
PRINT '   - SLP: 6 ofertas';
PRINT '   - Zacatecas: 6 ofertas';
PRINT '   - Aguascalientes: 6 ofertas';
PRINT '4. Distribución esperada por tipo de seguro:';
PRINT '   - Tradicional (Home Credit): 12 ofertas';
PRINT '   - Integral (Negocio): 6 ofertas';
PRINT '5. Distribución esperada por tipo de cliente:';
PRINT '   - Nuevo: 10 ofertas';
PRINT '   - Frecuente: 8 ofertas';
PRINT '';
PRINT 'Si algún valor no coincide, revisar el script de UPDATE y volver a ejecutar.';

GO
