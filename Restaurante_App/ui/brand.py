from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class BrandLockup(ttk.Frame):
    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master)
        self.columnconfigure(1, weight=1)

        color_fondo = ttk.Style(self).lookup("TFrame", "background") or "#f0f0f0"
        emblema = tk.Canvas(self, width=58, height=58, background=color_fondo, highlightthickness=0)
        emblema.grid(row=0, column=0, rowspan=2, padx=(0, 10))
        emblema.create_oval(2, 2, 56, 56, fill="#242520", outline="#b99a5c", width=2)
        emblema.create_line(12, 13, 46, 46, fill="#d6c69d", width=3, capstyle="round")
        emblema.create_line(46, 13, 12, 46, fill="#d6c69d", width=3, capstyle="round")
        emblema.create_line(9, 10, 14, 15, fill="#d6c69d", width=2)
        emblema.create_line(44, 10, 49, 15, fill="#d6c69d", width=2)
        emblema.create_polygon(20, 37, 13, 34, 17, 29, 25, 34, fill="#3e6547", outline="#b99a5c")
        emblema.create_polygon(35, 38, 44, 34, 41, 28, 32, 34, fill="#3e6547", outline="#b99a5c")
        emblema.create_line(28, 28, 29, 46, fill="#587548", width=3, smooth=True)
        for petalo in ((22, 14, 34, 26), (16, 19, 28, 31), (28, 19, 40, 31), (20, 25, 32, 37), (25, 24, 37, 36)):
            emblema.create_oval(*petalo, fill="#8b233d", outline="#d58b98", width=1)
        emblema.create_oval(26, 24, 32, 30, fill="#c39b54", outline="#e5ce9a")

        ttk.Label(
            self,
            text="SMOCK",
            font=("Georgia", 18, "bold"),
            foreground="#8b233d",
        ).grid(row=0, column=1, sticky="sw")
        ttk.Label(
            self,
            text="ROCK AND GRILL",
            font=("Georgia", 9, "bold"),
            foreground="#34332e",
        ).grid(row=1, column=1, sticky="nw")