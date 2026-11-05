import json
import os
from pathlib import Path


def _load_run_config() -> dict:
    config_path = Path("data/run_config.json")
    if config_path.exists():
        return json.loads(config_path.read_text(encoding="utf-8"))
    return {}


_run_config = _load_run_config()


class Settings:
    BASE_URL = "https://originacion-uat.providigital.com/v1/app/login"

    # Credenciales: se sobreescriben desde run_config.json si existe
    ESTRELLA = _run_config.get("focus_id", "2075000343335")
    PASSWORD  = _run_config.get("password",  "Estrella1*")
    CELULAR   = _run_config.get("celular",   "5513096751")
    CORREO    = _run_config.get("correo",    "luis.andrade@mtpinternational.mx")

    # Selección de la UI
    TIPO_CLIENTE    = _run_config.get("tipo_cliente",   "CN")
    AGENCIA_LABEL   = _run_config.get("agencia_label",  "Izcalli 335")
    METODO_ENTREGA  = _run_config.get("metodo_entrega", "BBVA")
    CICLOS          = _run_config.get("ciclos",          1)
    CON_SEGURO      = _run_config.get("con_seguro",      True)

    # Si es False, take_step_screenshot (utils/allure_utils.py) no guarda ni adjunta
    # capturas del paso a paso, para correr más rápido cuando no se necesitan.
    TOMAR_CAPTURAS  = _run_config.get("tomar_capturas",  True)

    # Lista de ofertas a insertar en el flujo OF (panel "Oferta" de la UI), cada una con
    # su propia agencia/tipo/nivel: [{"agencia_label": ..., "tipo_oferta": "AGREGAR"|"REFIN",
    # "nivel_precio": ""|"N1"|"N2"|"N3"|"PP20"|"PP25"}, ...]. Permite combinar, en una
    # misma corrida, ofertas con agencia/tipo/nivel distintos (ver tests/test_oferta.py).
    OFERTAS         = _run_config.get("ofertas", [])

    # Lista de agencias a crear en el flujo "Nueva estructura de agencia" (panel
    # "Agencia" de la UI), cada una con: {"sucursal": "Izcalli", "modo": "nuevo"|"reusar",
    # "combo": {...} si modo == "reusar"}. Ver tests/test_agencia_structure.py y
    # config/Context/NUEVA_ESTRUCTURA_AGENCIA.md.
    AGENCIAS        = _run_config.get("agencias", [])

    # Monto de la oferta CF (opcional). Si no se define, se elige uno aleatorio.
    MONTO_OFERTA    = _run_config.get("monto")

    # Tipo de oferta elegido en el menú (panel "Oferta"): "AGREGAR" o "REFIN".
    # Determina el texto de descOferta (ver utils/mexican_names.py / test_login_cf.py).
    TIPO_OFERTA     = _run_config.get("tipo_oferta", "AGREGAR")

    # Nivel de precio / promoción elegido en el menú (panel "Oferta"): "" (ninguno),
    # "N1"/"N2"/"N3" o "PP20"/"PP25". Son exclusivos entre sí (un solo valor) y se anexan
    # al final de descOferta. Regla completa: InsumosGen/negocio/onboarding_po.md sección 10.3.
    NIVEL_PRECIO    = _run_config.get("nivel_precio", "")

    # Regla de negocio: límite EXCLUSIVO de monto entregable en CF por agencia
    # (prefijo del label). En Tijuana el monto debe ser menor a 10,000 (10,000 no).
    MONTO_MAXIMO_CF_POR_AGENCIA = {"Tijuana": 10000}

    # Sucursales dentro de la estrategia Unbundling (prefijo del label de agencia),
    # vigente al 2026-08-26 según InsumosGen/negocio/onboarding_po.md sección 10.4.
    # Fuera de esta lista, ninguna oferta (CF o CN) debe llevar nivel N1/N2/N3.
    AGENCIAS_UNBUNDLING = [
        "Aguascalientes",
        "Zacatecas",
        "San Luis Potosí II",
        "Texcoco",
        "León II",
        "San Juan del Río",
        "Chihuahua",
    ]

    @staticmethod
    def agencia_es_unbundling(agencia_label: str) -> bool:
        return any(agencia_label.startswith(p) for p in Settings.AGENCIAS_UNBUNDLING)

    # Oficina postal Finabien: (estado, ciudad) por prefijo del label de agencia. Cada
    # valor puede ser un texto o una tupla de candidatos (se prueban en orden; se
    # ignoran acentos y mayúsculas). Agencias no listadas usan Puebla/Puebla.
    UBICACION_OFICINA_POSTAL_POR_AGENCIA = {
        "Tijuana":        ("Baja California", "Tijuana"),
        "Izcalli":        (("Estado de Mexico", "Mexico"), "Cuautitlan Izcalli"),
        "Zacatecas":      ("Zacatecas", "Zacatecas"),
        "Aguascalientes": ("Aguascalientes", "Aguascalientes"),
        "San Luis":       ("San Luis Potosi", "San Luis Potosi"),
    }

    @staticmethod
    def ubicacion_oficina_postal(agencia_label: str):
        """(estado, ciudad) donde buscar la oficina postal según la agencia."""
        for prefijo, ubicacion in Settings.UBICACION_OFICINA_POSTAL_POR_AGENCIA.items():
            if agencia_label.startswith(prefijo):
                return ubicacion
        return ("Puebla", "Puebla")

    LEGALARIO_FRONT_IMAGE_PATH = os.path.join("data", "ine_frente.jpeg")
    LEGALARIO_BACK_IMAGE_PATH = os.path.join("data", "ine_tras.jpeg")
    LEGALARIO_SELFIE_IMAGE_PATH = os.path.join("data", "selfie.jpeg")
    LEGALARIO_SELFIE_VIDEO_PATH = os.path.join("data", "selfie.y4m")
    COMPROBANTE_DOMICILIO_PATH = os.path.abspath(os.path.join("data", "comprobante.jpeg"))

    LEGALARIO_ONBOARDING_ID = "69e1305983beb98b360177f9"
    LEGALARIO_ORGANIZATION_ID = "6099a51598cfb21cf25ad42b"

    # Activar para ejecución desatendida de facematch.
    USE_FAKE_CAMERA = True

    # Elegible desde el panel "Venta" de la UI ("Ejecutar sin mostrar el
    # navegador"). Probado contra UAT: el facematch/OTP con cámara fake funciona
    # igual en headless — solo cambia que no se ve la ventana de Chrome.
    HEADLESS = _run_config.get("headless", False)
    IMPLICIT_WAIT = 10
