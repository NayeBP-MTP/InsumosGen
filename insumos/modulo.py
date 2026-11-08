"""Interfaz común de los módulos de insumo."""
from abc import ABC, abstractmethod

from insumos.contexto import ContextoVenta
from insumos.log_operacion import LogOperacion


class Modulo(ABC):
    """
    Una etapa completa del proceso (no un solo INSERT/UPDATE). Contrato:
    - recibe el `ContextoVenta` y lo devuelve enriquecido para el siguiente módulo;
    - es idempotente: si el efecto ya existe en la BD, lo omite;
    - anota en `log` cada escritura (tabla, llave, valor anterior) antes de terminar;
    - con `dry_run` no escribe: deja lo que habría hecho en el log del repositorio.
    """

    nombre: str = ""

    @abstractmethod
    def ejecutar(self, ctx: ContextoVenta, log: LogOperacion, dry_run: bool = False) -> ContextoVenta:
        ...
