# Semana 16 - Smock Rock and Grill

Esta entrega evoluciona el restaurante de la Semana 15. Conserva el inicio de sesión, la gestión de productos, el registro de ventas y la arquitectura modular, y amplía la gestión de usuarios para practicar eventos de Tkinter.

## Gestión de usuarios

El modelo `Usuario` incluye los roles `Administrador`, `Empleado` y `Cliente`. Solo el Administrador autenticado ve la pestaña de gestión. Desde allí puede registrar, consultar, actualizar y eliminar usuarios Empleado y Cliente. La cuenta Administrador no se muestra entre los registros administrables y el servicio rechaza su modificación o eliminación; también protege la cuenta actualmente autenticada.

La tabla presenta identificación, nombre, correo y rol. No expone contraseñas. Al seleccionar una fila, `<<TreeviewSelect>>` activa un callback con `bind()`. Este obtiene el identificador de la fila, consulta el objeto mediante `RestauranteServicio.buscar_usuario()` y carga sus datos en el formulario. La contraseña se conserva si se actualiza el registro dejando ese campo vacío.

## Eventos

- `bind("<<TreeviewSelect>>", ...)` carga en el formulario al usuario seleccionado.
- `bind("<<ComboboxSelected>>", ...)` responde al rol elegido y actualiza el estado del formulario.
- `bind("<Return>", ...)` reutiliza el método de registro como atajo de teclado.
- `bind("<Escape>", ...)` limpia el formulario y cancela la selección.
- Los botones Registrar, Actualizar, Eliminar y Limpiar usan `command=`.

`bind()` conecta eventos de widgets o teclado con callbacks que reciben el evento. `command=` ejecuta callbacks sencillos desde botones. En ambos casos, la vista coordina y muestra el resultado; las validaciones, reglas y persistencia permanecen en `RestauranteServicio` y `ArchivoServicio`.

## Persistencia y archivos

Los usuarios y sus roles se guardan en `datos/usuarios.json`. Los registros anteriores sin rol se cargan como `Cliente`; los datos de ejemplo identifican a `C001` como Administrador y a `C002` como Cliente. Productos y ventas continúan usando sus respectivos archivos JSON.

```text
datos/       productos.json, usuarios.json, ventas.json
modelos/     producto.py, usuario.py, venta.py
servicios/   archivo_servicio.py, restaurante_servicio.py
ui/          login_view.py, main_view.py
assets/      logo.xbm, usuarios.xbm
main.py
```

## Ejecución

Desde la carpeta del proyecto, ejecute:

```powershell
python main.py
```

Credenciales de ejemplo: identificación `C001`, contraseña `1234`.

## Pruebas

```powershell
python -m unittest discover -s tests -v
```

La autenticación y las contraseñas son únicamente para fines educativos; no es un sistema de seguridad para producción.