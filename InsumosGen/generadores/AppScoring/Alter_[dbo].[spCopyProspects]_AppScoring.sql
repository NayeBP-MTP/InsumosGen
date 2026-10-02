USE [Application_Score]
GO
/****** Object:  StoredProcedure [dbo].[spCopyProspects]    Script Date: 06/02/2026 05:34:16 p. m. ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

-- =============================================
-- Author:  Miguel Angel Ochoa
-- Create date: 14/Sep/2016
-- Description: Copia información de los clientes del ambiente de Application_Score a GeoCoverage_YFOS
--              donde los clientes tienen estatus Aceptado, Verificado por sucursal y que no han sido insertados previamente
-- Update: Add colony in the process
-- Update : Add values for AVT's ([Branch_No],[Ext_Number], [Int_Number],[Term1], [Offer1], [Term2],[Offer2],[Term3],[Offer3])
-- Update : Se agrega logica Unbundling (Solo se inserta 'N1', 'N2' o NULL segun el texto)
-- =============================================
ALTER PROCEDURE [dbo].[spCopyProspects]  
AS
BEGIN
-- SET NOCOUNT ON added to prevent extra result sets from
-- interfering with SELECT statements.
SET NOCOUNT ON;

    --Selecionamos unicamente los prospectos que fueron modificados y creados el dia de hoy
SELECT TC.Id_Prospect, TC.Id_Product, TC.Section, TC.Id_Branch, TC.Modification_Date,
TC.Id_Term, TC.Id_Status_Cis, TC.App_Score_Status, TC.AGENCY_ID, TC.DecMessageText -- Se agrega Agencia y DecMessageText
INTO #TCIS FROM APPLICATION_SCORE.DBO.TCIS tc  WITH(NOLOCK)
WHERE tc.Modification_Date > GETDATE()-1

--obtnemos las ofertas de los prospectos encontrados en la consulta anterior
  SELECT TOV.id_Prospect, TOV.[12_SEMANAS], TOV.[32_SEMANAS], TOV.[42_SEMANAS] ,TOV.[52_SEMANAS] INTO #TOfertas_Value FROM #tcis tc
LEFT JOIN TOfertas_Value AS TOV  WITH (NOLOCK) ON tov.id_prospect=tc.id_prospect
   and tov.Evaluation_date=( SELECT  TOP(1) Evaluation_date 
    FROM  TOfertas_Value WITH (NOLOCK)
    WHERE id_Prospect=tc.id_prospect and Evaluation_date = (select max(Evaluation_date) from TOfertas_Value where id_Prospect=tc.id_prospect ) )


TRUNCATE TABLE TEMPValidatedProspects 

-- INSERTA LOS PROSPECTOS EN LA BASE DE DATOS
--Se inserta en la tabla temporal antes de insertar o actualizar
INSERT INTO TEMPValidatedProspects 
   ( Id_Prospect ,
     Name ,
     [Address] ,
     zip ,
     City ,
     [State] ,
     TelephoneNumber ,
     MobileNumber ,
     Name_Branch ,
     Section ,     
     Term ,
     Product_Value ,
     Desc_Status_Cis,
     MaxOffer,
     [Colony], 
     [Date], 
     [Hour],
     [Branch_No], 
     [Ext_Number],
     [Int_Number],
     [Term1], 
     [Offer1], 
     [Term2],
     [Offer2],
     [Term3],
     [Offer3],
     ModificationDate,
     [Agency_Id],
     [Id_Avts_ContractType],
     [Beneficiary_Name],
     [Id_Avts_BeneficiaryRel],
     [RFC],
     [Unbundling] 

   )
   SELECT 
    DISTINCT [NUM CONTRATO]     = TP.ID_PROSPECT
   ,[NOMBRE CLIENTE] = TP.Name + ' ' + TP.Father_Surname + ' ' + TP.Mother_Surname
   ,[DIRECCIÓN]                  = ISNULL(LTRIM(RTRIM(TP.STREET)),'')
   ,[CODIGO POSTAL]     = ISNULL(LTRIM(RTRIM(TP.Zip)), 0)
   , [CIUDAD]       = ISNULL(LTRIM(RTRIM(CC.DESC_CITY)),'')
   , [ESTADO]       = ISNULL(ST.Desc_State,'')
   , [TEL CLIENTE]    = ISNULL(LTRIM(RTRIM(TP.TELEPHONE_NUMBER)),'')
   , [CELULAR CLIENTE]     = ISNULL(LTRIM(RTRIM(TP.MOBILE_NUMBER)),'')
   ,[SUCURSAL] = CB.Name_Branch
   , [SECCION]       = TC.Section
   ,[PLAZO DE PRESTAMO] = CASE
            WHEN ISNULL(TOV.[12_SEMANAS],0) > ISNULL(TOV.[32_SEMANAS] ,0) AND ISNULL(TOV.[12_SEMANAS] ,0) > ISNULL(TOV.[42_SEMANAS] ,0) AND ISNULL(TOV.[12_SEMANAS] ,0) > ISNULL(TOV.[52_SEMANAS] ,0) THEN '12'
            WHEN ISNULL(TOV.[32_SEMANAS],0) > ISNULL(TOV.[12_SEMANAS] ,0) AND ISNULL(TOV.[32_SEMANAS] ,0) > ISNULL(TOV.[42_SEMANAS] ,0) AND ISNULL(TOV.[32_SEMANAS] ,0) > ISNULL(TOV.[52_SEMANAS] ,0) THEN '32'
            WHEN ISNULL(TOV.[42_SEMANAS],0) > ISNULL(TOV.[32_SEMANAS] ,0) AND ISNULL(TOV.[42_SEMANAS] ,0) > ISNULL(TOV.[52_SEMANAS] ,0)  AND ISNULL(TOV.[42_SEMANAS] ,0) > ISNULL(TOV.[12_SEMANAS] ,0) THEN '42'
              WHEN ISNULL(TOV.[52_SEMANAS],0) > ISNULL(TOV.[42_SEMANAS] ,0) AND ISNULL(TOV.[52_SEMANAS] ,0) > ISNULL(TOV.[12_SEMANAS] ,0) AND ISNULL(TOV.[52_SEMANAS] ,0) > ISNULL(TOV.[32_SEMANAS] ,0)THEN '52'
              END
   , [CREDITO SOLICITADO]               = CPR.VALUE
   ,[descripcion] = CT.Desc_Status_Cis
   ,[CANTIDAD MAXIMA AUTORIZADA] =CASE
               WHEN ISNULL(CONVERT(DECIMAL(18,4),CONVERT(INT,TOV.[12_SEMANAS])),0) > ISNULL(CONVERT(DECIMAL(18,4),CONVERT(INT,TOV.[32_SEMANAS])),0) AND
                ISNULL(CONVERT(DECIMAL(18,4),CONVERT(INT,TOV.[12_SEMANAS])),0) > ISNULL(CONVERT(DECIMAL(18,4),CONVERT(INT,TOV.[42_SEMANAS])),0)  AND
                ISNULL(CONVERT(DECIMAL(18,4),CONVERT(INT,TOV.[12_SEMANAS])),0) > ISNULL(CONVERT(DECIMAL(18,4),CONVERT(INT,TOV.[52_SEMANAS])),0)
                 THEN ISNULL(CONVERT(DECIMAL(18,2),CONVERT(INT,TOV.[12_SEMANAS])),0)

               WHEN ISNULL(CONVERT(DECIMAL(18,4),CONVERT(INT,TOV.[32_SEMANAS])),0) > ISNULL(CONVERT(DECIMAL(18,4),CONVERT(INT,TOV.[12_SEMANAS])),0) AND
                ISNULL(CONVERT(DECIMAL(18,4),CONVERT(INT,TOV.[32_SEMANAS])),0) > ISNULL(CONVERT(DECIMAL(18,4),CONVERT(INT,TOV.[42_SEMANAS])),0)  AND
                ISNULL(CONVERT(DECIMAL(18,4),CONVERT(INT,TOV.[32_SEMANAS])),0) > ISNULL(CONVERT(DECIMAL(18,4),CONVERT(INT,TOV.[52_SEMANAS])),0)
                THEN ISNULL(CONVERT(DECIMAL(18,2),CONVERT(INT,TOV.[32_SEMANAS])),0)

               WHEN ISNULL(CONVERT(DECIMAL(18,4),CONVERT(INT,TOV.[42_SEMANAS])),0) > ISNULL(CONVERT(DECIMAL(18,4),CONVERT(INT,TOV.[32_SEMANAS])),0) AND 
               ISNULL(CONVERT(DECIMAL(18,4),CONVERT(INT,TOV.[42_SEMANAS])),0) > ISNULL(CONVERT(DECIMAL(18,4),CONVERT(INT,TOV.[12_SEMANAS])),0) AND
               ISNULL(CONVERT(DECIMAL(18,4),CONVERT(INT,TOV.[42_SEMANAS])),0) > ISNULL(CONVERT(DECIMAL(18,4),CONVERT(INT,TOV.[52_SEMANAS])),0)
                THEN ISNULL(CONVERT(DECIMAL(18,2),CONVERT(INT,TOV.[42_SEMANAS])),0)

                  WHEN ISNULL(CONVERT(DECIMAL(18,4),CONVERT(INT,TOV.[52_SEMANAS])),0) > ISNULL(CONVERT(DECIMAL(18,4),CONVERT(INT,TOV.[42_SEMANAS])),0) AND
               ISNULL(CONVERT(DECIMAL(18,4),CONVERT(INT,TOV.[52_SEMANAS])),0) > ISNULL(CONVERT(DECIMAL(18,4),CONVERT(INT,TOV.[12_SEMANAS])),0) AND
               ISNULL(CONVERT(DECIMAL(18,4),CONVERT(INT,TOV.[52_SEMANAS])),0) > ISNULL(CONVERT(DECIMAL(18,4),CONVERT(INT,TOV.[32_SEMANAS])),0)
               THEN ISNULL(CONVERT(DECIMAL(18,2),CONVERT(INT,TOV.[52_SEMANAS])),0)
              END
   ,[COLONY] = TP.Colony 
   , [FECHA]   = TC.Modification_Date
   ,[HORA]  = CONVERT(VARCHAR(10), GETDATE(), 108)
   ,[Branch_No] = CB.Branch_No  
   ,[Ext_Number] = TP.Ext_Number 
   ,[Int_Number] = TP.Int_Number 
            ,[Term1] = case 
         when TOV.[12_SEMANAS] IS NOT NULL then '12' ELSE   '52' end  
   ,[Offer1] = case
    when TOV.[12_SEMANAS] IS NOT NULL then CONVERT(DECIMAL(18,4),CONVERT(INT,TOV.[12_SEMANAS])) ELSE  ISNULL(CONVERT(DECIMAL(18,4),CONVERT(INT,TOV.[52_SEMANAS])),0) end 

   ,[Term2] = '32' 
   ,[Offer2] = ISNULL(CONVERT(DECIMAL(18,4),CONVERT(INT,TOV.[32_SEMANAS])),0)
   ,[Term3] = '42'
   ,[Offer3] = ISNULL(CONVERT(DECIMAL(18,4),CONVERT(INT,TOV.[42_SEMANAS])),0)
   ,[Modification_Date] = TC.Modification_Date
   ,[Agency_Id] = TC.AGENCY_ID 
   ,[Id_Avts_ContractType] = TP.Id_Avts_ContractType
   ,[Beneficiary_Name] = TP.Beneficiary_Name
   ,[Id_Avts_BeneficiaryRel] = TP.Id_Avts_BeneficiaryRel
   ,[RFC] = TP.RFC

   -- LOGICA CORRECTA DE UNBUNDLING:
   -- Solo inserta el literal 'N1' o 'N2' si existen en el texto.
   -- Si tiene 'S 1' u otra cosa, inserta NULL.
   ,[Unbundling] = CASE 
                        WHEN TC.DecMessageText LIKE '%N1%' THEN 'N1'
                        WHEN TC.DecMessageText LIKE '%N2%' THEN 'N2'
                        ELSE NULL 
                   END

  FROM      #tcis                   TC  WITH (NOLOCK)----------------
  JOIN      APPLICATION_SCORE.DBO.TCIS_PERSONAL            TP  WITH (NOLOCK) ON TC.ID_PROSPECT    = TP.ID_PROSPECT ------
  LEFT JOIN APPLICATION_SCORE.DBO.CPRODUCTS                CPR WITH (NOLOCK) ON TC.ID_PRODUCT     = CPR.ID_PRODUCT AND TC.ID_TERM = CPR.ID_TERM------ 
  LEFT JOIN APPLICATION_SCORE.DBO.CCITIES                  CC WITH (NOLOCK) ON TP.ID_CITY     = CC.ID_CITY--------------
  LEFT JOIN APPLICATION_SCORE.DBO.CSTATES       ST WITH (NOLOCK) ON TP.ID_STATE    = ST.ID_STATE--------------
  left join CBranches CB with (nolock) on CB.Id_Branch = TC.Id_Branch
  LEFT JOIN #TOfertas_Value AS TOV  with (nolock) ON tov.id_prospect=tc.id_prospect
  left join CStatus_Cis CT with (nolock) on CT.Id_Status_Cis = TC.Id_Status_Cis
  LEFT JOIN SentProspects  SP WITH(NOLOCK) ON TP.Id_Prospect = SP.Id_Prospect
  WHERE TC.App_Score_Status = 'Accepted'
    AND (CT.Id_Status_Cis IN (3,4)) 
    AND (SP.Id_Prospect IS NULL OR TC.Modification_Date > SP.DateSent)
    and CT.Desc_Status_Cis IS NOT NULL 


--SE ELIMINAN LOS REGISTROS QUE YA EXISTAN EN LA TABLA DESTINO 
DELETE FROM [GeoCoverage_YFOS].[dbo].[ValiadtedProspects]
WHERE Id_Prospect IN (SELECT DISTINCT Id_Prospect FROM TEMPValidatedProspects where Term IS NOT NULL)

--SE INSERTAN LOS REGISTROS QUE NO EXISTAN EN LA TABLA DESTINO DE YFOS  
INSERT INTO [GeoCoverage_YFOS].[dbo].[ValiadtedProspects]
SELECT Id_Prospect ,
      Name ,
      [Address] ,
      zip ,
      City ,
      [State] ,
      TelephoneNumber ,
      MobileNumber ,
      Name_Branch ,
      Section ,      
      Term ,
      Product_Value ,
      Desc_Status_Cis,
      MaxOffer,
      [Date], 
      FORMAT([Hour],'hh:mm'),
      [Colony],  
      [Branch_No], 
      [Ext_Number],
      [Int_Number],
      [Term1],
      [Offer1], 
      [Term2],
      [Offer2],
      [Term3],
      [Offer3],
      NULL,  
      NULL,
      NULL,
      [Agency_Id],
      [Id_Avts_ContractType], 
      [Beneficiary_Name],
      [Id_Avts_BeneficiaryRel],
      [RFC],
      [Unbundling] 
      FROM TEMPValidatedProspects TMP 
      WHERE Term IS NOT NULL    

-- ACTUALIZA LAS FECHAS DE MODIFICACION DE LOS REGISTROS YA INSERTADOS YA REGISTRADOS 
UPDATE SP
  SET SP.DateSent = TMP.ModificationDate
	FROM dbo.SentProspects SP
	INNER JOIN TEMPValidatedProspects TMP ON SP.Id_Prospect = TMP.Id_Prospect and TMP.Term IS NOT NULL


-- INSERTA LOS REGISTROS NUEVOS EN LA BITÁCORA DE ENVÍO 
INSERT INTO dbo.SentProspects
         ( Id_Prospect, Sent, DateSent)
    SELECT DISTINCT SP.Id_Prospect, 1, SP.ModificationDate
    FROM TEMPValidatedProspects SP
    WHERE SP.Id_Prospect NOT IN (SELECT Id_Prospect FROM SentProspects)  and SP.Term IS NOT NULL 

/*Se eliminan los datos para que no persistan*/
TRUNCATE TABLE TEMPValidatedProspects

drop TABLE #tcis
drop TABLE #TOfertas_Value
END