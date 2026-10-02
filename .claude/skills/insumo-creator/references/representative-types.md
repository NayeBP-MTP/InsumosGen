# Representative Types Reference

## Provident Role IDs (tipo_Representante)

The `tipo_Representante` field in `tblRepresentative_Table_AWS` corresponds to the `ProvidentRoleID` from the Roles table.

| ProvidentRoleID | RoleName | Description |
|-----------------|----------|-------------|
| 1 | DM | District Manager |
| 2 | Estrellas | Stars (Sales Representatives) |
| 3 | AM | Area Manager |
| 4 | OM | Operations Manager |
| 5 | Clerk | Administrative Clerk |
| 6 | AC | Area Coordinator |
| 7 | TL | Team Leader |
| 8 | CSAM | Customer Service Area Manager |

## Usage in SQL

When creating representatives, use the `ProvidentRoleID` value for the `tipo_Representante` field:

```sql
INSERT INTO [botDB].[dbo].[tblRepresentative_Table_AWS]
    ([Representative_Id], [Email_Address], [Display_Name], [Mobile_Tel_Num], 
     [tipo_Representante], [Maintained_By_Db_Id], [RFC])
VALUES
    (2075000012345, 'juan.perez@pruebasprovident.mx', 'Juan Pérez García', 
     '2481266346', 2, 2075, 'PEGJ900515GTO');  -- tipo_Representante = 2 (Estrellas)
```

## Common Representative Types

- **Estrellas (2)** — Most common type, front-line sales representatives
- **Clerk (5)** — Administrative support staff
- **DM (1)** — District-level management
- **AM (3)** — Area-level management
- **TL (7)** — Team leaders coordinating multiple representatives

## Notes

- The default type for most representatives is **Estrellas (2)**
- When creating test data, ensure the role matches the representative's intended function
- All representative types can be linked to agencies via `Agency_Representative_AWS`
