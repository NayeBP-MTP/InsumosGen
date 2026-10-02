# CNFS_NFS_DBO — Core Operational Entities

## Agreement_Table
**PK:** `(Agreement_Id, Agreement_Db_Id)`

The central loan/agreement record. One row per loan agreement.

| Column | Type | Notes |
|--------|------|-------|
| `Agreement_Id` | `T_Id IDENTITY(1,1)` | Auto-increment PK |
| `Agreement_Db_Id` | `T_Db_Id` | Site DB identifier |
| `Absolute_Arrears` | `T_Amount` | |
| `Actual_Paid_Up_Date` | `T_Date` | |
| `Actual_Paid_Up_Week` | `T_Number` | |
| `Agreement_Num` | `T_Agreement_Num` | Human-readable agreement number |
| `Agreement_Status_Code` | `T_Code` | FK → `Agreement_Status` |
| `Cancellation_Date` | `T_Date` | |
| `Cancellation_Week` | `T_Number` | |
| `Cancellation_Value` | `T_Amount` | |
| `Cancelled_By_Representative_Id` | `T_Nfs_Person_Id` | |
| `Company_Code` | `T_Company_Code` | FK → `Company` |
| `Creation_Date` | `T_Datetime` | |
| `Creation_Week` | `T_Number` | |
| `Customer_Id` | `T_Nfs_Person_Id` | FK → `Customer_Table` |
| `Customer_Type_Code_At_Issue` | `T_Code` | |
| `Early_Settlement_Bln` | `T_Boolean` | |
| `Early_Settlement_Rebate_Value` | `T_Amount` | |
| `Final_Instalment_Value` | `T_Amount` | |
| `First_Instalment_Value` | `T_Amount` | |
| `First_Payment_Due_Date` | `T_Date` | |
| `Issue_Date` | `T_Date` | |
| `Issue_Value` | `T_Amount` | |
| `Issuing_Representative_Id` | `T_Nfs_Person_Id` | FK → `Representative_Table` |
| `Outstanding_Balance` | `T_Amount` | |
| `Product_Version_Id` | `T_Id` | FK → `Product_Version_Table` |
| `Product_Version_Db_Id` | `T_Db_Id` | |
| `Regular_Instalment_Value` | `T_Amount` | |
| `Total_Amount_Payable` | `T_Amount` | |
| `Annual_Interest_Rate` | `T_Large_Percentage` | |
| `Refinancing_Agreement_Id` | `T_Id` | Self-reference for refinancing |
| `Agreement_Source_Code` | `T_Code` | FK → `Agreement_Source` |
| `Agreement_Issue_Location_Code` | `T_Code` | FK → `Agreement_Issue_Location` |
| `Codebtor_Id` | `T_Nfs_Person_Id` | |
| `Deleted_Flag` | `T_Delete_Flag` | Soft delete |
| *(+ standard audit columns)* | | |

---

## Agreement_Table_DT_LOG
Mirror/audit log of `Agreement_Table`. Same columns, no IDENTITY on PK. Used for distributed transaction logging.

---

## Agreement_Transaction_Table
**PK:** `(Agreement_Transaction_Id, Agreement_Transaction_Db_Id)`

Transactions (payments, adjustments, etc.) applied against an agreement.

| Column | Type | Notes |
|--------|------|-------|
| `Agreement_Transaction_Id` | `T_Id IDENTITY(1,1)` | |
| `Agreement_Transaction_Db_Id` | `T_Db_Id` | |
| `Agreement_Id` | `T_Id` | FK → `Agreement_Table` |
| `Agreement_Db_Id` | `T_Db_Id` | |
| `Agreement_Transaction_Type_Code` | `T_Code` | FK → `Agreement_Transaction_Type` |
| `Collection_Week` | `T_Number` | |
| `Company_Code` | `T_Company_Code` | |
| `Creation_Date` | `T_Datetime` | |
| `Effective_Date` | `T_Date` | |
| `Issuing_Representative_Id` | `T_Nfs_Person_Id` | |
| `Value` | `T_Amount` | |
| `Deleted_Flag` | `T_Delete_Flag` | |
| *(+ audit columns)* | | |

---

## Agreement_Transaction_Table_DT_LOG
Audit log mirror of `Agreement_Transaction_Table`.

---

## Agreement_Transaction_Type
**PK:** `Agreement_Transaction_Type_Code`

Reference table for transaction type codes.

| Column | Type |
|--------|------|
| `Agreement_Transaction_Type_Code` | `T_Code` NOT NULL |
| `Active_Bln` | `T_Boolean` |
| `Credit_Indicator_Bln` | `T_Boolean` |
| `Sequence_Num` | `T_Sequence_Num` |
| *(+ audit columns)* | |

---

## Agreement_Transaction_Type_Desc
**PK:** `(Agreement_Transaction_Type_Code, User_Language_Code)`

Multilingual descriptions for transaction types.

---

## Agreement_Status
**PK:** `Agreement_Status_Code`

| Column | Type |
|--------|------|
| `Agreement_Status_Code` | `T_Code` NOT NULL |
| `Active_Bln` | `T_Boolean` |
| `Sequence_Num` | `T_Sequence_Num` |
| *(+ audit columns)* | |

---

## Agreement_Status_Desc
**PK:** `(Agreement_Status_Code, User_Language_Code)`
Multilingual descriptions.

---

## Agreement_Issue_Location
**PK:** `Agreement_Issue_Location_Code`
Reference table for where an agreement was issued.

---

## Agreement_Issue_Location_Desc
**PK:** `(Agreement_Issue_Location_Code, User_Language_Code)`

---

## Agreement_Source
**PK:** `Agreement_Source_Code`
Reference table for agreement origination channel.

---

## Agreement_Source_Desc
**PK:** `(Agreement_Source_Code, User_Language_Code)`

---

## Customer_Table
**PK:** `Customer_Id`

The core customer record.

| Column | Type | Notes |
|--------|------|-------|
| `Customer_Id` | `T_Nfs_Person_Id` NOT NULL | PK |
| `Agency_Id` | `T_Agency_Id` | Current agency |
| `Birth_Date` | `T_Date` | |
| `Collection_Pct` | `T_Percentage` | |
| `Company_Code` | `T_Company_Code` | |
| `Customer_Status_Code` | `T_Code` | FK → `Customer_Status` |
| `Deceased_Bln` | `T_Boolean` | |
| `Deleted_Flag` | `T_Delete_Flag` | |
| `Display_Name` | nvarchar(510) | Computed full name |
| `Email_Address` | nvarchar(100) | |
| `Employment_Status_Code` | `T_Code` | |
| `Forename` | nvarchar(80) | |
| `Forename_Soundex` | `T_Soundex` | Phonetic search |
| `Gender_Code` | `T_Code` | |
| `Home_Tel_Num` | nvarchar(40) | |
| `Marketing_Source_Code` | `T_Code` | |
| `Mobile_Tel_Num` | nvarchar(40) | |
| `Num_Of_Consecutive_Misses` | `T_Small_Num` | Consecutive missed payments |
| `Pin` | nvarchar(40) | |
| `Print_On_Collecting_List_Bln` | `T_Boolean` | |
| `Repayment_Frequency_Code` | `T_Code` | |
| `Surname` | nvarchar(80) | |
| `Surname_Soundex` | `T_Soundex` | |
| `Title_Code` | `T_Code` | |
| `Depersonalisation_Date` | `T_Date` | GDPR depersonalisation |
| `Depersonalisation_Reason_Code` | `T_Code` | |
| *(+ audit columns)* | | |

---

## Customer_Table_DT_LOG
Audit log mirror of `Customer_Table`.

---

## Customer_Address
**PK:** `Customer_Id`

One-to-one address for a customer.

| Column | Type |
|--------|------|
| `Customer_Id` | `T_Nfs_Person_Id` NOT NULL |
| `Address_Cleaned_Bln` | `T_Boolean` |
| `Building_Name` | `T_Address_Line` |
| `District` | `T_Address_Line` |
| `Floor_Flat` | `T_Short_Address` |
| `Full_Address` | `T_Full_Address` NOT NULL |
| `House_Num` | `T_Short_Address` |
| `Postcode` | `T_Postcode` |
| `Region_County` | `T_Address_Line` |
| `Short_Address` | `T_Text` NOT NULL |
| `Street_Name` | `T_Address_Line` NOT NULL |
| `Town_City` | `T_Address_Line` |
| *(+ audit columns)* | |

---

## Customer_Address_History_Table
**PK:** `(Customer_Address_History_Id, Customer_Address_History_Db_Id)`

Tracks historical addresses for customers.

| Column | Type |
|--------|------|
| `Customer_Address_History_Id` | `T_Id IDENTITY(1,1)` |
| `Customer_Address_History_Db_Id` | `T_Db_Id` |
| `Customer_Id` | `T_Nfs_Person_Id` |
| `Start_Date` | `T_Date` |
| `End_Date` | `T_Date` |
| `Full_Address` | `T_Full_Address` |
| `Postcode` | `T_Postcode` |
| *(all address fields)* | |
| *(+ audit columns)* | |

---

## Customer_Agency_History_Table
**PK:** `(Customer_Agency_History_Id, Customer_Agency_History_Db_Id)`

Tracks which agency a customer has been assigned to over time, along with weekly snapshot data.

| Column | Type | Notes |
|--------|------|-------|
| `Customer_Agency_History_Id` | `T_Id IDENTITY(1,1)` | |
| `Agency_Id` | `T_Agency_Id` | |
| `Accounting_Week_Num` | `T_Number` | |
| `Customer_Id` | `T_Nfs_Person_Id` | |
| `Customer_Status_Code` | `T_Code` | |
| `Collection_Pct` | `T_Percentage` | |
| `Doc_Arrears_Stage` | `T_Small_Num` | |
| `Loan_Arrears_Stage` | `T_Small_Num` | |
| `Num_Of_Consecutive_Misses` | `T_Small_Num` | |
| `Finance_Loan_Arrears_Stage` | `T_Small_Num` | |
| `Finance_Num_Of_Consecutive_Misses` | `T_Small_Num` | |
| *(+ audit columns)* | |

---

## Customer_Business_Table
**PK:** `(Customer_Business_Id, Customer_Business_Db_Id)`

Business/employer information linked to a customer.

| Column | Type |
|--------|------|
| `Customer_Business_Id` | `T_Id IDENTITY(1,1)` |
| `Customer_Id` | `T_Nfs_Person_Id` |
| `Business_Name` | `T_Name` |
| `Employer_Tel_Num` | `T_Telephone_Num` |
| `Occupation` | `T_Short_Text` |
| `Employment_Status_Code` | `T_Code` |
| `Deleted_Flag` | `T_Delete_Flag` |
| *(+ audit columns)* | |

---

## Customer_Contact_Table
**PK:** `(Customer_Contact_Id, Customer_Contact_Db_Id)`

Logs contact/visit attempts with customers.

| Column | Type | Notes |
|--------|------|-------|
| `Customer_Contact_Id` | `T_Id IDENTITY(1,1)` | |
| `Agreement_Id` | `T_Id` | Optional link to agreement |
| `Agency_Id` | `T_Agency_Id` | |
| `Contact_Type_Code` | `T_Code` | |
| `Contact_Date` | `T_Date` | |
| `Collection_Week` | `T_Number` | |
| `Customer_Id` | `T_Nfs_Person_Id` | |
| `Representative_Id` | `T_Nfs_Person_Id` | |
| `Non_Payment_Code` | `T_Code` | |
| `Deleted_Flag` | `T_Delete_Flag` | |
| *(+ audit columns)* | |

---

## Customer_Lead_Table
**PK:** `Customer_Lead_Id`

Prospective customers / leads before they become full customers.

| Column | Type | Notes |
|--------|------|-------|
| `Customer_Lead_Id` | `T_Nfs_Person_Id` NOT NULL | PK |
| `Company_Code` | `T_Company_Code` | FK → `Company` |
| `Customer_Id` | `T_Nfs_Person_Id` | Nullable — set when converted |
| `Customer_Lead_Status_Code` | `T_Code` | |
| `Display_Name` | `T_Text` | |
| `Forename` | `T_Name` | |
| `Surname` | `T_Name` | |
| `Lead_Creation_Date` | `T_Date` | |
| `Marketing_Source_Code` | `T_Code` | |
| `Role_Id` | `T_Id` | Assigned agent role |
| `Role_Db_Id` | `T_Db_Id` | |
| `Depersonalisation_Date` | `T_Date` | |
| *(+ audit columns)* | |

---

## Customer_Status
**PK:** `Customer_Status_Code`

| Column | Type |
|--------|------|
| `Customer_Status_Code` | `T_Code` NOT NULL |
| `Active_Bln` | `T_Boolean` |
| `Sequence_Num` | `T_Sequence_Num` |
| *(+ audit columns)* | |

---

## Customer_Status_Desc
**PK:** `(Customer_Status_Code, User_Language_Code)`
Multilingual descriptions for customer status codes.

---

## Agency_Table
**PK:** `(Agency_Id, Agency_Db_Id)`

Represents a field agency/section.

| Column | Type | Notes |
|--------|------|-------|
| `Agency_Id` | `T_Agency_Id IDENTITY(1,1)` | |
| `Agency_Db_Id` | `T_Db_Id` | |
| `Agency_Status_Type_Code` | `T_Code` | |
| `Company_Code` | `T_Company_Code` | |
| `Deleted_Flag` | `T_Delete_Flag` | |
| `Location_Id` | `T_Id` | FK → `Location_Table` |
| `Location_Db_Id` | `T_Db_Id` | |
| `Role_Id` | `T_Id` | Assigned manager role |
| `Role_Db_Id` | `T_Db_Id` | |
| *(+ audit columns)* | |

---

## Agency_Status_Type
**PK:** `Agency_Status_Type_Code`
Reference table for agency statuses (e.g. Active, Closed).

---

## Agency_Status_Type_Desc
**PK:** `(Agency_Status_Type_Code, User_Language_Code)`

---

## Representative_Table
**PK:** `Representative_Id`

Field agents and staff members.

| Column | Type | Notes |
|--------|------|-------|
| `Representative_Id` | `T_Nfs_Person_Id` NOT NULL | PK |
| `Agency_Id` | `T_Agency_Id` | Current agency |
| `Birth_Date` | `T_Date` | |
| `Company_Code` | `T_Company_Code` | |
| `Creation_Date` | `T_Date` | |
| `Deleted_Flag` | `T_Delete_Flag` | |
| `Display_Name` | nvarchar(510) | |
| `Email_Address` | nvarchar(100) | |
| `Forename` | nvarchar(80) | |
| `Forename_Soundex` | `T_Soundex` | |
| `Gender_Code` | `T_Code` | |
| `Home_Tel_Num` | nvarchar(40) | |
| `Leaving_Date` | `T_Date` | |
| `Leaving_Reason_Id` | `T_Small_Num` | FK → `Leaving_Reason` |
| `Maintained_By_Db_Id` | `T_Db_Id` | |
| `Max_Cash_Holding` | `T_Amount` | Authority limit |
| `Max_Lending_Limit` | `T_Amount` | |
| `Max_Write_Off_Authority_Limit` | `T_Amount` | |
| `Mobile_Tel_Num` | nvarchar(40) | |
| `Representative_Status_Code` | `T_Code` | FK → `Representative_Status` |
| `Representative_Type_Code` | `T_Code` | FK → `Representative_Type` |
| `Start_Date` | `T_Date` | |
| `Surname` | nvarchar(80) | |
| `Surname_Soundex` | `T_Soundex` | |
| `Suspended_Bln` | `T_Boolean` | |
| `Depersonalisation_Date` | `T_Date` | GDPR |
| `Can_Be_Re_Engaged_Bln` | `T_Boolean` | |
| `Is_Senior_Agent` | `T_Boolean` | |
| *(+ audit columns)* | |

---

## Representative_Table_DT_LOG
Audit log mirror of `Representative_Table`.

---

## Representative_Address
**PK:** `Representative_Id`
One-to-one address record for a representative (same structure as `Customer_Address`).

---

## Representative_Role_Table
**PK:** `(Representative_Role_Id, Representative_Role_Db_Id)`

Links a representative to a role (many-to-many; a rep can hold multiple roles).

| Column | Type | Notes |
|--------|------|-------|
| `Representative_Role_Id` | `T_Id IDENTITY(1,1)` | |
| `Representative_Id` | `T_Nfs_Person_Id` | FK → `Representative_Table` |
| `Role_Id` | `T_Id` | FK → `Role_Table` |
| `Role_Db_Id` | `T_Db_Id` | |
| `Default_Location_Bln` | `T_Boolean` | |
| `Secondment_Bln` | `T_Boolean` | |
| `Deleted_Flag` | `T_Delete_Flag` | |
| *(+ audit columns)* | |

---

## Representative_Role_Table_DT_LOG
Audit log mirror.

---

## Third_Party_Request_Table
**PK:** `(Third_Party_Request_Id, Third_Party_Request_Db_Id)`

Records requests for customer data from third parties (e.g. solicitors).

| Column | Type |
|--------|------|
| `Third_Party_Request_Id` | `T_Id IDENTITY(1,1)` |
| `Customer_Id` | `T_Nfs_Person_Id` (nullable) |
| `Customer_Lead_Id` | `T_Nfs_Person_Id` (nullable) |
| `Representative_Id` | `T_Nfs_Person_Id` (nullable) |
| `Third_Party_Address` | `T_Full_Address` |
| `Third_Party_Name` | `T_Full_Name` |
| `Third_Party_Request_Date` | `T_Date` |
| `Third_Party_Scope` | `T_Long_Text` |
| `Deleted_Flag` | `T_Delete_Flag` |
| *(+ audit columns)* | |

---

## Exception_Table
**PK:** `(Exception_Id, Exception_Db_Id)`

Audit/exception log for business rule violations and anomalies. Contains many optional columns covering various exception types (arrears, stock, misbalance, document, etc.).

Key columns:
- `Exception_Type` — type code for the kind of exception
- `Include_In_Exception_Count_Bln` — whether this counts toward exception KPIs
- `Occurrence_Datetime` — when it occurred
- Many nullable context fields (agreement, customer, agency, stock, etc.)

---

## Exception_Type_Desc
**PK:** `(Exception_Type_Code, Language_Code)`
Multilingual descriptions for exception types.

---

## Marketing_Message_History_Table
**PK:** `(Marketing_Message_History_Db_Id, Marketing_Message_History_Id)`

Records marketing messages/offers shown to customers at a given week.

| Column | Type |
|--------|------|
| `Customer_Id` | `T_Nfs_Person_Id` |
| `Accounting_Week_Num` | `T_Number` |
| `Company_Code` | `T_Company_Code` |
| `Sales_Message_Code` | `T_Code` |
| `Sales_Offer_Type_Code` | `T_Code` |
| `Sales_Offer_Value` | `T_Amount` |
| `Maximum_Rate` | `T_Amount` |
| `Sales_Grade_Code` | `T_Code` |
| `Sales_Message_Text` | `T_Text` |
| `Customer_Facing_Sales_Message_Text` | `T_Text` |
| `Deleted_Flag` | `T_Delete_Flag` |
| *(+ audit columns)* | |
