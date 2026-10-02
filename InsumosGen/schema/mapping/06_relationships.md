# CNFS_NFS_DBO — Foreign Key Relationships (Ref Definitions)

All `Ref` declarations from the DBML file are listed below.
Format: `FK_NAME: ParentTable.Column < ChildTable.Column` (many-to-one: child references parent)

---

## Agency / Agency Status

| FK Name | Parent | Child |
|---------|--------|-------|
| `FK_AGS_ASA` | `Agency_Status_Type.Agency_Status_Type_Code` | `Agency_Status_Type_Desc.Agency_Status_Type_Code` |
| `FK_LAN_ASA` | `Language.Language_Code` | `Agency_Status_Type_Desc.User_Language_Code` |

---

## Agreement Issue Location & Source

| FK Name | Parent | Child |
|---------|--------|-------|
| `FK_AILD` | `Agreement_Issue_Location.Agreement_Issue_Location_Code` | `Agreement_Issue_Location_Desc.Agreement_Issue_Location_Code` |
| `FK_ASLD` | `Agreement_Source.Agreement_Source_Code` | `Agreement_Source_Desc.Agreement_Source_Code` |

---

## Customer Lead

| FK Name | Parent | Child |
|---------|--------|-------|
| `FK_COM_CLD` | `Company.Company_Code` | `Customer_Lead_Table.Company_Code` |
| `FK_REP_CLD` | `Representative_Table.Representative_Id` | `Customer_Lead_Table.Focus_Created_Id` |
| `FK_ROL_CLD` | `Role_Table.(Role_Id, Role_Db_Id)` | `Customer_Lead_Table.(Role_Id, Role_Db_Id)` |
| `FK_TIT_CLD` | `Title.Title_Code` | `Customer_Lead_Table.Title_Code` |

---

## Role Company Bank Accounts

| FK Name | Parent | Child |
|---------|--------|-------|
| `FK_ROL_RCB` | `Role_Table.(Role_Id, Role_Db_Id)` | `Role_Company_Bank_Accounts.(Role_Id, Role_Db_Id)` |
| `FK_SIT_RCB` | `Site.Db_Id` | `Role_Company_Bank_Accounts.Role_Company_Bank_Accounts_Db_Id` |

---

## Notes on Implicit Relationships

The DBML file defines only the above explicit `Ref` entries. However, based on column naming conventions and the `T_Db_Id` / `T_Id` composite key pattern, the following implicit relationships exist throughout the schema:

### Agreement → Customer / Representative / Product
- `Agreement_Table.Customer_Id` → `Customer_Table.Customer_Id`
- `Agreement_Table.Issuing_Representative_Id` → `Representative_Table.Representative_Id`
- `Agreement_Table.(Product_Version_Id, Product_Version_Db_Id)` → `Product_Version_Table.(Product_Version_Id, Product_Version_Db_Id)`
- `Agreement_Table.Agreement_Status_Code` → `Agreement_Status.Agreement_Status_Code`
- `Agreement_Table.Agreement_Source_Code` → `Agreement_Source.Agreement_Source_Code`
- `Agreement_Table.Agreement_Issue_Location_Code` → `Agreement_Issue_Location.Agreement_Issue_Location_Code`
- `Agreement_Table.Company_Code` → `Company.Company_Code`

### Agreement Transaction → Agreement / Type
- `Agreement_Transaction_Table.(Agreement_Id, Agreement_Db_Id)` → `Agreement_Table.(Agreement_Id, Agreement_Db_Id)`
- `Agreement_Transaction_Table.Agreement_Transaction_Type_Code` → `Agreement_Transaction_Type.Agreement_Transaction_Type_Code`

### Element → Agreement / Product Element
- `Element_Table.(Agreement_Id, Agreement_Db_Id)` → `Agreement_Table.(Agreement_Id, Agreement_Db_Id)`
- `Element_Table.(Product_Element_Id, Product_Element_Db_Id)` → `Product_Element_Table.(Product_Element_Id, Product_Element_Db_Id)`

### Event → Agreement / Event Type
- `Event_Table.(Agreement_Id, Agreement_Db_Id)` → `Agreement_Table.(Agreement_Id, Agreement_Db_Id)`
- `Event_Table.Event_Type_Code` → `Event_Type.Event_Type_Code`
- `Event_Table.Parent_Event_Id` → `Event_Table.Event_Id` *(self-reference)*
- `Event_Table.Contraing_Event_Id` → `Event_Table.Event_Id` *(self-reference)*

### Event Version → Event
- `Event_Version_Table.(Event_Id, Event_Db_Id)` → `Event_Table.(Event_Id, Event_Db_Id)`

### Event Impact → Event Version / Element
- `Event_Impact_Table.(Event_Id, Event_Db_Id, Event_Version)` → `Event_Version_Table.(Event_Id, Event_Db_Id, Event_Version)`
- `Event_Impact_Table.(Element_Id, Element_Db_Id)` → `Element_Table.(Element_Id, Element_Db_Id)`

### Event Impact Status / TAP → Event Version / Element
- `Event_Impact_Status_Table.(Event_Id, Event_Db_Id, Event_Version)` → `Event_Version_Table`
- `Event_Impact_Status_Table.(Element_Id, Element_Db_Id)` → `Element_Table`
- `Event_Impact_TAP_And_Rates_Table.(Agreement_Id, Agreement_Db_Id)` → `Agreement_Table`

### Product → Company / Version / Element / Package
- `Product_Table.Company_Code` → `Company.Company_Code`
- `Product_Version_Table.(Product_Id, Product_Db_Id)` → `Product_Table.(Product_Id, Product_Db_Id)`
- `Product_Element_Table.(Product_Version_Id, Product_Version_Db_Id)` → `Product_Version_Table.(Product_Version_Id, Product_Version_Db_Id)`
- `Product_Element_Table.Element_Type_Code` → `Element_Type.Element_Type_Code`
- `Product_Element_Attribute_Table.(Product_Element_Id, Product_Element_Db_Id)` → `Product_Element_Table`
- `Product_Element_Event_Type_Rule_Table.(Product_Element_Id, Product_Element_Db_Id)` → `Product_Element_Table`
- `Product_Element_Event_Type_Rule_Table.Event_Type_Code` → `Event_Type.Event_Type_Code`
- `Product_Version_Valid_Issue_Table.(Product_Version_Id, Product_Version_Db_Id)` → `Product_Version_Table`
- `Product_Version_Valid_Issue_Element_Table.(Product_Version_Id, Product_Version_Db_Id, Issue_Value)` → `Product_Version_Valid_Issue_Table`
- `Product_Version_Package_Table.(Product_Version_Id, Product_Version_Db_Id)` → `Product_Version_Table`
- `Product_Version_Package_Table.Package_Id` → `Package_Table.Package_Id`
- `Product_Role_Table.(Product_Id, Product_Db_Id)` → `Product_Table`
- `Product_Role_Table.(Role_Id, Role_Db_Id)` → `Role_Table`
- `Product_Group_Item_Table.(Product_Id, Product_Db_Id)` → `Product_Table`

### Representative → Role / Leaving Reason / Location
- `Representative_Table.Company_Code` → `Company.Company_Code`
- `Representative_Table.Representative_Status_Code` → `Representative_Status` (desc table)
- `Representative_Table.Representative_Type_Code` → `Representative_Type` (desc table)
- `Representative_Table.Leaving_Reason_Id` → `Leaving_Reason.Leaving_Reason_Id`
- `Representative_Table.Title_Code` → `Title.Title_Code`
- `Representative_Table.Buddy_Representative_Id` → `Representative_Table.Representative_Id` *(self-reference)*

### Representative Role → Representative / Role
- `Representative_Role_Table.Representative_Id` → `Representative_Table.Representative_Id`
- `Representative_Role_Table.(Role_Id, Role_Db_Id)` → `Role_Table.(Role_Id, Role_Db_Id)`

### Role → Role Type / Location / Parent Role
- `Role_Table.Company_Code` → `Company.Company_Code`
- `Role_Table.(Role_Type_Code, Company_Code)` → `Role_Type.(Role_Type_Code, Company_Code)`
- `Role_Table.(Location_Id, Location_Db_Id)` → `Location_Table.(Location_Id, Location_Db_Id)`
- `Role_Table.(Parent_Role_Id, Parent_Role_Db_Id)` → `Role_Table.(Role_Id, Role_Db_Id)` *(self-reference)*

### Agency → Location / Role / Status
- `Agency_Table.(Location_Id, Location_Db_Id)` → `Location_Table.(Location_Id, Location_Db_Id)`
- `Agency_Table.(Role_Id, Role_Db_Id)` → `Role_Table.(Role_Id, Role_Db_Id)`
- `Agency_Table.Agency_Status_Type_Code` → `Agency_Status_Type.Agency_Status_Type_Code`

### Location → Site / Company
- `Location_Table.Company_Code` → `Company.Company_Code`
- `Location_Address.(Location_Id, Location_Db_Id)` → `Location_Table.(Location_Id, Location_Db_Id)`
- `Site.(Location_Id, Location_Db_Id)` → `Location_Table.(Location_Id, Location_Db_Id)`

### Customer → Agency / Status / Title
- `Customer_Table.Company_Code` → `Company.Company_Code`
- `Customer_Table.Customer_Status_Code` → `Customer_Status.Customer_Status_Code`
- `Customer_Table.Title_Code` → `Title.Title_Code`
- `Customer_Address.Customer_Id` → `Customer_Table.Customer_Id`
- `Customer_Agency_History_Table.Customer_Id` → `Customer_Table.Customer_Id`

### Payment Flexibility → Agreement / Event
- `Payment_Flexibility_Request_Table.(Agreement_Id, Agreement_Db_Id)` → `Agreement_Table`
- `Payment_Flexibility_Request_Table.(Event_Id, Event_Db_Id)` → `Event_Table`
- `Payment_Flexibility_Request_Table.Payment_Flexibility_Reason_Code` → `Payment_Flexibility_Reason.Payment_Flexibility_Reason_Code`

### Stock → Representative / Agreement / Type / Status
- `Stock_Item_Table.Company_Code` → `Company.Company_Code`
- `Stock_Item_Table.Stock_Type_Code` → `Stock_Type.Stock_Type_Code`
- `Stock_Item_Table.Stock_Item_Status_Code` → `Stock_Item_Status.Stock_Item_Status_Code`
- `Stock_Item_Table.Responsible_Representative_Id` → `Representative_Table.Representative_Id`
- `Stock_Item_Table.(Agreement_Id, Agreement_Db_Id)` → `Agreement_Table` (when stock item is used for a loan)

### Security Check → Agency / Status
- `Security_Check_Table.Agency_Id` → `Agency_Table.Agency_Id`
- `Security_Check_Table.Security_Check_Status_Code` → `Security_Check_Status.Security_Check_Status_Code`

### Marketing Message → Customer / Company
- `Marketing_Message_History_Table.Customer_Id` → `Customer_Table.Customer_Id`
- `Marketing_Message_History_Table.Company_Code` → `Company.Company_Code`

### Exception Table
- Self-contained; references various entity IDs via nullable columns (no enforced FKs in schema definition).

### Property System
- `Property.Company_Code` → `Company.Company_Code`
- `Property.Property_Code_Selected_From_Code` → `Property_Code_Selected_From.Property_Code_Selected_From_Code`
- `Property_Value.Property_Code_Selected_From_Code` → `Property_Code_Selected_From.Property_Code_Selected_From_Code`
- `Property_Impact.Impacting_Property_ID` → `Property.Property_ID`
- `Property_Impact.Impacted_Property_ID` → `Property.Property_ID`

---

## Cross-Schema Implicit References

| Source Schema | Column | Target Schema | Table | Notes |
|---------------|--------|---------------|-------|-------|
| `Customer_App_pagosprovident.AgreementPayments` | `CustomerId` | `CNFS_NFS_DBO` | `Customer_Table.Customer_Id` | |
| `Customer_App_pagosprovident.AgreementPayments` | `AgreementId` | `CNFS_NFS_DBO` | `Agreement_Table.Agreement_Id` | |
| `Customer_App_pagosprovident.AgreementPayments` | `RepresentativeId` | `CNFS_NFS_DBO` | `Representative_Table.Representative_Id` | |
| `Customer_App_pagosprovident.AgreementPayments` | `TransactionType` | `CNFS_NFS_DBO` | `Agreement_Transaction_Type.Code` | char(2) = T_Code |
| `Customer_App_jwtprovident.arq_usuario` | `num_cliente_contrato` | `CNFS_NFS_DBO` | `Customer_Table` / `Agreement_Table` | varchar(200) |
| `Customer_App_jwtprovident.jwt_usuario` | `num_cliente_contrato` | `CNFS_NFS_DBO` | `Customer_Table` / `Agreement_Table` | varchar(20) |
| `Customer_App_jwtprovident.jwt_usuario` | `num_cliente` | `CNFS_NFS_DBO` | `Customer_Table.Customer_Id` | |
| `CNFS_dbo.AM_KPI` | `Agency_Id` | `CNFS_NFS_DBO` | `Agency_Table.Agency_Id` | |
| `CNFS_dbo.AM_KPI` | `AM_Role_Id` | `CNFS_NFS_DBO` | `Role_Table.Role_Id` | |
| `Pesos_Offer_Originacion.ExpedienteClienteVacio` | `Cliente` | `CNFS_NFS_DBO` | `Customer_Table.Customer_Id` | bigint |
| `Pesos_Offer_Originacion.ExpedienteClienteVacio` | `Agencia` | `CNFS_NFS_DBO` | `Agency_Table.Agency_Id` | bigint |
| `Pesos_Offer_LeadsDigitales.tblLeadsDigitales` | `GDSIdCliente` | `CNFS_NFS_DBO` | `Customer_Table.Customer_Id` | bigint |
| `Pesos_Offer_LeadsDigitales.tblLeadsDigitales` | `BranchNumber` | `Pesos_Offer_Originacion` | `CatBranches.Number` | bigint |
| `Pesos_Offer_Originacion.Concilacion_ProviDigital_focus` | `Num_cliente_Source` | `CNFS_NFS_DBO` | `Customer_Table.Customer_Id` | |
| `Pesos_Offer_Originacion.Concilacion_ProviDigital_focus` | `Agreement_Id_Source` | `CNFS_NFS_DBO` | `Agreement_Table.Agreement_Id` | |
| `Pesos_Offer_CognitoRoleAuthorizations.AuthorizedRole` | `ProvidentRole_FK` | `CNFS_NFS_DBO` | `Role_Table.Role_Id` (conceptually) | int |
