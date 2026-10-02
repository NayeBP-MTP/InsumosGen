--El paso primero es generar una venta desde aplicativo Providigital, para un CF se generará la oferta y para un CN se inicia el flujo desde la apliación sin previa oferta insertada.
-- Paso 1: Cambiar los datos de Número de Ciente y Nombre del Cliente
INSERT INTO Originacion.dbo.ExpedienteCliente (
                IdExpedienteCliente,
                IdKiban,
                IdOriginacion,
                IdOferta,
                IdPaso,
                IdExpedienteConsentimiento,
                IdExpedienteOferta,
                Agencia,
                Cliente,
                NombreCliente,
                RFCCliente,
                DomicilioCliente,
                TelefonoCasaCliente,
                TelefonoCelularCliente,
                SemanaVigenciaMsgPesos,
                AprobadoVenta,
                AprobadoRegistro,
                FechaAprobacion,
                FechaActualizacion,
                MotivoRechazo,
                FechaRechazo,
                FechaCreacion,
                OfertaAutorizada,
                MontoDispersar,
                NombrePersonalAprobo,
                referencia,
                folioContrato,
                numeroContrato,
                idAgente,
                EstadoSucursal,
                CiudadSucursal,
                IdTipoPago,
                Folio,
                DomicilioAct,
                FechaNacimientoAct,
                Cheque,
                FechaModificacionCheque,
                IdTipoCliente,
                IdTipoProducto,
                idOrigenOfertaEspecial,
                fechaCancelacionOrden,
                fechaCreacionOrden,
                idEstatusOfertaEspecial,
                IdEstatusCheque,
                FechaNacimiento,
                FechaFinalizacion,
                DireccionCobranzaCliente,
                DireccionCobranzaClienteActual,
                FechaCancelacion,
                FechaDispersion,
                NombrePersonalCancelo,
                FechaCobroOrdenPago,
                FicoScore,
                Reintentos,
                IdMotivoRechazo,
                Comentario,
                ID_Proveedor,
                FechaRegistroContrato,
                QuienRegistroContrato,
                IdMotivoRechazoSeguro,
                NoAutorizadoCliente,
                IdAgenteCambaceo,
                CategoriaEstrella,
                EventoId,
                CanceladoVencimiento,
                LeadId,
                AltId,
                FechaCreacionOferta,
                FechaCreacionOrdenVenta,
                ChequeCustomerService,
                ChequeCustomerServiceAsignadoPorId,
                ChequeCustomerServiceAsignadoPorNombre,
                ChequeCustomerServiceFechaAsignacion,
                SemanaVigenciaMsgPesosApprove,
                RazonesFicoScore,
                PuntajeConversion,
                FechaPrimeraFinalizacion,
                CancelaOrdenPago,
                CancelaContrato,
                FechaCancelacionOrdenPago,
                PasoPrevCC
        )
VALUES (
                3405,
                2001351,
                NULL,
                0,
                18,
                1174,
                NULL,
                2075000000335,
                0,
                --Este es el Id del cliente, lo debemos generar de manera manual. 2075 (agencia) + 0 + 4 (identificador mio) +2615 (semana) + 001 (consecutivo)
                N 'NAYELI BENITEZ PEREZ',
                --Se cambia el nombre del Cliente
                N 'BEPN9110181C3',
                N 'CJON ABASOLO 10 LOC SAN GREGORIO AZTOTOACAN 74130 SAN SALVADOR EL VERDE, PUE.',
                --Debemos llevar esta dirección tal cual a la siguiente tabla.
                NULL,
                NULL,
                0,
                1,
                0,
                '2026-04-09 11:17:36.763',
                '2026-04-09 11:17:36.763',
                NULL,
                NULL,
                '2026-04-09 11:03:57.273',
                NULL,
                9000.0,
                N'Maria Lopez',
                N'PR2240019976',
                N'PR24001997',
                N'240019976',
                2075000343335,
                NULL,
                NULL,
                1,
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                2,
                1,
                0,
                NULL,
                NULL,
                NULL,
                NULL,
                '1991-10-18 00:00:00.000',
                '2026-04-09 11:11:51.337',
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                0,
                0,
                NULL,
                NULL,
                1,
                NULL,
                NULL,
                21,
                0,
                0,
                N'MEGA',
                NULL,
                0,
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                202613,
                N'',
                NULL,
                '2026-04-09 11:11:51.337',
                NULL,
                NULL,
                NULL,
                NULL
        );
-- Paso 2: Cambiar los datos de la tabla ExpedienteClienteDireccion
-- Tomamos de la tabla de ExpedienteCliente el IdExpedienteCliente, la dirección y la fecha de nacimiento, abrimos la tabla de CustomerTable. Así como cambiar los datos de los comentarios que tienen ** en sus comentarios.
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
                -- [Customer_Id] ** ESTE DATO DEBE COINCIDIR CON EL DE EC
                1,
                -- [Address_Changes_Count]
                2075000000335,
                -- [Agency_Id] ** DEBE COINCIDIR CON LA VENTA
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
                -- [Birth_Date] ** COLOCAR FECHA DE NAC DE EC
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
                -- [Creation_Date]  ** FECHA DEL DIA
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
                -- [Display_Name] ** CAMBIAR EL NOMBRE AL DE LA TABLA EC
                3000,
                -- [Disposable_Income]
                '2022-01-03',
                -- [Disposable_Income_Date] ** FECHA DEL DIA
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
                -- [First_Agreement_Creation_Date] **FECHA DEL DIA
                202201,
                -- [First_Agreement_Creation_Week] **SEMANA ACTUAL
                '2022-01-03',
                -- [First_Agreement_Issue_Date] **FECHA DEL DIA
                1000000092,
                -- [Focus_Created_Id]
                'Adán',
                -- [Forename] **SOLO NOMBRE DEL CLIENTE
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
                -- [Nearest_Relative_Address] **DIRECCION DEL CLIENTE DE LA TABLA EC
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
---Paso 3 Crear el contrato
USE [CNFS_uat]
GO
INSERT INTO [NFS_DBO].[Agreement_Table] (
                [Agreement_Db_Id],
                [Absolute_Arrears],
                [Actual_Paid_Up_Date],
                [Actual_Paid_Up_Week],
                [Agreement_Num],
                [Agreement_Status_Code],
                [Cancellation_Date],
                [Cancellation_Week],
                [Cancellation_Value],
                [Cancelled_By_Representative_Id],
                [Creation_Date],
                [Creation_Week],
                [Company_Code],
                [Customer_Id],
                [Customer_Type_Code_At_Issue],
                [Deleted_Flag],
                [Early_Settlement_Bln],
                [Early_Settlement_Rebate_Value],
                [Early_Settlement_Rebate_Contra_Value],
                [Final_Instalment_Value],
                [First_Instalment_Value],
                [First_Payment_Due_Date],
                [Instalment_Periods_To_Date],
                [Is_Adjustment_Bln],
                [Issue_Date],
                [Issue_Value],
                [Issuing_Representative_Id],
                [Late_Issue_Bln],
                [Linked_Agreement_Number],
                [Loan_Reason_Code],
                [Next_Payment_Due],
                [Normal_Due_Day_In_Month],
                [Number_Of_Default_Charge_Applications_To_Date],
                [Outstanding_Balance],
                [Outstanding_Default_Charge],
                [Product_Category_Code],
                [Product_Version_Db_Id],
                [Product_Version_Id],
                [Regular_Instalment_Value],
                [Third_Party_Retailer_Event_Code],
                [Total_Amount_Payable],
                [Transferred_Bln],
                [Settlement_Balance],
                [Written_Back_Value],
                [Written_Off_Date],
                [Written_Off_Value],
                [Written_Off_Week],
                [Dt_Generation_Id],
                [Dt_Transaction_Id],
                [Dt_Write_Bln],
                [Last_Updated_Datetime],
                [Last_Updated_Id],
                [Annual_Interest_Rate],
                [Prevailing_Principal],
                [Company_Rate_Cap_Id],
                [Final_Instalment_Value_At_Issue],
                [First_Instalment_Value_At_Issue],
                [Regular_Instalment_Value_At_Issue],
                [Total_Amount_Payable_At_Issue],
                [Customer_Repayment_Account_Num],
                [Chosen_Payment_Due_Day],
                [Early_Settlement_Charge_Applied],
                [Refinancing_Agreement_Id],
                [Refinancing_Agreement_Db_Id],
                [Refinanced_Week],
                [Reporting_Week_Num],
                [Agreement_Form_Corrected_Bln],
                [Customer_Business_Id],
                [Customer_Business_Db_Id],
                [Credit_Check_Reference],
                [Codebtor_Id],
                [Finance_Absolute_Arrears],
                [Global_Transaction_Key],
                [Agreement_Source_Code],
                [Agreement_Issue_Location_Code],
                [Promotion_Reason_Code]
        )
VALUES (
                2000,
                0.000000 --CERO PORQUE EL CONTRATO ES NUEVO
,
                '2026-03-07 00:00:00' --**FECHA DE HOY
,
                202609 --**SEMANA DE HOY
,
                240018047 --ID DEL CONTRATO, SE TOMA DE EXPEDIENTECLIENTE
,
                'AC',
                NULL,
                NULL,
                NULL,
                NULL,
                '2026-03-03 00:00:00' --**FECHA DEL DIA
,
                202609 --**SEMANA ACTUAL
,
                'MEX',
                2075326020065 --**CustomerId, SE TOMA DE TABLA EC
,
                01 --**DEBE SER 01
,
                0,
                1 --**DEBE SER 1
,
                0.000000,
                0.000000,
                0.000000 --**DE ACUERDO A LA TABLA DE CARGO, ESTE ES EL PRIMER PAGO DE LA SEM1
,
                0.000000 --**DE ACUERDO A LA TABLA DE CARGO, ESTE ES EL PRIMER PAGO DE LA SEM1
,
                '2026-03-03 00:00:00' --**FECHA UNA SEMANA DESPUES DE LA DISPERSION
,
                0 --**DEBE SER 0    
,
                0,
                '2026-03-03 00:00:00' --**FECHA UNA SEMANA DESPUES DE LA DISPERSION
,
                0.000000 --**MONTO QUE SE LE PRESTÓ AL CLIENTE
,
                1001,
                0,
                NULL,
                01,
                '2026-03-03 00:00:00' --**FECHA UNA SEMANA DESPUES DE LA DISPERSION
,
                15,
                0,
                0.000000,
                0.000000,
                01,
                2000,
                118,
                0.000000 --**DE ACUERDO A LA TABLA DE CARGO, ESTE ES EL PAGO A PARTIR DE LA SEM2
,
                01,
                0.00000 --**MONTO QUE SE LE PRESTÓ AL CLIENTE
,
                0,
                0.000000 --**MONTO QUE SE LE PRESTÓ AL CLIENTE
,
                0.000000,
                NULL,
                0.000000,
                NULL,
                1,
                '50CE307D-6E8C-4101-8B81-81A506B37F86',
                0,
                '2026-03-03 00:00:00' --**FECHA DEL DIA
,
                1001,
                10.5000000000000,
                0.000000,
                1,
                0.000000,
                0.000000 --**MONTO DEL PRIMER PAGO DE ACUERDO A LAS TABLAS DE CARGO
,
                0.000000 --**DE ACUERDO A LA TABLA DE CARGO, ESTE ES EL PAGO A PARTIR DE LA SEM2
,
                0.000000 --**MONTO QUE SE LE PRESTÓ AL CLIENTE
,
                'ACC123456789',
                15,
                0.000000,
                NUll,
                NUll,
                NUll,
                NUll,
                0,
                NULL,
                NULL,
                'CREDITCHK001',
                NULL,
                0.000000,
                'D3C955D0-8595-4F99-93BA-B10869AD2438',
                01,
                01,
                01
        )
GO --PASO 4: Actualizar en CustomerAddressTable
INSERT INTO [CNFS_uat].[NFS_DBO].[Customer_Address_Table] (
                Customer_Address_Db_Id,
                Address_Cleaned_Bln,
                Building_Name,
                Customer_Address_Type_Code,
                Customer_Id,
                Deleted_Flag,
                District,
                District_Soundex,
                End_Date,
                Floor_Flat,
                Full_Address,
                House_Num,
                Is_Customer_Bln,
                Postcode,
                Region_County,
                Start_Date,
                Street_Name,
                Street_Name_Soundex,
                Short_Address,
                Town_City,
                Dt_Generation_Id,
                Dt_Transaction_Id,
                Dt_Write_Bln,
                Last_Updated_Datetime,
                Last_Updated_Id,
                Customer_Business_Id,
                Customer_Business_Db_Id
        )
VALUES (
                1,
                -- Customer_Address_Db_Id
                1,
                -- Address_Cleaned_Bln
                'Edificio Prueba',
                -- Building_Name
                'CU',
                -- Customer_Address_Type_Code
                2075002508024,
                -- Customer_Id **SOLO SE MODIFICA ESTE VALOR DE ACUERDO A TABLA EC
                0,
                -- Deleted_Flag
                'Colonia Norte',
                -- District
                'C453',
                -- District_Soundex
                '2025-08-06 00:00:00',
                -- End_Date
                '3B',
                -- Floor_Flat
                'Calle Aun más Falsota que la anterior otra vez 123, Ciudad',
                -- Full_Address
                '123',
                -- House_Num
                1,
                -- Is_Customer_Bln
                '12345',
                -- Postcode
                'Ciudad Prueba',
                -- Region_County
                '2025-01-01 00:00:00',
                -- Start_Date
                'Calle Falsa',
                -- Street_Name
                'C412',
                -- Street_Name_Soundex
                'Calle Falsa 123',
                -- Short_Address
                'Ciudad Prueba',
                -- Town_City
                1001,
                -- Dt_Generation_Id
                'CD08D0F8-8BD3-48EA-8087-EF53AC1C6F6D',
                -- Dt_Transaction_Id (GUID)
                1,
                -- Dt_Write_Bln
                '2025-08-06 18:56:00',
                -- Last_Updated_Datetime
                87654321,
                -- Last_Updated_Id
                2001,
                -- Customer_Business_Id
                2 -- Customer_Business_Db_Id
        );
--PASO 5: EN ESTE PASO SE DEBERÁ HACER EL REGISTRO DEL CLIENTE EN LA APLICACIÓN DE CA.