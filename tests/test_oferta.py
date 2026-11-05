import json
import allure

from pathlib import Path

from config.settings import Settings
from services.offer_repository import OfferRepository
from utils.progress import Progress
from tests.test_login_cf import _insertar_oferta_cf


RUN_RESULTS_PATH = Path(Settings.RUN_RESULTS_PATH) if Settings.RUN_RESULTS_PATH else Path("data/run_results_of.json")


@allure.epic("Provident")
@allure.feature("Ofertas")
@allure.story("Inserción de oferta CF")
class TestInsertarOferta:

    @allure.title("Inserción de ofertas en botDB — sin venta")
    def test_insertar_ofertas(self):
        # Cada entrada trae su propia agencia/tipo/nivel (ver panel "Oferta" de la UI),
        # lo que permite combinar en una misma corrida ofertas distintas entre sí.
        ofertas_config = Settings.OFERTAS
        total = len(ofertas_config)
        resultados = []
        repo = OfferRepository()

        print(f"\n{'='*50}")
        print("Flujo      : Oferta (solo inserción en BD)")
        print(f"Ofertas    : {total}")
        print(f"{'='*50}\n")

        for ciclo, cfg in enumerate(ofertas_config, start=1):
            agencia_label = cfg["agencia_label"]
            with allure.step(
                f"Oferta {ciclo} de {total} — {agencia_label} / "
                f"{cfg['tipo_oferta']} / nivel {cfg['nivel_precio'] or 'ninguno'}"
            ):
                try:
                    oferta = _insertar_oferta_cf(
                        repo, ciclo,
                        agencia_label=agencia_label,
                        tipo_oferta_elegido=cfg["tipo_oferta"],
                        nivel_precio=cfg["nivel_precio"],
                    )
                    resultados.append({
                        "ciclo": ciclo,
                        "estado": "exitoso",
                        "error": None,
                        "idOferta": oferta.idOferta,
                        "nombreCliente": oferta.nombreCliente,
                        "folio": None,
                        "montoOferta": oferta.montoOferta,
                        "semana": oferta.semana,
                        "agenciaCliente": oferta.agenciaCliente,
                        "agenciaLabel": agencia_label,
                    })
                    Progress.emit(
                        f"Oferta {ciclo}/{total} ({agencia_label}) insertada y verificada "
                        f"en botDB — idOferta {oferta.idOferta}, {oferta.nombreCliente}, "
                        f"monto {oferta.montoOferta}, semana {oferta.semana}",
                        "ok",
                    )
                except Exception as exc:
                    import traceback
                    traceback.print_exc()
                    resultados.append({
                        "ciclo": ciclo, "estado": "fallido", "error": str(exc),
                        "agenciaLabel": agencia_label,
                    })
                    Progress.emit(f"Oferta {ciclo}/{total} ({agencia_label}) FALLÓ: {exc}", "error")

        exitosos = sum(1 for r in resultados if r["estado"] == "exitoso")
        fallidos = total - exitosos

        RUN_RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
        RUN_RESULTS_PATH.write_text(
            json.dumps({
                "flujo": "OF",
                "total": total,
                "exitosos": exitosos,
                "fallidos": fallidos,
                "detalle": resultados,
            }, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        assert fallidos == 0, (
            f"{fallidos} de {total} oferta(s) fallaron. Revisa {RUN_RESULTS_PATH}."
        )
