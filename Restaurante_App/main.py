from __future__ import annotations

import tkinter as tk
from pathlib import Path

from servicios.archivo_servicio import ArchivoServicio
from servicios.restaurante_servicio import RestauranteServicio
from ui.login_view import LoginView
from ui.main_view import MainView


class RestauranteApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Restaurante App")
        self.root.geometry("980x650")
        self.root.minsize(900, 600)

        icono = Path(__file__).resolve().parent / "assets" / "logo.xbm"
        if icono.exists():
            try:
                self.root.iconphoto(False, tk.BitmapImage(file=str(icono), foreground="#8b233d"))
            except tk.TclError:
                pass

        self.archivo_servicio = ArchivoServicio()
        self.servicio = RestauranteServicio(
            self.archivo_servicio.cargar_productos(),
            self.archivo_servicio.cargar_usuarios(),
            self.archivo_servicio.cargar_ventas(),
            self.archivo_servicio,
        )
        self.frame_actual: tk.Widget | None = None
        self.mostrar_login()

    def mostrar_login(self) -> None:
        self._limpiar_frame_actual()
        self.frame_actual = LoginView(self.root, self.servicio, self._ingresar)
        self.frame_actual.pack(fill="both", expand=True)

    def _ingresar(self, usuario) -> None:
        self._limpiar_frame_actual()
        self.frame_actual = MainView(self.root, self.servicio, usuario, self.mostrar_login)
        self.frame_actual.pack(fill="both", expand=True)

    def _limpiar_frame_actual(self) -> None:
        if self.frame_actual is not None:
            self.frame_actual.destroy()
            self.frame_actual = None


def main() -> None:
    root = tk.Tk()
    app = RestauranteApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
