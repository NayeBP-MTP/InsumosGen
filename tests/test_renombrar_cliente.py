"""Pruebas unitarias (sin BD) del módulo RENOMBRAR_CLIENTE."""
import re
from datetime import datetime

import pytest

from insumos.contexto import ContextoVenta, ErrorContexto
from insumos.log_operacion import LogOperacion
from insumos.modulos.renombrar_cliente import RenombrarCliente
from services.originacion_repository import OriginacionRepository
from utils.mexican_names import MexicanNames

PERSONA = {"nombre": "MARÍA GUADALUPE", "apellido_paterno": "GÓMEZ", "apellido_materno": "ÁLVAREZ",
           "nombre_completo": "MARÍA GUADALUPE GÓMEZ ÁLVAREZ"}


class FuenteFake:
    def __init__(self, nacimiento=datetime(1996, 9, 7, 5, 0)):
        self.fila = {
            "IdExpedienteCliente": 7331, "numeroContrato": "240021111", "Agencia": 2075000000335,
            "Cliente": 2075261100023, "NombreCliente": "NAYELI BENITEZ PEREZ", "RFCCliente": "GURC9609067WA",
            "DomicilioCliente": "CALLE 1", "FechaNacimiento": nacimiento,
        }

    def leer_expediente(self, numero_contrato=None, id_expediente=None):
        return dict(self.fila)


def _ctx(fuente=None):
    return ContextoVenta(tipo="CF", numero_contrato="240021111", fuente=fuente or FuenteFake())


def _modulo(generar=lambda: dict(PERSONA)):
    return RenombrarCliente(repo=OriginacionRepository(dry_run=True), generar=generar)


def test_actualiza_nombre_y_rfc_coherentes_con_la_fecha_de_nacimiento(tmp_path):
    modulo, log, ctx = _modulo(), LogOperacion("240021111", tmp_path), _ctx()
    # dry_run=False del módulo contra repo dry_run: lo detecta (ver test de abajo); aquí usamos dry_run=True
    modulo.ejecutar(ctx, log, dry_run=True)
    (sql, params), = modulo.repo.dry_run_log
    assert "UPDATE [dbo].[ExpedienteCliente]" in sql
    nombre, rfc, id_exp = params
    assert nombre == "MARÍA GUADALUPE GÓMEZ ÁLVAREZ" and id_exp == 7331
    assert re.fullmatch(r"GOAM960907[A-Z0-9]{3}", rfc)  # G + primera vocal interna de GOMEZ (O) + A (ALVAREZ) + M (MARIA)
    assert (ctx.nombre_cliente, ctx.rfc, ctx.persona) == (nombre, rfc, PERSONA)


def test_dry_run_no_escribe_log(tmp_path):
    log = LogOperacion("240021111", tmp_path)
    _modulo().ejecutar(_ctx(), log, dry_run=True)
    assert log.entradas() == []


def test_con_dry_run_distinto_al_del_repositorio_falla_sin_escribir(tmp_path):
    modulo = _modulo()
    with pytest.raises(ValueError, match="dry_run"):
        modulo.ejecutar(_ctx(), LogOperacion("x", tmp_path), dry_run=False)
    assert modulo.repo.dry_run_log == []


class RepoReal(OriginacionRepository):
    """Repositorio 'real' que en vez de escribir en la BD guarda las sentencias."""

    def __init__(self):
        super().__init__(dry_run=False)
        self.escrituras = []

    def _escribir(self, sql, params=()):
        self.escrituras.append((sql, tuple(params)))


def test_escritura_real_deja_en_el_log_el_valor_anterior_y_el_nuevo(tmp_path):
    repo, log = RepoReal(), LogOperacion("240021111", tmp_path)
    ctx = RenombrarCliente(repo=repo, generar=lambda: dict(PERSONA)).ejecutar(_ctx(), log)
    assert len(repo.escrituras) == 1
    (e,) = [x for x in log.entradas() if x["tipo"] == "update"]
    assert e["host"] == "PESOS_OFFER" and e["tabla"] == "Originacion.dbo.ExpedienteCliente"
    assert e["llave"] == {"IdExpedienteCliente": 7331}
    assert e["anterior"] == {"NombreCliente": "NAYELI BENITEZ PEREZ", "RFCCliente": "GURC9609067WA"}
    assert e["nuevo"]["NombreCliente"] == ctx.nombre_cliente and e["nuevo"]["persona"] == PERSONA


def test_idempotente_al_reanudar_no_cambia_el_nombre_y_recupera_la_persona(tmp_path):
    repo, log = RepoReal(), LogOperacion("240021111", tmp_path)
    RenombrarCliente(repo=repo, generar=lambda: dict(PERSONA)).ejecutar(_ctx(), log)

    # nuevo proceso: el expediente ya trae el nombre nuevo en la BD
    fuente = FuenteFake()
    fuente.fila["NombreCliente"] = PERSONA["nombre_completo"]
    otro = {**PERSONA, "nombre_completo": "OTRO NOMBRE DISTINTO"}
    ctx = RenombrarCliente(repo=repo, generar=lambda: otro).ejecutar(_ctx(fuente), log)
    assert len(repo.escrituras) == 1  # no escribió de nuevo
    assert ctx.persona == PERSONA


def test_si_el_nombre_cambio_por_fuera_se_vuelve_a_renombrar(tmp_path):
    repo, log = RepoReal(), LogOperacion("240021111", tmp_path)
    RenombrarCliente(repo=repo, generar=lambda: dict(PERSONA)).ejecutar(_ctx(), log)
    RenombrarCliente(repo=repo, generar=lambda: dict(PERSONA)).ejecutar(_ctx(), log)  # BD aún con el nombre viejo
    assert len(repo.escrituras) == 2


def test_sin_fecha_de_nacimiento_falla(tmp_path):
    with pytest.raises(ErrorContexto, match="FechaNacimiento"):
        _modulo().ejecutar(_ctx(FuenteFake(nacimiento=None)), LogOperacion("x", tmp_path), dry_run=True)


def test_con_el_generador_real_el_rfc_sigue_el_patron(tmp_path):
    ctx = _modulo(MexicanNames.generar).ejecutar(_ctx(), LogOperacion("x", tmp_path), dry_run=True)
    assert re.fullmatch(r"[A-Z]{4}960907[A-Z0-9]{3}", ctx.rfc)
