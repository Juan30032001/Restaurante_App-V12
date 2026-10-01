from __future__ import annotations

from typing import Dict, List, Optional, Set, Tuple

from modelos.producto import Producto
from modelos.usuario import Usuario
from modelos.venta import Venta


class Restaurante:
    MENÚ_PRINCIPAL: Tuple[str, ...] = (
        "1. Registrar producto",
        "2. Buscar producto",
        "3. Actualizar producto",
        "4. Eliminar producto",
        "5. Listar productos",
        "6. Registrar usuario",
        "7. Listar usuarios",
        "8. Mostrar categorías",
        "9. Vender producto",
        "10. Consultar ventas de un usuario",
        "11. Salir",
    )

    def __init__(self) -> None:
        self.productos: List[Producto] = []
        self.usuarios: List[Usuario] = []
        self._productos_por_codigo: Dict[str, Producto] = {}
        self._usuarios_por_identificacion: Dict[str, Usuario] = {}
        self._acciones_menu: Dict[str, str] = {
            "1": "registrar_producto",
            "2": "buscar_producto",
            "3": "actualizar_producto",
            "4": "eliminar_producto",
            "5": "listar_productos",
            "6": "registrar_usuario",
            "7": "listar_usuarios",
            "8": "mostrar_categorias",
            "9": "vender_producto",
            "10": "consultar_ventas_usuario",
            "11": "salir",
        }
        self._ventas: List[Venta] = []
        self._ventas_por_usuario: Dict[str, List[Venta]] = {}

    def registrar_producto(self, producto: Producto) -> None:
        if self._existe_codigo_producto(producto.codigo):
            raise ValueError(f"El código de producto {producto.codigo} ya está registrado.")
        self.productos.append(producto)
        self._productos_por_codigo[producto.codigo] = producto

    def buscar_producto(self, codigo: str) -> Optional[Producto]:
        return self._productos_por_codigo.get(codigo)

    def actualizar_producto(self, codigo: str, nombre: str, categoria: str, precio: float) -> Producto:
        producto = self.buscar_producto(codigo)
        if producto is None:
            raise ValueError(f"El producto con código {codigo} no existe.")

        producto.nombre = nombre.strip() or producto.nombre
        producto.categoria = categoria.strip() or producto.categoria
        producto.precio = precio
        return producto

    def eliminar_producto(self, codigo: str) -> bool:
        producto = self.buscar_producto(codigo)
        if producto is None:
            raise ValueError(f"El producto con código {codigo} no existe.")

        self.productos = [item for item in self.productos if item.codigo != codigo]
        del self._productos_por_codigo[codigo]
        return True

    def listar_productos(self) -> List[Producto]:
        return self.productos

    def registrar_usuario(self, usuario: Usuario) -> None:
        if self._existe_identificacion_usuario(usuario.identificacion):
            raise ValueError(f"La identificación {usuario.identificacion} ya está registrada.")
        self.usuarios.append(usuario)
        self._usuarios_por_identificacion[usuario.identificacion] = usuario

    def listar_usuarios(self) -> List[Usuario]:
        return self.usuarios

    def buscar_usuario(self, identificacion: str) -> Optional[Usuario]:
        return self._usuarios_por_identificacion.get(identificacion)

    def vender_producto(self, codigo_producto: str, identificacion_usuario: str, cantidad: int) -> bool:
        usuario = self.buscar_usuario(identificacion_usuario)
        producto = self.buscar_producto(codigo_producto)
        if usuario is None or producto is None:
            return False
        if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad <= 0:
            return False
        if producto.stock < cantidad:
            return False
        venta = Venta(usuario.identificacion, producto.codigo, cantidad)
        self._ventas.append(venta)
        self._ventas_por_usuario.setdefault(venta.usuario_id, []).append(venta)
        producto.vender(cantidad)
        return True

    def consultar_ventas_usuario(self, identificacion_usuario: str) -> List[Venta]:
        return list(self._ventas_por_usuario.get(identificacion_usuario, []))

    def listar_ventas(self) -> List[Venta]:
        return self._ventas

    def cargar_ventas(self, ventas: List[Venta]) -> None:
        self._ventas = ventas
        self._ventas_por_usuario = {}
        for venta in ventas:
            self._ventas_por_usuario.setdefault(venta.usuario_id, []).append(venta)

    def obtener_categorias_productos(self) -> Set[str]:
        return {producto.categoria for producto in self.productos}

    def obtener_accion_menu(self, opcion: str) -> Optional[str]:
        return self._acciones_menu.get(opcion)

    def _existe_codigo_producto(self, codigo: str) -> bool:
        return codigo in self._productos_por_codigo

    def _existe_identificacion_usuario(self, identificacion: str) -> bool:
        return identificacion in self._usuarios_por_identificacion
