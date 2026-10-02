USE [AVTs]
GO
ALTER TABLE CatPaymentTermType
ADD ShouldDisplay BIT NOT NULL
    CONSTRAINT DF_CatPaymentTermType_ShouldDisplay DEFAULT (0);
GO
INSERT [dbo].[CatPaymentTermType] ([Id], [Name], [Description], [ShouldDisplay]) VALUES (NEWID(), N'N1', N'Nivel de precio 1', 1)
GO
INSERT [dbo].[CatPaymentTermType] ([Id], [Name], [Description], [ShouldDisplay]) VALUES (NEWID(), N'N2', N'Nivel de precio 2', 1)
GO
INSERT [dbo].[CatPaymentTermType] ([Id], [Name], [Description], [ShouldDisplay]) VALUES (NEWID(), N'N3', N'Nivel de precio 3', 1)
GO
