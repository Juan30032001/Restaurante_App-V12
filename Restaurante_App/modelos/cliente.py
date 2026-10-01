from __future__ import annotations


class Cliente:
    def __init__(self, identificacion: str, nombre: str, correo: str) -> None:
        self.identificacion = identificacion
        self.nombre = nombre
        self.correo = correo

    def mostrar_informacion(self) -> str:
        return f"Cliente: {self.nombre} | Identificación: {self.identificacion} | Correo: {self.correo}"
