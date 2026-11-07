"""Construcción e inserción de la oferta CF en botDB. Movido de tests/test_login_cf.py."""
import random
import allure
from config.settings import Settings
from services.offer_repository import OfferRepository, OfferData
from utils.offer_id_allocator import OfferIdAllocator
from utils.birthdate_allocator import BirthdateAllocator
from utils.catalog_db import CatalogDB
from utils.mexican_names import MexicanNames


# Finabien solo aparece en "Método de entrega" si el monto elegido es menor a esto.
MONTO_MAXIMO_FINABIEN = 10000


def limite_monto_agencia(agencia_label: str):
    """
    Límite EXCLUSIVO del monto a elegir en CF: el de la agencia (p. ej. Tijuana: < 10,000)
    y, con método de entrega Finabien, < 10,000 (el portal solo muestra Finabien con
    montos menores; ver Context.md). Devuelve el más restrictivo, o None.
    """
    topes = [
        tope for prefijo, tope in Settings.MONTO_MAXIMO_CF_POR_AGENCIA.items()
        if agencia_label.startswith(prefijo)
    ]
    if Settings.METODO_ENTREGA == "Finabien":
        topes.append(MONTO_MAXIMO_FINABIEN)
    return min(topes) if topes else None


def monto_para_agencia(agencia_label: str) -> int:
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


def construir_oferta_cf(
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

    monto = monto_para_agencia(agencia_label)
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


def insertar_oferta_cf(
    repo: OfferRepository,
    numero_ciclo: int,
    agencia_label: str = None,
    tipo_oferta_elegido: str = None,
    nivel_precio: str = None,
) -> OfferData:
    """Construye, inserta y verifica en botDB una oferta CF. Devuelve la oferta insertada."""
    with allure.step("Generar identificadores e insertar oferta de prueba en botDB"):
        oferta = construir_oferta_cf(numero_ciclo, agencia_label, tipo_oferta_elegido, nivel_precio)
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
