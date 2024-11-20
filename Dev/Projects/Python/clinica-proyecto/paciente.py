import customtkinter as ctk
from tkcalendar import Calendar
from datetime import datetime, timedelta
import locale
from tkinter import ttk

class PatientScreen(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configuración básica de la ventana
        self.title("Panel de Paciente")
        self.geometry("1200x700")
        
        # Configurar el tema claro por defecto
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Variables de estado
        self.current_page = ctk.StringVar(value="appointments")
        self.current_week = datetime.now()
        
        # Crear el diseño principal
        self.create_layout()
        
        # Mostrar la página inicial
        self.show_page()
        
    def create_layout(self):
        # Frame lateral (sidebar) - Color rosa claro
        self.sidebar = ctk.CTkFrame(self, fg_color="#FDF2F8")  # pink-50 equivalent
        self.sidebar.pack(side="left", fill="y", padx=0, pady=0)
        
        # Título del sidebar
        ctk.CTkLabel(
            self.sidebar,
            text="Panel de Paciente",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#831843"  # pink-800 for contrast
        ).pack(pady=(20, 30))
        
        # Botones de navegación
        self.nav_buttons = {}
        nav_items = [
            ("appointments", "Mis Citas"),
            ("history", "Mi Historial"),
            ("request", "Solicitar Cita")
        ]
        
        for page, text in nav_items:
            self.nav_buttons[page] = ctk.CTkButton(
                self.sidebar,
                text=text,
                command=lambda p=page: self.change_page(p),
                width=180,
                fg_color="transparent",
                text_color="#831843",  # pink-800
                hover_color="#FBCFE8"  # pink-200
            )
            self.nav_buttons[page].pack(pady=5, padx=10)
            
        # Botón de cerrar sesión
        ctk.CTkButton(
            self.sidebar,
            text="Cerrar Sesión",
            command=self.quit,
            width=180,
            fg_color="transparent",
            text_color="#831843",
            hover_color="#FBCFE8",
            border_width=1,
            border_color="#831843"
        ).pack(side="bottom", pady=20, padx=10)
        
        # Frame principal
        self.main_frame = ctk.CTkFrame(self, fg_color="#F8FAFC")  # slate-50 equivalent
        self.main_frame.pack(side="right", fill="both", expand=True, padx=0, pady=0)
        
    def create_appointments_page(self):
        # Limpiar el frame principal
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        # Contenedor principal con padding
        content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        ctk.CTkLabel(
            content_frame,
            text="Mis Citas",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#831843"
        ).pack(anchor="w", pady=(0, 20))
        
        # Frame del calendario
        cal_frame = ctk.CTkFrame(content_frame, fg_color="white")
        cal_frame.pack(fill="x", pady=(0, 20), padx=0)
        
        # Configurar el estilo del calendario
        style = ttk.Style(self)
        style.theme_use('clam')  # Puedes usar 'clam', 'alt', 'default', o 'classic'
        
        # Configurar colores personalizados
        style.configure("Custom.Calendar", 
                        background="white", 
                        foreground="black", 
                        fieldbackground="white", 
                        selectbackground="#DB2777",  # pink-600
                        selectforeground="white")  # Color de texto de la fecha seleccionada

        # Crear el calendario con el estilo personalizado
        cal = Calendar(
            cal_frame,
            selectmode='day',
            date_pattern='yyyy-mm-dd',
            style="Custom.Calendar"
        )
        cal.pack(pady=10, padx=10)
        
        # Botones de navegación
        nav_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        nav_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkButton(
            nav_frame,
            text="Semana Anterior",
            border_width=1,
            fg_color="transparent",
            text_color="#831843",
            border_color="#831843",
            hover_color="#FBCFE8",
            command=self.previous_week
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            nav_frame,
            text="Semana Siguiente",
            border_width=1,
            fg_color="transparent",
            text_color="#831843",
            border_color="#831843",
            hover_color="#FBCFE8",
            command=self.next_week
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            nav_frame,
            text="Agendar Cita",
            fg_color="#DB2777",  # pink-600
            hover_color="#BE185D",  # pink-700
            command=lambda: self.change_page("request")
        ).pack(side="left", padx=5)
        
        # Título de citas futuras
        ctk.CTkLabel(
            content_frame,
            text="Citas Futuras",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#831843"
        ).pack(anchor="w", pady=(0, 10))
        
        # Tabla de citas
        table_frame = ctk.CTkFrame(content_frame, fg_color="white")
        table_frame.pack(fill="both", expand=True)
        
        # Headers
        headers = ["Fecha", "Hora", "Médico", "Estado"]
        for col, header in enumerate(headers):
            ctk.CTkLabel(
                table_frame,
                text=header,
                font=ctk.CTkFont(weight="bold"),
                text_color="#831843"
            ).grid(row=0, column=col, padx=10, pady=5, sticky="w")
        
        # Datos de ejemplo
        appointments = [
            ("2023-05-01", "09:00", "Dr. García", "Confirmado"),
            ("2023-05-03", "14:00", "Dra. Rodríguez", "Pendiente"),
            ("2023-05-05", "11:00", "Dr. Martínez", "Confirmado")
        ]
        
        for row, appointment in enumerate(appointments, start=1):
            for col, value in enumerate(appointment):
                ctk.CTkLabel(
                    table_frame,
                    text=value,
                    text_color="black"
                ).grid(row=row, column=col, padx=10, pady=5, sticky="w")
                
    def create_history_page(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            content_frame,
            text="Mi Historial",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#831843"
        ).pack(pady=(0, 20))
        
        ctk.CTkLabel(
            content_frame,
            text="Aquí se mostrará tu historial médico.",
            font=ctk.CTkFont(size=16),
            text_color="black"
        ).pack()
        
    def create_request_page(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            content_frame,
            text="Solicitar Cita",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#831843"
        ).pack(pady=(0, 20))
        
        ctk.CTkLabel(
            content_frame,
            text="Aquí podrás solicitar una nueva cita médica.",
            font=ctk.CTkFont(size=16),
            text_color="black"
        ).pack()
        
    def previous_week(self):
        self.current_week -= timedelta(days=7)
        self.show_page()
        
    def next_week(self):
        self.current_week += timedelta(days=7)
        self.show_page()
        
    def change_page(self, page):
        self.current_page.set(page)
        self.show_page()
        
    def show_page(self):
        # Actualizar el estilo de los botones
        for page, button in self.nav_buttons.items():
            if page == self.current_page.get():
                button.configure(fg_color="#FBCFE8")  # pink-200
            else:
                button.configure(fg_color="transparent")
        
        # Mostrar la página correspondiente
        if self.current_page.get() == "appointments":
            self.create_appointments_page()
        elif self.current_page.get() == "history":
            self.create_history_page()
        elif self.current_page.get() == "request":
            self.create_request_page()

if __name__ == "__main__":
    app = PatientScreen()
    app.mainloop()