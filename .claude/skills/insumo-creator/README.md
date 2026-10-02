# Insumo Creator Skill

A comprehensive workflow for creating and maintaining database insumos (test data, representatives, agencies, etc.) for the InsumosProvident system.

## What This Skill Does

The Insumo Creator skill provides an orchestrated workflow for generating production-ready SQL scripts to populate your databases with test data. It:

- Generates realistic test data (names, emails, RFCs, IDs)
- Creates INSERT statements for multiple related tables
- Generates rollback scripts for safe reversal
- Ensures data consistency across BotDB and Challenger databases
- Validates all data before generating SQL

## Current Capabilities

### ✅ Representatives (Stars)

Create new representatives in both BotDB and Challenger databases:
- Generates unique Representative_Id values
- Creates realistic Mexican names with proper accents
- Generates matching RFCs based on names
- Creates proper email addresses
- Links representatives to agencies
- Populates all required tables

## File Structure

```
insumo-creator/
├── SKILL.md                          # Main skill instructions
├── README.md                         # This file
├── agents/
│   └── representative-creator.md     # Representative creation agent
├── references/
│   └── agencies.md                   # Agency branch reference data
└── scripts/
    └── name_generator.py             # Helper script for data generation
```

## How to Use

### Basic Usage

Simply ask to create representatives:

```
"Create 3 representatives for Izcalli"
"I need 5 new stars for Tijuana"
"Create a representative for Zacatecas branch"
```

The skill will:
1. Ask for any missing parameters (branch, quantity)
2. Generate realistic data
3. Create two SQL files:
   - `representative_insert_<timestamp>.sql` — INSERT statements
   - `representative_rollback_<timestamp>.sql` — DELETE statements

### Available Branches

| Branch Name | Branch Number |
|-------------|---------------|
| Izcalli (Cuautitlán Izcalli) | 2075 |
| Tijuana | 2093 |
| Zacatecas | 2060 |
| San Luis Potosí | 2049 |
| Aguascalientes | 2025 |

## Generated Data Examples

### Representative Data

```sql
-- Example generated representative
Representative_Id: 2075000012345
Display_Name: Juan Pérez García
Email: juan.perez@pruebasprovident.mx
RFC: PEGJ900515GTO
Mobile_Tel_Num: 2481266346
tipo_Representante: 2
Maintained_By_Db_Id: 2075
```

### Tables Populated

For each representative, the skill creates records in:

**BotDB:**
- `tblRepresentative_Table_AWS`
- `Agency_Representative_AWS`

**Challenger:**
- `tblRepresentative_Table_AWS`
- `Agency_Representative_AWS`

## Output Files

### Insert File

Contains all INSERT statements wrapped in a transaction:
- Clear comments for each section
- Organized by database and table
- Ready to run in SQL Server Management Studio

### Rollback File

Contains DELETE statements in reverse order:
- Removes records from all tables
- Safe transaction wrapper
- Can be run if you need to undo the inserts

## Helper Scripts

### name_generator.py

Python script for generating realistic Mexican names and RFCs. Can be used standalone:

```bash
python scripts/name_generator.py
```

Functions available:
- `generate_name(gender=None)` — Generate random name
- `generate_email(name_dict)` — Create email from name
- `generate_rfc(name_dict, birth_date=None)` — Generate RFC
- `generate_representative_id(branch_number, existing_ids=None)` — Create unique ID
- `generate_representatives(branch_number, count=1)` — Generate multiple reps

## Data Validation

The skill validates:
- ✓ Representative_Id follows 13-digit format
- ✓ Branch numbers are valid
- ✓ Names are realistic and properly formatted
- ✓ Emails follow `[name]@pruebasprovident.mx` pattern
- ✓ RFCs match name structure (4 letters + 6 digits + 3 chars)
- ✓ No duplicate IDs are generated
- ✓ All required fields are populated

## Future Enhancements

Planned insumo types to add:
- Agencies
- Customers
- Agreements
- Offers
- Leads
- Products

## Database Context

Works with:
- **BotDB** (Pesos_Offer_botDB) — Production bot database
- **Challenger_uat** — UAT/testing environment

Full schema available at:
- `InsumosGen/schema/InsumosProvident.dbml`
- `InsumosGen/schema/mapping/` — Detailed mapping documentation

## Troubleshooting

### Issue: Duplicate Representative_Id

The script generates random IDs. If you get a duplicate, the validation will catch it and generate a new one.

### Issue: Invalid Branch Number

Make sure you're using one of the 5 valid branches listed in `references/agencies.md`.

### Issue: RFC Doesn't Match Name

The RFC generation follows Mexican RFC rules. If it looks wrong, verify:
- First letter of paternal surname
- First vowel (after first letter) of paternal surname
- First letter of maternal surname
- First letter of first name

### Issue: SQL File Won't Run

Check that:
- You have permissions on both databases
- The databases exist and are accessible
- No records with the same IDs already exist

## Contributing

To add a new insumo type:

1. Create agent file: `agents/<type>-creator.md`
2. Document required parameters
3. Define SQL generation logic
4. Add validation rules
5. Update `SKILL.md` with new type
6. Test with sample data

## License

Internal use only for Provident Mexico database management.
