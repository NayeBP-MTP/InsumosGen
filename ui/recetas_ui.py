"""
Recetas de insumo en la UI: elegir la receta de un lote, confirmar la pausa de QA y retomar operaciones
pendientes. La lógica (sin Tk) vive en funciones sueltas para probarla sin abrir ventanas; los widgets
solo la llaman.
"""
import json
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Optional

from config.settings import Settings
from insumos.pendientes import COMPLETADA, EN_CURSO, ESPERANDO_QA, FALLIDA, PendientesStore
from insumos.recetas import RECETAS
from insumos.runner import RunnerRecetas

SIN_RECETA = "Sin receta"
USER_SETTINGS_PATH = Path("data/user_settings.json")

CONTINUAR, REANUDAR, DESHACER = "continuar", "reanudar", "deshacer"
ETIQUETA_ACCION = {
    CONTINUAR: "Continuar (QA confirmó)",
    REANUDAR: "Reanudar",
    DESHACER: "Deshacer",
}
ETIQUETA_ESTADO = {
    ESPERANDO_QA: "⏸ Esperando QA",
    EN_CURSO: "▶ En curso",
    FALLIDA: "✖ Fallida",
}


# ---------- lógica (sin Tk) ----------

def etiquetas_recetas(tipo: str, con_sin_receta: bool = False) -> list:
    """
    Opciones del desplegable de un lote "Registrar Cliente": las recetas de ese tipo de venta (la receta es
    obligatoria). Con `con_sin_receta` antepone 'Sin receta'.
    """
    nombres = [r.nombre for r in RECETAS.values() if r.tipo_venta == tipo]
    return ([SIN_RECETA] if con_sin_receta else []) + nombres


def receta_id_de_etiqueta(tipo: str, etiqueta: str) -> Optional[str]:
    """Id de la receta elegida, o None si es 'Sin receta' (o si la etiqueta no es de ese tipo)."""
    for receta in RECETAS.values():
        if receta.tipo_venta == tipo and receta.nombre == etiqueta:
            return receta.id
    return None


def fijar_colaborador(config: Optional[dict] = None, ajustes: Path = USER_SETTINGS_PATH) -> None:
    """
    El número de colaborador arma el número de cliente (CREAR_ID_CLIENTE). Sale de la corrida (`config`) o,
    si no hay, de los ajustes de usuario; así retomar una operación funciona sin haber armado una corrida.
    """
    colaborador = (config or {}).get("numero_colaborador")
    if not colaborador and Path(ajustes).exists():
        try:
            colaborador = json.loads(Path(ajustes).read_text(encoding="utf-8")).get("numero_colaborador")
        except (json.JSONDecodeError, OSError):
            colaborador = None
    if colaborador:
        Settings.NUMERO_COLABORADOR = colaborador


def filas_en_pausa(slots: dict, pendientes: Optional[PendientesStore] = None) -> list:
    """Una fila por slot en pausa de QA, con lo que QA necesita (contrato y fecha de nacimiento)."""
    pendientes = pendientes or PendientesStore()
    filas = []
    for tipo in ("CF", "CN"):
        for slot in slots.get(tipo, []):
            if slot["estado"] != ESPERANDO_QA:
                continue
            contrato = (slot.get("venta") or {}).get("numero_contrato")
            para_qa = (pendientes.obtener(contrato) or {}).get("para_qa") or {}
            filas.append({
                "slot": slot, "tipo": tipo, "contrato": contrato,
                "fecha_nacimiento": para_qa.get("fecha_nacimiento", ""),
                "nombre_cliente": para_qa.get("nombre_cliente", ""),
            })
    return filas


def confirmar_qa(slot: dict, runner: Optional[RunnerRecetas] = None,
                 pendientes: Optional[PendientesStore] = None) -> None:
    """
    QA confirmó: retoma la receta del slot desde el paso siguiente a la pausa y actualiza `estado` y `detalle`
    (`exitosa` o `fallida`; si falla, el reintento de `run.py` solo repite la receta). Si la operación ya se
    completó por otro lado (p. ej. `python -m insumos continuar`) solo sincroniza el slot.
    """
    contrato = slot["venta"]["numero_contrato"]
    nombre = RECETAS[slot["config"]["receta"]].nombre
    entrada = (pendientes or PendientesStore()).obtener(contrato)
    if entrada and entrada["estado"] == COMPLETADA:
        slot["estado"], slot["detalle"] = "exitosa", f"contrato {contrato} · receta {nombre}"
        return
    resultado = (runner or RunnerRecetas()).continuar_tras_qa(contrato)
    if resultado.estado == "completada":
        slot["estado"], slot["detalle"] = "exitosa", f"contrato {contrato} · receta {nombre}"
    else:
        slot["estado"] = "fallida"
        slot["detalle"] = f"Receta {resultado.receta} falló en {resultado.modulo_fallido}: {resultado.error}"[:200]


def acciones_de(entrada: dict) -> list:
    """Qué se puede hacer con una operación pendiente: en pausa, continuar; a medias, reanudar; siempre, deshacer."""
    primera = CONTINUAR if entrada["estado"] == ESPERANDO_QA else REANUDAR
    return [primera, DESHACER]


def ejecutar_accion(accion: str, operacion_id: str, runner: Optional[RunnerRecetas] = None) -> tuple:
    """Corre la acción sobre la operación y devuelve (ok, mensaje) para mostrarle al usuario."""
    runner = runner or RunnerRecetas()
    if accion == DESHACER:
        r = runner.deshacer(operacion_id)
        mensaje = f"Se revirtieron {len(r.deshechas)} escritura(s) del contrato {operacion_id}."
        if r.conflictos:
            return False, (mensaje + " Hay conflictos (la BD cambió después de que escribiera el módulo) y no "
                           "se pisaron; revísalos a mano.")
        return True, mensaje
    r = runner.continuar_tras_qa(operacion_id) if accion == CONTINUAR else runner.reanudar(operacion_id)
    if r.estado == "completada":
        return True, f"Receta {r.receta} completada para el contrato {operacion_id}."
    if r.estado == ESPERANDO_QA:
        return True, f"Receta {r.receta}: sigue en pausa de QA (contrato {operacion_id})."
    return False, f"Receta {r.receta} falló en {r.modulo_fallido}: {r.error}"


def describir_pendiente(entrada: dict) -> str:
    """Detalle de una fila: lo que QA necesita, el paso en que quedó o el error."""
    if entrada["estado"] == ESPERANDO_QA:
        qa = entrada.get("para_qa") or {}
        return f"Fecha de nacimiento {qa.get('fecha_nacimiento', '?')}"
    partes = [f"paso {entrada['paso_actual']}" if entrada.get("paso_actual") else None, entrada.get("error")]
    return " · ".join(p for p in partes if p)


# ---------- widgets ----------

class PanelEsperandoQA:
    """
    Panel de ResultsUI con una fila por operación en pausa de QA: contrato y fecha de nacimiento (lo que QA
    debe usar para registrar al usuario) y el botón que retoma la receta. Al confirmar, `al_cambiar` avisa a
    la pantalla para que refresque sus contadores.
    """

    BG = "#fff8e1"

    def __init__(self, parent: tk.Misc, slots: dict, al_cambiar, runner: Optional[RunnerRecetas] = None):
        self.slots, self.al_cambiar, self.runner = slots, al_cambiar, runner
        # Contenedor siempre empacado por quien lo usa: sin filas en pausa queda vacío (sin alto).
        self.frame = tk.Frame(parent)
        self.render()

    def render(self) -> None:
        for hijo in self.frame.winfo_children():
            hijo.destroy()
        filas = filas_en_pausa(self.slots)
        if not filas:
            return
        caja = tk.LabelFrame(
            self.frame, text=" Esperando QA ", font=("Segoe UI", 10, "bold"), bg=self.BG, fg="#8d6e00",
            padx=10, pady=6,
        )
        caja.pack(fill="x")
        tk.Label(
            caja, bg=self.BG, anchor="w", justify="left", font=("Segoe UI", 9),
            text="QA debe registrar al usuario con el contrato y la fecha de nacimiento. Cuando lo haga, confirma aquí.",
        ).pack(fill="x")
        for fila in filas:
            linea = tk.Frame(caja, bg=self.BG)
            linea.pack(fill="x", pady=2)
            tk.Label(
                linea, bg=self.BG, anchor="w", font=("Segoe UI", 10),
                text=f"{fila['tipo']} · contrato {fila['contrato']} · nacimiento {fila['fecha_nacimiento'] or '?'}",
            ).pack(side="left")
            tk.Button(
                linea, text="QA confirmó, continuar", font=("Segoe UI", 9, "bold"), bg="#1565C0", fg="white",
                activebackground="#0d47a1", activeforeground="white", relief="flat", padx=10, pady=2,
                cursor="hand2", command=lambda f=fila: self._confirmar(f),
            ).pack(side="right")

    def _confirmar(self, fila: dict) -> None:
        self.frame.winfo_toplevel().configure(cursor="watch")
        self.frame.update_idletasks()
        try:
            confirmar_qa(fila["slot"], runner=self.runner)
        except Exception as exc:  # la pausa se conserva; se muestra el motivo en vez de perderlo
            messagebox.showerror("No se pudo continuar", f"Contrato {fila['contrato']}:\n{exc}", parent=self.frame)
        finally:
            self.frame.winfo_toplevel().configure(cursor="")
        self.render()
        self.al_cambiar()


class RetomarUI:
    """
    Aviso al abrir `run.py` con operaciones sin terminar (en pausa de QA, a medias o fallidas): permite
    continuarlas, reanudarlas o deshacerlas antes de armar una corrida nueva.
    """

    def __init__(self, pendientes: Optional[PendientesStore] = None, runner: Optional[RunnerRecetas] = None):
        self.store, self.runner = pendientes or PendientesStore(), runner
        BG, ACCENT = "#f5f5f5", "#1565C0"

        self.root = tk.Tk()
        self.root.title("Providigital — Operaciones pendientes")
        self.root.configure(bg=BG)
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)
        ancho, alto = 820, 400
        self.root.update_idletasks()
        x, y = (self.root.winfo_screenwidth() - ancho) // 2, (self.root.winfo_screenheight() - alto) // 2
        self.root.geometry(f"{ancho}x{alto}+{x}+{y}")

        titulo = tk.Frame(self.root, bg=ACCENT, pady=14)
        titulo.pack(fill="x")
        tk.Label(titulo, text="Operaciones pendientes de insumo", font=("Segoe UI", 13, "bold"),
                 bg=ACCENT, fg="white", anchor="w").pack(fill="x", padx=20)
        self.aviso = tk.Label(self.root, bg=BG, anchor="w", justify="left", font=("Segoe UI", 10), wraplength=770)
        self.aviso.pack(fill="x", padx=20, pady=(12, 6))

        cols = ("contrato", "receta", "estado", "detalle")
        self.tree = ttk.Treeview(self.root, columns=cols, show="headings", height=8, selectmode="browse")
        for col, texto, ancho_col in [("contrato", "Contrato", 90), ("receta", "Receta", 200),
                                       ("estado", "Estado", 140), ("detalle", "Detalle", 320)]:
            self.tree.heading(col, text=texto)
            self.tree.column(col, width=ancho_col, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=20, pady=6)
        self.tree.bind("<<TreeviewSelect>>", lambda _e: self._actualizar_botones())

        botones = tk.Frame(self.root, bg=BG, pady=12)
        botones.pack()
        self.botones = {}
        for accion, color in ((CONTINUAR, ACCENT), (REANUDAR, ACCENT), (DESHACER, "#c62828")):
            self.botones[accion] = tk.Button(
                botones, text=ETIQUETA_ACCION[accion], font=("Segoe UI", 10, "bold"), bg=color, fg="white",
                disabledforeground="white", activebackground="#0d47a1", activeforeground="white",
                relief="flat", padx=14, pady=8, command=lambda a=accion: self._ejecutar(a),
            )
            self.botones[accion].pack(side="left", padx=6)
        tk.Button(botones, text="Seguir a una corrida nueva", font=("Segoe UI", 10, "bold"), bg="#e0e0e0",
                  relief="flat", padx=14, pady=8, command=self.root.destroy).pack(side="left", padx=6)

        self.entradas = {}
        self.refrescar()

    def refrescar(self) -> None:
        self.entradas = {e["operacion_id"]: e for e in self.store.pendientes()}
        self.tree.delete(*self.tree.get_children())
        for contrato, e in self.entradas.items():
            self.tree.insert("", "end", iid=contrato, values=(
                contrato, e.get("receta", ""), ETIQUETA_ESTADO.get(e["estado"], e["estado"]), describir_pendiente(e)))
        if not self.entradas:
            self.root.destroy()
            return
        self.aviso.configure(
            text=f"Hay {len(self.entradas)} operación(es) sin terminar de corridas anteriores. Elige una para "
                 "continuarla, reanudarla o deshacerla; o sigue a una corrida nueva (quedan pendientes).")
        self._actualizar_botones()

    def _seleccion(self) -> Optional[dict]:
        elegido = self.tree.selection()
        return self.entradas.get(elegido[0]) if elegido else None

    def _actualizar_botones(self) -> None:
        entrada = self._seleccion()
        habilitadas = acciones_de(entrada) if entrada else []
        for accion, boton in self.botones.items():
            boton.configure(state="normal" if accion in habilitadas else "disabled",
                            bg="#90a4ae" if accion not in habilitadas else ("#c62828" if accion == DESHACER else "#1565C0"))

    def _ejecutar(self, accion: str) -> None:
        entrada = self._seleccion()
        if not entrada:
            return
        contrato = entrada["operacion_id"]
        if accion == DESHACER and not messagebox.askyesno(
            "Deshacer", f"¿Revertir lo que la receta escribió en la BD para el contrato {contrato}?", parent=self.root
        ):
            return
        fijar_colaborador()
        self.root.configure(cursor="watch")
        self.root.update_idletasks()
        try:
            ok, mensaje = ejecutar_accion(accion, contrato, runner=self.runner)
        except Exception as exc:
            ok, mensaje = False, str(exc)
        finally:
            self.root.configure(cursor="")
        (messagebox.showinfo if ok else messagebox.showerror)(ETIQUETA_ACCION[accion], mensaje, parent=self.root)
        if self.root.winfo_exists():
            self.refrescar()

    def run(self) -> None:
        self.root.mainloop()


def retomar_pendientes(pendientes: Optional[PendientesStore] = None) -> None:
    """Abre `RetomarUI` solo si hay operaciones sin terminar."""
    pendientes = pendientes or PendientesStore()
    try:
        hay = bool(pendientes.pendientes())
    except ValueError as exc:  # archivo dañado: se avisa y la corrida nueva sigue siendo posible
        print(f"Aviso: no se pudieron leer las operaciones pendientes: {exc}")
        return
    if hay:
        RetomarUI(pendientes).run()
