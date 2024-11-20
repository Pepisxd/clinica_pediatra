import customtkinter as ctk
from PIL import Image
import os
from register import Register
from db_connection import conexion_db
import bcrypt
from doctor import DoctorScreen
from secretaria import SecretaryScreen
from adminDashboard import AdminDashboard

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class Login(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        self.title("Login")
        self.geometry("800x800")
        self.resizable(False, False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        logo_path = os.path.join(os.path.dirname(__file__), "images/logo.png")
        logo_imagen = Image.open(logo_path).resize((800, 800))

        logo = ctk.CTkImage(light_image=logo_imagen, dark_image=logo_imagen, size=(120, 120))

        # Login Frame
        self.login_frame = ctk.CTkFrame(self)
        self.login_frame.grid(row=0, column=0, padx=200, pady=100, sticky="news")
        self.login_frame.grid_columnconfigure(0, weight=1)
        self.login_frame.grid_rowconfigure(0, weight=0)

        # Labels and Entry Fields
        self.label = ctk.CTkLabel(self.login_frame, text="Bienvenido", font=("Arial Bold", 30), pady=10)
        self.label.grid(row=0, column=0, padx=0, pady=(50,0))

        self.label_info = ctk.CTkLabel(self.login_frame, 
                                     text="Ingresa tus credenciales para acceder a tu cuenta", 
                                     font=("Arial", 18), 
                                     text_color="gray", 
                                     pady=0, 
                                     wraplength=250)
        self.label_info.grid(row=1, column=0, padx=0, pady=10)

        self.label_username = ctk.CTkLabel(self.login_frame, text="Usuario", font=("Arial Bold", 16), pady=0)
        self.label_username.grid(row=2, column=0, padx=15, pady=(5,0), sticky="w")

        self.username_input = ctk.CTkEntry(self.login_frame, 
                                         placeholder_text="Ingresa tu nombre de usuario", 
                                         font=("Arial", 14), 
                                         height=40, 
                                         width=200)
        self.username_input.grid(row=3, column=0, padx=15, pady=10, sticky="ew")

        self.label_password = ctk.CTkLabel(self.login_frame, text="Contraseña", font=("Arial Bold", 16), pady=0)
        self.label_password.grid(row=4, column=0, padx=15, pady=(5,0), sticky="w")

        self.password_input = ctk.CTkEntry(self.login_frame, 
                                         placeholder_text="Ingresa tu contraseña", 
                                         font=("Arial", 14), 
                                         height=40, 
                                         width=200,
                                         show="*")
        self.password_input.grid(row=5, column=0, padx=15, pady=10, sticky="ew")

        # Event Binding for Entry Widgets
        self.username_input.bind("<FocusIn>", lambda event: self.on_entry(event, self.username_input, True))
        self.username_input.bind("<FocusOut>", lambda event: self.on_entry(event, self.username_input, False))
        self.password_input.bind("<FocusIn>", lambda event: self.on_entry(event, self.password_input, True))
        self.password_input.bind("<FocusOut>", lambda event: self.on_entry(event, self.password_input, False))

        # Login Button
        self.login_button = ctk.CTkButton(self.login_frame, text="Iniciar sesión", height=40, width=200, font=("Arial Bold", 14), fg_color="black", hover_color="#242624", text_color="white")
        self.login_button.grid(row=6, column=0, padx=10, pady=10)

        # Register Prompt
        self.text_frame = ctk.CTkFrame(self.login_frame, fg_color="transparent")
        self.text_frame.grid(row=12, column=0, columnspan=2, pady=(0, 10), sticky="n")

        self.label_login = ctk.CTkLabel(self.text_frame, text="No tienes cuenta?", font=("Arial", 14), text_color="gray")
        self.label_login.grid(row=0, column=0, padx=(0,0), sticky="e")

        self.label_login2 = ctk.CTkLabel(self.text_frame, text="Registrate", font=("Arial", 14, "underline"), text_color="gray", cursor="hand2")
        self.label_login2.grid(row=0, column=1, padx=(3, 0), sticky="w")

        image_label = ctk.CTkLabel(self.login_frame, image=logo, text="")
        image_label.grid(row=7, column=0, pady=10)  

        # Binding for Register Label
        self.label_login2.bind("<Button-1>", self.open_register)

        #Evento de login al boton de login
        self.login_button.configure(command=self.verificar_credenciales)

    def open_register(self, event):
        self.destroy()
        register_window = Register()
        register_window.mainloop()

    def on_entry(self, event, widget, focus):
        if focus:
            widget.configure(border_color="gray", border_width=3)
        else:
            widget.configure(border_color="gray", border_width=1)

    def verificar_credenciales(self):
        correo = self.username_input.get()
        contrasena = self.password_input.get()

        if not correo or not contrasena:
            self.mostrar_error("Por favor complete todos los campos")
            return

        conexion = conexion_db()
        if conexion:
            try:
                cursor = conexion.cursor()
                # Primero verificamos si el usuario existe
                cursor.execute("SELECT ID_Usuario, Contrasena, Rol, Nombre, Apellidos FROM Usuario WHERE Correo = %s", (correo,))
                resultado = cursor.fetchone()

                if resultado:
                    id_usuario, contrasena_db, rol, nombre, apellidos = resultado
                    
                    # Verificar si la contraseña en la BD ya está hasheada
                    try:
                        # Intenta verificar con bcrypt
                        if bcrypt.checkpw(contrasena.encode(), contrasena_db.encode()):
                            print("Inicio de sesión exitoso")
                            self.abrir_ventana_segun_rol(rol, id_usuario, nombre, apellidos, correo)
                        else:
                            self.mostrar_error("Contraseña incorrecta")
                    except ValueError:
                        # Si la contraseña en la BD no está hasheada, verificamos directamente
                        if contrasena == contrasena_db:
                            # La contraseña coincide, actualizamos a hash
                            hashed = bcrypt.hashpw(contrasena.encode(), bcrypt.gensalt())
                            cursor.execute("UPDATE Usuario SET Contrasena = %s WHERE ID_Usuario = %s", 
                                         (hashed.decode(), id_usuario))
                            conexion.commit()
                            print("Inicio de sesión exitoso y contraseña actualizada")
                            self.abrir_ventana_segun_rol(rol, id_usuario, nombre, apellidos)
                        else:
                            self.mostrar_error("Contraseña incorrecta")
                else:
                    self.mostrar_error("Usuario no encontrado")
            
            except Exception as e:
                print(f"Error: {e}")
                self.mostrar_error(f"Error al verificar credenciales: {str(e)}")
            finally:
                conexion.close()
        else:
            self.mostrar_error("Error al conectar a la base de datos")

    def abrir_ventana_segun_rol(self, rol, id_usuario, nombre, apellidos, email):
            self.withdraw()  # Ocultar ventana de login
            
            # Crear diccionario con datos del usuario
            user_data = {
                'id': id_usuario,
                'nombre': nombre,
                'apellidos': apellidos,
                'rol': rol,
                'correo': email
            }
            
            try:
                # Abrir ventana según el rol
                if rol == 1:  # Admin
                    ventana = AdminDashboard(user_data)
                    ventana.protocol("WM_DELETE_WINDOW", lambda: self.cerrar_sesion(ventana))
                    ventana.mainloop()
                elif rol == 2:  # Doctor
                    print(user_data)
                    ventana = DoctorScreen(user_data)
                    ventana.protocol("WM_DELETE_WINDOW", lambda: self.cerrar_sesion(ventana))
                    ventana.mainloop()
                elif rol == 3:  # Secretaria
                    ventana = SecretaryScreen(user_data)
                    ventana.protocol("WM_DELETE_WINDOW", lambda: self.cerrar_sesion(ventana))
                    ventana.mainloop()
                else:
                    raise ValueError(f"Rol no válido: {rol}")
            
 
            except Exception as e:
                print(f"Error al abrir ventana: {e}")
                self.deiconify()  # Mostrar ventana de login nuevamente
                self.mostrar_error(f"Error al abrir la ventana: {str(e)}")

    def cerrar_sesion(self, ventana_actual):
        if isinstance(ventana_actual, DoctorScreen):
            ventana_actual.on_closing()  # Esto ejecutará el commit y cerrará la conexión
        else:
            ventana_actual.destroy()
        self.deiconify()

    def mostrar_error(self, mensaje):
        error_window = ctk.CTkToplevel(self)
        error_window.title("Error")
        error_window.geometry("300x100")
                
        label = ctk.CTkLabel(error_window, text=mensaje)
        label.pack(pady=20)
                
        button = ctk.CTkButton(error_window, text="OK", command=error_window.destroy)
        button.pack()

if __name__ == "__main__":
    login = Login()
    login.mainloop()