from __future__ import annotations

import json
from pathlib import Path
from typing import Any, List

from modelos.producto import Producto
from modelos.usuario import Usuario
from modelos.venta import Venta


class ArchivoServicio:
    def __init__(self, ruta_productos: str = "datos/productos.json", ruta_usuarios: str = "datos/usuarios.json", ruta_ventas: str = "datos/ventas.json") -> None:
        self.ruta_productos = Path(ruta_productos)
        self.ruta_usuarios = Path(ruta_usuarios)
        self.ruta_ventas = Path(ruta_ventas)

    def cargar_productos(self) -> List[Producto]:
        try:
            with open(self.ruta_productos, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            print(f"Advertencia: {self.ruta_productos} no contiene JSON válido. Se iniciará sin productos.")
            return []
        except PermissionError:
            print(f"Error: no hay permisos para leer {self.ruta_productos}.")
            return []

        if not isinstance(datos, list):
            print("Advertencia: el archivo de productos debe contener una lista JSON.")
            return []

        productos: List[Producto] = []
        for indice, registro in enumerate(datos, start=1):
            try:
                if not isinstance(registro, dict):
                    raise ValueError("el registro no es un objeto JSON")
                productos.append(Producto.from_dict(registro))
            except (KeyError, ValueError) as error:
                print(f"Advertencia: se omitió el producto {indice}: {error}")
        return productos

    def guardar_productos(self, productos: List[Producto]) -> bool:
        try:
            self.ruta_productos.parent.mkdir(parents=True, exist_ok=True)
            with open(self.ruta_productos, "w", encoding="utf-8") as archivo:
                json.dump(
                    [producto.to_dict() for producto in productos],
                    archivo,
                    ensure_ascii=False,
                    indent=4,
                )
        except PermissionError:
            print(f"Error: no hay permisos para escribir {self.ruta_productos}.")
            return False
        return True

    def _cargar_coleccion(self, ruta: Path, constructor: Any, nombre: str) -> list[Any]:
        try:
            with open(ruta, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            print(f"Advertencia: {ruta} no contiene JSON válido. Se iniciará sin {nombre}.")
            return []
        except PermissionError:
            print(f"Error: no hay permisos para leer {ruta}.")
            return []
        if not isinstance(datos, list):
            print(f"Advertencia: el archivo de {nombre} debe contener una lista JSON.")
            return []
        elementos: list[object] = []
        for indice, registro in enumerate(datos, start=1):
            try:
                if not isinstance(registro, dict):
                    raise ValueError("el registro no es un objeto JSON")
                elementos.append(constructor.from_dict(registro))
            except (KeyError, ValueError) as error:
                print(f"Advertencia: se omitió {nombre} {indice}: {error}")
        return elementos

    def cargar_usuarios(self) -> List[Usuario]:
        return self._cargar_coleccion(self.ruta_usuarios, Usuario, "usuarios")

    def cargar_ventas(self) -> List[Venta]:
        return self._cargar_coleccion(self.ruta_ventas, Venta, "ventas")

    def _guardar_coleccion(self, ruta: Path, elementos: list[Any]) -> bool:
        try:
            ruta.parent.mkdir(parents=True, exist_ok=True)
            with open(ruta, "w", encoding="utf-8") as archivo:
                json.dump([elemento.to_dict() for elemento in elementos], archivo, ensure_ascii=False, indent=4)
        except PermissionError:
            print(f"Error: no hay permisos para escribir {ruta}.")
            return False
        return True

    def guardar_usuarios(self, usuarios: List[Usuario]) -> bool:
        return self._guardar_coleccion(self.ruta_usuarios, usuarios)

    def guardar_ventas(self, ventas: List[Venta]) -> bool:
        return self._guardar_coleccion(self.ruta_ventas, ventas)