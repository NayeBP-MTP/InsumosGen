import random
import unicodedata

NOMBRES_M = [
    "JOSÉ LUIS", "JUAN CARLOS", "MIGUEL ÁNGEL", "JESÚS", "FRANCISCO", "ALEJANDRO",
    "JORGE", "RICARDO", "ROBERTO", "FERNANDO", "EDUARDO", "ARTURO", "SERGIO",
    "MARIO", "RAÚL", "OSCAR", "HÉCTOR", "GERARDO", "ALFREDO", "RAFAEL",
]
NOMBRES_F = [
    "MARÍA GUADALUPE", "MARÍA DEL CARMEN", "ANA LAURA", "PATRICIA", "LETICIA",
    "ROSA MARÍA", "ADRIANA", "GABRIELA", "CLAUDIA", "VERÓNICA", "MARTHA",
    "SILVIA", "ELIZABETH", "ARACELI", "LORENA", "GLORIA", "MÓNICA", "YOLANDA",
]
APELLIDOS = [
    "HERNÁNDEZ", "GARCÍA", "MARTÍNEZ", "LÓPEZ", "GONZÁLEZ", "RODRÍGUEZ", "PÉREZ",
    "SÁNCHEZ", "RAMÍREZ", "CRUZ", "FLORES", "GÓMEZ", "MORALES", "VÁZQUEZ", "JIMÉNEZ",
    "REYES", "DÍAZ", "TORRES", "GUTIÉRREZ", "RUIZ", "MENDOZA", "AGUILAR", "ORTIZ",
    "CASTILLO", "MORENO", "ROMERO", "ÁLVAREZ", "MEDINA", "CHÁVEZ", "HERRERA",
]

_VOCALES = "AEIOU"


def _sin_acentos(texto: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn"
    )


def _primera_vocal_interna(apellido: str) -> str:
    for c in apellido[1:]:
        if c in _VOCALES:
            return c
    return "X"


class MexicanNames:
    """Genera nombres completos mexicanos realistas (ficticios) para ofertas CF."""

    @staticmethod
    def generar() -> dict:
        nombre = random.choice(random.choice([NOMBRES_M, NOMBRES_F]))
        ap_paterno, ap_materno = random.sample(APELLIDOS, 2)
        return {
            "nombre": nombre,
            "apellido_paterno": ap_paterno,
            "apellido_materno": ap_materno,
            "nombre_completo": f"{nombre} {ap_paterno} {ap_materno}",
        }

    @staticmethod
    def rfc(persona: dict, fecha_ddmmyyyy: str) -> str:
        """
        RFC de persona física con la forma real (4 letras + AAMMDD + 3 homoclave)
        derivado del nombre y la fecha de nacimiento. Es ficticio: la homoclave
        es aleatoria y no hay dígito verificador real.
        """
        dia, mes, anio = fecha_ddmmyyyy.split("/")
        paterno = _sin_acentos(persona["apellido_paterno"])
        materno = _sin_acentos(persona["apellido_materno"])
        nombre = _sin_acentos(persona["nombre"]).split()[0]
        letras = paterno[0] + _primera_vocal_interna(paterno) + materno[0] + nombre[0]
        homoclave = "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ0123456789", k=3))
        return f"{letras}{anio[2:]}{mes}{dia}{homoclave}"
