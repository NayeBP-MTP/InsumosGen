# CNFS_NFS_DBO — Reference / Lookup Data Tables

All tables in this file follow the same pattern:
- A **type/code** table with the code PK, `Active_Bln`, optional `Sequence_Num`
- A corresponding **`_Desc`** table with `(Code, User_Language_Code)` composite PK for multilingual descriptions

Audit columns (`Dt_Generation_Id`, `Dt_Transaction_Id`, `Dt_Write_Bln`, `Last_Updated_*`) are present on all tables.

---

## Language
**PK:** `Language_Code`
Master list of supported user interface languages.

---

## Title
**PK:** `Title_Code`

| Column | Type |
|--------|------|
| `Title_Code` | `T_Code` NOT NULL |
| `Active_Bln` | `T_Boolean` |
| `Description` | `T_Short_Text` |
| `Language_Code` | `T_Code` |
| `Sequence_Num` | `T_Sequence_Num` |

---

## Marital_Status_Type / Marital_Status_Type_Desc
**PK (type):** `Marital_Status_Type_Code`
**PK (desc):** `(Marital_Status_Type_Code, User_Language_Code)`

---

## Employment_Status_Desc
**PK:** `(Employment_Status_Code, User_Language_Code)`
Multilingual descriptions for employment status codes (no separate type table visible in schema).

---

## Residency_Status_Desc
**PK:** `(Residency_Status_Code, User_Language_Code)`

---

## Customer_Status / Customer_Status_Desc
**PK (type):** `Customer_Status_Code`
**PK (desc):** `(Customer_Status_Code, User_Language_Code)`
Status of a customer account (e.g. Active, Paid Up, Written Off, Deceased).

---

## Agency_Status_Type / Agency_Status_Type_Desc
**PK (type):** `Agency_Status_Type_Code`
**PK (desc):** `(Agency_Status_Type_Code, User_Language_Code)`
Status of an agency (e.g. Active, Closed).

---

## Representative_Status_Desc
**PK:** `(Representative_Status_Code, User_Language_Code)`
Describes representative statuses (e.g. Active, On Leave, Left).

---

## Representative_Type_Desc
**PK:** `(Representative_Type_Code, User_Language_Code)`
Describes representative types (e.g. Agent, Manager, Admin).

---

## Leaving_Reason / Leaving_Reason_Desc
**PK (type):** `Leaving_Reason_Id` (`T_Small_Num IDENTITY(1,1)`)
**PK (desc):** `(Leaving_Reason_Id, User_Language_Code)`

| Column | Type |
|--------|------|
| `Leaving_Reason_Code` | `T_Code` |
| `Active_Bln` | `T_Boolean` |
| `Re_Engagement_Bln` | `T_Boolean` |
| `Sequence_Num` | `T_Sequence_Num` |

---

## Resignation_Reason / Resignation_Reason_Desc
**PK (type):** `Resignation_Reason_Code`
**PK (desc):** `(Resignation_Reason_Code, User_Language_Code)`

| Column | Type |
|--------|------|
| `Resignation_Reason_Code` | `T_Code` |
| `Active_Bln` | `T_Boolean` |
| `Sequence_Num` | `T_Sequence_Num` |
| `Short_Desc` | `T_Short_Text` (in _Desc table) |
| `Description` | `T_Text` (in _Desc table) |

---

## Loan_Reason_Desc
**PK:** `(Loan_Reason_Code, User_Language_Code)`
Reason customer is taking a loan.

---

## Non_Payment / Non_Payment_Desc
**PK (type):** `Non_Payment_Code`
**PK (desc):** `(Non_Payment_Code, User_Language_Code)`
Codes for why a payment was not collected (e.g. Not In, Refused, Holiday).

---

## Agreement_Transaction_Type / Agreement_Transaction_Type_Desc
**PK (type):** `Agreement_Transaction_Type_Code`
**PK (desc):** `(Agreement_Transaction_Type_Code, User_Language_Code)`
Types of financial transactions on agreements (e.g. Payment, Write-Off, Default Charge).

---

## Agreement_Status / Agreement_Status_Desc
**PK (type):** `Agreement_Status_Code`
**PK (desc):** `(Agreement_Status_Code, User_Language_Code)`

---

## Agreement_Issue_Location / Agreement_Issue_Location_Desc
**PK (type):** `Agreement_Issue_Location_Code`
**PK (desc):** `(Agreement_Issue_Location_Code, User_Language_Code)`

---

## Agreement_Source / Agreement_Source_Desc
**PK (type):** `Agreement_Source_Code`
**PK (desc):** `(Agreement_Source_Code, User_Language_Code)`

---

## Element_Type / Element_Type_Desc
**PK (type):** `Element_Type_Code`
**PK (desc):** `(Element_Type_Code, User_Language_Code)`

Element types represent the components of an agreement's financial structure (e.g. Principal, Interest, Insurance Premium, Collection Fee).

---

## Event_Type / Event_Type_Desc
**PK (type):** `Event_Type_Code`
**PK (desc):** `(Event_Type_Code, Language_Code)`
*(See `02_products_events.md` for full `Event_Type` column details)*

---

## Payment_Flexibility_Reason / Payment_Flexibility_Reason_Desc
**PK (type):** `Payment_Flexibility_Reason_Code`
**PK (desc):** `(Payment_Flexibility_Reason_Code, User_Language_Code)`

---

## Receipt_Preference_Type / Receipt_Preference_Type_Desc
**PK (type):** `Receipt_Preference_Type_Code`
**PK (desc):** `(Receipt_Preference_Type_Code, User_Language_Code)`
How customers prefer to receive receipts (e.g. Paper, Electronic).

---

## Stock_Item_Status / Stock_Item_Status_Desc
**PK (type):** `Stock_Item_Status_Code`
**PK (desc):** `(Stock_Item_Status_Code, User_Language_Code)`
Status of a stock item (e.g. In Stock, Allocated, Used, Cancelled).

---

## Stock_Type / Stock_Type_Desc
**PK (type):** `Stock_Type_Code`
**PK (desc):** `(Stock_Type_Code, User_Language_Code)`
Types of stock items (e.g. Passbook, Card, Cheque Book).

| Extra column | `Check_Digited_Bln` — whether the stock number has a check digit |

---

## Security_Check_Status / Security_Check_Status_Desc
**PK (type):** `Security_Check_Status_Code`
**PK (desc):** `(Security_Check_Status_Code, User_Language_Code)`
Status of a security check process on an agency.

---

## Hierarchy_Type_Desc
**PK:** `(Hierarchy_Type_Code, User_Language_Code)`
Describes hierarchy types used in the organisational role structure.

---

## Marketing_Source_Desc
**PK:** `(Marketing_Source_Code, User_Language_Code)`
Source through which a customer was acquired.

---

## Recruitment_Source_Desc
**PK:** `(Recruitment_Source_Code, User_Language_Code)`
Source through which a representative was recruited.

---

## Write_Off_Reason_Desc
**PK:** `(Write_Off_Reason_Code, User_Language_Code)`
Reason for writing off an agreement.

---

## Misbalance_Type_Desc
**PK:** `(Misbalance_Type_Code, Language_Code)`
Types of financial misbalances (cash discrepancies).

---

## Exception_Type_Desc
**PK:** `(Exception_Type_Code, Language_Code)`
Types of system/business exceptions.

---

## Person_Contacted_Desc
**PK:** `(Person_Contacted_Code, Language_Code)`
Who was contacted during a customer visit (e.g. Customer, Spouse, Neighbour).

---

## Personal_Contact_Type_Desc
**PK:** `(Personal_Contact_Type_Code, User_Language_Code)`
Type of personal contact made.

---

## PrePaidCard_Number_Format
**PK:** `(PrePaidCard_Number_Format_Id, PrePaidCard_Number_Format)`
Defines valid number formats for pre-paid cards.

---

## Collect_By_Type_Desc
*(Listed in earlier read sections)*
**PK:** `(Collect_By_Type_Code, User_Language_Code)`
How a collection is made (e.g. Agent Visit, Direct Debit).

---

## Company
**PK:** `Company_Code`

Top-level company definition. All operational data is partitioned by company.

| Column | Type |
|--------|------|
| `Company_Code` | `T_Company_Code` NOT NULL |
| `Active_Bln` | `T_Boolean` |
| *(+ audit columns)* | |

---

## Company_Bank_Account_Table
**PK:** `(Company_Bank_Account_Id, Company_Bank_Account_Db_Id)` *(inferred)*

Stores company bank account details used for disbursements and collections.

---

## Accounting_Week
*(Also present in `Pesos_Offer_Originacion` schema — see `05_app_schemas.md`)*

**PK:** `(Accounting_Week_Num, Company_Code)`

| Column | Type |
|--------|------|
| `Accounting_Week_Num` | `T_Number` NOT NULL |
| `Company_Code` | `T_Company_Code` NOT NULL |
| `End_Date` | `T_Date` NOT NULL |
| `Month_Code` | `T_Code` NOT NULL |
| `Start_Date` | `T_Date` NOT NULL |
| *(+ audit columns)* | |
