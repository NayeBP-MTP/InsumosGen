

-- Sucursales del Excel
DECLARE @Branch_SLP UNIQUEIDENTIFIER = '1D0712B3-DBE1-4872-BB82-0879B123E7EC'; -- San Luis Potosi 2
DECLARE @Branch_Zacatecas UNIQUEIDENTIFIER = '51BCD590-3B05-47D9-8328-93ADE7B47BD1'; -- ZACATECAS
DECLARE @Branch_Aguascalientes UNIQUEIDENTIFIER = '7AE76DAF-08C3-43FB-B3E4-455E64AED01C'; -- AGUASCALIENTES 1

-- Réplica de la lógica de spCustomerSearch (sin paginación, sin full-text search)
SELECT TOP (30)
    O.Id AS OfferId,
    CONVERT(NVARCHAR(20), O.DataSourceRecordId) AS CustomerIdCS,
    ST.Name AS SaleTypeCS,
    CT.Name AS CustomerTypeCS,
    C.FullName AS CustomerNameCS,
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
    OS.Name AS StatusCS,
    S.Name AS SectionCS,
    B.Number AS BranchNumber,
    B.Name AS BranchName,
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
    B.Id IN (@Branch_SLP, @Branch_Zacatecas, @Branch_Aguascalientes)
    AND B.IsActive = 1
    AND O.StatusId = 'A3D0AF16-5924-43A3-841D-7620169C0E99' -- Available
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