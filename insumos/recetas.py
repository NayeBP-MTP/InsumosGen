"""Las seis recetas de creación de cliente, declaradas como datos (ver CREAR_CLIENTES.md, sección 3)."""
from dataclasses import dataclass, replace
from typing import Tuple

PAUSA_QA = "PAUSA_QA"

# Todos los módulos de insumo que existen. Cada uno debe estar en al menos una receta y cada paso de
# una receta debe estar aquí (lo comprueba `validar_recetas`, que corre al importar este módulo).
MODULOS = (
    "RENOMBRAR_CLIENTE", "CREAR_ID_CLIENTE", "ACTUALIZAR_ID_CLIENTE", "AGREEMENT", "REGISTRO_CLIENTE",
    "PASO_22_DISPERSADO",
)
TIPOS_VENTA = ("CN", "CF")


@dataclass(frozen=True)
class Receta:
    """
    `tipo_venta` ("CN" | "CF") es la venta que antecede a la receta (VENTA_CN / VENTA_CF) y define
    `Customer_Status_Code` (AA / CC). `pasos` son los módulos de insumo, en orden; `PAUSA_QA` es un
    paso más: detiene la receta hasta que QA confirme.
    """
    id: str
    nombre: str
    tipo_venta: str
    pasos: Tuple[str, ...]

    @property
    def tiene_pausa_qa(self) -> bool:
        return PAUSA_QA in self.pasos

    def sin_pausa_qa(self) -> "Receta":
        """La misma receta sin la pausa (si QA no interviene)."""
        return replace(self, pasos=tuple(p for p in self.pasos if p != PAUSA_QA))


RECETAS = {r.id: r for r in (
    Receta("CN_REGISTRO_INTERMEDIO", "CN con registro intermedio", "CN", (
        "RENOMBRAR_CLIENTE", "AGREEMENT", PAUSA_QA, "CREAR_ID_CLIENTE", "ACTUALIZAR_ID_CLIENTE",
        "REGISTRO_CLIENTE")),
    Receta("CN_REGISTRADO", "CN registrado", "CN", (
        "RENOMBRAR_CLIENTE", "CREAR_ID_CLIENTE", "AGREEMENT", "REGISTRO_CLIENTE")),
    Receta("CN_REGISTRO_DISPERSADO", "CN con registro dispersado", "CN", (
        "RENOMBRAR_CLIENTE", "PASO_22_DISPERSADO", "AGREEMENT", PAUSA_QA, "CREAR_ID_CLIENTE",
        "ACTUALIZAR_ID_CLIENTE", "REGISTRO_CLIENTE")),
    Receta("CN_REGISTRADO_DISPERSION", "CN registrado con dispersión", "CN", (
        "RENOMBRAR_CLIENTE", "CREAR_ID_CLIENTE", "PASO_22_DISPERSADO", "AGREEMENT", "REGISTRO_CLIENTE")),
    Receta("CF_DISPERSADO", "CF dispersado", "CF", (
        "RENOMBRAR_CLIENTE", "PASO_22_DISPERSADO", "AGREEMENT", "REGISTRO_CLIENTE")),
    Receta("CF_REGISTRADO", "CF registrado", "CF", (
        "RENOMBRAR_CLIENTE", "AGREEMENT", "REGISTRO_CLIENTE")),
)}


def validar_recetas(recetas=None, modulos=MODULOS, tipos_venta=TIPOS_VENTA) -> list:
    """
    Comprueba que el catálogo de recetas es coherente y devuelve la lista de problemas (vacía si todo
    está bien):
    - cada módulo de insumo está en al menos una receta y cada tipo de venta tiene recetas;
    - cada paso existe, sin repetirse, y la pausa de QA aparece a lo sumo una vez;
    - el orden respeta las dependencias entre módulos: RENOMBRAR antes de REGISTRO (usa el nombre
      generado), ACTUALIZAR después de AGREEMENT y de CREAR_ID, y en CN REGISTRO después de CREAR_ID
      (el cliente nuevo no tiene número hasta entonces); si en CN AGREEMENT va antes de CREAR_ID, la
      receta debe llevar ACTUALIZAR para propagar el número al contrato;
    - en CF no se usa CREAR_ID ni ACTUALIZAR (el expediente ya trae su `Cliente`).
    """
    recetas = RECETAS if recetas is None else recetas
    problemas = []
    usados = set()
    for clave, r in recetas.items():
        def mal(msg, r=r):
            problemas.append(f"{r.id}: {msg}")
        if clave != r.id:
            mal(f"está registrada con la clave {clave!r}")
        if r.tipo_venta not in tipos_venta:
            mal(f"tipo de venta desconocido {r.tipo_venta!r}")
        pasos = [p for p in r.pasos if p != PAUSA_QA]
        usados.update(pasos)
        for p in pasos:
            if p not in modulos:
                mal(f"paso desconocido {p!r}")
        for p in sorted({p for p in r.pasos if r.pasos.count(p) > 1}):
            mal(f"el paso {p} aparece más de una vez")
        if not pasos:
            mal("no tiene módulos")

        def pos(nombre):
            return pasos.index(nombre) if nombre in pasos else None
        if pos("REGISTRO_CLIENTE") is not None:
            if pos("RENOMBRAR_CLIENTE") is None or pos("RENOMBRAR_CLIENTE") > pos("REGISTRO_CLIENTE"):
                mal("REGISTRO_CLIENTE necesita RENOMBRAR_CLIENTE antes (usa el nombre generado)")
        if pos("ACTUALIZAR_ID_CLIENTE") is not None:
            for antes in ("AGREEMENT", "CREAR_ID_CLIENTE"):
                if pos(antes) is None or pos(antes) > pos("ACTUALIZAR_ID_CLIENTE"):
                    mal(f"ACTUALIZAR_ID_CLIENTE necesita {antes} antes")
        if r.tipo_venta == "CN":
            if pos("REGISTRO_CLIENTE") is not None and (
                    pos("CREAR_ID_CLIENTE") is None or pos("CREAR_ID_CLIENTE") > pos("REGISTRO_CLIENTE")):
                mal("en CN, REGISTRO_CLIENTE necesita CREAR_ID_CLIENTE antes (el cliente nuevo no tiene número)")
            if (pos("AGREEMENT") is not None and pos("CREAR_ID_CLIENTE") is not None
                    and pos("AGREEMENT") < pos("CREAR_ID_CLIENTE") and pos("ACTUALIZAR_ID_CLIENTE") is None):
                mal("AGREEMENT corre antes de CREAR_ID_CLIENTE: falta ACTUALIZAR_ID_CLIENTE para propagar el número")
        if r.tipo_venta == "CF":
            for p in ("CREAR_ID_CLIENTE", "ACTUALIZAR_ID_CLIENTE"):
                if p in pasos:
                    mal(f"en CF no se usa {p} (el expediente ya trae Cliente)")
        if r.pasos.count(PAUSA_QA) > 1:
            mal("tiene más de una pausa de QA")

    for modulo in modulos:
        if modulo not in usados:
            problemas.append(f"{modulo}: es un módulo de insumo pero no está en ninguna receta")
    for tipo in tipos_venta:
        if not any(r.tipo_venta == tipo for r in recetas.values()):
            problemas.append(f"venta {tipo}: no tiene ninguna receta")
    return problemas


def validar_o_fallar(recetas=None) -> None:
    problemas = validar_recetas(recetas)
    if problemas:
        raise ValueError("El catálogo de recetas es inconsistente:\n  - " + "\n  - ".join(problemas))


validar_o_fallar()  # una receta mal armada se detecta al importar, no a mitad de una ejecución real
