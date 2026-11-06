
 
INSERT INTO [NFS_DBO].[Agreement_Table]
           ([Agreement_Db_Id]
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
           ,[Promotion_Reason_Code])
     VALUES
           (2000
           ,0.000000 --** DEUDA DEL CLIENTE, EN 0 SI ES NUEVO
           ,'2026-06-04 00:00:00' -- ** FECHA DEL DIA
           ,202623 --** SEMANA ACTUAL
           ,240020468 --**CONTRATO DE LA VENTA DEL CLIENTE
           ,'AC' --** CONTRATO ESTA ACTIVO
           ,NULL
           ,NULL
           ,NULL
           ,NULL
           ,'2026-06-05 00:00:00' --**FECHA DEL DIA
           ,202623
           ,'MEX'
           ,0 --** CUSTOMER ID DE LA VENTA 
           ,01
           ,0
           ,1
           ,0.000000
           ,0.000000
           ,530.39 --**MONTO DEL PRIMER PAGO
           ,530.39 --**MONTO DEL PRIMER PAGO
           ,'2026-06-12 00:00:00' --**FECHA DE 8 DIAS DESPUES DE HACER LA VENTA
           ,0
           ,0
           ,'2026-06-12 00:00:00'--**FECHA DE 8 DIAS DESPUES DE HACER LA VENTA
           ,10000.000
           ,1001
           ,0
           ,NULL
           ,01
           ,'2026-06-12 00:00:00'--**FECHA DE 8 DIAS DESPUES DE HACER LA VENTA
           ,15
           ,0
           ,0.000000
           ,0.000000
           ,01
           ,2000
           ,118
           ,303.05 --**PAGO A PARTIR DE LA SEGUNDA SEMANA
           ,01
           ,9924.94 --**MONTO PRESTADO DE LA VENTA
           ,0
           ,9924.94 --**MONTO PRESTADO DE LA VENTA
           ,0.000000
           ,NULL
           ,0.000000
           ,NULL
           ,1
           ,'50CE307D-6E8C-4101-8B81-81A506B37F86'
           ,0
           ,'2026-06-04 00:00:00' -- ** FECHA DEL DIA
           ,1001
           ,10.5000000000000
           ,0.000000
           ,1
           ,0.000000
           ,530.39 --**MONTO DEL PRIMER PAGO
           ,303.05 --**PAGO A PARTIR DE LA SEGUNDA SEMANA
           ,9924.94 --**MONTO PRESTADO DE LA VENTA
           ,'ACC123456789'
           ,15
           ,0.000000
           ,NUll
           ,NUll
           ,NUll
           ,NUll
           ,0
           ,NULL
           ,NULL
           ,'CREDITCHK001'
           ,NULL
           ,0.000000
           ,'D3C955D0-8595-4F99-93BA-B10869AD2438'
           ,01
           ,01
           ,01)

 