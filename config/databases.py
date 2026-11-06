"""
Mapeo base de datos -> host de SQL Server.

Hay 5 hosts y cada uno aloja varias bases (una base vive en un solo host). Las credenciales
se definen una vez por host en el `.env` (`<HOST>_SERVER`, `<HOST>_USER`, `<HOST>_PASSWORD`,
`<HOST>_DRIVER`); aquí es el único lugar donde se escribe el nombre de una base.
Diseño: config/Context/crearClientesFC/CREAR_CLIENTES.md (decisión 4).
"""

PESOS_OFFER = "PESOS_OFFER"
CNFS = "CNFS"
CHALLENGER = "CHALLENGER"
CUSTOMER_APP = "CUSTOMER_APP"
PAYMENTLINK = "PAYMENTLINK"

HOSTS = (PESOS_OFFER, CNFS, CHALLENGER, CUSTOMER_APP, PAYMENTLINK)

# Base -> host. Customer_App y PaymentLink no tienen bases registradas todavía.
DATABASE_HOSTS = {
    "botDB": PESOS_OFFER,
    "Originacion": PESOS_OFFER,
    "CNFS_uat": CNFS,
    "Challenger_uat": CHALLENGER,
}


def host_de(base: str) -> str:
    """Host que aloja `base`; ValueError (con las bases conocidas) si no está mapeada."""
    try:
        return DATABASE_HOSTS[base]
    except KeyError:
        conocidas = ", ".join(sorted(DATABASE_HOSTS))
        raise ValueError(
            f"Base de datos '{base}' sin host asignado en config/databases.py. "
            f"Bases conocidas: {conocidas}."
        ) from None
