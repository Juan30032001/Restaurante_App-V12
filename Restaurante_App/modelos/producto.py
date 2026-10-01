from __future__ import annotations


class Producto:
    def __init__(self, codigo: str, nombre: str, categoria: str, precio: float, stock: int = 0) -> None:
        if not codigo.strip() or not nombre.strip() or not categoria.strip():
            raise ValueError("El código, nombre y categoría son obligatorios.")
        if precio <= 0:
            raise ValueError("El precio debe ser mayor que cero y estar expresado en dólares.")
        if isinstance(stock, bool) or not isinstance(stock, int) or stock < 0:
            raise ValueError("El stock debe ser un número entero mayor o igual que cero.")

        self.codigo = codigo.strip()
        self.nombre = nombre.strip()
        self.categoria = categoria.strip()
        self.precio = float(precio)
        self.stock = stock

    def to_dict(self) -> dict[str, str | float | int]:
        return {
            "codigo": self.codigo,
            "nombre": self.nombre,
            "categoria": self.categoria,
            "precio": self.precio,
            "stock": self.stock,
        }

    @classmethod
    def from_dict(cls, datos: dict[str, object]) -> "Producto":
        try:
            codigo = datos["codigo"]
            nombre = datos["nombre"]
            categoria = datos["categoria"]
            precio = datos["precio"]
            stock = datos.get("stock", 0)
        except KeyError as error:
            raise KeyError(f"Falta la clave {error.args[0]} en el producto.") from error

        if not isinstance(codigo, str) or not isinstance(nombre, str) or not isinstance(categoria, str):
            raise ValueError("Los datos de texto del producto no son válidos.")
        if isinstance(precio, bool) or not isinstance(precio, (int, float)):
            raise ValueError("El precio del producto debe ser numérico y estar expresado en dólares.")
        if isinstance(stock, bool) or not isinstance(stock, int):
            raise ValueError("El stock del producto debe ser un número entero.")
        return cls(codigo, nombre, categoria, float(precio), stock)

    def vender(self, cantidad: int) -> None:
        if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad <= 0:
            raise ValueError("La cantidad debe ser un entero mayor que cero.")
        if cantidad > self.stock:
            raise ValueError("No hay stock suficiente para realizar la venta.")
        self.stock -= cantidad

    def mostrar_informacion(self) -> str:
        return (
            f"Producto: {self.nombre} | Código: {self.codigo} | "
            f"Categoría: {self.categoria} | Precio: USD ${self.precio:.2f} | Stock: {self.stock}"
        )
