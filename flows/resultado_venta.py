"""Resultado de una venta (CN/CF): datos para los módulos de insumo, localizados en la BD."""
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Optional

from config.settings import Settings
from services.originacion_repository import OriginacionRepository

# Tras el último click el backend tarda en escribir FechaFinalizacion.
LOCALIZAR_ESPERA = 30
LOCALIZAR_INTERVALO = 2


@dataclass
class ResultadoVenta:
    """`numero_contrato` y `nombre_ine` son None si la venta no se pudo localizar en la BD."""
    tipo: str  # "CN" | "CF"
    agencia_label: str
    con_seguro: bool
    inicio: Optional[datetime] = None  # hora del servidor (SYSDATETIME) al empezar la venta
    folio: Optional[str] = None  # del log del front; no fiable (ver Context.md)
    id_oferta: int = 0
    nombre_ine: Optional[str] = None
    numero_contrato: Optional[str] = None
    folio_contrato: Optional[str] = None
    id_expediente: Optional[int] = None

    def a_dict(self) -> dict:
        d = asdict(self)
        d["inicio"] = self.inicio.isoformat(sep=" ") if self.inicio else None
        return d


def hora_inicio_servidor() -> Optional[datetime]:
    """Hora del servidor al arrancar la venta; None (con aviso) si la BD no responde."""
    try:
        return OriginacionRepository().hora_servidor()
    except Exception as exc:
        print(f"No se pudo leer la hora del servidor; el contrato no se localizará: {exc}")
        return None


def localizar_venta(resultado: ResultadoVenta, repo: Optional[OriginacionRepository] = None) -> ResultadoVenta:
    """
    Completa `resultado` con el expediente que la venta acaba de crear en Originacion:
    mismo vendedor (estrella), `IdOferta` (CF) o 0 (CN) y `FechaFinalizacion` posterior al
    inicio. Si hay varios candidatos (corridas paralelas del mismo vendedor) toma el más
    reciente y lo avisa.
    """
    if resultado.inicio is None:
        return resultado
    try:
        repo = repo or OriginacionRepository()
        limite = time.time() + LOCALIZAR_ESPERA
        while True:
            filas = repo.buscar_venta_finalizada(
                int(Settings.ESTRELLA), resultado.inicio, resultado.id_oferta
            )
            if filas or time.time() >= limite:
                break
            time.sleep(LOCALIZAR_INTERVALO)
    except Exception as exc:
        print(f"No se pudo localizar la venta en Originacion: {exc}")
        return resultado
    if not filas:
        print(f"Venta no localizada en Originacion (estrella {Settings.ESTRELLA}, desde {resultado.inicio}).")
        return resultado
    if len(filas) > 1:
        print(f"{len(filas)} expedientes candidatos; se toma el más reciente: "
              f"{[f['numeroContrato'] for f in filas]}")
    fila = filas[0]
    resultado.nombre_ine = fila["NombreCliente"]
    resultado.numero_contrato = fila["numeroContrato"]
    resultado.folio_contrato = fila["folioContrato"]
    resultado.id_expediente = fila["IdExpedienteCliente"]
    print(f"Venta localizada: contrato {resultado.numero_contrato}, INE '{resultado.nombre_ine}'")
    return resultado
