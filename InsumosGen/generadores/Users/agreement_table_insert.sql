INSERT INTO CNFS_uat.NFS_DBO.Agreement_Table (
        Agreement_Id,
        Agreement_Db_Id,
        Absolute_Arrears,
        Actual_Paid_Up_Date,
        Actual_Paid_Up_Week,
        Agreement_Num,
        Agreement_Status_Code,
        Cancellation_Date,
        Cancellation_Week,
        Cancellation_Value,
        Cancelled_By_Representative_Id,
        Creation_Date,
        Creation_Week,
        Company_Code,
        Customer_Id,
        Customer_Type_Code_At_Issue,
        Deleted_Flag,
        Early_Settlement_Bln,
        Early_Settlement_Rebate_Value,
        Early_Settlement_Rebate_Contra_Value,
        Final_Instalment_Value,
        First_Instalment_Value,
        First_Payment_Due_Date,
        Instalment_Periods_To_Date,
        Is_Adjustment_Bln,
        Issue_Date,
        Issue_Value,
        Issuing_Representative_Id,
        Late_Issue_Bln,
        Linked_Agreement_Number,
        Loan_Reason_Code,
        Next_Payment_Due,
        Normal_Due_Day_In_Month,
        Number_Of_Default_Charge_Applications_To_Date,
        Outstanding_Balance,
        Outstanding_Default_Charge,
        Product_Category_Code,
        Product_Version_Db_Id,
        Product_Version_Id,
        Regular_Instalment_Value,
        Third_Party_Retailer_Event_Code,
        Total_Amount_Payable,
        Transferred_Bln,
        Settlement_Balance,
        Written_Back_Value,
        Written_Off_Date,
        Written_Off_Value,
        Written_Off_Week,
        Dt_Generation_Id,
        Dt_Transaction_Id,
        Dt_Write_Bln,
        Last_Updated_Datetime,
        Last_Updated_Id,
        Last_Updated_Timestamp,
        Annual_Interest_Rate,
        Prevailing_Principal,
        Company_Rate_Cap_Id,
        Final_Instalment_Value_At_Issue,
        First_Instalment_Value_At_Issue,
        Regular_Instalment_Value_At_Issue,
        Total_Amount_Payable_At_Issue,
        Customer_Repayment_Account_Num,
        Chosen_Payment_Due_Day,
        Early_Settlement_Charge_Applied,
        Refinancing_Agreement_Id,
        Refinancing_Agreement_Db_Id,
        Refinanced_Week,
        Reporting_Week_Num,
        Agreement_Form_Corrected_Bln,
        Customer_Business_Id,
        Customer_Business_Db_Id,
        Credit_Check_Reference,
        Codebtor_Id,
        Finance_Absolute_Arrears,
        Global_Transaction_Key,
        Agreement_Source_Code,
        Agreement_Issue_Location_Code,
        Promotion_Reason_Code
    )
VALUES(
        134,
        2000,
        -- se mantiene este dato
        0.000000,
        -- se mantiene este dato
        '2026-03-07 00:00:00.000',
        -- se actualiza de acuerdo a la fecha de emisión
        202609,
        -- se actualiza de acuerdo a las semanas del año
        240010470,
        -- Este es el número del contrato, se toma de un Query que te compartiré
        N'AC',
        -- se mantiene e 
        NULL,
        -- se mantiene este dato
        NULL,
        -- se mantiene este dato
        NULL,
        -- se mantiene este dato
        '2026-02-04 00:00:00.000',
        -- se modifica de acuerdo a la fecha de emisión
        202609,
        -- se actualiza de acuerdo a las semanas del año
        N'MEX',
        -- se mantiene este dato
        2075042613006,
        --número de cliente al que se le asignó el contrato
        N'1 ',
        -- se mantiene este dato
        0,
        -- se mantiene este dato
        1,
        -- se mantiene este dato
        1000.000000,
        0.000000,
        378.750000,
        378.750000,
        '2026-03-03 00:00:00.000',
        --se actualiza de acuerdo a la fecha de emisión
        7,
        -- se mantiene este dato
        0,
        -- se mantiene este dato
        '2026-03-03 00:00:00.000',
        --se actualiza de acuerdo a la fecha de emisión
        0.000000,
        -- se mantiene este dato
        1001,
        -- se mantiene este dato
        0,
        -- se mantiene este dato
        NULL,
        -- se mantiene este dato
        N'1 ',
        -- se mantiene este dato
        '2026-03-03 00:00:00.000',
        --se actualiza de acuerdo a la fecha de emisión
        15,
        -- se mantiene este dato
        0,
        -- se mantiene este dato
        0.000000,
        -- se mantiene este dato
        0.000000,
        -- se mantiene este dato
        N'1 ',
        -- se mantiene este dato
        2000,
        -- se mantiene este dato
        112,
        -- tiene que ver con el tipo de id que se tiene de acuerdo al plazo  (106 =42 semanas, 131 = 65 semanas y 112 ( 12 semanas))
        378.750000,
        N'1 ',
        -- se mantiene este dato
        4545.000000,
        0,
        --se mantiene este dato
        1893.750000,
        0.000000,
        --se mantiene este dato
        NULL,
        --se mantiene este dato
        0.000000,
        --se mantiene este dato
        NULL,
        --se mantiene este dato
        1,
        --se mantiene este dato
        N'50CE307D-6E8C-4101-8B81-81A506B37F86',
        --autogenerar
        0,
        --se mantiene este dato
        '2026-03-03 00:00:00.000',
        --se actualiza de acuerdo a la fecha de emisión
        1001,
        --se mantiene este dato
        0x00000000004ABD0A,
        --se mantiene este dato
        10.5000000000000,
        --se mantiene este dato
        0.000000,
        --se mantiene 
        1,
        -- se mantiene
        378.750000,
        378.750000,
        378.750000,
        4545.000000,
        N'ACC123456789',
        -- se mantiene
        15,
        -- se mantiene
        0.000000,
        -- se mantiene
        NULL,
        -- se mantiene
        NULL,
        -- se mantiene
        NULL,
        -- se mantiene
        NULL,
        -- se mantiene
        0,
        -- se mantiene
        NULL,
        -- se mantiene
        NULL,
        -- se mantiene
        N'CREDITCHK001',
        -- se mantiene
        NULL,
        -- se mantiene
        0.000000,
        -- se mantiene
        N'D3C955D0-8595-4F99-93BA-B10869AD2438',
        -- se mantiene
        N'1 ',
        -- se mantiene
        N'1 ',
        -- se mantiene
        N'1 ' -- se mantiene
    );