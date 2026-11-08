"""Pruebas unitarias (sin BD) de las escrituras de OriginacionRepository y CnfsRepository en dry_run."""
from insumos import plantillas
from services.cnfs_repository import CnfsRepository, sentencia_insert
from services.originacion_repository import OriginacionRepository


def test_sentencia_insert_usa_columnas_entre_corchetes_y_parametros():
    sql, params = sentencia_insert("[NFS_DBO].[T]", {"A": 1, "B": None, "C": "x"})
    assert sql == "INSERT INTO [NFS_DBO].[T] ([A], [B], [C]) VALUES (?, ?, ?)"
    assert params == (1, None, "x")


def test_insert_de_las_plantillas_tiene_tantos_parametros_como_columnas():
    for tabla, plantilla in (("[NFS_DBO].[Agreement_Table]", plantillas.AGREEMENT),
                             ("[NFS_DBO].[Customer_Table]", plantillas.CUSTOMER),
                             ("[NFS_DBO].[Customer_Address_Table]", plantillas.CUSTOMER_ADDRESS)):
        sql, params = sentencia_insert(tabla, plantilla)
        assert sql.count("?") == len(params) == len(plantilla)


def test_cnfs_dry_run_no_escribe_y_deja_las_sentencias_en_orden():
    repo = CnfsRepository(dry_run=True)
    repo.insertar_agreement({"Agreement_Num": 240021110, "Customer_Id": 0})
    repo.insertar_cliente_y_direccion({"Customer_Id": 5}, {"Customer_Id": 5, "Customer_Address_Db_Id": 1})
    repo.actualizar_customer_id_agreement("240021110", 2611070401001)
    sqls = [s for s, _ in repo.dry_run_log]
    assert [s.split("[")[0].split()[0] for s in sqls] == ["INSERT", "INSERT", "INSERT", "UPDATE"]
    assert "[Agreement_Table]" in sqls[0] and "[Customer_Table]" in sqls[1] and "[Customer_Address_Table]" in sqls[2]
    assert repo.dry_run_log[3] == (
        "UPDATE [NFS_DBO].[Agreement_Table] SET Customer_Id = ? WHERE Agreement_Num = ?",
        (2611070401001, 240021110),
    )


def test_originacion_dry_run_deja_los_update():
    repo = OriginacionRepository(dry_run=True)
    repo.actualizar_nombre_rfc(7329, "NUEVO NOMBRE", "NUNO900101AB1")
    repo.actualizar_cliente(7329, 2611070401001)
    repo.actualizar_id_paso(7329, 22)
    assert repo.dry_run_log == [
        ("UPDATE [dbo].[ExpedienteCliente] SET NombreCliente = ?, RFCCliente = ? WHERE IdExpedienteCliente = ?",
         ("NUEVO NOMBRE", "NUNO900101AB1", 7329)),
        ("UPDATE [dbo].[ExpedienteCliente] SET Cliente = ? WHERE IdExpedienteCliente = ?", (2611070401001, 7329)),
        ("UPDATE [dbo].[ExpedienteCliente] SET IdPaso = ? WHERE IdExpedienteCliente = ?", (22, 7329)),
    ]
