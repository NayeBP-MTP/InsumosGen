import tkinter as tk
from tkinter import ttk

from ui.history_ui import open_history_dialog


class ResultsUI:
    """
    Pantalla de estado al final de una corrida: una fila por venta solicitada
    (CF/CN) con su estado, intentos y último resultado. Devuelve la acción
    elegida por el usuario: "retry", "new" o "close".
    """

    def __init__(self, config: dict, slots: dict, ronda: int):
        self.action = "close"
        self.slots = slots

        BG = "#f5f5f5"
        ACCENT = "#1565C0"
        FONT_LABEL = ("Segoe UI", 10)
        FONT_BTN = ("Segoe UI", 10, "bold")

        self.root = tk.Tk()
        self.root.title("Providigital — Resultado de la ejecución")
        self.root.configure(bg=BG)
        self.root.protocol("WM_DELETE_WINDOW", self._close)

        width, height = 860, 460
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

        total = sum(len(v) for v in slots.values())
        ok = sum(1 for v in slots.values() for s in v if s["estado"] == "exitosa")
        pendientes = total - ok

        if config.get("agencia_label"):
            encabezado = f"{config['agencia_label']}  ·  {config.get('metodo_entrega', '')}"
        elif config.get("agencias"):
            encabezado = f"{len(config['agencias'])} agencia(s) nueva(s)"
        else:
            encabezado = f"{len(config.get('ofertas', []))} oferta(s)"
        info = f"{encabezado}  ·  Ronda {ronda}  ·  {ok} de {total} exitosas"
        tk.Label(self.root, text=info, font=FONT_LABEL, bg=BG, anchor="w").pack(
            fill="x", padx=20, pady=(12, 2)
        )
        if pendientes:
            banner, color = f"✖ {pendientes} operación(es) pendiente(s) o con error.", "#c62828"
        else:
            banner, color = "✔ Todas las operaciones se completaron correctamente.", "#2e7d32"
        tk.Label(
            self.root, text=banner, font=("Segoe UI", 10, "bold"), bg=BG, fg=color, anchor="w"
        ).pack(fill="x", padx=20, pady=(0, 6))

        cols = ("tipo", "venta", "estado", "intentos", "detalle")
        tree = ttk.Treeview(self.root, columns=cols, show="headings", height=10)
        for col, text, w in [
            ("tipo", "Tipo", 60), ("venta", "Venta", 70), ("estado", "Estado", 110),
            ("intentos", "Intentos", 70), ("detalle", "Último resultado", 400),
        ]:
            tree.heading(col, text=text)
            tree.column(col, width=w, anchor="w")
        tree.tag_configure("ok", foreground="#2e7d32")
        tree.tag_configure("pend", foreground="#c62828")

        for tipo in ("OF", "CF", "CN", "AGENCIA"):
            for i, slot in enumerate(slots.get(tipo, []), start=1):
                exitosa = slot["estado"] == "exitosa"
                tree.insert(
                    "", "end",
                    values=(
                        tipo, f"{i} de {len(slots[tipo])}",
                        "✔ Exitosa" if exitosa else "✖ Pendiente",
                        slot["intentos"], slot["detalle"],
                    ),
                    tags=("ok" if exitosa else "pend",),
                )
        tree.pack(fill="both", expand=True, padx=20, pady=6)

        btns = tk.Frame(self.root, bg=BG, pady=12)
        btns.pack(fill="x")
        inner = tk.Frame(btns, bg=BG)
        inner.pack()

        retry = tk.Button(
            inner, text=f"↻  Reintentar pendientes ({pendientes})", font=FONT_BTN,
            bg=ACCENT, fg="white", activebackground="#0d47a1", activeforeground="white",
            relief="flat", padx=16, pady=8, cursor="hand2",
            command=lambda: self._finish("retry"),
            state="normal" if pendientes else "disabled",
        )
        retry.pack(side="left", padx=6)
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

    def _finish(self, action: str):
        self.action = action
        self.root.destroy()

    def _close(self):
        self._finish("close")

    def run(self) -> str:
        self.root.mainloop()
        return self.action
