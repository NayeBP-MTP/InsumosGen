"""Pruebas unitarias (sin BD) de la línea de comandos `python -m insumos`."""
import pytest

from config.settings import Settings
from insumos.cli import BIEN, FALLO, USO, main
from insumos.contexto import ErrorContexto
from insumos.deshacer import ResultadoDeshacer
from insumos.pendientes import PendientesStore
from insumos.recetas import RECETAS
from insumos.runner import ResultadoReceta


class RunnerFalso:
    def __init__(self, dry_run=False, resultado=None, deshacer=None):
        self.dry_run, self.llamadas = dry_run, []
        self.resultado, self.res_deshacer = resultado, deshacer

    def ejecutar(self, receta, ctx):
        self.llamadas.append(("ejecutar", receta, ctx))
        return self.resultado or ResultadoReceta(receta.id, ctx.numero_contrato, "completada", ["A", "B"])

    def continuar_tras_qa(self, contrato):
        self.llamadas.append(("continuar", contrato))
        return self.resultado or ResultadoReceta("CN_REGISTRO_INTERMEDIO", contrato, "completada", ["X"])

    def reanudar(self, contrato):
        self.llamadas.append(("reanudar", contrato))
        return self.resultado or ResultadoReceta("CN_REGISTRADO", contrato, "completada", [])

    def deshacer(self, contrato):
        self.llamadas.append(("deshacer", contrato, self.dry_run))
        return self.res_deshacer or ResultadoDeshacer(contrato, ["REGISTRO_CLIENTE: insert ..."], [])


def correr(argv, tmp_path, runner=None, **kw):
    salida = []
    runner = runner or RunnerFalso(**kw)
    creados = []

    def fabrica(dry_run=False):
        runner.dry_run = dry_run
        creados.append(dry_run)
        return runner

    codigo = main(argv, fabrica_runner=fabrica, pendientes=PendientesStore(tmp_path / "p.json"), salida=salida.append)
    return codigo, "\n".join(salida), runner, creados


def test_listar_muestra_las_seis_recetas_con_sus_pasos(tmp_path):
    codigo, texto, _, _ = correr(["listar"], tmp_path)
    assert codigo == BIEN
    for receta in RECETAS.values():
        assert receta.id in texto and receta.nombre in texto
    assert "RENOMBRAR_CLIENTE -> AGREEMENT -> PAUSA_QA -> CREAR_ID_CLIENTE" in texto


def test_ejecutar_arma_el_contexto_con_el_tipo_de_la_receta(tmp_path):
    codigo, texto, runner, creados = correr(
        ["ejecutar", "CF_REGISTRADO", "--contrato", "240021111", "--sin-seguro"], tmp_path)
    (_, receta, ctx), = runner.llamadas
    assert codigo == BIEN and receta.id == "CF_REGISTRADO"
    assert (ctx.tipo, ctx.numero_contrato, ctx.con_seguro) == ("CF", "240021111", False)
    assert creados == [False] and "sin seguro" in texto and "completada" in texto


def test_el_seguro_por_defecto_sale_de_la_configuracion(tmp_path, monkeypatch):
    monkeypatch.setattr(Settings, "CON_SEGURO", False)
    _, _, runner, _ = correr(["ejecutar", "CN_REGISTRADO", "--contrato", "1"], tmp_path)
    assert runner.llamadas[0][2].con_seguro is False
    _, _, runner, _ = correr(["ejecutar", "CN_REGISTRADO", "--contrato", "1", "--con-seguro"], tmp_path)
    assert runner.llamadas[0][2].con_seguro is True


def test_dry_run_se_pasa_al_runner(tmp_path):
    codigo, texto, _, creados = correr(["ejecutar", "CN_REGISTRADO", "--contrato", "1", "--dry-run"], tmp_path)
    assert creados == [True] and texto.startswith("[dry-run]")


def test_sin_pausa_qa_quita_la_pausa(tmp_path):
    _, _, runner, _ = correr(["ejecutar", "CN_REGISTRO_INTERMEDIO", "--contrato", "1", "--sin-pausa-qa"], tmp_path)
    assert not runner.llamadas[0][1].tiene_pausa_qa


def test_colaborador_se_fija_en_la_configuracion(tmp_path, monkeypatch):
    monkeypatch.setattr(Settings, "NUMERO_COLABORADOR", "")
    correr(["ejecutar", "CN_REGISTRADO", "--contrato", "1", "--colaborador", "07"], tmp_path)
    assert Settings.NUMERO_COLABORADOR == "07"


def test_la_pausa_de_qa_sale_bien_e_indica_que_hacer(tmp_path):
    r = ResultadoReceta("CN_REGISTRO_INTERMEDIO", "240021110", "esperando_qa", ["RENOMBRAR_CLIENTE", "AGREEMENT"])
    codigo, texto, _, _ = correr(["ejecutar", "CN_REGISTRO_INTERMEDIO", "--contrato", "240021110"], tmp_path,
                                 resultado=r)
    assert codigo == BIEN and "pausa de QA" in texto and "python -m insumos continuar 240021110" in texto


def test_una_falla_sale_con_1_y_ofrece_reanudar_o_deshacer(tmp_path):
    r = ResultadoReceta("CN_REGISTRADO", "240021110", "fallida", error="boom", modulo_fallido="AGREEMENT")
    codigo, texto, _, _ = correr(["ejecutar", "CN_REGISTRADO", "--contrato", "240021110"], tmp_path, resultado=r)
    assert codigo == FALLO and "FALLÓ en AGREEMENT: boom" in texto
    assert "reanudar 240021110" in texto and "deshacer 240021110" in texto


def test_una_falla_deshecha_sola_lo_dice(tmp_path):
    r = ResultadoReceta("CN_REGISTRADO", "1", "fallida", error="x", modulo_fallido="AGREEMENT", deshecho=True)
    codigo, texto, _, _ = correr(["ejecutar", "CN_REGISTRADO", "--contrato", "1"], tmp_path, resultado=r)
    assert codigo == FALLO and "se deshizo sola" in texto and "reanudar" not in texto


def test_continuar_y_reanudar_llaman_al_runner(tmp_path):
    codigo, _, runner, _ = correr(["continuar", "240021110"], tmp_path)
    assert codigo == BIEN and runner.llamadas == [("continuar", "240021110")]
    codigo, _, runner, _ = correr(["reanudar", "240021110"], tmp_path)
    assert codigo == BIEN and runner.llamadas == [("reanudar", "240021110")]


def test_deshacer_informa_lo_revertido_y_admite_dry_run(tmp_path):
    codigo, texto, runner, _ = correr(["deshacer", "240021110"], tmp_path)
    assert codigo == BIEN and "Revertidas 1 escritura" in texto
    assert runner.llamadas == [("deshacer", "240021110", False)]
    codigo, texto, runner, _ = correr(["deshacer", "240021110", "--dry-run"], tmp_path)
    assert "[dry-run] revertiría 1" in texto and runner.llamadas == [("deshacer", "240021110", True)]


def test_deshacer_con_conflicto_sale_con_1(tmp_path):
    res = ResultadoDeshacer("1", [], [("RENOMBRAR_CLIENTE: update ...", "conflicto: la BD tiene otro valor")])
    codigo, texto, _, _ = correr(["deshacer", "1"], tmp_path, deshacer=res)
    assert codigo == FALLO and "omitida (conflicto" in texto and "Hay conflictos" in texto


def test_deshacer_sin_log_dice_que_no_hay_nada(tmp_path):
    codigo, texto, _, _ = correr(["deshacer", "1"], tmp_path, deshacer=ResultadoDeshacer("1"))
    assert codigo == BIEN and "Nada que deshacer" in texto


def test_pendientes_vacio_y_con_operaciones(tmp_path):
    _, texto, _, _ = correr(["pendientes"], tmp_path)
    assert "No hay operaciones pendientes" in texto
    tienda = PendientesStore(tmp_path / "p.json")
    tienda.guardar("240021110", receta="CN_REGISTRO_INTERMEDIO", estado="esperando_qa", paso_actual="PAUSA_QA",
                   para_qa={"numero_contrato": "240021110", "fecha_nacimiento": "1996-09-03"})
    tienda.guardar("240021111", receta="CF_REGISTRADO", estado="fallida", paso_actual="AGREEMENT", error="boom")
    tienda.guardar("240021112", receta="CF_REGISTRADO", estado="completada")
    _, texto, _, _ = correr(["pendientes"], tmp_path)
    assert "240021110  CN_REGISTRO_INTERMEDIO  esperando_qa" in texto and "fecha de nacimiento 1996-09-03" in texto
    assert "240021111  CF_REGISTRADO  fallida  paso: AGREEMENT  error: boom" in texto
    assert "240021112" not in texto  # las completadas no se ofrecen


def test_errores_de_datos_salen_con_2_sin_traceback(tmp_path):
    class Roto(RunnerFalso):
        def reanudar(self, contrato):
            raise ErrorContexto("No hay una operación con id 9.")

    codigo, texto, _, _ = correr(["reanudar", "9"], tmp_path, runner=Roto())
    assert codigo == USO and texto == "Error: No hay una operación con id 9."


@pytest.mark.parametrize("argv", [[], ["ejecutar"], ["ejecutar", "NO_EXISTE", "--contrato", "1"],
                                  ["ejecutar", "CN_REGISTRADO"], ["deshacer"]])
def test_uso_invalido_lo_rechaza_argparse(argv, tmp_path):
    with pytest.raises(SystemExit) as exc:
        correr(argv, tmp_path)
    assert exc.value.code == 2
