import threading
import tkinter as tk
from tkinter import ttk

from utils.progress import Progress


class ProgressUI:
    """
    Ventana de avance durante una ronda: muestra la fase y el paso actual, un registro
    con cada paso (los tests los reportan vía utils/progress.py) y, al terminar, un
    mensaje de confirmación o de error. `worker` se ejecuta en un hilo aparte.
    """

    POLL_MS = 300

    def __init__(self, config: dict, ronda: int, worker):
        self.worker = worker
        self.worker_error = None
        self.offset = 0
        self.hubo_error = False

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

        title = tk.Frame(self.root, bg=ACCENT, pady=14)
        title.pack(fill="x")
        tk.Label(
            title, text="Ejecutando…", font=("Segoe UI", 13, "bold"),
            bg=ACCENT, fg="white", anchor="w"
        ).pack(fill="x", padx=20)
        self.title_label = title.winfo_children()[0]

        if config.get("agencia_label"):
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

        self.banner = tk.Label(self.root, text="", font=("Segoe UI", 10, "bold"), bg=BG, anchor="w")
        self.banner.pack(fill="x", padx=20)

        btns = tk.Frame(self.root, bg=BG, pady=12)
        btns.pack(fill="x")
        self.continuar = tk.Button(
            btns, text="Ver resultados", font=("Segoe UI", 10, "bold"), bg=ACCENT, fg="white",
            activebackground="#0d47a1", activeforeground="white", relief="flat",
            padx=16, pady=8, state="disabled", command=self.root.destroy
        )
        self.continuar.pack()

    def _agregar(self, evento: dict):
        nivel = evento.get("nivel", "info")
        msg = evento.get("msg", "")
        if nivel == "fase":
            self.fase_var.set(msg)
        elif nivel == "info":
            self.paso_var.set(f"Paso actual: {msg}")
        elif nivel == "error":
            self.hubo_error = True
        icono = {"ok": "✔ ", "error": "✖ ", "fase": "▶ "}.get(nivel, "· ")
        self.log.configure(state="normal")
        self.log.insert("end", f"{evento.get('hora', '')}  {icono}{msg}\n", nivel)
        self.log.see("end")
        self.log.configure(state="disabled")

    def _poll(self):
        eventos, self.offset = Progress.read_from(self.offset)
        for e in eventos:
            self._agregar(e)

        if self.thread.is_alive():
            self.root.after(self.POLL_MS, self._poll)
        else:
            self._terminar()

    def _terminar(self):
        eventos, self.offset = Progress.read_from(self.offset)
        for e in eventos:
            self._agregar(e)

        self.bar.stop()
        self.bar.configure(mode="determinate", value=100)
        if self.worker_error:
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
