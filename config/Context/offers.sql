INSERT INTO [dbo].[Ofertas]
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
           ,[FechaActualizacion]
           ,[EarlySettlementRebateValue]
           ,[Outstanding_Balance])
     VALUES
           (26094007 -- IdOferta incrementado se construye a través de (26 (año) + 09 (mes) + 4 identificador único por persona + 00N (consecutivo) 
           ,'NADIA HUERTA' -- Inventado
           ,80.0 -- Se mantiene
           ,8500 -- Se mantiene
           ,'RE' Si es Refin en el Mensaje de pesos (descOferta) es RE, sino será AD
           ,NULL -- Se mantiene NULL
           ,NULL -- Se mantiene NULL
           ,'Calle 60 No. 415, Col. Centro, CP 97000, Mérida, Yucatán' -- Se mantiene NULL
           ,2025000001234 -- Depende de la agencia a la que se quiere asignar la venta
           ,'S' -- Depende de la agencia a la que se quiere asignar la venta
           ,'amOferta' --Se mantiene
           ,2025 --Son los ptimeros 4 dígitos de la agencia (ejemplo:2025000001234 sólo se toma 2025)
           ,1 -- se mantiene en 1
           ,NULL -- Se mantiene
           ,'TARIFA MÁX 700 REFIN! 260010111 21000/65 D' -- Se genera de acuerdo a las reglas de negocio
           ,202633 --Semana actual del año, cambia cada miércoles
           ,2093726050022 -- modificar Customer_Id -- Se autogenera del siguiente modo: 2075 (primeros 4 digitos de la agencia) + 2609 (año y mes a 4 digitos) + 4 (Identificador por persona) + 000N (Consecutivo)
           ,260010111 -- modificar Agreement_Num --Se autogenera: 2609 (año y mes a 4 digitos) + 4 identificador por persona + 000N (Consecutivo)
           ,291 -- modificar Agreement_Id ---------------- (NULL)
           ,2000 -- modificar Agreement_Db_Id --(NULL)
           ,10917.52 -- Modificar (Settlement_Balance) --(NULL)
           ,'1999-10-14 00:00:00.000' -- Inventado
           ,'ROOG910311H47' -- Inventado
           ,'CC'
           ,'AC' -- Del nuevo registro (Agreement_Status_Code)
           ,NULL
           ,NULL
           ,'2026-09-03 12:29:46.707' --Fecha del día
           ,NULL
           ,NULL)