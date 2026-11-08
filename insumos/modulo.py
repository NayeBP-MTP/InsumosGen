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

    @staticmethod
    def _es_dry_run(dry_run: bool, *repositorios) -> bool:
        """
        `dry_run` del módulo y de sus repositorios deben coincidir: un módulo en dry_run con un
        repositorio real escribiría de verdad. Devuelve True si se debe simular.
        """
        reales = [r for r in repositorios if r.dry_run != dry_run]
        if reales:
            raise ValueError(
                f"dry_run={dry_run} pero {[type(r).__name__ for r in reales]} se construyó con "
                f"dry_run={not dry_run}: construye los repositorios con el mismo valor."
            )
        return dry_run
