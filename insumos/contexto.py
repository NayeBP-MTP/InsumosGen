"""ContextoVenta: datos de la venta que se acumulan de módulo en módulo, con carga perezosa."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Protocol


class ErrorContexto(Exception):
    """Falta un dato imprescindible de la venta (no se debe escribir con valores en cero)."""


class FuenteExpediente(Protocol):
    """Lectura de Originacion que necesita el contexto (la implementa OriginacionRepository)."""

    def leer_expediente(self, numero_contrato=None, id_expediente=None) -> dict:
        """Fila de ExpedienteCliente: IdExpedienteCliente, numeroContrato, Agencia, Cliente,
        NombreCliente, RFCCliente, DomicilioCliente, FechaNacimiento."""

    def leer_montos(self, id_expediente: int) -> dict:
        """Fila de ExpedienteOferta del expediente: MontoTotal[Seguro], PrimerPagoSemanal[Seguro],
        PagoSubsecuente[Seguro]."""


@dataclass(frozen=True)
class Montos:
    monto_prestamo: float
    primer_pago: float
    pago_semanal: float


# columna de ExpedienteOferta por valor lógico: (sin seguro, con seguro)
COLUMNAS_MONTOS = {
    "monto_prestamo": ("MontoTotal", "MontoTotalSeguro"),
    "primer_pago": ("PrimerPagoSemanal", "PrimerPagoSemanalSeguro"),
    "pago_semanal": ("PagoSubsecuente", "PagoSubsecuenteSeguro"),
}


def elegir_montos(fila: dict, con_seguro: bool) -> Montos:
    """Toma de `fila` las columnas con o sin seguro; falla si alguna viene NULL, 0 o negativa."""
    valores = {}
    for logico, columnas in COLUMNAS_MONTOS.items():
        columna = columnas[1] if con_seguro else columnas[0]
        valor = fila.get(columna)
        if valor is None or float(valor) <= 0:
            raise ErrorContexto(
                f"ExpedienteOferta.{columna} viene {'NULL' if valor is None else valor}: no se "
                f"puede registrar el contrato {'con' if con_seguro else 'sin'} seguro con montos en cero."
            )
        valores[logico] = float(valor)
    return Montos(**valores)


@dataclass
class ContextoVenta:
    """
    `tipo` es "CN" o "CF" (define Customer_Status_Code: AA / CC). La venta se identifica por
    `numero_contrato` (criterio más seguro) o por `id_expediente`. El expediente y los montos se
    cargan la primera vez que un módulo los pide (`cargar_expediente`, `cargar_montos`).
    """
    tipo: str
    numero_contrato: Optional[str] = None
    id_expediente: Optional[int] = None
    con_seguro: bool = True
    inicio: Optional[datetime] = None
    cliente: int = 0
    agencia: Optional[int] = None
    fecha_nacimiento: Optional[datetime] = None
    nombre_cliente: Optional[str] = None
    rfc: Optional[str] = None
    domicilio: Optional[str] = None
    montos: Optional[Montos] = None
    fuente: Optional[FuenteExpediente] = field(default=None, repr=False, compare=False)

    def __post_init__(self):
        if self.tipo not in ("CN", "CF"):
            raise ErrorContexto(f"Tipo de venta desconocido: {self.tipo!r} (se esperaba 'CN' o 'CF')")

    @classmethod
    def desde_resultado_venta(cls, resultado, fuente: Optional[FuenteExpediente] = None):
        """Contexto inicial a partir del ResultadoVenta que devuelven VENTA_CN / VENTA_CF."""
        if not resultado.numero_contrato:
            raise ErrorContexto(
                "La venta no devolvió numero_contrato (¿sin BD o no se localizó el expediente?); "
                "dalo a mano para arrancar la receta sin venta."
            )
        return cls(
            tipo=resultado.tipo, numero_contrato=resultado.numero_contrato,
            id_expediente=resultado.id_expediente, con_seguro=resultado.con_seguro,
            inicio=resultado.inicio, fuente=fuente,
        )

    @property
    def status_code(self) -> str:
        """Customer_Status_Code: CC = CF, AA = CN."""
        return "CC" if self.tipo == "CF" else "AA"

    @property
    def expediente_cargado(self) -> bool:
        return self.nombre_cliente is not None

    def cargar_expediente(self) -> "ContextoVenta":
        """Lee ExpedienteCliente una sola vez y completa los datos del cliente."""
        if self.expediente_cargado:
            return self
        if not (self.numero_contrato or self.id_expediente):
            raise ErrorContexto("Falta numero_contrato o id_expediente para localizar la venta.")
        fila = self._fuente().leer_expediente(
            numero_contrato=self.numero_contrato, id_expediente=self.id_expediente
        )
        self.numero_contrato = str(fila["numeroContrato"])
        self.id_expediente = fila["IdExpedienteCliente"]
        self.agencia = fila["Agencia"]
        self.cliente = int(fila["Cliente"] or 0)
        self.nombre_cliente = fila["NombreCliente"]
        self.rfc = fila["RFCCliente"]
        self.domicilio = fila["DomicilioCliente"]
        self.fecha_nacimiento = fila["FechaNacimiento"]
        return self

    def cargar_montos(self) -> "ContextoVenta":
        """Lee ExpedienteOferta una sola vez y elige los montos con o sin seguro."""
        if self.montos is not None:
            return self
        self.cargar_expediente()
        self.montos = elegir_montos(self._fuente().leer_montos(self.id_expediente), self.con_seguro)
        return self

    def _fuente(self) -> FuenteExpediente:
        if self.fuente is None:
            raise ErrorContexto("El contexto no tiene fuente de datos para cargar el expediente.")
        return self.fuente
