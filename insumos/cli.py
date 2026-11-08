"""
Línea de comandos de las recetas de insumo (sin la UI; pensada para QA):

    python -m insumos listar
    python -m insumos pendientes
    python -m insumos ejecutar CN_REGISTRADO --contrato 240021110 [--sin-seguro] [--dry-run]
    python -m insumos continuar 240021110      # QA confirmó: sigue después de PAUSA_QA
    python -m insumos reanudar 240021110       # retoma una operación fallida o a medias
    python -m insumos deshacer 240021110 [--dry-run]

Códigos de salida: 0 bien (incluida la pausa de QA), 1 la receta falló o deshacer encontró conflictos,
2 uso o datos inválidos.
"""
import argparse
import sys
from typing import Callable, Optional

from config.settings import Settings
from insumos.contexto import ContextoVenta, ErrorContexto
from insumos.pendientes import ESPERANDO_QA, PendientesStore
from insumos.recetas import PAUSA_QA, RECETAS
from insumos.runner import ResultadoReceta, RunnerRecetas

BIEN, FALLO, USO = 0, 1, 2


def construir_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="python -m insumos", description="Recetas de creación de cliente (insumos).")
    sub = p.add_subparsers(dest="comando", required=True)

    sub.add_parser("listar", help="Muestra las recetas disponibles y sus módulos.")
    sub.add_parser("pendientes", help="Muestra las operaciones en pausa de QA, en curso o fallidas.")

    e = sub.add_parser("ejecutar", help="Ejecuta una receta sobre una venta ya hecha.")
    e.add_argument("receta", choices=sorted(RECETAS), help="Id de la receta (ver `listar`).")
    e.add_argument("--contrato", required=True, help="numeroContrato de la venta (ExpedienteCliente.numeroContrato).")
    seguro = e.add_mutually_exclusive_group()
    seguro.add_argument("--con-seguro", dest="con_seguro", action="store_true", default=None)
    seguro.add_argument("--sin-seguro", dest="con_seguro", action="store_false",
                        help="Elige los montos con/sin seguro (por defecto, el de data/run_config.json).")
    e.add_argument("--sin-pausa-qa", action="store_true", help="Omite la pausa de QA de la receta.")
    e.add_argument("--colaborador", help="Número de colaborador (1-2 dígitos); por defecto el de run_config.json.")
    e.add_argument("--dry-run", action="store_true", help="No escribe nada: muestra lo que haría.")

    for nombre, ayuda in (("continuar", "QA confirmó: continúa la receta después de PAUSA_QA."),
                          ("reanudar", "Retoma una operación fallida o a medias desde el primer módulo pendiente.")):
        c = sub.add_parser(nombre, help=ayuda)
        c.add_argument("contrato")
        c.add_argument("--colaborador")

    d = sub.add_parser("deshacer", help="Revierte lo que escribió la operación (log en orden inverso).")
    d.add_argument("contrato")
    d.add_argument("--dry-run", action="store_true", help="Solo informa qué revertiría.")
    return p


def _mostrar_resultado(r: ResultadoReceta, salida: Callable[[str], None]) -> int:
    if r.estado == "completada":
        salida(f"Receta {r.receta} completada para el contrato {r.operacion_id}. "
               f"Módulos ejecutados ahora: {', '.join(r.ejecutados) or 'ninguno (ya estaba todo hecho)'}.")
        return BIEN
    if r.estado == ESPERANDO_QA:
        salida(f"Receta {r.receta}: en pausa de QA. Módulos ejecutados ahora: {', '.join(r.ejecutados) or 'ninguno'}.")
        salida(f"QA debe registrar al usuario con el contrato {r.operacion_id} y su fecha de nacimiento; "
               f"después ejecuta: python -m insumos continuar {r.operacion_id}")
        return BIEN
    salida(f"Receta {r.receta} FALLÓ en {r.modulo_fallido}: {r.error}")
    if r.deshecho:
        salida("Falló antes de la pausa de QA (o antes del último módulo): se deshizo sola y la BD quedó como estaba.")
    else:
        salida(f"Se conserva lo hecho. Opciones: python -m insumos reanudar {r.operacion_id}  |  "
               f"python -m insumos deshacer {r.operacion_id}")
    return FALLO


def _fijar_colaborador(args) -> None:
    if getattr(args, "colaborador", None):
        Settings.NUMERO_COLABORADOR = args.colaborador


def main(argv: Optional[list] = None, fabrica_runner: Optional[Callable[..., RunnerRecetas]] = None,
         pendientes: Optional[PendientesStore] = None, salida: Callable[[str], None] = print) -> int:
    """`fabrica_runner(dry_run=...)` y `pendientes` se inyectan en pruebas; por defecto, los reales."""
    args = construir_parser().parse_args(argv)
    fabrica_runner = fabrica_runner or (lambda dry_run=False: RunnerRecetas(dry_run=dry_run))
    try:
        return _ejecutar_comando(args, fabrica_runner, pendientes or PendientesStore(), salida)
    except (ErrorContexto, LookupError, ValueError) as exc:
        salida(f"Error: {exc}")
        return USO


def _ejecutar_comando(args, fabrica_runner, pendientes: PendientesStore, salida) -> int:
    if args.comando == "listar":
        for r in RECETAS.values():
            salida(f"{r.id}  ({r.tipo_venta})  {r.nombre}")
            salida("    " + " -> ".join(r.pasos))
        return BIEN

    if args.comando == "pendientes":
        entradas = pendientes.pendientes()
        if not entradas:
            salida("No hay operaciones pendientes.")
        for e in entradas:
            linea = f"{e['operacion_id']}  {e['receta']}  {e['estado']}"
            if e.get("paso_actual"):
                linea += f"  paso: {e['paso_actual']}"
            if e.get("error"):
                linea += f"  error: {e['error']}"
            salida(linea)
            if e["estado"] == ESPERANDO_QA:
                salida(f"    QA: contrato {e['para_qa']['numero_contrato']}, "
                       f"fecha de nacimiento {e['para_qa']['fecha_nacimiento']}")
        return BIEN

    _fijar_colaborador(args)

    if args.comando == "ejecutar":
        receta = RECETAS[args.receta]
        if args.sin_pausa_qa:
            receta = receta.sin_pausa_qa()
        con_seguro = Settings.CON_SEGURO if args.con_seguro is None else args.con_seguro
        salida(f"{'[dry-run] ' if args.dry_run else ''}Receta {receta.id} ({receta.nombre}) sobre el contrato "
               f"{args.contrato}, {'con' if con_seguro else 'sin'} seguro.")
        ctx = ContextoVenta(tipo=receta.tipo_venta, numero_contrato=args.contrato, con_seguro=con_seguro)
        return _mostrar_resultado(fabrica_runner(dry_run=args.dry_run).ejecutar(receta, ctx), salida)

    if args.comando == "continuar":
        return _mostrar_resultado(fabrica_runner().continuar_tras_qa(args.contrato), salida)

    if args.comando == "reanudar":
        return _mostrar_resultado(fabrica_runner().reanudar(args.contrato), salida)

    if args.comando == "deshacer":
        r = fabrica_runner(dry_run=args.dry_run).deshacer(args.contrato)
        prefijo = "[dry-run] revertiría" if args.dry_run else "Revertidas"
        salida(f"{prefijo} {len(r.deshechas)} escritura(s) del contrato {args.contrato}:")
        for d in r.deshechas:
            salida(f"    {d}")
        for descripcion, motivo in r.omitidas:
            salida(f"    omitida ({motivo}): {descripcion}")
        if not (r.deshechas or r.omitidas):
            salida("    Nada que deshacer: el log no tiene escrituras vigentes.")
        if r.conflictos:
            salida("Hay conflictos: la BD cambió después de que escribiera el módulo; no se pisó. Revísalos a mano.")
            return FALLO
        return BIEN

    raise ValueError(f"Comando desconocido: {args.comando}")  # pragma: no cover (argparse ya lo valida)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
