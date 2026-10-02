--Tabla contratos y su contenido
id | nombre | idSucursal | prefijo | direccion | ciudad | estado | diaPago | template_id | --+--------------+----------+-------+---------------------------------------------------------------------------------------------+---------------+---------------+-------+------------------------+
1 | Izcalli | 2075 | PR | Av.31 Poniente | Mexico | Mexico | Viernes | 670700de6865ee4cfe4e7ca2 | 2 | Zacatecas | 2060 | FN | Avenida Sevilla No.111 | Zacatecas | Zacatecas | Jueves | 69698085f519861b225b2aae | 3 | Tijuana | 2093 | GS | Boulevard Agua Caliente No.8582 4to Piso,
Zona Centro,
C.P.22000,
Tijuana,
Baja California | Tijuana | Baja California | Jueves | 69698085f519861b225b2aae | 4 | Aguascalientes | 2025 | EF | Av Aguascalientes Sur 201,
Prados del Sur,
20235 Aguascalientes,
Ags | Aguascalientes | Aguascalientes | Jueves | 69698085f519861b225b2aae | 5 | San Luis 2 | 2049 | EW | Av.31 Poniente | San Luis Potosi | San Luis Potosi | Jueves | 69698085f519861b225b2aae | --Tabla history
id | createdAt | email | folioInicio | folioFin | sucursal | trackingId | deleted | --+-----------------------+-----+-----------+--------+--------+----------+-------+
1 | 2025 -08 -04 17 :09 :52.333 | Admin | 23001001 | 23002000 | 2075 | | 0 | 2 | 2025 -08 -04 17 :10 :55.637 | Admin | 24001001 | 24002000 | 2075 | | 0 | 3 | 2025 -11 -26 17 :10 :55.637 | Admin | 25001001 | 25002000 | 2060 | | 0 | 4 | 2025 -12 -04 17 :10 :55.637 | Admin | 26001001 | 26002000 | 2093 | | 0 | 5 | 2026 -02 -05 18 :17 :55.637 | Admin | 27001001 | 27002000 | 2025 | | 0 | 6 | 2026 -02 -05 18 :17 :55.637 | Admin | 28001001 | 28002000 | 2049 | | 0 | --tabla contratos (Ejemplo de como esta se alimenta. Si te das cuenta toma el id de sucursal y el id History)
id | folioContrato | numeroContrato | idSucursal | idHistory --+-------------+--------------+----------+---------+
6 | 101 | PR25001061 | 1 | 2 --query que he ocupado para generar más folios para las diferentes agencias, este he usado.
-- Insert 1,000 consecutive rows (the original + 999 more)
;
WITH nums AS (
    -- produce numbers 0..999
    SELECT TOP (1000) ROW_NUMBER() OVER (
            ORDER BY (
                    SELECT NULL
                )
        ) - 1 AS n
    FROM master..spt_values a
        CROSS JOIN master..spt_values b
)
INSERT INTO RegistroContratos.dbo.contratos (
        folioContrato,
        numeroContrato,
        idSucursal,
        idHistory
    )
SELECT N'EF' + CONVERT(varchar(20), 28001001 + n) -- folio: GS26001001, GS26001002, ...
,
    280010001 + n -- numeroContrato: 260010001, 260010002, ...
,
    4,
    5
FROM nums;