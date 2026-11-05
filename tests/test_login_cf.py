import json
import random
import allure

from pathlib import Path

from config.settings import Settings
from pages.login_page import LoginPage
from pages.prestamo_personal_page import PrestamoPersonalPage
from pages.ofertas_listado_page import OfertasListadoPage
from services.network_interceptor import NetworkInterceptor
from services.offer_repository import OfferRepository, OfferData
from utils.offer_id_allocator import OfferIdAllocator
from utils.birthdate_allocator import BirthdateAllocator
from utils.catalog_db import CatalogDB
from utils.mexican_names import MexicanNames
from utils.progress import Progress

from pages.legalario_page import LegalarioPage
from tests.test_login import (
    _flujo_metodo_entrega,
    _flujo_identidad_a_otp,
    _flujo_beneficiario_a_finalizar,
)


RUN_RESULTS_PATH = Path(Settings.RUN_RESULTS_PATH) if Settings.RUN_RESULTS_PATH else Path("data/run_results_cf.json")


def _limite_monto_agencia(agencia_label: str):
    """Límite EXCLUSIVO de monto CF para la agencia (p. ej. Tijuana: < 10,000), o None."""
    for prefijo, tope in Settings.MONTO_MAXIMO_CF_POR_AGENCIA.items():
        if agencia_label.startswith(prefijo):
            return tope
    return None


def _monto_para_agencia(agencia_label: str) -> int:
    """
    Monto de la oferta: `monto` de run_config.json o uno aleatorio. Valida el tope
    por agencia (en Tijuana el monto de CF debe ser menor a 10,000).
    """
    monto = int(Settings.MONTO_OFERTA) if Settings.MONTO_OFERTA else random.choice(
        [1500, 2000, 2500, 3000]
    )
    for prefijo, tope in Settings.MONTO_MAXIMO_CF_POR_AGENCIA.items():
        if agencia_label.startswith(prefijo) and monto >= tope:
            raise ValueError(
                f"Monto {monto} no permitido para CF en {agencia_label}: debe ser "
                f"menor a {tope}. Ajusta 'monto' en data/run_config.json."
            )
    return monto


def _construir_oferta_cf(
    numero_ciclo: int,
    agencia_label: str = None,
    tipo_oferta_elegido: str = None,
    nivel_precio: str = None,
) -> OfferData:
    """
    Construye una oferta de prueba lista para insertar en botDB.dbo.Ofertas,
    con identificadores únicos (ver utils/offer_id_allocator.py) y datos
    ficticios pero coherentes con la agencia dada.

    agencia_label/tipo_oferta_elegido/nivel_precio son opcionales: si no se pasan
    (flujo CF normal) se usan los valores globales de Settings; el flujo de Oferta
    (tests/test_oferta.py) los pasa explícitos para poder combinar, en una misma
    corrida, ofertas con agencia/tipo/nivel distintos entre sí.

    Reglas de negocio pendientes de confirmar con negocio (marcadas también
    en ESPECIFICACIONES.md): template exacto de `descOferta`.
    """
    agencia_label = agencia_label if agencia_label is not None else Settings.AGENCIA_LABEL
    tipo_oferta_elegido = (
        tipo_oferta_elegido if tipo_oferta_elegido is not None else Settings.TIPO_OFERTA
    )
    nivel_precio = nivel_precio if nivel_precio is not None else Settings.NIVEL_PRECIO

    agencia_data = CatalogDB.get_agencia_by_label(agencia_label)
    if not agencia_data:
        raise RuntimeError(
            f"No se encontró la agencia '{agencia_label}' en el catálogo local"
        )

    agencia_cliente = int(agencia_data["agencia"])
    branch = int(str(agencia_data["agencia"])[:4])

    ids = OfferIdAllocator.get_unique_ids(branch=branch)

    fecha_nacimiento_ddmmyyyy = BirthdateAllocator.get_unique_birthdate()
    dia, mes, anio = fecha_nacimiento_ddmmyyyy.split("/")
    fecha_nacimiento_sql = f"{anio}-{mes}-{dia} 00:00:00.000"

    monto = _monto_para_agencia(agencia_label)
    plazo1, tasa1 = 14000, 65

    # tipoDeOferta y el texto de descOferta ("AGREGAR"/"REFIN!") dependen de lo
    # elegido en el menú (panel "Oferta" → Tipo de oferta).
    # Ver config/Context/REGLAS_DE_NEGOCIO.md.
    es_refin = tipo_oferta_elegido == "REFIN"
    tipo_oferta = "RE" if es_refin else "AD"

    # Agreement_Num: solo para REFIN. Fórmula confirmada contra insumos reales
    # (InsumosGen/CONTEXT.md + InsumosGen/output/Ofertas240826.sql):
    # '510' + AA (2 primeros dígitos de idOferta) + los últimos 4 dígitos de
    # idOferta (persona + consecutivo). Ej. idOferta=26084052 → 510264052.
    # Para AGREGAR se mantiene NULL (no aparece en descOferta).
    id_oferta_str = str(ids["idOferta"])
    agreement_num = int(f"510{id_oferta_str[:2]}{id_oferta_str[-4:]}") if es_refin else None
    texto_tipo = f"REFIN! {agreement_num}" if es_refin else "AGREGAR"

    persona = MexicanNames.generar()
    nombre_cliente = persona["nombre_completo"]
    desc_oferta = f"TARIFA MÁX {monto} {texto_tipo} {plazo1}/{tasa1} A"

    # Nivel de precio / promoción elegido en el menú (panel "Oferta"): N1/N2/N3 o
    # PP20/PP25, exclusivos entre sí. Se anexa al final de descOferta (formato en
    # InsumosGen/CONTEXT.md, "Formato descOferta"). Regla de negocio completa (qué
    # nivel aplica a qué tipo de cliente y sucursal Unbundling) en
    # InsumosGen/negocio/onboarding_po.md sección 10.3.
    if nivel_precio:
        desc_oferta = f"{desc_oferta} {nivel_precio}"

    rfc = MexicanNames.rfc(persona, fecha_nacimiento_ddmmyyyy)

    return OfferData(
        idOferta=ids["idOferta"],
        nombreCliente=nombre_cliente,
        porcentajeCalidadCliente=float(random.randint(60, 95)),
        montoOferta=monto,
        tipoDeOferta=tipo_oferta,
        agenciaCliente=agencia_cliente,
        # seccionCliente depende de la agencia (catálogo local, ver utils/catalog_db.py
        # y config/Context/REGLAS_DE_NEGOCIO.md). 'R' es el fallback para agencias sin
        # sección confirmada — es el valor observado con más frecuencia en insumos reales.
        seccionCliente=agencia_data.get("seccion") or "R",
        amOferta="amOferta",
        branchOferta=branch,
        descOferta=desc_oferta,
        semana=ids["semana"],
        Customer_Id=ids["Customer_Id"],
        Agreement_Num=agreement_num,
        FechaNacimiento=fecha_nacimiento_sql,
        RFC=rfc,
        direccionCliente="Calle de Prueba 123, Col. Centro, CP 00000",
    )


def _insertar_oferta_cf(
    repo: OfferRepository,
    numero_ciclo: int,
    agencia_label: str = None,
    tipo_oferta_elegido: str = None,
    nivel_precio: str = None,
) -> OfferData:
    """Construye, inserta y verifica en botDB una oferta CF. Devuelve la oferta insertada."""
    with allure.step("Generar identificadores e insertar oferta de prueba en botDB"):
        oferta = _construir_oferta_cf(numero_ciclo, agencia_label, tipo_oferta_elegido, nivel_precio)
        # El listado del front (getpesosmsgs) solo muestra las ofertas de la semana MÁS
        # RECIENTE de la tabla: con una semana anterior la oferta existe en BD pero no
        # aparece. Se usa la mayor entre la calculada y la máxima presente en la tabla.
        semana_calculada = int(oferta.semana)
        semana_tabla = repo.get_max_semana()
        oferta.semana = max(semana_calculada, semana_tabla)
        print(
            f"Semana de la oferta: {oferta.semana} "
            f"(calculada={semana_calculada}, máxima en tabla={semana_tabla})"
        )
        repo.insert_offer(oferta)
        with allure.step("Verificar que la oferta quedó insertada en botDB (SELECT)"):
            fila = repo.verify_offer_inserted(oferta)
            print(
                "Oferta verificada en BD — "
                f"idOferta={fila['idOferta']}, estatus={fila['idEstatusOferta']}, "
                f"agencia={fila['agenciaCliente']}, vendida={fila['VendidaProvidigital']}"
            )
        print(
            f"Oferta insertada — idOferta={oferta.idOferta}, "
            f"nombreCliente={oferta.nombreCliente}"
        )
    return oferta


def _capturar_diagnostico_falla(driver, ciclo: int) -> None:
    """Guarda screenshot, URL y HTML del punto de falla en data/diagnostico_cf/."""
    try:
        out = Path("data/diagnostico_cf")
        out.mkdir(parents=True, exist_ok=True)
        driver.save_screenshot(str(out / f"ciclo{ciclo}_falla.png"))
        (out / f"ciclo{ciclo}_falla.html").write_text(driver.page_source, encoding="utf-8")
        (out / f"ciclo{ciclo}_falla_url.txt").write_text(driver.current_url, encoding="utf-8")
        interceptor = NetworkInterceptor(driver)
        interceptor.save_to_file(
            interceptor.get_captured_requests(), str(out / f"ciclo{ciclo}_falla_requests.json")
        )
        interceptor.save_to_file(
            {"legalario_otp": interceptor.get_last_legalario_otp_response()},
            str(out / f"ciclo{ciclo}_falla_otp_legalario.json"),
        )
    except Exception as exc:
        print(f"No se pudo capturar diagnóstico: {exc}")


def _ejecutar_venta_cf(driver, numero_ciclo: int, contexto_falla: dict = None) -> dict:
    """
    Flujo completo de venta para Cliente Frecuente (CF).

    Orden validado en UAT: oferta preautorizada → método de entrega →
    identidad Legalario → documentos (+ consentimiento de geolocalización) →
    datos personales (sin OTP Provident) → beneficiario → contrato/firma →
    finalizar venta. Ver ESPECIFICACIONES.md.

    `contexto_falla` (opcional): dict mutable donde se anota el `idOferta` recién
    insertado en cuanto se conoce, antes de tocar el navegador. Así, si el resto
    del flujo falla, quien llama puede saber qué oferta quedó huérfana en botDB
    sin depender de comparar snapshots de la tabla de IDs (que no es seguro
    cuando hay varias ventas CF corriendo en paralelo).
    """
    login_page = LoginPage(driver)
    interceptor = NetworkInterceptor(driver)
    prestamo_personal_page = PrestamoPersonalPage(driver)
    legalario_page = LegalarioPage(driver)
    ofertas_listado_page = OfertasListadoPage(driver)

    repo = OfferRepository()
    oferta = _insertar_oferta_cf(repo, numero_ciclo)
    if contexto_falla is not None:
        contexto_falla["idOferta"] = oferta.idOferta

    # =========================
    # LOGIN Y FLUJO INICIAL (específico de Cliente Frecuente)
    # =========================
    with allure.step("Abrir la página de login"):
        login_page.open(Settings.BASE_URL)

    with allure.step("Ingresar estrella correcta"):
        login_page.enter_estrella(Settings.ESTRELLA)

    with allure.step("Ingresar contraseña correcta"):
        login_page.enter_password(Settings.PASSWORD)

    with allure.step("Enviar formulario"):
        login_page.click_login()

    with allure.step("Instalar interceptor de red (para OTP Legalario del contrato)"):
        interceptor.install_network_interceptor()
        interceptor.clear_captured_requests()
        interceptor.clear_all_otp_responses()

    with allure.step("Presionar 'Ventas'"):
        login_page.click_ventas()

    with allure.step("Presionar 'Registrar Venta'"):
        login_page.click_registrar_ventas()

    with allure.step("Presionar 'Cliente frecuente'"):
        login_page.click_cliente_frecuente()

    with allure.step(f"Buscar y seleccionar cliente: {oferta.nombreCliente}"):
        try:
            ofertas_listado_page.seleccionar_cliente(oferta.nombreCliente)
        except Exception as exc:
            semana_tabla = repo.get_max_semana()
            raise AssertionError(
                f"La oferta {oferta.idOferta} ('{oferta.nombreCliente}') está en botDB con "
                f"semana={oferta.semana} pero no apareció en el listado del front. Semana más "
                f"reciente en la tabla: {semana_tabla}. El front solo lista la semana más "
                f"reciente; revisa que la oferta la tenga. Detalle: {exc}"
            ) from exc

    with allure.step("Confirmar oferta preautorizada (plazo y monto)"):
        prestamo_personal_page.confirmar_oferta_cf(
            monto_maximo_exclusivo=_limite_monto_agencia(Settings.AGENCIA_LABEL)
        )

    _flujo_metodo_entrega(driver, login_page, interceptor, prestamo_personal_page)

    _flujo_identidad_a_otp(
        driver, login_page, legalario_page, interceptor, prestamo_personal_page,
        incluir_otp_provident=False,
    )

    folio = _flujo_beneficiario_a_finalizar(
        driver, login_page, interceptor, prestamo_personal_page
    )

    return {
        "idOferta": oferta.idOferta,
        "nombreCliente": oferta.nombreCliente,
        "folio": folio,
    }


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
                    oferta_info = _ejecutar_venta_cf(driver, ciclo, contexto_falla=contexto_falla)
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
                    _capturar_diagnostico_falla(driver, ciclo)
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
