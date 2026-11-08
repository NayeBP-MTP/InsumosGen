"""Estado persistido de las operaciones de insumo (incluida la pausa de QA): data/insumos_pendientes.json."""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

RUTA_DEFAULT = Path("data/insumos_pendientes.json")

EN_CURSO = "en_curso"
ESPERANDO_QA = "esperando_qa"
COMPLETADA = "completada"
FALLIDA = "fallida"
DESHECHA = "deshecha"
# Estados que se ofrecen al abrir el asistente ("Retomar operaciones pendientes").
RETOMABLES = (EN_CURSO, ESPERANDO_QA, FALLIDA)


class PendientesStore:
    """
    Una entrada por operación (`operacion_id` = contrato). La pausa de QA es un estado, no un hilo
    bloqueado: sobrevive a cerrar la ventana. Cada escritura reemplaza el archivo completo de forma
    atómica (temporal + os.replace).
    """

    def __init__(self, ruta: Optional[Path] = None):
        self.ruta = Path(ruta or RUTA_DEFAULT)

    def _leer(self) -> dict:
        if not self.ruta.exists():
            return {}
        try:
            return json.loads(self.ruta.read_text(encoding="utf-8")).get("operaciones", {})
        except json.JSONDecodeError as exc:
            raise ValueError(f"{self.ruta} está dañado ({exc}); revísalo antes de continuar.") from exc

    def _escribir(self, operaciones: dict) -> None:
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        temporal = self.ruta.with_suffix(".tmp")
        temporal.write_text(json.dumps({"operaciones": operaciones}, indent=2, ensure_ascii=False), encoding="utf-8")
        os.replace(temporal, self.ruta)

    def obtener(self, operacion_id: str) -> Optional[dict]:
        return self._leer().get(str(operacion_id))

    def guardar(self, operacion_id: str, **campos) -> dict:
        """Crea o actualiza la entrada (mezcla `campos` con lo que ya tenía) y la devuelve."""
        operaciones = self._leer()
        entrada = operaciones.get(str(operacion_id), {"operacion_id": str(operacion_id),
                                                       "creada": datetime.now().isoformat(timespec="seconds")})
        entrada.update(campos)
        entrada["actualizada"] = datetime.now().isoformat(timespec="seconds")
        operaciones[str(operacion_id)] = entrada
        self._escribir(operaciones)
        return entrada

    def listar(self, estados=None) -> list:
        """Entradas (más recientes primero), opcionalmente solo las de `estados`."""
        entradas = sorted(self._leer().values(), key=lambda e: e.get("actualizada", ""), reverse=True)
        return [e for e in entradas if estados is None or e.get("estado") in estados]

    def pendientes(self) -> list:
        return self.listar(RETOMABLES)

    def eliminar(self, operacion_id: str) -> None:
        operaciones = self._leer()
        if operaciones.pop(str(operacion_id), None) is not None:
            self._escribir(operaciones)
