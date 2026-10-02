INSERT INTO [CNFS_uat].[NFS_DBO].[Agreement_Table]
(
[Agreement_Db_Id]
,[Absolute_Arrears]
,[Actual_Paid_Up_Date]
,[Actual_Paid_Up_Week]
,[Agreement_Num]
,[Agreement_Status_Code]
,[Cancellation_Date]
,[Cancellation_Week]
,[Cancellation_Value]
,[Cancelled_By_Representative_Id]
,[Creation_Date]
,[Creation_Week]
,[Company_Code]
,[Customer_Id]
,[Customer_Type_Code_At_Issue]
,[Deleted_Flag]
,[Early_Settlement_Bln]
,[Early_Settlement_Rebate_Value]
,[Early_Settlement_Rebate_Contra_Value]
,[Final_Instalment_Value]
,[First_Instalment_Value]
,[First_Payment_Due_Date]
,[Instalment_Periods_To_Date]
,[Is_Adjustment_Bln]
,[Issue_Date]
,[Issue_Value]
,[Issuing_Representative_Id]
,[Late_Issue_Bln]
,[Linked_Agreement_Number]
,[Loan_Reason_Code]
,[Next_Payment_Due]
,[Normal_Due_Day_In_Month]
,[Number_Of_Default_Charge_Applications_To_Date]
,[Outstanding_Balance]
,[Outstanding_Default_Charge]
,[Product_Category_Code]
,[Product_Version_Db_Id]
,[Product_Version_Id]
,[Regular_Instalment_Value]
,[Third_Party_Retailer_Event_Code]
,[Total_Amount_Payable]
,[Transferred_Bln]
,[Settlement_Balance]
,[Written_Back_Value]
,[Written_Off_Date]
,[Written_Off_Value]
,[Written_Off_Week]
,[Dt_Generation_Id]
,[Dt_Transaction_Id]
,[Dt_Write_Bln]
,[Last_Updated_Datetime]
,[Last_Updated_Id]
,[Annual_Interest_Rate]
,[Prevailing_Principal]
,[Company_Rate_Cap_Id]
,[Final_Instalment_Value_At_Issue]
,[First_Instalment_Value_At_Issue]
,[Regular_Instalment_Value_At_Issue]
,[Total_Amount_Payable_At_Issue]
,[Customer_Repayment_Account_Num]
,[Chosen_Payment_Due_Day]
,[Early_Settlement_Charge_Applied]
,[Refinancing_Agreement_Id]
,[Refinancing_Agreement_Db_Id]
,[Refinanced_Week]
,[Reporting_Week_Num]
,[Agreement_Form_Corrected_Bln]
,[Customer_Business_Id]
,[Customer_Business_Db_Id]
,[Credit_Check_Reference]
,[Codebtor_Id]
,[Finance_Absolute_Arrears]
,[Global_Transaction_Key]
,[Agreement_Source_Code]
,[Agreement_Issue_Location_Code]
,[Promotion_Reason_Code]
)
VALUES
(
 2000        -- Agreement_Db_Id -TODOS LOS CONTRATOS SE ENCUENTRAN EN ESTA VERSIÓN *
,0        -- Absolute_Arrears  -Adeudo pendiente
,'2025-08-01 00:00:00'     -- Actual_Paid_Up_Date -Fecha basada en el ultimo pago
,06     -- Actual_Paid_Up_Week -Semana en que se registro esta semana 
,844568683-- Agreement_Num * LILI
,'AC'     -- Agreement_Status_Code -- Activo = AC Pagado =PU * LILI
,NULL     -- Cancellation_Date 
,NULL     -- Cancellation_Week
,NULL        -- Cancellation_Value 
,NULL     -- Cancelled_By_Representative_Id
,'2026-02-06' -- Creation_Date*
,202606   -- Creation_Week *
,'MX'     -- Company_Code
,2006001287879 -- Customer_Id* LILI
,01      -- Customer_Type_Code_At_Issue 
,0        -- Deleted_Flag
,0        -- Early_Settlement_Bln - Si tiene 1 puede anticipar pagos 
,0        -- Early_Settlement_Rebate_Value - 0
,0        -- Early_Settlement_Rebate_Contra_Value 
,500      -- Final_Instalment_Value *REVISAR TABULADOR
,500      -- First_Instalment_Value *REVISAR TABULADOR
,'2026-02-06' -- First_Payment_Due_Date *
,22        -- Instalment_Periods_To_Date
,0        -- Is_Adjustment_Bln -0
,'2026-02-06' -- Issue_Date*
,13000     -- Issue_Value - Valor del monto del prestamo 
,1001        -- Issuing_Representative_Id 
,0        -- Late_Issue_Bln
,NULL     -- Linked_Agreement_Number
,01     -- Loan_Reason_Code
,'2026-02-13' -- Next_Payment_Due --Siguiente semana a la fecha de creacion
,15        -- Normal_Due_Day_In_Month
,0        -- Number_Of_Default_Charge_Applications_To_Date
,31744.85     -- Outstanding_Balance * LILI
,0        -- Outstanding_Default_Charge --Cargos monatorios
,01     -- Product_Category_Code
,2000        -- Product_Version_Db_Id siempre va en conjunto con el primer campo 
,118        -- Product_Version_Id - debe apuntar hacia el producto y a un termino 
,622.46      -- Regular_Instalment_Value - monto semanal 
,01     -- Third_Party_Retailer_Event_Code
,27176.070000     -- Total_Amount_Payable --Monto total a  pagar 
,0        -- Transferred_Bln
,31744.85     -- Settlement_Balance * LILI
,0        -- Written_Back_Value ---
,NULL     -- Written_Off_Date
,0        -- Written_Off_Value
,NULL     -- Written_Off_Week
,1        -- Dt_Generation_Id
,NEWID() -- Dt_Transaction_Id -- 
,0        -- Dt_Write_Bln
,'2026-02-06' -- Last_Updated_Datetime --Fecha de modificacion del contrato
,1001        -- Last_Updated_Id
,10.5000000000000    -- Annual_Interest_Rate
,5500.000000     -- Prevailing_Principal
,1        -- Company_Rate_Cap_Id
,500      -- Final_Instalment_Value_At_Issue
,500      -- First_Instalment_Value_At_Issue
,622.46      -- Regular_Instalment_Value_At_Issue * LILI
,6000     -- Total_Amount_Payable_At_Issue
,'ACC123456789' -- Customer_Repayment_Account_Num
,15        -- Chosen_Payment_Due_Day
,0        -- Early_Settlement_Charge_Applied
,NULL     -- Refinancing_Agreement_Id
,NULL     -- Refinancing_Agreement_Db_Id
,NULL     -- Refinanced_Week
,NULL   -- Reporting_Week_Num
,0        -- Agreement_Form_Corrected_Bln
,NULL     -- Customer_Business_Id
,NULL     -- Customer_Business_Db_Id
,'CREDITCHK001'     -- Credit_Check_Reference
,NULL     -- Codebtor_Id
,0        -- Finance_Absolute_Arrears
,NEWID()     -- Global_Transaction_Key
,01    -- Agreement_Source_Code
,01     -- Agreement_Issue_Location_Code
,01     -- Promotion_Reason_Code
)

INSERT INTO [CNFS_uat].[NFS_DBO].[Agreement_Table]
(
[Agreement_Db_Id]
,[Absolute_Arrears]
,[Actual_Paid_Up_Date]
,[Actual_Paid_Up_Week]
,[Agreement_Num]
,[Agreement_Status_Code]
,[Cancellation_Date]
,[Cancellation_Week]
,[Cancellation_Value]
,[Cancelled_By_Representative_Id]
,[Creation_Date]
,[Creation_Week]
,[Company_Code]
,[Customer_Id]
,[Customer_Type_Code_At_Issue]
,[Deleted_Flag]
,[Early_Settlement_Bln]
,[Early_Settlement_Rebate_Value]
,[Early_Settlement_Rebate_Contra_Value]
,[Final_Instalment_Value]
,[First_Instalment_Value]
,[First_Payment_Due_Date]
,[Instalment_Periods_To_Date]
,[Is_Adjustment_Bln]
,[Issue_Date]
,[Issue_Value]
,[Issuing_Representative_Id]
,[Late_Issue_Bln]
,[Linked_Agreement_Number]
,[Loan_Reason_Code]
,[Next_Payment_Due]
,[Normal_Due_Day_In_Month]
,[Number_Of_Default_Charge_Applications_To_Date]
,[Outstanding_Balance]
,[Outstanding_Default_Charge]
,[Product_Category_Code]
,[Product_Version_Db_Id]
,[Product_Version_Id]
,[Regular_Instalment_Value]
,[Third_Party_Retailer_Event_Code]
,[Total_Amount_Payable]
,[Transferred_Bln]
,[Settlement_Balance]
,[Written_Back_Value]
,[Written_Off_Date]
,[Written_Off_Value]
,[Written_Off_Week]
,[Dt_Generation_Id]
,[Dt_Transaction_Id]
,[Dt_Write_Bln]
,[Last_Updated_Datetime]
,[Last_Updated_Id]
,[Annual_Interest_Rate]
,[Prevailing_Principal]
,[Company_Rate_Cap_Id]
,[Final_Instalment_Value_At_Issue]
,[First_Instalment_Value_At_Issue]
,[Regular_Instalment_Value_At_Issue]
,[Total_Amount_Payable_At_Issue]
,[Customer_Repayment_Account_Num]
,[Chosen_Payment_Due_Day]
,[Early_Settlement_Charge_Applied]
,[Refinancing_Agreement_Id]
,[Refinancing_Agreement_Db_Id]
,[Refinanced_Week]
,[Reporting_Week_Num]
,[Agreement_Form_Corrected_Bln]
,[Customer_Business_Id]
,[Customer_Business_Db_Id]
,[Credit_Check_Reference]
,[Codebtor_Id]
,[Finance_Absolute_Arrears]
,[Global_Transaction_Key]
,[Agreement_Source_Code]
,[Agreement_Issue_Location_Code]
,[Promotion_Reason_Code]
)
VALUES
(
 2000        -- Agreement_Db_Id -TODOS LOS CONTRATOS SE ENCUENTRAN EN ESTA VERSIÓN *
,0        -- Absolute_Arrears  -Adeudo pendiente
,'2025-08-01 00:00:00'     -- Actual_Paid_Up_Date -Fecha basada en el ultimo pago
,06     -- Actual_Paid_Up_Week -Semana en que se registro esta semana 
,844546876-- Agreement_Num * LILI
,'AC'     -- Agreement_Status_Code -- Activo = AC Pagado =PU * LILI
,NULL     -- Cancellation_Date 
,NULL     -- Cancellation_Week
,NULL        -- Cancellation_Value 
,NULL     -- Cancelled_By_Representative_Id
,'2026-02-06' -- Creation_Date*
,202606   -- Creation_Week *
,'MX'     -- Company_Code
,2006001287879 -- Customer_Id* LILI
,01      -- Customer_Type_Code_At_Issue 
,0        -- Deleted_Flag
,0        -- Early_Settlement_Bln - Si tiene 1 puede anticipar pagos 
,0        -- Early_Settlement_Rebate_Value - 0
,0        -- Early_Settlement_Rebate_Contra_Value 
,500      -- Final_Instalment_Value *REVISAR TABULADOR
,500      -- First_Instalment_Value *REVISAR TABULADOR
,'2026-02-06' -- First_Payment_Due_Date *
,22        -- Instalment_Periods_To_Date
,0        -- Is_Adjustment_Bln -0
,'2026-02-06' -- Issue_Date*
,13000     -- Issue_Value - Valor del monto del prestamo 
,1001        -- Issuing_Representative_Id 
,0        -- Late_Issue_Bln
,NULL     -- Linked_Agreement_Number
,01     -- Loan_Reason_Code
,'2026-02-13' -- Next_Payment_Due --Siguiente semana a la fecha de creacion
,15        -- Normal_Due_Day_In_Month
,0        -- Number_Of_Default_Charge_Applications_To_Date
,51341.96     -- Outstanding_Balance * LILI
,0        -- Outstanding_Default_Charge --Cargos monatorios
,01     -- Product_Category_Code
,2000        -- Product_Version_Db_Id siempre va en conjunto con el primer campo 
,118        -- Product_Version_Id - debe apuntar hacia el producto y a un termino 
,841.72      -- Regular_Instalment_Value - monto semanal 
,01     -- Third_Party_Retailer_Event_Code
,27176.070000     -- Total_Amount_Payable --Monto total a  pagar 
,0        -- Transferred_Bln
,51341.96     -- Settlement_Balance * LILI
,0        -- Written_Back_Value ---
,NULL     -- Written_Off_Date
,0        -- Written_Off_Value
,NULL     -- Written_Off_Week
,1        -- Dt_Generation_Id
,'50CE307D-6E8C-4101-8B81-81A506B37F86' -- Dt_Transaction_Id -- 
,0        -- Dt_Write_Bln
,'2026-02-06' -- Last_Updated_Datetime --Fecha de modificacion del contrato
,1001        -- Last_Updated_Id
,10.5000000000000    -- Annual_Interest_Rate
,5500.000000     -- Prevailing_Principal
,1        -- Company_Rate_Cap_Id
,500      -- Final_Instalment_Value_At_Issue
,500      -- First_Instalment_Value_At_Issue
,841.72      -- Regular_Instalment_Value_At_Issue * LILI
,6000     -- Total_Amount_Payable_At_Issue
,'ACC123456789' -- Customer_Repayment_Account_Num
,15        -- Chosen_Payment_Due_Day
,0        -- Early_Settlement_Charge_Applied
,NULL     -- Refinancing_Agreement_Id
,NULL     -- Refinancing_Agreement_Db_Id
,NULL     -- Refinanced_Week
,NULL   -- Reporting_Week_Num
,0        -- Agreement_Form_Corrected_Bln
,NULL     -- Customer_Business_Id
,NULL     -- Customer_Business_Db_Id
,'CREDITCHK001'     -- Credit_Check_Reference
,NULL     -- Codebtor_Id
,0        -- Finance_Absolute_Arrears
,'D3C955D0-8595-4F99-93BA-B10869AD2438'     -- Global_Transaction_Key
,01    -- Agreement_Source_Code
,01     -- Agreement_Issue_Location_Code
,01     -- Promotion_Reason_Code
)

INSERT INTO [CNFS_uat].[NFS_DBO].[Agreement_Table]
(
[Agreement_Db_Id]
,[Absolute_Arrears]
,[Actual_Paid_Up_Date]
,[Actual_Paid_Up_Week]
,[Agreement_Num]
,[Agreement_Status_Code]
,[Cancellation_Date]
,[Cancellation_Week]
,[Cancellation_Value]
,[Cancelled_By_Representative_Id]
,[Creation_Date]
,[Creation_Week]
,[Company_Code]
,[Customer_Id]
,[Customer_Type_Code_At_Issue]
,[Deleted_Flag]
,[Early_Settlement_Bln]
,[Early_Settlement_Rebate_Value]
,[Early_Settlement_Rebate_Contra_Value]
,[Final_Instalment_Value]
,[First_Instalment_Value]
,[First_Payment_Due_Date]
,[Instalment_Periods_To_Date]
,[Is_Adjustment_Bln]
,[Issue_Date]
,[Issue_Value]
,[Issuing_Representative_Id]
,[Late_Issue_Bln]
,[Linked_Agreement_Number]
,[Loan_Reason_Code]
,[Next_Payment_Due]
,[Normal_Due_Day_In_Month]
,[Number_Of_Default_Charge_Applications_To_Date]
,[Outstanding_Balance]
,[Outstanding_Default_Charge]
,[Product_Category_Code]
,[Product_Version_Db_Id]
,[Product_Version_Id]
,[Regular_Instalment_Value]
,[Third_Party_Retailer_Event_Code]
,[Total_Amount_Payable]
,[Transferred_Bln]
,[Settlement_Balance]
,[Written_Back_Value]
,[Written_Off_Date]
,[Written_Off_Value]
,[Written_Off_Week]
,[Dt_Generation_Id]
,[Dt_Transaction_Id]
,[Dt_Write_Bln]
,[Last_Updated_Datetime]
,[Last_Updated_Id]
,[Annual_Interest_Rate]
,[Prevailing_Principal]
,[Company_Rate_Cap_Id]
,[Final_Instalment_Value_At_Issue]
,[First_Instalment_Value_At_Issue]
,[Regular_Instalment_Value_At_Issue]
,[Total_Amount_Payable_At_Issue]
,[Customer_Repayment_Account_Num]
,[Chosen_Payment_Due_Day]
,[Early_Settlement_Charge_Applied]
,[Refinancing_Agreement_Id]
,[Refinancing_Agreement_Db_Id]
,[Refinanced_Week]
,[Reporting_Week_Num]
,[Agreement_Form_Corrected_Bln]
,[Customer_Business_Id]
,[Customer_Business_Db_Id]
,[Credit_Check_Reference]
,[Codebtor_Id]
,[Finance_Absolute_Arrears]
,[Global_Transaction_Key]
,[Agreement_Source_Code]
,[Agreement_Issue_Location_Code]
,[Promotion_Reason_Code]
)
VALUES
(
 2000        -- Agreement_Db_Id -TODOS LOS CONTRATOS SE ENCUENTRAN EN ESTA VERSIÓN *
,0        -- Absolute_Arrears  -Adeudo pendiente
,'2025-08-01 00:00:00'     -- Actual_Paid_Up_Date -Fecha basada en el ultimo pago
,06     -- Actual_Paid_Up_Week -Semana en que se registro esta semana 
,844575575-- Agreement_Num * LILI
,'AC'     -- Agreement_Status_Code -- Activo = AC Pagado =PU * LILI
,NULL     -- Cancellation_Date 
,NULL     -- Cancellation_Week
,NULL        -- Cancellation_Value 
,NULL     -- Cancelled_By_Representative_Id
,'2026-02-06' -- Creation_Date*
,202606   -- Creation_Week *
,'MX'     -- Company_Code
,2006001287879 -- Customer_Id* LILI
,01      -- Customer_Type_Code_At_Issue 
,0        -- Deleted_Flag
,0        -- Early_Settlement_Bln - Si tiene 1 puede anticipar pagos 
,0        -- Early_Settlement_Rebate_Value - 0
,0        -- Early_Settlement_Rebate_Contra_Value 
,500      -- Final_Instalment_Value *REVISAR TABULADOR
,500      -- First_Instalment_Value *REVISAR TABULADOR
,'2026-02-06' -- First_Payment_Due_Date *
,22        -- Instalment_Periods_To_Date
,0        -- Is_Adjustment_Bln -0
,'2026-02-06' -- Issue_Date*
,13000     -- Issue_Value - Valor del monto del prestamo 
,1001        -- Issuing_Representative_Id 
,0        -- Late_Issue_Bln
,NULL     -- Linked_Agreement_Number
,01     -- Loan_Reason_Code
,'2026-02-13' -- Next_Payment_Due --Siguiente semana a la fecha de creacion
,15        -- Normal_Due_Day_In_Month
,0        -- Number_Of_Default_Charge_Applications_To_Date
,20497.82     -- Outstanding_Balance * LILI
,0        -- Outstanding_Default_Charge --Cargos monatorios
,01     -- Product_Category_Code
,2000        -- Product_Version_Db_Id siempre va en conjunto con el primer campo 
,118        -- Product_Version_Id - debe apuntar hacia el producto y a un termino 
,481.59      -- Regular_Instalment_Value - monto semanal 
,01     -- Third_Party_Retailer_Event_Code
,27176.070000     -- Total_Amount_Payable --Monto total a  pagar 
,0        -- Transferred_Bln
,20497.82     -- Settlement_Balance * LILI
,0        -- Written_Back_Value ---
,NULL     -- Written_Off_Date
,0        -- Written_Off_Value
,NULL     -- Written_Off_Week
,1        -- Dt_Generation_Id
,'50CE307D-6E8C-4101-8B81-81A506B37F86' -- Dt_Transaction_Id -- 
,0        -- Dt_Write_Bln
,'2026-02-06' -- Last_Updated_Datetime --Fecha de modificacion del contrato
,1001        -- Last_Updated_Id
,10.5000000000000    -- Annual_Interest_Rate
,5500.000000     -- Prevailing_Principal
,1        -- Company_Rate_Cap_Id
,500      -- Final_Instalment_Value_At_Issue
,500      -- First_Instalment_Value_At_Issue
,481.59      -- Regular_Instalment_Value_At_Issue * LILI
,6000     -- Total_Amount_Payable_At_Issue
,'ACC123456789' -- Customer_Repayment_Account_Num
,15        -- Chosen_Payment_Due_Day
,0        -- Early_Settlement_Charge_Applied
,NULL     -- Refinancing_Agreement_Id
,NULL     -- Refinancing_Agreement_Db_Id
,NULL     -- Refinanced_Week
,NULL   -- Reporting_Week_Num
,0        -- Agreement_Form_Corrected_Bln
,NULL     -- Customer_Business_Id
,NULL     -- Customer_Business_Db_Id
,'CREDITCHK001'     -- Credit_Check_Reference
,NULL     -- Codebtor_Id
,0        -- Finance_Absolute_Arrears
,'D3C955D0-8595-4F99-93BA-B10869AD2438'     -- Global_Transaction_Key
,01    -- Agreement_Source_Code
,01     -- Agreement_Issue_Location_Code
,01     -- Promotion_Reason_Code
)

INSERT INTO [CNFS_uat].[NFS_DBO].[Agreement_Table]
(
[Agreement_Db_Id]
,[Absolute_Arrears]
,[Actual_Paid_Up_Date]
,[Actual_Paid_Up_Week]
,[Agreement_Num]
,[Agreement_Status_Code]
,[Cancellation_Date]
,[Cancellation_Week]
,[Cancellation_Value]
,[Cancelled_By_Representative_Id]
,[Creation_Date]
,[Creation_Week]
,[Company_Code]
,[Customer_Id]
,[Customer_Type_Code_At_Issue]
,[Deleted_Flag]
,[Early_Settlement_Bln]
,[Early_Settlement_Rebate_Value]
,[Early_Settlement_Rebate_Contra_Value]
,[Final_Instalment_Value]
,[First_Instalment_Value]
,[First_Payment_Due_Date]
,[Instalment_Periods_To_Date]
,[Is_Adjustment_Bln]
,[Issue_Date]
,[Issue_Value]
,[Issuing_Representative_Id]
,[Late_Issue_Bln]
,[Linked_Agreement_Number]
,[Loan_Reason_Code]
,[Next_Payment_Due]
,[Normal_Due_Day_In_Month]
,[Number_Of_Default_Charge_Applications_To_Date]
,[Outstanding_Balance]
,[Outstanding_Default_Charge]
,[Product_Category_Code]
,[Product_Version_Db_Id]
,[Product_Version_Id]
,[Regular_Instalment_Value]
,[Third_Party_Retailer_Event_Code]
,[Total_Amount_Payable]
,[Transferred_Bln]
,[Settlement_Balance]
,[Written_Back_Value]
,[Written_Off_Date]
,[Written_Off_Value]
,[Written_Off_Week]
,[Dt_Generation_Id]
,[Dt_Transaction_Id]
,[Dt_Write_Bln]
,[Last_Updated_Datetime]
,[Last_Updated_Id]
,[Annual_Interest_Rate]
,[Prevailing_Principal]
,[Company_Rate_Cap_Id]
,[Final_Instalment_Value_At_Issue]
,[First_Instalment_Value_At_Issue]
,[Regular_Instalment_Value_At_Issue]
,[Total_Amount_Payable_At_Issue]
,[Customer_Repayment_Account_Num]
,[Chosen_Payment_Due_Day]
,[Early_Settlement_Charge_Applied]
,[Refinancing_Agreement_Id]
,[Refinancing_Agreement_Db_Id]
,[Refinanced_Week]
,[Reporting_Week_Num]
,[Agreement_Form_Corrected_Bln]
,[Customer_Business_Id]
,[Customer_Business_Db_Id]
,[Credit_Check_Reference]
,[Codebtor_Id]
,[Finance_Absolute_Arrears]
,[Global_Transaction_Key]
,[Agreement_Source_Code]
,[Agreement_Issue_Location_Code]
,[Promotion_Reason_Code]
)
VALUES
(
 2000        -- Agreement_Db_Id -TODOS LOS CONTRATOS SE ENCUENTRAN EN ESTA VERSIÓN *
,0        -- Absolute_Arrears  -Adeudo pendiente
,'2025-08-01 00:00:00'     -- Actual_Paid_Up_Date -Fecha basada en el ultimo pago
,06     -- Actual_Paid_Up_Week -Semana en que se registro esta semana 
,575303232-- Agreement_Num * LILI
,'AC'     -- Agreement_Status_Code -- Activo = AC Pagado =PU * LILI
,NULL     -- Cancellation_Date 
,NULL     -- Cancellation_Week
,NULL        -- Cancellation_Value 
,NULL     -- Cancelled_By_Representative_Id
,'2026-02-06' -- Creation_Date*
,202606   -- Creation_Week *
,'MX'     -- Company_Code
,2007001672933 -- Customer_Id* LILI
,01      -- Customer_Type_Code_At_Issue 
,0        -- Deleted_Flag
,0        -- Early_Settlement_Bln - Si tiene 1 puede anticipar pagos 
,0        -- Early_Settlement_Rebate_Value - 0
,0        -- Early_Settlement_Rebate_Contra_Value 
,500      -- Final_Instalment_Value *REVISAR TABULADOR
,500      -- First_Instalment_Value *REVISAR TABULADOR
,'2026-02-06' -- First_Payment_Due_Date *
,22        -- Instalment_Periods_To_Date
,0        -- Is_Adjustment_Bln -0
,'2026-02-06' -- Issue_Date*
,13000     -- Issue_Value - Valor del monto del prestamo 
,1001        -- Issuing_Representative_Id 
,0        -- Late_Issue_Bln
,NULL     -- Linked_Agreement_Number
,01     -- Loan_Reason_Code
,'2026-02-13' -- Next_Payment_Due --Siguiente semana a la fecha de creacion
,15        -- Normal_Due_Day_In_Month
,0        -- Number_Of_Default_Charge_Applications_To_Date
,10490.06     -- Outstanding_Balance * LILI
,0        -- Outstanding_Default_Charge --Cargos monatorios
,01     -- Product_Category_Code
,2000        -- Product_Version_Db_Id siempre va en conjunto con el primer campo 
,118        -- Product_Version_Id - debe apuntar hacia el producto y a un termino 
,404.04      -- Regular_Instalment_Value - monto semanal 
,01     -- Third_Party_Retailer_Event_Code
,27176.070000     -- Total_Amount_Payable --Monto total a  pagar 
,0        -- Transferred_Bln
,10490.06     -- Settlement_Balance * LILI
,0        -- Written_Back_Value ---
,NULL     -- Written_Off_Date
,0        -- Written_Off_Value
,NULL     -- Written_Off_Week
,1        -- Dt_Generation_Id
,'50CE307D-6E8C-4101-8B81-81A506B37F86' -- Dt_Transaction_Id -- 
,0        -- Dt_Write_Bln
,'2026-02-06' -- Last_Updated_Datetime --Fecha de modificacion del contrato
,1001        -- Last_Updated_Id
,10.5000000000000    -- Annual_Interest_Rate
,5500.000000     -- Prevailing_Principal
,1        -- Company_Rate_Cap_Id
,500      -- Final_Instalment_Value_At_Issue
,500      -- First_Instalment_Value_At_Issue
,404.04      -- Regular_Instalment_Value_At_Issue * LILI
,6000     -- Total_Amount_Payable_At_Issue
,'ACC123456789' -- Customer_Repayment_Account_Num
,15        -- Chosen_Payment_Due_Day
,0        -- Early_Settlement_Charge_Applied
,NULL     -- Refinancing_Agreement_Id
,NULL     -- Refinancing_Agreement_Db_Id
,NULL     -- Refinanced_Week
,NULL   -- Reporting_Week_Num
,0        -- Agreement_Form_Corrected_Bln
,NULL     -- Customer_Business_Id
,NULL     -- Customer_Business_Db_Id
,'CREDITCHK001'     -- Credit_Check_Reference
,NULL     -- Codebtor_Id
,0        -- Finance_Absolute_Arrears
,'D3C955D0-8595-4F99-93BA-B10869AD2438'     -- Global_Transaction_Key
,01    -- Agreement_Source_Code
,01     -- Agreement_Issue_Location_Code
,01     -- Promotion_Reason_Code
)

INSERT INTO [CNFS_uat].[NFS_DBO].[Agreement_Table]
(
[Agreement_Db_Id]
,[Absolute_Arrears]
,[Actual_Paid_Up_Date]
,[Actual_Paid_Up_Week]
,[Agreement_Num]
,[Agreement_Status_Code]
,[Cancellation_Date]
,[Cancellation_Week]
,[Cancellation_Value]
,[Cancelled_By_Representative_Id]
,[Creation_Date]
,[Creation_Week]
,[Company_Code]
,[Customer_Id]
,[Customer_Type_Code_At_Issue]
,[Deleted_Flag]
,[Early_Settlement_Bln]
,[Early_Settlement_Rebate_Value]
,[Early_Settlement_Rebate_Contra_Value]
,[Final_Instalment_Value]
,[First_Instalment_Value]
,[First_Payment_Due_Date]
,[Instalment_Periods_To_Date]
,[Is_Adjustment_Bln]
,[Issue_Date]
,[Issue_Value]
,[Issuing_Representative_Id]
,[Late_Issue_Bln]
,[Linked_Agreement_Number]
,[Loan_Reason_Code]
,[Next_Payment_Due]
,[Normal_Due_Day_In_Month]
,[Number_Of_Default_Charge_Applications_To_Date]
,[Outstanding_Balance]
,[Outstanding_Default_Charge]
,[Product_Category_Code]
,[Product_Version_Db_Id]
,[Product_Version_Id]
,[Regular_Instalment_Value]
,[Third_Party_Retailer_Event_Code]
,[Total_Amount_Payable]
,[Transferred_Bln]
,[Settlement_Balance]
,[Written_Back_Value]
,[Written_Off_Date]
,[Written_Off_Value]
,[Written_Off_Week]
,[Dt_Generation_Id]
,[Dt_Transaction_Id]
,[Dt_Write_Bln]
,[Last_Updated_Datetime]
,[Last_Updated_Id]
,[Annual_Interest_Rate]
,[Prevailing_Principal]
,[Company_Rate_Cap_Id]
,[Final_Instalment_Value_At_Issue]
,[First_Instalment_Value_At_Issue]
,[Regular_Instalment_Value_At_Issue]
,[Total_Amount_Payable_At_Issue]
,[Customer_Repayment_Account_Num]
,[Chosen_Payment_Due_Day]
,[Early_Settlement_Charge_Applied]
,[Refinancing_Agreement_Id]
,[Refinancing_Agreement_Db_Id]
,[Refinanced_Week]
,[Reporting_Week_Num]
,[Agreement_Form_Corrected_Bln]
,[Customer_Business_Id]
,[Customer_Business_Db_Id]
,[Credit_Check_Reference]
,[Codebtor_Id]
,[Finance_Absolute_Arrears]
,[Global_Transaction_Key]
,[Agreement_Source_Code]
,[Agreement_Issue_Location_Code]
,[Promotion_Reason_Code]
)
VALUES
(
 2000        -- Agreement_Db_Id -TODOS LOS CONTRATOS SE ENCUENTRAN EN ESTA VERSIÓN *
,0        -- Absolute_Arrears  -Adeudo pendiente
,'2025-08-01 00:00:00'     -- Actual_Paid_Up_Date -Fecha basada en el ultimo pago
,06     -- Actual_Paid_Up_Week -Semana en que se registro esta semana 
,575331406-- Agreement_Num * LILI
,'AC'     -- Agreement_Status_Code -- Activo = AC Pagado =PU * LILI
,NULL     -- Cancellation_Date 
,NULL     -- Cancellation_Week
,NULL        -- Cancellation_Value 
,NULL     -- Cancelled_By_Representative_Id
,'2026-02-06' -- Creation_Date*
,202606   -- Creation_Week *
,'MX'     -- Company_Code
,2007001672933 -- Customer_Id* LILI
,01      -- Customer_Type_Code_At_Issue 
,0        -- Deleted_Flag
,0        -- Early_Settlement_Bln - Si tiene 1 puede anticipar pagos 
,0        -- Early_Settlement_Rebate_Value - 0
,0        -- Early_Settlement_Rebate_Contra_Value 
,500      -- Final_Instalment_Value *REVISAR TABULADOR
,500      -- First_Instalment_Value *REVISAR TABULADOR
,'2026-02-06' -- First_Payment_Due_Date *
,22        -- Instalment_Periods_To_Date
,0        -- Is_Adjustment_Bln -0
,'2026-02-06' -- Issue_Date*
,13000     -- Issue_Value - Valor del monto del prestamo 
,1001        -- Issuing_Representative_Id 
,0        -- Late_Issue_Bln
,NULL     -- Linked_Agreement_Number
,01     -- Loan_Reason_Code
,'2026-02-13' -- Next_Payment_Due --Siguiente semana a la fecha de creacion
,15        -- Normal_Due_Day_In_Month
,0        -- Number_Of_Default_Charge_Applications_To_Date
,4269.82     -- Outstanding_Balance * LILI
,0        -- Outstanding_Default_Charge --Cargos monatorios
,01     -- Product_Category_Code
,2000        -- Product_Version_Db_Id siempre va en conjunto con el primer campo 
,118        -- Product_Version_Id - debe apuntar hacia el producto y a un termino 
,80.75      -- Regular_Instalment_Value - monto semanal 
,01     -- Third_Party_Retailer_Event_Code
,27176.070000     -- Total_Amount_Payable --Monto total a  pagar 
,0        -- Transferred_Bln
,4269.82     -- Settlement_Balance * LILI
,0        -- Written_Back_Value ---
,NULL     -- Written_Off_Date
,0        -- Written_Off_Value
,NULL     -- Written_Off_Week
,1        -- Dt_Generation_Id
,'50CE307D-6E8C-4101-8B81-81A506B37F86' -- Dt_Transaction_Id -- 
,0        -- Dt_Write_Bln
,'2026-02-06' -- Last_Updated_Datetime --Fecha de modificacion del contrato
,1001        -- Last_Updated_Id
,10.5000000000000    -- Annual_Interest_Rate
,5500.000000     -- Prevailing_Principal
,1        -- Company_Rate_Cap_Id
,500      -- Final_Instalment_Value_At_Issue
,500      -- First_Instalment_Value_At_Issue
,80.75      -- Regular_Instalment_Value_At_Issue * LILI
,6000     -- Total_Amount_Payable_At_Issue
,'ACC123456789' -- Customer_Repayment_Account_Num
,15        -- Chosen_Payment_Due_Day
,0        -- Early_Settlement_Charge_Applied
,NULL     -- Refinancing_Agreement_Id
,NULL     -- Refinancing_Agreement_Db_Id
,NULL     -- Refinanced_Week
,NULL   -- Reporting_Week_Num
,0        -- Agreement_Form_Corrected_Bln
,NULL     -- Customer_Business_Id
,NULL     -- Customer_Business_Db_Id
,'CREDITCHK001'     -- Credit_Check_Reference
,NULL     -- Codebtor_Id
,0        -- Finance_Absolute_Arrears
,'D3C955D0-8595-4F99-93BA-B10869AD2438'     -- Global_Transaction_Key
,01    -- Agreement_Source_Code
,01     -- Agreement_Issue_Location_Code
,01     -- Promotion_Reason_Code
)

INSERT INTO [CNFS_uat].[NFS_DBO].[Agreement_Table]
(
[Agreement_Db_Id]
,[Absolute_Arrears]
,[Actual_Paid_Up_Date]
,[Actual_Paid_Up_Week]
,[Agreement_Num]
,[Agreement_Status_Code]
,[Cancellation_Date]
,[Cancellation_Week]
,[Cancellation_Value]
,[Cancelled_By_Representative_Id]
,[Creation_Date]
,[Creation_Week]
,[Company_Code]
,[Customer_Id]
,[Customer_Type_Code_At_Issue]
,[Deleted_Flag]
,[Early_Settlement_Bln]
,[Early_Settlement_Rebate_Value]
,[Early_Settlement_Rebate_Contra_Value]
,[Final_Instalment_Value]
,[First_Instalment_Value]
,[First_Payment_Due_Date]
,[Instalment_Periods_To_Date]
,[Is_Adjustment_Bln]
,[Issue_Date]
,[Issue_Value]
,[Issuing_Representative_Id]
,[Late_Issue_Bln]
,[Linked_Agreement_Number]
,[Loan_Reason_Code]
,[Next_Payment_Due]
,[Normal_Due_Day_In_Month]
,[Number_Of_Default_Charge_Applications_To_Date]
,[Outstanding_Balance]
,[Outstanding_Default_Charge]
,[Product_Category_Code]
,[Product_Version_Db_Id]
,[Product_Version_Id]
,[Regular_Instalment_Value]
,[Third_Party_Retailer_Event_Code]
,[Total_Amount_Payable]
,[Transferred_Bln]
,[Settlement_Balance]
,[Written_Back_Value]
,[Written_Off_Date]
,[Written_Off_Value]
,[Written_Off_Week]
,[Dt_Generation_Id]
,[Dt_Transaction_Id]
,[Dt_Write_Bln]
,[Last_Updated_Datetime]
,[Last_Updated_Id]
,[Annual_Interest_Rate]
,[Prevailing_Principal]
,[Company_Rate_Cap_Id]
,[Final_Instalment_Value_At_Issue]
,[First_Instalment_Value_At_Issue]
,[Regular_Instalment_Value_At_Issue]
,[Total_Amount_Payable_At_Issue]
,[Customer_Repayment_Account_Num]
,[Chosen_Payment_Due_Day]
,[Early_Settlement_Charge_Applied]
,[Refinancing_Agreement_Id]
,[Refinancing_Agreement_Db_Id]
,[Refinanced_Week]
,[Reporting_Week_Num]
,[Agreement_Form_Corrected_Bln]
,[Customer_Business_Id]
,[Customer_Business_Db_Id]
,[Credit_Check_Reference]
,[Codebtor_Id]
,[Finance_Absolute_Arrears]
,[Global_Transaction_Key]
,[Agreement_Source_Code]
,[Agreement_Issue_Location_Code]
,[Promotion_Reason_Code]
)
VALUES
(
 2000        -- Agreement_Db_Id -TODOS LOS CONTRATOS SE ENCUENTRAN EN ESTA VERSIÓN *
,0        -- Absolute_Arrears  -Adeudo pendiente
,'2025-08-01 00:00:00'     -- Actual_Paid_Up_Date -Fecha basada en el ultimo pago
,06     -- Actual_Paid_Up_Week -Semana en que se registro esta semana 
,625022603-- Agreement_Num * LILI
,'AC'     -- Agreement_Status_Code -- Activo = AC Pagado =PU * LILI
,NULL     -- Cancellation_Date 
,NULL     -- Cancellation_Week
,NULL        -- Cancellation_Value 
,NULL     -- Cancelled_By_Representative_Id
,'2026-02-06' -- Creation_Date*
,202606   -- Creation_Week *
,'MX'     -- Company_Code
,2007001672933 -- Customer_Id* LILI
,01      -- Customer_Type_Code_At_Issue 
,0        -- Deleted_Flag
,0        -- Early_Settlement_Bln - Si tiene 1 puede anticipar pagos 
,0        -- Early_Settlement_Rebate_Value - 0
,0        -- Early_Settlement_Rebate_Contra_Value 
,500      -- Final_Instalment_Value *REVISAR TABULADOR
,500      -- First_Instalment_Value *REVISAR TABULADOR
,'2026-02-06' -- First_Payment_Due_Date *
,22        -- Instalment_Periods_To_Date
,0        -- Is_Adjustment_Bln -0
,'2026-02-06' -- Issue_Date*
,13000     -- Issue_Value - Valor del monto del prestamo 
,1001        -- Issuing_Representative_Id 
,0        -- Late_Issue_Bln
,NULL     -- Linked_Agreement_Number
,01     -- Loan_Reason_Code
,'2026-02-13' -- Next_Payment_Due --Siguiente semana a la fecha de creacion
,15        -- Normal_Due_Day_In_Month
,0        -- Number_Of_Default_Charge_Applications_To_Date
,3694.87     -- Outstanding_Balance * LILI
,0        -- Outstanding_Default_Charge --Cargos monatorios
,01     -- Product_Category_Code
,2000        -- Product_Version_Db_Id siempre va en conjunto con el primer campo 
,118        -- Product_Version_Id - debe apuntar hacia el producto y a un termino 
,178.3      -- Regular_Instalment_Value - monto semanal 
,01     -- Third_Party_Retailer_Event_Code
,27176.070000     -- Total_Amount_Payable --Monto total a  pagar 
,0        -- Transferred_Bln
,3694.87     -- Settlement_Balance * LILI
,0        -- Written_Back_Value ---
,NULL     -- Written_Off_Date
,0        -- Written_Off_Value
,NULL     -- Written_Off_Week
,1        -- Dt_Generation_Id
,'50CE307D-6E8C-4101-8B81-81A506B37F86' -- Dt_Transaction_Id -- 
,0        -- Dt_Write_Bln
,'2026-02-06' -- Last_Updated_Datetime --Fecha de modificacion del contrato
,1001        -- Last_Updated_Id
,10.5000000000000    -- Annual_Interest_Rate
,5500.000000     -- Prevailing_Principal
,1        -- Company_Rate_Cap_Id
,500      -- Final_Instalment_Value_At_Issue
,500      -- First_Instalment_Value_At_Issue
,178.3      -- Regular_Instalment_Value_At_Issue * LILI
,6000     -- Total_Amount_Payable_At_Issue
,'ACC123456789' -- Customer_Repayment_Account_Num
,15        -- Chosen_Payment_Due_Day
,0        -- Early_Settlement_Charge_Applied
,NULL     -- Refinancing_Agreement_Id
,NULL     -- Refinancing_Agreement_Db_Id
,NULL     -- Refinanced_Week
,NULL   -- Reporting_Week_Num
,0        -- Agreement_Form_Corrected_Bln
,NULL     -- Customer_Business_Id
,NULL     -- Customer_Business_Db_Id
,'CREDITCHK001'     -- Credit_Check_Reference
,NULL     -- Codebtor_Id
,0        -- Finance_Absolute_Arrears
,'D3C955D0-8595-4F99-93BA-B10869AD2438'     -- Global_Transaction_Key
,01    -- Agreement_Source_Code
,01     -- Agreement_Issue_Location_Code
,01     -- Promotion_Reason_Code
)

INSERT INTO [CNFS_uat].[NFS_DBO].[Agreement_Table]
(
[Agreement_Db_Id]
,[Absolute_Arrears]
,[Actual_Paid_Up_Date]
,[Actual_Paid_Up_Week]
,[Agreement_Num]
,[Agreement_Status_Code]
,[Cancellation_Date]
,[Cancellation_Week]
,[Cancellation_Value]
,[Cancelled_By_Representative_Id]
,[Creation_Date]
,[Creation_Week]
,[Company_Code]
,[Customer_Id]
,[Customer_Type_Code_At_Issue]
,[Deleted_Flag]
,[Early_Settlement_Bln]
,[Early_Settlement_Rebate_Value]
,[Early_Settlement_Rebate_Contra_Value]
,[Final_Instalment_Value]
,[First_Instalment_Value]
,[First_Payment_Due_Date]
,[Instalment_Periods_To_Date]
,[Is_Adjustment_Bln]
,[Issue_Date]
,[Issue_Value]
,[Issuing_Representative_Id]
,[Late_Issue_Bln]
,[Linked_Agreement_Number]
,[Loan_Reason_Code]
,[Next_Payment_Due]
,[Normal_Due_Day_In_Month]
,[Number_Of_Default_Charge_Applications_To_Date]
,[Outstanding_Balance]
,[Outstanding_Default_Charge]
,[Product_Category_Code]
,[Product_Version_Db_Id]
,[Product_Version_Id]
,[Regular_Instalment_Value]
,[Third_Party_Retailer_Event_Code]
,[Total_Amount_Payable]
,[Transferred_Bln]
,[Settlement_Balance]
,[Written_Back_Value]
,[Written_Off_Date]
,[Written_Off_Value]
,[Written_Off_Week]
,[Dt_Generation_Id]
,[Dt_Transaction_Id]
,[Dt_Write_Bln]
,[Last_Updated_Datetime]
,[Last_Updated_Id]
,[Annual_Interest_Rate]
,[Prevailing_Principal]
,[Company_Rate_Cap_Id]
,[Final_Instalment_Value_At_Issue]
,[First_Instalment_Value_At_Issue]
,[Regular_Instalment_Value_At_Issue]
,[Total_Amount_Payable_At_Issue]
,[Customer_Repayment_Account_Num]
,[Chosen_Payment_Due_Day]
,[Early_Settlement_Charge_Applied]
,[Refinancing_Agreement_Id]
,[Refinancing_Agreement_Db_Id]
,[Refinanced_Week]
,[Reporting_Week_Num]
,[Agreement_Form_Corrected_Bln]
,[Customer_Business_Id]
,[Customer_Business_Db_Id]
,[Credit_Check_Reference]
,[Codebtor_Id]
,[Finance_Absolute_Arrears]
,[Global_Transaction_Key]
,[Agreement_Source_Code]
,[Agreement_Issue_Location_Code]
,[Promotion_Reason_Code]
)
VALUES
(
 2000        -- Agreement_Db_Id -TODOS LOS CONTRATOS SE ENCUENTRAN EN ESTA VERSIÓN *
,0        -- Absolute_Arrears  -Adeudo pendiente
,'2025-08-01 00:00:00'     -- Actual_Paid_Up_Date -Fecha basada en el ultimo pago
,06     -- Actual_Paid_Up_Week -Semana en que se registro esta semana 
,625125360-- Agreement_Num * LILI
,'AC'     -- Agreement_Status_Code -- Activo = AC Pagado =PU * LILI
,NULL     -- Cancellation_Date 
,NULL     -- Cancellation_Week
,NULL        -- Cancellation_Value 
,NULL     -- Cancelled_By_Representative_Id
,'2026-02-06' -- Creation_Date*
,202606   -- Creation_Week *
,'MX'     -- Company_Code
,2008001539493 -- Customer_Id* LILI
,01      -- Customer_Type_Code_At_Issue 
,0        -- Deleted_Flag
,0        -- Early_Settlement_Bln - Si tiene 1 puede anticipar pagos 
,0        -- Early_Settlement_Rebate_Value - 0
,0        -- Early_Settlement_Rebate_Contra_Value 
,500      -- Final_Instalment_Value *REVISAR TABULADOR
,500      -- First_Instalment_Value *REVISAR TABULADOR
,'2026-02-06' -- First_Payment_Due_Date *
,22        -- Instalment_Periods_To_Date
,0        -- Is_Adjustment_Bln -0
,'2026-02-06' -- Issue_Date*
,13000     -- Issue_Value - Valor del monto del prestamo 
,1001        -- Issuing_Representative_Id 
,0        -- Late_Issue_Bln
,NULL     -- Linked_Agreement_Number
,01     -- Loan_Reason_Code
,'2026-02-13' -- Next_Payment_Due --Siguiente semana a la fecha de creacion
,15        -- Normal_Due_Day_In_Month
,0        -- Number_Of_Default_Charge_Applications_To_Date
,21512.17     -- Outstanding_Balance * LILI
,0        -- Outstanding_Default_Charge --Cargos monatorios
,01     -- Product_Category_Code
,2000        -- Product_Version_Db_Id siempre va en conjunto con el primer campo 
,118        -- Product_Version_Id - debe apuntar hacia el producto y a un termino 
,346.98      -- Regular_Instalment_Value - monto semanal 
,01     -- Third_Party_Retailer_Event_Code
,27176.070000     -- Total_Amount_Payable --Monto total a  pagar 
,0        -- Transferred_Bln
,21512.17     -- Settlement_Balance * LILI
,0        -- Written_Back_Value ---
,NULL     -- Written_Off_Date
,0        -- Written_Off_Value
,NULL     -- Written_Off_Week
,1        -- Dt_Generation_Id
,'50CE307D-6E8C-4101-8B81-81A506B37F86' -- Dt_Transaction_Id -- 
,0        -- Dt_Write_Bln
,'2026-02-06' -- Last_Updated_Datetime --Fecha de modificacion del contrato
,1001        -- Last_Updated_Id
,10.5000000000000    -- Annual_Interest_Rate
,5500.000000     -- Prevailing_Principal
,1        -- Company_Rate_Cap_Id
,500      -- Final_Instalment_Value_At_Issue
,500      -- First_Instalment_Value_At_Issue
,346.98      -- Regular_Instalment_Value_At_Issue * LILI
,6000     -- Total_Amount_Payable_At_Issue
,'ACC123456789' -- Customer_Repayment_Account_Num
,15        -- Chosen_Payment_Due_Day
,0        -- Early_Settlement_Charge_Applied
,NULL     -- Refinancing_Agreement_Id
,NULL     -- Refinancing_Agreement_Db_Id
,NULL     -- Refinanced_Week
,NULL   -- Reporting_Week_Num
,0        -- Agreement_Form_Corrected_Bln
,NULL     -- Customer_Business_Id
,NULL     -- Customer_Business_Db_Id
,'CREDITCHK001'     -- Credit_Check_Reference
,NULL     -- Codebtor_Id
,0        -- Finance_Absolute_Arrears
,'D3C955D0-8595-4F99-93BA-B10869AD2438'     -- Global_Transaction_Key
,01    -- Agreement_Source_Code
,01     -- Agreement_Issue_Location_Code
,01     -- Promotion_Reason_Code
)
