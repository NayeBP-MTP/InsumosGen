# InsumosProvident.dbml — Schema Overview

## Schemas / Databases Present

| Schema | Description |
|--------|-------------|
| `CNFS_NFS_DBO` | Core NFS (National Field System) — main operational database |
| `CNFS_dbo` | Analytics, reporting, and utility tables |
| `CNFS_perezvma` | User-specific reporting tables |
| `Customer_App_jwtprovident` | Customer mobile app — JWT auth framework (arq_* and jwt_* tables) |
| `Customer_App_master` | SQL Server system/fallback tables |
| `Customer_App_pagosprovident` | Customer payment receipts (AgreementPayments) |
| `Customer_App_provident_app_customer` | Customer app FAQs and notifications |
| `Pesos_Offer_CognitoRoleAuthorizations` | AWS Cognito role-based access control |
| `Pesos_Offer_FloatControlDB` | Cash float control and bank reference management |
| `Pesos_Offer_LeadsDigitales` | Digital leads capture and processing |
| `Pesos_Offer_Originacion` | Loan origination workflow, expedientes (case files), backoffice |

## File Breakdown

| File | Contents |
|------|----------|
| `01_CNFS_NFS_DBO_core.md` | Agreement, Customer, Representative, Agency — the main operational entities |
| `02_CNFS_NFS_DBO_products_events.md` | Product, ProductVersion, Element, Event, and related rule tables |
| `03_CNFS_NFS_DBO_reference_data.md` | All `*_Desc`, `*_Type`, `*_Status` lookup/reference tables |
| `04_CNFS_NFS_DBO_org_structure.md` | Role, Location, Site, Company, Security, Stock tables |
| `05_app_schemas.md` | Customer_App_*, Pesos_Offer_*, CNFS_dbo, CNFS_perezvma |
| `06_relationships.md` | All `Ref` foreign key relationships defined in the DBML |

## Common Audit Columns

Every table in `CNFS_NFS_DBO` carries these standard audit columns:

| Column | Type | Notes |
|--------|------|-------|
| `Dt_Generation_Id` | `T_Dt_Generation_Id` | Default 0 |
| `Dt_Transaction_Id` | `T_Dt_Transaction_Id` | Business transaction identifier |
| `Dt_Write_Bln` | `T_Write_Bln` | Distributed transaction write flag |
| `Last_Updated_Datetime` | `T_Last_Updated_Smalldatetime` | |
| `Last_Updated_Id` | `T_Nfs_Person_Id` | Who last updated |
| `Last_Updated_Timestamp` | `timestamp` | Row version |

## Common Custom Types Used

| Type | Meaning |
|------|---------|
| `T_Id` | Standard integer ID |
| `T_Db_Id` | Database/site identifier (for distributed DB) |
| `T_Nfs_Person_Id` | Person identifier (bigint-like) |
| `T_Code` | Short code (varchar ~2-4 chars) |
| `T_3CharCode` | 3-character code |
| `T_Boolean` | Boolean flag (tinyint) |
| `T_Amount` | Monetary amount |
| `T_Small_Amount` | Smaller monetary amount |
| `T_Large_Amount` | Large monetary amount |
| `T_Percentage` | Percentage |
| `T_Large_Percentage` | High-precision percentage |
| `T_Date` | Date |
| `T_Datetime` | Datetime |
| `T_Smalldatetime` | Smalldatetime |
| `T_Delete_Flag` | Soft delete flag |
| `T_Short_Text` | Short string |
| `T_Text` | Medium string |
| `T_Long_Text` | Long string |
| `T_Name` | Person/entity name |
| `T_Full_Name` | Full name |
| `T_Full_Address` | Full address string |
| `T_Postcode` | Postal code |
| `T_Telephone_Num` | Phone number |
| `T_Agency_Id` | Agency identifier |
| `T_Company_Code` | Company code |
| `T_Number` | Integer number |
| `T_Small_Num` | Small integer |
| `T_Big_Id` | Large integer ID |
| `T_Soundex` | Soundex phonetic code |
| `T_Sequence_Num` | Ordering sequence |
| `T_Stock_Num` | Stock item number |
| `T_Pin_Code` | Customer PIN |
