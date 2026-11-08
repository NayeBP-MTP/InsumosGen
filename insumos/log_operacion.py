"""Log por operación: qué escribió cada módulo (host, tabla, llave, valor anterior)."""
import json
from datetime import datetime
from pathlib import Path
from typing import Iterator, Optional

DIRECTORIO_DEFAULT = Path("data/insumos")


class LogOperacion:
    """
    Un archivo JSON por línea por operación (`<operacion_id>.jsonl`). Registrar no toca la BD.
    Entradas: marcas de módulo (`modulo_iniciado` / `modulo_completado`, para reanudar) y
    escrituras (`insert` / `update` / `delete`, para deshacer en orden inverso).
    """

    def __init__(self, operacion_id: str, directorio: Optional[Path] = None):
        self.operacion_id = str(operacion_id)
        self.ruta = Path(directorio or DIRECTORIO_DEFAULT) / f"{self.operacion_id}.jsonl"

    def _anotar(self, entrada: dict) -> None:
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        entrada = {"ts": datetime.now().isoformat(timespec="milliseconds"), **entrada}
        with self.ruta.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entrada, ensure_ascii=False, default=str) + "\n")

    def modulo_iniciado(self, modulo: str) -> None:
        self._anotar({"tipo": "modulo_iniciado", "modulo": modulo})

    def modulo_completado(self, modulo: str) -> None:
        self._anotar({"tipo": "modulo_completado", "modulo": modulo})

    def escritura(self, modulo: str, accion: str, host: str, tabla: str, llave: dict,
                  anterior: Optional[dict] = None, nuevo: Optional[dict] = None) -> None:
        """`accion`: insert | update | delete. `anterior` solo en update/delete; `nuevo` en insert/update."""
        if accion not in ("insert", "update", "delete"):
            raise ValueError(f"accion desconocida: {accion!r}")
        self._anotar({
            "tipo": accion, "modulo": modulo, "host": host, "tabla": tabla,
            "llave": llave, "anterior": anterior, "nuevo": nuevo,
        })

    def deshecho(self) -> None:
        """Marca que la operación se deshizo: lo anterior ya no cuenta para reanudar ni para deshacer."""
        self._anotar({"tipo": "deshecho"})

    def entradas(self) -> list:
        """Todo el historial del archivo (no se borra nunca)."""
        if not self.ruta.exists():
            return []
        with self.ruta.open(encoding="utf-8") as f:
            return [json.loads(linea) for linea in f if linea.strip()]

    def vigentes(self) -> list:
        """Entradas posteriores a la última marca `deshecho`: lo que sigue en pie en la BD."""
        entradas = self.entradas()
        for i in range(len(entradas) - 1, -1, -1):
            if entradas[i]["tipo"] == "deshecho":
                return entradas[i + 1:]
        return entradas

    def modulos_completados(self) -> list:
        """Nombres de módulos terminados, en orden (la receta se reanuda en el primero que falte)."""
        return [e["modulo"] for e in self.vigentes() if e["tipo"] == "modulo_completado"]

    def escrituras_para_deshacer(self) -> Iterator[dict]:
        """Escrituras vigentes en orden inverso al que ocurrieron."""
        return reversed([e for e in self.vigentes() if e["tipo"] in ("insert", "update", "delete")])
