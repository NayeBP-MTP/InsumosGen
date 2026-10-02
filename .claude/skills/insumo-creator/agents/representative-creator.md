# Representative Creator Agent

This agent creates new representatives in both BotDB and Challenger databases, generating production-ready SQL with rollback scripts.

## Responsibilities

1. Generate unique Representative_Id values following the correct format
2. Create random but realistic representative names
3. Generate matching RFCs based on names and dates
4. Create INSERT statements for both databases
5. Generate corresponding DELETE statements for rollback
6. Ensure data consistency across all tables

## Required Parameters

Ask the user for:

1. **Branch** — Which agency branch (Izcalli, Tijuana, Zacatecas, San Luis Potosí, Aguascalientes)
2. **Agency_Id or Agency Suffix** — The specific 13-digit Agency_Id OR the 6-digit suffix (since there may be multiple agencies per branch location). If the user provides a suffix, construct the full Agency_Id using the branch number.
3. **Quantity** — How many representatives to create
4. **tipo_Representante** — Representative type (see `references/representative-types.md` for valid values):
   - 1 = DM (District Manager)
   - 2 = Estrellas (Stars) — **Default**
   - 3 = AM (Area Manager)
   - 4 = OM (Operations Manager)
   - 5 = Clerk
   - 6 = AC (Area Coordinator)
   - 7 = TL (Team Leader)
   - 8 = CSAM (Customer Service Area Manager)
5. **Custom Name(s)** (Optional) — If the user provides specific name(s), use them instead of generating random names. If creating multiple representatives and only some names are provided, generate random names for the rest.

## Data Generation Rules

### Representative_Id Construction

Format: `[BBBB][000][SSSSS]` (13 digits total)
- `BBBB` = 4-digit branch number (e.g., 2075 for Izcalli)
- `000` = Always three zeros
- `SSSSS` = Random 5-6 digit suffix with leading zeros if needed

Example: `2075000012345`

### Name Generation

**If user provides custom name(s):**
- Use the exact name(s) provided by the user
- Ensure proper Spanish characters are preserved (á, é, í, ó, ú, ñ)
- Parse the name to extract first name, paternal surname, and maternal surname for RFC generation
- If creating multiple reps and only some names provided, generate random names for the remaining ones

**If generating random names:**
Generate realistic Mexican names randomly. Examples:
- Juan Pérez García
- María González López
- Carlos Rodríguez Martínez
- Ana Hernández Sánchez
- Luis Ramírez Torres
- Carmen Flores Morales
- José Mendoza Cruz
- Laura Castillo Ruiz

**Important:** Use proper Spanish characters (á, é, í, ó, ú, ñ) in names.

### Email Generation

Format: `[firstname].[lastname]@pruebasprovident.mx`

Rules:
- Use first name and first last name only
- Convert to lowercase
- Remove accents (á→a, é→e, etc.)
- Remove spaces

Examples:
- Juan Pérez García → `juan.perez@pruebasprovident.mx`
- María González López → `maria.gonzalez@pruebasprovident.mx`

### Phone Number

Always use: `2481266346` (unless user specifies otherwise)

### RFC Generation

Format: `[4 letters][6 digits][3 chars]`

Construction rules:
1. **First letter** — First letter of paternal surname (apellido paterno)
2. **Second letter** — First vowel (after first letter) of paternal surname
3. **Third letter** — First letter of maternal surname (apellido materno)
4. **Fourth letter** — First letter of first name
5. **6 digits** — Birth date in YYMMDD format
6. **3 chars** — Random homoclave (can use letters/numbers)

Example for "Juan Pérez García" born 1990-05-15:
- Paternal: Pérez → P, E
- Maternal: García → G
- Name: Juan → J
- Date: 900515
- Homoclave: GTO (random)
- Result: `PEGJ900515GTO`

**Note:** The birth date doesn't need to match exactly; generate a random realistic date (1970-2000).

### Maintained_By_Db_Id

Use only the 4-digit branch number from agencies.md

## Tables to Populate

### 1. BotDB.dbo.tblRepresentative_Table_AWS

```sql
INSERT INTO [botDB].[dbo].[tblRepresentative_Table_AWS]
    ([Representative_Id], [Email_Address], [Display_Name], [Mobile_Tel_Num], 
     [tipo_Representante], [Maintained_By_Db_Id], [RFC])
VALUES
    (2075000012345, 'juan.perez@pruebasprovident.mx', 'Juan Pérez García', 
     '2481266346', 2, 2075, 'PEGJ900515GTO');  -- tipo_Representante: 2 = Estrellas
```

### 2. Challenger_uat.dbo.tblRepresentative_Table_AWS

Same structure as BotDB — create identical INSERT statement but for Challenger database.

### 3. BotDB.dbo.Agency_Representative_AWS

Links the representative to their agency:

```sql
INSERT INTO [botDB].[dbo].[Agency_Representative_AWS]
    ([Agency_Id], [Representative_Id], [Maintained_By_Db_Id])
VALUES
    (2075000001234, 2075000012345, 2075);
```

**Note:** The `Agency_Id` should be provided by the user (either as the full 13-digit ID or as the 6-digit suffix). If the user provides only the suffix, construct the full Agency_Id by combining the branch number + "000" + suffix. Refer to `references/agencies.md` for existing agencies.

### 4. Challenger_uat.dbo.Agency_Representative_AWS

Same structure as BotDB — create identical INSERT statement.

## SQL File Structure

### Insert File (`representative_insert_<timestamp>.sql`)

**Important:** Group all SQL queries by database, not by table. Each database should have its own BEGIN TRANSACTION / COMMIT TRANSACTION block.

```sql
-- ============================================================
-- Representative Creation Script
-- Generated: <timestamp>
-- Branch: <branch_name> (<branch_number>)
-- Agency: <agency_id>
-- Quantity: <count> representative(s)
-- Type: <role_name> (tipo_Representante = <tipo_id>)
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
    -- Representative 1: <name>
    (<rep_id_1>, '<email_1>', '<name_1>', '2481266346', 2, <branch>, '<rfc_1>'),
    -- Representative 2: <name>
    (<rep_id_2>, '<email_2>', '<name_2>', '2481266346', 2, <branch>, '<rfc_2>');
    -- ... (continue for all representatives)

-- Table: Agency_Representative_AWS
INSERT INTO [botDB].[dbo].[Agency_Representative_AWS]
    ([Agency_Id], [Representative_Id], [Maintained_By_Db_Id])
VALUES
    (<agency_id>, <rep_id_1>, <branch>),
    (<agency_id>, <rep_id_2>, <branch>);
    -- ... (continue for all representatives)

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
    -- Representative 1: <name>
    (<rep_id_1>, '<email_1>', '<name_1>', '2481266346', 2, <branch>, '<rfc_1>'),
    -- Representative 2: <name>
    (<rep_id_2>, '<email_2>', '<name_2>', '2481266346', 2, <branch>, '<rfc_2>');
    -- ... (continue for all representatives)

-- Table: Agency_Representative_AWS
INSERT INTO [Challenger_uat].[dbo].[Agency_Representative_AWS]
    ([Agency_Id], [Representative_Id], [Maintained_By_Db_Id])
VALUES
    (<agency_id>, <rep_id_1>, <branch>),
    (<agency_id>, <rep_id_2>, <branch>);
    -- ... (continue for all representatives)

COMMIT TRANSACTION;

-- ============================================================
-- Summary
-- ============================================================
-- Created <count> representative(s) for branch <branch_name> (<branch_number>)
-- Agency: <agency_id>
-- Representative IDs: <rep_id_1>, <rep_id_2>, ...
-- ============================================================
```

### Rollback File (`representative_rollback_<timestamp>.sql`)

**Important:** Group all DELETE queries by database, matching the insert file structure. Each database should have its own BEGIN TRANSACTION / COMMIT TRANSACTION block.

```sql
-- ============================================================
-- Representative Rollback Script
-- Generated: <timestamp>
-- Branch: <branch_name> (<branch_number>)
-- Agency: <agency_id>
-- Quantity: <count> representative(s)
-- Type: <role_name> (tipo_Representante = <tipo_id>)
-- ============================================================
-- WARNING: This will DELETE the representatives created by the insert script
-- ============================================================

-- ============================================================
-- DATABASE: Challenger_uat (Delete first - reverse order)
-- ============================================================
BEGIN TRANSACTION;

-- Table: Agency_Representative_AWS
DELETE FROM [Challenger_uat].[dbo].[Agency_Representative_AWS]
WHERE [Representative_Id] IN (<rep_id_1>, <rep_id_2>, ...);

-- Table: tblRepresentative_Table_AWS
DELETE FROM [Challenger_uat].[dbo].[tblRepresentative_Table_AWS]
WHERE [Representative_Id] IN (<rep_id_1>, <rep_id_2>, ...);

COMMIT TRANSACTION;

-- ============================================================
-- DATABASE: BotDB
-- ============================================================
BEGIN TRANSACTION;

-- Table: Agency_Representative_AWS
DELETE FROM [botDB].[dbo].[Agency_Representative_AWS]
WHERE [Representative_Id] IN (<rep_id_1>, <rep_id_2>, ...);

-- Table: tblRepresentative_Table_AWS
DELETE FROM [botDB].[dbo].[tblRepresentative_Table_AWS]
WHERE [Representative_Id] IN (<rep_id_1>, <rep_id_2>, ...);

COMMIT TRANSACTION;

-- ============================================================
-- Summary
-- ============================================================
-- Deleted <count> representative(s) from branch <branch_name> (<branch_number>)
-- Agency: <agency_id>
-- Representative IDs removed: <rep_id_1>, <rep_id_2>, ...
-- ============================================================
```

## Validation Checklist

Before generating SQL, verify:

- [ ] All Representative_Id values are unique and follow the 13-digit format
- [ ] Branch number exists in `references/agencies.md`
- [ ] All names are realistic and properly formatted (or match user-provided custom names)
- [ ] If custom names provided, they are used exactly as specified
- [ ] All emails follow the `[name]@pruebasprovident.mx` pattern
- [ ] All RFCs match the name structure (4 letters + 6 digits + 3 chars)
- [ ] Phone number is `2481266346`
- [ ] Maintained_By_Db_Id is the 4-digit branch number
- [ ] Agency_Id is valid for the branch
- [ ] Both INSERT and ROLLBACK files are generated
- [ ] SQL queries are grouped by database (BotDB, then Challenger_uat)
- [ ] DELETE statements are in reverse order and grouped by database

## Output

After generating the SQL files, provide the user with:

1. **File paths** — Full paths to both SQL files
2. **Summary table** — List of all created representatives with their IDs, names, and emails
3. **Instructions** — How to run the SQL files
4. **Notes** — Any important information (e.g., Agency_Id assumptions)

Example summary:

```
✓ Generated SQL files:
  - Insert: C:\...\representative_insert_20260324_184300.sql
  - Rollback: C:\...\representative_rollback_20260324_184300.sql

✓ Created 3 representatives for Izcalli (2075):

| Representative_Id | Name                    | Email                          | RFC           |
|-------------------|-------------------------|--------------------------------|---------------|
| 2075000012345     | Juan Pérez García       | juan.perez@pruebasprovident.mx | PEGJ900515GTO |
| 2075000012346     | María González López    | maria.gonzalez@pruebasprovident.mx | GOLM850320ABC |
| 2075000012347     | Carlos Rodríguez Martínez | carlos.rodriguez@pruebasprovident.mx | ROMC920815XYZ |

✓ To execute:
  1. Review the SQL files
  2. Run representative_insert_20260324_184300.sql in your SQL client
  3. If rollback needed, run representative_rollback_20260324_184300.sql

⚠ Note: Using Agency_Id 2075000001234 (verify this exists in your database)
```
