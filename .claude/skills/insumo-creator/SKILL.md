---
name: insumo-creator
description: One-stop creation workflow for adding/maintaining database insumos (representatives, agencies, customers, etc.) from InsumosProvident schema. Use this skill whenever the user wants to create test data, add representatives, generate SQL inserts for database entities, create rollback scripts, or manage any database insumos. The skill orchestrates multiple specialized agents to generate production-ready SQL files with rollback capabilities.
---

# Insumo Creator

A comprehensive workflow for creating and maintaining database insumos (test data, representatives, agencies, etc.) for the InsumosProvident system. This skill spawns an orchestrator that guides you through the creation process and delegates to specialized agents.

## Overview

This skill helps you create database insumos by:
1. Asking what type of insumo you want to create
2. Gathering required parameters
3. Delegating to specialized creator agents
4. Generating SQL files with INSERT statements
5. Creating rollback SQL scripts for safe reversal

## Workflow

### Step 1: Determine Insumo Type

Ask the user what type of insumo they want to create:

**Available insumo types:**
- **Representatives** — Create new representatives in both BotDB and Challenger databases
- **Agency Structure** — Create a brand new agency (a "star"/representative point
  of sale) under a DM/AM team in `AgencyStructure`, reusing an existing team or
  creating one, in both Challenger_uat and botDB (see
  `agents/agency-structure-creator.md` and
  `config/Context/NUEVA_ESTRUCTURA_AGENCIA.md`)
- *(More types will be added as agents are developed)*

### Step 2: Gather Parameters

Based on the insumo type selected, collect the necessary information from the user. Each insumo type has different requirements (see agent-specific documentation in `agents/` directory).

### Step 3: Delegate to Specialized Agent

Read the appropriate agent file from `agents/` and follow its instructions to generate the SQL. Each agent is responsible for:
- Validating input parameters
- Generating INSERT statements for all required tables
- Creating corresponding DELETE statements for rollback
- Ensuring data consistency across related tables

### Step 4: Generate Output Files

Create two SQL files in the workspace:

1. **`<insumo-type>_insert_<timestamp>.sql`** — The main SQL file with all INSERT statements
2. **`<insumo-type>_rollback_<timestamp>.sql`** — The rollback SQL file with DELETE statements in reverse order

Both files should:
- Include clear comments explaining what they do
- Be ready to run outside the IDE
- Handle dependencies correctly (insert order matters)
- Include transaction wrappers for safety

### Step 5: Present Results

Show the user:
- Path to both generated SQL files
- Summary of what was created (number of records, tables affected)
- Any important notes or warnings
- Instructions for running the SQL files

## File Structure

```
insumo-creator/
├── SKILL.md (this file)
├── agents/
│   ├── representative-creator.md — Creates representatives/stars
│   ├── agency-structure-creator.md — Creates a new agency (star) under a DM/AM team
│   └── (future agents...)
├── references/
│   ├── agencies.md — Agency branch numbers and ID construction rules
│   └── representative-types.md — Representative role types and IDs
└── scripts/
    └── (helper scripts if needed)
```

## Important Notes

- Always generate both INSERT and ROLLBACK SQL files
- Use transactions to ensure atomicity
- Validate all IDs follow the correct format (see `references/agencies.md`)
- Generate realistic random data (names, emails, RFCs)
- Ensure email format is always `[name]@pruebasprovident.mx`
- Phone numbers should be `2481266346` unless specified otherwise
- RFCs must match the generated names

## Database Context

The skill works with multiple databases:
- **BotDB** (Pesos_Offer_botDB) — Production bot database
- **Challenger_uat** — UAT/testing environment
- Both databases have similar schemas for representatives and agencies

Key tables:
- `tblRepresentative_Table_AWS` — Representative master data
- `Agency_Representative_AWS` — Links representatives to agencies

See the full schema in the workspace at `InsumosGen/schema/InsumosProvident.dbml` and mapping documentation in `InsumosGen/schema/mapping/`.

## Usage Examples

**Example 1: Create a single representative**
```
User: "Create a new representative for Izcalli branch"
→ Orchestrator asks for quantity (default: 1)
→ Delegates to representative-creator agent
→ Generates SQL files with 1 representative
```

**Example 2: Create multiple representatives**
```
User: "I need 5 new stars for Tijuana"
→ Orchestrator confirms: 5 representatives for branch 2093
→ Delegates to representative-creator agent
→ Generates SQL files with 5 representatives
```

**Example 3: Create representatives for multiple branches**
```
User: "Create 2 reps for Izcalli and 3 for Zacatecas"
→ Orchestrator processes each branch separately
→ Generates combined SQL files
```

## Error Handling

If something goes wrong:
- Validate all IDs before generating SQL
- Check that branch numbers exist in `references/agencies.md`
- Ensure no duplicate IDs are generated
- Verify RFC format matches name structure
- Confirm email addresses follow the required pattern

## Extending the Skill

To add new insumo types:
1. Create a new agent file in `agents/<type>-creator.md`
2. Document the required parameters
3. Define the SQL generation logic
4. Update this file's "Available insumo types" list
5. Test with sample data
