"""
Reanudar y deshacer con los módulos REALES contra una BD en memoria (sin red): se fuerza una falla en cada
módulo, antes y después de su efecto, y se comprueba qué se deshace solo, qué se reanuda y que deshacer
deja todo como estaba.
"""
import copy
from datetime import datetime

import pytest

from config.settings import Settings
from insumos.contexto import ContextoVenta, ErrorContexto
from insumos.deshacer import Deshacedor
from insumos.log_operacion import LogOperacion
from insumos.modulo import Modulo
from insumos.pendientes import PendientesStore
from insumos.recetas import PAUSA_QA, RECETAS
from insumos.runner import RunnerRecetas, fabrica_por_defecto
from services.cnfs_repository import CnfsRepository
from services.originacion_repository import OriginacionRepository
from utils.cliente_id_allocator import ClienteIdAllocator

CONTRATO = "240021110"
OFERTA = {"MontoTotal": 10520.39, "MontoTotalSeguro": 11028.61, "PrimerPagoSemanal": 562.26,
          "PrimerPagoSemanalSeguro": 589.36, "PagoSubsecuente": 321.23, "PagoSubsecuenteSeguro": 336.75}


class Mundo:
    """Estado de las dos BD en memoria."""

    def __init__(self):
        self.expediente = {
            "IdExpedienteCliente": 7329, "numeroContrato": CONTRATO, "Agencia": 2075000000335, "Cliente": 0,
            "NombreCliente": "NAYELI BENITEZ PEREZ", "RFCCliente": "BEPN9609031C7", "DomicilioCliente": "CALLE 1",
            "FechaNacimiento": datetime(1996, 9, 3), "IdPaso": 30,
        }
        self.agreements, self.customers, self.addresses = {}, {}, {}

    def foto(self):
        return copy.deepcopy((self.expediente, self.agreements, self.customers, self.addresses))


class OrigFalsa(OriginacionRepository):
    def __init__(self, mundo, dry_run=False):
        super().__init__(dry_run=dry_run)
        self.m = mundo

    def _cambiar(self, **campos):
        if self.dry_run:
            self.dry_run_log.append(campos)
        else:
            self.m.expediente.update(campos)

    def leer_expediente(self, numero_contrato=None, id_expediente=None):
        return dict(self.m.expediente)

    def leer_montos(self, id_expediente):
        return OFERTA

    def max_cliente_con_prefijo(self, prefijo):
        c = self.m.expediente["Cliente"]
        return c if prefijo * 1000 <= c <= prefijo * 1000 + 999 else None

    def actualizar_nombre_rfc(self, id_expediente, nombre, rfc):
        self._cambiar(NombreCliente=nombre, RFCCliente=rfc)

    def actualizar_cliente(self, id_expediente, cliente):
        self._cambiar(Cliente=cliente)

    def actualizar_id_paso(self, id_expediente, id_paso):
        self._cambiar(IdPaso=id_paso)


class CnfsFalsa(CnfsRepository):
    def __init__(self, mundo, dry_run=False):
        super().__init__(dry_run=dry_run)
        self.m = mundo

    def agreement_existe(self, n):
        return int(n) in self.m.agreements

    def customer_id_de_agreement(self, n):
        return self.m.agreements.get(int(n))

    def customer_existe(self, c):
        return int(c) in self.m.customers

    def address_existe(self, c, db):
        return (int(c), int(db)) in self.m.addresses

    def max_customer_id_con_prefijo(self, prefijo):
        return max((c for c in self.m.customers if prefijo * 1000 <= c <= prefijo * 1000 + 999), default=None)

    def insertar_agreement(self, valores):
        if self.dry_run:
            return self.dry_run_log.append(valores)
        self.m.agreements[valores["Agreement_Num"]] = valores["Customer_Id"]

    def insertar_cliente_y_direccion(self, customer, direccion):
        if self.dry_run:
            return self.dry_run_log.append((customer, direccion))
        self.m.customers[customer["Customer_Id"]] = customer["Customer_Status_Code"]
        self.m.addresses[(direccion["Customer_Id"], direccion["Customer_Address_Db_Id"])] = True

    def actualizar_customer_id_agreement(self, n, customer_id):
        if not self.dry_run:
            self.m.agreements[int(n)] = int(customer_id)

    def borrar_agreement(self, n):
        if not self.dry_run:
            self.m.agreements.pop(int(n), None)

    def borrar_customer(self, c):
        if not self.dry_run:
            self.m.customers.pop(int(c), None)

    def borrar_address(self, c, db):
        if not self.dry_run:
            self.m.addresses.pop((int(c), int(db)), None)


class Falla(Modulo):
    """Envuelve un módulo real: falla antes de su efecto o, con `despues`, después de escribir."""

    def __init__(self, real, despues):
        self.real, self.despues, self.nombre = real, despues, real.nombre

    def ejecutar(self, ctx, log, dry_run=False):
        if not self.despues:
            raise RuntimeError(f"falla simulada antes de {self.nombre}")
        self.real.ejecutar(ctx, log, dry_run)
        raise RuntimeError(f"falla simulada después de {self.nombre}")


@pytest.fixture(autouse=True)
def colaborador(monkeypatch):
    monkeypatch.setattr(Settings, "NUMERO_COLABORADOR", "04")


def armar(tmp_path, mundo=None, falla=None, despues=False, auto=True):
    """Runner con módulos reales sobre `mundo`; `falla` = nombre del módulo que debe fallar."""
    mundo = mundo or Mundo()
    orig, cnfs = OrigFalsa(mundo), CnfsFalsa(mundo)
    base = fabrica_por_defecto(False, orig, cnfs, ClienteIdAllocator(tmp_path / "ids.sqlite3"))

    def fabrica(nombre):
        real = base(nombre)
        return Falla(real, despues) if nombre == falla else real
    fabrica.fuente, fabrica.repositorios = orig, (orig, cnfs)
    runner = RunnerRecetas(directorio_logs=tmp_path / "logs", pendientes=PendientesStore(tmp_path / "p.json"),
                           fabrica=fabrica, auto_deshacer=auto)
    return runner, mundo


def ctx_cn(mundo):
    return ContextoVenta(tipo="CN", numero_contrato=CONTRATO, id_expediente=7329, con_seguro=True,
                         fuente=OrigFalsa(mundo))


def log_de(tmp_path):
    return LogOperacion(CONTRATO, tmp_path / "logs")


def estado_completo(mundo, dispersado=True):
    e = mundo.expediente
    assert e["NombreCliente"] != "NAYELI BENITEZ PEREZ" and e["RFCCliente"] != "BEPN9609031C7"
    assert len(str(e["Cliente"])) == 13 and (e["IdPaso"] == 22) == dispersado
    assert mundo.agreements == {int(CONTRATO): e["Cliente"]}
    assert mundo.customers == {e["Cliente"]: "AA"} and (e["Cliente"], 1) in mundo.addresses


# ---------- falla ANTES de la pausa: se deshace sola ----------

@pytest.mark.parametrize("despues", [False, True], ids=["antes_del_efecto", "despues_del_efecto"])
@pytest.mark.parametrize("modulo", ["RENOMBRAR_CLIENTE", "PASO_22_DISPERSADO", "AGREEMENT"])
def test_falla_antes_de_la_pausa_se_deshace_sola_y_deja_todo_como_estaba(tmp_path, modulo, despues):
    runner, mundo = armar(tmp_path, falla=modulo, despues=despues)
    original = mundo.foto()
    r = runner.ejecutar(RECETAS["CN_REGISTRO_DISPERSADO"], ctx_cn(mundo))
    assert (r.estado, r.modulo_fallido, r.deshecho) == ("fallida", modulo, True)
    assert mundo.foto() == original
    assert runner.pendientes.obtener(CONTRATO)["estado"] == "deshecha"
    assert runner.pendientes.pendientes() == []  # no se ofrece retomar lo deshecho
    assert log_de(tmp_path).modulos_completados() == []


def test_tras_deshacerse_sola_se_puede_volver_a_ejecutar_desde_cero(tmp_path):
    runner, mundo = armar(tmp_path, falla="AGREEMENT")
    runner.ejecutar(RECETAS["CN_REGISTRO_DISPERSADO"], ctx_cn(mundo))
    sano, _ = armar(tmp_path, mundo=mundo)
    r = sano.ejecutar(RECETAS["CN_REGISTRO_DISPERSADO"], ctx_cn(mundo))
    assert r.estado == "esperando_qa" and r.ejecutados == ["RENOMBRAR_CLIENTE", "PASO_22_DISPERSADO", "AGREEMENT"]


def test_reanudar_una_operacion_deshecha_pide_ejecutar_de_nuevo(tmp_path):
    runner, mundo = armar(tmp_path, falla="AGREEMENT")
    runner.ejecutar(RECETAS["CN_REGISTRO_DISPERSADO"], ctx_cn(mundo))
    with pytest.raises(ErrorContexto, match="se deshizo"):
        runner.reanudar(CONTRATO)


# ---------- falla DESPUÉS de la pausa: se conserva y se reanuda ----------

@pytest.mark.parametrize("despues", [False, True], ids=["antes_del_efecto", "despues_del_efecto"])
@pytest.mark.parametrize("modulo", ["CREAR_ID_CLIENTE", "ACTUALIZAR_ID_CLIENTE", "REGISTRO_CLIENTE"])
def test_falla_tras_la_pausa_se_conserva_y_reanudar_la_completa(tmp_path, modulo, despues):
    receta = RECETAS["CN_REGISTRO_DISPERSADO"]
    runner, mundo = armar(tmp_path, falla=modulo, despues=despues)
    assert runner.ejecutar(receta, ctx_cn(mundo)).estado == "esperando_qa"
    antes_de_fallar = mundo.foto()

    r = runner.continuar_tras_qa(CONTRATO, fuente=OrigFalsa(mundo))
    assert (r.estado, r.modulo_fallido, r.deshecho) == ("fallida", modulo, False)
    if modulo == "CREAR_ID_CLIENTE" and not despues:
        assert mundo.foto() == antes_de_fallar  # no llegó a escribir nada
    else:
        assert mundo.foto() != antes_de_fallar  # el estado parcial se conserva, no se deshace
    assert runner.pendientes.obtener(CONTRATO)["estado"] == "fallida"
    assert [e["operacion_id"] for e in runner.pendientes.pendientes()] == [CONTRATO]

    sano, _ = armar(tmp_path, mundo=mundo)  # proceso nuevo, ya sin falla
    r = sano.reanudar(CONTRATO)
    assert r.estado == "completada" and modulo in r.ejecutados and "RENOMBRAR_CLIENTE" not in r.ejecutados
    estado_completo(mundo)
    assert sano.pendientes.obtener(CONTRATO)["estado"] == "completada"


def test_reanudar_tras_fallar_despues_del_efecto_no_duplica_nada(tmp_path):
    runner, mundo = armar(tmp_path, falla="REGISTRO_CLIENTE", despues=True)
    runner.ejecutar(RECETAS["CN_REGISTRO_DISPERSADO"], ctx_cn(mundo))
    runner.continuar_tras_qa(CONTRATO, fuente=OrigFalsa(mundo))  # REGISTRO insertó y luego "murió"
    assert len(mundo.customers) == 1
    sano, _ = armar(tmp_path, mundo=mundo)
    assert sano.reanudar(CONTRATO).estado == "completada"
    estado_completo(mundo)
    assert len(mundo.customers) == 1 and len(mundo.addresses) == 1


# ---------- recetas sin pausa: umbral = último módulo ----------

def test_sin_pausa_falla_en_el_ultimo_modulo_se_conserva(tmp_path):
    runner, mundo = armar(tmp_path, falla="REGISTRO_CLIENTE")
    r = runner.ejecutar(RECETAS["CN_REGISTRADO"], ctx_cn(mundo))
    assert (r.estado, r.deshecho) == ("fallida", False)
    assert mundo.agreements and mundo.expediente["Cliente"]  # lo anterior se conserva para reanudar
    sano, _ = armar(tmp_path, mundo=mundo)
    assert sano.reanudar(CONTRATO).estado == "completada"
    estado_completo(mundo, dispersado=False)


def test_sin_pausa_falla_antes_del_ultimo_modulo_se_deshace(tmp_path):
    runner, mundo = armar(tmp_path, falla="AGREEMENT")
    original = mundo.foto()
    r = runner.ejecutar(RECETAS["CN_REGISTRADO"], ctx_cn(mundo))
    assert (r.estado, r.deshecho) == ("fallida", True) and mundo.foto() == original


def test_auto_deshacer_se_puede_apagar(tmp_path):
    runner, mundo = armar(tmp_path, falla="AGREEMENT", auto=False)
    r = runner.ejecutar(RECETAS["CN_REGISTRADO"], ctx_cn(mundo))
    assert (r.estado, r.deshecho) == ("fallida", False) and mundo.expediente["Cliente"]


# ---------- deshacer a demanda ----------

def completar(tmp_path, receta="CN_REGISTRO_INTERMEDIO"):
    runner, mundo = armar(tmp_path)
    original = mundo.foto()
    assert runner.ejecutar(RECETAS[receta], ctx_cn(mundo)).estado == "esperando_qa"
    assert runner.continuar_tras_qa(CONTRATO, fuente=OrigFalsa(mundo)).estado == "completada"
    return runner, mundo, original


def test_deshacer_a_demanda_una_operacion_terminada_deja_todo_como_estaba(tmp_path):
    runner, mundo, original = completar(tmp_path)
    estado_completo(mundo, dispersado=False)
    r = runner.deshacer(CONTRATO)
    assert mundo.foto() == original and r.omitidas == [] and len(r.deshechas) == 6
    assert runner.pendientes.obtener(CONTRATO)["estado"] == "deshecha"
    assert log_de(tmp_path).modulos_completados() == []


def test_deshacer_recorre_el_log_en_orden_inverso(tmp_path):
    runner, mundo, _ = completar(tmp_path)
    r = runner.deshacer(CONTRATO)
    tablas = [d.split(" en ")[1].split(" ")[0].split(".")[-1] for d in r.deshechas]
    assert tablas == ["Customer_Address_Table", "Customer_Table", "Agreement_Table", "ExpedienteCliente",
                      "ExpedienteCliente", "ExpedienteCliente"] or tablas[:2] == ["Customer_Address_Table", "Customer_Table"]
    assert r.deshechas[0].startswith("REGISTRO_CLIENTE")  # lo último que se hizo es lo primero que se deshace
    assert r.deshechas[-1].startswith("RENOMBRAR_CLIENTE")


def test_deshacer_dos_veces_es_idempotente(tmp_path):
    runner, mundo, original = completar(tmp_path)
    runner.deshacer(CONTRATO)
    r = runner.deshacer(CONTRATO)
    assert r.deshechas == [] and mundo.foto() == original


def test_tras_deshacer_la_receta_se_ejecuta_de_nuevo_completa(tmp_path):
    runner, mundo, _ = completar(tmp_path)
    runner.deshacer(CONTRATO)
    r = runner.ejecutar(RECETAS["CN_REGISTRO_INTERMEDIO"], ctx_cn(mundo))
    assert r.estado == "esperando_qa" and r.ejecutados == ["RENOMBRAR_CLIENTE", "AGREEMENT"]


def test_no_pisa_lo_que_cambio_otro_y_lo_informa_como_conflicto(tmp_path):
    runner, mundo, original = completar(tmp_path)
    mundo.expediente["NombreCliente"] = "NOMBRE PUESTO POR QA"  # alguien lo cambió después
    r = runner.deshacer(CONTRATO)
    assert mundo.expediente["NombreCliente"] == "NOMBRE PUESTO POR QA"
    (descripcion, motivo), = r.conflictos
    assert descripcion.startswith("RENOMBRAR_CLIENTE") and motivo.startswith("conflicto")
    # lo demás sí se revirtió
    assert mundo.expediente["Cliente"] == 0 and mundo.expediente["IdPaso"] == 30
    assert not mundo.agreements and not mundo.customers and not mundo.addresses


def test_deshacer_en_dry_run_informa_sin_tocar_nada_ni_marcar_el_log(tmp_path):
    runner, mundo, _ = completar(tmp_path)
    foto, vigentes = mundo.foto(), log_de(tmp_path).vigentes()
    dd = Deshacedor(OrigFalsa(mundo, dry_run=True), CnfsFalsa(mundo, dry_run=True), dry_run=True)
    r = dd.deshacer(log_de(tmp_path))
    assert len(r.deshechas) == 6 and mundo.foto() == foto and log_de(tmp_path).vigentes() == vigentes


def test_el_deshacedor_exige_dry_run_coherente(tmp_path):
    mundo = Mundo()
    with pytest.raises(ValueError, match="dry_run"):
        Deshacedor(OrigFalsa(mundo), CnfsFalsa(mundo), dry_run=True)


def test_el_log_no_se_borra_al_deshacer_y_marca_el_corte(tmp_path):
    runner, mundo, _ = completar(tmp_path)
    antes = len(log_de(tmp_path).entradas())
    runner.deshacer(CONTRATO)
    log = log_de(tmp_path)
    assert len(log.entradas()) == antes + 1 and log.entradas()[-1]["tipo"] == "deshecho"
    assert log.vigentes() == [] and list(log.escrituras_para_deshacer()) == []


def test_tabla_desconocida_en_el_log_falla_en_vez_de_ignorarse(tmp_path):
    mundo = Mundo()
    log = LogOperacion("x", tmp_path)
    log.escritura("M", "insert", "H", "OtraBase.dbo.Rara", {"id": 1}, nuevo={"id": 1})
    with pytest.raises(ValueError, match="No sé"):
        Deshacedor(OrigFalsa(mundo), CnfsFalsa(mundo)).deshacer(log)
