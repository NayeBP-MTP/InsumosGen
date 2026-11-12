import json
import allure

from pathlib import Path

from config.settings import Settings
from config.sucursales import get_sucursal_by_nombre
from services.agency_repository import (
    ChallengerRepository, BotDbAgencyRepository,
    DmInfo, AmInfo, generar_dm_nuevo, generar_am_nuevo, insertar_persona, crear_agencia,
)
from utils.progress import Progress
from utils.paths import app_data_dir


RUN_RESULTS_PATH = Path(Settings.RUN_RESULTS_PATH) if Settings.RUN_RESULTS_PATH else app_data_dir() / "run_results_agencia.json"


def _resolver_dm_am(cfg: dict, sucursal: dict, challenger: ChallengerRepository, botdb: BotDbAgencyRepository):
    """
    Cada fila/slot de agencia es independiente: si `modo` es "nuevo" crea su propio
    DM/AM (un equipo nuevo con una sola estrella); si es "reusar" usa el combo ya
    existente que el usuario eligió en la UI (ver ui/selector_ui.py).
    """
    if cfg["modo"] == "nuevo":
        dm_info, dm_persona = generar_dm_nuevo(sucursal, challenger)
        am_info, am_persona = generar_am_nuevo(sucursal, challenger)
        insertar_persona(dm_persona, sucursal["branch"], challenger, botdb)
        insertar_persona(am_persona, sucursal["branch"], challenger, botdb)
        return dm_info, am_info

    combo = cfg["combo"]
    dm_info = DmInfo(
        dm_code=combo["dm_code"], dm_id=combo["dm_id"],
        dm_name=combo["dm_name"], section=combo["section"],
    )
    am_info = AmInfo(am_text=combo["am_text"], am_id=combo["am_id"], am_name=combo["am_name"])
    return dm_info, am_info


@allure.epic("Provident")
@allure.feature("Estructura de agencias")
@allure.story("Alta de nueva estructura de agencia")
class TestCrearEstructuraAgencia:

    @allure.title("Alta de estructura(s) de agencia en Challenger_uat y botDB")
    def test_crear_agencias(self):
        agencias_config = Settings.AGENCIAS
        total = len(agencias_config)
        resultados = []
        challenger = ChallengerRepository()
        botdb = BotDbAgencyRepository()

        print(f"\n{'='*50}")
        print("Flujo      : Nueva estructura de agencia")
        print(f"Agencias   : {total}")
        print(f"{'='*50}\n")

        for ciclo, cfg in enumerate(agencias_config, start=1):
            sucursal = get_sucursal_by_nombre(cfg["sucursal"])
            with allure.step(
                f"Agencia {ciclo} de {total} — {cfg['sucursal']} / "
                f"{'DM/AM nuevo' if cfg['modo'] == 'nuevo' else 'DM/AM existente'}"
            ):
                try:
                    dm_info, am_info = _resolver_dm_am(cfg, sucursal, challenger, botdb)
                    resultado = crear_agencia(sucursal, dm_info, am_info, challenger, botdb)
                    resultados.append({
                        "ciclo": ciclo,
                        "estado": "exitoso",
                        "error": None,
                        "sucursal": cfg["sucursal"],
                        **resultado,
                    })
                    Progress.emit(
                        f"Agencia {ciclo}/{total} ({cfg['sucursal']}) creada — "
                        f"Agency_Id {resultado['agency_id']}, estrella {resultado['star_name']}, "
                        f"DM {resultado['dm_code']}, AM {resultado['am_text']}",
                        "ok",
                    )
                except Exception as exc:
                    import traceback
                    traceback.print_exc()
                    resultados.append({
                        "ciclo": ciclo, "estado": "fallido", "error": str(exc),
                        "sucursal": cfg["sucursal"],
                    })
                    Progress.emit(f"Agencia {ciclo}/{total} ({cfg['sucursal']}) FALLÓ: {exc}", "error")

        exitosos = sum(1 for r in resultados if r["estado"] == "exitoso")
        fallidos = total - exitosos

        RUN_RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
        RUN_RESULTS_PATH.write_text(
            json.dumps({
                "flujo": "AGENCIA",
                "total": total,
                "exitosos": exitosos,
                "fallidos": fallidos,
                "detalle": resultados,
            }, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        assert fallidos == 0, (
            f"{fallidos} de {total} estructura(s) de agencia fallaron. Revisa {RUN_RESULTS_PATH}."
        )
