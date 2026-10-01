import unittest
import json
import tempfile
from pathlib import Path

from modelos.producto import Producto
from modelos.usuario import Usuario
from modelos.venta import Venta
from servicios.restaurante import Restaurante
from servicios.archivo_servicio import ArchivoServicio
from servicios.restaurante_servicio import RestauranteServicio


class RestauranteTests(unittest.TestCase):
    def test_producto_se_convierte_a_diccionario_con_precio_en_dolares(self) -> None:
        producto = Producto("P001", "Pizza", "Comida", 15.00, 10)

        self.assertEqual(producto.to_dict()["precio"], 15.0)
        self.assertIn("USD", producto.mostrar_informacion())
        self.assertEqual(producto.to_dict()["stock"], 10)

    def test_guardar_y_cargar_productos_reconstruye_objetos(self) -> None:
        with tempfile.TemporaryDirectory() as carpeta_temporal:
            ruta = Path(carpeta_temporal) / "productos.json"
            servicio = ArchivoServicio(str(ruta))
            productos = [Producto("P001", "Pizza", "Comida", 15.00)]

            self.assertTrue(servicio.guardar_productos(productos))
            with ruta.open("r", encoding="utf-8") as archivo:
                self.assertEqual(json.load(archivo)[0]["precio"], 15.0)

            productos_cargados = servicio.cargar_productos()

            self.assertIsInstance(productos_cargados[0], Producto)
            self.assertEqual(productos_cargados[0].precio, 15.0)

    def test_registrar_y_listar_productos(self) -> None:
        restaurante = Restaurante()
        producto = Producto("P001", "Pizza", "Comida", 15.00)

        restaurante.registrar_producto(producto)
        productos = restaurante.listar_productos()

        self.assertEqual(len(productos), 1)
        self.assertEqual(productos[0].codigo, "P001")
        self.assertEqual(productos[0].nombre, "Pizza")

    def test_validar_codigos_duplicados(self) -> None:
        restaurante = Restaurante()
        restaurante.registrar_producto(Producto("P001", "Pizza", "Comida", 15.00))

        with self.assertRaises(ValueError):
            restaurante.registrar_producto(Producto("P001", "Burger", "Comida", 18.00))

    def test_indices_de_productos_y_usuarios_se_mantienen_sincronizados(self) -> None:
        restaurante = Restaurante()
        producto = Producto("P001", "Pizza", "Comida", 15.00)
        usuario = Usuario("C001", "Ana", "ana@restaurante.com")

        restaurante.registrar_producto(producto)
        restaurante.registrar_usuario(usuario)

        self.assertIs(restaurante.buscar_producto("P001"), producto)
        self.assertIs(restaurante.buscar_usuario("C001"), usuario)
        self.assertIn("P001", restaurante._productos_por_codigo)
        self.assertIn("C001", restaurante._usuarios_por_identificacion)

        restaurante.eliminar_producto("P001")

        self.assertIsNone(restaurante.buscar_producto("P001"))
        self.assertNotIn("P001", restaurante._productos_por_codigo)

    def test_registrar_y_listar_usuarios(self) -> None:
        restaurante = Restaurante()
        usuario = Usuario("C001", "Ana García", "ana@restaurante.com")

        restaurante.registrar_usuario(usuario)
        usuarios = restaurante.listar_usuarios()

        self.assertEqual(len(usuarios), 1)
        self.assertEqual(usuarios[0].identificacion, "C001")
        self.assertEqual(usuarios[0].nombre, "Ana García")

    def test_evitar_identificaciones_duplicadas_y_obtener_categorias_unicas(self) -> None:
        restaurante = Restaurante()
        restaurante.registrar_producto(Producto("P001", "Pizza", "Comida", 15.00))
        restaurante.registrar_producto(Producto("P002", "Ensalada", "Comida", 12.00))
        restaurante.registrar_producto(Producto("P003", "Coca Cola", "Bebida", 4.50))

        with self.assertRaises(ValueError):
            restaurante.registrar_usuario(Usuario("C001", "Luis", "luis@restaurante.com"))
            restaurante.registrar_usuario(Usuario("C001", "Pedro", "pedro@restaurante.com"))

        categorias = restaurante.obtener_categorias_productos()
        self.assertEqual(categorias, {"Comida", "Bebida"})

    def test_vender_producto_registra_venta_y_disminuye_stock(self) -> None:
        restaurante = Restaurante()
        restaurante.registrar_usuario(Usuario("C001", "Ana", "ana@restaurante.com"))
        restaurante.registrar_producto(Producto("P001", "Pizza", "Comida", 15.00, 5))

        self.assertTrue(restaurante.vender_producto("P001", "C001", 2))
        self.assertEqual(restaurante.buscar_producto("P001").stock, 3)
        ventas = restaurante.consultar_ventas_usuario("C001")
        self.assertEqual(len(ventas), 1)
        self.assertIsInstance(ventas[0], Venta)
        self.assertEqual(ventas[0].cantidad, 2)

    def test_rechazar_venta_no_altera_stock_ni_coleccion(self) -> None:
        restaurante = Restaurante()
        restaurante.registrar_usuario(Usuario("C001", "Ana", "ana@restaurante.com"))
        restaurante.registrar_producto(Producto("P001", "Pizza", "Comida", 15.00, 2))

        self.assertFalse(restaurante.vender_producto("P001", "C001", 3))
        self.assertFalse(restaurante.vender_producto("P001", "C001", 0))
        self.assertEqual(restaurante.buscar_producto("P001").stock, 2)
        self.assertEqual(restaurante.listar_ventas(), [])

    def test_guardar_y_cargar_usuarios_y_ventas(self) -> None:
        with tempfile.TemporaryDirectory() as carpeta_temporal:
            servicio = ArchivoServicio(
                str(Path(carpeta_temporal) / "productos.json"),
                str(Path(carpeta_temporal) / "usuarios.json"),
                str(Path(carpeta_temporal) / "ventas.json"),
            )
            usuarios = [Usuario("C001", "Ana", "ana@restaurante.com")]
            ventas = [Venta("C001", "P001", 2)]

            self.assertTrue(servicio.guardar_usuarios(usuarios))
            self.assertTrue(servicio.guardar_ventas(ventas))

            usuarios_cargados = servicio.cargar_usuarios()
            ventas_cargadas = servicio.cargar_ventas()
            self.assertIsInstance(usuarios_cargados[0], Usuario)
            self.assertIsInstance(ventas_cargadas[0], Venta)
            self.assertEqual(ventas_cargadas[0].producto_codigo, "P001")

    def test_cargar_ventas_reconstruye_indice_por_usuario(self) -> None:
        restaurante = Restaurante()
        ventas = [Venta("C001", "P001", 2), Venta("C001", "P002", 1)]

        restaurante.cargar_ventas(ventas)

        self.assertEqual(restaurante.consultar_ventas_usuario("C001"), ventas)
        self.assertEqual(restaurante.consultar_ventas_usuario("C002"), [])

    def test_servicio_crud_de_productos_persiste_los_cambios(self) -> None:
        with tempfile.TemporaryDirectory() as carpeta_temporal:
            ruta = Path(carpeta_temporal) / "productos.json"
            archivo = ArchivoServicio(str(ruta))
            servicio = RestauranteServicio([], [], [], archivo)

            servicio.registrar_producto("P010", "Sopa", "Comida", 5.5, 4)
            servicio.actualizar_producto("P010", "Sopa del día", "Especial", 6.0, 7)

            producto_guardado = ArchivoServicio(str(ruta)).cargar_productos()[0]
            self.assertEqual(producto_guardado.nombre, "Sopa del día")
            self.assertEqual(producto_guardado.stock, 7)

            servicio.eliminar_producto("P010")
            self.assertEqual(ArchivoServicio(str(ruta)).cargar_productos(), [])

    def test_registrar_venta_persiste_y_descuenta_stock(self) -> None:
        with tempfile.TemporaryDirectory() as carpeta_temporal:
            ruta_productos = Path(carpeta_temporal) / "productos.json"
            ruta_usuarios = Path(carpeta_temporal) / "usuarios.json"
            ruta_ventas = Path(carpeta_temporal) / "ventas.json"
            archivo = ArchivoServicio(str(ruta_productos), str(ruta_usuarios), str(ruta_ventas))
            servicio = RestauranteServicio([], [], [], archivo)

            servicio.registrar_usuario("C010", "Paola", "paola@restaurante.com", "1234")
            servicio.registrar_producto("P020", "Té frío", "Bebida", 4.5, 5)

            venta = servicio.registrar_venta("C010", "P020", 2)

            self.assertEqual(venta.cantidad, 2)
            self.assertEqual(servicio.buscar_producto("P020").stock, 3)
            self.assertEqual(len(servicio.listar_ventas()), 1)
            self.assertEqual(ArchivoServicio(str(ruta_productos), str(ruta_usuarios), str(ruta_ventas)).cargar_ventas()[0].cantidad, 2)

    def test_crud_usuarios_persiste_roles_y_protege_cuenta_activa(self) -> None:
        usuario_legacy = Usuario.from_dict({
            "identificacion": "C000",
            "nombre": "Cliente anterior",
            "correo": "cliente@restaurante.com",
        })
        self.assertEqual(usuario_legacy.rol, "Cliente")

        with tempfile.TemporaryDirectory() as carpeta_temporal:
            ruta = Path(carpeta_temporal) / "usuarios.json"
            archivo = ArchivoServicio(ruta_usuarios=str(ruta))
            administrador = Usuario("A001", "Admin", "admin@restaurante.com", rol="Administrador")
            servicio = RestauranteServicio([], [administrador], archivo_servicio=archivo)

            servicio.registrar_usuario("E001", "Eva", "eva@restaurante.com", "clave", "Empleado")
            servicio.actualizar_usuario("E001", "Eva Ruiz", "eva@restaurante.com", "Cliente")

            usuario_guardado = ArchivoServicio(ruta_usuarios=str(ruta)).cargar_usuarios()[1]
            self.assertEqual(usuario_guardado.nombre, "Eva Ruiz")
            self.assertEqual(usuario_guardado.rol, "Cliente")
            self.assertEqual(usuario_guardado.contrasena, "clave")

            with self.assertRaisesRegex(ValueError, "actualmente autenticada"):
                servicio.eliminar_usuario("E001", "E001")
            with self.assertRaisesRegex(ValueError, "Administrador"):
                servicio.eliminar_usuario("A001")

            servicio.eliminar_usuario("E001", "A001")
            self.assertEqual([usuario.identificacion for usuario in servicio.listar_usuarios()], ["A001"])


if __name__ == "__main__":
    unittest.main()
