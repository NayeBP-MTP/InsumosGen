Pasos para crear de cero una nueva agencia y nuevos usuarios Provident.
--1.- Dar de alta en la tabla Agency Structure de la BD de Challenger(DEV- UAT)
insert into [Challenger_uat].[dbo].[AgencyStructure] 
 values(2075000001234, 2075000012345, 'Pablo Enciso', 'IzcalliDM62C', 2075000012789, 'Katerin Perez','C','AM530 Izcalli', 2075000012987,'Yadira gonzalez')

--2.- Dar de alta los usuarios en la tabla de tblRepresentative_Table_AWS en Challenger(DEV- UAT)
insert into [dbo].[tblRepresentative_Table_AWS] 
Values(2075000012345, 'pablo.enciso@provident.com.mx', 'Pablo Enciso', 2225990807, 2, 1, 'XXXX021906GTO')

--3.- Crear su Categoria de la agencia en la tabla P_Estrella_Mensual_Category
  insert into [Challenger_uat].[dbo].[P_ESTRELLAS_MENSUAL_CATEGORIAS]
  ( [Representative_name] ,[Branch],[Agency_Id],[Representative_Id],[DM_Letter],[Month_Calc],[Category],[Payment_Month],[Avg_Collected_Cust],[Sales_Volume],[NetIncrease],[Avg_payment_coll],[GdsCategory])
 Values('Pablo Enciso','Cuautitlán Izcalli',2075000001234,2075000012345, 'C','Junio','ULTRA', 'Julio',0.905, 23, 2, 0.09,'ULTRA')

-- 4.- Generar la agencia en la tabla Agency_Representative_AWS de la BD de BOTDB de la instancia Pesos Offers(DEV -UAT)
 insert into [botDB].[dbo].[Agency_Representative_AWS] values (2075000001234,2075000012345, 2075)

-- 5.- Generar los usuarios en la tabla tblRepresentative Table de la BD de BotDB en la instancias de pesos offers
 insert into [dbo].[tblRepresentative_Table_AWS] 
Values(2075000012345, 'juan.enciso@provident.com.mx', 'Pablo Enciso', 2225990807, 2, 1, 'XXXX021906GTO')