import json
import allure

from pathlib import Path
from config.settings import Settings
from pages.login_page import LoginPage
from utils.allure_utils import take_step_screenshot
from utils.progress import Progress
from flows.venta_cf import capturar_diagnostico_falla, ejecutar_venta_cf


RUN_RESULTS_PATH = Path(Settings.RUN_RESULTS_PATH) if Settings.RUN_RESULTS_PATH else Path("data/run_results_cf.json")


@allure.epic("Provident")
@allure.feature("Login")
@allure.story("Venta Cliente Frecuente")
class TestLoginProvidentCF:

    @allure.title("Ventas automatizadas Cliente Frecuente — ciclos múltiples")
    def test_login_exitoso_cf(self, driver):
        total = Settings.CICLOS
        resultados = []

        print(f"\n{'='*50}")
        print(f"Flujo      : Cliente Frecuente (CF)")
        print(f"Agencia    : {Settings.AGENCIA_LABEL}")
        print(f"Método     : {Settings.METODO_ENTREGA}")
        print(f"Ciclos     : {total}")
        print(f"{'='*50}\n")

        for ciclo in range(1, total + 1):
            print(f"--- Iniciando ciclo CF {ciclo}/{total} ---")

            with allure.step(f"Ciclo CF {ciclo} de {total}"):
                contexto_falla = {}
                try:
                    oferta_info = ejecutar_venta_cf(driver, ciclo, contexto_falla=contexto_falla)
                    resultados.append({
                        "ciclo": ciclo,
                        "estado": "exitoso",
                        "error": None,
                        **oferta_info,
                    })
                    print(f"--- Ciclo CF {ciclo} EXITOSO ---\n")
                    Progress.emit(
                        f"Venta CF {ciclo}/{total} finalizada (folio {oferta_info.get('folio')})", "ok"
                    )

                except Exception as exc:
                    import traceback
                    traceback.print_exc()
                    resultados.append({
                        "ciclo": ciclo,
                        "estado": "fallido",
                        "error": str(exc),
                        "idOferta": contexto_falla.get("idOferta"),
                    })
                    print(f"--- Ciclo CF {ciclo} FALLIDO: {exc} ---\n")
                    Progress.emit(
                        f"Venta CF {ciclo}/{total} FALLÓ: {(str(exc).splitlines() or [''])[0][:120]}",
                        "error",
                    )
                    capturar_diagnostico_falla(driver, ciclo)
                    # Evidencia del estado real en el momento del fallo, antes de que la
                    # recuperación de sesión navegue al login.
                    try:
                        take_step_screenshot(driver, "fallo_en_ciclo", force=True)
                    except Exception:
                        pass
                    LoginPage(driver).recuperar_sesion_tras_fallo()

        exitosos = sum(1 for r in resultados if r["estado"] == "exitoso")
        fallidos = total - exitosos

        resumen = {
            "flujo": "CF",
            "agencia": Settings.AGENCIA_LABEL,
            "metodo_entrega": Settings.METODO_ENTREGA,
            "total": total,
            "exitosos": exitosos,
            "fallidos": fallidos,
            "detalle": resultados
        }

        RUN_RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
        RUN_RESULTS_PATH.write_text(
            json.dumps(resumen, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

        print(f"\n{'='*50}")
        print(f"RESUMEN FINAL CF")
        print(f"  Agencia   : {Settings.AGENCIA_LABEL}")
        print(f"  Total     : {total}")
        print(f"  Exitosos  : {exitosos}")
        print(f"  Fallidos  : {fallidos}")
        print(f"  Resultados: {RUN_RESULTS_PATH.resolve()}")
        print(f"{'='*50}\n")

        assert fallidos == 0, (
            f"{fallidos} de {total} ciclo(s) CF fallaron. "
            f"Revisa {RUN_RESULTS_PATH} para más detalles."
        )
