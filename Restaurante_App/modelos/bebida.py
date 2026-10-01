from __future__ import annotations

from modelos.producto import Producto


class Bebida(Producto):
    def __init__(
        self,
        codigo: str,
        nombre: str,
        categoria: str,
        precio: float,
        tamaño: str,
        envase: str,
    ) -> None:
        super().__init__(codigo, nombre, categoria, precio)
        self.tamaño = tamaño
        self.envase = envase

    def mostrar_informacion(self) -> str:
        return (
            f"Bebida: {self.nombre} | Código: {self.codigo} | "
            f"Categoría: {self.categoria} | Precio: ${self.precio:,.0f} | "
            f"Tamaño: {self.tamaño} | Envase: {self.envase}"
        )
