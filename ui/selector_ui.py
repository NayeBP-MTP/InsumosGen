import json
import math
import re
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config.settings import Settings
from config.sucursales import SUCURSALES, get_sucursal_by_nombre
from ui.history_ui import open_history_dialog
from utils.catalog_db import CatalogDB
from utils.vpn_check import verificar_vpn


RUN_CONFIG_PATH = Path("data/run_config.json")
INSUMOS = [
    ("OF", "Oferta (solo inserción en BD)"),
    ("VENTA", "Venta (CN / CF)"),
    ("AGENCIA", "Nueva estructura de agencia"),
]
MODO_CREAR_NUEVO = "nuevo"
MODO_REUSAR = "reusar"
NIVELES_PRECIO = [
    ("", "Ninguno"),
    ("N1", "N1"),
    ("N2", "N2"),
    ("N3", "N3"),
    ("PP20", "PP20"),
    ("PP25", "PP25"),
]
INSUMO_PLACEHOLDER = "Selecciona una opción"
USER_SETTINGS_PATH = Path("data/user_settings.json")
DEFAULT_CELULAR = "5513096751"
DEFAULT_CORREO = "luis.andrade@mtpinternational.mx"
EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class SelectorUI:

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Providigital — Configuración de Ejecución")
        self.root.resizable(False, False)
        self._icon_img = self._make_snowflake_icon()
        self.root.iconphoto(True, self._icon_img)

        self.agencias = CatalogDB.get_agencias()
        self.metodos = CatalogDB.get_metodos_entrega()

        self.agencia_var = tk.StringVar()
        self.metodo_var = tk.StringVar()
        self.insumo_var = tk.StringVar()  # código: OF / VENTA
        self.insumo_label_var = tk.StringVar(value=INSUMO_PLACEHOLDER)

        # Oferta: lista de filas independientes (agencia + tipo + nivel por fila,
        # ver _agregar_fila_oferta). Venta: cantidad por tipo (CF y CN). Agencia:
        # lista de filas independientes (sucursal + modo por fila, ver
        # _agregar_fila_agencia) — cada fila crea su propio DM/AM si elige "nuevo".
        self.ofertas_rows = []
        self.agencias_rows = []
        self._combos_cache = {}  # branch -> lista de combos DM/AM ya consultados
        self.cantidad_vars = {"CF": tk.IntVar(value=0), "CN": tk.IntVar(value=0)}
        self.con_seguro_var = tk.StringVar(value="si")  # "si" / "no"
        self.tomar_capturas_var = tk.BooleanVar(value=True)

        self.user_settings = self._load_user_settings()
        self.celular_var = tk.StringVar(value=self.user_settings.get("celular", DEFAULT_CELULAR))
        self.correo_var = tk.StringVar(value=self.user_settings.get("correo", DEFAULT_CORREO))

        self.confirmed = False

        self._build_ui()
        self._agregar_fila_oferta()
        self._agregar_fila_agencia()
        self._lock_window_size()

    @staticmethod
    def _load_user_settings() -> dict:
        if USER_SETTINGS_PATH.exists():
            try:
                return json.loads(USER_SETTINGS_PATH.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                return {}
        return {}

    def _save_user_settings(self):
        USER_SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
        USER_SETTINGS_PATH.write_text(
            json.dumps(self.user_settings, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

    @staticmethod
    def _add_tooltip(widget, text: str):
        tooltip = {"win": None}

        def _show(_event):
            x = widget.winfo_rootx()
            y = widget.winfo_rooty() + widget.winfo_height() + 4
            win = tk.Toplevel(widget)
            win.wm_overrideredirect(True)
            win.wm_geometry(f"+{x}+{y}")
            tk.Label(
                win, text=text, font=("Segoe UI", 9), bg="#333333", fg="white",
                padx=8, pady=3
            ).pack()
            tooltip["win"] = win

        def _hide(_event):
            if tooltip["win"] is not None:
                tooltip["win"].destroy()
                tooltip["win"] = None

        widget.bind("<Enter>", _show)
        widget.bind("<Leave>", _hide)

    @staticmethod
    def _make_snowflake_icon(size: int = 32, bg: str = "#1565C0", fg: str = "#ffffff") -> tk.PhotoImage:
        img = tk.PhotoImage(width=size, height=size)
        img.put(bg, to=(0, 0, size, size))
        cx = cy = (size - 1) / 2
        radius = size * 0.42

        def set_px(x, y):
            xi, yi = int(round(x)), int(round(y))
            if 0 <= xi < size and 0 <= yi < size:
                img.put(fg, (xi, yi))

        for i in range(6):
            angle = i * math.pi / 3
            dx, dy = math.cos(angle), math.sin(angle)
            for t in range(int(radius) + 1):
                set_px(cx + dx * t, cy + dy * t)
            for frac in (0.55, 0.85):
                bx = cx + dx * radius * frac
                by = cy + dy * radius * frac
                pdx, pdy = -dy, dx
                tick_len = radius * 0.18
                for s in range(-int(tick_len), int(tick_len) + 1):
                    set_px(bx + pdx * s * 0.3, by + pdy * s * 0.3)
        return img

    def _lock_window_size(self, width: int = 600):
        """Mide el estado con más contenido (panel de venta) y fija ese alto para
        toda la navegación, evitando que la ventana crezca/encoja entre pasos."""
        self.root.update_idletasks()
        heights = [self.root.winfo_reqheight()]

        self.title_label.pack_forget()
        self.step1_frame.pack_forget()
        self.step2_header.pack(fill="x")
        for panel in (self.panel_oferta, self.panel_venta, self.panel_agencia):
            panel.pack(fill="x")
            self.root.update_idletasks()
            heights.append(self.root.winfo_reqheight())
            panel.pack_forget()
        self.step2_header.pack_forget()

        self.title_label.pack(fill="x")
        self.step1_frame.pack(fill="x")

        self._fixed_height = max(heights)
        self._center_window(width, self._fixed_height)

    def _center_window(self, width: int, height: int = None):
        self.root.update_idletasks()
        if height is None:
            height = self.root.winfo_reqheight()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - width) // 2
        y = (sh - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _build_ui(self):
        BG = "#f5f5f5"
        ACCENT = "#1565C0"
        FONT_LABEL = ("Segoe UI", 10)
        FONT_TITLE = ("Segoe UI", 13, "bold")
        FONT_BTN = ("Segoe UI", 10, "bold")
        self._FONT_LABEL = FONT_LABEL
        self._FONT_BTN = FONT_BTN
        self._BG = BG

        self.root.configure(bg=BG)

        # ── Título ──────────────────────────────────────────────
        self.title_frame = tk.Frame(self.root, bg=ACCENT, pady=14)
        self.title_frame.pack(fill="x")
        self.title_frame.grid_columnconfigure(0, weight=1)

        self.title_left = tk.Frame(self.title_frame, bg=ACCENT)
        self.title_left.grid(row=0, column=0, sticky="ew", padx=(20, 10))

        self.title_label = tk.Label(
            self.title_left,
            text="Automatización - Provident UAT",
            font=FONT_TITLE,
            bg=ACCENT,
            fg="white",
            anchor="w"
        )
        self.title_label.pack(fill="x")

        # ── Encabezado del paso 2 (dentro de la barra azul) ─────
        self.step2_header = tk.Frame(self.title_left, bg=ACCENT)

        self.back_btn = tk.Button(
            self.step2_header,
            text="◀",
            font=("Segoe UI", 11, "bold"),
            bg="#0d47a1",
            fg="white",
            activebackground="#0a3a75",
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=8,
            pady=2,
            cursor="hand2",
            command=self._volver_al_menu
        )
        self.back_btn.pack(side="left", padx=(0, 12))

        self.step2_title = tk.Label(
            self.step2_header, text="", font=("Segoe UI", 15, "bold"), bg=ACCENT, fg="white", anchor="w"
        )
        self.step2_title.pack(side="left", fill="x", expand=True)

        ajustes_btn = tk.Button(
            self.title_frame,
            text="⚙",
            font=("Segoe UI", 15),
            bg=ACCENT,
            fg="white",
            activebackground="#0d47a1",
            activeforeground="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self._open_settings_dialog
        )
        ajustes_btn.grid(row=0, column=2, sticky="e", padx=(0, 15))
        self._add_tooltip(ajustes_btn, "Ajustes")

        historial_btn = tk.Button(
            self.title_frame,
            text="📋",
            font=("Segoe UI", 15),
            bg=ACCENT,
            fg="white",
            activebackground="#0d47a1",
            activeforeground="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=lambda: open_history_dialog(self.root)
        )
        historial_btn.grid(row=0, column=1, sticky="e", padx=(0, 10))
        self._add_tooltip(historial_btn, "Historial")

        # ── Paso 1: tipo de insumo ──────────────────────────────
        form = tk.Frame(self.root, bg=BG, padx=40, pady=12)
        form.pack(fill="x")

        self.step1_frame = tk.Frame(form, bg=BG)
        self.step1_frame.pack(fill="x")

        tk.Label(
            self.step1_frame, text="¿Qué deseas realizar?", font=FONT_TITLE, bg=BG, anchor="w"
        ).pack(fill="x", pady=(0, 6))
        self.insumo_combo = ttk.Combobox(
            self.step1_frame, textvariable=self.insumo_label_var,
            values=[texto for _, texto in INSUMOS], state="readonly", width=40
        )
        self.insumo_combo.pack(fill="x", pady=(0, 12))
        self.insumo_combo.bind("<<ComboboxSelected>>", lambda _e: self._on_insumo_changed())

        # ── Paso 2a: opciones de Oferta (lista de filas independientes) ──
        self.panel_oferta = tk.Frame(form, bg=BG)

        OFERTAS_CANVAS_HEIGHT = 300
        ofertas_scroll_area = tk.Frame(self.panel_oferta, bg=BG)
        ofertas_scroll_area.pack(fill="x")

        self.ofertas_canvas = tk.Canvas(
            ofertas_scroll_area, bg=BG, highlightthickness=0, height=OFERTAS_CANVAS_HEIGHT
        )
        ofertas_scrollbar = ttk.Scrollbar(
            ofertas_scroll_area, orient="vertical", command=self.ofertas_canvas.yview
        )
        self.ofertas_canvas.configure(yscrollcommand=ofertas_scrollbar.set)
        self.ofertas_canvas.pack(side="left", fill="both", expand=True)
        ofertas_scrollbar.pack(side="right", fill="y")

        self.ofertas_list_frame = tk.Frame(self.ofertas_canvas, bg=BG)
        self._ofertas_canvas_window = self.ofertas_canvas.create_window(
            (0, 0), window=self.ofertas_list_frame, anchor="nw"
        )

        def _actualizar_scrollregion(_e=None):
            self.ofertas_canvas.configure(scrollregion=self.ofertas_canvas.bbox("all"))

        def _ajustar_ancho_interno(event):
            self.ofertas_canvas.itemconfig(self._ofertas_canvas_window, width=event.width)

        self.ofertas_list_frame.bind("<Configure>", _actualizar_scrollregion)
        self.ofertas_canvas.bind("<Configure>", _ajustar_ancho_interno)

        def _on_mousewheel(event):
            self.ofertas_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.ofertas_canvas.bind("<Enter>", lambda _e: self.ofertas_canvas.bind_all("<MouseWheel>", _on_mousewheel))
        self.ofertas_canvas.bind("<Leave>", lambda _e: self.ofertas_canvas.unbind_all("<MouseWheel>"))

        tk.Button(
            self.panel_oferta,
            text="+ Agregar oferta",
            font=FONT_LABEL,
            bg="#e0e0e0",
            relief="flat",
            cursor="hand2",
            command=self._agregar_fila_oferta
        ).pack(anchor="w", pady=(8, 10))

        # ── Paso 2b: opciones de Venta ───────────────────────────
        self.panel_venta = tk.Frame(form, bg=BG)

        tk.Label(
            self.panel_venta, text="Ventas a realizar:", font=FONT_LABEL, bg=BG, anchor="w"
        ).grid(row=0, column=0, sticky="w", pady=(0, 4))
        cantidades_frame = tk.Frame(self.panel_venta, bg=BG)
        cantidades_frame.grid(row=1, column=0, sticky="w", pady=(0, 10))
        for fila, (tipo, texto) in enumerate(
            [("CF", "Cliente frecuente (CF)"), ("CN", "Cliente nuevo (CN)")]
        ):
            tk.Label(
                cantidades_frame, text=texto, font=FONT_LABEL, bg=BG, width=22, anchor="w"
            ).grid(row=fila, column=0, sticky="w", pady=2)
            tk.Button(
                cantidades_frame, text="−", font=FONT_BTN, width=2, relief="flat", bg="#e0e0e0",
                command=lambda t=tipo: self._cambiar_cantidad_venta(t, -1)
            ).grid(row=fila, column=1)
            tk.Label(
                cantidades_frame, textvariable=self.cantidad_vars[tipo],
                font=("Segoe UI", 11, "bold"), bg=BG, width=4
            ).grid(row=fila, column=2)
            tk.Button(
                cantidades_frame, text="+", font=FONT_BTN, width=2, relief="flat", bg="#e0e0e0",
                command=lambda t=tipo: self._cambiar_cantidad_venta(t, 1)
            ).grid(row=fila, column=3)

        tk.Label(self.panel_venta, text="¿Con seguro?", font=FONT_LABEL, bg=BG, anchor="w").grid(
            row=2, column=0, sticky="w", pady=(0, 4)
        )
        seguro_frame = tk.Frame(self.panel_venta, bg=BG)
        seguro_frame.grid(row=3, column=0, sticky="w", pady=(0, 10))
        tk.Radiobutton(
            seguro_frame, text="Con seguro", value="si", variable=self.con_seguro_var,
            font=FONT_LABEL, bg=BG, activebackground=BG, cursor="hand2"
        ).pack(side="left", padx=(0, 16))
        tk.Radiobutton(
            seguro_frame, text="Sin seguro", value="no", variable=self.con_seguro_var,
            font=FONT_LABEL, bg=BG, activebackground=BG, cursor="hand2"
        ).pack(side="left")

        tk.Label(self.panel_venta, text="Agencia:", font=FONT_LABEL, bg=BG, anchor="w").grid(
            row=4, column=0, sticky="w", pady=(0, 4)
        )
        self.agencia_combo_venta = ttk.Combobox(
            self.panel_venta, textvariable=self.agencia_var,
            values=[ag["label"] for ag in self.agencias], state="readonly", width=38
        )
        self.agencia_combo_venta.grid(row=5, column=0, sticky="ew", pady=(0, 10))

        tk.Label(self.panel_venta, text="Método de entrega:", font=FONT_LABEL, bg=BG, anchor="w").grid(
            row=6, column=0, sticky="w", pady=(0, 4)
        )
        self.metodo_combo = ttk.Combobox(
            self.panel_venta, textvariable=self.metodo_var,
            values=[m["nombre"] for m in self.metodos], state="readonly", width=38
        )
        self.metodo_combo.grid(row=7, column=0, sticky="ew", pady=(0, 10))

        tk.Label(self.panel_venta, text="Número de celular:", font=FONT_LABEL, bg=BG, anchor="w").grid(
            row=8, column=0, sticky="w", pady=(0, 4)
        )
        tk.Entry(
            self.panel_venta, textvariable=self.celular_var, font=FONT_LABEL, width=40
        ).grid(row=9, column=0, sticky="ew", pady=(0, 10))

        tk.Label(self.panel_venta, text="Correo electrónico:", font=FONT_LABEL, bg=BG, anchor="w").grid(
            row=10, column=0, sticky="w", pady=(0, 4)
        )
        tk.Entry(
            self.panel_venta, textvariable=self.correo_var, font=FONT_LABEL, width=40
        ).grid(row=11, column=0, sticky="ew", pady=(0, 4))

        tk.Checkbutton(
            self.panel_venta,
            text="Tomar capturas paso a paso de la venta",
            variable=self.tomar_capturas_var,
            font=FONT_LABEL,
            bg=BG,
            activebackground=BG,
            cursor="hand2"
        ).grid(row=12, column=0, sticky="w", pady=(6, 0))

        # ── Paso 2c: opciones de Nueva estructura de agencia ──────
        self.panel_agencia = tk.Frame(form, bg=BG)

        AGENCIAS_CANVAS_HEIGHT = 300
        agencias_scroll_area = tk.Frame(self.panel_agencia, bg=BG)
        agencias_scroll_area.pack(fill="x")

        self.agencias_canvas = tk.Canvas(
            agencias_scroll_area, bg=BG, highlightthickness=0, height=AGENCIAS_CANVAS_HEIGHT
        )
        agencias_scrollbar = ttk.Scrollbar(
            agencias_scroll_area, orient="vertical", command=self.agencias_canvas.yview
        )
        self.agencias_canvas.configure(yscrollcommand=agencias_scrollbar.set)
        self.agencias_canvas.pack(side="left", fill="both", expand=True)
        agencias_scrollbar.pack(side="right", fill="y")

        self.agencias_list_frame = tk.Frame(self.agencias_canvas, bg=BG)
        self._agencias_canvas_window = self.agencias_canvas.create_window(
            (0, 0), window=self.agencias_list_frame, anchor="nw"
        )

        def _actualizar_scrollregion_agencias(_e=None):
            self.agencias_canvas.configure(scrollregion=self.agencias_canvas.bbox("all"))

        def _ajustar_ancho_interno_agencias(event):
            self.agencias_canvas.itemconfig(self._agencias_canvas_window, width=event.width)

        self.agencias_list_frame.bind("<Configure>", _actualizar_scrollregion_agencias)
        self.agencias_canvas.bind("<Configure>", _ajustar_ancho_interno_agencias)

        def _on_mousewheel_agencias(event):
            self.agencias_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.agencias_canvas.bind(
            "<Enter>", lambda _e: self.agencias_canvas.bind_all("<MouseWheel>", _on_mousewheel_agencias)
        )
        self.agencias_canvas.bind("<Leave>", lambda _e: self.agencias_canvas.unbind_all("<MouseWheel>"))

        tk.Button(
            self.panel_agencia,
            text="+ Agregar agencia",
            font=FONT_LABEL,
            bg="#e0e0e0",
            relief="flat",
            cursor="hand2",
            command=self._agregar_fila_agencia
        ).pack(anchor="w", pady=(8, 10))

        # ── Botón Iniciar ────────────────────────────────────────
        btn_frame = tk.Frame(self.root, bg=BG)
        btn_frame.pack(fill="x", side="bottom", pady=(6, 20))

        self.confirm_btn = tk.Button(
            btn_frame,
            text="Elige un insumo para continuar",
            font=FONT_BTN,
            bg=ACCENT,
            fg="white",
            activebackground="#0d47a1",
            activeforeground="white",
            disabledforeground="white",
            relief="flat",
            padx=20,
            pady=8,
            cursor="hand2",
            state="disabled",
            command=self._on_confirm
        )
        self.confirm_btn.pack()

    def _cambiar_cantidad_venta(self, tipo: str, delta: int):
        var = self.cantidad_vars[tipo]
        var.set(max(0, min(50, var.get() + delta)))

    def _agregar_fila_oferta(self):
        self.ofertas_rows.append({
            "agencia_var": tk.StringVar(),
            "tipo_var": tk.StringVar(value="AGREGAR"),
            "nivel_var": tk.StringVar(value=""),
            "nivel_label_var": tk.StringVar(value="Ninguno"),
        })
        self._renderizar_filas_oferta()

    def _quitar_fila_oferta(self, row: dict):
        if len(self.ofertas_rows) <= 1:
            return
        self.ofertas_rows.remove(row)
        self._renderizar_filas_oferta()

    def _actualizar_aviso_fila_oferta(self, row: dict):
        aviso = row.get("aviso_label")
        if aviso is None:
            return
        agencia_label = row["agencia_var"].get()
        nivel = row["nivel_var"].get()
        if nivel and agencia_label and not Settings.agencia_es_unbundling(agencia_label):
            aviso.configure(
                text=(
                    f"⚠ '{agencia_label}' no está en la lista de sucursales Unbundling: "
                    f"según la regla de negocio, no debería llevar nivel {nivel}."
                )
            )
        else:
            aviso.configure(text="")

    def _renderizar_filas_oferta(self):
        FONT_LABEL = self._FONT_LABEL
        CARD_BG = "#ffffff"
        for child in self.ofertas_list_frame.winfo_children():
            child.destroy()

        for idx, row in enumerate(self.ofertas_rows, start=1):
            card = tk.Frame(self.ofertas_list_frame, bg=CARD_BG, relief="groove", bd=1)
            card.pack(fill="x", pady=(0, 10))
            inner = tk.Frame(card, bg=CARD_BG, padx=12, pady=10)
            inner.pack(fill="x")

            header = tk.Frame(inner, bg=CARD_BG)
            header.pack(fill="x", pady=(0, 8))
            tk.Label(
                header, text=f"Oferta {idx}", font=("Segoe UI", 10, "bold"), bg=CARD_BG
            ).pack(side="left")
            if len(self.ofertas_rows) > 1:
                tk.Button(
                    header, text="✕ Quitar", font=("Segoe UI", 8), bg=CARD_BG, fg="#c62828",
                    relief="flat", cursor="hand2",
                    command=lambda r=row: self._quitar_fila_oferta(r)
                ).pack(side="right")

            tk.Label(inner, text="Agencia:", font=FONT_LABEL, bg=CARD_BG, anchor="w").pack(fill="x")
            agencia_combo = ttk.Combobox(
                inner, textvariable=row["agencia_var"],
                values=[ag["label"] for ag in self.agencias], state="readonly"
            )
            agencia_combo.pack(fill="x", pady=(2, 8))

            tk.Label(inner, text="Tipo de oferta:", font=FONT_LABEL, bg=CARD_BG, anchor="w").pack(fill="x")
            tipo_frame = tk.Frame(inner, bg=CARD_BG)
            tipo_frame.pack(fill="x", pady=(2, 8))
            tk.Radiobutton(
                tipo_frame, text="Agregar", value="AGREGAR", variable=row["tipo_var"],
                font=FONT_LABEL, bg=CARD_BG, activebackground=CARD_BG, cursor="hand2"
            ).pack(side="left", padx=(0, 16))
            tk.Radiobutton(
                tipo_frame, text="Refin", value="REFIN", variable=row["tipo_var"],
                font=FONT_LABEL, bg=CARD_BG, activebackground=CARD_BG, cursor="hand2"
            ).pack(side="left")

            tk.Label(
                inner, text="Nivel de precio / promoción:", font=FONT_LABEL, bg=CARD_BG, anchor="w"
            ).pack(fill="x")
            nivel_combo = ttk.Combobox(
                inner, textvariable=row["nivel_label_var"],
                values=[texto for _, texto in NIVELES_PRECIO], state="readonly", width=20
            )
            nivel_combo.pack(anchor="w", pady=(2, 4))

            aviso = tk.Label(
                inner, text="", font=("Segoe UI", 8), bg=CARD_BG, fg="#c62828",
                wraplength=460, justify="left", anchor="w"
            )
            aviso.pack(fill="x")
            row["aviso_label"] = aviso

            def _on_fila_changed(_e=None, r=row):
                codigo = next(
                    c for c, texto in NIVELES_PRECIO if texto == r["nivel_label_var"].get()
                )
                r["nivel_var"].set(codigo)
                self._actualizar_aviso_fila_oferta(r)

            agencia_combo.bind("<<ComboboxSelected>>", _on_fila_changed)
            nivel_combo.bind("<<ComboboxSelected>>", _on_fila_changed)

        # El Canvas de ofertas tiene alto fijo (OFERTAS_CANVAS_HEIGHT) y hace scroll
        # internamente, así que agregar/quitar filas ya no cambia el tamaño de la ventana.

    def _agregar_fila_agencia(self):
        self.agencias_rows.append({
            "sucursal_var": tk.StringVar(value=SUCURSALES[0]["nombre"]),
            "modo_var": tk.StringVar(value=MODO_CREAR_NUEVO),
            "combo_label_var": tk.StringVar(value=""),
            "combo": None,
        })
        self._renderizar_filas_agencia()

    def _quitar_fila_agencia(self, row: dict):
        if len(self.agencias_rows) <= 1:
            return
        self.agencias_rows.remove(row)
        self._renderizar_filas_agencia()

    def _combos_de_sucursal(self, nombre_sucursal: str) -> list:
        """Combos DM/AM existentes para esa sucursal, consultados en vivo a
        Challenger_uat (se cachean en memoria mientras dura la ventana). Devuelve
        lista vacía (sin lanzar) si no hay conexión — el usuario puede seguir
        creando un DM/AM nuevo."""
        sucursal = get_sucursal_by_nombre(nombre_sucursal)
        branch = sucursal["branch"]
        if branch in self._combos_cache:
            return self._combos_cache[branch]
        try:
            from services.agency_repository import ChallengerRepository
            combos = ChallengerRepository().get_dm_am_combos(branch)
        except Exception:
            combos = []
        self._combos_cache[branch] = combos
        return combos

    @staticmethod
    def _etiqueta_combo(combo: dict) -> str:
        return (
            f"{combo['dm_code']} ({combo['dm_name']}) · Sección {combo['section']} · "
            f"{combo['am_text']} ({combo['am_name']})"
        )

    def _renderizar_filas_agencia(self):
        FONT_LABEL = self._FONT_LABEL
        CARD_BG = "#ffffff"
        for child in self.agencias_list_frame.winfo_children():
            child.destroy()

        for idx, row in enumerate(self.agencias_rows, start=1):
            card = tk.Frame(self.agencias_list_frame, bg=CARD_BG, relief="groove", bd=1)
            card.pack(fill="x", pady=(0, 10))
            inner = tk.Frame(card, bg=CARD_BG, padx=12, pady=10)
            inner.pack(fill="x")

            header = tk.Frame(inner, bg=CARD_BG)
            header.pack(fill="x", pady=(0, 8))
            tk.Label(
                header, text=f"Agencia {idx}", font=("Segoe UI", 10, "bold"), bg=CARD_BG
            ).pack(side="left")
            if len(self.agencias_rows) > 1:
                tk.Button(
                    header, text="✕ Quitar", font=("Segoe UI", 8), bg=CARD_BG, fg="#c62828",
                    relief="flat", cursor="hand2",
                    command=lambda r=row: self._quitar_fila_agencia(r)
                ).pack(side="right")

            tk.Label(inner, text="Sucursal:", font=FONT_LABEL, bg=CARD_BG, anchor="w").pack(fill="x")
            sucursal_combo = ttk.Combobox(
                inner, textvariable=row["sucursal_var"],
                values=[s["nombre"] for s in SUCURSALES], state="readonly"
            )
            sucursal_combo.pack(fill="x", pady=(2, 8))

            tk.Label(inner, text="DM / AM:", font=FONT_LABEL, bg=CARD_BG, anchor="w").pack(fill="x")
            modo_frame = tk.Frame(inner, bg=CARD_BG)
            modo_frame.pack(fill="x", pady=(2, 8))
            modo_nuevo_rb = tk.Radiobutton(
                modo_frame, text="Crear equipo nuevo", value=MODO_CREAR_NUEVO, variable=row["modo_var"],
                font=FONT_LABEL, bg=CARD_BG, activebackground=CARD_BG, cursor="hand2"
            )
            modo_nuevo_rb.pack(side="left", padx=(0, 16))
            modo_reusar_rb = tk.Radiobutton(
                modo_frame, text="Reutilizar existente", value=MODO_REUSAR, variable=row["modo_var"],
                font=FONT_LABEL, bg=CARD_BG, activebackground=CARD_BG, cursor="hand2"
            )
            modo_reusar_rb.pack(side="left")

            combo_label = tk.Label(
                inner, text="Equipo (DM/AM) a reutilizar:", font=FONT_LABEL, bg=CARD_BG, anchor="w"
            )
            combo_combo = ttk.Combobox(
                inner, textvariable=row["combo_label_var"], values=[], state="readonly"
            )
            aviso = tk.Label(
                inner, text="", font=("Segoe UI", 8), bg=CARD_BG, fg="#c62828",
                wraplength=460, justify="left", anchor="w"
            )

            def _refrescar_combos(r=row, lbl=combo_label, cmb=combo_combo, av=aviso):
                if r["modo_var"].get() != MODO_REUSAR:
                    lbl.pack_forget()
                    cmb.pack_forget()
                    av.configure(text="")
                    av.pack_forget()
                    r["combo"] = None
                    return
                combos = self._combos_de_sucursal(r["sucursal_var"].get())
                etiquetas = [self._etiqueta_combo(c) for c in combos]
                lbl.pack(fill="x")
                cmb.configure(values=etiquetas)
                cmb.pack(fill="x", pady=(2, 4))
                if not combos:
                    av.configure(
                        text="No se encontró ningún equipo existente para esta sucursal "
                        "(o no hay conexión a Challenger_uat/VPN). Elige \"Crear equipo nuevo\"."
                    )
                    av.pack(fill="x")
                elif r["combo_label_var"].get() not in etiquetas:
                    r["combo_label_var"].set(etiquetas[0])
                    r["combo"] = combos[0]
                    av.configure(text="")
                    av.pack_forget()
                else:
                    av.configure(text="")
                    av.pack_forget()

            def _on_combo_elegido(_e=None, r=row):
                combos = self._combos_de_sucursal(r["sucursal_var"].get())
                etiquetas = [self._etiqueta_combo(c) for c in combos]
                if r["combo_label_var"].get() in etiquetas:
                    r["combo"] = combos[etiquetas.index(r["combo_label_var"].get())]

            def _on_sucursal_cambiada(_e=None, r=row, refrescar=_refrescar_combos):
                self._combos_cache.pop(get_sucursal_by_nombre(r["sucursal_var"].get())["branch"], None)
                refrescar()

            sucursal_combo.bind("<<ComboboxSelected>>", _on_sucursal_cambiada)
            modo_nuevo_rb.configure(command=_refrescar_combos)
            modo_reusar_rb.configure(command=_refrescar_combos)
            combo_combo.bind("<<ComboboxSelected>>", _on_combo_elegido)

            _refrescar_combos()

        # El Canvas de agencias tiene alto fijo (AGENCIAS_CANVAS_HEIGHT) y hace scroll
        # internamente, así que agregar/quitar filas ya no cambia el tamaño de la ventana.

    def _on_insumo_changed(self):
        insumo = next(c for c, texto in INSUMOS if texto == self.insumo_label_var.get())
        self.insumo_var.set(insumo)

        self.step1_frame.pack_forget()
        self.panel_oferta.pack_forget()
        self.panel_venta.pack_forget()
        self.panel_agencia.pack_forget()
        self.title_label.pack_forget()

        self.step2_header.pack(fill="x")

        if insumo == "OF":
            self.step2_title.configure(text="Ofertas")
            self.panel_oferta.pack(fill="x")
            self.confirm_btn.configure(text="▶  Insertar Oferta")
        elif insumo == "AGENCIA":
            self.step2_title.configure(text="Nueva estructura de agencia")
            self.panel_agencia.pack(fill="x")
            self.confirm_btn.configure(text="▶  Crear Agencia(s)")
        else:
            self.step2_title.configure(text="Ventas")
            self.panel_venta.pack(fill="x")
            self.confirm_btn.configure(text="▶  Crear Venta")
        self.confirm_btn.configure(state="normal")
        self._center_window(600, self._fixed_height)

    def _volver_al_menu(self):
        self.step2_header.pack_forget()
        self.panel_oferta.pack_forget()
        self.panel_venta.pack_forget()
        self.panel_agencia.pack_forget()

        self.insumo_var.set("")
        self.insumo_label_var.set(INSUMO_PLACEHOLDER)
        self.confirm_btn.configure(text="Elige un insumo para continuar", state="disabled")

        self.title_label.pack(fill="x")
        self.step1_frame.pack(fill="x")
        self._center_window(600, self._fixed_height)

    def _open_settings_dialog(self):
        BG = "#f5f5f5"
        ACCENT = "#1565C0"
        FONT_LABEL = ("Segoe UI", 10)
        FONT_TITLE = ("Segoe UI", 12, "bold")
        FONT_BTN = ("Segoe UI", 10, "bold")

        dialog = tk.Toplevel(self.root)
        dialog.title("Ajustes")
        dialog.resizable(False, False)
        dialog.configure(bg=BG)
        dialog.transient(self.root)
        dialog.grab_set()

        width, height = 380, 300
        self.root.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - width) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - height) // 2
        dialog.geometry(f"{width}x{height}+{x}+{y}")

        tk.Label(
            dialog, text="Ajustes de usuario (valores por defecto)", font=FONT_TITLE, bg=BG,
            wraplength=320
        ).pack(pady=(16, 10))

        form = tk.Frame(dialog, bg=BG, padx=30)
        form.pack(fill="both", expand=True)

        tk.Label(
            form, text="Número de celular:", font=FONT_LABEL, bg=BG, anchor="w"
        ).pack(fill="x")

        celular_entry = tk.Entry(form, font=FONT_LABEL, width=25)
        celular_entry.insert(0, self.celular_var.get())
        celular_entry.pack(fill="x", pady=(4, 10))

        tk.Label(
            form, text="Correo electrónico:", font=FONT_LABEL, bg=BG, anchor="w"
        ).pack(fill="x")

        correo_entry = tk.Entry(form, font=FONT_LABEL, width=25)
        correo_entry.insert(0, self.correo_var.get())
        correo_entry.pack(fill="x", pady=(4, 4))

        error_label = tk.Label(
            form, text="", font=("Segoe UI", 8), bg=BG, fg="#c62828", wraplength=300, justify="left"
        )
        error_label.pack(fill="x", pady=(4, 0))

        def _save():
            celular = celular_entry.get().strip()
            correo = correo_entry.get().strip()

            if not celular.isdigit() or len(celular) != 10:
                error_label.config(text="Ingresa un número de celular válido (10 dígitos).")
                return
            if not EMAIL_REGEX.match(correo):
                error_label.config(text="Ingresa un correo electrónico válido.")
                return

            self.celular_var.set(celular)
            self.correo_var.set(correo)
            self.user_settings["celular"] = celular
            self.user_settings["correo"] = correo
            self._save_user_settings()
            dialog.destroy()

        btn_frame = tk.Frame(dialog, bg=BG, pady=10)
        btn_frame.pack(fill="x")
        tk.Button(
            btn_frame,
            text="Guardar",
            font=FONT_BTN,
            bg=ACCENT,
            fg="white",
            activebackground="#0d47a1",
            activeforeground="white",
            relief="flat",
            padx=14,
            pady=6,
            cursor="hand2",
            command=_save
        ).pack()

        celular_entry.focus_set()
        dialog.wait_window()

    def _on_confirm(self):
        insumo = self.insumo_var.get()

        if not insumo:
            messagebox.showwarning("Campo requerido", "Debes elegir qué deseas realizar.")
            return

        if insumo == "OF":
            if not self.ofertas_rows:
                messagebox.showwarning("Campo requerido", "Agrega al menos una oferta.")
                return
            ofertas_cfg = []
            for idx, row in enumerate(self.ofertas_rows, start=1):
                agencia_label_fila = row["agencia_var"].get()
                if not agencia_label_fila:
                    messagebox.showwarning(
                        "Campo requerido", f"Selecciona la agencia de la oferta {idx}."
                    )
                    return
                ofertas_cfg.append({
                    "agencia_label": agencia_label_fila,
                    "tipo_oferta":   row["tipo_var"].get(),
                    "nivel_precio":  row["nivel_var"].get(),
                })
            ventas = {"OF": len(ofertas_cfg)}
        elif insumo == "AGENCIA":
            if not self.agencias_rows:
                messagebox.showwarning("Campo requerido", "Agrega al menos una agencia.")
                return
            agencias_cfg = []
            for idx, row in enumerate(self.agencias_rows, start=1):
                modo = row["modo_var"].get()
                if modo == MODO_REUSAR and not row.get("combo"):
                    messagebox.showwarning(
                        "Campo requerido",
                        f"Selecciona el equipo (DM/AM) a reutilizar en la agencia {idx}, "
                        "o cambia a \"Crear equipo nuevo\"."
                    )
                    return
                cfg = {"sucursal": row["sucursal_var"].get(), "modo": modo}
                if modo == MODO_REUSAR:
                    cfg["combo"] = row["combo"]
                agencias_cfg.append(cfg)
            ventas = {"AGENCIA": len(agencias_cfg)}
        else:
            agencia_label = self.agencia_var.get()
            if not agencia_label:
                messagebox.showwarning("Campo requerido", "Debes seleccionar una agencia.")
                return
            metodo = self.metodo_var.get()
            if not metodo:
                messagebox.showwarning("Campo requerido", "Debes seleccionar un método de entrega.")
                return
            ventas = {t: v.get() for t, v in self.cantidad_vars.items()}
            if sum(ventas.values()) < 1:
                messagebox.showwarning(
                    "Valor inválido", "Debes indicar al menos 1 venta (CF o CN)."
                )
                return
            celular = self.celular_var.get().strip()
            correo = self.correo_var.get().strip()
            if not celular.isdigit() or len(celular) != 10:
                messagebox.showwarning(
                    "Campo requerido", "Ingresa un número de celular válido (10 dígitos)."
                )
                return
            if not EMAIL_REGEX.match(correo):
                messagebox.showwarning(
                    "Campo requerido", "Ingresa un correo electrónico válido."
                )
                return
            con_seguro = self.con_seguro_var.get() == "si"
            tomar_capturas = self.tomar_capturas_var.get()

        # La ejecución requiere VPN de Provident (portal UAT, botDB y, para AGENCIA,
        # también Challenger_uat, solo accesibles con ella).
        self.root.configure(cursor="watch")
        self.confirm_btn.configure(state="disabled", text="Verificando VPN…")
        self.root.update_idletasks()
        try:
            vpn_ok, faltantes = verificar_vpn(requiere_bd=True, requiere_challenger=(insumo == "AGENCIA"))
        finally:
            self.root.configure(cursor="")
            self._on_insumo_changed()
        if not vpn_ok:
            messagebox.showerror(
                "Sin conexión a la VPN",
                "No se puede iniciar la ejecución porque no hay conexión a la VPN de Provident."
                "\n\nNo se pudo alcanzar:\n  • " + "\n  • ".join(faltantes) +
                "\n\nConéctate a la VPN e inténtalo de nuevo."
            )
            return

        if insumo == "OF":
            # Oferta no inicia sesión en el portal ni abre navegador: no requiere
            # agencia/credenciales únicas, cada fila ya trae su propia agencia.
            config = {
                "ventas":         ventas,
                "ofertas":        ofertas_cfg,
                "tomar_capturas": False,
            }
        elif insumo == "AGENCIA":
            # Igual que Oferta: no inicia sesión en el portal ni abre navegador.
            config = {
                "ventas":         ventas,
                "agencias":       agencias_cfg,
                "tomar_capturas": False,
            }
        else:
            agencia_data = CatalogDB.get_agencia_by_label(agencia_label)
            config = {
                "ventas":         ventas,
                "agencia_label":  agencia_label,
                "agencia":        agencia_data["agencia"],
                "focus_id":       agencia_data["focus_id"],
                "password":       agencia_data["password"],
                "metodo_entrega": metodo,
                "con_seguro":     con_seguro,
                "celular":        self.celular_var.get(),
                "correo":         self.correo_var.get(),
                "tomar_capturas": tomar_capturas
            }

        RUN_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        RUN_CONFIG_PATH.write_text(
            json.dumps(config, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

        self.confirmed = True
        self.root.destroy()

    def run(self) -> bool:
        self.root.mainloop()
        return self.confirmed
