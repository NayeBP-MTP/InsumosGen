from typing import Optional

from services.db import SqlServerRepository

TABLA_AGREEMENT = "[NFS_DBO].[Agreement_Table]"
TABLA_CUSTOMER = "[NFS_DBO].[Customer_Table]"
TABLA_ADDRESS = "[NFS_DBO].[Customer_Address_Table]"


def sentencia_insert(tabla: str, valores: dict) -> tuple:
    """INSERT parametrizado (sql, params) para un dict columna -> valor (plantilla ya rellenada)."""
    columnas = ", ".join(f"[{c}]" for c in valores)
    marcas = ", ".join("?" for _ in valores)
    return f"INSERT INTO {tabla} ({columnas}) VALUES ({marcas})", tuple(valores.values())


class CnfsRepository(SqlServerRepository):
    """
    Acceso a CNFS_uat.NFS_DBO (host CNFS, conexión CNFS del almacén de credenciales): Customer_Table, Agreement_Table y
    Customer_Address_Table. Los INSERT salen de las plantillas de `insumos/plantillas.py`.
    """

    def __init__(self, dry_run: bool = False):
        super().__init__("CNFS_uat", dry_run=dry_run)

    def _escalar(self, sql: str, params=()):
        with self._get_connection() as conn:
            fila = conn.execute(sql, params).fetchone()
            return fila[0] if fila else None

    # --- lecturas ---

    def agreement_existe(self, numero_contrato) -> bool:
        return self._escalar(
            f"SELECT 1 FROM {TABLA_AGREEMENT} WHERE Agreement_Num = ?", (int(numero_contrato),)
        ) is not None

    def customer_id_de_agreement(self, numero_contrato) -> Optional[int]:
        """`Customer_Id` del contrato (0 si aún no tiene cliente) o None si el contrato no existe."""
        return self._escalar(
            f"SELECT Customer_Id FROM {TABLA_AGREEMENT} WHERE Agreement_Num = ?", (int(numero_contrato),)
        )

    def customer_existe(self, customer_id) -> bool:
        return self._escalar(
            f"SELECT 1 FROM {TABLA_CUSTOMER} WHERE Customer_Id = ?", (int(customer_id),)
        ) is not None

    def address_existe(self, customer_id, customer_address_db_id) -> bool:
        return self._escalar(
            f"SELECT 1 FROM {TABLA_ADDRESS} WHERE Customer_Id = ? AND Customer_Address_Db_Id = ?",
            (int(customer_id), int(customer_address_db_id)),
        ) is not None

    def max_customer_id_con_prefijo(self, prefijo: int) -> Optional[int]:
        """Mayor `Customer_Id` de 13 dígitos que empieza con `prefijo` (10 dígitos: AAMMDD + colaborador + 02), o None."""
        base = int(prefijo) * 1000
        return self._escalar(
            f"SELECT MAX(Customer_Id) FROM {TABLA_CUSTOMER} WHERE Customer_Id BETWEEN ? AND ?",
            (base, base + 999),
        )

    # --- escrituras (con dry_run) ---

    def insertar_agreement(self, valores: dict) -> None:
        self._escribir(*sentencia_insert(TABLA_AGREEMENT, valores))

    def insertar_cliente_y_direccion(self, customer: dict, direccion: dict) -> None:
        """Las dos altas del registro de cliente en una sola transacción."""
        self._escribir_transaccion([
            sentencia_insert(TABLA_CUSTOMER, customer),
            sentencia_insert(TABLA_ADDRESS, direccion),
        ])

    def actualizar_customer_id_agreement(self, numero_contrato, customer_id) -> None:
        self._escribir(
            f"UPDATE {TABLA_AGREEMENT} SET Customer_Id = ? WHERE Agreement_Num = ?",
            (int(customer_id), int(numero_contrato)),
        )

    # --- borrados (solo para deshacer lo que insertaron los módulos) ---

    def borrar_agreement(self, numero_contrato) -> None:
        self._escribir(f"DELETE FROM {TABLA_AGREEMENT} WHERE Agreement_Num = ?", (int(numero_contrato),))

    def borrar_customer(self, customer_id) -> None:
        self._escribir(f"DELETE FROM {TABLA_CUSTOMER} WHERE Customer_Id = ?", (int(customer_id),))

    def borrar_address(self, customer_id, customer_address_db_id) -> None:
        self._escribir(
            f"DELETE FROM {TABLA_ADDRESS} WHERE Customer_Id = ? AND Customer_Address_Db_Id = ?",
            (int(customer_id), int(customer_address_db_id)),
        )
