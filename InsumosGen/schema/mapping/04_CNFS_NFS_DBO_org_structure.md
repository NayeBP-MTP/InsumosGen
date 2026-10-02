# CNFS_NFS_DBO — Organisational Structure, Sites, Stock & Security

## Role_Table
**PK:** `(Role_Id, Role_Db_Id)`

Represents a position/role in the organisational hierarchy (Branch, Region, Area Manager, etc.).

| Column | Type | Notes |
|--------|------|-------|
| `Role_Id` | `T_Id IDENTITY(1,1)` | |
| `Role_Db_Id` | `T_Db_Id` | |
| `Company_Code` | `T_Company_Code` | FK → `Company` |
| `Description` | `T_Short_Text` NOT NULL | Role name |
| `Description_Soundex` | `T_Soundex` | Phonetic search |
| `Role_Type_Code` | `T_Code` | FK → `Role_Type` |
| `Hierarchy_Type_Code` | `T_Code` | |
| `Location_Id` / `Location_Db_Id` | IDs | FK → `Location_Table` |
| `Admin_Location_Id` / `Admin_Location_Db_Id` | IDs | Administrative location |
| `Parent_Role_Id` / `Parent_Role_Db_Id` | IDs | Self-reference — org hierarchy |
| `Role_Commission_Id` / `Role_Commission_Db_Id` | IDs | FK → commission settings |
| `Maintained_By_Db_Id` | `T_Db_Id` | |
| `Machine_Network_Name` | `T_Text` | Device assigned to role |
| `Printer_Network_Name` | `T_Text` | |
| `Default_Booklet_Printer_Network_Name` | `T_Text` | |
| `Default_Duplex_Printer_Network_Name` | `T_Text` | |
| `Role_Deleted_Bln` | `T_Boolean` | |
| `Deleted_Flag` | `T_Delete_Flag` | Soft delete |
| `Company_Tel_Num` | `T_Telephone_Num` | |
| *(+ audit columns)* | |

---

## Role_Table_DT_LOG
Audit log mirror of `Role_Table`.

---

## Role_Type
**PK:** `(Role_Type_Code, Company_Code)`

Defines a type of role and its authority limits.

| Column | Type | Notes |
|--------|------|-------|
| `Role_Type_Code` | `T_Code` NOT NULL | |
| `Company_Code` | `T_Company_Code` NOT NULL | |
| `Active_Directory_Access_Required_Bln` | `T_Boolean` | |
| `Company_Desc` | `T_Short_Text` | |
| `Description` | `T_Short_Text` | |
| `Inherit_Parent_Span_Of_Control_Bln` | `T_Boolean` | |
| `Maintained_On_Local_Nfs_Bln` | `T_Boolean` | |
| `Manage_Agency_Bln` | `T_Boolean` | |
| `Subordinate_Roles_Bln` | `T_Boolean` | |
| `Max_Cash_Holding` | `T_Amount` | Authority limit |
| `Max_Float_Allocation_Authority_Limit` | `T_Amount` | |
| `Max_Lending_Limit` | `T_Amount` | |
| `Max_Write_Back_Authority_Limit` | `T_Amount` | |
| `Max_Write_Off_Authority_Limit` | `T_Amount` | |
| `Generate_Non_Balancing_Exceptions_Daily_Bln` | `T_Boolean` | |
| *(+ audit columns)* | |

---

## Role_Working_Association_Table
**PK:** `(Role_Working_Association_Id, Role_Working_Association_Db_Id)`

Defines working relationships between roles (e.g. a manager can access/work with another role's data).

| Column | Type |
|--------|------|
| `Role_Id` / `Role_Db_Id` | IDs |
| `Associated_Role_Id` / `Associated_Role_Db_Id` | IDs |
| `Deleted_Flag` | `T_Delete_Flag` |
| *(+ audit columns)* | |

---

## Role_Company_Bank_Accounts
**PK:** `(Role_Company_Bank_Accounts_Id, Role_Company_Bank_Accounts_Db_Id)`

Links roles to the company bank accounts they can use.

| Column | Type |
|--------|------|
| `Role_Id` / `Role_Db_Id` | IDs — FK → `Role_Table` |
| `Company_Bank_Account_Id` | `T_Id` |
| `Deleted_Flag` | `T_Delete_Flag` |
| *(+ audit columns)* | |

---

## Location_Table
**PK:** `(Location_Id, Location_Db_Id)`

Physical locations (branches, offices, warehouses).

| Column | Type | Notes |
|--------|------|-------|
| `Location_Id` | `T_Id IDENTITY(1,1)` | |
| `Location_Db_Id` | `T_Db_Id` | |
| `Company_Code` | `T_Company_Code` | |
| `Location_Name` | `T_Name` NOT NULL | |
| `Location_Status_Code` | `T_Code` | |
| `Location_Type_Code` | `T_Code` | |
| `Maintained_By_Db_Id` | `T_Db_Id` | |
| `Transfer_Db_Id` | `T_Db_Id` | |
| `Head_Office_Short_Tel_Num` | `T_Telephone_Num` | |
| `Office_Tel_Num` | `T_Telephone_Num` | |
| `Office_Fax_Num` | `T_Telephone_Num` | |
| `Deleted_Flag` | `T_Delete_Flag` | |
| *(+ audit columns)* | |

---

## Location_Address
**PK:** `(Location_Id, Location_Db_Id)`

Address for a location (one-to-one).

| Column | Type |
|--------|------|
| `Full_Address` | `T_Full_Address` NOT NULL |
| `Short_Address` | `T_Text` NOT NULL |
| `Street_Name` | `T_Address_Line` NOT NULL |
| `Building_Name` | `T_Address_Line` |
| `District` | `T_Address_Line` |
| `Floor_Flat` | `T_Short_Address` |
| `House_Num` | `T_Short_Address` |
| `Postcode` | `T_Postcode` |
| `Region_County` | `T_Address_Line` |
| `Town_City` | `T_Address_Line` |
| `Start_Date` | `T_Date` |
| `End_Date` | `T_Date` |
| `Address_Cleaned_Bln` | `T_Boolean` |
| *(+ audit columns)* | |

---

## Site
**PK:** `Db_Id`

Represents a database instance/site in the distributed system. Each site has a `Db_Id` that appears as the `*_Db_Id` suffix in all entity PKs.

| Column | Type | Notes |
|--------|------|-------|
| `Db_Id` | `T_Db_Id IDENTITY(1,1)` | |
| `Db_Type` | `T_Code` | Central / Peripheral |
| `Location_Id` / `Location_Db_Id` | IDs | FK → `Location_Table` |
| `Maintained_By_Db_Id` | `T_Db_Id` | |
| `System_Down_Bln` | `T_Boolean` | |
| `Technical_Batch_Start_Time` | `T_Time` | |
| `Technical_Batch_End_Time` | `T_Time` | |
| `Dt_Db_Schema_Version` | `T_Short_Text` | Schema version tracking |
| `CLR_Prefix` | `T_Short_Text` | Default `'XX'` |
| `Configuration_Xml_Filename` | `T_Text` | |
| `First_Access_After_Backup_Datetime` | `T_Smalldatetime` | |
| `Last_Backup_Datetime` | `T_Smalldatetime` | |
| *(+ audit columns)* | |

---

## Section_Letter_Conversion_Table
**PK:** `(Role_Id, Role_Db_Id)`

Maps a role (agency section) to an external section letter and rapid extract set number.

| Column | Type |
|--------|------|
| `Role_Id` / `Role_Db_Id` | IDs |
| `External_Section_Letter` | `T_Code` |
| `Rapid_Extract_Set_Num` | `T_Small_Num` |
| `Deleted_Flag` | `T_Delete_Flag` |
| *(+ audit columns)* | |

---

## Stock_Item_Table
**PK:** `(Stock_Item_Id, Stock_Item_Db_Id)`

Individual stock items (passbooks, payment cards, cheque books, etc.).

| Column | Type | Notes |
|--------|------|-------|
| `Stock_Item_Id` | `T_Id IDENTITY(1,1)` | |
| `Company_Code` | `T_Company_Code` | |
| `Stock_Item_Num` | `T_Stock_Num` NOT NULL | Unique item number |
| `Non_Digited_Stock_Item_Num` | `T_Stock_Num` NOT NULL | Without check digit |
| `Stock_Type_Code` | `T_Code` | FK → `Stock_Type` |
| `Stock_Item_Status_Code` | `T_Code` | FK → `Stock_Item_Status` |
| `Inherent_Value` | `T_Amount` NOT NULL | Face value |
| `Value` | `T_Amount` DEFAULT 0 | Current value |
| `Allocation_Date` | `T_Date` | |
| `Responsible_Representative_Id` | `T_Nfs_Person_Id` | Current holder |
| `Pending_Alloc_Representative_Id` | `T_Nfs_Person_Id` | Pending allocation |
| `Pending_Transfer_Representative_Id` | `T_Nfs_Person_Id` | |
| `Transferred_From_Representative_Id` | `T_Nfs_Person_Id` | |
| `Acknowledged_Representative_Id` | `T_Nfs_Person_Id` | |
| `Acknowledged_Datetime` | `T_Smalldatetime` | |
| `Agreement_Id` / `Agreement_Db_Id` | IDs | Linked agreement (if used) |
| `Company_Bank_Account_Id` | `T_Id` | |
| `Cancellation_Date` | `T_Date` | |
| `Cancellation_Reason` | `T_Text` | |
| `Archive_Box_Reference` | `T_Short_Text` | |
| `Booklet_Id` / `Booklet_Db_Id` | IDs | Linked booklet |
| `Deleted_Flag` | `T_Delete_Flag` | |
| *(+ audit columns)* | |

---

## Security_Check_Table
**PK:** `(Security_Check_Id, Security_Check_Db_Id)`

A periodic security check run on an agency, counting active customers.

| Column | Type | Notes |
|--------|------|-------|
| `Agency_Id` | `T_Agency_Id` NOT NULL | |
| `Accounting_Week_Num` | `T_Number` NOT NULL | |
| `Company_Code` | `T_Company_Code` | |
| `Security_Check_Status_Code` | `T_Code` | FK → `Security_Check_Status` |
| `Customer_Count` | `T_Number` | |
| `All_Agency_Customers_Bln` | `T_Boolean` | |
| `Deleted_Flag` | `T_Delete_Flag` | |
| *(+ audit columns)* | |

---

## Receipt_Attestation_Log
**PK:** `(Db_Id, Report_Date, Representative_Id)`

Logs when a representative's receipt attestation report was printed.

| Column | Type |
|--------|------|
| `Db_Id` | `T_Db_Id` |
| `Report_Date` | `T_Date` |
| `Representative_Id` | `T_Nfs_Person_Id` |
| `Report_Printed_Bln` | `T_Boolean` |
| `Report_Serial_Number` | `T_Short_Text` |
| `Sequence_Number` | `T_Small_Num` |
| *(+ audit columns)* | |

---

## Extract_Set_Queue
**PK:** `Extract_Set_Queue_Id`

Queues extract sets to be sent to external systems (e.g. Rapid).

| Column | Type | Notes |
|--------|------|-------|
| `Accounting_Week_Num` | `T_Number` | |
| `Agency_Queue_Id` / `Agency_Queue_Db_Id` | IDs | |
| `Company_Code` | `T_Company_Code` | |
| `Extract_Set_Type` | `T_Code` | |
| `Status` | `T_Code` | Processing status |
| `Last_Action` | `T_Code` | |
| `Site_Db_Id` | `T_Db_Id` | |
| `Rapid_Data_Release_Num` | `T_Text` | |
| `Rapid_Extract_Set_Num` | `T_Number` | |
| `Rapid_Release_Num` | `T_Short_Text` | |
| *(last_updated columns, no Dt_Generation_Id)* | |

---

## Visitation_Performance_Table
**PK:** `(Visitation_Performance_Id, Visitation_Performance_Db_Id)`

Weekly KPI snapshot per agency: arrears visits, CSVs, leads, marketing activity counts.

| Column | Type |
|--------|------|
| `Agency_Id` | `T_Agency_Id` |
| `Accounting_Week_Num` | `T_Number` |
| `Arrears_Brought_Forward` | `T_Small_Num` |
| `Arrears_Created` | `T_Small_Num` |
| `Arrears_Completed` | `T_Small_Num` |
| `Arrears_Cancelled` | `T_Small_Num` |
| `Arrears_Open` | `T_Small_Num` |
| `Arrears_Written_Off` | `T_Small_Num` |
| `CSVs_Brought_Forward` | `T_Small_Num` |
| `CSVs_Created` | `T_Small_Num` |
| `CSVs_Completed` | `T_Small_Num` |
| `Leads_Brought_Forward` | `T_Small_Num` |
| `Leads_Created` | `T_Small_Num` |
| `Leads_Accepted` | `T_Small_Num` |
| `Leads_Rejected` | `T_Small_Num` |
| `Marketing_Created` | `T_Small_Num` |
| `Marketing_Sales` | `T_Small_Num` |
| `Deleted_Flag` | `T_Delete_Flag` |
| *(+ audit columns)* | |

---

## Performance_Product_Figures_Table
**PK:** `(Performance_Product_Figures, Performance_Product_Figures_Db_Id)`

Product-level performance metrics associated with an assessment.

| Column | Type |
|--------|------|
| `Assess_Performance_Id` / `Assess_Performance_Db_Id` | IDs |
| `Product_Type_Code` | `T_Code` |
| `Product_Term_Type_Code` | `T_Code` |
| `Product_Type_Num` | `T_Number` |
| `Product_Type_Value` | `T_Amount` |
| `Deleted_Flag` | `T_Delete_Flag` |
| *(+ audit columns)* | |

---

## backup_Customer_Agency_History_Table

A backup/snapshot copy of `Customer_Agency_History_Table` without a composite `_Db_Id` PK. Contains the same key customer weekly snapshot columns plus birth date, collection %, status, arrears stages, etc.
