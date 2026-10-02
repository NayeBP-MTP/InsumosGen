/* =========================================================================
   OfertasRefin_N1N2N3_310826.sql
   Generacion de Ofertas - Semana 202635
   - 3 REFIN Cliente Frecuente con nivel de descuento N1, N2, N3
   - Sucursal Fronteriza, Seccion A (agencia 2093000000111)
   Consecutivo idOferta: 26084062 - 26084064
   FechaActualizacion: 2026-08-31
   ========================================================================= */

-- =========================================================================
-- SECCION A (Sucursal Fronteriza - Agencia 2093000000111) - REFIN N1
-- =========================================================================

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
         (26084062,'Lorena Patricia Esquivel Montes',79,8000,'RE',NULL,NULL,'Calle Insurgentes 320 Col. Centro, C.P. 88000 Nuevo Laredo, Tamaulipas',2093000000111,'A','amOferta',2093,1,NULL,'TARIFA MÁX 650 REFIN! 510264062 8000/32 A N1',202635,2093426084062,510264062,NULL,NULL,NULL,'1991-04-17 00:01:23.457','ESML910417','CC',NULL,NULL,1,'2026-08-31');

-- =========================================================================
-- SECCION A (Sucursal Fronteriza - Agencia 2093000000111) - REFIN N2
-- =========================================================================

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
         (26084063,'Mauricio Andres Salinas Vidal',82,11000,'RE',NULL,NULL,'Av. Guerrero 450 Col. Jardin, C.P. 87000 Ciudad Victoria, Tamaulipas',2093000000111,'A','amOferta',2093,1,NULL,'TARIFA MÁX 900 REFIN! 510264063 11000/42 B S N2',202635,2093426084063,510264063,NULL,NULL,NULL,'1988-09-25 00:01:23.457','SAVM880925','CC',NULL,NULL,1,'2026-08-31');

-- =========================================================================
-- SECCION A (Sucursal Fronteriza - Agencia 2093000000111) - REFIN N3
-- =========================================================================

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
         (26084064,'Claudia Berenice Fuentes Ibarra',84,15000,'RE',NULL,NULL,'Calle Matamoros 115 Col. Las Americas, C.P. 88630 Reynosa, Tamaulipas',2093000000111,'A','amOferta',2093,1,NULL,'TARIFA MÁX 800 REFIN! 510264064 15000/52 A N3',202635,2093426084064,510264064,NULL,NULL,NULL,'1993-06-08 00:01:23.457','FUIC930608','CC',NULL,NULL,1,'2026-08-31');
