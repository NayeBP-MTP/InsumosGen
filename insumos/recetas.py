"""Las seis recetas de creación de cliente, declaradas como datos (ver CREAR_CLIENTES.md, sección 3)."""
from dataclasses import dataclass, replace
from typing import Tuple

PAUSA_QA = "PAUSA_QA"


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
