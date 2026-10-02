INSERT INTO CNFS_uat.NFS_DBO.Agreement_Transaction_Table (
        Agreement_Transaction_Id,
        Agreement_Transaction_Db_Id,
        Agreement_Security_Check_Balance_Db_Id,
        Agreement_Security_Check_Balance_Id,
        Accounting_Week_Num,
        Agency_Id,
        Agreement_Db_Id,
        Agreement_Transaction_Type_Code,
        Balanced_Bln,
        Agreement_Id,
        Committed_Bln,
        Company_Code,
        Creation_Date,
        Deleted_Flag,
        Money_Balancing_Bln,
        Non_Payment_Code,
        Original_Representative_Id,
        Product_Version_Db_Id,
        Product_Version_Id,
        Reference_Text,
        Representative_Id,
        Value,
        Write_Off_Reason_Code,
        Dt_Generation_Id,
        Dt_Transaction_Id,
        Dt_Write_Bln,
        Last_Updated_Datetime,
        Last_Updated_Id,
        Last_Updated_Timestamp,
        Effective_Accounting_Week_Num,
        Transaction_Date,
        Unsigned_Bln,
        Undated_Bln,
        Amount_That_Cleared_Default_Charges,
        Committed_Date,
        Balance_Id,
        Balance_Db_Id,
        Default_Charge_Rule_Code,
        Committed_By_Representative_Id,
        Allow_Updates_Bln,
        Global_Transaction_Key,
        External_User_Id
    )
VALUES(
        2000385,
        --insertamos este dato de las transacciones disponibles
        102,
        -- este dato siempre será 102
        NULL,
        -- este dato siempre será NULL
        NULL,
        -- este dato siempre será NULL
        202614,
        -- este dato siempre será el año y semana actual
        2075000000335,
        -- este dato siempre será el agency id del cliente
        2000,
        -- este dato siempre será 2000
        N'HC',
        -- este dato puede ser HC u OP
        1,
        -- este dato siempre será 1
        103,
        -- este dato siempre será 103
        1,
        -- este dato siempre será 1
        N'MEX',
        -- este dato siempre será MEX
        '2026-04-06 10:00:00.000',
        -- esta fecha es la fecha de hoy ya que se generará el comprobante mañana
        0,
        -- este dato siempre será 0
        0,
        -- este dato siempre será 0
        NULL,
        -- este dato siempre será NULL
        NULL,
        -- este dato siempre será NULL
        2000,
        -- este dato siempre será 2000
        112,
        -- este dato es el que define el plazo del contrato, 106 = 42 sem, 131 = 65 sem y 112 =12 sem.
        N'Pago acuerdo 5-3',
        -- este dato siempre será el nombre del acuerdo
        2075000343335,
        -- este dato siempre será el agency id del cliente
        378.750000,
        -- de la tabla de cargo este es el valor del pago de la columna "Cuota Semana 2 a 12"
        NULL,
        -- este dato siempre será NULL
        1,
        -- este dato siempre será 1
        N'DB321C3D-6C24-4A50-9F7C-AF7E003C52C2',
        -- este dato siempre será único
        0,
        -- este dato siempre será 0
        '2024-03-24 10:00:00.000',
        --no tiene relevancia
        5001,
        -- este dato siempre será 5001
        0x00000000004CA486,
        -- este dato siempre será el mismo
        50,
        -- este dato siempre será 50
        '2026-04-06 10:00:00.000',
        -- esta fecha es la fecha de hoy ya que se generará el comprobante mañana
        0,
        -- este dato siempre será 0
        0,
        -- este dato siempre será 0
        0.000000,
        -- este dato siempre será 0.000000
        NULL,
        -- este dato siempre será NULL
        NULL,
        -- este dato siempre será NULL
        NULL,
        -- este dato siempre será NULL
        NULL,
        -- este dato siempre será NULL
        1,
        -- este dato siempre será 1
        1,
        -- este dato siempre será 1
        N'61F1D174-C3C6-42CA-BF67-2B3F6D246C6F',
        -- este dato siempre será único
        NULL -- este dato siempre será NULL
    );