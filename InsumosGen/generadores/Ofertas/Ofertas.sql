

CREATE TABLE botDB.dbo.Ofertas (
	idOferta bigint NULL,
	nombreCliente varchar(255) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	porcentajeCalidadCliente numeric(6,2) NULL,
	montoOferta float NULL,
	tipoDeOferta varchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	telefonoCliente1 varchar(20) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	telefonoCliente2 varchar(20) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	direccionCliente varchar(550) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	agenciaCliente bigint NULL,
	seccionCliente varchar(5) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	amOferta varchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	branchOferta int NULL,
	idEstatusOferta int NULL,
	EstatusComentario varchar(250) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	descOferta varchar(250) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	semana int NULL,
	Customer_Id bigint NULL,
	Agreement_Num bigint NULL,
	Agreement_Id int NULL,
	Agreement_Db_Id int NULL,
	Agreement_Balance numeric(18,4) NULL,
	FechaNacimiento datetime NULL,
	RFC varchar(20) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	id int NOT NULL,
	Customer_Status_Code varchar(10) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	Agreement_Status_Code varchar(5) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	DireccionCobranzaCliente varchar(550) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	VendidaProvidigital bit NULL,
	FechaActualizacion datetime NULL,
	EarlySettlementRebateValue float NULL,
	Outstanding_Balance float NULL
);


CREATE TABLE botDB.dbo.estatusOferta (
	idEstatusOferta int NOT NULL,
	nombre varchar(255) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	OrdenamientoClientesInteresados smallint NULL,
	CONSTRAINT PK_estatusOferta PRIMARY KEY (idEstatusOferta)
);


ALTER TABLE botDB.dbo.Ofertas ADD CONSTRAINT FK_Ofertas_estatusOferta_1 FOREIGN KEY (idEstatusOferta) REFERENCES botDB.dbo.estatusOferta(idEstatusOferta);

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
         ,[FechaActualizacion])
   VALUES   --
         (25102007 -- Este idOferta se GENERA y debe ser consecutivo se compone de 25 (el año) + 09 (el mes) +  4 +  y un consecutivo de 3 dígitos empezando en 001 para la primera, 002, para la segunda y asi sucecivamente de acuerdo al numero de ofertas solicitado
         ,'Omar Castillo Estrada' -- Este dato se GENERA (Random)
         ,80
         ,4000
         ,'AD'
         ,NULL
         ,NULL
         ,'Miguel Hidalgo 159 Col. Centro, C.P. 54700 Toluca, Estado de Mexico'
         ,2075000000335 -- Sucursal
         ,'A'  -- Se debe especificar si se requiere otra sección
         ,'amOferta'
         ,2075
         ,1
         ,NULL
         ,'TARIFA MÁX 1100 AGREGAR 10300/42 S PP20' -- Se genera de acuerdo a las siguientes reglas:
         -- <CapacidadPago> <"AGREGAR"/"REFIN!" {Contrato}> <monto>/<plazos> {'ó' <monto>/<plazos>} {flags}
         -- CapacidadPago: desde 82 hasta 1445 (aleatorio)
         -- "AGREGAR"/"REFIN!" {Contrato}: "AGREGAR" es un crédito adicional. 'REFIN!' es un refinanciamiento, Y debe llevar el número de contrato (Agreement_Num)
         -- <monto>/<plazos> {'ó' <monto>/<plazos>}: (monto/plazos)<50%(CapacidadPago). Pueden ser 1 o 2 pares de monto/plazos separados por "ó". Montos de 2000 hasta 25000 en incrementos de 500. Plazos de 12, 32, 42, 52 y 65
         -- flags (en ese orden): [nvlRiesgo] [seguro] [semCredOrig] ([Descuento]/[Nivel])
         -- nvlRiesgo: A, B, C, D, E, R. Colocar A de preferencia. R=Riesgo
         -- seguro: 'S' en caso de que el cliente requiera seguro
         -- semCredOrig: 1-23 semana en la que va el crédito original.Sólo en créditos 'AGREGAR'
         -- Descuento (Precio Preferencial): 'PP ' + 20/25 dependiendo del porcentaje del descuento. Ej. 20%=PP20. Exclusivo del nivel
         -- Nivel: N1/N2/N3 dependiendo del nivel de confianza del cliente. Exclusivo del descuento

         ,202605
         ,2075225100007 -- Customer_Id se GENERA y debe seguir el consecutivo que asignemos. 2075 (agencia) + 4 + 2602 (año y mes) + 0001 (consecutivo de cliente, este coincide con los 3 últimos digitos del idOferta)
         ,510252007 -- Agreement_Num este campo solo se llena para ofertas de tipo RE (510251001 por ejemplo) SE COMPONE DE= 510 +25 (AÑO) + 4 + ultimos 3 digitos de idOferta
         ,NULL
         ,NULL
         ,NULL
         ,'1997-11-16 00:01:23.457' -- Fecha de nacimiento (Random)
         ,'CAEO971116' -- Este dato se EDITA ("RFC")  y debe coincidir con el nombre y fecha de nacimiento 
         ,'CC'
         ,NULL
         ,NULL
         ,1
         ,'2025-10-21' -- Fecha de actualizacion a día de hoy
         )