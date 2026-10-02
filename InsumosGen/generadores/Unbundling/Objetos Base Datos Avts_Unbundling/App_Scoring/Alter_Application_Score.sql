USE Application_Score
ALTER TABLE [dbo].[TCis]
ADD DecMessageText nvarchar(MAX) NULL
go
ALTER TABLE [dbo].[TEMPValidatedProspects]
ADD [Unbundling] nvarchar(MAX) NULL
