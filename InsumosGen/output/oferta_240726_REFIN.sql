-- Ofertas REFIN para agencia Izcalli 2075000000335, sección R
-- Generadas: 2026-07-24
-- Semana actual: 202630 (miércoles más reciente: 2026-07-22)
-- Consecutivos: 26074063 y 26074064
-- Características: REFIN plazo 42, con y sin seguro

INSERT INTO [botDB].[dbo].[Ofertas]
         ([idOferta]
         ,[nombreCliente]
         ,[porcentajeCalidadCliente]
         ,[montoOferta]
         ,[tipoDeOferta]
         ,[telefonoCliente1]
         ,[telefonoCliente2]
         ,[direccionCliente]
         ,[agenciaCliente]
         ,[seccionCliente]
         ,[amOferta]
         ,[branchOferta]
         ,[idEstatusOferta]
         ,[EstatusComentario]
         ,[descOferta]
         ,[semana]
         ,[Customer_Id]
         ,[Agreement_Num]
         ,[Agreement_Id]
         ,[Agreement_Db_Id]
         ,[Agreement_Balance]
         ,[FechaNacimiento]
         ,[RFC]
         ,[Customer_Status_Code]
         ,[Agreement_Status_Code]
         ,[DireccionCobranzaCliente]
         ,[VendidaProvidigital]
         ,[FechaActualizacion])
   VALUES
         -- Oferta 1: REFIN plazo 42, CON SEGURO
         (26074063
         ,'PATRICIA ANDREA LUNA ESPINOZA'
         ,81
         ,6500
         ,'RE'
         ,NULL
         ,NULL
         ,'Miguel Hidalgo 159 Col. Centro, C.P. 54700 Toluca, Estado de Mexico'
         ,2075000000335
         ,'R'
         ,'amOferta'
         ,2075
         ,1
         ,NULL
         ,'TARIFA MÁX 1180 REFIN! 510264063 6500/42 A S'
         ,202630
         ,2075426074063
         ,510264063
         ,NULL
         ,NULL
         ,NULL
         ,'1990-05-12 00:01:23.457'
         ,'LUEP900512MN7'
         ,'CC'
         ,NULL
         ,NULL
         ,1
         ,'2026-07-24'),

         -- Oferta 2: REFIN plazo 42, SIN SEGURO
         (26074064
         ,'ROBERTO ISRAEL FUENTES MORALES'
         ,79
         ,8500
         ,'RE'
         ,NULL
         ,NULL
         ,'Miguel Hidalgo 159 Col. Centro, C.P. 54700 Toluca, Estado de Mexico'
         ,2075000000335
         ,'R'
         ,'amOferta'
         ,2075
         ,1
         ,NULL
         ,'TARIFA MÁX 1420 REFIN! 510264064 8500/42 B'
         ,202630
         ,2075426074064
         ,510264064
         ,NULL
         ,NULL
         ,NULL
         ,'1987-11-29 00:01:23.457'
         ,'FUMR871129HD4'
         ,'CC'
         ,NULL
         ,NULL
         ,1
         ,'2026-07-24');
