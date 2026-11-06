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
    1,                                       -- Customer_Address_Db_Id
    1,                                       -- Address_Cleaned_Bln
    'Edificio Prueba',                       -- Building_Name
    'CU',                                    -- Customer_Address_Type_Code
    2075002508024,                           -- Customer_Id
    0,                                       -- Deleted_Flag
    'Colonia Norte',                        -- District
    'C453',                                  -- District_Soundex
    '2025-08-06 00:00:00',                   -- End_Date
    '3B',                                    -- Floor_Flat
    'Calle Aun más Falsota que la anterior otra vez 123, Ciudad',              -- Full_Address
    '123',                                   -- House_Num
    1,                                       -- Is_Customer_Bln
    '12345',                                 -- Postcode
    'Ciudad Prueba',                         -- Region_County
    '2025-01-01 00:00:00',                   -- Start_Date
    'Calle Falsa',                           -- Street_Name
    'C412',                                  -- Street_Name_Soundex
    'Calle Falsa 123',                       -- Short_Address
    'Ciudad Prueba',                         -- Town_City
    1001,                                    -- Dt_Generation_Id
    'CD08D0F8-8BD3-48EA-8087-EF53AC1C6F6D',  -- Dt_Transaction_Id (GUID)
    1,                                       -- Dt_Write_Bln
    '2025-08-06 18:56:00',                   -- Last_Updated_Datetime
    87654321,                                -- Last_Updated_Id
    2001,                                    -- Customer_Business_Id
    2                                        -- Customer_Business_Db_Id
);