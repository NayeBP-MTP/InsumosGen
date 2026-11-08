"""Deshacer una operación: recorre el log en orden inverso y revierte lo que escribieron los módulos."""
from dataclasses import dataclass, field
from typing import Optional

from insumos.log_operacion import LogOperacion
from services.cnfs_repository import CnfsRepository
from services.originacion_repository import OriginacionRepository

T_EXPEDIENTE = "Originacion.dbo.ExpedienteCliente"
T_AGREEMENT = "CNFS_uat.NFS_DBO.Agreement_Table"
T_CUSTOMER = "CNFS_uat.NFS_DBO.Customer_Table"
T_ADDRESS = "CNFS_uat.NFS_DBO.Customer_Address_Table"


@dataclass
class ResultadoDeshacer:
    """`deshechas`: lo revertido; `omitidas`: [(descripción, motivo)] lo que no hacía falta o no se tocó."""
    operacion_id: str
    deshechas: list = field(default_factory=list)
    omitidas: list = field(default_factory=list)

    @property
    def conflictos(self) -> list:
        return [o for o in self.omitidas if o[1].startswith("conflicto")]


class Deshacedor:
    """
    Revierte cada escritura del log, de la última a la primera:
    - `insert` -> DELETE de la fila (si ya no existe, se omite);
    - `update` -> vuelve al valor `anterior`, **solo si la BD todavía tiene el valor `nuevo`**. Si alguien
      más lo cambió (p. ej. QA ya registró al usuario) no se pisa: queda como `conflicto` en `omitidas`.

    Es idempotente (volver a deshacer no encuentra nada que revertir). Al terminar anota la marca
    `deshecho` en el log, de modo que la operación puede volver a ejecutarse desde cero. En `dry_run`
    solo informa qué haría y no marca el log.
    """

    def __init__(self, originacion: Optional[OriginacionRepository] = None, cnfs: Optional[CnfsRepository] = None,
                 dry_run: bool = False):
        self.originacion = originacion or OriginacionRepository(dry_run=dry_run)
        self.cnfs = cnfs or CnfsRepository(dry_run=dry_run)
        self.dry_run = dry_run
        if self.originacion.dry_run != dry_run or self.cnfs.dry_run != dry_run:
            raise ValueError("dry_run del deshacedor y de sus repositorios deben coincidir.")

    def deshacer(self, log: LogOperacion) -> ResultadoDeshacer:
        resultado = ResultadoDeshacer(log.operacion_id)
        for entrada in log.escrituras_para_deshacer():
            descripcion = f"{entrada['modulo']}: {entrada['tipo']} en {entrada['tabla']} {entrada['llave']}"
            motivo = self._revertir(entrada)
            if motivo is None:
                resultado.deshechas.append(descripcion)
            else:
                resultado.omitidas.append((descripcion, motivo))
        if not self.dry_run:
            log.deshecho()
        return resultado

    # --- internos: cada _revertir_* devuelve None si revirtió o el motivo de la omisión ---

    def _revertir(self, e: dict) -> Optional[str]:
        accion, tabla = e["tipo"], e["tabla"]
        if accion == "insert":
            return self._borrar(tabla, e["llave"])
        if accion == "update":
            return self._restaurar(tabla, e)
        raise ValueError(f"No sé deshacer '{accion}' ({tabla}).")

    def _borrar(self, tabla: str, llave: dict) -> Optional[str]:
        if tabla == T_AGREEMENT:
            if not self.cnfs.agreement_existe(llave["Agreement_Num"]):
                return "ya no existe"
            self.cnfs.borrar_agreement(llave["Agreement_Num"])
        elif tabla == T_CUSTOMER:
            if not self.cnfs.customer_existe(llave["Customer_Id"]):
                return "ya no existe"
            self.cnfs.borrar_customer(llave["Customer_Id"])
        elif tabla == T_ADDRESS:
            if not self.cnfs.address_existe(llave["Customer_Id"], llave["Customer_Address_Db_Id"]):
                return "ya no existe"
            self.cnfs.borrar_address(llave["Customer_Id"], llave["Customer_Address_Db_Id"])
        else:
            raise ValueError(f"No sé borrar en {tabla}.")
        return None

    def _restaurar(self, tabla: str, e: dict) -> Optional[str]:
        anterior, nuevo, llave = e["anterior"], e["nuevo"], e["llave"]
        if tabla == T_AGREEMENT:
            actual = {"Customer_Id": self.cnfs.customer_id_de_agreement(llave["Agreement_Num"])}
            if actual["Customer_Id"] is None:
                return "ya no existe"
            motivo = self._comparar(actual, nuevo, anterior)
            if motivo is None:
                self.cnfs.actualizar_customer_id_agreement(llave["Agreement_Num"], anterior["Customer_Id"])
            return motivo
        if tabla == T_EXPEDIENTE:
            fila = self.originacion.leer_expediente(id_expediente=llave["IdExpedienteCliente"])
            actual = {c: fila[c] for c in anterior}
            if "Cliente" in actual:
                actual["Cliente"] = actual["Cliente"] or 0
            motivo = self._comparar(actual, nuevo, anterior)
            if motivo is None:
                self._escribir_expediente(llave["IdExpedienteCliente"], anterior)
            return motivo
        raise ValueError(f"No sé restaurar {tabla}.")

    @staticmethod
    def _comparar(actual: dict, nuevo: dict, anterior: dict) -> Optional[str]:
        """None si la BD sigue con el valor que escribió el módulo; si no, por qué se omite."""
        if all(actual[c] == nuevo[c] for c in anterior):
            return None
        if all(actual[c] == anterior[c] for c in anterior):
            return "ya estaba en su valor anterior"
        return f"conflicto: la BD tiene {actual} y el módulo había escrito {({c: nuevo[c] for c in anterior})}"

    def _escribir_expediente(self, id_expediente: int, anterior: dict) -> None:
        if set(anterior) == {"NombreCliente", "RFCCliente"}:
            self.originacion.actualizar_nombre_rfc(id_expediente, anterior["NombreCliente"], anterior["RFCCliente"])
        elif set(anterior) == {"Cliente"}:
            self.originacion.actualizar_cliente(id_expediente, anterior["Cliente"])
        elif set(anterior) == {"IdPaso"}:
            self.originacion.actualizar_id_paso(id_expediente, anterior["IdPaso"])
        else:
            raise ValueError(f"No sé restaurar las columnas {sorted(anterior)} de ExpedienteCliente.")
