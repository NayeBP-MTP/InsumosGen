INSERT INTO [CNFS_uat].[NFS_DBO].[Customer_Table] (
        [Customer_Id],
        [Address_Changes_Count],
        [Agency_Id],
        [Agency_Segment_Db_Id],
        [Agency_Segment_Id],
        [Agency_Sequence_Num],
        [Avg_Overdue_Weeks],
        [Bank_Account_Indicator_Code],
        [Birth_Date],
        [BIS_To_FOCUS_Transfer_Bln],
        [Cancellation_Week],
        [Cdr_Referred_Date],
        [Child_1_Birth_Year],
        [Child_2_Birth_Year],
        [Child_3_Birth_Year],
        [Child_4_Birth_Year],
        [Child_5_Birth_Year],
        [Child_6_Birth_Year],
        [Collection_Pct],
        [Company_Code],
        [Correspondence_Bln],
        [Creation_Date],
        [Creation_Week],
        [Credit_Card_Indicator_Code],
        [Customer_Income_Frequency_Code],
        [Customer_Lower_Commission_Target],
        [Customer_Maintain_Quality_Message],
        [Customer_Rate],
        [Customer_Status_Code],
        [Customer_Language_Code],
        [Customer_Type_Code],
        [Customer_Type_Date],
        [Customer_Type_Week],
        [Customer_Upper_Commission_Target],
        [Debit_Card_Indicator_Code],
        [Deceased_Bln],
        [Deleted_Flag],
        [Display_Name],
        [Disposable_Income],
        [Disposable_Income_Date],
        [Doc_Arrears_Stage],
        [Email_Address],
        [Employer_Address],
        [Employer_Name],
        [Employer_Tel_Num],
        [Employment_Status_Code],
        [External_System_Created_Id],
        [External_Unique],
        [First_Agreement_Creation_Date],
        [First_Agreement_Creation_Week],
        [First_Agreement_Issue_Date],
        [Focus_Created_Id],
        [Forename],
        [Forename_Soundex],
        [Gender_Code],
        [Home_Tel_Num],
        [Income_Day],
        [Initials],
        [Iq_Category_Code],
        [Last_Agreement_Date],
        [Last_Agreement_Issue_Value],
        [Last_Agreement_Rate],
        [Last_Payment_Accounting_Week_Num],
        [Last_Rate_Increase_Value],
        [Loan_Arrears_Stage],
        [Local_District],
        [Local_District_Soundex],
        [Marketing_Mail_Allowed_Bln],
        [Marketing_Source_Code],
        [Marketing_Tel_Calls_Allowed_Bln],
        [Max_Avg_Payment_Over_The_Last_N_Weeks],
        [Max_Avg_Rate_Over_The_Last_N_Weeks],
        [Max_Total_Outstanding_Balance_In_Last_N_Months],
        [Max_Total_Rate_In_Last_N_Months],
        [Mobile_Tel_Num],
        [Mv_Insurance_Renewal_Month_Code],
        [Mv_Ownership_Code],
        [Nearest_Relative_Address],
        [Nearest_Relative_Name],
        [Nearest_Relative_Relationship_To_Customer],
        [Nearest_Relative_Tel_Num],
        [Num_Of_Consecutive_Misses],
        [Num_Of_Rd_Cheques_In_Last_N_Weeks],
        [Num_Of_Weeks_Since_Last_Rate_Increase],
        [Occupation],
        [Original_Bis_Num],
        [Original_BIS_Reference_File_Bln],
        [Other_Loan_Indicator_Code],
        [Paid_Up_Date],
        [Paid_Up_Week],
        [Password],
        [Previsited_Manager_Id],
        [Pin],
        [Print_On_Collecting_List_Bln],
        [Pu_Reinstated_Date],
        [Pu_Reinstated_Week],
        [Po_Box],
        [Previous_Doc_Arrears_Stage],
        [Previous_Loan_Arrears_Stage],
        [Previous_Week_Segment_Db_Id],
        [Previous_Week_Segment_Id],
        [Rd_Cheques_In_Last_N_Weeks_Value],
        [Repayment_Frequency_Code],
        [Reservable_Bln],
        [Residency_Status_Code],
        [Store_Card_Indicator_Code],
        [Suppress_All_Contact_Bln],
        [Surname],
        [Surname_Soundex],
        [Title_Code],
        [Transfer_Pending_Bln],
        [Untraceable_Bln],
        [Untraceable_Date],
        [Untraceable_Week],
        [Written_Off_Date],
        [Written_Off_Week],
        [Dt_Generation_Id],
        [Dt_Transaction_Id],
        [Dt_Write_Bln],
        [Last_Updated_Datetime],
        [Last_Updated_Id],
        [Maiden_Name],
        [Mothers_Maiden_Name],
        [Town_Of_Birth],
        [Marketing_Electronic_Mail_Allowed_Bln],
        [Third_Party_Disclosure_Allowed_Bln],
        [MARKETING_REFERENCE_NUMBER],
        [Total_Income_Proved],
        [Total_Income_Unproved],
        [Total_Expenses],
        [Time_At_Address_Months],
        [Time_At_Address_Years],
        [Time_In_Employment_Months],
        [Time_In_Employment_Years],
        [Identification_Document_Reference],
        [Identification_Document_Type_Code],
        [Credit_Check_Allowed_Bln],
        [Maiden_Title],
        [Mothers_Maiden_Title],
        [Data_Disclosure_Allowed_Bln],
        [Historical_Data_Disclosure_Allowed_Bln],
        [Nationality_Code],
        [Education_Type_Code],
        [Marital_Status_Type_Code],
        [Finance_Loan_Arrears_Stage],
        [Finance_Num_Of_Consecutive_Misses],
        [Stage_Target_Value],
        [Global_Transaction_Key],
        [Receipt_Preference_Type_Code],
        [Email_Receipts_Bln],
        [Portal_Access_Bln],
        [Depersonalisation_Date],
        [Depersonalisation_Reason_Code],
        [Confirmation_Slip_Required_Bln],
        [Hide_Receipt_Issued_Before]
    )
VALUES (
        0,
        -- [Customer_Id] ** SE COLOCA EL ID DE LA VENTA GENERADA
        1,
        -- [Address_Changes_Count]
        2075000000335,
        -- [Agency_Id] ** SE ACTUALIZA A LA AGENCIA DE LA CUAL SE HIZO LA VENTA
        2021,
        -- [Agency_Segment_Db_Id]
        10464,
        -- [Agency_Segment_Id]
        330,
        -- [Agency_Sequence_Num]
        0,
        -- [Avg_Overdue_Weeks]
        'UN',
        -- [Bank_Account_Indicator_Code]
        '1995-12-22',
        -- [Birth_Date] ** FECHA DE NACIMIENTO DEL CLIENTE DE LA VENTA
        0,
        -- [BIS_To_FOCUS_Transfer_Bln]
        NULL,
        -- [Cancellation_Week]
        NULL,
        -- [Cdr_Referred_Date]
        NULL,
        -- [Child_1_Birth_Year]
        NULL,
        -- [Child_2_Birth_Year]
        NULL,
        -- [Child_3_Birth_Year]
        NULL,
        -- [Child_4_Birth_Year]
        NULL,
        -- [Child_5_Birth_Year]
        NULL,
        -- [Child_6_Birth_Year]
        100,
        -- [Collection_Pct]
        'MEX',
        -- [Company_Code]
        0,
        -- [Correspondence_Bln]
        '2022-01-03',
        -- [Creation_Date] ** FECHA DEL DIA
        202201,
        -- [Creation_Week] ** SEMANA ACTUAL
        'UN',
        -- [Credit_Card_Indicator_Code]
        'WK',
        -- [Customer_Income_Frequency_Code]
        0,
        -- [Customer_Lower_Commission_Target]
        0.0,
        -- [Customer_Maintain_Quality_Message]
        0.0,
        -- [Customer_Rate]
        'CC',
        -- [Customer_Status_Code]
        'MX',
        -- [Customer_Language_Code]
        'DA',
        -- [Customer_Type_Code]
        '2022-01-03',
        -- [Customer_Type_Date] ** FECHA DEL DIA
        202201,
        -- [Customer_Type_Week] ** SEMANA ACTUAL
        0,
        -- [Customer_Upper_Commission_Target]
        'UN',
        -- [Debit_Card_Indicator_Code]
        0,
        -- [Deceased_Bln]
        0,
        -- [Deleted_Flag]
        'Adán Primero Juárez',
        -- [Display_Name] ** NOMBRE COMPLETO DEL CLIENTE DE LA VENTA
        3000,
        -- [Disposable_Income]
        '2022-01-03',
        -- [Disposable_Income_Date] ** FECHA DEL DIA DEL PAGO DEL CLIENTE
        0,
        -- [Doc_Arrears_Stage]
        NULL,
        -- [Email_Address]
        NULL,
        -- [Employer_Address]
        NULL,
        -- [Employer_Name]
        NULL,
        -- [Employer_Tel_Num]
        'SE',
        -- [Employment_Status_Code]
        '9396/PEWE',
        -- [External_System_Created_Id]
        NULL,
        -- [External_Unique]
        '2022-01-03',
        -- [First_Agreement_Creation_Date] ** FECHA DE 8 DIAS DESPUES DE PAGARLE AL CLIENTE
        202201,
        -- [First_Agreement_Creation_Week]
        '2022-01-03',
        -- [First_Agreement_Issue_Date]
        1000000092,
        -- [Focus_Created_Id]
        'Adán',
        -- [Forename] ** NOMBRE DE LA PERSONA
        'P362',
        -- [Forename_Soundex]
        'FE',
        -- [Gender_Code]
        NULL,
        -- [Home_Tel_Num]
        NULL,
        -- [Income_Day]
        'P',
        -- [Initials]
        NULL,
        -- [Iq_Category_Code]
        NULL,
        -- [Last_Agreement_Date]
        1500,
        -- [Last_Agreement_Issue_Value]
        97.5,
        -- [Last_Agreement_Rate]
        202530,
        -- [Last_Payment_Accounting_Week_Num]
        0,
        -- [Last_Rate_Increase_Value]
        0,
        -- [Loan_Arrears_Stage]
        NULL,
        -- [Local_District]
        0,
        -- [Local_District_Soundex]
        1,
        -- [Marketing_Mail_Allowed_Bln]
        'OT',
        -- [Marketing_Source_Code]
        1,
        -- [Marketing_Tel_Calls_Allowed_Bln]
        NULL,
        -- [Max_Avg_Payment_Over_The_Last_N_Weeks]
        NULL,
        -- [Max_Avg_Rate_Over_The_Last_N_Weeks]
        NULL,
        -- [Max_Total_Outstanding_Balance_In_Last_N_Months]
        NULL,
        -- [Max_Total_Rate_In_Last_N_Months]
        5511243802,
        -- [Mobile_Tel_Num]
        NULL,
        -- [Mv_Insurance_Renewal_Month_Code]
        'UN',
        -- [Mv_Ownership_Code]
        'CJON ABASOLO 10 LOC SAN GREGORIO AZTOTOACAN 74130 SAN SALVADOR EL VERDE, PUE.',
        -- [Nearest_Relative_Address] ** DIRECCION
        'Alvaro Lopez',
        -- [Nearest_Relative_Name]
        'Yerno',
        -- [Nearest_Relative_Relationship_To_Customer]
        5831290872,
        -- [Nearest_Relative_Tel_Num]
        0,
        -- [Num_Of_Consecutive_Misses]
        NULL,
        -- [Num_Of_Rd_Cheques_In_Last_N_Weeks]
        0,
        -- [Num_Of_Weeks_Since_Last_Rate_Increase]
        'comerciante',
        -- [Occupation]
        '9396C0372100',
        -- [Original_Bis_Num]
        0,
        -- [Original_BIS_Reference_File_Bln]
        'UN',
        -- [Other_Loan_Indicator_Code]
        NULL,
        -- [Paid_Up_Date]
        NULL,
        -- [Paid_Up_Week]
        NULL,
        -- [Password]
        NULL,
        -- [Previsited_Manager_Id]
        'CAMP660623SP1',
        -- [Pin]
        1,
        -- [Print_On_Collecting_List_Bln]
        NULL,
        -- [Pu_Reinstated_Date]
        NULL,
        -- [Pu_Reinstated_Week]
        NULL,
        -- [Po_Box]
        0,
        -- [Previous_Doc_Arrears_Stage]
        0,
        -- [Previous_Loan_Arrears_Stage]
        NULL,
        -- [Previous_Week_Segment_Db_Id]
        NULL,
        -- [Previous_Week_Segment_Id]
        NULL,
        -- [Rd_Cheques_In_Last_N_Weeks_Value]
        'WK',
        -- [Repayment_Frequency_Code]
        1,
        -- [Reservable_Bln]
        'OW',
        -- [Residency_Status_Code]
        'UN',
        -- [Store_Card_Indicator_Code]
        0,
        -- [Suppress_All_Contact_Bln]
        'Calva Martinez',
        -- [Surname]
        'C415',
        -- [Surname_Soundex]
        'SA',
        -- [Title_Code]
        0,
        -- [Transfer_Pending_Bln]
        0,
        -- [Untraceable_Bln]
        NULL,
        -- [Untraceable_Date]
        NULL,
        -- [Untraceable_Week]
        NULL,
        -- [Written_Off_Date]
        NULL,
        -- [Written_Off_Week]
        2057,
        -- [Dt_Generation_Id]
        '2A72C44C-C48E-4451-BABB-CAC56DAB15B0',
        -- [Dt_Transaction_Id]
        1,
        -- [Dt_Write_Bln]
        '2025-07-31',
        -- [Last_Updated_Datetime]
        2021001685247,
        -- [Last_Updated_Id]
        NULL,
        -- [Maiden_Name]
        NULL,
        -- [Mothers_Maiden_Name]
        NULL,
        -- [Town_Of_Birth]
        1,
        -- [Marketing_Electronic_Mail_Allowed_Bln]
        1,
        -- [Third_Party_Disclosure_Allowed_Bln]
        NULL,
        -- [MARKETING_REFERENCE_NUMBER]
        0,
        -- [Total_Income_Proved]
        8000,
        -- [Total_Income_Unproved]
        5000,
        -- [Total_Expenses]
        NULL,
        -- [Time_At_Address_Months]
        NULL,
        -- [Time_At_Address_Years]
        NULL,
        -- [Time_In_Employment_Months]
        NULL,
        -- [Time_In_Employment_Years]
        NULL,
        -- [Identification_Document_Reference]
        NULL,
        -- [Identification_Document_Type_Code]
        NULL,
        -- [Credit_Check_Allowed_Bln]
        NULL,
        -- [Maiden_Title]
        NULL,
        -- [Mothers_Maiden_Title]
        NULL,
        -- [Data_Disclosure_Allowed_Bln]
        NULL,
        -- [Historical_Data_Disclosure_Allowed_Bln]
        NULL,
        -- [Nationality_Code]
        NULL,
        -- [Education_Type_Code]
        NULL,
        -- [Marital_Status_Type_Code]
        0,
        -- [Finance_Loan_Arrears_Stage]
        0,
        -- [Finance_Num_Of_Consecutive_Misses]
        161.69,
        -- [Stage_Target_Value]
        NULL,
        -- [Global_Transaction_Key]
        'ER',
        -- [Receipt_Preference_Type_Code]
        0,
        -- [Email_Receipts_Bln]
        1,
        -- [Portal_Access_Bln]
        NULL,
        -- [Depersonalisation_Date]
        NULL,
        -- [Depersonalisation_Reason_Code]
        NULL,
        -- [Confirmation_Slip_Required_Bln]
        NULL -- [Hide_Receipt_Issued_Before]
    );