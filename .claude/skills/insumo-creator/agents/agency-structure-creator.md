# Agency Structure Creator Agent

This agent creates a brand new agency (a "star"/representative point of sale)
under a DM/AM team in `AgencyStructure`, in both Challenger_uat and botDB. It
reuses the Python helpers already built for the automation framework instead of
hand-computing IDs, so the numbering stays consistent with what `run.py`'s
"Nueva estructura de agencia" flow produces.

See `config/Context/NUEVA_ESTRUCTURA_AGENCIA.md` for the full design rationale
(why the `Agency_Id` scheme changed, how DM/AM numbering was decided, etc.) —
read it before changing anything here.

## Responsibilities

1. Ask for sucursal, how many agencies, and whether each reuses an existing
   DM/AM team or creates a new one.
2. Compute (never guess) `Agency_Id`, and — for a new DM/AM — the DM number, AM
   number, section letter, and representative identities, by running the
   project's Python helpers via Bash (read-only against the live DB, except for
   reserving values in the local SQLite allocators — see "How the numbers are
   computed" below).
3. Generate INSERT + ROLLBACK SQL files covering all 5 tables, across
   Challenger_uat and botDB, matching the existing `agenciesGenerator.sql`
   style (`BEGIN TRANSACTION` / `BEGIN TRY` / `COMMIT` / `CATCH` + `ROLLBACK`).
4. Tell the user clearly that nothing is written to the database until they run
   the generated SQL file — the Python step only computes and reserves the
   `Agency_Id`/section letter locally so a second run of this agent won't repeat
   them.

## Required Parameters

Ask the user for:

1. **Sucursal** — one of the five configured in `config/sucursales.py`: Izcalli,
   Zacatecas, Aguascalientes, San Luis Potosí, Tijuana. (A new sucursal needs a
   new entry there first — see that file's docstring for the fields required.)
2. **Cantidad** — how many agencies (stars) to create in this batch.
3. **Modo de DM/AM, por agencia** — for each agency in the batch:
   - **Reutilizar un equipo existente** — list the live options (see below) and
     let the user pick one, or
   - **Crear un equipo nuevo** — a brand new DM + AM pair just for this agency.

   Don't assume a batch shares one team: each agency asks independently, same as
   each row in the "Oferta" panel of `run.py`'s UI is independent. If the user
   wants N agencies under one new team, create the team for the first agency
   and reuse it for the rest **within the same command** (see "Creating a new
   DM/AM" below — don't call `generar_dm_nuevo`/`generar_am_nuevo` again for the
   following agencies of that same team).

### Listing existing DM/AM teams to reuse

```bash
python -c "
from services.agency_repository import ChallengerRepository
from config.sucursales import get_sucursal_by_nombre
sucursal = get_sucursal_by_nombre('Izcalli')  # ajustar
for c in ChallengerRepository().get_dm_am_combos(sucursal['branch']):
    print(c)
"
```

Show the user the list (DM code + DM name + section + AM text + AM name) and let
them pick one.

## How the numbers are computed

**Never hand-derive `Agency_Id`, DM/AM numbers, or the section letter.** The
legacy data in `AgencyStructure` is inconsistent across sucursales (e.g. Tijuana
uses "BRM" instead of "DM" in its DM code) — always go through these helpers:

### 1. `Agency_Id` (one call per agency, always — reuse or new team doesn't matter)

```bash
python -c "
from utils.agency_id_allocator import AgencyIdAllocator
from config.sucursales import get_sucursal_by_nombre
sucursal = get_sucursal_by_nombre('Izcalli')  # ajustar
print(AgencyIdAllocator.get_unique_agency_id(sucursal['branch']))
"
```

This **reserves** the Agency_Id in `data/generated_agency_ids.sqlite3` (shared
with `run.py`), so it's safe to call once per agency even if the generated SQL
is never run — it just won't be reused by a later call.

### 2. Creating a new DM/AM team (only when the user chose "Crear un equipo nuevo")

```bash
python -c "
import sys; sys.stdout.reconfigure(encoding='utf-8')
from services.agency_repository import ChallengerRepository, generar_dm_nuevo, generar_am_nuevo
from config.sucursales import get_sucursal_by_nombre
sucursal = get_sucursal_by_nombre('Izcalli')  # ajustar
challenger = ChallengerRepository()
dm_info, dm_persona = generar_dm_nuevo(sucursal, challenger)
am_info, am_persona = generar_am_nuevo(sucursal, challenger)
print('DM:', dm_info, dm_persona)
print('AM:', am_info, am_persona)
"
```

This is **read-only against Challenger_uat** plus a local-SQLite reservation of
the section letter (`data/generated_agency_ids.sqlite3`) — it does not insert
anything. `dm_persona`/`am_persona` carry the Representative_Id/name/email/RFC
you'll use in the DM/AM's own `tblRepresentative_Table_AWS` rows.

### 3. Generating the star (always, one call per agency)

```bash
python -c "
import sys; sys.stdout.reconfigure(encoding='utf-8')
from services.agency_repository import ChallengerRepository, generar_persona
from config.sucursales import get_sucursal_by_nombre
sucursal = get_sucursal_by_nombre('Izcalli')  # ajustar
print(generar_persona(sucursal['branch'], tipo_representante=2, challenger=ChallengerRepository()))
"
```

`tipo_Representante`: 1=DM, 2=Estrella, 3=AM (see `references/representative-types.md`).

## Tables to populate (per agency)

Same 5 inserts as the manual flow in `config/Context/NUEVA_ESTRUCTURA_AGENCIA.md`
section 1.1 / `InsumosGen/generadores/agenciesGenerator.sql`:

1. `Challenger_uat.dbo.AgencyStructure` — one row per agency (star), always.
2. `Challenger_uat.dbo.tblRepresentative_Table_AWS` — the star, always; the DM
   and AM too, but **only the first time** that DM/AM is created in this batch
   (reused rows for the rest of the batch/already-existing teams don't repeat
   this insert).
3. `Challenger_uat.dbo.P_ESTRELLAS_MENSUAL_CATEGORIAS` — one row per agency
   (star). `DM_Letter` = the agency's section letter. Pick a plausible
   `Category`/`GdsCategory` from `MINI`/`GRAN`/`MEGA`/`ULTRA`, current month name
   (Spanish) for `Month_Calc`, next month for `Payment_Month`, and reasonable
   random-looking values for the numeric columns (see existing rows in that
   table for realistic ranges — `Avg_Collected_Cust` ~0.70–0.95,
   `Avg_payment_coll` ~0.05–0.12).
4. `botDB.dbo.Agency_Representative_AWS` — one row per agency:
   `(Agency_Id, Representative_Id, Maintained_By_Db_Id)` where
   `Maintained_By_Db_Id` = sucursal branch number.
5. `botDB.dbo.tblRepresentative_Table_AWS` — same star (and DM/AM, first time
   only) as #2, mirrored into botDB.

## SQL File Structure

Follow the same two-file, per-database-transaction convention as
`representative-creator.md` (`agency_insert_<timestamp>.sql` /
`agency_rollback_<timestamp>.sql`), grouping by database
(Challenger_uat first since botDB's `Agency_Representative_AWS` references the
`Agency_Id`/`Representative_Id` conceptually, even though there's no physical
FK). Reuse the column order from `InsumosGen/generadores/agenciesGenerator.sql`
for `AgencyStructure`'s `VALUES` (it has no explicit column list — the 10
columns are `AgencyId, StarId, StarName, Dm, DmFocusId, DmName, Section, Am,
AMFocusId, AMName`, in that order).

Rollback order (reverse of insert): `P_ESTRELLAS_MENSUAL_CATEGORIAS` →
`AgencyStructure` → `tblRepresentative_Table_AWS` (Challenger_uat), then
`Agency_Representative_AWS` → `tblRepresentative_Table_AWS` (botDB). Only
delete DM/AM representative rows in the rollback if this same script created
them (don't delete a reused team).

## Validation Checklist

- [ ] Every `Agency_Id`/DM number/AM number/section letter came from the Python
      helpers above — none hand-typed or incremented by eyeballing
      `AgencyStructure`.
- [ ] A new DM/AM team is only generated once per batch-of-agencies that share
      it, not once per agency.
- [ ] Emails follow `[nombre].[apellido]@pruebasprovident.mx` with accents
      stripped (the Python helpers already do this — don't hand-edit them).
- [ ] `Maintained_By_Db_Id` is the 4-digit branch number.
- [ ] Both INSERT and ROLLBACK files generated, grouped by database, each with
      its own `BEGIN TRANSACTION`/`COMMIT`.
- [ ] The user understands nothing is in the database yet — only after they run
      the insert file.

## Output

Same format as `representative-creator.md`'s "Output" section: file paths, a
summary table (sucursal, Agency_Id, star name/email, DM code, AM text per
agency), how to run the files, and any notes (e.g. "este lote creó un equipo
nuevo IzcalliDM64E / AM4351 Izcalli, compartido por las 3 agencias").
