# Example SQL Templates

This document provides complete SQL templates for common payment receipt generation scenarios.

## Template 1: In-Progress Contract (5/12 Payments)

```sql
-- =====================================================
-- Payment Receipt Generator
-- Generated: 2026-04-06 18:30:00
-- Customer_Id: 2075042613005
-- Agreement_Id: 134
-- Contract Term: 12 weeks
-- Number of Payments: 5/12
-- Status: In-Progress (Active)
-- Loan Amount: 3,000.00 MXN
-- =====================================================

BEGIN TRANSACTION;

-- Step 1: Agreement (New Contract)
INSERT INTO CNFS_uat.NFS_DBO.Agreement_Table (
    Agreement_Id, Agreement_Db_Id, Absolute_Arrears, Actual_Paid_Up_Date, Actual_Paid_Up_Week,
    Agreement_Num, Agreement_Status_Code, Cancellation_Date, Cancellation_Week, Cancellation_Value,
    Cancelled_By_Representative_Id, Creation_Date, Creation_Week, Company_Code, Customer_Id,
    Customer_Type_Code_At_Issue, Deleted_Flag, Early_Settlement_Bln, Early_Settlement_Rebate_Value,
    Early_Settlement_Rebate_Contra_Value, Final_Instalment_Value, First_Instalment_Value,
    First_Payment_Due_Date, Instalment_Periods_To_Date, Is_Adjustment_Bln, Issue_Date, Issue_Value,
    Issuing_Representative_Id, Late_Issue_Bln, Linked_Agreement_Number, Loan_Reason_Code,
    Next_Payment_Due, Normal_Due_Day_In_Month, Number_Of_Default_Charge_Applications_To_Date,
    Outstanding_Balance, Outstanding_Default_Charge, Product_Category_Code, Product_Version_Db_Id,
    Product_Version_Id, Regular_Instalment_Value, Third_Party_Retailer_Event_Code,
    Total_Amount_Payable, Transferred_Bln, Settlement_Balance, Written_Back_Value, Written_Off_Date,
    Written_Off_Value, Written_Off_Week, Dt_Generation_Id, Dt_Transaction_Id, Dt_Write_Bln,
    Last_Updated_Datetime, Last_Updated_Id, Last_Updated_Timestamp, Annual_Interest_Rate,
    Prevailing_Principal, Company_Rate_Cap_Id, Final_Instalment_Value_At_Issue,
    First_Instalment_Value_At_Issue, Regular_Instalment_Value_At_Issue, Total_Amount_Payable_At_Issue,
    Customer_Repayment_Account_Num, Chosen_Payment_Due_Day, Early_Settlement_Charge_Applied,
    Refinancing_Agreement_Id, Refinancing_Agreement_Db_Id, Refinanced_Week, Reporting_Week_Num,
    Agreement_Form_Corrected_Bln, Customer_Business_Id, Customer_Business_Db_Id,
    Credit_Check_Reference, Codebtor_Id, Finance_Absolute_Arrears, Global_Transaction_Key,
    Agreement_Source_Code, Agreement_Issue_Location_Code, Promotion_Reason_Code
)
VALUES (
    134, 2000, 0.000000, NULL, NULL,
    240010470, N'AC', NULL, NULL, NULL,
    '2026-02-04 00:00:00.000', '2026-03-03 00:00:00.000', 202609, N'MEX', 2075042613005,
    N'1 ', 0, 1, 1000.000000,
    0.000000, 378.750000, 378.750000,
    '2026-03-10 00:00:00.000', 7, 0, '2026-03-03 00:00:00.000', 3000.000000,
    1001, 0, NULL, N'1 ',
    '2026-03-10 00:00:00.000', 15, 0,
    0.000000, 0.000000, N'1 ', 2000,
    112, 378.750000, N'1 ',
    4545.000000, 0, 1893.750000, 0.000000, NULL,
    0.000000, NULL, N'50CE307D-6E8C-4101-8B81-81A506B37F86', 0, 0,
    '2026-03-03 00:00:00.000', 1001, 0x00000000004ABD0A, 10.5000000000000,
    0.000000, 1, 378.750000,
    378.750000, 378.750000, 4545.000000,
    N'ACC123456789', 15, 0.000000,
    NULL, NULL, NULL, NULL,
    0, NULL, NULL,
    N'CREDITCHK001', NULL, 0.000000, N'D3C955D0-8595-4F99-93BA-B10869AD2438',
    N'1 ', N'1 ', N'1 '
);

-- Step 2: Transactions (5 payments)
INSERT INTO CNFS_uat.NFS_DBO.Agreement_Transaction_Table (
    Agreement_Transaction_Id, Agreement_Transaction_Db_Id, Agreement_Security_Check_Balance_Db_Id,
    Agreement_Security_Check_Balance_Id, Accounting_Week_Num, Agency_Id, Agreement_Db_Id,
    Agreement_Transaction_Type_Code, Balanced_Bln, Agreement_Id, Committed_Bln, Company_Code,
    Creation_Date, Deleted_Flag, Money_Balancing_Bln, Non_Payment_Code, Original_Representative_Id,
    Product_Version_Db_Id, Product_Version_Id, Reference_Text, Representative_Id, Value,
    Write_Off_Reason_Code, Dt_Generation_Id, Dt_Transaction_Id, Dt_Write_Bln, Last_Updated_Datetime,
    Last_Updated_Id, Last_Updated_Timestamp, Effective_Accounting_Week_Num, Transaction_Date,
    Unsigned_Bln, Undated_Bln, Amount_That_Cleared_Default_Charges, Committed_Date, Balance_Id,
    Balance_Db_Id, Default_Charge_Rule_Code, Committed_By_Representative_Id, Allow_Updates_Bln,
    Global_Transaction_Key, External_User_Id
)
VALUES
    (2000385, 102, NULL, NULL, 202610, 2075000000335, 2000, N'HC', 1, 134, 1, N'MEX',
     '2026-03-10 10:00:00.000', 0, 0, NULL, NULL, 2000, 112, N'Pago 1 de 12', 2075000343335, 378.750000,
     NULL, 1, N'DB321C3D-6C24-4A50-9F7C-AF7E003C52C2', 0, '2024-03-24 10:00:00.000',
     5001, 0x00000000004CA486, 50, '2026-03-10 10:00:00.000', 0, 0, 0.000000, NULL, NULL,
     NULL, NULL, 1, 1, N'61F1D174-C3C6-42CA-BF67-2B3F6D246C6F', NULL),
    (2000386, 102, NULL, NULL, 202611, 2075000000335, 2000, N'HC', 1, 134, 1, N'MEX',
     '2026-03-17 10:00:00.000', 0, 0, NULL, NULL, 2000, 112, N'Pago 2 de 12', 2075000343335, 378.750000,
     NULL, 1, N'A8F2E3D1-5B94-4C21-8E7A-C9D4F6A2B8E3', 0, '2024-03-24 10:00:00.000',
     5001, 0x00000000004CA486, 50, '2026-03-17 10:00:00.000', 0, 0, 0.000000, NULL, NULL,
     NULL, NULL, 1, 1, N'F7E8D9C0-4A5B-3C2D-1E0F-9A8B7C6D5E4F', NULL),
    (2000387, 102, NULL, NULL, 202612, 2075000000335, 2000, N'HC', 1, 134, 1, N'MEX',
     '2026-03-24 10:00:00.000', 0, 0, NULL, NULL, 2000, 112, N'Pago 3 de 12', 2075000343335, 378.750000,
     NULL, 1, N'C3D4E5F6-7A8B-9C0D-1E2F-3A4B5C6D7E8F', 0, '2024-03-24 10:00:00.000',
     5001, 0x00000000004CA486, 50, '2026-03-24 10:00:00.000', 0, 0, 0.000000, NULL, NULL,
     NULL, NULL, 1, 1, N'E9F0A1B2-C3D4-E5F6-7A8B-9C0D1E2F3A4B', NULL),
    (2000388, 102, NULL, NULL, 202613, 2075000000335, 2000, N'HC', 1, 134, 1, N'MEX',
     '2026-03-31 10:00:00.000', 0, 0, NULL, NULL, 2000, 112, N'Pago 4 de 12', 2075000343335, 378.750000,
     NULL, 1, N'B5C6D7E8-F9A0-1B2C-3D4E-5F6A7B8C9D0E', 0, '2024-03-24 10:00:00.000',
     5001, 0x00000000004CA486, 50, '2026-03-31 10:00:00.000', 0, 0, 0.000000, NULL, NULL,
     NULL, NULL, 1, 1, N'D1E2F3A4-B5C6-D7E8-F9A0-1B2C3D4E5F6A', NULL),
    (2000389, 102, NULL, NULL, 202614, 2075000000335, 2000, N'HC', 1, 134, 1, N'MEX',
     '2026-04-07 10:00:00.000', 0, 0, NULL, NULL, 2000, 112, N'Pago 5 de 12', 2075000343335, 378.750000,
     NULL, 1, N'F7A8B9C0-D1E2-F3A4-B5C6-D7E8F9A0B1C2', 0, '2024-03-24 10:00:00.000',
     5001, 0x00000000004CA486, 50, '2026-04-07 10:00:00.000', 0, 0, 0.000000, NULL, NULL,
     NULL, NULL, 1, 1, N'A3B4C5D6-E7F8-A9B0-C1D2-E3F4A5B6C7D8', NULL);

-- Step 3: Receipts (5 receipts)
INSERT INTO CNFS_uat.NFS_DBO.Agreement_Transaction_Receipt_Table (
    Agreement_Transaction_Receipt_Id, Agreement_Transaction_Receipt_Db_Id, Agreement_Transaction_Id,
    Agreement_Transaction_Db_Id, Receipt_Reference, Extracted, Transaction_Date, Deleted_Flag,
    Dt_Generation_Id, Dt_Transaction_Id, Dt_Write_Bln, Last_Updated_Datetime, Last_Updated_Id,
    Last_Updated_Timestamp, Stock_Item_Id, Stock_Item_Db_Id, Creation_Date,
    Previously_Committed_Transaction_Bln, Receipt_Type_Code, Representative_Id, Undated_Bln,
    Unsigned_Bln, Validated_Bln, Validation_Date, ReceiptHash
)
VALUES
    (410768, 102, 2000385, 102, N'RC-2000385', 0, '2026-03-10 10:00:00.000', 0,
     0, N'16B2D146-90AC-4700-BA13-8116BF033174', 0, '2025-10-15 19:52:00.000', 5002,
     0x00000000004CA41E, NULL, NULL, '2026-03-10 10:00:00.000', 0, N'RCT', 2075000343335,
     0, 0, 0, NULL, N'                               '),
    (410769, 102, 2000386, 102, N'RC-2000386', 0, '2026-03-17 10:00:00.000', 0,
     0, N'27C3E257-A1BD-5811-CB24-9227CG144285', 0, '2025-10-15 19:52:00.000', 5002,
     0x00000000004CA41E, NULL, NULL, '2026-03-17 10:00:00.000', 0, N'RCT', 2075000343335,
     0, 0, 0, NULL, N'                               '),
    (410770, 102, 2000387, 102, N'RC-2000387', 0, '2026-03-24 10:00:00.000', 0,
     0, N'38D4F368-B2CE-6922-DC35-A338DH255396', 0, '2025-10-15 19:52:00.000', 5002,
     0x00000000004CA41E, NULL, NULL, '2026-03-24 10:00:00.000', 0, N'RCT', 2075000343335,
     0, 0, 0, NULL, N'                               '),
    (410771, 102, 2000388, 102, N'RC-2000388', 0, '2026-03-31 10:00:00.000', 0,
     0, N'49E5G479-C3DF-7A33-ED46-B449EI3664A7', 0, '2025-10-15 19:52:00.000', 5002,
     0x00000000004CA41E, NULL, NULL, '2026-03-31 10:00:00.000', 0, N'RCT', 2075000343335,
     0, 0, 0, NULL, N'                               '),
    (410772, 102, 2000389, 102, N'RC-2000389', 0, '2026-04-07 10:00:00.000', 0,
     0, N'5AF6H58A-D4EG-8B44-FE57-C55AFJ4775B8', 0, '2025-10-15 19:52:00.000', 5002,
     0x00000000004CA41E, NULL, NULL, '2026-04-07 10:00:00.000', 0, N'RCT', 2075000343335,
     0, 0, 0, NULL, N'                               ');

COMMIT TRANSACTION;

-- =====================================================
-- ROLLBACK SCRIPT
-- Execute these statements in order to undo the inserts above
-- =====================================================
-- BEGIN TRANSACTION;
-- DELETE FROM CNFS_uat.NFS_DBO.Agreement_Transaction_Receipt_Table 
-- WHERE Agreement_Transaction_Receipt_Id IN (410768, 410769, 410770, 410771, 410772);
-- DELETE FROM CNFS_uat.NFS_DBO.Agreement_Transaction_Table 
-- WHERE Agreement_Transaction_Id IN (2000385, 2000386, 2000387, 2000388, 2000389);
-- DELETE FROM CNFS_uat.NFS_DBO.Agreement_Table 
-- WHERE Agreement_Id = 134;
-- COMMIT TRANSACTION;
```

## Template 2: Liquidated Contract (12/12 Payments - Paid Up)

```sql
-- =====================================================
-- Payment Receipt Generator
-- Generated: 2026-04-06 18:30:00
-- Customer_Id: 2075042613005
-- Agreement_Id: 135
-- Contract Term: 12 weeks
-- Number of Payments: 12/12
-- Status: Liquidated (Paid Up)
-- Loan Amount: 3,000.00 MXN
-- =====================================================

BEGIN TRANSACTION;

-- Step 1: Agreement (Liquidated Contract)
INSERT INTO CNFS_uat.NFS_DBO.Agreement_Table (
    Agreement_Id, Agreement_Db_Id, Absolute_Arrears, Actual_Paid_Up_Date, Actual_Paid_Up_Week,
    Agreement_Num, Agreement_Status_Code, Cancellation_Date, Cancellation_Week, Cancellation_Value,
    Cancelled_By_Representative_Id, Creation_Date, Creation_Week, Company_Code, Customer_Id,
    Customer_Type_Code_At_Issue, Deleted_Flag, Early_Settlement_Bln, Early_Settlement_Rebate_Value,
    Early_Settlement_Rebate_Contra_Value, Final_Instalment_Value, First_Instalment_Value,
    First_Payment_Due_Date, Instalment_Periods_To_Date, Is_Adjustment_Bln, Issue_Date, Issue_Value,
    Issuing_Representative_Id, Late_Issue_Bln, Linked_Agreement_Number, Loan_Reason_Code,
    Next_Payment_Due, Normal_Due_Day_In_Month, Number_Of_Default_Charge_Applications_To_Date,
    Outstanding_Balance, Outstanding_Default_Charge, Product_Category_Code, Product_Version_Db_Id,
    Product_Version_Id, Regular_Instalment_Value, Third_Party_Retailer_Event_Code,
    Total_Amount_Payable, Transferred_Bln, Settlement_Balance, Written_Back_Value, Written_Off_Date,
    Written_Off_Value, Written_Off_Week, Dt_Generation_Id, Dt_Transaction_Id, Dt_Write_Bln,
    Last_Updated_Datetime, Last_Updated_Id, Last_Updated_Timestamp, Annual_Interest_Rate,
    Prevailing_Principal, Company_Rate_Cap_Id, Final_Instalment_Value_At_Issue,
    First_Instalment_Value_At_Issue, Regular_Instalment_Value_At_Issue, Total_Amount_Payable_At_Issue,
    Customer_Repayment_Account_Num, Chosen_Payment_Due_Day, Early_Settlement_Charge_Applied,
    Refinancing_Agreement_Id, Refinancing_Agreement_Db_Id, Refinanced_Week, Reporting_Week_Num,
    Agreement_Form_Corrected_Bln, Customer_Business_Id, Customer_Business_Db_Id,
    Credit_Check_Reference, Codebtor_Id, Finance_Absolute_Arrears, Global_Transaction_Key,
    Agreement_Source_Code, Agreement_Issue_Location_Code, Promotion_Reason_Code
)
VALUES (
    135, 2000, 0.000000, '2026-05-26 00:00:00.000', 202621,
    240010471, N'PU', NULL, NULL, NULL,
    '2026-02-04 00:00:00.000', '2026-03-03 00:00:00.000', 202609, N'MEX', 2075042613005,
    N'1 ', 0, 1, 1000.000000,
    0.000000, 378.750000, 378.750000,
    '2026-03-10 00:00:00.000', 7, 0, '2026-03-03 00:00:00.000', 3000.000000,
    1001, 0, NULL, N'1 ',
    '2026-03-10 00:00:00.000', 15, 0,
    0.000000, 0.000000, N'1 ', 2000,
    112, 378.750000, N'1 ',
    4545.000000, 0, 0.000000, 0.000000, NULL,
    0.000000, NULL, N'A1B2C3D4-E5F6-7A8B-9C0D-1E2F3A4B5C6D', 0, 0,
    '2026-05-26 00:00:00.000', 1001, 0x00000000004ABD0A, 10.5000000000000,
    0.000000, 1, 378.750000,
    378.750000, 378.750000, 4545.000000,
    N'ACC123456789', 15, 0.000000,
    NULL, NULL, NULL, NULL,
    0, NULL, NULL,
    N'CREDITCHK001', NULL, 0.000000, N'B2C3D4E5-F6A7-8B9C-0D1E-2F3A4B5C6D7E',
    N'1 ', N'1 ', N'1 '
);

-- Step 2: Transactions (12 payments - all payments made)
-- [Similar structure to Template 1, but with 12 transaction records]
-- Transaction dates: weekly from 2026-03-10 to 2026-05-26

-- Step 3: Receipts (12 receipts)
-- [Similar structure to Template 1, but with 12 receipt records]

COMMIT TRANSACTION;

-- =====================================================
-- ROLLBACK SCRIPT
-- =====================================================
-- [Rollback script with all 12 transaction and receipt IDs]
```

## Template 3: Existing Contract - Add Transactions Only

```sql
-- =====================================================
-- Payment Receipt Generator
-- Generated: 2026-04-06 18:30:00
-- Customer_Id: 2075042613005
-- Agreement_Id: 134 (EXISTING)
-- Adding 3 additional payments
-- =====================================================

BEGIN TRANSACTION;

-- Step 1: Transactions (3 new payments)
INSERT INTO CNFS_uat.NFS_DBO.Agreement_Transaction_Table (
    Agreement_Transaction_Id, Agreement_Transaction_Db_Id, Agreement_Security_Check_Balance_Db_Id,
    Agreement_Security_Check_Balance_Id, Accounting_Week_Num, Agency_Id, Agreement_Db_Id,
    Agreement_Transaction_Type_Code, Balanced_Bln, Agreement_Id, Committed_Bln, Company_Code,
    Creation_Date, Deleted_Flag, Money_Balancing_Bln, Non_Payment_Code, Original_Representative_Id,
    Product_Version_Db_Id, Product_Version_Id, Reference_Text, Representative_Id, Value,
    Write_Off_Reason_Code, Dt_Generation_Id, Dt_Transaction_Id, Dt_Write_Bln, Last_Updated_Datetime,
    Last_Updated_Id, Last_Updated_Timestamp, Effective_Accounting_Week_Num, Transaction_Date,
    Unsigned_Bln, Undated_Bln, Amount_That_Cleared_Default_Charges, Committed_Date, Balance_Id,
    Balance_Db_Id, Default_Charge_Rule_Code, Committed_By_Representative_Id, Allow_Updates_Bln,
    Global_Transaction_Key, External_User_Id
)
VALUES
    (2000390, 102, NULL, NULL, 202615, 2075000000335, 2000, N'OP', 1, 134, 1, N'MEX',
     '2026-04-14 10:00:00.000', 0, 0, NULL, NULL, 2000, 112, N'Pago 6 de 12', 2075000343335, 378.750000,
     NULL, 1, N'C7D8E9F0-A1B2-C3D4-E5F6-7A8B9C0D1E2F', 0, '2024-03-24 10:00:00.000',
     5001, 0x00000000004CA486, 50, '2026-04-14 10:00:00.000', 0, 0, 0.000000, NULL, NULL,
     NULL, NULL, 1, 1, N'E5F6A7B8-C9D0-E1F2-A3B4-C5D6E7F8A9B0', NULL),
    (2000391, 102, NULL, NULL, 202616, 2075000000335, 2000, N'OP', 1, 134, 1, N'MEX',
     '2026-04-21 10:00:00.000', 0, 0, NULL, NULL, 2000, 112, N'Pago 7 de 12', 2075000343335, 378.750000,
     NULL, 1, N'D8E9F0A1-B2C3-D4E5-F6A7-8B9C0D1E2F3A', 0, '2024-03-24 10:00:00.000',
     5001, 0x00000000004CA486, 50, '2026-04-21 10:00:00.000', 0, 0, 0.000000, NULL, NULL,
     NULL, NULL, 1, 1, N'F6A7B8C9-D0E1-F2A3-B4C5-D6E7F8A9B0C1', NULL),
    (2000392, 102, NULL, NULL, 202617, 2075000000335, 2000, N'OP', 1, 134, 1, N'MEX',
     '2026-04-28 10:00:00.000', 0, 0, NULL, NULL, 2000, 112, N'Pago 8 de 12', 2075000343335, 378.750000,
     NULL, 1, N'E9F0A1B2-C3D4-E5F6-A7B8-9C0D1E2F3A4B', 0, '2024-03-24 10:00:00.000',
     5001, 0x00000000004CA486, 50, '2026-04-28 10:00:00.000', 0, 0, 0.000000, NULL, NULL,
     NULL, NULL, 1, 1, N'A7B8C9D0-E1F2-A3B4-C5D6-E7F8A9B0C1D2', NULL);

-- Step 2: Receipts (3 new receipts)
INSERT INTO CNFS_uat.NFS_DBO.Agreement_Transaction_Receipt_Table (
    Agreement_Transaction_Receipt_Id, Agreement_Transaction_Receipt_Db_Id, Agreement_Transaction_Id,
    Agreement_Transaction_Db_Id, Receipt_Reference, Extracted, Transaction_Date, Deleted_Flag,
    Dt_Generation_Id, Dt_Transaction_Id, Dt_Write_Bln, Last_Updated_Datetime, Last_Updated_Id,
    Last_Updated_Timestamp, Stock_Item_Id, Stock_Item_Db_Id, Creation_Date,
    Previously_Committed_Transaction_Bln, Receipt_Type_Code, Representative_Id, Undated_Bln,
    Unsigned_Bln, Validated_Bln, Validation_Date, ReceiptHash
)
VALUES
    (410773, 102, 2000390, 102, N'RC-2000390', 0, '2026-04-14 10:00:00.000', 0,
     0, N'6BG7I69B-E5FH-9C55-GF68-D66BGK5886C9', 0, '2025-10-15 19:52:00.000', 5002,
     0x00000000004CA41E, NULL, NULL, '2026-04-14 10:00:00.000', 0, N'RCT', 2075000343335,
     0, 0, 0, NULL, N'                               '),
    (410774, 102, 2000391, 102, N'RC-2000391', 0, '2026-04-21 10:00:00.000', 0,
     0, N'7CH8J7AC-F6GI-AD66-HG79-E77CHL6997DA', 0, '2025-10-15 19:52:00.000', 5002,
     0x00000000004CA41E, NULL, NULL, '2026-04-21 10:00:00.000', 0, N'RCT', 2075000343335,
     0, 0, 0, NULL, N'                               '),
    (410775, 102, 2000392, 102, N'RC-2000392', 0, '2026-04-28 10:00:00.000', 0,
     0, N'8DI9K8BD-G7HJ-BE77-IH8A-F88DIM7AA8EB', 0, '2025-10-15 19:52:00.000', 5002,
     0x00000000004CA41E, NULL, NULL, '2026-04-28 10:00:00.000', 0, N'RCT', 2075000343335,
     0, 0, 0, NULL, N'                               ');

COMMIT TRANSACTION;

-- =====================================================
-- ROLLBACK SCRIPT
-- =====================================================
-- BEGIN TRANSACTION;
-- DELETE FROM CNFS_uat.NFS_DBO.Agreement_Transaction_Receipt_Table 
-- WHERE Agreement_Transaction_Receipt_Id IN (410773, 410774, 410775);
-- DELETE FROM CNFS_uat.NFS_DBO.Agreement_Transaction_Table 
-- WHERE Agreement_Transaction_Id IN (2000390, 2000391, 2000392);
-- COMMIT TRANSACTION;
```

## Key Points from Templates

1. **Transaction Wrapper**: Always use `BEGIN TRANSACTION` and `COMMIT TRANSACTION`
2. **Sequential IDs**: Ensure Transaction_Id and Receipt_Id are sequential
3. **Composite Key**: Receipt must reference Transaction using both `Agreement_Transaction_Id` and `Agreement_Transaction_Db_Id` (always 102)
4. **Receipt Reference**: Format is always `'RC-{Transaction_Id}'`
5. **Weekly Intervals**: Payment dates are typically 7 days apart
6. **Week Numbers**: Increment by 1 for each week (format: YYYYWW)
7. **Rollback**: Always commented out, in reverse order of inserts
8. **GUIDs**: Generate unique GUIDs for each record
9. **Status Codes**: 'AC' for active, 'PU' for paid up (liquidated)
10. **Paid Up Fields**: Only populate `Actual_Paid_Up_Date` and `Actual_Paid_Up_Week` for liquidated contracts
