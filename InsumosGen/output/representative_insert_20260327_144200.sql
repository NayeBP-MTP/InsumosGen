-- ============================================================
-- Representative Creation Script
-- Generated: 2026-03-27 14:42:00
-- Branch: Izcalli (2075)
-- Agency: 2075000000335
-- Quantity: 1 representative(s)
-- Type: Clerk (tipo_Representante = 5)
-- ============================================================

-- ============================================================
-- DATABASE: BotDB
-- ============================================================
BEGIN TRANSACTION;

-- Table: tblRepresentative_Table_AWS
INSERT INTO [botDB].[dbo].[tblRepresentative_Table_AWS]
    ([Representative_Id], [Email_Address], [Display_Name], [Mobile_Tel_Num], 
     [tipo_Representante], [Maintained_By_Db_Id], [RFC])
VALUES
    -- Representative 1: Patricia Flores Domínguez
    (2075000762341, 'patricia.flores@pruebasprovident.mx', 'Patricia Flores Domínguez', '2481266346', 5, 2075, 'FODP920823H2R');

-- Table: Agency_Representative_AWS
INSERT INTO [botDB].[dbo].[Agency_Representative_AWS]
    ([Agency_Id], [Representative_Id], [Maintained_By_Db_Id])
VALUES
    (2075000000335, 2075000762341, 2075);

COMMIT TRANSACTION;

-- ============================================================
-- DATABASE: Challenger_uat
-- ============================================================
BEGIN TRANSACTION;

-- Table: tblRepresentative_Table_AWS
INSERT INTO [Challenger_uat].[dbo].[tblRepresentative_Table_AWS]
    ([Representative_Id], [Email_Address], [Display_Name], [Mobile_Tel_Num], 
     [tipo_Representante], [Maintained_By_Db_Id], [RFC])
VALUES
    -- Representative 1: Patricia Flores Domínguez
    (2075000762341, 'patricia.flores@pruebasprovident.mx', 'Patricia Flores Domínguez', '2481266346', 5, 2075, 'FODP920823H2R');

-- Table: Agency_Representative_AWS
INSERT INTO [Challenger_uat].[dbo].[Agency_Representative_AWS]
    ([Agency_Id], [Representative_Id], [Maintained_By_Db_Id])
VALUES
    (2075000000335, 2075000762341, 2075);

COMMIT TRANSACTION;

-- ============================================================
-- Summary
-- ============================================================
-- Created 1 representative(s) for branch Izcalli (2075)
-- Agency: 2075000000335
-- Representative IDs: 2075000762341
-- ============================================================
