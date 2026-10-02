# Catálogo de sucursales habilitadas para el flujo "Nueva estructura de agencia".
# Ver config/Context/NUEVA_ESTRUCTURA_AGENCIA.md para el diseño completo.
#
# - branch: número de 4 dígitos (primeros 4 dígitos de Agency_Id/Representative_Id).
# - dm_prefix: texto que antecede al número en el código de DM de esa sucursal en
#   Challenger_uat.AgencyStructure.Dm (cada sucursal respeta su propio formato
#   histórico, ej. Tijuana usa "BRM" en vez de "DM").
# - am_match: texto usado para filtrar (LIKE %am_match%) los AM existentes de esa
#   sucursal en AgencyStructure.Am al calcular el siguiente número de AM.
# - ubicacion: texto usado como "Branch" (ubicación) en P_ESTRELLAS_MENSUAL_CATEGORIAS.

SUCURSALES = [
    {
        "nombre": "Izcalli",
        "branch": 2075,
        "dm_prefix": "IzcalliDM",
        "am_match": "Izcalli",
        "ubicacion": "Cuautitlán Izcalli",
    },
    {
        "nombre": "Zacatecas",
        "branch": 2060,
        "dm_prefix": "ZacatecasDM",
        "am_match": "Zacatecas",
        "ubicacion": "Zacatecas",
    },
    {
        "nombre": "Aguascalientes",
        "branch": 2025,
        "dm_prefix": "Aguascalientes1DM",
        "am_match": "Aguascalientes",
        "ubicacion": "Aguascalientes",
    },
    {
        "nombre": "San Luis Potosí",
        "branch": 2049,
        "dm_prefix": "SanLuis2DM",
        "am_match": "San Luis",
        "ubicacion": "San Luis Potosí",
    },
    {
        "nombre": "Tijuana",
        "branch": 2093,
        "dm_prefix": "TijuanaBRM",
        "am_match": "Tijuana",
        "ubicacion": "Tijuana",
    },
]


def get_sucursal_by_nombre(nombre: str) -> dict:
    for s in SUCURSALES:
        if s["nombre"] == nombre:
            return s
    raise ValueError(f"Sucursal desconocida: {nombre}")


def get_sucursal_by_branch(branch: int) -> dict:
    for s in SUCURSALES:
        if s["branch"] == branch:
            return s
    raise ValueError(f"Branch desconocido: {branch}")
