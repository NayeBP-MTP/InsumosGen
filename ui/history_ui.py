import tkinter as tk
from tkinter import ttk

from insumos.pendientes import ESPERANDO_QA
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
    qa = sum(1 for r in registros if r.get("estado") == ESPERANDO_QA)
    tk.Label(
        dialog, text=f"{len(registros)} intento(s) registrado(s) · {ok} exitoso(s) · "
                     f"{len(registros) - ok - qa} fallido(s)" + (f" · {qa} esperando QA" if qa else ""),
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
    tree.tag_configure("qa", foreground="#8d6e00")

    textos = {"exitosa": ("✔ Exitosa", "ok"), ESPERANDO_QA: ("⏸ Esperando QA", "qa")}
    for r in registros:
        texto, tag = textos.get(r.get("estado"), ("✖ Fallida", "fail"))
        tree.insert(
            "", "end",
            values=(
                r.get("fecha", ""), r.get("agencia", ""), r.get("metodo", ""),
                r.get("tipo", ""), r.get("seguro", ""), r.get("ronda", ""),
                texto, r.get("detalle", ""),
            ),
            tags=(tag,),
        )

    scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scroll.set)
    tree.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")
