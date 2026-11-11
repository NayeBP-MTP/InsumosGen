import json
import math
import re
import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from keyring.errors import KeyringError

from config.credentials import CredentialStore
from config.legacy_env import importar_env
from config.settings import Settings
from config.sucursales import SUCURSALES, get_sucursal_by_nombre
from services.connection_gate import HOSTS_ARRANQUE, HOSTS_BD, hosts_requeridos, hosts_sin_configurar, probar_hosts
from ui.conexiones_ui import open_connections_dialog
from ui.history_ui import open_history_dialog
from utils.catalog_db import CatalogDB
from utils.vpn_check import verificar_vpn
from utils.paths import app_data_dir


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUN_CONFIG_PATH = app_data_dir() / "run_config.json"
ENV_LEGADO = Path(__file__).resolve().parents[1] / ".env"
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
USER_SETTINGS_PATH = app_data_dir() / "user_settings.json"
DEFAULT_CELULAR = "5513096751"
DEFAULT_CORREO = "luis.andrade@mtpinternational.mx"
EMAIL_REGEX = re.compile(
    r"^[A-Za-z0-9]+([._%+-][A-Za-z0-9]+)*"       # parte local: sin puntos al borde ni dobles
    r"@([A-Za-z0-9]+(-[A-Za-z0-9]+)*\.)+[A-Za-z]{2,}$"  # dominio con TLD de 2+ letras
)


def correo_valido(correo: str) -> bool:
    """Checks básicos: sin espacios, un solo @, parte local/dominio bien formados y longitudes."""
    local, _, _dominio = correo.partition("@")
    return len(correo) <= 254 and len(local) <= 64 and bool(EMAIL_REGEX.match(correo))
NOMBRE_INE_REGEX = re.compile(r"^[A-ZÁÉÍÓÚÜÑ]+( [A-ZÁÉÍÓÚÜÑ]+)*$")
COLABORADOR_REGEX = re.compile(r"^[0-9]{2}$")
CELULAR_REGEX = re.compile(r"^[0-9]{10}$")
AJUSTES_INCOMPLETOS_TEXTO = "Completa los ajustes de usuario para continuar"


class SelectorUI:

    def __init__(self, config_path: Path = None):
        # run.py pasa su propia ruta (por PID) para que dos ventanas de
        # `python run.py` corriendo a la vez no se pisen el config una a la otra.
        # Sin ella (uso directo/pruebas), se usa la ruta fija de siempre.
        self.config_path = config_path or RUN_CONFIG_PATH

        self.root = tk.Tk()
        self.root.title("Providigital — Configuración de Ejecución")
        self.root.resizable(False, False)
        self._icon_img = self._make_snowflake_icon()
        self.root.iconphoto(True, self._icon_img)

        self.credenciales = CredentialStore()
        self.agencias = CatalogDB.get_agencias()
        self.metodos = CatalogDB.get_metodos_entrega()

        self.insumo_var = tk.StringVar()  # código: OF / VENTA
        self.insumo_label_var = tk.StringVar(value=INSUMO_PLACEHOLDER)

        # Oferta y Agencia: lista de filas independientes (ver _agregar_fila_oferta /
        # _agregar_fila_agencia). Venta: igual patrón — una lista de "lotes", cada uno
        # con su propia agencia/tipo(CF o CN)/método/seguro/cantidad (ver
        # _agregar_fila_venta), para poder combinar p. ej. 5 CN en Izcalli + 3 CF en
        # Tijuana en una sola corrida.
        self.ofertas_rows = []
        self.agencias_rows = []
        self.ventas_rows = []
        self._combos_cache = {}  # branch -> lista de combos DM/AM ya consultados
        self.tomar_capturas_var = tk.BooleanVar(value=False)
        self.navegador_var = tk.StringVar(value="visible")  # "visible" / "headless"

        self.user_settings = self._load_user_settings()
        self.celular_var = tk.StringVar(value=self.user_settings.get("celular", DEFAULT_CELULAR))
        self.correo_var = tk.StringVar(value=self.user_settings.get("correo", DEFAULT_CORREO))
        # Sin valor por defecto: el usuario debe capturarlos antes de poder operar.
        self.nombre_ine_var = tk.StringVar(value=self.user_settings.get("nombre_ine", ""))
        self.colaborador_var = tk.StringVar(value=self.user_settings.get("numero_colaborador", ""))

        self.confirmed = False

        self._build_ui()
        self._importar_env_legado()
        self._agregar_fila_oferta()
        self._agregar_fila_agencia()
        self._agregar_fila_venta()
        self._lock_window_size()
        self._actualizar_gate_ajustes()
        # Si falta algo obligatorio, abre las ventanas necesarias una tras otra (tras mostrar la ventana).
        if self._pasos_de_arranque():
            self.root.after(300, self._primer_arranque)

    def _conexiones_pendientes(self) -> list:
        """Hosts que toda corrida necesita y aún no están configurados (sin almacén seguro: todos)."""
        try:
            return hosts_sin_configurar(self.credenciales, HOSTS_ARRANQUE)
        except KeyringError:
            return list(HOSTS_ARRANQUE)

    def _pasos_de_arranque(self) -> list:
        """Ventanas que hay que abrir al iniciar, en este orden: 'conexiones' y después 'ajustes'."""
        pasos = []
        if self._conexiones_pendientes():
            pasos.append("conexiones")
        if not self._ajustes_completos()[0]:
            pasos.append("ajustes")
        return pasos

    def _primer_arranque(self):
        """Abre, una tras otra, las ventanas de lo que falta; el gate de la pantalla principal sigue bloqueado hasta completarlo."""
        for paso in self._pasos_de_arranque():
            if paso == "conexiones":
                open_connections_dialog(
                    self.root, self.credenciales, hosts=HOSTS_ARRANQUE,
                    mensaje="Para empezar necesitas la conexión a la base de datos de Pesos_Offer (botDB y "
                            "Originacion), que toda ejecución usa. Captúrala y pruébala; las demás "
                            "conexiones se te piden cuando una ejecución las necesite.",
                )
            else:
                self._open_settings_dialog()
        self._actualizar_gate_ajustes()

    def _abrir_conexiones(self):
        """Botón 🔌: abre todas las conexiones y refresca el gate (puede completar lo que faltaba)."""
        open_connections_dialog(self.root, self.credenciales)
        self._actualizar_gate_ajustes()

    @staticmethod
    def _estado_archivos() -> list:
        """Checks obligatorios de archivos: [(etiqueta, ok, detalle)]. Orden fijo: selfie, INE, comprobante, video."""
        def _lleno(ruta) -> bool:
            p = Path(ruta)
            return p.is_file() and p.stat().st_size > 0

        selfie = Path(Settings.LEGALARIO_SELFIE_IMAGE_PATH)
        video = Path(Settings.LEGALARIO_SELFIE_VIDEO_PATH)
        faltan_ine = [
            lado for lado, ruta in (("frontal", Settings.LEGALARIO_FRONT_IMAGE_PATH),
                                    ("trasera", Settings.LEGALARIO_BACK_IMAGE_PATH))
            if not _lleno(ruta)
        ]

        selfie_ok = _lleno(selfie)
        ine_ok = not faltan_ine
        comprobante_ok = _lleno(Settings.COMPROBANTE_DOMICILIO_PATH)
        video_ok = _lleno(video) and selfie_ok and video.stat().st_mtime >= selfie.stat().st_mtime
        if video_ok:
            video_detalle = ""
        elif not video.is_file():
            video_detalle = "Falta generarlo con el botón de abajo" if selfie_ok else "Requiere primero la foto de frente"
        elif not selfie_ok:
            video_detalle = "Requiere primero la foto de frente"
        else:
            video_detalle = "Es anterior a la foto de frente; vuelve a generarlo"
        return [
            ("Foto de frente (selfie) cargada", selfie_ok, "" if selfie_ok else "Súbela con el botón de abajo"),
            ("Foto INE frontal y trasera cargadas", ine_ok,
             "" if ine_ok else "Falta la INE " + " y la INE ".join(faltan_ine)),
            ("Comprobante de domicilio cargado", comprobante_ok,
             "" if comprobante_ok else "Súbelo con el botón de abajo"),
            ("Video generado a partir de la foto de frente", video_ok, video_detalle),
        ]

    def _ajustes_completos(self) -> tuple:
        """(ok, motivos) — todos los ajustes de usuario deben estar llenos y válidos."""
        motivos = []
        celular = self.celular_var.get().strip()
        if not CELULAR_REGEX.match(celular):
            motivos.append("Número de celular")
        if not correo_valido(self.correo_var.get().strip()):
            motivos.append("Correo electrónico")
        if not NOMBRE_INE_REGEX.match(self.nombre_ine_var.get().strip()):
            motivos.append("Nombre como aparece en la INE")
        if not COLABORADOR_REGEX.match(self.colaborador_var.get().strip()):
            motivos.append("Número de colaborador")
        motivos += [etiqueta for etiqueta, ok, _ in self._estado_archivos() if not ok]
        return not motivos, motivos

    def _actualizar_gate_ajustes(self):
        """Bloquea la elección de insumo mientras falten conexiones o ajustes de usuario."""
        ok, motivos = self._ajustes_completos()
        conexiones = self._conexiones_pendientes()
        if ok and not conexiones:
            self.ajustes_aviso.pack_forget()
            self.insumo_combo.configure(state="readonly")
            return
        pendientes = [f"Conexión {HOSTS_BD[h].titulo}" for h in conexiones] + motivos
        self.ajustes_aviso.configure(
            text="⚠ Completa lo pendiente (🔌 Conexiones, ⚙ Ajustes) para continuar.\nPendiente: "
                 + ", ".join(pendientes)
        )
        self.ajustes_aviso.pack(fill="x", pady=(0, 8), before=self.insumo_combo)
        self.insumo_combo.configure(state="disabled")
        if self.insumo_var.get():
            self._volver_al_menu()

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

        conexiones_btn = tk.Button(
            self.title_frame,
            text="🔌",
            font=("Segoe UI", 15),
            bg=ACCENT,
            fg="white",
            activebackground="#0d47a1",
            activeforeground="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self._abrir_conexiones
        )
        conexiones_btn.grid(row=0, column=3, sticky="e", padx=(0, 15))
        self._add_tooltip(conexiones_btn, "Conexiones")

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
        self.ajustes_aviso = tk.Label(
            self.step1_frame, text="", font=("Segoe UI", 9), bg=BG, fg="#c62828",
            wraplength=480, justify="left", anchor="w"
        )
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

        # ── Paso 2b: opciones de Venta (lista de lotes independientes, cada uno
        # con su propia agencia/tipo/método/seguro/cantidad — ver _agregar_fila_venta)
        self.panel_venta = tk.Frame(form, bg=BG)

        tk.Label(
            self.panel_venta, text="Lotes de venta:", font=FONT_LABEL, bg=BG, anchor="w"
        ).pack(fill="x", pady=(0, 6))

        VENTAS_CANVAS_HEIGHT = 220
        ventas_scroll_area = tk.Frame(self.panel_venta, bg=BG)
        ventas_scroll_area.pack(fill="x")

        self.ventas_canvas = tk.Canvas(
            ventas_scroll_area, bg=BG, highlightthickness=0, height=VENTAS_CANVAS_HEIGHT
        )
        ventas_scrollbar = ttk.Scrollbar(
            ventas_scroll_area, orient="vertical", command=self.ventas_canvas.yview
        )
        self.ventas_canvas.configure(yscrollcommand=ventas_scrollbar.set)
        self.ventas_canvas.pack(side="left", fill="both", expand=True)
        ventas_scrollbar.pack(side="right", fill="y")

        self.ventas_list_frame = tk.Frame(self.ventas_canvas, bg=BG)
        self._ventas_canvas_window = self.ventas_canvas.create_window(
            (0, 0), window=self.ventas_list_frame, anchor="nw"
        )

        def _actualizar_scrollregion_ventas(_e=None):
            self.ventas_canvas.configure(scrollregion=self.ventas_canvas.bbox("all"))

        def _ajustar_ancho_interno_ventas(event):
            self.ventas_canvas.itemconfig(self._ventas_canvas_window, width=event.width)

        self.ventas_list_frame.bind("<Configure>", _actualizar_scrollregion_ventas)
        self.ventas_canvas.bind("<Configure>", _ajustar_ancho_interno_ventas)

        def _on_mousewheel_ventas(event):
            self.ventas_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.ventas_canvas.bind("<Enter>", lambda _e: self.ventas_canvas.bind_all("<MouseWheel>", _on_mousewheel_ventas))
        self.ventas_canvas.bind("<Leave>", lambda _e: self.ventas_canvas.unbind_all("<MouseWheel>"))

        tk.Button(
            self.panel_venta,
            text="+ Agregar lote de venta",
            font=FONT_LABEL,
            bg="#e0e0e0",
            relief="flat",
            cursor="hand2",
            command=self._agregar_fila_venta
        ).pack(anchor="w", pady=(8, 10))

        tk.Label(self.panel_venta, text="Número de celular:", font=FONT_LABEL, bg=BG, anchor="w").pack(
            fill="x", pady=(0, 4)
        )
        tk.Entry(
            self.panel_venta, textvariable=self.celular_var, font=FONT_LABEL, width=40
        ).pack(fill="x", pady=(0, 10))

        tk.Label(self.panel_venta, text="Correo electrónico:", font=FONT_LABEL, bg=BG, anchor="w").pack(
            fill="x", pady=(0, 4)
        )
        tk.Entry(
            self.panel_venta, textvariable=self.correo_var, font=FONT_LABEL, width=40
        ).pack(fill="x", pady=(0, 4))

        tk.Checkbutton(
            self.panel_venta,
            text="Tomar capturas paso a paso de la venta",
            variable=self.tomar_capturas_var,
            font=FONT_LABEL,
            bg=BG,
            activebackground=BG,
            cursor="hand2"
        ).pack(anchor="w", pady=(6, 0))

        tk.Label(
            self.panel_venta, text="Navegador:", font=FONT_LABEL, bg=BG, anchor="w"
        ).pack(fill="x", pady=(10, 4))
        navegador_frame = tk.Frame(self.panel_venta, bg=BG)
        navegador_frame.pack(fill="x", pady=(0, 4))
        tk.Radiobutton(
            navegador_frame, text="Ver el navegador paso a paso", value="visible",
            variable=self.navegador_var, font=FONT_LABEL, bg=BG, activebackground=BG,
            cursor="hand2"
        ).pack(anchor="w")
        tk.Radiobutton(
            navegador_frame, text="Ejecutar en segundo plano (sin mostrar el navegador)",
            value="headless", variable=self.navegador_var, font=FONT_LABEL, bg=BG,
            activebackground=BG, cursor="hand2"
        ).pack(anchor="w")

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

    def _cambiar_cantidad_fila_venta(self, row: dict, delta: int):
        var = row["cantidad_var"]
        var.set(max(1, min(50, var.get() + delta)))
        self._actualizar_texto_boton_venta()

    def _agregar_fila_venta(self):
        self.ventas_rows.append({
            "tipo_var": tk.StringVar(value="CN"),
            "agencia_var": tk.StringVar(),
            "metodo_var": tk.StringVar(),
            "seguro_var": tk.StringVar(value="si"),  # "si" / "no"
            "cantidad_var": tk.IntVar(value=1),
        })
        self._renderizar_filas_venta()
        self._actualizar_texto_boton_venta()

    def _quitar_fila_venta(self, row: dict):
        if len(self.ventas_rows) <= 1:
            return
        self.ventas_rows.remove(row)
        self._renderizar_filas_venta()
        self._actualizar_texto_boton_venta()

    def _actualizar_texto_boton_venta(self):
        """Pluraliza el botón de confirmar cuando el total de ventas pedidas es > 1."""
        if self.insumo_var.get() != "VENTA":
            return
        total = sum(row["cantidad_var"].get() for row in self.ventas_rows)
        self.confirm_btn.configure(
            text="▶  Crear Ventas" if total > 1 else "▶  Crear Venta"
        )

    def _renderizar_filas_venta(self):
        FONT_LABEL = self._FONT_LABEL
        FONT_BTN = self._FONT_BTN
        CARD_BG = "#ffffff"
        for child in self.ventas_list_frame.winfo_children():
            child.destroy()

        for idx, row in enumerate(self.ventas_rows, start=1):
            card = tk.Frame(self.ventas_list_frame, bg=CARD_BG, relief="groove", bd=1)
            card.pack(fill="x", pady=(0, 10))
            inner = tk.Frame(card, bg=CARD_BG, padx=12, pady=10)
            inner.pack(fill="x")

            header = tk.Frame(inner, bg=CARD_BG)
            header.pack(fill="x", pady=(0, 8))
            tk.Label(
                header, text=f"Lote {idx}", font=("Segoe UI", 10, "bold"), bg=CARD_BG
            ).pack(side="left")
            if len(self.ventas_rows) > 1:
                tk.Button(
                    header, text="✕ Quitar", font=("Segoe UI", 8), bg=CARD_BG, fg="#c62828",
                    relief="flat", cursor="hand2",
                    command=lambda r=row: self._quitar_fila_venta(r)
                ).pack(side="right")

            tk.Label(inner, text="Tipo de cliente:", font=FONT_LABEL, bg=CARD_BG, anchor="w").pack(fill="x")
            tipo_frame = tk.Frame(inner, bg=CARD_BG)
            tipo_frame.pack(fill="x", pady=(2, 8))
            tk.Radiobutton(
                tipo_frame, text="Cliente nuevo (CN)", value="CN", variable=row["tipo_var"],
                font=FONT_LABEL, bg=CARD_BG, activebackground=CARD_BG, cursor="hand2"
            ).pack(side="left", padx=(0, 16))
            tk.Radiobutton(
                tipo_frame, text="Cliente frecuente (CF)", value="CF", variable=row["tipo_var"],
                font=FONT_LABEL, bg=CARD_BG, activebackground=CARD_BG, cursor="hand2"
            ).pack(side="left")

            tk.Label(inner, text="Agencia:", font=FONT_LABEL, bg=CARD_BG, anchor="w").pack(fill="x")
            agencia_combo = ttk.Combobox(
                inner, textvariable=row["agencia_var"],
                values=[ag["label"] for ag in self.agencias], state="readonly"
            )
            agencia_combo.pack(fill="x", pady=(2, 8))

            tk.Label(inner, text="Método de entrega:", font=FONT_LABEL, bg=CARD_BG, anchor="w").pack(fill="x")
            metodo_combo = ttk.Combobox(
                inner, textvariable=row["metodo_var"],
                values=[m["nombre"] for m in self.metodos], state="readonly"
            )
            metodo_combo.pack(fill="x", pady=(2, 8))

            tk.Label(inner, text="¿Con seguro?", font=FONT_LABEL, bg=CARD_BG, anchor="w").pack(fill="x")
            seguro_frame = tk.Frame(inner, bg=CARD_BG)
            seguro_frame.pack(fill="x", pady=(2, 8))
            tk.Radiobutton(
                seguro_frame, text="Con seguro", value="si", variable=row["seguro_var"],
                font=FONT_LABEL, bg=CARD_BG, activebackground=CARD_BG, cursor="hand2"
            ).pack(side="left", padx=(0, 16))
            tk.Radiobutton(
                seguro_frame, text="Sin seguro", value="no", variable=row["seguro_var"],
                font=FONT_LABEL, bg=CARD_BG, activebackground=CARD_BG, cursor="hand2"
            ).pack(side="left")

            tk.Label(inner, text="Cantidad:", font=FONT_LABEL, bg=CARD_BG, anchor="w").pack(fill="x")
            cantidad_frame = tk.Frame(inner, bg=CARD_BG)
            cantidad_frame.pack(anchor="w", pady=(2, 0))
            tk.Button(
                cantidad_frame, text="−", font=FONT_BTN, width=2, relief="flat", bg="#e0e0e0",
                command=lambda r=row: self._cambiar_cantidad_fila_venta(r, -1)
            ).pack(side="left")
            tk.Label(
                cantidad_frame, textvariable=row["cantidad_var"],
                font=("Segoe UI", 11, "bold"), bg=CARD_BG, width=4
            ).pack(side="left")
            tk.Button(
                cantidad_frame, text="+", font=FONT_BTN, width=2, relief="flat", bg="#e0e0e0",
                command=lambda r=row: self._cambiar_cantidad_fila_venta(r, 1)
            ).pack(side="left")

        # El Canvas de ventas tiene alto fijo (VENTAS_CANVAS_HEIGHT) y hace scroll
        # internamente, así que agregar/quitar filas ya no cambia el tamaño de la ventana.

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
            self._actualizar_texto_boton_venta()
        self.confirm_btn.configure(state="normal")
        self._center_window(600, self._fixed_height)

    def _volver_al_menu(self):
        self.step2_header.pack_forget()
        self.panel_oferta.pack_forget()
        self.panel_venta.pack_forget()
        self.panel_agencia.pack_forget()

        self.insumo_var.set("")
        self.insumo_label_var.set(INSUMO_PLACEHOLDER)
        self.confirm_btn.configure(
            text="Elige un insumo para continuar"
            if self._ajustes_completos()[0] else AJUSTES_INCOMPLETOS_TEXTO,
            state="disabled"
        )

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

        # Solo se fija el ancho (con un espaciador): el alto lo da el contenido, así no sobra espacio
        # en blanco y la ventana crece si aparecen detalles o errores. Se centra al final.
        tk.Frame(dialog, width=440, height=0, bg=BG).pack()

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
        correo_entry.pack(fill="x", pady=(4, 10))

        tk.Label(
            form, text="Nombre como aparece en la INE (MAYÚSCULAS):", font=FONT_LABEL, bg=BG,
            anchor="w"
        ).pack(fill="x")

        nombre_var = tk.StringVar(value=self.nombre_ine_var.get())
        # Fuerza mayúsculas mientras se escribe.
        nombre_var.trace_add("write", lambda *_: nombre_var.set(nombre_var.get().upper())
                             if nombre_var.get() != nombre_var.get().upper() else None)
        nombre_entry = tk.Entry(form, font=FONT_LABEL, width=25, textvariable=nombre_var)
        nombre_entry.pack(fill="x", pady=(4, 10))

        tk.Label(
            form, text="Número de colaborador (2 dígitos):", font=FONT_LABEL, bg=BG, anchor="w"
        ).pack(fill="x")

        colaborador_entry = tk.Entry(form, font=FONT_LABEL, width=25)
        colaborador_entry.insert(0, self.colaborador_var.get())
        colaborador_entry.pack(fill="x", pady=(4, 10))

        tk.Label(
            form, text="Checks obligatorios:", font=FONT_LABEL, bg=BG, anchor="w"
        ).pack(fill="x")
        checks_frame = tk.Frame(form, bg=BG)
        checks_frame.pack(fill="x", pady=(4, 0))

        def _subir(destino: str, titulo: str):
            ruta = filedialog.askopenfilename(
                parent=dialog, title=titulo,
                filetypes=[("Imágenes", "*.jpg *.jpeg *.png"), ("Todos", "*.*")]
            )
            if not ruta:
                return
            try:
                from PIL import Image
                Path(destino).parent.mkdir(parents=True, exist_ok=True)
                with Image.open(ruta) as img:
                    img.convert("RGB").save(destino, "JPEG", quality=95)
            except Exception as exc:
                error_label.config(text=f"No se pudo cargar la imagen: {exc}")
                return
            error_label.config(text="")
            _refrescar_checks()

        gen = {"proc": None}

        def _generar_video():
            if gen["proc"] is not None:
                return
            error_label.config(text="")
            flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
            gen["proc"] = subprocess.Popen(
                [sys.executable, str(PROJECT_ROOT / "utils" / "generate_fake_camera_video.py")],
                cwd=PROJECT_ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, creationflags=flags
            )
            _refrescar_checks()
            dialog.after(300, _esperar_video)

        def _esperar_video():
            proc = gen["proc"]
            if proc is None or not dialog.winfo_exists():
                return
            if proc.poll() is None:
                dialog.after(300, _esperar_video)
                return
            salida = proc.stdout.read() or ""
            gen["proc"] = None
            if proc.returncode != 0:
                error_label.config(
                    text="No se pudo generar el video: " + (salida.strip().splitlines() or ["error"])[-1]
                )
            _refrescar_checks()

        def _boton(parent, texto, comando, habilitado=True):
            tk.Button(
                parent, text=texto, font=("Segoe UI", 8), relief="flat", bg="#e3f2fd",
                command=comando, state="normal" if habilitado else "disabled"
            ).pack(side="left", padx=(0, 6))

        def _refrescar_checks():
            for child in checks_frame.winfo_children():
                child.destroy()
            estado = self._estado_archivos()
            selfie_ok, video_ok = estado[0][1], estado[3][1]
            generando = gen["proc"] is not None
            for i, (etiqueta, ok, detalle) in enumerate(estado):
                tk.Label(
                    checks_frame, text=("✔ " if ok else "✘ ") + etiqueta,
                    font=("Segoe UI", 9), bg=BG, fg="#2e7d32" if ok else "#c62828",
                    anchor="w", wraplength=350, justify="left"
                ).pack(fill="x")
                if detalle:
                    tk.Label(
                        checks_frame, text=detalle, font=("Segoe UI", 8), bg=BG, fg="#757575",
                        anchor="w", wraplength=350, justify="left", padx=14
                    ).pack(fill="x")
                fila = tk.Frame(checks_frame, bg=BG, padx=14)
                fila.pack(fill="x", pady=(0, 4))
                if i == 0:
                    _boton(fila, "Subir foto de frente…", lambda: _subir(
                        Settings.LEGALARIO_SELFIE_IMAGE_PATH, "Foto de frente (selfie)"))
                elif i == 1:
                    _boton(fila, "Subir INE frontal…", lambda: _subir(
                        Settings.LEGALARIO_FRONT_IMAGE_PATH, "INE frontal"))
                    _boton(fila, "Subir INE trasera…", lambda: _subir(
                        Settings.LEGALARIO_BACK_IMAGE_PATH, "INE trasera"))
                elif i == 2:
                    _boton(fila, "Subir comprobante de domicilio…", lambda: _subir(
                        Settings.COMPROBANTE_DOMICILIO_PATH, "Comprobante de domicilio"))
                else:
                    if generando:
                        texto = "Generando video…"
                    else:
                        texto = "Regenerar video" if (Path(Settings.LEGALARIO_SELFIE_VIDEO_PATH).is_file())                             else "Generar video"
                    # Solo con la selfie cargada, y solo si falta o está viejo.
                    _boton(fila, texto, _generar_video,
                           habilitado=selfie_ok and not video_ok and not generando)
            return all(ok for _, ok, _ in estado)

        _refrescar_checks()

        error_label = tk.Label(
            form, text="", font=("Segoe UI", 8), bg=BG, fg="#c62828", wraplength=350, justify="left"
        )
        error_label.pack(fill="x", pady=(4, 0))

        def _save():
            celular = celular_entry.get().strip()
            correo = correo_entry.get().strip()
            nombre = " ".join(nombre_var.get().split())
            colaborador = colaborador_entry.get().strip()

            if not CELULAR_REGEX.match(celular):
                error_label.config(text="Ingresa un número de celular válido: exactamente 10 dígitos (solo números).")
                return
            if not correo_valido(correo):
                error_label.config(text="Ingresa un correo electrónico válido (ej. nombre@dominio.com, sin espacios).")
                return
            if not NOMBRE_INE_REGEX.match(nombre):
                error_label.config(
                    text="Ingresa el nombre tal como aparece en la INE, solo letras en mayúsculas."
                )
                return
            if not COLABORADOR_REGEX.match(colaborador):
                error_label.config(text="El número de colaborador debe ser de 2 dígitos.")
                return

            self.celular_var.set(celular)
            self.correo_var.set(correo)
            self.nombre_ine_var.set(nombre)
            self.colaborador_var.set(colaborador)
            self.user_settings["celular"] = celular
            self.user_settings["correo"] = correo
            self.user_settings["nombre_ine"] = nombre
            self.user_settings["numero_colaborador"] = colaborador
            self._save_user_settings()

            if not _refrescar_checks():
                error_label.config(
                    text="Datos guardados, pero los checks obligatorios deben cumplirse "
                         "para poder operar."
                )
                self._actualizar_gate_ajustes()
                return
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

        self.root.update_idletasks()
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - dialog.winfo_reqwidth()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - dialog.winfo_reqheight()) // 2
        dialog.geometry(f"+{max(x, 0)}+{max(y, 0)}")

        celular_entry.focus_set()
        dialog.wait_window()
        self._actualizar_gate_ajustes()

    def _importar_env_legado(self):
        """
        Migra una sola vez las conexiones de un .env de versiones anteriores al almacén seguro y
        ofrece borrar el archivo (ya no se usa). Sin .env, o sin nada nuevo que importar, no hace nada.
        """
        if not ENV_LEGADO.exists():
            return
        try:
            importados = importar_env(self.credenciales, ENV_LEGADO)
        except (KeyringError, OSError):
            return  # sin almacén seguro: el diálogo "Conexiones" lo explicará cuando haga falta
        if importados and messagebox.askyesno(
            "Conexiones importadas",
            f"Se importaron al almacén seguro de Windows las conexiones del archivo .env: "
            f"{', '.join(importados)}.\n\nEl .env ya no se usa. ¿Quieres borrarlo ahora?",
        ):
            ENV_LEGADO.unlink()

    def _asegurar_conexiones(self, hosts: list) -> bool:
        """
        True si los hosts que la corrida necesita ya están configurados. Si falta alguno, abre
        el diálogo "Conexiones" y vuelve a comprobar (False si el usuario cancela).
        """
        try:
            faltantes = hosts_sin_configurar(self.credenciales, hosts)
        except KeyringError:
            faltantes = list(hosts)  # el diálogo explica por qué no hay almacén seguro
        if not faltantes:
            return True
        open_connections_dialog(
            self.root, self.credenciales, hosts=hosts,
            mensaje="Faltan las conexiones que esta ejecución necesita. Captúralas y prueba que funcionen.",
        )
        try:
            return not hosts_sin_configurar(self.credenciales, hosts)
        except KeyringError:
            return False

    def _on_confirm(self):
        ajustes_ok, pendientes = self._ajustes_completos()
        if not ajustes_ok:
            messagebox.showwarning(
                "Ajustes incompletos",
                "Completa los ajustes de usuario antes de continuar.\n\nPendiente:\n  • "
                + "\n  • ".join(pendientes)
            )
            self._actualizar_gate_ajustes()
            return

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
            if not self.ventas_rows:
                messagebox.showwarning("Campo requerido", "Agrega al menos un lote de venta.")
                return
            ventas_batches = []
            for idx, row in enumerate(self.ventas_rows, start=1):
                agencia_label_fila = row["agencia_var"].get()
                if not agencia_label_fila:
                    messagebox.showwarning(
                        "Campo requerido", f"Selecciona la agencia del lote {idx}."
                    )
                    return
                metodo_fila = row["metodo_var"].get()
                if not metodo_fila:
                    messagebox.showwarning(
                        "Campo requerido", f"Selecciona el método de entrega del lote {idx}."
                    )
                    return
                agencia_data = CatalogDB.get_agencia_by_label(agencia_label_fila)
                ventas_batches.append({
                    "id":             f"lote{idx}",
                    "tipo_cliente":   row["tipo_var"].get(),
                    "agencia_label":  agencia_label_fila,
                    "agencia":        agencia_data["agencia"],
                    "focus_id":       agencia_data["focus_id"],
                    "password":       agencia_data["password"],
                    "metodo_entrega": metodo_fila,
                    "con_seguro":     row["seguro_var"].get() == "si",
                    "cantidad":       row["cantidad_var"].get(),
                })
            ventas = {}
            for batch in ventas_batches:
                ventas[batch["tipo_cliente"]] = ventas.get(batch["tipo_cliente"], 0) + batch["cantidad"]
            if sum(ventas.values()) < 1:
                messagebox.showwarning(
                    "Valor inválido", "Debes indicar al menos 1 venta (CF o CN)."
                )
                return
            celular = self.celular_var.get().strip()
            correo = self.correo_var.get().strip()
            if not CELULAR_REGEX.match(celular):
                messagebox.showwarning(
                    "Campo requerido", "Ingresa un número de celular válido: exactamente 10 dígitos (solo números)."
                )
                return
            if not correo_valido(correo):
                messagebox.showwarning(
                    "Campo requerido", "Ingresa un correo electrónico válido (ej. nombre@dominio.com, sin espacios)."
                )
                return
            tomar_capturas = self.tomar_capturas_var.get()

        hosts = hosts_requeridos(insumo)
        if not self._asegurar_conexiones(hosts):
            return

        # La ejecución requiere VPN de Provident (portal UAT y las bases de datos, solo
        # accesibles con ella) y que las credenciales guardadas funcionen: se prueba el
        # portal y, por cada base que la corrida necesita, el login y la lectura de su tabla.
        self.root.configure(cursor="watch")
        self.confirm_btn.configure(state="disabled", text="Verificando conexiones…")
        self.root.update_idletasks()
        try:
            vpn_ok, faltantes = verificar_vpn(requiere_bd=False)
            resultados = probar_hosts(self.credenciales, hosts) if vpn_ok else {}
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
        fallidas = {h: r for h, r in resultados.items() if not r.ok}
        if fallidas:
            detalle = "\n\n".join(f"{h}: {r.mensaje}" for h, r in fallidas.items())
            if messagebox.askyesno(
                "Conexión a la base de datos fallida",
                f"No se puede iniciar la ejecución.\n\n{detalle}\n\n¿Quieres revisar las conexiones?",
            ):
                open_connections_dialog(self.root, self.credenciales, hosts=list(fallidas))
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
            config = {
                "ventas":         ventas,
                "ventas_batches": ventas_batches,
                "celular":        self.celular_var.get(),
                "correo":         self.correo_var.get(),
                "nombre_ine":     self.nombre_ine_var.get(),
                "numero_colaborador": self.colaborador_var.get(),
                "tomar_capturas": tomar_capturas,
                "headless":       self.navegador_var.get() == "headless",
            }

        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config_path.write_text(
            json.dumps(config, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

        self.confirmed = True
        self.root.destroy()

    def run(self) -> bool:
        self.root.mainloop()
        return self.confirmed
