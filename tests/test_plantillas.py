"""Las plantillas como datos (insumos/plantillas.py) deben coincidir con los .sql de referencia."""
import re
from pathlib import Path

import pytest

from insumos import plantillas

SQL_DIR = Path("config/Context/crearClientesFC")

CASOS = [
    ("queryCustomerTable.sql", plantillas.CUSTOMER, plantillas.CUSTOMER_TABLA),
    ("queryAgreementTable.sql", plantillas.AGREEMENT, plantillas.AGREEMENT_TABLA),
    ("queryCustomerAddressTable.sql", plantillas.CUSTOMER_ADDRESS, plantillas.CUSTOMER_ADDRESS_TABLA),
]


def _columnas_sql(archivo):
    sql = (SQL_DIR / archivo).read_text(encoding="utf-8")
    m = re.search(r"INSERT\s+INTO\s+(\S+)\s*\((.*?)\)\s*VALUES", sql, re.S | re.I)
    sin_comentarios = re.sub(r"--[^\n]*", "", m.group(2))
    cols = [c.strip().strip("[]") for c in sin_comentarios.split(",") if c.strip()]
    return m.group(1).replace("[", "").replace("]", ""), cols


@pytest.mark.parametrize("archivo,plantilla,tabla", CASOS)
def test_columnas_y_orden_coinciden_con_el_sql(archivo, plantilla, tabla):
    tabla_sql, columnas = _columnas_sql(archivo)
    assert list(plantilla) == columnas
    assert len(set(columnas)) == len(columnas)
    assert tabla == tabla_sql


def test_valores_clave_de_la_plantilla_de_agreement():
    a = plantillas.AGREEMENT
    assert a["Agreement_Status_Code"] == "AC" and a["Company_Code"] == "MEX"
    # los cinco montos de la venta que los módulos deben sobrescribir existen en la plantilla
    for col in ("First_Instalment_Value", "Regular_Instalment_Value", "Final_Instalment_Value_At_Issue",
                "Issue_Value", "Outstanding_Balance"):
        assert col in a


def test_las_plantillas_son_independientes_de_los_sql_en_tiempo_de_ejecucion():
    # los módulos copian la plantilla antes de modificarla; este test documenta que son dicts normales
    copia = dict(plantillas.CUSTOMER)
    copia["Customer_Id"] = 123
    assert plantillas.CUSTOMER["Customer_Id"] == 0
