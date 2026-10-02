-- =============================================
-- SCRIPT PARA CREAR NUEVA AGENCIA - IZCALLI
-- =============================================
-- Este script ejecuta todas las inserciones necesarias en un solo query
-- para crear una nueva agencia en Challenger_uat y BotDB
-- 
-- IMPORTANTE: Ajustar los siguientes valores antes de ejecutar:
-- - Agency_Id: ID único de la agencia (formato: 2075000001XXX)
-- - Representative_Id: ID único del representante (formato: 2075000012XXX)
-- - DM_Id: ID del District Manager (formato: 2075000012XXX)
-- - AM_Id: ID del Area Manager (formato: 2075000012XXX)
-- - Nombres, correos y teléfonos de los representantes
-- =============================================

BEGIN TRANSACTION;

BEGIN TRY
    -- Variables de ejemplo para la nueva agencia Izcalli
    DECLARE @Agency_Id BIGINT = 2075000001235;
    DECLARE @Representative_Id BIGINT = 2075000012346;
    DECLARE @DM_Id BIGINT = 2075000012790;
    DECLARE @AM_Id BIGINT = 2075000012988;
    DECLARE @Representative_Name NVARCHAR(100) = 'Nombre Representante';
    DECLARE @Representative_Email NVARCHAR(100) = 'representante@provident.com.mx';
    DECLARE @Representative_Phone BIGINT = 5512345678;
    DECLARE @Representative_RFC NVARCHAR(20) = 'XXXX000000XXX';
    DECLARE @DM_Name NVARCHAR(100) = 'Nombre DM';
    DECLARE @DM_Letter NVARCHAR(1) = 'C';
    DECLARE @Branch_Name NVARCHAR(100) = 'AM530 Izcalli';
    DECLARE @AM_Name NVARCHAR(100) = 'Nombre AM';
    DECLARE @Branch_Location NVARCHAR(100) = 'Cuautitlán Izcalli';
    DECLARE @Prefix INT = 2075;

    -- =============================================
    -- PASO 1: Insertar en AgencyStructure (Challenger_uat)
    -- =============================================
    INSERT INTO [Challenger_uat].[dbo].[AgencyStructure] 
    VALUES(
        @Agency_Id,
        @Representative_Id,
        @Representative_Name,
        'IzcalliDM62C',
        @DM_Id,
        @DM_Name,
        @DM_Letter,
        @Branch_Name,
        @AM_Id,
        @AM_Name
    );

    PRINT 'PASO 1 COMPLETADO: AgencyStructure insertada correctamente';

    -- =============================================
    -- PASO 2: Insertar representante en tblRepresentative_Table_AWS (Challenger_uat)
    -- =============================================
    INSERT INTO [Challenger_uat].[dbo].[tblRepresentative_Table_AWS] 
    VALUES(
        @Representative_Id,
        @Representative_Email,
        @Representative_Name,
        @Representative_Phone,
        2,
        1,
        @Representative_RFC
    );

    PRINT 'PASO 2 COMPLETADO: Representante insertado en Challenger_uat';

    -- =============================================
    -- PASO 3: Crear categoría en P_ESTRELLAS_MENSUAL_CATEGORIAS (Challenger_uat)
    -- =============================================
    INSERT INTO [Challenger_uat].[dbo].[P_ESTRELLAS_MENSUAL_CATEGORIAS]
    (
        [Representative_name],
        [Branch],
        [Agency_Id],
        [Representative_Id],
        [DM_Letter],
        [Month_Calc],
        [Category],
        [Payment_Month],
        [Avg_Collected_Cust],
        [Sales_Volume],
        [NetIncrease],
        [Avg_payment_coll],
        [GdsCategory]
    )
    VALUES(
        @Representative_Name,
        @Branch_Location,
        @Agency_Id,
        @Representative_Id,
        @DM_Letter,
        'Marzo',
        'ULTRA',
        'Abril',
        0.905,
        23,
        2,
        0.09,
        'ULTRA'
    );

    PRINT 'PASO 3 COMPLETADO: Categoría P_ESTRELLAS_MENSUAL insertada correctamente';

    -- =============================================
    -- PASO 4: Insertar agencia en Agency_Representative_AWS (BotDB)
    -- =============================================
    INSERT INTO [botDB].[dbo].[Agency_Representative_AWS] 
    VALUES (
        @Agency_Id,
        @Representative_Id,
        @Prefix
    );

    PRINT 'PASO 4 COMPLETADO: Agencia insertada en BotDB';

    -- =============================================
    -- PASO 5: Insertar representante en tblRepresentative_Table_AWS (BotDB)
    -- =============================================
    INSERT INTO [botDB].[dbo].[tblRepresentative_Table_AWS] 
    VALUES(
        @Representative_Id,
        @Representative_Email,
        @Representative_Name,
        @Representative_Phone,
        2,
        1,
        @Representative_RFC
    );

    PRINT 'PASO 5 COMPLETADO: Representante insertado en BotDB';

    -- =============================================
    -- COMMIT SI TODO SALIÓ BIEN
    -- =============================================
    COMMIT TRANSACTION;
    PRINT '==============================================';
    PRINT 'ÉXITO: Nueva agencia Izcalli creada correctamente';
    PRINT 'Agency_Id: ' + CAST(@Agency_Id AS NVARCHAR(20));
    PRINT 'Representative_Id: ' + CAST(@Representative_Id AS NVARCHAR(20));
    PRINT '==============================================';

END TRY
BEGIN CATCH
    -- =============================================
    -- ROLLBACK EN CASO DE ERROR
    -- =============================================
    ROLLBACK TRANSACTION;
    
    PRINT '==============================================';
    PRINT 'ERROR: La transacción ha sido revertida';
    PRINT 'Mensaje de error: ' + ERROR_MESSAGE();
    PRINT 'Línea de error: ' + CAST(ERROR_LINE() AS NVARCHAR(10));
    PRINT '==============================================';
    
END CATCH;
