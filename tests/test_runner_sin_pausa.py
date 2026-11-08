"""Reanudar conserva la variante de una receta lanzada sin pausa de QA."""
from insumos.contexto import ContextoVenta
from insumos.modulo import Modulo
from insumos.pendientes import PendientesStore
from insumos.recetas import PAUSA_QA, RECETAS
from insumos.runner import RunnerRecetas


class Bitacora:
    def __init__(self, falla=None):
        self.llamadas, self.falla = [], falla

    def fabrica(self, nombre):
        bitacora = self

        class Falso(Modulo):
            def ejecutar(self, ctx, log, dry_run=False):
                bitacora.llamadas.append(nombre)
                if bitacora.falla == nombre:
                    raise RuntimeError(f"falló {nombre}")
                return ctx

        return Falso()


def _runner(tmp_path, bitacora):
    return RunnerRecetas(directorio_logs=tmp_path / "logs", auto_deshacer=False,
                         pendientes=PendientesStore(tmp_path / "p.json"), fabrica=bitacora.fabrica)


def test_reanudar_conserva_la_variante_sin_pausa_qa(tmp_path):
    receta = RECETAS["CN_REGISTRO_INTERMEDIO"].sin_pausa_qa()
    ctx = ContextoVenta(tipo="CN", numero_contrato="240021110", id_expediente=7329)
    runner = _runner(tmp_path, Bitacora(falla="CREAR_ID_CLIENTE"))
    assert runner.ejecutar(receta, ctx).estado == "fallida"
    assert runner.pendientes.obtener("240021110")["sin_pausa_qa"] is True

    bit = Bitacora()
    r = _runner(tmp_path, bit).reanudar("240021110")  # no debe reintroducir la pausa
    assert r.estado == "completada" and PAUSA_QA not in bit.llamadas
    assert r.ejecutados == ["CREAR_ID_CLIENTE", "ACTUALIZAR_ID_CLIENTE", "REGISTRO_CLIENTE"]


def test_una_receta_normal_no_marca_sin_pausa(tmp_path):
    bit = Bitacora()
    runner = _runner(tmp_path, bit)
    runner.ejecutar(RECETAS["CN_REGISTRADO"], ContextoVenta(tipo="CN", numero_contrato="1", id_expediente=1,
                                                                    fuente=None))
    assert runner.pendientes.obtener("1")["sin_pausa_qa"] is False
