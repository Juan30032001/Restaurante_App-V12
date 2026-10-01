from __future__ import annotations

from typing import Iterable

from modelos.producto import Producto
from modelos.usuario import Usuario
from modelos.venta import Venta
from servicios.archivo_servicio import ArchivoServicio


class RestauranteServicio:
    """Coordina los datos que necesita la interfaz gráfica del restaurante."""

    def __init__(
        self,
        productos: Iterable[Producto | dict[str, object]],
        usuarios: Iterable[Usuario | dict[str, object]],
        ventas: Iterable[Venta | dict[str, object]] | None = None,
        archivo_servicio: ArchivoServicio | None = None,
    ) -> None:
        self._productos = [self._convertir_producto(producto) for producto in productos]
        self._usuarios = [self._convertir_usuario(usuario) for usuario in usuarios]
        self._ventas = [self._convertir_venta(venta) for venta in (ventas or [])]
        self._archivo_servicio = archivo_servicio

    @staticmethod
    def _convertir_producto(producto: Producto | dict[str, object]) -> Producto:
        return producto if isinstance(producto, Producto) else Producto.from_dict(producto)

    @staticmethod
    def _convertir_usuario(usuario: Usuario | dict[str, object]) -> Usuario:
        return usuario if isinstance(usuario, Usuario) else Usuario.from_dict(usuario)

    @staticmethod
    def _convertir_venta(venta: Venta | dict[str, object]) -> Venta:
        return venta if isinstance(venta, Venta) else Venta.from_dict(venta)

    def validar_acceso(self, identificacion: str, contrasena: str) -> Usuario | None:
        for usuario in self._usuarios:
            if usuario.identificacion == identificacion.strip() and usuario.contrasena == contrasena:
                return usuario
        return None

    def listar_productos(self) -> list[Producto]:
        return list(self._productos)

    def buscar_producto(self, codigo: str) -> Producto | None:
        codigo_normalizado = codigo.strip()
        return next((producto for producto in self._productos if producto.codigo == codigo_normalizado), None)

    def registrar_producto(
        self, codigo: str, nombre: str, categoria: str, precio: float, stock: int
    ) -> Producto:
        producto = Producto(codigo, nombre, categoria, precio, stock)
        if self.buscar_producto(producto.codigo) is not None:
            raise ValueError(f"El código {producto.codigo} ya está registrado.")
        self._productos.append(producto)
        self._guardar_productos()
        return producto

    def actualizar_producto(
        self, codigo: str, nombre: str, categoria: str, precio: float, stock: int
    ) -> Producto:
        producto = self.buscar_producto(codigo)
        if producto is None:
            raise ValueError(f"El producto con código {codigo.strip()} no existe.")
        actualizado = Producto(producto.codigo, nombre, categoria, precio, stock)
        producto.nombre = actualizado.nombre
        producto.categoria = actualizado.categoria
        producto.precio = actualizado.precio
        producto.stock = actualizado.stock
        self._guardar_productos()
        return producto

    def eliminar_producto(self, codigo: str) -> None:
        producto = self.buscar_producto(codigo)
        if producto is None:
            raise ValueError(f"El producto con código {codigo.strip()} no existe.")
        self._productos.remove(producto)
        self._guardar_productos()

    def _guardar_productos(self) -> None:
        if self._archivo_servicio is not None and not self._archivo_servicio.guardar_productos(self._productos):
            raise OSError("No fue posible guardar los productos.")

    def listar_usuarios(self) -> list[Usuario]:
        return list(self._usuarios)

    def buscar_usuario(self, identificacion: str) -> Usuario | None:
        identificacion_normalizada = identificacion.strip()
        return next((usuario for usuario in self._usuarios if usuario.identificacion == identificacion_normalizada), None)

    def registrar_usuario(
        self,
        identificacion: str | Usuario,
        nombre: str | None = None,
        correo: str | None = None,
        contrasena: str = "1234",
        rol: str = "Cliente",
    ) -> Usuario:
        if isinstance(identificacion, Usuario):
            usuario = identificacion
        else:
            if nombre is None or correo is None:
                raise ValueError("Identificación, nombre y correo son obligatorios.")
            usuario = Usuario(identificacion, nombre, correo, contrasena, rol)

        if usuario.rol == "Administrador":
            raise ValueError("La gestión de usuarios solo permite registrar Empleados o Clientes.")
        if self.buscar_usuario(usuario.identificacion) is not None:
            raise ValueError(f"La identificación {usuario.identificacion} ya está registrada.")
        self._usuarios.append(usuario)
        self._guardar_usuarios()
        return usuario

    def actualizar_usuario(
        self,
        identificacion: str,
        nombre: str,
        correo: str,
        rol: str,
        contrasena: str = "",
    ) -> Usuario:
        usuario = self.buscar_usuario(identificacion)
        if usuario is None:
            raise ValueError(f"El usuario con identificación {identificacion.strip()} no existe.")
        if usuario.rol == "Administrador":
            raise ValueError("Las cuentas Administrador no se modifican desde esta gestión.")
        if rol == "Administrador":
            raise ValueError("La gestión de usuarios solo permite asignar Empleado o Cliente.")

        actualizado = Usuario(
            usuario.identificacion,
            nombre,
            correo,
            contrasena or usuario.contrasena,
            rol,
        )
        usuario.nombre = actualizado.nombre
        usuario.correo = actualizado.correo
        usuario.contrasena = actualizado.contrasena
        usuario.rol = actualizado.rol
        self._guardar_usuarios()
        return usuario

    def eliminar_usuario(self, identificacion: str, identificacion_protegida: str | None = None) -> None:
        usuario = self.buscar_usuario(identificacion)
        if usuario is None:
            raise ValueError(f"El usuario con identificación {identificacion.strip()} no existe.")
        if usuario.rol == "Administrador":
            raise ValueError("Las cuentas Administrador no se eliminan desde esta gestión.")
        if usuario.identificacion == (identificacion_protegida or "").strip():
            raise ValueError("No puede eliminar la cuenta actualmente autenticada.")
        self._usuarios.remove(usuario)
        self._guardar_usuarios()

    def _guardar_usuarios(self) -> None:
        if self._archivo_servicio is not None and not self._archivo_servicio.guardar_usuarios(self._usuarios):
            raise OSError("No fue posible guardar los usuarios.")

    def listar_ventas(self) -> list[Venta]:
        return list(self._ventas)

    def consultar_ventas_usuario(self, identificacion_usuario: str) -> list[Venta]:
        return [venta for venta in self._ventas if venta.usuario_id == identificacion_usuario.strip()]

    def registrar_venta(self, identificacion_usuario: str, codigo_producto: str, cantidad: int) -> Venta:
        usuario = self.buscar_usuario(identificacion_usuario)
        producto = self.buscar_producto(codigo_producto)
        if usuario is None:
            raise ValueError("El usuario seleccionado no existe.")
        if producto is None:
            raise ValueError("El producto seleccionado no existe.")
        if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad <= 0:
            raise ValueError("La cantidad debe ser un entero mayor que cero.")
        if cantidad > producto.stock:
            raise ValueError("No hay stock suficiente para registrar la venta.")

        venta = Venta(usuario.identificacion, producto.codigo, cantidad)
        producto.stock -= cantidad
        self._ventas.append(venta)
        self._guardar_productos()
        self._guardar_ventas()
        return venta

    def _guardar_ventas(self) -> None:
        if self._archivo_servicio is not None and not self._archivo_servicio.guardar_ventas(self._ventas):
            raise OSError("No fue posible guardar las ventas.")

    def registrar_venta_desde_seleccion(self, usuario_seleccionado: Usuario, producto_seleccionado: Producto, cantidad: int) -> Venta:
        return self.registrar_venta(usuario_seleccionado.identificacion, producto_seleccionado.codigo, cantidad)