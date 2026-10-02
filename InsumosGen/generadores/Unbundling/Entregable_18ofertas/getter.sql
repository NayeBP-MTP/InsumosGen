USE [AVTs]
GO
/****** Object:  StoredProcedure [dbo].[spCustomerSearch]    Script Date: 11/02/2026 07:00:45 p. m. ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
-- =============================================
-- Author:		VWL
-- Create date: 04/06/2020
-- Description:	Obtiene la lista de clientes junto con sus ofertas
-- =============================================
ALTER PROCEDURE [dbo].[spCustomerSearch]
	@SearchTerm NVARCHAR(100),
	@BranchId UNIQUEIDENTIFIER,
	@PageNumber INT = 1,
	@PageSize   INT = 10,
	@OrderBy NVARCHAR(50) = 'customerIdCS',
	@Direction NVARCHAR(4) = 'asc'
AS
BEGIN
	SET NOCOUNT ON;
 
	DECLARE
		@OfferStatus_Available UNIQUEIDENTIFIER = 'A3D0AF16-5924-43A3-841D-7620169C0E99',
		@OfferStatus_Cancelled UNIQUEIDENTIFIER = '039609E2-7A01-4711-B4A3-809316621E20',
		@OfferStatus_Rejected UNIQUEIDENTIFIER = '50FE8F59-75D3-4478-8B05-2D8E06A16FCF',
		@SearchTerm_Prefix NVARCHAR(105) = '"' + @SearchTerm + '*"',
		@SearchTerm_empty1 INT,
		@SearchTerm_empty2 INT;
 
	IF @SearchTerm = ''
	BEGIN
        SET @SearchTerm_empty1 = 1
        SET @SearchTerm_empty2 = 1
	END
	ELSE IF @SearchTerm <> ''
	BEGIN
		SET @SearchTerm_empty1 = 1
		SET @SearchTerm_empty2 = 2
	END
    SELECT
		O.Id,
		CONVERT(NVARCHAR(20), O.DataSourceRecordId) AS CustomerIdCS,
		ST.Name AS SaleTypeCS,
		CT.Name AS CustomerTypeCS,
		C.FullName AS CustomerNameCS,   
		CONVERT(NVARCHAR(16), AAT.Amount) AS AuthorizedAmount1CS,
		PT.Name AS AuthorizedTerm1CS,
		CONVERT(NVARCHAR(16),
		(CASE WHEN (SELECT COUNT(AAT.ID) FROM AuthorizedAmountAndTerm AAT
							WHERE AAT.OfferId = O.Id) = 1 
						THEN 
							NULL
						ELSE
							AAT2.Amount
				END)) AS AuthorizedAmount2CS,
		(CASE WHEN (SELECT COUNT(AAT.ID) FROM AuthorizedAmountAndTerm AAT
							WHERE AAT.OfferId = O.Id) = 1 
						THEN 
							NULL
						ELSE
							PT2.Name
				END) AS AuthorizedTerm2CS,
		OS.Name AS StatusCS,
		S.Name AS SectionCS,
		O.LastUser,
		O.LastUserId,
		CONVERT(NVARCHAR(36), O.WorkSourceId) AS WorkSourceId,
		CONVERT(NVARCHAR(36), O.StatusId) AS StatusId,
		R.Name AS StatusReason,
		cptp.id as [CatPaymentTermTypeId],
		cptp.name as [CatPaymentTermTypeName],
		cptp.shouldDisplay as [CatPaymentTermTypeShouldDisplay],
		COUNT(*) OVER() AS TotalItemCount
	FROM Offer O WITH (NOLOCK)
	JOIN Branch B WITH (NOLOCK)
		ON O.BranchId = B.Id
	JOIN Customer C WITH (NOLOCK)
		ON O.CustomerId = C.Id
	JOIN CatCustomerType CT WITH (NOLOCK)
		ON C.CatCustomerTypeId = CT.Id
	JOIN CatSaleType ST WITH (NOLOCK)
		ON O.SalesTypeId = ST.Id
	JOIN CatOfferStatus OS WITH (NOLOCK)
		ON O.StatusId = OS.Id
	LEFT JOIN CatReason R WITH (NOLOCK)
		ON O.StatusReasonId = R.Id
	LEFT JOIN CatSection S WITH (NOLOCK)
		ON O.SectionId = S.Id
	LEFT JOIN AuthorizedAmountAndTerm AAT WITH (NOLOCK)
			ON O.Id = AAT.OfferId
	LEFT JOIN CatPaymentTerm PT WITH (NOLOCK)
			ON PT.Id = AAT.CatPaymentTermId
	LEFT JOIN AuthorizedAmountAndTerm AAT2 WITH (NOLOCK)
			ON O.Id = AAT2.OfferId
	LEFT JOIN CatPaymentTerm PT2 WITH (NOLOCK)
			ON PT2.Id = AAT2.CatPaymentTermId
	JOIN CatPaymentTermType cptp on cptp.Id=AAT.CatPaymentTermTypeId --UPDATE Table show paymenttermtype (n1,n2,n3)
	WHERE
		B.Id = @BranchId AND
		B.IsActive = 1 AND
		PT.Name = (SELECT MAX(PT.Name) 
					FROM Offer O2
					JOIN AuthorizedAmountAndTerm AAT
							ON O2.Id = AAT.OfferId
					JOIN CatPaymentTerm PT
							ON PT.Id = AAT.CatPaymentTermId
					WHERE O2.Id = O.Id
					GROUP BY O2.Id
					) AND
		PT2.Name = (SELECT MIN(PT.Name) 
					FROM Offer O2
					JOIN AuthorizedAmountAndTerm AAT
							ON O2.Id = AAT.OfferId
					JOIN CatPaymentTerm PT
							ON PT.Id = AAT.CatPaymentTermId
					WHERE O2.Id = O.Id
					GROUP BY O2.Id
					) AND
		(
			O.StatusId = @OfferStatus_Available OR
			O.StatusId = @OfferStatus_Cancelled AND (O.LastUpdate BETWEEN DATEADD(MONTH, -1, GETDATE()) AND GETDATE()) OR
			O.StatusId = @OfferStatus_Rejected AND (O.LastUpdate BETWEEN DATEADD(MONTH, -1, GETDATE()) AND GETDATE())
		) AND
		(
			(CONTAINS(O.DataSourceRecordId_Search, @SearchTerm_Prefix) OR (@SearchTerm_empty1 = @SearchTerm_empty2)) OR
			(CONTAINS(ST.Name, @SearchTerm_Prefix) OR (@SearchTerm_empty1 = @SearchTerm_empty2)) OR
			(CONTAINS(CT.Name, @SearchTerm_Prefix) OR (@SearchTerm_empty1 = @SearchTerm_empty2)) OR
			(CONTAINS(C.FullName, @SearchTerm_Prefix) OR (@SearchTerm_empty1 = @SearchTerm_empty2)) OR
			(CONTAINS(OS.Name, @SearchTerm_Prefix) OR (@SearchTerm_empty1 = @SearchTerm_empty2))
		)
	ORDER BY 
		CASE WHEN @Direction = 'asc' THEN
			CASE @OrderBy
				WHEN 'customerIdCS' THEN CONVERT(NVARCHAR(20), O.DataSourceRecordId)
				WHEN 'saleTypeCS' THEN ST.Name
				WHEN 'customerTypeCS' THEN CT.Name
				WHEN 'customerNameCS' THEN C.FullName
				WHEN 'authorizedAmount1CS' THEN CONVERT(NVARCHAR(16), AAT.Amount)
				WHEN 'authorizedTerm1CS' THEN PT.Name
				WHEN 'authorizedAmount2CS' THEN CONVERT(NVARCHAR(16), AAT2.Amount)
				WHEN 'authorizedTerm2CS' THEN PT2.Name
				WHEN 'sectionCS' THEN S.Name
				WHEN 'statusCS' THEN OS.Name
			END
		END ASC,
		CASE WHEN @Direction = 'desc' THEN
			CASE @OrderBy
				WHEN 'customerIdCS' THEN CONVERT(NVARCHAR(20), O.DataSourceRecordId)
				WHEN 'saleTypeCS' THEN ST.Name
				WHEN 'customerTypeCS' THEN CT.Name
				WHEN 'customerNameCS' THEN C.FullName
				WHEN 'authorizedAmount1CS' THEN CONVERT(NVARCHAR(16), AAT.Amount)
				WHEN 'authorizedTerm1CS' THEN PT.Name
				WHEN 'authorizedAmount2CS' THEN CONVERT(NVARCHAR(16), AAT2.Amount)
				WHEN 'authorizedTerm2CS' THEN PT2.Name
				WHEN 'sectionCS' THEN S.Name
				WHEN 'statusCS' THEN OS.Name
			END
		END DESC
	OFFSET @PageSize * (@PageNumber - 1) ROWS
    FETCH NEXT @PageSize ROWS ONLY OPTION (RECOMPILE);
END