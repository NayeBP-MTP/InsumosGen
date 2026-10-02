USE [Application_Score]
GO
/****** Object:  StoredProcedure [dbo].[sp_Insert_Score_Results]    Script Date: 09/02/2026 10:43:58 a. m. ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO


/*
Fecha Creación: 12/14/2017
Descripcion: Incluye la fecha de modificación en TCis
*/


/********************************************************** 
*Procedure Name: [sp_Insert_Score_Results]
*Description : Update Score Result Information into [TCis] 
*Author: MPM Date : 30/05/2010  creation
*********************************************************/ 
ALTER PROCEDURE [dbo].[sp_Insert_Score_Results]
(
	 @Id_Prospect		     bigint	
    ,@App_Score_Result 		 int
    ,@Id_Status_Score        int
    ,@App_Score_Status 		 nvarchar(20)
	,@Id_Strategy_Score_Band int 
    ,@Income_INEGI           float  -- it was saved when save the first data flow
    ,@Id_Rejected_Reason     int
    ,@Process_Time           int
    ,@Id_Customer_Type       int
    ,@Id_Strategy_FICO_Band   int
    ,@Type_FICO     nvarchar(15)
    ,@Id_Fico int
    ,@Score_FICO int
	,@DecMessageText     nvarchar(MAX) -- <<< CAMBIO AQUI: Nuevo parámetro agregado Unbundling

)
AS
SET NOCOUNT ON
BEGIN

    if @Id_Rejected_Reason=-1
    BEGIN
	UPDATE [TCis]
	SET
		  [App_Score_Result]=@App_Score_Result
		 ,[Id_Status_Score]= @Id_Status_Score				 
		 ,[App_Score_Status]= @App_Score_Status             
		 ,[Id_Strategy_Score_Band]=@Id_Strategy_Score_Band                         
		 ,[Income_INEGI]=@Income_INEGI          				             
		 ,[Id_Rejected_Reason]=NULL --@Id_Rejected_Reason   
         ,[Process_Time]=@Process_Time   
         ,[Id_Customer_Type]=@Id_Customer_Type--new
         ,[Id_Strategy_FICO_Band] =@Id_Strategy_FICO_Band --FICO 16/12/2013
         ,[Score_FICO] =@Type_FICO  --FICO 16/12/2013
         ,[FICO_Score_Result]=@Score_FICO  --FICO 16/12/2013
		 ,[Modification_Date]=GETDATE()
		 ,[DecMessageText]=@DecMessageText -- <<< CAMBIO AQUI: Nuevo parámetro agregado Unbundling

	WHERE [Id_Prospect]=@Id_Prospect
    END
    ELSE
    BEGIN
         UPDATE [TCis]
	      SET
		  [App_Score_Result]=@App_Score_Result
		 ,[Id_Status_Score]= @Id_Status_Score				 
		 ,[App_Score_Status]= @App_Score_Status             
		 ,[Id_Strategy_Score_Band]=null-- @Id_Strategy_Score_Band                      
		 ,[Income_INEGI]=@Income_INEGI          				             
		 ,[Id_Rejected_Reason]=@Id_Rejected_Reason   
         ,[Process_Time]=@Process_Time   
         ,[Id_Customer_Type]=@Id_Customer_Type--new
         ,[Id_Strategy_FICO_Band] = NULL --@Id_Strategy_FICO_Band
         ,[Score_FICO] =@Type_FICO
        ,[FICO_Score_Result]=@Score_FICO  --FICO 16/12/2013
		,[Modification_Date]=GETDATE()
		,[DecMessageText]=@DecMessageText -- <<< CAMBIO AQUI: Nuevo parámetro agregado Unbundling
		
	      WHERE [Id_Prospect]=@Id_Prospect
    END
    
    If @Id_Fico!=0
	begin
    UPDATE  [T_Fico]
   SET 
    [FICO_score]= @Type_FICO
   WHERE 
     [Id_Fico]= @Id_Fico
	 update Tcis set Id_Fico=@Id_Fico where Id_Prospect=@Id_Prospect
	 end
	RETURN
	SET NOCOUNT OFF
END

SET ANSI_NULLS ON



/****** Object:  StoredProcedure [dbo].[sp_Edit_TCis]    Script Date: 01/04/2018 09:02:54 a. m. ******/
SET ANSI_NULLS ON
