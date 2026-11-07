import json
import allure

from pathlib import Path

from config.settings import Settings
from flows.venta_cn import ejecutar_venta_cn
from pages.login_page import LoginPage
from utils.allure_utils import take_step_screenshot
from utils.progress import Progress


RUN_RESULTS_PATH = Path(Settings.RUN_RESULTS_PATH) if Settings.RUN_RESULTS_PATH else Path("data/run_results.json")


@allure.epic("Provident")
@allure.feature("Login")
@allure.story("Autenticación exitosa")
class TestLoginProvident:

    @allure.title("Ventas automatizadas — ciclos múltiples")
    def test_login_exitoso(self, driver):
        total = Settings.CICLOS
        resultados = []

        print(f"\n{'='*50}")
        print(f"Agencia    : {Settings.AGENCIA_LABEL}")
        print(f"Método     : {Settings.METODO_ENTREGA}")
        print(f"Ciclos     : {total}")
        print(f"{'='*50}\n")

        for ciclo in range(1, total + 1):
            print(f"--- Iniciando ciclo {ciclo}/{total} ---")

            with allure.step(f"Ciclo {ciclo} de {total}"):
                try:
                    ejecutar_venta_cn(driver, ciclo)
                    resultados.append({
                        "ciclo": ciclo,
                        "estado": "exitoso",
                        "error": None
                    })
                    print(f"--- Ciclo {ciclo} EXITOSO ---\n")
                    Progress.emit(f"Venta CN {ciclo}/{total} finalizada", "ok")

                except Exception as exc:
                    resultados.append({
                        "ciclo": ciclo,
                        "estado": "fallido",
                        "error": str(exc)
                    })
                    print(f"--- Ciclo {ciclo} FALLIDO: {exc} ---\n")
                    Progress.emit(
                        f"Venta CN {ciclo}/{total} FALLÓ: {(str(exc).splitlines() or [''])[0][:120]}",
                        "error",
                    )
                    # Evidencia del estado real en el momento del fallo, antes de que la
                    # recuperación de sesión navegue al login.
                    try:
                        take_step_screenshot(driver, "fallo_en_ciclo", force=True)
                    except Exception:
                        pass
                    LoginPage(driver).recuperar_sesion_tras_fallo()

        # =========================
        # RESUMEN DE RESULTADOS
        # =========================
        exitosos = sum(1 for r in resultados if r["estado"] == "exitoso")
        fallidos = total - exitosos

        resumen = {
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
        print(f"RESUMEN FINAL")
        print(f"  Agencia   : {Settings.AGENCIA_LABEL}")
        print(f"  Total     : {total}")
        print(f"  Exitosos  : {exitosos}")
        print(f"  Fallidos  : {fallidos}")
        print(f"  Resultados: {RUN_RESULTS_PATH.resolve()}")
        print(f"{'='*50}\n")

        assert fallidos == 0, (
            f"{fallidos} de {total} ciclo(s) fallaron. "
            f"Revisa {RUN_RESULTS_PATH} para más detalles."
        )
