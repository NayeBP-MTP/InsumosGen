"""Runner de recetas: ejecuta los módulos de una receta en orden sobre un ContextoVenta."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

from insumos.contexto import ContextoVenta, ErrorContexto
from insumos.deshacer import Deshacedor, ResultadoDeshacer
from insumos.log_operacion import LogOperacion
from insumos.modulo import Modulo
from insumos.pendientes import COMPLETADA, DESHECHA, EN_CURSO, ESPERANDO_QA, FALLIDA, PendientesStore
from insumos.recetas import PAUSA_QA, RECETAS, Receta


@dataclass
class ResultadoReceta:
    """
    `estado`: completada | esperando_qa | fallida (en dry_run siempre completada o fallida).
    `deshecho`: la falla ocurrió antes de la pausa o del último módulo y se deshizo sola.
    """
    receta: str
    operacion_id: str
    estado: str
    ejecutados: list = field(default_factory=list)  # módulos que corrieron en ESTA llamada
    error: Optional[str] = None
    modulo_fallido: Optional[str] = None
    deshecho: bool = False
    resumen_deshacer: Optional[ResultadoDeshacer] = None


def fabrica_por_defecto(dry_run: bool = False, originacion=None, cnfs=None, allocator=None) -> Callable[[str], Modulo]:
    """
    Construye los módulos con repositorios que comparten `dry_run` (los módulos lo exigen). `originacion`,
    `cnfs` y `allocator` se inyectan en pruebas; por defecto son los reales.
    """
    from insumos.modulos.actualizar_id_cliente import ActualizarIdCliente
    from insumos.modulos.agreement import Agreement
    from insumos.modulos.crear_id_cliente import CrearIdCliente
    from insumos.modulos.paso_22_dispersado import Paso22Dispersado
    from insumos.modulos.registro_cliente import RegistroCliente
    from insumos.modulos.renombrar_cliente import RenombrarCliente
    from services.cnfs_repository import CnfsRepository
    from services.originacion_repository import OriginacionRepository

    originacion = originacion or OriginacionRepository(dry_run=dry_run)
    cnfs = cnfs or CnfsRepository(dry_run=dry_run)
    modulos = {
        "RENOMBRAR_CLIENTE": lambda: RenombrarCliente(repo=originacion),
        "CREAR_ID_CLIENTE": lambda: CrearIdCliente(repo=originacion, repo_cnfs=cnfs, allocator=allocator),
        "ACTUALIZAR_ID_CLIENTE": lambda: ActualizarIdCliente(repo=originacion, repo_cnfs=cnfs),
        "AGREEMENT": lambda: Agreement(repo=cnfs),
        "REGISTRO_CLIENTE": lambda: RegistroCliente(repo=cnfs),
        "PASO_22_DISPERSADO": lambda: Paso22Dispersado(repo=originacion),
    }
    fabrica = lambda nombre: modulos[nombre]()  # noqa: E731
    fabrica.fuente = originacion  # lo usa el runner como fuente de datos del ContextoVenta
    fabrica.repositorios = (originacion, cnfs)  # en dry_run: sus `dry_run_log` son lo que se habría escrito
    return fabrica


class RunnerRecetas:
    """
    Ejecuta una receta módulo a módulo. Cada módulo anota en su log `modulo_iniciado` y
    `modulo_completado`; la receta siempre arranca en el primer paso no completado, así que volver a
    llamar a `ejecutar` retoma una operación a medias.

    `PAUSA_QA` es un estado persistido (`data/insumos_pendientes.json`), no un hilo bloqueado: la
    receta termina con `esperando_qa` guardando lo que QA necesita, y `continuar_tras_qa` la retoma
    desde el paso siguiente aunque se haya cerrado el programa. En `dry_run` no se persiste nada y la
    pausa se atraviesa para ver la receta completa.

    **Reanudar** (`reanudar`, o `ejecutar` otra vez) siempre es la primera opción ante una falla: los
    módulos son idempotentes. **Deshacer** (`deshacer`) revierte el log a demanda. Solo se deshace solo
    (`auto_deshacer`) si la falla ocurre antes de `PAUSA_QA` (o antes del último módulo en las recetas
    sin pausa); pasada la pausa, o en el último módulo, el estado parcial se conserva para reanudar.
    """

    def __init__(self, dry_run: bool = False, directorio_logs: Optional[Path] = None,
                 pendientes: Optional[PendientesStore] = None,
                 fabrica: Optional[Callable[[str], Modulo]] = None,
                 deshacedor: Optional[Deshacedor] = None, auto_deshacer: bool = True):
        self.dry_run = dry_run
        self.directorio_logs = directorio_logs
        self.pendientes = pendientes or PendientesStore()
        self.fabrica = fabrica or fabrica_por_defecto(dry_run)
        self.auto_deshacer = auto_deshacer
        self._deshacedor = deshacedor

    # --- API ---

    def ejecutar(self, receta: Receta, ctx: ContextoVenta) -> ResultadoReceta:
        """Ejecuta (o retoma) `receta` sobre la venta de `ctx`; `ctx` debe traer `numero_contrato`."""
        self._preparar(receta, ctx)
        return self._correr(receta, ctx)

    def continuar_tras_qa(self, operacion_id: str, fuente=None) -> ResultadoReceta:
        """QA confirmó: marca la pausa como cumplida y sigue con el resto de la receta."""
        entrada = self.pendientes.obtener(operacion_id)
        if entrada is None:
            raise ErrorContexto(f"No hay una operación pendiente con id {operacion_id}.")
        if entrada["estado"] != ESPERANDO_QA:
            raise ErrorContexto(f"La operación {operacion_id} no está esperando QA (estado: {entrada['estado']}).")
        receta = RECETAS[entrada["receta"]]
        ctx = ContextoVenta.desde_dict(entrada["contexto"], fuente or getattr(self.fabrica, "fuente", None))
        LogOperacion(operacion_id, self.directorio_logs).modulo_completado(PAUSA_QA)
        return self._correr(receta, ctx)

    def reanudar(self, operacion_id: str, fuente=None) -> ResultadoReceta:
        """Retoma una operación a medias (en curso o fallida) desde el primer módulo no completado."""
        entrada = self.pendientes.obtener(operacion_id)
        if entrada is None:
            raise ErrorContexto(f"No hay una operación con id {operacion_id}.")
        if entrada["estado"] == DESHECHA:
            raise ErrorContexto(
                f"La operación {operacion_id} se deshizo; vuelve a ejecutar la receta desde el principio."
            )
        ctx = ContextoVenta.desde_dict(entrada["contexto"], fuente or getattr(self.fabrica, "fuente", None))
        return self._correr(RECETAS[entrada["receta"]], ctx)

    def deshacer(self, operacion_id: str) -> ResultadoDeshacer:
        """Revierte lo que escribió la operación (log en orden inverso) y la marca como deshecha."""
        resultado = self._deshacedor_activo().deshacer(LogOperacion(operacion_id, self.directorio_logs))
        if not self.dry_run:
            self.pendientes.guardar(operacion_id, estado=DESHECHA, paso_actual=None)
        return resultado

    # --- internos ---

    def _deshacedor_activo(self) -> Deshacedor:
        if self._deshacedor is None:
            originacion, cnfs = self.fabrica.repositorios
            self._deshacedor = Deshacedor(originacion, cnfs, dry_run=self.dry_run)
        return self._deshacedor

    @staticmethod
    def _falla_deshacible(receta: Receta, indice: int) -> bool:
        """Falla antes de PAUSA_QA (o antes del último módulo si no hay pausa): no deja datos huérfanos."""
        umbral = receta.pasos.index(PAUSA_QA) if receta.tiene_pausa_qa else len(receta.pasos) - 1
        return indice < umbral

    def _preparar(self, receta: Receta, ctx: ContextoVenta) -> None:
        if not ctx.numero_contrato:
            raise ErrorContexto("La receta necesita numero_contrato en el contexto para identificar la operación.")
        if ctx.tipo != receta.tipo_venta:
            raise ErrorContexto(
                f"La receta '{receta.nombre}' es para ventas {receta.tipo_venta} y el contexto es {ctx.tipo}."
            )
        if ctx.fuente is None:
            ctx.fuente = getattr(self.fabrica, "fuente", None)

    def _correr(self, receta: Receta, ctx: ContextoVenta) -> ResultadoReceta:
        operacion = str(ctx.numero_contrato)
        resultado = ResultadoReceta(receta.id, operacion, COMPLETADA)
        log = LogOperacion(operacion, self.directorio_logs)
        hechos = set() if self.dry_run else set(log.modulos_completados())

        for indice, paso in enumerate(receta.pasos):
            if paso in hechos:
                continue
            if paso == PAUSA_QA:
                if self.dry_run:
                    print("(PAUSA_QA) QA confirmaría aquí; en dry_run se continúa.")
                    continue
                return self._pausar(receta, ctx, resultado)

            self._guardar(operacion, receta, ctx, EN_CURSO, paso_actual=paso)
            try:
                if not self.dry_run:
                    log.modulo_iniciado(paso)
                self.fabrica(paso).ejecutar(ctx, log, dry_run=self.dry_run)
                if not self.dry_run:
                    log.modulo_completado(paso)
            except Exception as exc:
                resultado.estado, resultado.error, resultado.modulo_fallido = FALLIDA, str(exc), paso
                if self.auto_deshacer and not self.dry_run and self._falla_deshacible(receta, indice):
                    resultado.resumen_deshacer = self._deshacedor_activo().deshacer(log)
                    resultado.deshecho = True
                    self._guardar(operacion, receta, ctx, DESHECHA, paso_actual=paso, error=str(exc))
                else:
                    self._guardar(operacion, receta, ctx, FALLIDA, paso_actual=paso, error=str(exc))
                return resultado
            resultado.ejecutados.append(paso)

        self._guardar(operacion, receta, ctx, COMPLETADA, paso_actual=None, error=None)
        return resultado

    def _pausar(self, receta: Receta, ctx: ContextoVenta, resultado: ResultadoReceta) -> ResultadoReceta:
        ctx.cargar_expediente()  # lo que QA necesita para registrar al usuario
        self._guardar(
            resultado.operacion_id, receta, ctx, ESPERANDO_QA, paso_actual=PAUSA_QA, error=None,
            para_qa={
                "numero_contrato": ctx.numero_contrato,
                "fecha_nacimiento": ctx.fecha_nacimiento.date().isoformat() if ctx.fecha_nacimiento else None,
                "nombre_cliente": ctx.nombre_cliente,
            },
        )
        resultado.estado = ESPERANDO_QA
        return resultado

    def _guardar(self, operacion: str, receta: Receta, ctx: ContextoVenta, estado: str, **extra) -> None:
        if self.dry_run:
            return
        self.pendientes.guardar(operacion, receta=receta.id, estado=estado, contexto=ctx.a_dict(), **extra)
