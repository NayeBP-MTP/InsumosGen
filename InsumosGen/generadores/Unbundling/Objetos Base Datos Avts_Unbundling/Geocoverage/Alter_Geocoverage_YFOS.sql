USE Geocoverage_YFOS
 /*Cambios proceso clientes frecuentes*/
ALTER TABLE [dbo].[STAGE_Pesos_Offer]
ADD Unbundling VARCHAR(25) NULL
 
ALTER TABLE [dbo].[Pesos_Offer]
ADD Unbundling VARCHAR(25) NULL
 
ALTER TABLE [dbo].[Pesos_Offer_Historic]
ADD Unbundling VARCHAR(25) NULL

/*Cambios proceso scoring*/
ALTER TABLE [dbo].[ValiadtedProspects]
ADD Unbundling VARCHAR(25) NULL

ALTER TABLE [dbo].[ValiadtedProspects_Historic]
ADD Unbundling VARCHAR(25) NULL