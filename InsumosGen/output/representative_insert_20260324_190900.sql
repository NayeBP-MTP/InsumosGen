-- ============================================================
-- Representative Creation Script
-- Generated: 2026-03-24 19:09:00
-- Quantity: 4 representatives across 4 agencies
-- ============================================================

-- Begin Transaction
BEGIN TRANSACTION;

-- ============================================================
-- DATABASE: BotDB
-- ============================================================

-- Table: tblRepresentative_Table_AWS
INSERT INTO [botDB].[dbo].[tblRepresentative_Table_AWS]
    ([Representative_Id], [Email_Address], [Display_Name], [Mobile_Tel_Num], 
     [tipo_Representante], [Maintained_By_Db_Id], [RFC])
VALUES
    -- Representative 1: Erick Daniel Ávila (Izcalli)
    (2075000567890, 'erick.avila@pruebasprovident.mx', 'Erick Daniel Ávila', '2481266346', 2, 2075, 'AADE920518H3K'),
    -- Representative 2: Juan Vera (Zacatecas)
    (2060000678901, 'juan.vera@pruebasprovident.mx', 'Juan Vera', '2481266346', 2, 2060, 'VEXJ850723M9P'),
    -- Representative 3: Laura Muñoa (San Luis Potosí)
    (2049000789012, 'laura.munoa@pruebasprovident.mx', 'Laura Muñoa', '2481266346', 2, 2049, 'MUOL910315R2T'),
    -- Representative 4: Ulises Gomez (Aguascalientes)
    (2025000890123, 'ulises.gomez@pruebasprovident.mx', 'Ulises Gomez', '2481266346', 2, 2025, 'GOMU880627V5W');

-- Table: Agency_Representative_AWS
INSERT INTO [botDB].[dbo].[Agency_Representative_AWS]
    ([Agency_Id], [Representative_Id], [Maintained_By_Db_Id])
VALUES
    (2075000000335, 2075000567890, 2075),
    (2060000001239, 2060000678901, 2060),
    (2049000001234, 2049000789012, 2049),
    (2025000001234, 2025000890123, 2025);
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
    -- Representative 1: Erick Daniel Ávila (Izcalli)
    (2075000567890, 'erick.avila@pruebasprovident.mx', 'Erick Daniel Ávila', '2481266346', 2, 2075, 'AADE920518H3K'),
    -- Representative 2: Juan Vera (Zacatecas)
    (2060000678901, 'juan.vera@pruebasprovident.mx', 'Juan Vera', '2481266346', 2, 2060, 'VEXJ850723M9P'),
    -- Representative 3: Laura Muñoa (San Luis Potosí)
    (2049000789012, 'laura.munoa@pruebasprovident.mx', 'Laura Muñoa', '2481266346', 2, 2049, 'MUOL910315R2T'),
    -- Representative 4: Ulises Gomez (Aguascalientes)
    (2025000890123, 'ulises.gomez@pruebasprovident.mx', 'Ulises Gomez', '2481266346', 2, 2025, 'GOMU880627V5W');

-- Table: Agency_Representative_AWS
INSERT INTO [Challenger_uat].[dbo].[Agency_Representative_AWS]
    ([Agency_Id], [Representative_Id], [Maintained_By_Db_Id])
VALUES
    (2075000000335, 2075000567890, 2075),
    (2060000001239, 2060000678901, 2060),
    (2049000001234, 2049000789012, 2049),
    (2025000001234, 2025000890123, 2025);

-- Commit Transaction
COMMIT TRANSACTION;

-- ============================================================
-- Summary
-- ============================================================
-- Created 4 representatives across 4 agencies:
-- 1. Erick Daniel Ávila (2075000567890) - Izcalli Agency 2075000000335
-- 2. Juan Vera (2060000678901) - Zacatecas Agency 2060000001239
-- 3. Laura Muñoa (2049000789012) - San Luis Potosí Agency 2049000001234
-- 4. Ulises Gomez (2025000890123) - Aguascalientes Agency 2025000001234
-- ============================================================
