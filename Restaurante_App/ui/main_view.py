from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Callable

from modelos.producto import Producto
from modelos.usuario import Usuario
from servicios.restaurante_servicio import RestauranteServicio
from ui.brand import BrandLockup


class MainView(tk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        servicio: RestauranteServicio,
        usuario: Usuario,
        cerrar_sesion: Callable[[], None],
    ) -> None:
        super().__init__(master, padx=24, pady=20)
        self.servicio = servicio
        self.usuario = usuario
        self.cerrar_sesion = cerrar_sesion
        self._crear_controles()

    def _crear_controles(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        encabezado = ttk.Frame(self)
        encabezado.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        encabezado.columnconfigure(1, weight=1)
        BrandLockup(encabezado).grid(row=0, column=0, sticky="w")
        ttk.Label(encabezado, text=self.usuario.nombre).grid(row=0, column=1, sticky="e", padx=(0, 12))
        ttk.Button(encabezado, text="Cerrar sesión", command=self.cerrar_sesion).grid(row=0, column=2, padx=(12, 0))
        descripcion = "Administre el catálogo y registre ventas del restaurante."
        if self.usuario.rol == "Administrador":
            descripcion = "Administre el catálogo, los usuarios y las ventas del restaurante."
        ttk.Label(self, text=descripcion).grid(row=1, column=0, sticky="w", pady=(0, 12))

        self.pestanas = ttk.Notebook(self)
        self.pestanas.grid(row=2, column=0, sticky="nsew")

        productos_tab = ttk.Frame(self.pestanas, padding=14)
        ventas_tab = ttk.Frame(self.pestanas, padding=14)

        self.pestanas.add(productos_tab, text="Productos")
        if self.usuario.rol == "Administrador":
            usuarios_tab = ttk.Frame(self.pestanas, padding=14)
            self.pestanas.add(usuarios_tab, text="Usuarios")
            self._crear_pestana_usuarios(usuarios_tab)
        self.pestanas.add(ventas_tab, text="Ventas")

        self._crear_pestana_productos(productos_tab)
        self._crear_pestana_ventas(ventas_tab)

    def _crear_pestana_productos(self, contenedor: ttk.Frame) -> None:
        contenedor.columnconfigure(1, weight=1)
        contenedor.rowconfigure(0, weight=1)

        formulario = ttk.LabelFrame(contenedor, text="Datos del producto", padding=12)
        formulario.grid(row=0, column=0, sticky="ns", padx=(0, 14))

        campos = (("Código", "codigo"), ("Nombre", "nombre"), ("Categoría", "categoria"), ("Precio (USD)", "precio"), ("Stock", "stock"))
        self.campos: dict[str, tk.StringVar] = {}
        for fila, (etiqueta, clave) in enumerate(campos):
            self.campos[clave] = tk.StringVar()
            ttk.Label(formulario, text=etiqueta).grid(row=fila * 2, column=0, sticky="w", pady=(0, 3))
            ttk.Entry(formulario, textvariable=self.campos[clave], width=27).grid(row=fila * 2 + 1, column=0, sticky="ew", pady=(0, 9))

        acciones = ttk.Frame(formulario)
        acciones.grid(row=10, column=0, sticky="ew", pady=(4, 0))
        acciones.columnconfigure(0, weight=1)
        acciones.columnconfigure(1, weight=1)
        ttk.Button(acciones, text="Registrar", command=self.registrar_producto).grid(row=0, column=0, sticky="ew", padx=(0, 4), pady=3)
        ttk.Button(acciones, text="Actualizar", command=self.actualizar_producto).grid(row=0, column=1, sticky="ew", padx=(4, 0), pady=3)
        ttk.Button(acciones, text="Cargar / consultar", command=self.cargar_producto).grid(row=1, column=0, columnspan=2, sticky="ew", pady=3)
        ttk.Button(acciones, text="Eliminar", command=self.eliminar_producto).grid(row=2, column=0, columnspan=2, sticky="ew", pady=3)
        ttk.Button(acciones, text="Limpiar formulario", command=self._limpiar_formulario).grid(row=3, column=0, columnspan=2, sticky="ew", pady=3)

        listado = ttk.LabelFrame(contenedor, text="Productos registrados", padding=10)
        listado.grid(row=0, column=1, sticky="nsew")
        listado.columnconfigure(0, weight=1)
        listado.rowconfigure(0, weight=1)

        columnas = ("codigo", "nombre", "categoria", "precio", "stock")
        self.tabla_productos = ttk.Treeview(listado, columns=columnas, show="headings", selectmode="browse")
        encabezados = {"codigo": "Código", "nombre": "Nombre", "categoria": "Categoría", "precio": "Precio (USD)", "stock": "Stock"}
        anchos = {"codigo": 85, "nombre": 190, "categoria": 105, "precio": 90, "stock": 65}
        for columna in columnas:
            self.tabla_productos.heading(columna, text=encabezados[columna])
            self.tabla_productos.column(columna, width=anchos[columna], anchor="w")

        barra = ttk.Scrollbar(listado, orient="vertical", command=self.tabla_productos.yview)
        self.tabla_productos.configure(yscrollcommand=barra.set)
        self.tabla_productos.grid(row=0, column=0, sticky="nsew")
        barra.grid(row=0, column=1, sticky="ns")
        ttk.Button(listado, text="Cargar seleccionado", command=self.cargar_seleccionado).grid(row=1, column=0, columnspan=2, sticky="e", pady=(10, 0))
        self._actualizar_tabla_productos()

    def _crear_pestana_usuarios(self, contenedor: ttk.Frame) -> None:
        contenedor.columnconfigure(1, weight=1)
        contenedor.rowconfigure(0, weight=1)

        formulario = ttk.LabelFrame(contenedor, text="Datos del usuario", padding=12)
        formulario.grid(row=0, column=0, sticky="ns", padx=(0, 14))
        formulario.columnconfigure(0, weight=1)

        self.campos_usuario: dict[str, tk.StringVar] = {}
        for fila, (etiqueta, clave) in enumerate((
            ("Identificación", "identificacion"),
            ("Nombre", "nombre"),
            ("Correo", "correo"),
            ("Contraseña", "contrasena"),
        )):
            self.campos_usuario[clave] = tk.StringVar()
            ttk.Label(formulario, text=etiqueta).grid(row=fila * 2, column=0, sticky="w", pady=(0, 3))
            entrada = ttk.Entry(formulario, textvariable=self.campos_usuario[clave], width=28)
            entrada.grid(row=fila * 2 + 1, column=0, sticky="ew", pady=(0, 8))
            if clave == "contrasena":
                entrada.configure(show="*")
            if clave == "identificacion":
                self.entrada_identificacion_usuario = entrada
            entrada.bind("<Return>", self._evento_return_usuario)
            entrada.bind("<Escape>", self._evento_escape_usuario)

        ttk.Label(formulario, text="Rol").grid(row=8, column=0, sticky="w", pady=(0, 3))
        self.rol_usuario = ttk.Combobox(formulario, state="readonly", values=("Empleado", "Cliente"), width=25)
        self.rol_usuario.grid(row=9, column=0, sticky="ew", pady=(0, 5))
        self.rol_usuario.set("Cliente")
        self.rol_usuario.bind("<<ComboboxSelected>>", self._evento_rol_usuario)
        self.rol_usuario.bind("<Return>", self._evento_return_usuario)
        self.rol_usuario.bind("<Escape>", self._evento_escape_usuario)

        self.estado_usuario = tk.StringVar(value="Seleccione un rol para el nuevo usuario.")
        ttk.Label(formulario, textvariable=self.estado_usuario, wraplength=225).grid(row=10, column=0, sticky="w", pady=(0, 8))

        acciones = ttk.Frame(formulario)
        acciones.grid(row=11, column=0, sticky="ew")
        acciones.columnconfigure(0, weight=1)
        acciones.columnconfigure(1, weight=1)
        ttk.Button(acciones, text="Registrar", command=self.registrar_usuario).grid(row=0, column=0, sticky="ew", padx=(0, 4), pady=3)
        ttk.Button(acciones, text="Actualizar", command=self.actualizar_usuario).grid(row=0, column=1, sticky="ew", padx=(4, 0), pady=3)
        ttk.Button(acciones, text="Eliminar", command=self.eliminar_usuario).grid(row=1, column=0, sticky="ew", padx=(0, 4), pady=3)
        ttk.Button(acciones, text="Limpiar", command=self._limpiar_formulario_usuario).grid(row=1, column=1, sticky="ew", padx=(4, 0), pady=3)

        listado = ttk.LabelFrame(contenedor, text="Empleados y clientes registrados", padding=10)
        listado.grid(row=0, column=1, sticky="nsew")
        listado.columnconfigure(0, weight=1)
        listado.rowconfigure(1, weight=1)

        ruta_icono = Path(__file__).resolve().parent.parent / "assets" / "usuarios.xbm"
        if ruta_icono.exists():
            self.icono_usuarios = tk.BitmapImage(master=self, file=str(ruta_icono), foreground="#1f4d3d")
            ttk.Label(listado, image=self.icono_usuarios, text=" Usuarios del restaurante", compound="left").grid(row=0, column=0, sticky="w", pady=(0, 8))

        columnas = ("identificacion", "nombre", "correo", "rol")
        self.tabla_usuarios = ttk.Treeview(listado, columns=columnas, show="headings", selectmode="browse")
        for columna, titulo, ancho in (("identificacion", "Identificación", 105), ("nombre", "Nombre", 155), ("correo", "Correo", 205), ("rol", "Rol", 95)):
            self.tabla_usuarios.heading(columna, text=titulo)
            self.tabla_usuarios.column(columna, width=ancho, anchor="w")

        barra = ttk.Scrollbar(listado, orient="vertical", command=self.tabla_usuarios.yview)
        self.tabla_usuarios.configure(yscrollcommand=barra.set)
        self.tabla_usuarios.grid(row=1, column=0, sticky="nsew")
        barra.grid(row=1, column=1, sticky="ns")
        self.tabla_usuarios.bind("<<TreeviewSelect>>", self._evento_seleccion_usuario)
        self.tabla_usuarios.bind("<Escape>", self._evento_escape_usuario)
        self._actualizar_tabla_usuarios()

    def _evento_seleccion_usuario(self, event: tk.Event) -> None:
        seleccion = self.tabla_usuarios.selection()
        if seleccion:
            self._cargar_usuario(seleccion[0])

    def _evento_return_usuario(self, event: tk.Event) -> str:
        self.registrar_usuario()
        return "break"

    def _evento_escape_usuario(self, event: tk.Event) -> str:
        self._limpiar_formulario_usuario()
        return "break"

    def _evento_rol_usuario(self, event: tk.Event) -> None:
        self.estado_usuario.set(f"El usuario se registrará con el rol {self.rol_usuario.get()}.")

    def _cargar_usuario(self, identificacion: str) -> None:
        usuario = self.servicio.buscar_usuario(identificacion)
        if usuario is None or usuario.rol == "Administrador":
            return
        self.campos_usuario["identificacion"].set(usuario.identificacion)
        self.campos_usuario["nombre"].set(usuario.nombre)
        self.campos_usuario["correo"].set(usuario.correo)
        self.campos_usuario["contrasena"].set("")
        self.rol_usuario.set(usuario.rol)
        self.entrada_identificacion_usuario.state(["readonly"])
        self.estado_usuario.set("Deje la contraseña vacía para conservarla.")

    def registrar_usuario(self) -> None:
        try:
            self.servicio.registrar_usuario(
                self.campos_usuario["identificacion"].get(),
                self.campos_usuario["nombre"].get(),
                self.campos_usuario["correo"].get(),
                self.campos_usuario["contrasena"].get(),
                self.rol_usuario.get(),
            )
        except (ValueError, OSError) as error:
            messagebox.showerror("No se pudo registrar", str(error))
            return
        self._actualizar_tabla_usuarios()
        self._actualizar_selector_ventas()
        self._limpiar_formulario_usuario()
        messagebox.showinfo("Usuario registrado", "El usuario se guardó correctamente.")

    def actualizar_usuario(self) -> None:
        seleccion = self.tabla_usuarios.selection()
        if not seleccion:
            messagebox.showwarning("Sin selección", "Seleccione un usuario de la tabla para actualizarlo.")
            return
        identificacion = seleccion[0]
        try:
            self.servicio.actualizar_usuario(
                identificacion,
                self.campos_usuario["nombre"].get(),
                self.campos_usuario["correo"].get(),
                self.rol_usuario.get(),
                self.campos_usuario["contrasena"].get(),
            )
        except (ValueError, OSError) as error:
            messagebox.showerror("No se pudo actualizar", str(error))
            return
        self._actualizar_tabla_usuarios()
        self.tabla_usuarios.selection_set(identificacion)
        self._cargar_usuario(identificacion)
        self._actualizar_selector_ventas()
        messagebox.showinfo("Usuario actualizado", "Los cambios se guardaron correctamente.")

    def eliminar_usuario(self) -> None:
        seleccion = self.tabla_usuarios.selection()
        if not seleccion:
            messagebox.showwarning("Sin selección", "Seleccione un usuario de la tabla para eliminarlo.")
            return
        identificacion = seleccion[0]
        if identificacion == self.usuario.identificacion:
            messagebox.showwarning("Cuenta protegida", "No puede eliminar la cuenta actualmente autenticada.")
            return
        if not messagebox.askyesno("Confirmar eliminación", f"¿Desea eliminar al usuario {identificacion}?"):
            return
        try:
            self.servicio.eliminar_usuario(identificacion, self.usuario.identificacion)
        except (ValueError, OSError) as error:
            messagebox.showerror("No se pudo eliminar", str(error))
            return
        self._actualizar_tabla_usuarios()
        self._actualizar_selector_ventas()
        self._limpiar_formulario_usuario()
        messagebox.showinfo("Usuario eliminado", "El usuario dejó de estar disponible.")

    def _limpiar_formulario_usuario(self) -> None:
        for campo in self.campos_usuario.values():
            campo.set("")
        self.rol_usuario.set("Cliente")
        self.entrada_identificacion_usuario.state(["!readonly"])
        for seleccion in self.tabla_usuarios.selection():
            self.tabla_usuarios.selection_remove(seleccion)
        self.estado_usuario.set("Formulario limpio. Seleccione un rol para continuar.")

    def _crear_pestana_ventas(self, contenedor: ttk.Frame) -> None:
        contenedor.columnconfigure(0, weight=1)
        contenedor.columnconfigure(1, weight=1)
        contenedor.rowconfigure(0, weight=1)

        formulario = ttk.LabelFrame(contenedor, text="Registrar venta", padding=16)
        formulario.grid(row=0, column=0, sticky="ns", padx=(0, 14))
        formulario.columnconfigure(0, weight=1)

        cabecera = tk.Frame(formulario, bg="#eef9f1", padx=12, pady=10)
        cabecera.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        cabecera.columnconfigure(0, weight=1)
        tk.Label(cabecera, text="Nueva venta", font=("Segoe UI", 12, "bold"), bg="#eef9f1", fg="#1f4d3d").grid(row=0, column=0, sticky="w")
        tk.Label(cabecera, text="Seleccione un cliente y un producto para registrar la operación.", bg="#eef9f1", fg="#4a5568").grid(row=1, column=0, sticky="w")

        ttk.Label(formulario, text="Usuario").grid(row=1, column=0, sticky="w", pady=(0, 4))
        self.usuario_seleccion = ttk.Combobox(formulario, state="readonly", width=30)
        self.usuario_seleccion.grid(row=2, column=0, sticky="ew", pady=(0, 10))

        ttk.Label(formulario, text="Producto").grid(row=3, column=0, sticky="w", pady=(0, 4))
        self.producto_seleccion = ttk.Combobox(formulario, state="readonly", width=30)
        self.producto_seleccion.grid(row=4, column=0, sticky="ew", pady=(0, 10))

        ttk.Label(formulario, text="Cantidad").grid(row=5, column=0, sticky="w", pady=(0, 4))
        self.cantidad_venta = tk.StringVar(value="1")
        ttk.Entry(formulario, textvariable=self.cantidad_venta, width=30).grid(row=6, column=0, sticky="ew", pady=(0, 12))

        ttk.Button(formulario, text="Registrar venta", command=self.registrar_venta).grid(row=7, column=0, sticky="ew", ipadx=8, ipady=4)
        self._actualizar_selector_ventas()

        listado = ttk.LabelFrame(contenedor, text="Ventas registradas", padding=10)
        listado.grid(row=0, column=1, sticky="nsew")
        listado.columnconfigure(0, weight=1)
        listado.rowconfigure(0, weight=1)

        self.tabla_ventas = ttk.Treeview(listado, columns=("usuario", "producto", "cantidad", "fecha"), show="headings", height=16)
        for columna, titulo, ancho in (("usuario", "Usuario", 130), ("producto", "Producto", 130), ("cantidad", "Cantidad", 80), ("fecha", "Fecha", 175)):
            self.tabla_ventas.heading(columna, text=titulo)
            self.tabla_ventas.column(columna, width=ancho, anchor="w")

        barra = ttk.Scrollbar(listado, orient="vertical", command=self.tabla_ventas.yview)
        self.tabla_ventas.configure(yscrollcommand=barra.set)
        self.tabla_ventas.grid(row=0, column=0, sticky="nsew")
        barra.grid(row=0, column=1, sticky="ns")
        self._actualizar_tabla_ventas()

    def _actualizar_tabla_productos(self) -> None:
        for elemento in self.tabla_productos.get_children():
            self.tabla_productos.delete(elemento)
        for producto in self.servicio.listar_productos():
            self.tabla_productos.insert("", "end", iid=producto.codigo, values=(producto.codigo, producto.nombre, producto.categoria, f"{producto.precio:.2f}", producto.stock))

    def _actualizar_tabla_usuarios(self) -> None:
        for elemento in self.tabla_usuarios.get_children():
            self.tabla_usuarios.delete(elemento)
        for usuario in self.servicio.listar_usuarios():
            if usuario.rol != "Administrador":
                self.tabla_usuarios.insert(
                    "",
                    "end",
                    iid=usuario.identificacion,
                    values=(usuario.identificacion, usuario.nombre, usuario.correo, usuario.rol),
                )

    def _actualizar_tabla_ventas(self) -> None:
        for elemento in self.tabla_ventas.get_children():
            self.tabla_ventas.delete(elemento)
        for venta in self.servicio.listar_ventas():
            self.tabla_ventas.insert("", "end", values=(venta.usuario_id, venta.producto_codigo, venta.cantidad, venta.fecha))

    def _actualizar_selector_ventas(self) -> None:
        usuarios = self.servicio.listar_usuarios()
        productos = self.servicio.listar_productos()

        if usuarios:
            self.usuario_seleccion["values"] = [usuario.identificacion for usuario in usuarios]
            self.usuario_seleccion.current(0)
        else:
            self.usuario_seleccion.set("")
            self.usuario_seleccion["values"] = []

        if productos:
            self.producto_seleccion["values"] = [f"{producto.codigo} - {producto.nombre}" for producto in productos]
            self.producto_seleccion.current(0)
        else:
            self.producto_seleccion.set("")
            self.producto_seleccion["values"] = []

    def _datos_formulario(self) -> tuple[str, str, str, float, int]:
        try:
            precio = float(self.campos["precio"].get().replace(",", "."))
            stock = int(self.campos["stock"].get())
        except ValueError as error:
            raise ValueError("Precio y stock deben ser valores numéricos válidos.") from error
        return (self.campos["codigo"].get(), self.campos["nombre"].get(), self.campos["categoria"].get(), precio, stock)

    def registrar_producto(self) -> None:
        try:
            self.servicio.registrar_producto(*self._datos_formulario())
        except (ValueError, OSError) as error:
            messagebox.showerror("No se pudo registrar", str(error))
            return
        self._actualizar_tabla_productos()
        self._actualizar_selector_ventas()
        self._limpiar_formulario()
        messagebox.showinfo("Producto registrado", "El producto se guardó correctamente.")

    def cargar_producto(self) -> None:
        producto = self.servicio.buscar_producto(self.campos["codigo"].get())
        if producto is None:
            messagebox.showwarning("Producto no encontrado", "Ingrese un código existente para consultar.")
            return
        self._mostrar_producto(producto)

    def cargar_seleccionado(self) -> None:
        seleccion = self.tabla_productos.selection()
        if not seleccion:
            messagebox.showwarning("Sin selección", "Seleccione un producto de la tabla.")
            return
        producto = self.servicio.buscar_producto(seleccion[0])
        if producto is not None:
            self._mostrar_producto(producto)

    def actualizar_producto(self) -> None:
        try:
            self.servicio.actualizar_producto(*self._datos_formulario())
        except (ValueError, OSError) as error:
            messagebox.showerror("No se pudo actualizar", str(error))
            return
        self._actualizar_tabla_productos()
        self._actualizar_selector_ventas()
        messagebox.showinfo("Producto actualizado", "Los cambios se guardaron correctamente.")

    def eliminar_producto(self) -> None:
        codigo = self.campos["codigo"].get().strip()
        if not codigo:
            messagebox.showwarning("Código requerido", "Ingrese o cargue un código de producto.")
            return
        if not messagebox.askyesno("Confirmar eliminación", f"¿Desea eliminar el producto {codigo}?"):
            return
        try:
            self.servicio.eliminar_producto(codigo)
        except (ValueError, OSError) as error:
            messagebox.showerror("No se pudo eliminar", str(error))
            return
        self._actualizar_tabla_productos()
        self._actualizar_selector_ventas()
        self._limpiar_formulario()
        messagebox.showinfo("Producto eliminado", "El producto dejó de estar disponible.")

    def registrar_venta(self) -> None:
        if not self.usuario_seleccion.get() or not self.producto_seleccion.get():
            messagebox.showwarning("Selección incompleta", "Debe elegir un usuario y un producto antes de registrar la venta.")
            return

        identificacion = self.usuario_seleccion.get().strip()
        producto_seleccionado = self.producto_seleccion.get().strip()
        codigo_producto = producto_seleccionado.split(" - ", 1)[0].strip()

        try:
            cantidad = int(self.cantidad_venta.get())
        except ValueError:
            messagebox.showerror("Cantidad inválida", "La cantidad debe ser un número entero válido.")
            return

        try:
            venta = self.servicio.registrar_venta(identificacion, codigo_producto, cantidad)
        except (ValueError, OSError) as error:
            messagebox.showerror("No se pudo registrar la venta", str(error))
            return

        self._actualizar_tabla_ventas()
        self._actualizar_tabla_productos()
        self.cantidad_venta.set("1")
        messagebox.showinfo("Venta registrada", f"Se registró la venta de {venta.cantidad} unidades para {venta.usuario_id}.")

    def _mostrar_producto(self, producto: Producto) -> None:
        valores = {"codigo": producto.codigo, "nombre": producto.nombre, "categoria": producto.categoria, "precio": str(producto.precio), "stock": str(producto.stock)}
        for clave, valor in valores.items():
            self.campos[clave].set(valor)

    def _limpiar_formulario(self) -> None:
        for campo in self.campos.values():
            campo.set("")