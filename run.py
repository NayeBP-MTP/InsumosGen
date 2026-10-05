import json
import sqlite3
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


class RunController:
    """
    Permite abortar una ronda en curso desde la UI: guarda el subproceso pytest
    activo para poder matarlo, y una bandera que `_ejecutar_ronda` revisa entre
    fases para no arrancar la siguiente.
    """

    def __init__(self):
        self.cancel_event = threading.Event()
        self._process = None
        self._lock = threading.Lock()

    def set_process(self, proc) -> None:
        with self._lock:
            self._process = proc

    def abort(self) -> None:
        self.cancel_event.set()
        with self._lock:
            proc = self._process
        if proc and proc.poll() is None:
            try:
                proc.terminate()
            except Exception:
                pass


TEST_FILE_BY_TIPO_CLIENTE = {
    "CN": "tests/test_login.py",
    "CF": "tests/test_login_cf.py",
    "OF": "tests/test_oferta.py",
    "AGENCIA": "tests/test_agencia_structure.py",
}

RESULTS_FILE_BY_TIPO_CLIENTE = {
    "CN": Path("data/run_results.json"),
    "CF": Path("data/run_results_cf.json"),
    "OF": Path("data/run_results_of.json"),
    "AGENCIA": Path("data/run_results_agencia.json"),
}

# Orden de ejecución cuando la corrida combina tipos. AGENCIA es independiente de
# la venta (OF/CF/CN): un insumo elegido en la UI nunca combina AGENCIA con los demás.
ORDEN_TIPOS = ["OF", "CF", "CN", "AGENCIA"]

CONFIG_PATH = Path("data/run_config.json")
OFFER_IDS_DB_PATH = Path("data/generated_offer_ids.sqlite3")


def _resumen_error(error: str) -> str:
    """Primera línea útil del error (sin el stacktrace de chromedriver)."""
    primera = (error or "").strip().splitlines()[0] if error else ""
    primera = primera.replace("Message:", "").strip() or "Falló (ver logs / data/diagnostico_cf)"
    return primera[:90]


def _leer_resultados(tipo: str) -> list:
    path = RESULTS_FILE_BY_TIPO_CLIENTE[tipo]
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("detalle", [])
    except json.JSONDecodeError:
        return []


def _ids_ofertas_generadas() -> set:
    """idOferta emitidos hasta ahora por utils/offer_id_allocator.py."""
    if not OFFER_IDS_DB_PATH.exists():
        return set()
    with sqlite3.connect(OFFER_IDS_DB_PATH, timeout=30) as conn:
        try:
            return {row[0] for row in conn.execute("SELECT id_oferta FROM used_offer_ids")}
        except sqlite3.OperationalError:
            return set()


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
    controller: RunController = None,
) -> int:
    # Settings lee run_config.json al importarse (en cada subproceso pytest),
    # por lo que se reescribe con el tipo y los ciclos de la fase actual.
    fase_config = {**run_config, "tipo_cliente": tipo, "ciclos": ciclos}
    if tipo == "OF" and ofertas_cfg is not None:
        # Solo las ofertas aún pendientes (ver slots en main()), no la lista completa
        # original: así un reintento no vuelve a insertar las que ya tuvieron éxito.
        fase_config["ofertas"] = ofertas_cfg
    if tipo == "AGENCIA" and ofertas_cfg is not None:
        # Mismo patrón que OF: solo las agencias aún pendientes.
        fase_config["agencias"] = ofertas_cfg
    CONFIG_PATH.write_text(json.dumps(fase_config, indent=2, ensure_ascii=False), encoding="utf-8")

    # Evita leer resultados de una corrida anterior si esta no llega a escribirlos.
    RESULTS_FILE_BY_TIPO_CLIENTE[tipo].unlink(missing_ok=True)

    etiqueta = {
        "OF": "Inserción de oferta", "CF": "Venta CF", "CN": "Venta CN",
        "AGENCIA": "Alta de estructura de agencia",
    }[tipo]
    if tipo not in ("OF", "AGENCIA"):
        etiqueta += " sin seguro" if not run_config.get("con_seguro", True) else " con seguro"
    print(f"\n>>> Fase {tipo}: {ciclos} operación(es)")
    Progress.emit(f"{etiqueta}: {ciclos} operación(es)", "fase")
    proc = subprocess.Popen(
        [
            sys.executable, "-m", "pytest",
            TEST_FILE_BY_TIPO_CLIENTE[tipo],
            "--alluredir=allure-results",
            "-s", "-v"
        ],
        cwd=Path(__file__).parent
    )
    if controller:
        controller.set_process(proc)
    returncode = proc.wait()
    if controller:
        controller.set_process(None)
    return returncode


def _ejecutar_ronda(
    slots: dict, run_config: dict, huerfanas: list, ronda: int,
    controller: RunController = None,
) -> None:
    """Ejecuta solo las ventas pendientes de cada tipo y actualiza `slots`."""
    # Antes de generar ofertas nuevas, se limpian las de intentos fallidos.
    _borrar_ofertas_fallidas(huerfanas)

    for tipo in ORDEN_TIPOS:
        if controller and controller.cancel_event.is_set():
            Progress.emit("Ejecución abortada por el usuario.", "error")
            break

        pendientes = [s for s in slots.get(tipo, []) if s["estado"] != "exitosa"]
        if not pendientes:
            continue

        ids_antes = _ids_ofertas_generadas() if tipo == "CF" else set()
        if tipo in ("OF", "AGENCIA"):
            ofertas_cfg = [s["config"] for s in pendientes]
            _ejecutar_fase(tipo, len(pendientes), run_config, ofertas_cfg=ofertas_cfg, controller=controller)
        else:
            _ejecutar_fase(tipo, len(pendientes), run_config, controller=controller)
        detalle = _leer_resultados(tipo)

        if tipo == "CF":
            ids_exitosos = {d.get("idOferta") for d in detalle if d.get("estado") == "exitoso"}
            huerfanas.extend(sorted(_ids_ofertas_generadas() - ids_antes - ids_exitosos))

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
                    slot["config"]["agencia_label"] if tipo == "OF"
                    else slot["config"]["sucursal"] if tipo == "AGENCIA"
                    else run_config.get("agencia_label", "")
                ),
                "metodo": run_config.get("metodo_entrega", ""),
                "tipo": tipo,
                "seguro": (
                    ("Con seguro" if run_config.get("con_seguro", True) else "Sin seguro")
                    if tipo not in ("OF", "AGENCIA") else ""
                ),
                "ronda": ronda,
                "estado": slot["estado"],
                "detalle": slot["detalle"],
            })

        RunHistory.append(registros)


def main():
    while True:
        ui = SelectorUI()
        if not ui.run():
            print("Ejecución cancelada por el usuario.")
            sys.exit(0)

        if not CONFIG_PATH.exists():
            print("Error: no se generó run_config.json.")
            sys.exit(1)

        run_config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        ventas = run_config.get("ventas", {})
        ofertas_cfg = run_config.get("ofertas", [])
        agencias_cfg = run_config.get("agencias", [])
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
                slots[tipo] = [
                    {"estado": "pendiente", "intentos": 0, "detalle": "Sin ejecutar"}
                    for _ in range(ventas.get(tipo, 0))
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
            ProgressUI(
                run_config, ronda,
                lambda: _ejecutar_ronda(slots, run_config, huerfanas, ronda, controller=controller),
                slots=slots,
                controller=controller,
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
