-- ============================================================
-- Representative Rollback Script
-- Generated: 2026-03-27 14:42:00
-- Branch: Izcalli (2075)
-- Agency: 2075000000335
-- Quantity: 1 representative(s)
-- Type: Clerk (tipo_Representante = 5)
-- ============================================================
-- WARNING: This will DELETE the representatives created by the insert script
-- ============================================================

-- ============================================================
-- DATABASE: Challenger_uat (Delete first - reverse order)
-- ============================================================
BEGIN TRANSACTION;

-- Table: Agency_Representative_AWS
DELETE FROM [Challenger_uat].[dbo].[Agency_Representative_AWS]
WHERE [Representative_Id] IN (2075000762341);

-- Table: tblRepresentative_Table_AWS
DELETE FROM [Challenger_uat].[dbo].[tblRepresentative_Table_AWS]
WHERE [Representative_Id] IN (2075000762341);

COMMIT TRANSACTION;

-- ============================================================
-- DATABASE: BotDB
-- ============================================================
BEGIN TRANSACTION;

-- Table: Agency_Representative_AWS
DELETE FROM [botDB].[dbo].[Agency_Representative_AWS]
WHERE [Representative_Id] IN (2075000762341);

-- Table: tblRepresentative_Table_AWS
DELETE FROM [botDB].[dbo].[tblRepresentative_Table_AWS]
WHERE [Representative_Id] IN (2075000762341);

COMMIT TRANSACTION;

-- ============================================================
-- Summary
-- ============================================================
-- Deleted 1 representative(s) from branch Izcalli (2075)
-- Agency: 2075000000335
-- Representative IDs removed: 2075000762341
-- ============================================================
