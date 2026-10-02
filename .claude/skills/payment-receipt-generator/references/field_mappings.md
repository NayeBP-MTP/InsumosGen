# Field Mappings Reference

Complete field reference for all tables involved in payment receipt generation.

## Table of Contents
1. [Agreement_Table](#agreement_table)
2. [Agreement_Transaction_Table](#agreement_transaction_table)
3. [Agreement_Transaction_Receipt_Table](#agreement_transaction_receipt_table)
4. [Common Patterns](#common-patterns)

---

## Agreement_Table

### Fields That Change Per Contract

| Field | Description | Example | Notes |
|-------|-------------|---------|-------|
| Agreement_Id | Unique contract ID | 134 | Sequential, get next available |
| Agreement_Num | Contract number | 240010470 | Format varies, ask user or generate |
| Customer_Id | Customer identifier | 2075042613006 | Must exist in Customer_Table |
| Issue_Date | Contract issue date | '2026-03-03 00:00:00.000' | User-specified or current date |
| Creation_Date | Record creation date | '2026-03-03 00:00:00.000' | Usually same as Issue_Date |
| First_Payment_Due_Date | First payment due | '2026-03-03 00:00:00.000' | Usually 1 week after issue |
| Actual_Paid_Up_Date | Paid off date | '2026-03-07 00:00:00.000' | Only for liquidated (PU status) |
| Actual_Paid_Up_Week | Week paid off | 202609 | Only for liquidated (YYYYWW) |
| Creation_Week | Week created | 202609 | Format: YYYYWW |
| Issue_Value | Principal amount | 0.000000 | Loan amount from user |
| First_Instalment_Value | First payment | 378.750000 | From tabla de cargo |
| Regular_Instalment_Value | Regular payment | 378.750000 | From tabla de cargo |
| Final_Instalment_Value | Final payment | 378.750000 | From tabla de cargo |
| Total_Amount_Payable | Total to pay | 4545.000000 | Sum of all installments |
| Product_Version_Id | Product type | 112 | 112=12wk, 106=42wk, 131=65wk |
| Agreement_Status_Code | Status | 'AC' or 'PU' | AC=Active, PU=Paid Up |
| Issuing_Representative_Id | Rep who issued | 1001 | From user input |
| Last_Updated_Datetime | Last update | '2026-03-03 00:00:00.000' | Current timestamp |

### Fields That Remain Constant

| Field | Value | Notes |
|-------|-------|-------|
| Agreement_Db_Id | 2000 | Always 2000 |
| Absolute_Arrears | 0.000000 | Always 0 |
| Cancellation_Date | NULL | NULL unless cancelled |
| Cancellation_Week | NULL | NULL unless cancelled |
| Cancellation_Value | NULL | NULL unless cancelled |
| Cancelled_By_Representative_Id | '2026-02-04 00:00:00.000' | Placeholder date |
| Company_Code | N'MEX' | Always MEX |
| Customer_Type_Code_At_Issue | N'1 ' | Always '1 ' (with space) |
| Deleted_Flag | 0 | Always 0 |
| Early_Settlement_Bln | 1 | Always 1 |
| Early_Settlement_Rebate_Value | 1000.000000 | Standard value |
| Early_Settlement_Rebate_Contra_Value | 0.000000 | Always 0 |
| Instalment_Periods_To_Date | 7 | Standard value |
| Is_Adjustment_Bln | 0 | Always 0 |
| Late_Issue_Bln | 0 | Always 0 |
| Linked_Agreement_Number | NULL | NULL unless refinance |
| Loan_Reason_Code | N'1 ' | Always '1 ' |
| Normal_Due_Day_In_Month | 15 | Always 15 |
| Number_Of_Default_Charge_Applications_To_Date | 0 | Always 0 |
| Outstanding_Balance | 0.000000 | Always 0 |
| Outstanding_Default_Charge | 0.000000 | Always 0 |
| Product_Category_Code | N'1 ' | Always '1 ' |
| Product_Version_Db_Id | 2000 | Always 2000 |
| Third_Party_Retailer_Event_Code | N'1 ' | Always '1 ' |
| Transferred_Bln | 0 | Always 0 |
| Settlement_Balance | 1893.750000 | Calculate or use standard |
| Written_Back_Value | 0.000000 | Always 0 |
| Written_Off_Date | NULL | NULL unless written off |
| Written_Off_Value | 0.000000 | Always 0 |
| Written_Off_Week | NULL | NULL unless written off |
| Dt_Write_Bln | 0 | Always 0 |
| Last_Updated_Id | 1001 | Standard user ID |
| Last_Updated_Timestamp | 0x00000000004ABD0A | Standard timestamp |
| Annual_Interest_Rate | 10.5000000000000 | Fixed at 10.5% |
| Prevailing_Principal | 0.000000 | Always 0 |
| Company_Rate_Cap_Id | 1 | Always 1 |
| Final_Instalment_Value_At_Issue | 378.750000 | Same as Final_Instalment_Value |
| First_Instalment_Value_At_Issue | 378.750000 | Same as First_Instalment_Value |
| Regular_Instalment_Value_At_Issue | 378.750000 | Same as Regular_Instalment_Value |
| Total_Amount_Payable_At_Issue | 4545.000000 | Same as Total_Amount_Payable |
| Customer_Repayment_Account_Num | N'ACC123456789' | Standard account |
| Chosen_Payment_Due_Day | 15 | Always 15 |
| Early_Settlement_Charge_Applied | 0.000000 | Always 0 |
| Refinancing_Agreement_Id | NULL | NULL unless refinance |
| Refinancing_Agreement_Db_Id | NULL | NULL unless refinance |
| Refinanced_Week | NULL | NULL unless refinance |
| Reporting_Week_Num | NULL | NULL |
| Agreement_Form_Corrected_Bln | 0 | Always 0 |
| Customer_Business_Id | NULL | NULL |
| Customer_Business_Db_Id | NULL | NULL |
| Credit_Check_Reference | N'CREDITCHK001' | Standard reference |
| Codebtor_Id | NULL | NULL |
| Finance_Absolute_Arrears | 0.000000 | Always 0 |
| Agreement_Source_Code | N'1 ' | Always '1 ' |
| Agreement_Issue_Location_Code | N'1 ' | Always '1 ' |
| Promotion_Reason_Code | N'1 ' | Always '1 ' |

### Fields to Auto-Generate

| Field | Type | Notes |
|-------|------|-------|
| Dt_Generation_Id | GUID | Generate new GUID |
| Global_Transaction_Key | GUID | Generate new GUID |

---

## Agreement_Transaction_Table

### Fields That Change Per Transaction

| Field | Description | Example | Notes |
|-------|-------------|---------|-------|
| Agreement_Transaction_Id | Transaction ID | 2000385 | Sequential, get next available |
| Accounting_Week_Num | Week number | 202614 | Format: YYYYWW |
| Agency_Id | Branch ID | 2075000000335 | From user or agreement |
| Agreement_Id | Contract ID | 103 | Links to Agreement_Table |
| Agreement_Transaction_Type_Code | Type | N'HC' or N'OP' | Ask user/QA preference |
| Product_Version_Id | Product type | 112 | 112=12wk, 106=42wk, 131=65wk |
| Reference_Text | Description | N'Pago acuerdo 5-3' | Descriptive text |
| Representative_Id | Rep ID | 2075000343335 | From user input |
| Value | Payment amount | 378.750000 | From tabla de cargo |
| Transaction_Date | Payment date | '2026-04-06 10:00:00.000' | Weekly intervals |
| Creation_Date | Created date | '2026-04-06 10:00:00.000' | Same as Transaction_Date |

### Fields That Remain Constant

| Field | Value | Notes |
|-------|-------|-------|
| Agreement_Transaction_Db_Id | 102 | Always 102 |
| Agreement_Security_Check_Balance_Db_Id | NULL | Always NULL |
| Agreement_Security_Check_Balance_Id | NULL | Always NULL |
| Agreement_Db_Id | 2000 | Always 2000 |
| Balanced_Bln | 1 | Always 1 |
| Committed_Bln | 1 | Always 1 |
| Company_Code | N'MEX' | Always MEX |
| Deleted_Flag | 0 | Always 0 |
| Money_Balancing_Bln | 0 | Always 0 |
| Non_Payment_Code | NULL | Always NULL |
| Original_Representative_Id | NULL | Always NULL |
| Product_Version_Db_Id | 2000 | Always 2000 |
| Write_Off_Reason_Code | NULL | Always NULL |
| Dt_Write_Bln | 0 | Always 0 |
| Last_Updated_Datetime | '2024-03-24 10:00:00.000' | Standard timestamp |
| Last_Updated_Id | 5001 | Always 5001 |
| Last_Updated_Timestamp | 0x00000000004CA486 | Standard value |
| Effective_Accounting_Week_Num | 50 | Always 50 |
| Unsigned_Bln | 0 | Always 0 |
| Undated_Bln | 0 | Always 0 |
| Amount_That_Cleared_Default_Charges | 0.000000 | Always 0 |
| Committed_Date | NULL | Always NULL |
| Balance_Id | NULL | Always NULL |
| Balance_Db_Id | NULL | Always NULL |
| Default_Charge_Rule_Code | NULL | Always NULL |
| Committed_By_Representative_Id | 1 | Always 1 |
| Allow_Updates_Bln | 1 | Always 1 |
| External_User_Id | NULL | Always NULL |

### Fields to Auto-Generate

| Field | Type | Notes |
|-------|------|-------|
| Dt_Generation_Id | Integer | Always 1 |
| Dt_Transaction_Id | GUID | Generate new GUID |
| Global_Transaction_Key | GUID | Generate new GUID |

---

## Agreement_Transaction_Receipt_Table

### Fields That Change Per Receipt

| Field | Description | Example | Notes |
|-------|-------------|---------|-------|
| Agreement_Transaction_Receipt_Id | Receipt ID | 410768 | Sequential, get next available |
| Agreement_Transaction_Id | Transaction ID | 390980 | From corresponding transaction |
| Receipt_Reference | Reference | N'RC-390980' | Format: 'RC-{Transaction_Id}' |
| Transaction_Date | Receipt date | '2026-04-06 10:00:00.000' | Same as transaction date |
| Creation_Date | Created date | '2026-04-06 10:00:00.000' | Same as transaction date |
| Validation_Date | Validated date | NULL | NULL or validation timestamp |
| Representative_Id | Rep ID | 2075000343335 | From user input |

### Fields That Remain Constant

| Field | Value | Notes |
|-------|-------|-------|
| Agreement_Transaction_Receipt_Db_Id | 102 | Always 102 |
| Agreement_Transaction_Db_Id | 102 | Always 102 (composite key) |
| Extracted | 0 | Always 0 |
| Deleted_Flag | 0 | Always 0 |
| Dt_Generation_Id | 0 | Always 0 |
| Dt_Write_Bln | 0 | Always 0 |
| Last_Updated_Datetime | '2025-10-15 19:52:00.000' | Standard timestamp |
| Last_Updated_Id | 5002 | Always 5002 |
| Last_Updated_Timestamp | 0x00000000004CA41E | Standard value |
| Stock_Item_Id | NULL | Always NULL |
| Stock_Item_Db_Id | NULL | Always NULL |
| Previously_Committed_Transaction_Bln | 0 | Always 0 |
| Receipt_Type_Code | N'RCT' | Always 'RCT' |
| Undated_Bln | 0 | Always 0 |
| Unsigned_Bln | 0 | Always 0 |
| Validated_Bln | 0 | Always 0 |
| ReceiptHash | N' ' | Empty or generate GUID |

### Fields to Auto-Generate

| Field | Type | Notes |
|-------|------|-------|
| Dt_Transaction_Id | GUID | Generate new GUID |
| ReceiptHash | GUID or Empty | Can be ' ' or new GUID |

---

## Common Patterns

### Date Formats
- SQL datetime: `'2026-04-06 10:00:00.000'`
- Week format: `YYYYWW` (e.g., 202614 = year 2026, week 14)

### GUID Generation
Generate new GUIDs in format: `XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX`

Example: `'D3C955D0-8595-4F99-93BA-B10869AD2438'`

### String Fields with Trailing Space
Some code fields have trailing space: `N'1 '` (note the space before closing quote)

Fields with this pattern:
- Customer_Type_Code_At_Issue
- Loan_Reason_Code
- Product_Category_Code
- Third_Party_Retailer_Event_Code
- Agreement_Source_Code
- Agreement_Issue_Location_Code
- Promotion_Reason_Code

### Decimal Precision
All monetary values use 6 decimal places: `378.750000`

### Product Version Mapping
- 12 weeks → Product_Version_Id = 112
- 42 weeks → Product_Version_Id = 106
- 65 weeks → Product_Version_Id = 131

### Composite Key Relationship
Agreement_Transaction and Agreement_Transaction_Receipt are linked by:
- Agreement_Transaction_Id (must match)
- Agreement_Transaction_Db_Id (always 102 in both tables)

### Branch Code Extraction
Branch code = first 4 digits of Agency_Id
- Agency_Id: 2075000000335 → Branch: 2075
- Agency_Id: 2093000000111 → Branch: 2093
