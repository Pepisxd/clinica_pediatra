import customtkinter as ctk
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from db_connection import conexion_db

class EditUserWindow(ctk.CTkToplevel):
    def __init__(self, parent, user_data, on_save):
        super().__init__(parent)
        self.title("Editar Usuario")
        self.geometry("400x500")
        
        # Callback para guardado
        self.user_data = user_data
        self.on_save = on_save
        
        # Roles disponibles
        self.roles = {"Admin": 1, "Doctor": 2, "Secretaria": 3}
        
        # Ventana modal
        self.transient(parent)
        self.grab_set()
        
        # Crear widgets
        self.create_widgets()
        
    def create_widgets(self):
        # Título
        title = ctk.CTkLabel(self, text="Editar Usuario", font=("Arial", 20, "bold"))
        title.pack(pady=20)
        
        # Frame para el formulario
        form_frame = ctk.CTkFrame(self)
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Campos para nombre y email
        fields = [
            ("Nombre:", self.user_data[0]),
            ("Email:", self.user_data[1])
        ]
        
        self.entries = {}
        for label_text, default_value in fields:
            field_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
            field_frame.pack(fill="x", pady=10)
            
            label = ctk.CTkLabel(field_frame, text=label_text)
            label.pack(anchor="w")
            
            entry = ctk.CTkEntry(field_frame)
            entry.pack(fill="x", pady=(5, 0))
            entry.insert(0, default_value)
            
            self.entries[label_text] = entry
        
        # ComboBox de rol
        role_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        role_frame.pack(fill="x", pady=10)
        
        role_label = ctk.CTkLabel(role_frame, text="Rol:")
        role_label.pack(anchor="w")
        
        self.role_combobox = ctk.CTkComboBox(
            role_frame,
            values=list(self.roles.keys()),
            state="readonly"
        )
        self.role_combobox.pack(fill="x", pady=(5, 0))
        self.role_combobox.set(self.user_data[2] if self.user_data[2] in self.roles else "Admin")
        
        # Botones de guardar y cancelar
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkButton(button_frame, text="Cancelar", command=self.destroy, fg_color="gray").pack(side="left", padx=5, expand=True)
        ctk.CTkButton(button_frame, text="Guardar", command=self.save_changes).pack(side="left", padx=5, expand=True)
        
    def save_changes(self):
        # Validar campos y rol
        nombre = self.entries["Nombre:"].get().strip()
        email = self.entries["Email:"].get().strip()
        rol_text = self.role_combobox.get()
        rol = self.roles.get(rol_text, 1)
        
        if not nombre or not email or "@" not in email or "." not in email:
            messagebox.showerror("Error", "Todos los campos son requeridos con email válido")
            return
        
        # Conectar a la base de datos y actualizar
        user_id = self.user_data[0]
        connection = conexion_db()
        cursor = connection.cursor()
        try:
            cursor.execute("UPDATE Usuario SET Nombre = %s, Correo = %s, Rol = %s WHERE ID_Usuario = %s", (nombre, email, rol, user_id))
            connection.commit()
            updated_data = (user_id, nombre, email, rol)
            self.on_save(updated_data)
            self.destroy()
        except Exception as e:
            connection.rollback()
            print(e)
            messagebox.showerror("Error", "Ocurrió un error al guardar los cambios")
        finally:
            cursor.close()
            connection.close()


class AdminDashboard(ctk.CTk):
    def __init__(self, user_data=None):
        super().__init__()
        # Configuración inicial
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # Almacena los datos de los usuarios
        self.user_data = user_data if user_data else {}
        self.users_data = [
            ("Juan Pérez", "juan@example.com", "Admin"),
            ("María García", "maria@example.com", "Doctor")
        ]

        # Ventana principal
        self.title("Panel de Administrador")
        self.geometry("1200x700")

        self.active_frame = None
        self.current_tab = "users"

        self.create_layout()
        
    def create_layout(self):
        # Frame principal que divide la pantalla en sidebar y contenido
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True)
        
        # Sidebar
        self.create_sidebar()
        
        # Área de contenido principal
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content_frame.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        
        # Crear cards de métricas
        self.create_metric_cards()
        
        # Mostrar el contenido inicial (usuarios)
        self.show_users()

    def create_sidebar(self):
        sidebar = ctk.CTkFrame(self.main_frame, width=200)
        sidebar.pack(side="left", fill="y", padx=10, pady=10)
        
        # Título del sidebar
        user_name = f"{self.user_data.get('nombre', '')} {self.user_data.get('apellidos', '')}"
        title = ctk.CTkLabel(sidebar, text=f"Bienvenido\n{user_name}", 
                           font=("Arial", 20, "bold"), wraplength=180)
        title.pack(pady=20, padx=10)

         # Rol del usuario
        rol_text = "Administrador" if self.user_data.get('rol') == 1 else "Usuario"
        rol_label = ctk.CTkLabel(sidebar, text=rol_text, font=("Arial", 14))
        rol_label.pack(pady=(0, 20), padx=10)       

        # Botones de navegación
        buttons_data = [
            ("Usuarios", "users", self.show_users),
            ("Servicios", "services", self.show_services),
            ("Reportes", "reports", self.show_reports),
            ("Cerrar Sesión", "logout", self.quit)
        ]
        
        for text, tab, command in buttons_data:
            btn = ctk.CTkButton(
                sidebar,
                text=text,
                command=command,
                anchor="w",
                height=40
            )
            btn.pack(fill="x", padx=10, pady=5)
    
    def create_metric_cards(self):
        metrics_frame = ctk.CTkFrame(self.content_frame)
        metrics_frame.pack(fill="x", pady=(0, 20))
        
        # Configurar el grid con 4 columnas
        for i in range(4):
            metrics_frame.grid_columnconfigure(i, weight=1)
        
        metrics_data = [
            ("Total Usuarios", str(len(self.users_data))),
            ("Servicios Activos", "15"),
            ("Ingresos Mensuales", "$45,231"),
            ("Nuevos Pacientes", "+73")
        ]
        
        for i, (title, value) in enumerate(metrics_data):
            card = ctk.CTkFrame(metrics_frame)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            
            ctk.CTkLabel(card, text=title, font=("Arial", 12)).pack(pady=(10, 5))
            ctk.CTkLabel(card, text=value, font=("Arial", 20, "bold")).pack(pady=(0, 10))
    
    def create_table(self, parent, headers, data):
        # Crear frame para la tabla
        table_frame = ctk.CTkFrame(parent)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Crear Treeview
        tree = ttk.Treeview(table_frame, columns=headers, show="headings", height=10)
        
        # Configurar encabezados
        for header in headers:
            tree.heading(header, text=header)
            tree.column(header, width=150)
        
        # Agregar datos
        for row in data:
            tree.insert("", "end", values=row)
        
        # Agregar scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetar elementos
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        return tree
    
    def edit_user(self, tree):
        # Obtener el item seleccionado
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un usuario para editar")
            return
        
        # Obtener los datos del usuario seleccionado
        user_data = tree.item(selected_item)['values']
        
        def on_save(updated_data):

            role_names = {1: "Admin", 2: "Doctor", 3: "Secretaria"}
                    # Convertir updated_data a lista para poder modificarlo
            updated_values = list(updated_data)
            
            # El rol está en la posición 3 (índice 3)
            # Convertir el ID del rol al nombre correspondiente
            role_id = updated_values[3]  # Obtener el ID del rol
            role_name = role_names.get(role_id, "Desconocido")  # Convertir ID a nombre
            updated_values[3] = role_name  # Actualizar el valor del rol
            
            # Actualizar el item en el TreeView
            tree.item(selected_item, values=tuple(updated_values))
            
        # Crear ventana de edición
        edit_window = EditUserWindow(self, user_data, on_save)


    def show_users(self):
        # Limpiar contenido previo
        self.clear_content()

        # Encabezados y datos de la tabla
        headers = ["ID", "Nombre", "Email", "Rol"]

        # Conexión a la base de datos y obtención de datos con el rol en texto
        connection = conexion_db()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT ID_Usuario, Nombre, Correo, 
                CASE 
                    WHEN Rol = 1 THEN 'Admin' 
                    WHEN Rol = 2 THEN 'Doctor' 
                    WHEN Rol = 3 THEN 'Secretaria' 
                    ELSE 'Desconocido' 
                END as Rol 
            FROM Usuario
        """)
        self.users_data = cursor.fetchall()

        # Crear tabla de usuarios
        user_tree = self.create_table(self.content_frame, headers, self.users_data)
        user_tree.pack(fill="both", expand=True)

        # Botón para editar usuario
        edit_button = ctk.CTkButton(
            self.content_frame,
            text="Editar Usuario",
            command=lambda: self.edit_user(user_tree)
        )
        edit_button.pack(pady=10)

       # Botón para eliminar usuario
        delete_button = ctk.CTkButton(
            self.content_frame,
            text="Eliminar Usuario",
            fg_color="red",
            command=lambda: self.delete_user(user_tree)
        )
        delete_button.pack(pady=10)


    def show_services(self):
        # Implementar lógica para mostrar servicios
        self.clear_content()
        ctk.CTkLabel(self.content_frame, text="Servicios").pack(pady=20)

    def show_reports(self):
        # Implementar lógica para mostrar reportes
        self.clear_content()
        ctk.CTkLabel(self.content_frame, text="Reportes").pack(pady=20)

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def delete_user(self, tree):
        # Obtener el item seleccionado
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un usuario para eliminar")
            return
        
        # Confirmar eliminación
        if messagebox.askyesno("Confirmar eliminación", 
                             "¿Está seguro que desea eliminar este usuario?"):
            # Obtener datos del usuario
            user_data = tree.item(selected_item)['values']
            user_id = user_data[0]
            
            # Conectar a la base de datos y eliminar el usuario
            connection = conexion_db()
            cursor = connection.cursor()
            try:
                cursor.execute("DELETE FROM Usuario WHERE ID_Usuario = %s", (user_id,))
                connection.commit()
                # Eliminar de la tabla
                tree.delete(selected_item)
                # Eliminar de los datos
                self.users_data.remove(tuple(user_data))
                messagebox.showinfo("Éxito", "Usuario eliminado correctamente")
            except Exception as e:
                connection.rollback()
                print(e)
                messagebox.showerror("Error", "Ocurrió un error al eliminar el usuario")
            finally:
                cursor.close()
                connection.close()

if __name__ == "__main__":
    app = AdminDashboard()
    app.mainloop()