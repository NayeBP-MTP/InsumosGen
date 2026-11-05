import re
import threading
import tkinter as tk
from tkinter import messagebox, ttk

from utils.progress import Progress

# Los tests emiten el resultado de cada operación con un mensaje que incluye
# "{ciclo}/{total}" (p. ej. "Venta CF 3/10 finalizada", "Oferta 2/5 ... FALLÓ: ...").
# Ese patrón, junto con el nivel ok/error, distingue el resultado de una operación
# de otros eventos de nivel error (p. ej. no poder borrar una oferta huérfana).
_PATRON_CICLO = re.compile(r"\b\d+/\d+\b")


class ProgressUI:
    """
    Ventana de avance durante una ronda: muestra la fase y el paso actual, un registro
    con cada paso (los tests los reportan vía utils/progress.py) y, al terminar, un
    mensaje de confirmación o de error. `worker` se ejecuta en un hilo aparte.
    """

    POLL_MS = 300

    def __init__(self, config: dict, ronda: int, worker, slots: dict = None, controller=None):
        self.worker = worker
        self.worker_error = None
        self.offset = 0
        self.hubo_error = False
        self.slots = slots or {}
        self.controller = controller
        self.abortando = False
        self.total_resumen = sum(len(v) for v in self.slots.values())
        # Las ya exitosas vienen de rondas anteriores (un reintento solo repite las
        # pendientes); las fallidas de esta ronda se cuentan en vivo desde los eventos.
        self.exitosas_resumen = sum(
            1 for lista in self.slots.values() for s in lista if s.get("estado") == "exitosa"
        )
        self.fallidas_resumen = 0

        BG = "#f5f5f5"
        ACCENT = "#1565C0"
        self.root = tk.Tk()
        self.root.title("Providigital — Ejecución en curso")
        self.root.configure(bg=BG)
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)  # solo se cierra al terminar

        width, height = 760, 520
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - width) // 2
        y = (self.root.winfo_screenheight() - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.minsize(560, 380)

        title = tk.Frame(self.root, bg=ACCENT, pady=14)
        title.pack(fill="x")
        tk.Label(
            title, text="Ejecutando…", font=("Segoe UI", 13, "bold"),
            bg=ACCENT, fg="white", anchor="w"
        ).pack(fill="x", padx=20)
        self.title_label = title.winfo_children()[0]

        if config.get("ventas_batches"):
            agencias = sorted({b["agencia_label"] for b in config["ventas_batches"]})
            total_lotes = len(config["ventas_batches"])
            subtitulo = (
                f"{total_lotes} lote(s) de venta · {', '.join(agencias)}  ·  Ronda {ronda}"
            )
        elif config.get("agencia_label"):
            subtitulo = f"{config['agencia_label']}  ·  {config.get('metodo_entrega', '')}  ·  Ronda {ronda}"
        elif config.get("agencias"):
            subtitulo = f"{len(config['agencias'])} agencia(s) nueva(s)  ·  Ronda {ronda}"
        else:
            ofertas = config.get("ofertas", [])
            subtitulo = f"{len(ofertas)} oferta(s)  ·  Ronda {ronda}"
        tk.Label(
            self.root,
            text=subtitulo,
            font=("Segoe UI", 10), bg=BG, anchor="w"
        ).pack(fill="x", padx=20, pady=(12, 2))

        resumen = tk.Frame(self.root, bg=BG)
        resumen.pack(fill="x", padx=20, pady=(2, 8))
        self.resumen_vars = {}
        resumen_spec = [
            ("total", "Total", "#333"),
            ("faltantes", "Faltantes", "#f9a825"),
            ("exitosas", "Exitosas", "#2e7d32"),
            ("fallidas", "Fallidas", "#c62828"),
        ]
        for i, (clave, etiqueta, color) in enumerate(resumen_spec):
            celda = tk.Frame(resumen, bg=BG)
            celda.grid(row=0, column=i, sticky="w", padx=(0 if i == 0 else 24, 0))
            var = tk.StringVar(value="0")
            tk.Label(
                celda, textvariable=var, font=("Segoe UI", 16, "bold"), bg=BG, fg=color
            ).pack(anchor="w")
            tk.Label(
                celda, text=etiqueta, font=("Segoe UI", 9), bg=BG, fg="#777"
            ).pack(anchor="w")
            self.resumen_vars[clave] = var
        self._actualizar_resumen()

        self.fase_var = tk.StringVar(value="Preparando…")
        tk.Label(
            self.root, textvariable=self.fase_var, font=("Segoe UI", 11, "bold"),
            bg=BG, anchor="w"
        ).pack(fill="x", padx=20)

        self.paso_var = tk.StringVar(value="")
        tk.Label(
            self.root, textvariable=self.paso_var, font=("Segoe UI", 10),
            bg=BG, fg="#555", anchor="w", wraplength=700, justify="left"
        ).pack(fill="x", padx=20, pady=(2, 8))

        self.bar = ttk.Progressbar(self.root, mode="indeterminate")
        self.bar.pack(fill="x", padx=20)
        self.bar.start(12)

        # Botones y banner se empacan con side="bottom" ANTES que el log (que es el
        # único con expand=True): así quedan fijos al fondo de la ventana y siempre
        # visibles, y es el log el que se encoge si la ventana se achica — antes,
        # al estar packed después del frame expandible, se podían salir de la vista.
        btns = tk.Frame(self.root, bg=BG, pady=12)
        btns.pack(side="bottom")
        self.continuar = tk.Button(
            btns, text="Ver resultados", font=("Segoe UI", 10, "bold"), bg=ACCENT, fg="white",
            activebackground="#0d47a1", activeforeground="white", relief="flat",
            padx=16, pady=8, state="disabled", command=self.root.destroy
        )
        self.continuar.pack(side="left", padx=(0, 10))

        self.abortar = tk.Button(
            btns, text="Abortar", font=("Segoe UI", 10, "bold"), bg="#c62828", fg="white",
            activebackground="#8e0000", activeforeground="white", relief="flat",
            padx=16, pady=8, state="normal" if self.controller else "disabled",
            command=self._pedir_abortar,
        )
        self.abortar.pack(side="left")

        self.banner = tk.Label(self.root, text="", font=("Segoe UI", 10, "bold"), bg=BG, anchor="w")
        self.banner.pack(side="bottom", fill="x", padx=20)

        frame = tk.Frame(self.root, bg=BG)
        frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.log = tk.Text(
            frame, font=("Consolas", 9), state="disabled", wrap="word", bg="white", relief="flat"
        )
        scroll = ttk.Scrollbar(frame, orient="vertical", command=self.log.yview)
        self.log.configure(yscrollcommand=scroll.set)
        self.log.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.log.tag_configure("info", foreground="#333")
        self.log.tag_configure("fase", foreground=ACCENT, font=("Consolas", 9, "bold"))
        self.log.tag_configure("ok", foreground="#2e7d32", font=("Consolas", 9, "bold"))
        self.log.tag_configure("error", foreground="#c62828", font=("Consolas", 9, "bold"))

    def _pedir_abortar(self) -> None:
        if not self.controller or self.abortando:
            return
        if not messagebox.askyesno(
            "Abortar ejecución",
            "¿Abortar la ejecución en curso? El ciclo actual se interrumpe de inmediato "
            "y no se reintenta automáticamente; podrás revisar qué quedó pendiente en "
            "la pantalla de resultados.",
            parent=self.root,
        ):
            return
        self.abortando = True
        self.abortar.configure(state="disabled", text="Abortando…")
        self.fase_var.set("Abortando…")
        self.controller.abort()

    def _actualizar_resumen(self):
        faltantes = self.total_resumen - self.exitosas_resumen - self.fallidas_resumen
        self.resumen_vars["total"].set(str(self.total_resumen))
        self.resumen_vars["faltantes"].set(str(max(faltantes, 0)))
        self.resumen_vars["exitosas"].set(str(self.exitosas_resumen))
        self.resumen_vars["fallidas"].set(str(self.fallidas_resumen))

    def _agregar(self, evento: dict):
        nivel = evento.get("nivel", "info")
        msg = evento.get("msg", "")
        # Con varios lotes/agencias corriendo en paralelo, esta etiqueta dice de
        # cuál viene el evento (ver PROVIDIGITAL_RUN_TAG en run.py) — sin ella,
        # "Paso actual" se confundía entre los pasos de ventas distintas.
        tag = evento.get("worker")
        tag_prefix = f"[{tag}] " if tag else ""
        if nivel == "fase":
            self.fase_var.set(f"{tag_prefix}{msg}")
        elif nivel == "info":
            self.paso_var.set(f"Paso actual: {tag_prefix}{msg}")
        elif nivel == "error":
            self.hubo_error = True

        # Resultado de una operación individual (venta/oferta/agencia), no
        # cualquier evento ok/error (p. ej. limpieza de ofertas huérfanas).
        if nivel in ("ok", "error") and _PATRON_CICLO.search(msg):
            if nivel == "ok":
                self.exitosas_resumen += 1
            else:
                self.fallidas_resumen += 1

        icono = {"ok": "✔ ", "error": "✖ ", "fase": "▶ "}.get(nivel, "· ")
        self.log.configure(state="normal")
        self.log.insert("end", f"{evento.get('hora', '')}  {icono}{tag_prefix}{msg}\n", nivel)
        self.log.see("end")
        self.log.configure(state="disabled")

    def _poll(self):
        eventos, self.offset = Progress.read_from(self.offset)
        for e in eventos:
            self._agregar(e)
        self._actualizar_resumen()

        if self.thread.is_alive():
            self.root.after(self.POLL_MS, self._poll)
        else:
            self._terminar()

    def _terminar(self):
        eventos, self.offset = Progress.read_from(self.offset)
        for e in eventos:
            self._agregar(e)
        self._actualizar_resumen()

        self.bar.stop()
        self.bar.configure(mode="determinate", value=100)
        if self.abortando:
            self.hubo_error = True
            self.title_label.configure(text="Ejecución abortada")
            self.banner.configure(
                text="✖ Abortada por el usuario. Revisa qué quedó pendiente en los resultados.",
                fg="#c62828",
            )
        elif self.worker_error:
            self.hubo_error = True
            self.title_label.configure(text="La ejecución terminó con un error")
            self.banner.configure(text=f"✖ Error inesperado: {self.worker_error}", fg="#c62828")
        elif self.hubo_error:
            self.title_label.configure(text="Ejecución terminada con errores")
            self.banner.configure(
                text="✖ Hubo pasos con error. Revisa el registro y los resultados.", fg="#c62828"
            )
        else:
            self.title_label.configure(text="Ejecución terminada")
            self.banner.configure(text="✔ Todo se completó correctamente.", fg="#2e7d32")
        self.fase_var.set("Finalizado")
        self.paso_var.set("")
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)
        self.abortar.configure(state="disabled")
        self.continuar.configure(state="normal")

    def _run_worker(self):
        try:
            self.worker()
        except Exception as exc:  # se muestra en la ventana en lugar de perderse en el hilo
            self.worker_error = str(exc)

    def run(self):
        self.thread = threading.Thread(target=self._run_worker, daemon=True)
        self.thread.start()
        self.root.after(self.POLL_MS, self._poll)
        self.root.mainloop()
