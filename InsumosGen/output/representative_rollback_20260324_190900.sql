-- ============================================================
-- Representative Rollback Script
-- Generated: 2026-03-24 19:09:00
-- Quantity: 4 representatives across 4 agencies
-- ============================================================
-- WARNING: This will DELETE the representatives created by the insert script
-- ============================================================

-- Begin Transaction
BEGIN TRANSACTION;

-- ============================================================
-- DATABASE: Challenger_uat (Delete first - reverse order)
-- ============================================================

-- Table: Agency_Representative_AWS
DELETE FROM [Challenger_uat].[dbo].[Agency_Representative_AWS]
WHERE [Representative_Id] IN (2075000567890, 2060000678901, 2049000789012, 2025000890123);

-- Table: tblRepresentative_Table_AWS
DELETE FROM [Challenger_uat].[dbo].[tblRepresentative_Table_AWS]
WHERE [Representative_Id] IN (2075000567890, 2060000678901, 2049000789012, 2025000890123);

-- ============================================================
-- DATABASE: BotDB
-- ============================================================

-- Table: Agency_Representative_AWS
DELETE FROM [botDB].[dbo].[Agency_Representative_AWS]
WHERE [Representative_Id] IN (2075000567890, 2060000678901, 2049000789012, 2025000890123);

-- Table: tblRepresentative_Table_AWS
DELETE FROM [botDB].[dbo].[tblRepresentative_Table_AWS]
WHERE [Representative_Id] IN (2075000567890, 2060000678901, 2049000789012, 2025000890123);

-- Commit Transaction
COMMIT TRANSACTION;

-- ============================================================
-- Summary
-- ============================================================
-- Deleted 4 representatives:
-- 1. Erick Daniel Ávila (2075000567890) - Izcalli
-- 2. Juan Vera (2060000678901) - Zacatecas
-- 3. Laura Muñoa (2049000789012) - San Luis Potosí
-- 4. Ulises Gomez (2025000890123) - Aguascalientes
-- ============================================================
