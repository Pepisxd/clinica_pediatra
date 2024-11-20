import customtkinter as ctk
from CTkMessagebox import CTkMessagebox  
from db_connection import conexion_db
import bcrypt



ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class Register(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        self.title("Registro")
        self.geometry("600x800")
        self.resizable(False, False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Frame de registro centrado
        self.register_frame = ctk.CTkFrame(self)
        self.register_frame.grid(row=0, column=0, padx=50, pady=50, sticky="nsew")
        self.register_frame.grid_columnconfigure((0, 1), weight=1)  # Dos columnas para alinear Nombre y Apellido

        # Título
        self.label = ctk.CTkLabel(self.register_frame, text="Crear una cuenta", font=("Arial Bold", 24))
        self.label.grid(row=0, column=0, columnspan=2, padx=20, pady=(10, 10), sticky="n")

        # Descripción
        self.label_info = ctk.CTkLabel(self.register_frame, text="Ingresa tus datos para registrarte en el sistema", font=("Arial", 14), text_color="gray")
        self.label_info.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 20))

        # Nombre y Apellido en la misma fila
        self.label_nombre = ctk.CTkLabel(self.register_frame, text="Nombre", font=("Arial Bold", 14))
        self.label_nombre.grid(row=2, column=0, padx=10, pady=(0, 5), sticky="w")

        self.label_apellido = ctk.CTkLabel(self.register_frame, text="Apellido", font=("Arial Bold", 14))
        self.label_apellido.grid(row=2, column=1, padx=10, pady=(0, 5), sticky="w")

        self.nombre_input = ctk.CTkEntry(self.register_frame, placeholder_text="Juan", height=40)
        self.nombre_input.grid(row=3, column=0, padx=10, pady=(0, 20), sticky="ew")

        self.apellido_input = ctk.CTkEntry(self.register_frame, placeholder_text="Pérez", height=40)
        self.apellido_input.grid(row=3, column=1, padx=10, pady=(0, 20), sticky="ew")

        # Correo electrónico
        self.label_email = ctk.CTkLabel(self.register_frame, text="Correo electrónico", font=("Arial Bold", 14))
        self.label_email.grid(row=4, column=0, columnspan=2, padx=10, pady=(0, 5), sticky="w")

        self.email_input = ctk.CTkEntry(self.register_frame, placeholder_text="juan@ejemplo.com", height=40)
        self.email_input.grid(row=5, column=0, columnspan=2, padx=10, pady=(0, 20), sticky="ew")

        # Contraseña
        self.label_password = ctk.CTkLabel(self.register_frame, text="Contraseña", font=("Arial Bold", 14))
        self.label_password.grid(row=6, column=0, columnspan=2, padx=10, pady=(0, 5), sticky="w")

        self.password_input = ctk.CTkEntry(self.register_frame, placeholder_text="********", show="*", height=40)
        self.password_input.grid(row=7, column=0, columnspan=2, padx=10, pady=(0, 20), sticky="ew")

        # Confirmar contraseña
        self.label_password_confirm = ctk.CTkLabel(self.register_frame, text="Confirmar contraseña", font=("Arial Bold", 14))
        self.label_password_confirm.grid(row=8, column=0, columnspan=2, padx=10, pady=(0, 5), sticky="w")

        self.password_confirm_input = ctk.CTkEntry(self.register_frame, placeholder_text="********", show="*", height=40)
        self.password_confirm_input.grid(row=9, column=0, columnspan=2, padx=10, pady=(0, 20), sticky="ew")

        # Checkbox para términos y condiciones
        self.terms_var = ctk.StringVar()
        self.terms_checkbox = ctk.CTkCheckBox(self.register_frame, text="Acepto los términos y condiciones", variable=self.terms_var, onvalue="Yes", offvalue="No", fg_color="black", font=("Arial", 14), hover_color="#242624", text_color="black")
        self.terms_checkbox.grid(row=10, column=0, columnspan=2, padx=10, pady=(0, 20))

        # Botón de registro
        self.register_button = ctk.CTkButton(self.register_frame, text="Registrarse", font=("Arial", 16), height=40, fg_color="black", hover_color="#242624", text_color="white")
        self.register_button.grid(row=11, column=0, columnspan=2, padx=10, pady=20, sticky="ew")

        # Frame adicional para centrar ambos textos
        self.text_frame = ctk.CTkFrame(self.register_frame, fg_color="transparent")
        self.text_frame.grid(row=12, column=0, columnspan=2, pady=(0, 10), sticky="n")

        # Texto "¿Ya tienes una cuenta?" seguido por "Inicia sesión"
        self.label_login = ctk.CTkLabel(self.text_frame, text="¿Ya tienes una cuenta?", font=("Arial", 14), text_color="gray")
        self.label_login.grid(row=0, column=0, padx=(0,0), sticky="e")

        self.label_login2 = ctk.CTkLabel(self.text_frame, text="Inicia sesión", font=("Arial", 14, "underline"), text_color="gray", cursor="hand2")
        self.label_login2.grid(row=0, column=1, padx=(3, 0), sticky="w")
        self.label_login2.bind("<Button-1>", self.show_login)

        #Evento para registrar con el boton de registo
        self.register_button.configure(command=self.registar_usuario)

    def show_login(self, event):
        self.destroy()
        from login import Login
        Login()

    def registar_usuario(self):
        nombre = self.nombre_input.get()
        apellido = self.apellido_input.get()
        correo = self.email_input.get()
        contrasena = self.password_input.get()
        confirmar_contrasena = self.password_confirm_input.get()
        terminos = self.terms_var.get()

        # Validaciones
        if not nombre or not apellido or not correo or not contrasena or not confirmar_contrasena:
            CTkMessagebox(
                title="Error", 
                message="Todos los campos son obligatorios",
                icon="cancel",
                sound=True
            ).get()  # Añadimos .get() para hacerlo modal
            return

        if terminos != "Yes":
            CTkMessagebox(
                title="Error", 
                message="Debes aceptar los términos y condiciones",
                icon="cancel",
                sound=True
            ).get()
            return

        if contrasena != confirmar_contrasena:
            CTkMessagebox(
                title="Error", 
                message="Las contraseñas no coinciden",
                icon="cancel",
                sound=True
            ).get()
            return
        
        contrasena_hash = bcrypt.hashpw(contrasena.encode(), bcrypt.gensalt())

        conexion = conexion_db()
        if conexion:
            cursor = conexion.cursor()
            try:
                cursor.execute(
                    "INSERT INTO Usuario (Nombre, Apellidos, Correo, Contrasena, Rol) VALUES (%s,%s,%s,%s,%s)", 
                    (nombre, apellido, correo, contrasena_hash.decode(), 3)
                )
                conexion.commit()
                
                response = CTkMessagebox(
                    title="Éxito", 
                    message="Usuario registrado correctamente\n¿Deseas iniciar sesión ahora?",
                    icon="check",
                    option_1="No",
                    option_2="Sí",
                    sound=True
                ).get()
                
                if response == "Sí":
                    self.destroy()
                    from login import Login
                    Login().mainloop()
                    
            except Exception as e:
                CTkMessagebox(
                    title="Error", 
                    message="No se pudo registrar el usuario. El correo podría estar en uso.",
                    icon="cancel",
                    sound=True
                ).get()
                print(e)
            finally:
                conexion.close()

if __name__ == "__main__":
    register = Register()
    register.mainloop()