import threading
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional

from config.credentials import CredentialsMissing, CredentialStore
from services.connection_gate import (
    HOSTS_BD,
    conexion_de_formulario,
    driver_sugerido,
    drivers_sql_server,
)
from services.connection_tester import ConnectionTester


def open_connections_dialog(parent: tk.Misc, store: Optional[CredentialStore] = None,
                            hosts: Optional[list[str]] = None, mensaje: str = "") -> bool:
    """
    Diálogo modal "Conexiones" para capturar, probar y guardar los hosts de SQL Server (las
    contraseñas van al Administrador de credenciales de Windows, nunca a disco). `hosts` limita
    qué tarjetas se muestran (por defecto todas). Devuelve True si se guardó algo.
    """
    BG = "#f5f5f5"
    ACCENT = "#1565C0"
    FONT_LABEL = ("Segoe UI", 10)
    FONT_TITLE = ("Segoe UI", 12, "bold")
    FONT_BTN = ("Segoe UI", 10, "bold")

    store = store or CredentialStore()
    disponible, detalle = store.backend_disponible()
    if not disponible:
        messagebox.showerror(
            "Almacén de credenciales no disponible",
            "No se puede usar el Administrador de credenciales de Windows, así que no es posible "
            f"guardar contraseñas de forma segura.\n\nDetalle: {detalle}",
            parent=parent,
        )
        return False

    instalados = drivers_sql_server()
    tester = ConnectionTester()
    guardado = {"ok": False}

    dialog = tk.Toplevel(parent)
    dialog.title("Conexiones")
    dialog.resizable(False, False)
    dialog.configure(bg=BG)
    dialog.transient(parent)
    dialog.grab_set()

    tk.Label(dialog, text="Conexiones a bases de datos", font=FONT_TITLE, bg=BG).pack(pady=(14, 2))
    tk.Label(
        dialog,
        text=mensaje or "Las contraseñas se guardan cifradas en el Administrador de credenciales de Windows.",
        font=("Segoe UI", 9), bg=BG, fg="#555555", wraplength=460, justify="center",
    ).pack(padx=20, pady=(0, 8))

    tarjetas = {}
    for host in hosts or list(HOSTS_BD):
        info = HOSTS_BD[host]
        try:
            actual = store.get_connection(host)
        except CredentialsMissing:
            actual = None

        card = tk.LabelFrame(dialog, text=f" {info.titulo} ", font=FONT_LABEL, bg=BG, padx=12, pady=8)
        card.pack(fill="x", padx=20, pady=6)
        card.grid_columnconfigure(1, weight=1)

        server_var = tk.StringVar(value=actual.server if actual else "")
        user_var = tk.StringVar(value=actual.user if actual else "")
        # Se precarga la contraseña guardada (enmascarada) para que se vea que sí quedó guardada.
        password_var = tk.StringVar(value=actual.password if actual else "")
        driver_var = tk.StringVar(value=actual.driver if actual else driver_sugerido(instalados))

        def _fila(fila, etiqueta, widget):
            tk.Label(card, text=etiqueta, font=FONT_LABEL, bg=BG, anchor="w").grid(
                row=fila, column=0, sticky="w", pady=2)
            widget.grid(row=fila, column=1, columnspan=2, sticky="ew", padx=(8, 0), pady=2)

        _fila(0, "Servidor:", tk.Entry(card, textvariable=server_var, font=FONT_LABEL, width=34))
        _fila(1, "Usuario:", tk.Entry(card, textvariable=user_var, font=FONT_LABEL))
        password_entry = tk.Entry(card, textvariable=password_var, font=FONT_LABEL, show="•")
        _fila(2, "Contraseña:", password_entry)
        _fila(3, "Driver ODBC:", ttk.Combobox(card, textvariable=driver_var, values=instalados, font=FONT_LABEL))

        mostrar_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            card, text="Mostrar contraseña", variable=mostrar_var, bg=BG, font=("Segoe UI", 9),
            command=lambda e=password_entry, v=mostrar_var: e.configure(show="" if v.get() else "•"),
        ).grid(row=4, column=1, sticky="w", padx=(8, 0))

        # El resultado va junto al botón; si el mensaje es largo se envuelve y la ventana crece.
        probar_btn = tk.Button(card, text="Probar", font=("Segoe UI", 9, "bold"), cursor="hand2")
        probar_btn.grid(row=5, column=0, sticky="w", pady=(6, 0))
        resultado = tk.Label(card, text="", font=("Segoe UI", 8), bg=BG, wraplength=330,
                             justify="left", anchor="w")
        resultado.grid(row=5, column=1, columnspan=2, sticky="ew", padx=(8, 0), pady=(6, 0))

        tarjetas[host] = {
            "server": server_var, "user": user_var, "password": password_var, "driver": driver_var,
            "resultado": resultado, "probar": probar_btn, "tenia": actual is not None,
        }

    def _leer(host):
        t = tarjetas[host]
        return conexion_de_formulario(
            store, host, t["server"].get(), t["user"].get(), t["password"].get(), t["driver"].get())

    def _probar(host):
        t = tarjetas[host]
        try:
            conexion = _leer(host)
        except ValueError as e:
            t["resultado"].config(text=str(e), fg="#c62828")
            return
        info = HOSTS_BD[host]
        t["probar"].config(state="disabled")
        t["resultado"].config(text="Probando…", fg="#555555")
        salida = {}

        def _trabajo():
            salida["r"] = tester.probar(conexion, base=info.base, tabla=info.tabla)

        def _esperar():
            if "r" not in salida:
                dialog.after(100, _esperar)
                return
            r = salida["r"]
            t["probar"].config(state="normal")
            t["resultado"].config(text=("✔ " if r.ok else "✖ ") + r.mensaje, fg="#2e7d32" if r.ok else "#c62828")

        threading.Thread(target=_trabajo, daemon=True).start()
        dialog.after(100, _esperar)

    for host, t in tarjetas.items():
        t["probar"].config(command=lambda h=host: _probar(h))

    error_label = tk.Label(dialog, text="", font=("Segoe UI", 9), bg=BG, fg="#c62828", wraplength=460)
    error_label.pack(padx=20)

    def _guardar():
        pendientes = []
        for host, t in tarjetas.items():
            vacia = not (t["server"].get().strip() or t["user"].get().strip() or t["password"].get())
            if vacia and not t["tenia"]:
                continue  # tarjeta sin tocar y sin nada guardado: se omite
            try:
                pendientes.append((host, _leer(host)))
            except ValueError as e:
                error_label.config(text=f"{HOSTS_BD[host].titulo}: {e}")
                return
        for host, conexion in pendientes:
            store.save_connection(host, conexion)
        guardado["ok"] = bool(pendientes)
        dialog.destroy()

    botones = tk.Frame(dialog, bg=BG, pady=10)
    botones.pack()
    tk.Button(
        botones, text="Guardar", font=FONT_BTN, bg=ACCENT, fg="white", activebackground="#0d47a1",
        activeforeground="white", relief="flat", padx=14, pady=6, cursor="hand2", command=_guardar,
    ).pack(side="left", padx=6)
    tk.Button(
        botones, text="Cancelar", font=FONT_BTN, relief="flat", padx=14, pady=6, cursor="hand2",
        command=dialog.destroy,
    ).pack(side="left", padx=6)

    dialog.update_idletasks()
    x = parent.winfo_x() + (parent.winfo_width() - dialog.winfo_width()) // 2
    y = parent.winfo_y() + max((parent.winfo_height() - dialog.winfo_height()) // 2, 0)
    dialog.geometry(f"+{max(x, 0)}+{max(y, 0)}")
    dialog.wait_window()
    return guardado["ok"]
