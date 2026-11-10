import tkinter as tk
from tkinter import ttk

from insumos.pendientes import ESPERANDO_QA
from ui.history_ui import open_history_dialog
from ui.recetas_ui import PanelEsperandoQA, fijar_colaborador

# Estado del slot -> (texto, etiqueta de color) en la tabla. Esperando QA no es un fallo ni un éxito.
ESTADOS_TABLA = {
    "exitosa": ("✔ Exitosa", "ok"),
    ESPERANDO_QA: ("⏸ Esperando QA", "qa"),
    "pendiente": ("✖ Pendiente", "pend"),
}


def contar_estados(slots: dict) -> dict:
    """Totales de la corrida: las operaciones en pausa de QA no cuentan como pendientes (no se reintentan)."""
    todos = [s for v in slots.values() for s in v]
    ok = sum(1 for s in todos if s["estado"] == "exitosa")
    qa = sum(1 for s in todos if s["estado"] == ESPERANDO_QA)
    return {"total": len(todos), "ok": ok, "qa": qa, "pendientes": len(todos) - ok - qa}


class ResultsUI:
    """
    Pantalla de estado al final de una corrida: una fila por venta solicitada
    (CF/CN) con su estado, intentos y último resultado. Devuelve la acción
    elegida por el usuario: "retry", "new" o "close".
    """

    def __init__(self, config: dict, slots: dict, ronda: int):
        self.action = "close"
        self.slots = slots
        fijar_colaborador(config)  # lo necesita la receta al continuar tras la pausa de QA

        BG = "#f5f5f5"
        ACCENT = "#1565C0"
        FONT_LABEL = ("Segoe UI", 10)
        FONT_BTN = ("Segoe UI", 10, "bold")

        self.root = tk.Tk()
        self.root.title("Providigital — Resultado de la ejecución")
        self.root.configure(bg=BG)
        self.root.protocol("WM_DELETE_WINDOW", self._close)

        width, height = 860, 560 if contar_estados(slots)["qa"] else 460
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - width) // 2
        y = (self.root.winfo_screenheight() - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

        title = tk.Frame(self.root, bg=ACCENT, pady=14)
        title.pack(fill="x")
        tk.Label(
            title, text="Resultado de la ejecución", font=("Segoe UI", 13, "bold"),
            bg=ACCENT, fg="white", anchor="w"
        ).pack(fill="x", padx=20)

        if config.get("ventas_batches"):
            agencias = sorted({b["agencia_label"] for b in config["ventas_batches"]})
            self.encabezado = f"{len(config['ventas_batches'])} lote(s) de venta · {', '.join(agencias)}"
        elif config.get("agencia_label"):
            self.encabezado = f"{config['agencia_label']}  ·  {config.get('metodo_entrega', '')}"
        elif config.get("agencias"):
            self.encabezado = f"{len(config['agencias'])} agencia(s) nueva(s)"
        else:
            self.encabezado = f"{len(config.get('ofertas', []))} oferta(s)"
        self.ronda = ronda

        self.info_label = tk.Label(self.root, font=FONT_LABEL, bg=BG, anchor="w")
        self.info_label.pack(fill="x", padx=20, pady=(12, 2))
        self.banner_label = tk.Label(self.root, font=("Segoe UI", 10, "bold"), bg=BG, anchor="w")
        self.banner_label.pack(fill="x", padx=20, pady=(0, 6))

        # Las operaciones en pausa de QA no son un fallo: su botón retoma la receta (ver ui/recetas_ui.py).
        self.panel_qa = PanelEsperandoQA(self.root, slots, al_cambiar=self._refrescar)
        self.panel_qa.frame.pack(fill="x", padx=20, pady=(0, 6))

        cols = ("tipo", "venta", "estado", "intentos", "detalle")
        self.tree = ttk.Treeview(self.root, columns=cols, show="headings", height=10)
        for col, text, w in [
            ("tipo", "Tipo", 60), ("venta", "Venta", 70), ("estado", "Estado", 110),
            ("intentos", "Intentos", 70), ("detalle", "Último resultado", 400),
        ]:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=w, anchor="w")
        self.tree.tag_configure("ok", foreground="#2e7d32")
        self.tree.tag_configure("pend", foreground="#c62828")
        self.tree.tag_configure("qa", foreground="#8d6e00")
        self.tree.pack(fill="both", expand=True, padx=20, pady=6)

        btns = tk.Frame(self.root, bg=BG, pady=12)
        btns.pack(fill="x")
        inner = tk.Frame(btns, bg=BG)
        inner.pack()

        retry = tk.Button(
            inner, font=FONT_BTN,
            bg=ACCENT, fg="white", activebackground="#0d47a1", activeforeground="white",
            relief="flat", padx=16, pady=8, cursor="hand2",
            command=lambda: self._finish("retry"),
        )
        retry.pack(side="left", padx=6)
        self.retry = retry
        self._refrescar()
        tk.Button(
            inner, text="📋 Historial", font=FONT_BTN, relief="flat", bg="#e0e0e0",
            padx=16, pady=8, cursor="hand2", command=lambda: open_history_dialog(self.root)
        ).pack(side="left", padx=6)
        tk.Button(
            inner, text="Nueva configuración", font=FONT_BTN, relief="flat", bg="#e0e0e0",
            padx=16, pady=8, cursor="hand2", command=lambda: self._finish("new")
        ).pack(side="left", padx=6)
        tk.Button(
            inner, text="Cerrar", font=FONT_BTN, relief="flat", bg="#e0e0e0",
            padx=16, pady=8, cursor="hand2", command=self._close
        ).pack(side="left", padx=6)

    def _refrescar(self):
        """Repinta contadores, banner, tabla y botón de reintento (al abrir y tras confirmar una pausa de QA)."""
        c = contar_estados(self.slots)
        self.info_label.configure(
            text=f"{self.encabezado}  ·  Ronda {self.ronda}  ·  {c['ok']} de {c['total']} exitosas"
                 + (f"  ·  {c['qa']} esperando QA" if c["qa"] else "")
        )
        if c["pendientes"]:
            banner, color = f"✖ {c['pendientes']} operación(es) pendiente(s) o con error.", "#c62828"
        elif c["qa"]:
            banner, color = f"⏸ {c['qa']} operación(es) esperando a QA; el resto se completó.", "#8d6e00"
        else:
            banner, color = "✔ Todas las operaciones se completaron correctamente.", "#2e7d32"
        self.banner_label.configure(text=banner, fg=color)

        self.tree.delete(*self.tree.get_children())
        for tipo in ("OF", "CF", "CN", "AGENCIA"):
            for i, slot in enumerate(self.slots.get(tipo, []), start=1):
                texto, tag = ESTADOS_TABLA.get(slot["estado"], ESTADOS_TABLA["pendiente"])
                self.tree.insert(
                    "", "end",
                    values=(tipo, f"{i} de {len(self.slots[tipo])}", texto, slot["intentos"], slot["detalle"]),
                    tags=(tag,),
                )
        self.retry.configure(
            text=f"↻  Reintentar pendientes ({c['pendientes']})",
            state="normal" if c["pendientes"] else "disabled",
        )

    def _finish(self, action: str):
        self.action = action
        self.root.destroy()

    def _close(self):
        self._finish("close")

    def run(self) -> str:
        self.root.mainloop()
        return self.action
