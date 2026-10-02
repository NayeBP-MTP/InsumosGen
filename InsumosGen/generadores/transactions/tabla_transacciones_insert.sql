INSERT INTO CNFS_uat.NFS_DBO.Agreement_Transaction_Receipt_Table (
        Agreement_Transaction_Receipt_Id,
        Agreement_Transaction_Receipt_Db_Id,
        Agreement_Transaction_Id,
        Agreement_Transaction_Db_Id,
        Receipt_Reference,
        Extracted,
        Transaction_Date,
        Deleted_Flag,
        Dt_Generation_Id,
        Dt_Transaction_Id,
        Dt_Write_Bln,
        Last_Updated_Datetime,
        Last_Updated_Id,
        Last_Updated_Timestamp,
        Stock_Item_Id,
        Stock_Item_Db_Id,
        Creation_Date,
        Previously_Committed_Transaction_Bln,
        Receipt_Type_Code,
        Representative_Id,
        Undated_Bln,
        Unsigned_Bln,
        Validated_Bln,
        Validation_Date,
        ReceiptHash
    )
VALUES(
        410768,
        --llave primaria
        102,
        --llave primaria de la base de datos
        390980,
        --id de la transaccion
        102,
        --db id de la transaccion
        N'RC-390980',
        --referencia del recibo (hace match con id de la transaccion)
        0,
        --se mantiene este dato
        '2026-04-06 10:00:00.000',
        --fecha de hoy
        0,
        --se mantiene este dato
        0,
        --se mantiene este dato
        N'16B2D146-90AC-4700-BA13-8116BF033174',
        --hash
        0,
        --se mantiene este dato
        '2025-10-15 19:52:00.000',
        --fecha de validacion
        5002,
        --id del usuario que validó
        0x00000000004CA41E,
        --timestamp
        NULL,
        --se mantiene este dato
        NULL,
        --se mantiene este dato
        '2026-04-06 10:00:00.000',
        --fecha de creacion
        0,
        --se mantiene este dato
        N'RCT',
        --tipo de recibo
        2075000343335,
        --id del representante
        0,
        --se mantiene este dato
        0,
        --se mantiene este dato
        0,
        --se mantiene este dato
        NULL,
        --se mantiene este dato   
        N' --se mantiene este dato
                               '
    );