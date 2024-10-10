from tkinter import ttk
from tkinter import *
import sqlite3

class VentanaPrincipal:
    db = 'database/productos.db'

    def __init__(self, root):
        self.ventana = root
        self.ventana.title("App Gestor de Productos") #Titulo de la ventana
        self.ventana.resizable(1,1) #Activar la redimension de la ventana
        self.ventana.wm_iconbitmap('recursos/icon.ico')

        #Contenedor Frame principal
        frame = LabelFrame(self.ventana, text = "Registrar un nuevo Producto", font=('Calibri', 16, 'bold'))
        frame.grid(row = 0, column = 0, columnspan = 3, pady = 20)

        #Label nombre
        self.etiqueta_nombre = Label(frame, text = "Nombre: ", font=('Calibri', 13)) #Etiqueta del nombre ubicado en el frame
        self.etiqueta_nombre.grid(row = 1, column = 0) #Posicionamiento a traves de grid

        #Entry Nombre (caja de texto que recibe el nombre)
        self.nombre = Entry(frame, font=('Calibri', 13)) #Caja de texto ubicada en el frame
        self.nombre.focus() #Para que el foco del raton vaya a Entry al inicio
        self.nombre.grid(row = 1, column = 1)

        #Label Precio
        self.etiqueta_precio = Label(frame, text = "Precio: ", font=('Calibri', 13))
        self.etiqueta_precio.grid(row = 2, column = 0)
        self.precio = Entry(frame, font=('Calibri', 13))
        self.precio.grid(row = 2, column = 1)

        #Label existencias
        self.etiqueta_existencias = Label(frame, text="Existencias: ", font=('Calibri', 13))
        self.etiqueta_existencias.grid(row=3, column=0)
        self.existencias = Entry(frame, font=('Calibri', 13))
        self.existencias.grid(row=3, column=1)

        #Boton Añadir producto
        s = ttk.Style()
        s.configure('my.TButton', font=('Calibri', 14, 'bold'))
        self.boton_aniadir = ttk.Button(frame, text = "Guardar Producto", command= self.add_producto, style='my.TButton')
        self.boton_aniadir.grid(row = 4, columnspan= 2, sticky= W+ E)

        #Tabla de Productos
        #Estilo personalizado para la tabla
        style = ttk.Style()
        style.configure("mystyle.Treeview", highlightthickness=0, bd=0, font=('Calibri', 11)) #Modifica la fuente de la tabla
        style.configure("mystyle.Treeview.Heading", font= ('Calibri', 13, 'bold')) #Fuente de Cabecera
        style.layout("mystyle.Treeview", [('mystyle.Treeview.treearea', {'sticky': 'nswe'})]) #Eliminar bordes

        #Estructura de la tabla
        self.tabla = ttk.Treeview(height=20, columns=('#1', '#2', '#3'), style="mystyle.Treeview")
        self.tabla.grid(row=5, column=0, columnspan= 2)
        self.tabla.heading('#0', text='Nombre', anchor=CENTER)
        self.tabla.heading('#1', text='Precio', anchor=CENTER)
        self.tabla.heading('#2', text='Existencias', anchor=CENTER)

        #Botones de Eliminar y Editar
        s = ttk.Style()
        s.configure('my.TButton', font=('Calibri', 14, 'bold'))
        self.boton_eliminar = ttk.Button(text= "ELIMINAR", command= self.del_producto, style='my.TButton')
        self.boton_eliminar.grid(row = 6, column = 0, sticky = W + E)
        self.boton_editar = ttk.Button(text= "EDITAR", command= self.edit_producto, style='my.TButton')
        self.boton_editar.grid(row = 6, column = 1, sticky= W + E)

        #Mensaje informativo para el usuario
        self.mensaje = Label(text= '', fg = 'red')
        self.mensaje.grid(row=3, column=0, columnspan=2, sticky= W + E)

        self.get_productos()

    def db_consulta(self, consulta, parametros = ()):
        with sqlite3.connect(self.db) as con: #Iniciamos una conexion con la base de datos (con)
            cursor = con.cursor() #Generamos un cursor de la conexion  para poder operar en la base de datos
            resultado = cursor.execute(consulta, parametros) #Preparar la consulta SQL
            con.commit() #Ejecutar la consulta SQL
        return resultado #Retornar el resultado de la consulta SQL

    def get_productos(self):

        # Limpiar la tabla existente
        registros_tabla = self.tabla.get_children()
        for fila in registros_tabla:
            self.tabla.delete(fila)

        query = "SELECT * FROM producto WHERE nombre IS NOT NULL AND precio IS NOT NULL AND existencias IS NOT NULL ORDER BY nombre DESC"
        registros = self.db_consulta(query)

        # Verificar si se obtuvieron resultados
        if not registros:
            print("No se encontraron productos en la base de datos.")
            return

        for fila in registros:
            try:
                if len(fila) >= 4:
                    self.tabla.insert('', 'end', text=fila[1], values=(fila[2], fila[3]))
                else:
                    print(f"Fila con datos incompletos: {fila}")
            except IndexError:
                print(f"Error de índice en la fila {fila}. Verifica la estructura de la tabla en la base de datos.")

    def validacion_nombre(self):
        return self.nombre.get().strip() != ""

    def validacion_precio(self):
        try:
            precio = float(self.precio.get())
            return precio > 0
        except ValueError:
            return False

    def validacion_existencias(self):
        try:
            existencias = int(self.existencias.get())
            return existencias >= 0
        except ValueError:
            return False

    def del_producto(self):
        # Debug
        # print(self.tabla.item(self.tabla.selection()))
        # print(self.tabla.item(self.tabla.selection())['text'])
        # print(self.tabla.item(self.tabla.selection())['values'])
        # print(self.tabla.item(self.tabla.selection())['values'][0])

        self.mensaje['text'] = ''  # Mensaje inicialmente vacio
        # Comprobacion de que se seleccione un producto para poder eliminarlo
        try:
            selected_item = self.tabla.item(self.tabla.selection())
            if selected_item:
                values = selected_item['values']
                if values:
                    nombre = selected_item['text']

                    self.mensaje['text'] = ''
                    nombre = self.tabla.item(self.tabla.selection())['text']
                    query = 'DELETE FROM producto WHERE nombre = ?'  # Consulta SQL
                    self.db_consulta(query, (nombre,))  # Ejecutar la consulta
                    self.mensaje['text'] = 'Producto {} eliminado con éxito'.format(nombre)
                    self.get_productos()  # Actualizar la tabla de productos

        except IndexError:
            self.mensaje['text'] = "Por favor, seleccione un producto"

    def edit_producto(self):
        try:
            nombre = self.tabla.item(self.tabla.selection())['text']
            precio = self.tabla.item(self.tabla.selection())['values'][0]
            existencias = self.tabla.item(self.tabla.selection())['values'][1]
            VentanaEditarProducto(self, nombre, precio, existencias, self.mensaje)
        except IndexError:
            self.mensaje['text'] = 'Por favor, seleccione un producto'

    def add_producto(self):
        errores = []

        nombre = self.nombre.get().strip()
        precio = self.precio.get().strip()
        existencias = self.existencias.get().strip()

        if not nombre and not precio and not existencias:
            self.mensaje['text'] = 'Por favor, introduce los datos'
            return

        if not nombre:
            errores.append('El nombre es obligatorio y no puede estar vacío')

        if not precio:
            errores.append('El precio es obligatorio')
        elif not precio.replace('.', '', 1).isdigit():
            errores.append('Por favor, introduzca un valor numérico en el precio')

        if not existencias:
            errores.append('Las existencias son obligatorias')
        elif not existencias.isdigit():
            errores.append('Por favor, introduzca un valor numérico en las existencias')

        if errores:
            self.mensaje['text'] = '\n'.join(errores)
            return

        query = 'INSERT INTO producto VALUES(NULL, ?, ?, ?)'
        parametros = (self.nombre.get(), self.precio.get(), self.existencias.get())
        self.db_consulta(query, parametros)
        print("Datos guardados")
        self.mensaje['text'] = 'Producto {} añadido con éxito'.format(self.nombre.get())
        self.nombre.delete(0, END) #Borrar el nombre
        self.precio.delete(0, END) #Borrar el precio
        self.existencias.delete(0, END)
        # Debug
        # print(self.nombre.get())
        # print(self.precio.get())
        # print (self.existencias.get())
        self.get_productos()  #Cuando se finalice la insercion de datos volvemos a invocar este metodo para actualizar el contenido

class VentanaEditarProducto:
    def __init__(self, ventana_principal, nombre, precio, existencias, mensaje):
        self.ventana_principal = ventana_principal
        self.nombre = nombre
        self.precio = precio
        self.existencias = existencias
        self.mensaje = mensaje
        self.ventana_editar = Toplevel()
        self.ventana_editar.title("Editar Producto")

        #Creación del contenedor de Frame para la edición del producto
        frame_ep = LabelFrame(self.ventana_editar, text= "Editar el siguiente producto", font=('Calibri', 16, 'bold'))
        frame_ep.grid(row= 0, column= 0, columnspan= 2, pady= 20, padx= 20)

        #Label y Entry para el nombre antiguo (solo lectura)
        Label(frame_ep, text="Nombre antiguo: ", font=('Calibri', 13)).grid(row=1, column=0)
        Entry(frame_ep, textvariable=StringVar(self.ventana_editar, value=nombre), state='readonly', font=('Calibri', 13)).grid(row=1, column=1)

        #Label y Entry para el nombre nuevo
        Label(frame_ep, text="Nombre nuevo: ", font=('Calibri', 13)).grid(row=2, column=0)
        self.input_nombre_nuevo = Entry(frame_ep, font=('Calibri', 13))
        self.input_nombre_nuevo.grid(row=2, column=1)
        self.input_nombre_nuevo.focus()

        #Precio antiguo (solo lectura)
        Label(frame_ep, text="Precio antiguo: ", font=('Calibri', 13)).grid(row=3, column=0)
        Entry(frame_ep, textvariable=StringVar(self.ventana_editar, value=precio), state='readonly', font=('Calibri', 13)).grid(row=3, column=1)

        #Precio nuevo
        Label(frame_ep, text="Precio nuevo: ", font=('Calibri', 13)).grid(row=4, column=0)
        self.input_precio_nuevo = Entry(frame_ep, font=('Calibri', 13))
        self.input_precio_nuevo.grid(row=4, column=1)

        #Existencias antiguas (solo lectura)
        Label(frame_ep, text="Existencias antiguas: ", font=('Calibri', 13)).grid(row=5, column=0)
        Entry(frame_ep, textvariable=StringVar(self.ventana_editar, value=existencias), state='readonly', font=('Calibri', 13)).grid(row=5, column=1)

        #Existencias nuevas
        Label(frame_ep, text="Existencias nuevas: ", font=('Calibri', 13)).grid(row=6, column=0)
        self.input_existencias_nuevas = Entry(frame_ep, font=('Calibri', 13))
        self.input_existencias_nuevas.grid(row=6, column=1)

        #Boton actualizar producto
        ttk.Style().configure('my.TButton', font=('Calibri', 14, 'bold'))
        #Ejemplo de cómo creamos y configuramos el estilo de una sola linea

        ttk.Button(frame_ep, text="Actualizar Producto", style='my.TButton', command=self.actualizar).grid(row=7, columnspan= 2, sticky= W + E)

    def actualizar(self):
        nuevo_nombre = self.input_nombre_nuevo.get() or self.nombre
        nuevo_precio = self.input_precio_nuevo.get() or self.precio
        nuevas_existencias = self.input_existencias_nuevas.get() or self.existencias

        if nuevo_nombre and nuevo_precio and nuevas_existencias.isdigit():
            query = 'UPDATE producto SET nombre = ?, precio = ?, existencias = ? WHERE nombre = ?'
            parametros = (nuevo_nombre, nuevo_precio, nuevas_existencias, self.nombre)
            self.ventana_principal.db_consulta(query, parametros)
            self.mensaje['text'] = f'El producto {self.nombre} ha sido actualizado con éxito'
        else:
            self.mensaje['text'] = f'No se pudo actualizar el producto {self.nombre}'

        self.ventana_editar.destroy()
        self.ventana_principal.get_productos()

if __name__== '__main__':
    root = Tk() #Instancia de la ventana principal
    app = VentanaPrincipal(root) #Se envia a la clase VentanaPrincipal el control sobre la ventana root
    root.mainloop() #Bucle de la aplicación

