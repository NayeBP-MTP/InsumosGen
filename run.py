import concurrent.futures
import json
import os
import subprocess
import sys
import threading
from datetime import datetime
from pathlib import Path

from ui.progress_ui import ProgressUI
from ui.results_ui import ResultsUI
from ui.selector_ui import SelectorUI
from utils.progress import Progress
from utils.run_history import RunHistory


def _matar_arbol_proceso(pid: int) -> None:
    """Mata un proceso y todo su árbol (pytest → chromedriver → Chrome). En
    Windows, Popen.terminate()/.kill() solo matan el proceso de pytest con
    TerminateProcess — eso no corre la limpieza de conftest.py (atexit/señales
    no se disparan con una terminación forzosa), así que chromedriver y Chrome
    quedaban abiertos al Abortar. `taskkill /T` sí mata todo el árbol."""
    if not pid:
        return
    try:
        if sys.platform == "win32":
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(pid)],
                capture_output=True, timeout=30,
            )
        else:
            import signal
            os.kill(pid, signal.SIGKILL)
    except Exception:
        pass


class RunController:
    """
    Permite abortar una ronda en curso desde la UI: guarda los subprocesos pytest
    activos para poder matarlos, y una bandera que las fases revisan para no
    arrancar más trabajo. Con ventas CF/CN en paralelo puede haber varios
    subprocesos vivos a la vez, por eso se trackean en un set (no un solo proc).
    """

    def __init__(self):
        self.cancel_event = threading.Event()
        self._procesos = set()
        self._lock = threading.Lock()

    def add_process(self, proc) -> None:
        with self._lock:
            self._procesos.add(proc)

    def remove_process(self, proc) -> None:
        with self._lock:
            self._procesos.discard(proc)

    def abort(self) -> None:
        self.cancel_event.set()
        with self._lock:
            procesos = list(self._procesos)
        for proc in procesos:
            if proc.poll() is None:
                _matar_arbol_proceso(proc.pid)


# Tope de LOTES (agencias) corriendo en paralelo — no de ventas individuales:
# dentro de un mismo lote, las ventas siempre van secuenciales en una sola
# sesión/login (ver _ejecutar_lote_venta), porque el portal no acepta dos
# sesiones simultáneas con la misma cuenta. Cada lote abre su propio Chrome con
# facematch/OTP. Empezar conservador: subirlo sin medir estabilidad de UAT/
# Legalario y de la máquina local puede generar fallos que no se ven con 1 a la vez.
MAX_WORKERS_VENTAS = 4


TEST_FILE_BY_TIPO_CLIENTE = {
    "CN": "tests/test_login.py",
    "CF": "tests/test_login_cf.py",
    "OF": "tests/test_oferta.py",
    "AGENCIA": "tests/test_agencia_structure.py",
}

# Orden de ejecución cuando la corrida combina tipos. AGENCIA es independiente de
# la venta (OF/CF/CN): un insumo elegido en la UI nunca combina AGENCIA con los demás.
ORDEN_TIPOS = ["OF", "CF", "CN", "AGENCIA"]

# Identifica a ESTE proceso de run.py frente a otros que puedan estar corriendo
# al mismo tiempo (otra ventana de `python run.py`). Se usa para que el config,
# los resultados de OF/AGENCIA y el canal de progreso de cada ventana vivan en
# archivos propios — antes todos compartían una sola ruta fija y una ventana
# podía pisarle el config/progreso a la otra. Los lotes de venta CF/CN ya tenían
# su propio aislamiento por lote (`run_id`); esto cubre lo que faltaba.
PROCESO_ID = str(os.getpid())

CONFIG_PATH = Path(f"data/run_config_{PROCESO_ID}.json")


def _config_path(run_id: str = None) -> Path:
    """Ruta de config para esta fase. Con `run_id` (un lote de venta CF/CN con su
    propia agencia), cada uno escribe/lee su propio archivo en vez de pisar el
    config.json global — así varios lotes del mismo tipo (ej. dos lotes CN) no se
    pisan entre sí, incluso si en el futuro se lanzan concurrentemente."""
    return Path(f"data/run_config_{run_id}.json") if run_id else CONFIG_PATH


def _results_path(tipo: str, run_id: str = None) -> Path:
    """Resultados de esta fase. Sin `run_id` (OF/AGENCIA), se usa PROCESO_ID como
    sufijo — antes era una ruta fija compartida por tipo, y dos ventanas de
    run.py haciendo OF/AGENCIA a la vez podían leer el resultado de la otra."""
    return Path(f"data/run_results_{tipo.lower()}_{run_id or PROCESO_ID}.json")


def _resumen_error(error: str) -> str:
    """Primera línea útil del error (sin el stacktrace de chromedriver)."""
    primera = (error or "").strip().splitlines()[0] if error else ""
    primera = primera.replace("Message:", "").strip() or "Falló (ver logs / data/diagnostico_cf)"
    return primera[:90]


def _leer_resultados(tipo: str, run_id: str = None) -> list:
    path = _results_path(tipo, run_id)
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("detalle", [])
    except json.JSONDecodeError:
        return []


def _borrar_ofertas_fallidas(huerfanas: list) -> None:
    """Borra de botDB las ofertas CF de intentos que no terminaron en venta."""
    if not huerfanas:
        return
    from services.offer_repository import OfferRepository

    repo = OfferRepository()
    for id_oferta in list(huerfanas):
        try:
            repo.delete_offer(id_oferta)
            print(f"Oferta fallida {id_oferta} eliminada de botDB")
            Progress.emit(f"Oferta fallida {id_oferta} eliminada de botDB", "info")
            huerfanas.remove(id_oferta)
        except Exception as exc:
            print(f"No se pudo eliminar la oferta {id_oferta}: {exc}")
            Progress.emit(f"No se pudo eliminar la oferta {id_oferta}: {exc}", "error")


def _ejecutar_fase(
    tipo: str, ciclos: int, run_config: dict, ofertas_cfg: list = None,
    controller: RunController = None, run_id: str = None,
) -> int:
    # Settings lee su config al importarse (en cada subproceso pytest). Con
    # `run_id` (un lote de venta CF/CN con su propia agencia), se escribe en un
    # archivo propio de ese lote y se le indica al subproceso vía variable de
    # entorno — así no pisa el config de otro lote del mismo tipo.
    fase_config = {**run_config, "tipo_cliente": tipo, "ciclos": ciclos}
    if tipo == "OF" and ofertas_cfg is not None:
        # Solo las ofertas aún pendientes (ver slots en main()), no la lista completa
        # original: así un reintento no vuelve a insertar las que ya tuvieron éxito.
        fase_config["ofertas"] = ofertas_cfg
    if tipo == "AGENCIA" and ofertas_cfg is not None:
        # Mismo patrón que OF: solo las agencias aún pendientes.
        fase_config["agencias"] = ofertas_cfg

    config_path = _config_path(run_id)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(fase_config, indent=2, ensure_ascii=False), encoding="utf-8")

    # Evita leer resultados de una corrida anterior si esta no llega a escribirlos.
    results_path = _results_path(tipo, run_id)
    results_path.unlink(missing_ok=True)

    etiqueta = {
        "OF": "Inserción de oferta", "CF": "Venta CF", "CN": "Venta CN",
        "AGENCIA": "Alta de estructura de agencia",
    }[tipo]
    if tipo not in ("OF", "AGENCIA"):
        etiqueta += " sin seguro" if not run_config.get("con_seguro", True) else " con seguro"
        if run_config.get("agencia_label"):
            etiqueta += f" — {run_config['agencia_label']}"
    print(f"\n>>> Fase {tipo}: {ciclos} operación(es)")
    Progress.emit(f"{etiqueta}: {ciclos} operación(es)", "fase")

    env = os.environ.copy()
    env["PROVIDIGITAL_RUN_CONFIG_PATH"] = str(config_path)
    # Crítico cuando run_id está aislado (lotes/ventas en paralelo): si no se fija
    # esta variable, el subproceso escribe su resultado en la ruta fija de
    # siempre (data/run_results[_cf].json) y run.py nunca lo encuentra en la ruta
    # aislada que espera — reporta "Falló" aunque la venta sí haya terminado bien.
    env["PROVIDIGITAL_RUN_RESULTS_PATH"] = str(results_path)
    if run_id:
        # Etiqueta legible para la ventana de progreso (ver ui/progress_ui.py):
        # distingue de qué lote/agencia viene cada paso cuando varios corren a
        # la vez en paralelo.
        env["PROVIDIGITAL_RUN_TAG"] = f"{tipo} · {run_config.get('agencia_label', run_id)}"
    proc = subprocess.Popen(
        [
            sys.executable, "-m", "pytest",
            TEST_FILE_BY_TIPO_CLIENTE[tipo],
            "--alluredir=allure-results",
            "-s", "-v"
        ],
        cwd=Path(__file__).parent,
        env=env,
    )
    if controller:
        controller.add_process(proc)
    try:
        returncode = proc.wait()
    finally:
        if controller:
            controller.remove_process(proc)
    return returncode


def _agrupar_por_lote(tareas: list) -> list:
    """Agrupa (tipo, slot) por `batch_id`, preservando el orden de aparición de
    cada lote. Cada grupo = una sola agencia/cuenta → debe correr en UNA sola
    sesión del portal (ver _ejecutar_lote_venta)."""
    grupos = {}
    orden = []
    for tipo, slot in tareas:
        bid = (tipo, slot["batch_id"])
        if bid not in grupos:
            grupos[bid] = []
            orden.append(bid)
        grupos[bid].append(slot)
    return [(bid[0], grupos[bid]) for bid in orden]


def _ejecutar_lote_venta(tipo: str, grupo: list, run_config: dict, controller: RunController = None) -> list:
    """Ejecuta TODAS las ventas pendientes de UN lote (una sola agencia/cuenta)
    en una sola invocación de pytest — un solo login, ciclos secuenciales dentro
    de esa sesión, como siempre hizo test_login.py/test_login_cf.py.

    Esto NO es opcional: el portal no acepta dos sesiones simultáneas con el
    mismo usuario/contraseña (confirmado en UAT — "Usuario o contraseña
    incorrectos" al intentar 4 logins a la vez con la misma cuenta). El
    paralelismo real es ENTRE lotes (agencias distintas), nunca dentro de uno.
    """
    batch_cfg = grupo[0]["config"]
    run_id = f"{tipo.lower()}_{grupo[0]['batch_id']}"
    fase_config = {**run_config, **batch_cfg}
    _ejecutar_fase(tipo, len(grupo), fase_config, controller=controller, run_id=run_id)
    return _leer_resultados(tipo, run_id)


def _ejecutar_ventas_en_paralelo(
    tareas: list, slots: dict, run_config: dict, huerfanas: list, ronda: int,
    controller: RunController = None, max_workers: int = MAX_WORKERS_VENTAS,
) -> None:
    """Corre los lotes de venta pendientes (CF y CN, de cualquier agencia) en un
    pool de hasta `max_workers` procesos pytest simultáneos — un proceso por
    lote (una sola sesión/login por agencia), nunca uno por venta individual.
    No espera a que termine un lote para iniciar el siguiente."""
    total = sum(len(slots.get(t, [])) for t in ("CF", "CN"))
    registros = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
        futuros = {}
        for tipo, grupo in _agrupar_por_lote(tareas):
            if controller and controller.cancel_event.is_set():
                break
            futuro = pool.submit(_ejecutar_lote_venta, tipo, grupo, run_config, controller)
            futuros[futuro] = (tipo, grupo)

        for futuro in concurrent.futures.as_completed(futuros):
            tipo, grupo = futuros[futuro]
            batch_cfg = grupo[0]["config"]
            try:
                detalle = futuro.result()
            except Exception as exc:
                detalle = []
                error_lote = str(exc)
            else:
                error_lote = None

            for i, slot in enumerate(grupo):
                slot["intentos"] += 1
                res = detalle[i] if i < len(detalle) else None
                if res and res.get("estado") == "exitoso":
                    slot["estado"] = "exitosa"
                    partes = [res.get("nombreCliente"), f"folio {res['folio']}" if res.get("folio") else None]
                    slot["detalle"] = " · ".join(p for p in partes if p) or "Venta finalizada"
                else:
                    slot["detalle"] = _resumen_error((res.get("error") if res else None) or error_lote or "")
                    # El propio resultado trae el idOferta aunque haya fallado
                    # (ver tests/test_login_cf.py) — así se sabe qué oferta CF
                    # quedó huérfana en botDB sin tocar la tabla global de IDs.
                    if tipo == "CF" and res and res.get("idOferta"):
                        huerfanas.append(res["idOferta"])

                registros.append({
                    "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "agencia": batch_cfg.get("agencia_label", ""),
                    "metodo": batch_cfg.get("metodo_entrega", ""),
                    "tipo": tipo,
                    "seguro": "Con seguro" if batch_cfg.get("con_seguro", True) else "Sin seguro",
                    "ronda": ronda,
                    "estado": slot["estado"],
                    "detalle": slot["detalle"],
                })

            # "Dashboard" del log en consola: la ventana de Tkinter mostraba estos
            # contadores en vivo (Total/Exitosas/Fallidas); el log en consola
            # también los imprime, cada vez que un lote termina. Con auto-retry,
            # lo que no es "exitosa" puede volver a intentarse en la próxima
            # ronda, así que se cuenta junto como "pendiente(s)/fallida(s)".
            exitosas = sum(1 for t in ("CF", "CN") for s in slots.get(t, []) if s["estado"] == "exitosa")
            Progress.emit(
                f"Resumen: {exitosas}/{total} exitosas · {total - exitosas} pendiente(s)/fallida(s)",
                "fase",
            )

    RunHistory.append(registros)


def _ejecutar_ronda(
    slots: dict, run_config: dict, huerfanas: list, ronda: int,
    controller: RunController = None,
) -> None:
    """Ejecuta solo las ventas pendientes de cada tipo y actualiza `slots`."""
    # Antes de generar ofertas nuevas, se limpian las de intentos fallidos.
    _borrar_ofertas_fallidas(huerfanas)

    for tipo in ("OF", "AGENCIA"):
        if controller and controller.cancel_event.is_set():
            Progress.emit("Ejecución abortada por el usuario.", "error")
            return

        pendientes = [s for s in slots.get(tipo, []) if s["estado"] != "exitosa"]
        if not pendientes:
            continue

        ofertas_cfg = [s["config"] for s in pendientes]
        _ejecutar_fase(tipo, len(pendientes), run_config, ofertas_cfg=ofertas_cfg, controller=controller)
        detalle = _leer_resultados(tipo)

        registros = []
        for i, slot in enumerate(pendientes):
            slot["intentos"] += 1
            res = detalle[i] if i < len(detalle) else None
            if res and res.get("estado") == "exitoso":
                slot["estado"] = "exitosa"
                partes = [
                    f"oferta {res['idOferta']}" if tipo == "OF" and res.get("idOferta") else None,
                    res.get("nombreCliente"),
                    f"monto {res['montoOferta']}" if tipo == "OF" and res.get("montoOferta") else None,
                    f"semana {res['semana']}" if tipo == "OF" and res.get("semana") else None,
                    f"folio {res['folio']}" if res.get("folio") else None,
                    f"Agency_Id {res['agency_id']}" if tipo == "AGENCIA" and res.get("agency_id") else None,
                    res.get("star_name") if tipo == "AGENCIA" else None,
                    f"DM {res['dm_code']}" if tipo == "AGENCIA" and res.get("dm_code") else None,
                    f"AM {res['am_text']}" if tipo == "AGENCIA" and res.get("am_text") else None,
                ]
                slot["detalle"] = " · ".join(p for p in partes if p) or {
                    "OF": "Oferta insertada", "AGENCIA": "Agencia creada",
                }.get(tipo, "Venta finalizada")
            else:
                slot["detalle"] = _resumen_error(res.get("error") if res else "")

            registros.append({
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "agencia": (
                    slot["config"]["agencia_label"] if tipo == "OF" else slot["config"]["sucursal"]
                ),
                "metodo": "",
                "tipo": tipo,
                "seguro": "",
                "ronda": ronda,
                "estado": slot["estado"],
                "detalle": slot["detalle"],
            })

        RunHistory.append(registros)

    # CF/CN se procesan juntos: todas las ventas pendientes (de cualquier lote o
    # agencia) son tareas independientes de un mismo pool de workers — no se
    # espera a que termine una para lanzar la siguiente (ver MAX_WORKERS_VENTAS).
    if not (controller and controller.cancel_event.is_set()):
        tareas = [
            (tipo, slot)
            for tipo in ("CF", "CN")
            for slot in slots.get(tipo, [])
            if slot["estado"] != "exitosa"
        ]
        if tareas:
            _ejecutar_ventas_en_paralelo(tareas, slots, run_config, huerfanas, ronda, controller=controller)


def main():
    # Propio para este proceso (ver PROCESO_ID): dos ventanas de `python run.py`
    # corriendo a la vez ya no comparten ni se truncan el canal de progreso.
    Progress.set_path(f"data/run_progress_{PROCESO_ID}.jsonl")

    while True:
        ui = SelectorUI(config_path=CONFIG_PATH)
        if not ui.run():
            print("Ejecución cancelada por el usuario.")
            sys.exit(0)

        if not CONFIG_PATH.exists():
            print("Error: no se generó run_config.json.")
            sys.exit(1)

        run_config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        ofertas_cfg = run_config.get("ofertas", [])
        agencias_cfg = run_config.get("agencias", [])
        ventas_batches = run_config.get("ventas_batches", [])
        slots = {}
        for tipo in ORDEN_TIPOS:
            if tipo in ("OF", "AGENCIA"):
                # Cada slot lleva su propia config (agencia/tipo/nivel, o sucursal/modo
                # para AGENCIA) para que un reintento solo reprocese lo que falló, con
                # sus mismos datos.
                cfgs = ofertas_cfg if tipo == "OF" else agencias_cfg
                slots[tipo] = [
                    {"estado": "pendiente", "intentos": 0, "detalle": "Sin ejecutar", "config": cfg}
                    for cfg in cfgs
                ]
            else:
                # CF/CN: un lote por agencia/método/seguro (ver panel "Venta" de la UI).
                # Cada slot lleva la config de SU lote y un `batch_id` para que
                # _ejecutar_ronda agrupe y lance una invocación de pytest por lote.
                slots[tipo] = [
                    {
                        "estado": "pendiente", "intentos": 0, "detalle": "Sin ejecutar",
                        "config": {k: v for k, v in batch.items() if k not in ("id", "cantidad")},
                        "batch_id": batch["id"],
                    }
                    for batch in ventas_batches if batch["tipo_cliente"] == tipo
                    for _ in range(batch["cantidad"])
                ]

        if not any(slots.values()):
            print("Error: no hay ventas configuradas.")
            sys.exit(1)

        ronda = 0
        huerfanas = []  # idOferta CF de intentos fallidos, pendientes de borrar
        while True:
            ronda += 1
            Progress.reset()
            controller = RunController()
            worker = lambda: _ejecutar_ronda(slots, run_config, huerfanas, ronda, controller=controller)
            ProgressUI(
                run_config, ronda, worker, slots=slots, controller=controller,
            ).run()

            # Restaura la selección original del usuario (las fases la sobrescriben).
            CONFIG_PATH.write_text(
                json.dumps(run_config, indent=2, ensure_ascii=False), encoding="utf-8"
            )

            accion = ResultsUI(run_config, slots, ronda).run()
            if accion != "retry":
                break

        if accion == "close":
            todas_ok = all(s["estado"] == "exitosa" for v in slots.values() for s in v)
            sys.exit(0 if todas_ok else 1)
        # accion == "new": vuelve al menú de inicio


if __name__ == "__main__":
    main()
