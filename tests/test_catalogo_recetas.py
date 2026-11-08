"""El catálogo de recetas debe ser coherente: cada módulo de insumo tiene receta y cada receta es ejecutable."""
from dataclasses import replace

import pytest

from insumos.recetas import (
    MODULOS, PAUSA_QA, RECETAS, TIPOS_VENTA, Receta, validar_o_fallar, validar_recetas)
from insumos.runner import fabrica_por_defecto


def _con(*recetas):
    return {r.id: r for r in recetas}


def _receta(pasos, tipo="CN", id="X"):
    return Receta(id, "x", tipo, tuple(pasos))


def test_el_catalogo_real_no_tiene_problemas():
    assert validar_recetas() == []
    validar_o_fallar()


def test_cada_modulo_de_insumo_esta_en_al_menos_una_receta():
    usados = {p for r in RECETAS.values() for p in r.pasos if p != PAUSA_QA}
    assert usados == set(MODULOS)


def test_cada_tipo_de_venta_tiene_recetas():
    for tipo in TIPOS_VENTA:
        assert [r.id for r in RECETAS.values() if r.tipo_venta == tipo], tipo


def test_cada_modulo_tiene_su_implementacion_en_la_fabrica_y_viceversa():
    fabrica = fabrica_por_defecto(dry_run=True)
    assert {fabrica(m).nombre for m in MODULOS} == set(MODULOS)


def test_la_fabrica_se_niega_si_el_catalogo_tiene_un_modulo_que_no_implementa(monkeypatch):
    import insumos.runner as runner
    monkeypatch.setattr(runner, "MODULOS", MODULOS + ("MODULO_NUEVO",))
    with pytest.raises(ValueError, match="MODULO_NUEVO"):
        fabrica_por_defecto(dry_run=True)


def test_las_variantes_sin_pausa_tambien_son_validas():
    sin_pausa = {r.id: r.sin_pausa_qa() for r in RECETAS.values()}
    assert validar_recetas(sin_pausa) == []


# --- cada regla detecta su problema ---

def test_un_modulo_sin_receta_se_detecta():
    sin_paso22 = _con(*[r for r in RECETAS.values() if "PASO_22_DISPERSADO" not in r.pasos])
    assert any("PASO_22_DISPERSADO" in p and "no está en ninguna receta" in p for p in validar_recetas(sin_paso22))


def test_un_tipo_de_venta_sin_recetas_se_detecta():
    solo_cn = _con(*[r for r in RECETAS.values() if r.tipo_venta == "CN"])
    assert any("venta CF" in p for p in validar_recetas(solo_cn))


def test_un_paso_desconocido_o_repetido_se_detecta():
    problemas = validar_recetas({**RECETAS, "X": _receta(["RENOMBRAR_CLIENTE", "INVENTADO", "RENOMBRAR_CLIENTE"])})
    assert any("paso desconocido 'INVENTADO'" in p for p in problemas)
    assert any("RENOMBRAR_CLIENTE aparece más de una vez" in p for p in problemas)


def test_tipo_de_venta_desconocido_y_clave_distinta_al_id(monkeypatch):
    problemas = validar_recetas({**RECETAS, "OTRA": _receta(["RENOMBRAR_CLIENTE", "AGREEMENT"], tipo="XX", id="Y")})
    assert any("tipo de venta desconocido 'XX'" in p for p in problemas)
    assert any("registrada con la clave 'OTRA'" in p for p in problemas)


def test_receta_vacia_o_con_dos_pausas():
    problemas = validar_recetas({**RECETAS, "X": _receta([PAUSA_QA]),
                                 "Y": _receta(["RENOMBRAR_CLIENTE", PAUSA_QA, PAUSA_QA], id="Y")})
    assert any(p.startswith("X:") and "no tiene módulos" in p for p in problemas)
    assert any(p.startswith("Y:") and "más de una pausa" in p for p in problemas)


@pytest.mark.parametrize("pasos,tipo,fragmento", [
    (["AGREEMENT", "REGISTRO_CLIENTE"], "CF", "REGISTRO_CLIENTE necesita RENOMBRAR_CLIENTE"),
    (["REGISTRO_CLIENTE", "RENOMBRAR_CLIENTE"], "CF", "REGISTRO_CLIENTE necesita RENOMBRAR_CLIENTE"),
    (["RENOMBRAR_CLIENTE", "CREAR_ID_CLIENTE", "ACTUALIZAR_ID_CLIENTE"], "CN", "ACTUALIZAR_ID_CLIENTE necesita AGREEMENT"),
    (["RENOMBRAR_CLIENTE", "AGREEMENT", "ACTUALIZAR_ID_CLIENTE"], "CN", "ACTUALIZAR_ID_CLIENTE necesita CREAR_ID_CLIENTE"),
    (["RENOMBRAR_CLIENTE", "AGREEMENT", "REGISTRO_CLIENTE"], "CN", "en CN, REGISTRO_CLIENTE necesita CREAR_ID_CLIENTE"),
    (["RENOMBRAR_CLIENTE", "REGISTRO_CLIENTE", "CREAR_ID_CLIENTE"], "CN", "en CN, REGISTRO_CLIENTE necesita CREAR_ID_CLIENTE"),
    (["RENOMBRAR_CLIENTE", "AGREEMENT", "CREAR_ID_CLIENTE"], "CN", "falta ACTUALIZAR_ID_CLIENTE"),
    (["RENOMBRAR_CLIENTE", "CREAR_ID_CLIENTE", "AGREEMENT"], "CF", "en CF no se usa CREAR_ID_CLIENTE"),
    (["RENOMBRAR_CLIENTE", "AGREEMENT", "ACTUALIZAR_ID_CLIENTE"], "CF", "en CF no se usa ACTUALIZAR_ID_CLIENTE"),
])
def test_dependencias_entre_modulos(pasos, tipo, fragmento):
    problemas = validar_recetas({**RECETAS, "X": _receta(pasos, tipo)})
    assert any(p.startswith("X:") and fragmento in p for p in problemas), problemas


def test_validar_o_fallar_lista_todos_los_problemas():
    roto = {**RECETAS, "X": _receta(["INVENTADO"])}
    with pytest.raises(ValueError, match="inconsistente") as exc:
        validar_o_fallar(roto)
    assert "paso desconocido 'INVENTADO'" in str(exc.value)


def test_una_receta_valida_nueva_pasa():
    nueva = _receta(["RENOMBRAR_CLIENTE", "PASO_22_DISPERSADO", "CREAR_ID_CLIENTE", "AGREEMENT", "REGISTRO_CLIENTE"], id="NUEVA")
    assert validar_recetas({**RECETAS, "NUEVA": nueva}) == []
