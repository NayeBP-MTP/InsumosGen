---
name: payment-receipt-generator
description: Generate payment receipts (comprobantes de pago) for contracts in the CNFS_uat.NFS_DBO database. Use this skill when the user wants to create payment transactions, generate receipts for contracts, create test payment data, insert transaction records with receipts, or manage payment comprobantes for existing or new contracts. This skill handles the complete flow from customer to contract to transactions to receipts, including proper relationship management and rollback scripts.
---

# Payment Receipt Generator

This skill generates SQL INSERT statements for payment receipts (comprobantes de pago) in the CNFS_uat.NFS_DBO database system. It handles the complete data flow: Customer → Agreement (Contract) → Agreement_Transaction → Agreement_Transaction_Receipt.

## When to Use This Skill

Use this skill when the user needs to:
- Generate payment receipts (comprobantes de pago) for existing or new contracts
- Create transaction records with their corresponding receipts
- Set up test payment data for QA purposes
- Create contracts with payment history (liquidated or in-progress)
- Generate SQL with automatic rollback scripts

## Database Structure Overview

The payment receipt system follows this hierarchy:

```
Customer_Table (Customer_Id)
    ↓
Agreement_Table (Agreement_Id, Customer_Id)
    ↓
Agreement_Transaction_Table (Agreement_Transaction_Id, Agreement_Id)
    ↓
Agreement_Transaction_Receipt_Table (Agreement_Transaction_Receipt_Id, Agreement_Transaction_Id)
```

**Key Relationship:** Agreement_Transaction and Agreement_Transaction_Receipt have a 1:1 relationship using the composite key: `(Agreement_Transaction_Id, Agreement_Transaction_Db_Id)`

## User Input Requirements

Before generating the SQL, gather this information from the user:

### Required Information
1. **Customer_Id** - If working with existing customer (format: 2075042613005)
2. **Agreement_Id** - If working with existing contract
3. **Number of payments** - How many transaction/receipt pairs to generate
4. **Contract status** - Liquidated (PU) or In-Progress
   - Liquidated: payments = term (e.g., 12/12, 42/42, 65/65)
   - In-Progress: payments < term (e.g., 5/12, 20/42, 30/65)
5. **Contract term** - 12, 42, or 65 weeks
6. **Transaction type** - HC or OP (ask QA for their preference)
7. **Loan amount** - Principal amount for the contract
8. **Agency_Id** - Branch where contract was issued (e.g., 2075000000335)
9. **Representative_Id** - Representative who issued the contract

### Optional Information
- **Agreement_Num** - Contract number (if specific format needed)
- **Issue_Date** - When contract was issued (defaults to current date)
- **Payment dates** - Specific dates for each payment (defaults to weekly intervals)

## Generation Workflow

Follow these steps to generate the complete SQL:

### Step 1: Validate Input

Before generating SQL, validate:
- Contract term is one of: 12, 42, or 65 weeks
- Number of payments ≤ contract term
- For liquidated contracts: number of payments = contract term
- Loan amount is reasonable for the term

### Step 2: Calculate Payment Amounts

Read the tabla de cargo reference file to get the correct payment amounts:

```
references/tabla_de_cargo.md
```

The payment structure varies by term and payment number:
- **First payment** (Cuota Semana 1)
- **Regular payments** (Cuota Semana 2 a N)
- **Final payment** (if different)

**CRITICAL VALIDATION:** Verify that:
- `First_Instalment_Value` matches tabla de cargo "Cuota Semana 1"
- `Regular_Instalment_Value` matches tabla de cargo "Cuota Semana 2 a N"
- `Total_Amount_Payable` = sum of all installments
- Transaction `Value` field matches the corresponding installment amount

### Step 3: Determine Product_Version_Id

Map the contract term to Product_Version_Id:
- 12 weeks → Product_Version_Id = 112
- 42 weeks → Product_Version_Id = 106
- 65 weeks → Product_Version_Id = 131

### Step 4: Generate Agreement (if needed)

If creating a new contract, generate INSERT for `Agreement_Table` with:

**Key fields to calculate:**
- `Agreement_Num` - Contract number (format varies, ask user or generate)
- `Issue_Date`, `Creation_Date`, `First_Payment_Due_Date` - Date logic
- `Issue_Value` - Principal loan amount
- `First_Instalment_Value` - From tabla de cargo
- `Regular_Instalment_Value` - From tabla de cargo
- `Final_Instalment_Value` - From tabla de cargo (may equal regular)
- `Total_Amount_Payable` - Sum of all installments
- `Product_Version_Id` - Based on term (112, 106, or 131)
- `Agreement_Status_Code` - 'AC' for active, 'PU' for paid up
- `Actual_Paid_Up_Date` - Only if status is 'PU'
- `Actual_Paid_Up_Week` - Only if status is 'PU'

**Fields that remain constant:**
- `Agreement_Db_Id` = 2000
- `Company_Code` = 'MEX'
- `Customer_Type_Code_At_Issue` = '1 '
- `Deleted_Flag` = 0
- `Early_Settlement_Bln` = 1
- `Product_Category_Code` = '1 '
- `Third_Party_Retailer_Event_Code` = '1 '
- `Annual_Interest_Rate` = 10.5000000000000
- `Company_Rate_Cap_Id` = 1

**Fields to auto-generate:**
- `Dt_Generation_Id` - New GUID
- `Global_Transaction_Key` - New GUID

### Step 5: Generate Transactions

For each payment, generate INSERT for `Agreement_Transaction_Table`:

**Key fields to calculate:**
- `Agreement_Transaction_Id` - Sequential ID (get next available)
- `Accounting_Week_Num` - Year + week number (format: YYYYWW)
- `Transaction_Date` - Date of payment
- `Value` - Payment amount from tabla de cargo
- `Reference_Text` - Description (e.g., "Pago acuerdo 5-3")
- `Agreement_Transaction_Type_Code` - 'HC' or 'OP' (per user request)

**Fields that remain constant:**
- `Agreement_Transaction_Db_Id` = 102
- `Agreement_Db_Id` = 2000
- `Balanced_Bln` = 1
- `Committed_Bln` = 1
- `Company_Code` = 'MEX'
- `Deleted_Flag` = 0
- `Money_Balancing_Bln` = 0
- `Product_Version_Db_Id` = 2000
- `Unsigned_Bln` = 0
- `Undated_Bln` = 0
- `Allow_Updates_Bln` = 1
- `Last_Updated_Id` = 5001
- `Last_Updated_Timestamp` = 0x00000000004CA486
- `Effective_Accounting_Week_Num` = 50

**Fields to auto-generate:**
- `Dt_Transaction_Id` - New GUID
- `Global_Transaction_Key` - New GUID

### Step 6: Generate Receipts

For each transaction, generate INSERT for `Agreement_Transaction_Receipt_Table`:

**CRITICAL:** The receipt uses the composite key from the transaction:
- `Agreement_Transaction_Id` - Same as transaction
- `Agreement_Transaction_Db_Id` = 102 (same as transaction)

**Key fields to calculate:**
- `Agreement_Transaction_Receipt_Id` - Sequential ID (get next available)
- `Receipt_Reference` - Format: 'RC-{Agreement_Transaction_Id}'
- `Transaction_Date` - Same as transaction date
- `Creation_Date` - Same as transaction date
- `Validation_Date` - Validation timestamp

**Fields that remain constant:**
- `Agreement_Transaction_Receipt_Db_Id` = 102
- `Extracted` = 0
- `Deleted_Flag` = 0
- `Dt_Write_Bln` = 0
- `Receipt_Type_Code` = 'RCT'
- `Previously_Committed_Transaction_Bln` = 0
- `Undated_Bln` = 0
- `Unsigned_Bln` = 0
- `Validated_Bln` = 0
- `Last_Updated_Id` = 5002
- `Last_Updated_Timestamp` = 0x00000000004CA41E

**Fields to auto-generate:**
- `Dt_Transaction_Id` - New GUID
- `ReceiptHash` - New GUID or leave as ' '

### Step 7: Generate Rollback Script

At the end of the SQL file, generate DELETE statements in reverse order:

```sql
-- ROLLBACK SCRIPT
-- Execute these statements in order to undo the inserts above

DELETE FROM CNFS_uat.NFS_DBO.Agreement_Transaction_Receipt_Table 
WHERE Agreement_Transaction_Receipt_Id IN ({list of IDs});

DELETE FROM CNFS_uat.NFS_DBO.Agreement_Transaction_Table 
WHERE Agreement_Transaction_Id IN ({list of IDs});

-- Only if you created a new agreement:
DELETE FROM CNFS_uat.NFS_DBO.Agreement_Table 
WHERE Agreement_Id = {Agreement_Id};
```

## SQL File Structure

Generate a single SQL file with this structure:

```sql
-- =====================================================
-- Payment Receipt Generator
-- Generated: {timestamp}
-- Customer_Id: {value}
-- Agreement_Id: {value}
-- Contract Term: {value} weeks
-- Number of Payments: {value}
-- Status: {Liquidated/In-Progress}
-- =====================================================

BEGIN TRANSACTION;

-- Step 1: Agreement (if creating new contract)
INSERT INTO CNFS_uat.NFS_DBO.Agreement_Table (...) VALUES (...);

-- Step 2: Transactions
INSERT INTO CNFS_uat.NFS_DBO.Agreement_Transaction_Table (...) VALUES (...);
-- Repeat for each payment

-- Step 3: Receipts
INSERT INTO CNFS_uat.NFS_DBO.Agreement_Transaction_Receipt_Table (...) VALUES (...);
-- Repeat for each payment

COMMIT TRANSACTION;

-- =====================================================
-- ROLLBACK SCRIPT
-- =====================================================
-- BEGIN TRANSACTION;
-- DELETE FROM CNFS_uat.NFS_DBO.Agreement_Transaction_Receipt_Table WHERE Agreement_Transaction_Receipt_Id IN (...);
-- DELETE FROM CNFS_uat.NFS_DBO.Agreement_Transaction_Table WHERE Agreement_Transaction_Id IN (...);
-- DELETE FROM CNFS_uat.NFS_DBO.Agreement_Table WHERE Agreement_Id = ...;
-- COMMIT TRANSACTION;
```

## Important Notes

### Date and Week Calculations
- Week format: YYYYWW (e.g., 202614 = year 2026, week 14)
- Weeks change on **Wednesdays**
- Use current date for generation unless user specifies otherwise
- Payment dates should be weekly intervals from issue date

### GUID Generation
Generate new GUIDs for:
- `Dt_Generation_Id`
- `Dt_Transaction_Id` (for both transactions and receipts)
- `Global_Transaction_Key`

### ID Generation
For sequential IDs (Agreement_Transaction_Id, Agreement_Transaction_Receipt_Id):
- Ask user for starting ID or
- Use a reasonable high number to avoid conflicts (e.g., 2000000+)

### Branch and Agency Mapping
The first 4 digits of Agency_Id = branch code:
- Agency 2075000000335 → Branch 2075
- Agency 2093000000111 → Branch 2093

### Error Prevention
- Always use fully qualified table names: `CNFS_uat.NFS_DBO.{table_name}`
- Ensure composite keys match between transactions and receipts
- Validate payment amounts against tabla de cargo
- Check that total payments don't exceed contract term
- For liquidated contracts, ensure payment count = term

## Example Usage

**User request:** "Generate 5 payments for a 12-week contract for customer 2075042613005"

**Your response:**
1. Confirm: Creating 5/12 payments (in-progress contract)
2. Ask for: loan amount, transaction type (HC/OP), representative ID
3. Look up tabla de cargo for 12-week payment amounts
4. Generate SQL with 5 transaction/receipt pairs
5. Include rollback script

**User request:** "Create a liquidated 42-week contract with all payments"

**Your response:**
1. Confirm: Creating new contract with 42/42 payments (liquidated)
2. Ask for: customer ID, loan amount, agency, representative, transaction type
3. Look up tabla de cargo for 42-week payment amounts
4. Generate SQL with agreement + 42 transaction/receipt pairs
5. Set Agreement_Status_Code = 'PU' and Actual_Paid_Up_Date
6. Include rollback script

## Reference Files

- `references/tabla_de_cargo.md` - Payment amount tables by term and installment number
- `references/field_mappings.md` - Complete field reference for all tables

Read these files as needed during generation to ensure accuracy.
