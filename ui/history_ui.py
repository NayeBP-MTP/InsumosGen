import tkinter as tk
from tkinter import ttk

from utils.run_history import RunHistory


def open_history_dialog(parent: tk.Misc) -> None:
    """Ventana con el historial de intentos de venta, del más reciente al más antiguo."""
    BG = "#f5f5f5"

    dialog = tk.Toplevel(parent)
    dialog.title("Historial de ventas")
    dialog.configure(bg=BG)
    dialog.transient(parent)

    width, height = 980, 480
    parent.update_idletasks()
    x = parent.winfo_x() + (parent.winfo_width() - width) // 2
    y = parent.winfo_y() + (parent.winfo_height() - height) // 2
    dialog.geometry(f"{width}x{height}+{max(x, 0)}+{max(y, 0)}")

    registros = list(reversed(RunHistory.load()))
    ok = sum(1 for r in registros if r.get("estado") == "exitosa")
    tk.Label(
        dialog, text=f"{len(registros)} intento(s) registrado(s) · {ok} exitoso(s) · "
                     f"{len(registros) - ok} fallido(s)",
        font=("Segoe UI", 10), bg=BG, anchor="w"
    ).pack(fill="x", padx=16, pady=(12, 6))

    cols = ("fecha", "agencia", "metodo", "tipo", "seguro", "ronda", "estado", "detalle")
    frame = tk.Frame(dialog, bg=BG)
    frame.pack(fill="both", expand=True, padx=16, pady=(0, 12))

    tree = ttk.Treeview(frame, columns=cols, show="headings")
    for col, text, w in [
        ("fecha", "Fecha", 130), ("agencia", "Agencia", 100), ("metodo", "Método", 80),
        ("tipo", "Tipo", 45), ("seguro", "Seguro", 80), ("ronda", "Ronda", 50),
        ("estado", "Estado", 90), ("detalle", "Resultado", 380),
    ]:
        tree.heading(col, text=text)
        tree.column(col, width=w, anchor="w")
    tree.tag_configure("ok", foreground="#2e7d32")
    tree.tag_configure("fail", foreground="#c62828")

    for r in registros:
        exitosa = r.get("estado") == "exitosa"
        tree.insert(
            "", "end",
            values=(
                r.get("fecha", ""), r.get("agencia", ""), r.get("metodo", ""),
                r.get("tipo", ""), r.get("seguro", ""), r.get("ronda", ""),
                "✔ Exitosa" if exitosa else "✖ Fallida", r.get("detalle", ""),
            ),
            tags=("ok" if exitosa else "fail",),
        )

    scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scroll.set)
    tree.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")
