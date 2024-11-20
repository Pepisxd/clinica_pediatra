import customtkinter as ctk
from tkcalendar import Calendar
import locale
import os
from datetime import datetime, timedelta
from tkinter import messagebox
from db_connection import conexion_db
from dateutil.relativedelta import relativedelta

# Configurar el tema y el modo por defecto
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class SecretaryScreen(ctk.CTk):
    def __init__(self, user_data , *args, **kwargs):
        #self.secretary_email = secretary_email

        self.user_data = user_data
        self.secretary_email = user_data.get("correo")
        self.secretary_id = user_data.get("id")  # Extraer el ID desde el diccionario
        self.secretary_name = f"{user_data.get('nombre')} {user_data.get('apellidos')}"
        
      

        super().__init__(*args, **kwargs)

        #print(f"Email de la secretaria: {secretary_email}")

        self.conn = self.conexion_db()
        if not self.conn:
            raise ConnectionError("No se pudo establecer conexión con la base de datos")
        
        self.cursor = self.conn.cursor()
    
        #self.secretary_id = self.get_secretary_id(secretary_email)
        print(f"ID de la secretaria: {self.secretary_id}")
        
        # Configuración básica de la ventana
        self.title("Sistema de Gestión Médica")
        self.geometry("1200x700")

        # Variables de estado
        self.current_page = ctk.StringVar(value="appointments")
        
        # Crear el diseño principal
        self.create_layout()
        
        # Mostrar la página inicial
        self.show_page()

        # Asegurarse de cerrar la conexión al cerrar la aplicación
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def conexion_db(self):
        try:
            return conexion_db()
        except Exception as e:
            print(f"Error al conectar con la base de datos: {str(e)}")
            return None

    def on_closing(self):
        try:
            if hasattr(self, 'conn') and self.conn:
                self.conn.commit()
                
                if hasattr(self, 'cursor') and self.cursor:
                    self.cursor.close()
                self.conn.close()
        except Exception as e:
            print(f"Error al cerrar la conexión: {e}")
        finally:
            self.destroy()

    def get_secretary_id(self, email):
        if not email:
            raise ValueError("Email no proporcionado")
            
        query = """
            SELECT ID_Usuario FROM Usuario
            WHERE Correo = %s AND Rol = 3
        """
        try:
            self.cursor.execute(query, (email,))
            result = self.cursor.fetchone()
            if result:
                return result[0]
            else:
                raise ValueError(f"No se encontró la secretaria con email: {email}")
        except Exception as e:
            raise ValueError(f"Error en la consulta: {str(e)}")

    def get_secretary_name(self):
        query = "SELECT Nombre, Apellidos FROM Usuario WHERE ID_Usuario = %s"
        self.cursor.execute(query, (self.secretary_id,))
        result = self.cursor.fetchone()
        if result:
            return f"{result[0]} {result[1]}"
        return "Secretaria"
        
    def create_layout(self):
        # Frame lateral (sidebar)
        self.sidebar = ctk.CTkFrame(self, width=200)
        self.sidebar.pack(side="left", fill="y", padx=10, pady=10)

        secretary_name = self.get_secretary_name()
        ctk.CTkLabel(
            self.sidebar,
            text=secretary_name,
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(20, 10))

        # Título del sidebar
        ctk.CTkLabel(
            self.sidebar,
            text="Panel de Secretaria",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(0, 30))
        
        # Botones de navegación
        self.nav_buttons = {}
        for page in [("appointments", "Mis Citas"), 
                     ("patients", "Pacientes")]:
            self.nav_buttons[page[0]] = ctk.CTkButton(
                self.sidebar,
                text=page[1],
                command=lambda p=page[0]: self.change_page(p),
                width=180
            )
            self.nav_buttons[page[0]].pack(pady=5)
            
        # Botón de cerrar sesión
        ctk.CTkButton(
            self.sidebar,
            text="Cerrar Sesión",
            command=self.quit,
            width=180
        ).pack(side="bottom", pady=20)
        
        # Frame principal
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10) # Crear la página de citas
    
    def create_appointments_page(self):
        # Limpiar el frame principal
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Título
        ctk.CTkLabel(
            self.main_frame,
            text="Agenda de Citas",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=(20, 10))

        # Frame para selector de médico
        doctor_frame = ctk.CTkFrame(self.main_frame)
        doctor_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            doctor_frame,
            text="Médico:",
            font=ctk.CTkFont(weight="bold")
        ).pack(side="left", padx=10)

        # Variable para almacenar el médico seleccionado
        self.selected_doctor = ctk.StringVar()
        self.doctor_menu = ctk.CTkOptionMenu(
            doctor_frame,
            variable=self.selected_doctor,
            values=["Seleccione un médico"],
            command=self.on_doctor_changed
        )
        self.doctor_menu.pack(side="left", padx=10)
        
        # Cargar lista de médicos
        self.load_doctors()

        # Botón de Agendar Cita
        ctk.CTkButton(
            self.main_frame,
            text="Agendar Cita",
            width=200,
            height=40,
            fg_color="#4CAF50",
            hover_color="#45a049",
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.show_appointment_form
        ).pack(pady=(0, 20))

        # Frame superior para el calendario y filtros
        top_frame = ctk.CTkFrame(self.main_frame)
        top_frame.pack(fill="x", padx=20, pady=10)

        # Frame izquierdo para el calendario
        left_frame = ctk.CTkFrame(top_frame)
        left_frame.pack(side="left", padx=20, pady=10)

        # Calendario
        self.calendar = Calendar(
            left_frame,
            selectmode='day',
            date_pattern='yyyy-mm-dd',
            showweeknumbers=False
        )
        self.calendar.pack(pady=10)

        # Frame para filtros
        filter_frame = ctk.CTkFrame(top_frame)
        filter_frame.pack(side="right", fill="y", pady=10, padx=20)

        # Filtro de estado
        self.estado_var = ctk.StringVar(value="Todos")
        ctk.CTkLabel(filter_frame, text="Estado de la cita:").pack(pady=5)
        ctk.CTkOptionMenu(
            filter_frame,
            values=["Todos", "Pendiente", "Confirmada", "Cancelada", "Completada"],
            variable=self.estado_var,
            command=self.update_appointments
        ).pack(pady=5)

        # Botones de acción
        ctk.CTkButton(
            filter_frame,
            text="Ver citas del día",
            command=lambda: self.filter_appointments_by_date(datetime.now().strftime('%Y-%m-%d'))
        ).pack(pady=5)

        ctk.CTkButton(
            filter_frame,
            text="Ver todas las citas",
            command=self.update_appointments
        ).pack(pady=5)

        # Frame para la tabla de citas
        self.table_frame = ctk.CTkFrame(self.main_frame)
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Mostrar las citas
        self.display_appointments()
        
    def load_doctors(self):
        """Cargar lista de médicos desde la base de datos"""
        try:
            query = """
                SELECT ID_Usuario, CONCAT(Nombre, ' ', Apellidos) as NombreCompleto 
                FROM Usuario 
                WHERE Rol = 2 
                ORDER BY Nombre
            """
            self.cursor.execute(query)
            doctors = self.cursor.fetchall()
            
            # Crear diccionario de médicos para referencia posterior
            self.doctors_dict = {f"{doctor[1]} (ID: {doctor[0]})": doctor[0] for doctor in doctors}
            
            # Actualizar el menú de médicos
            doctor_list = list(self.doctors_dict.keys())
            self.doctor_menu.configure(values=doctor_list)
            
            if doctor_list:
                self.selected_doctor.set(doctor_list[0])
                self.current_doctor_id = self.doctors_dict[doctor_list[0]]
            
        except Exception as e:
            print(f"Error al cargar médicos: {e}")
            self.show_error("Error al cargar la lista de médicos")
            
    def on_doctor_changed(self, selection):
        """Manejar el cambio de médico seleccionado"""
        if selection in self.doctors_dict:
            self.current_doctor_id = self.doctors_dict[selection]
            self.update_appointments()

    def display_appointments(self, date_filter=None):
        # Limpiar tabla existente
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        # Verificar si hay un médico seleccionado
        if not hasattr(self, 'current_doctor_id'):
            ctk.CTkLabel(
                self.table_frame,
                text="Por favor seleccione un médico",
                font=ctk.CTkFont(size=16)
            ).pack(pady=20)
            return

        # Crear encabezados
        headers = ["Fecha", "Hora", "Paciente", "Edad", "Estado", "Motivo", "Acciones"]
        for col, header in enumerate(headers):
            ctk.CTkLabel(
                self.table_frame,
                text=header,
                font=ctk.CTkFont(weight="bold")
            ).grid(row=0, column=col, padx=10, pady=5, sticky="w")

        # Construir la consulta SQL
        query = """
            SELECT c.Fecha, c.Hora, p.Nombre, p.Apellidos, p.Fecha_Nacimiento, 
                c.Estado, c.Motivo, c.ID_Cita
            FROM Cita c
            JOIN Paciente p ON c.ID_Paciente = p.ID_Paciente
            WHERE c.ID_Medico = %s
        """
        params = [self.current_doctor_id]

        if date_filter:
            query += " AND DATE(c.Fecha) = %s"
            params.append(date_filter)

        if self.estado_var.get() != "Todos":
            query += " AND c.Estado = %s"
            params.append(self.estado_var.get())

        query += " ORDER BY c.Fecha, c.Hora"

        try:
            self.cursor.execute(query, tuple(params))
            appointments = self.cursor.fetchall()

            for row, appt in enumerate(appointments, start=1):
                # [El resto del código de display_appointments permanece igual]
                # Asegurarse de que la fecha y hora sean objetos datetime
                if isinstance(appt[0], datetime):
                    fecha = appt[0].strftime("%Y-%m-%d")
                else:
                    fecha = appt[0]

                if isinstance(appt[1], datetime):
                    hora = appt[1].strftime("%H:%M")
                else:
                    hora = appt[1]
                paciente = f"{appt[2]} {appt[3]}"
                
                fecha_nac = appt[4]
                if not isinstance(fecha_nac, str):
                    fecha_nac = fecha_nac.strftime("%Y-%m-%d")
                
                try:
                    fecha_nac_dt = datetime.strptime(fecha_nac, '%Y-%m-%d')
                    edad = relativedelta(datetime.now(), fecha_nac_dt)
                    edad_str = f"{edad.years}a {edad.months}m"
                except Exception as e:
                    print(f"Error al calcular la edad: {e}")
                    edad_str = "N/A"
                
                estado = appt[5]
                motivo = appt[6]
                cita_id = appt[7]

                # Mostrar información
                ctk.CTkLabel(self.table_frame, text=fecha).grid(row=row, column=0, padx=10, pady=5, sticky="w")
                ctk.CTkLabel(self.table_frame, text=hora).grid(row=row, column=1, padx=10, pady=5, sticky="w")
                ctk.CTkLabel(self.table_frame, text=paciente).grid(row=row, column=2, padx=10, pady=5, sticky="w")
                ctk.CTkLabel(self.table_frame, text=edad_str).grid(row=row, column=3, padx=10, pady=5, sticky="w")
                
                estado_label = ctk.CTkLabel(self.table_frame, text=estado)
                estado_label.grid(row=row, column=4, padx=10, pady=5, sticky="w")
                
                if estado == "Confirmada":
                    estado_label.configure(text_color="green")
                elif estado == "Cancelada":
                    estado_label.configure(text_color="red")
                elif estado == "Completada":
                    estado_label.configure(text_color="blue")
                
                ctk.CTkLabel(self.table_frame, text=motivo).grid(row=row, column=5, padx=10, pady=5, sticky="w")

                # Frame para botones de acción
                action_frame = ctk.CTkFrame(self.table_frame)
                action_frame.grid(row=row, column=6, padx=10, pady=5)

                if estado == "Pendiente":
                    ctk.CTkButton(
                        action_frame,
                        text="Confirmar",
                        width=80,
                        command=lambda id=cita_id: self.update_appointment_status(id, "Confirmada")
                    ).pack(side="left", padx=2)

                if estado in ["Pendiente", "Confirmada"]:
                    ctk.CTkButton(
                        action_frame,
                        text="Cancelar",
                        width=80,
                        fg_color="red",
                        command=lambda id=cita_id: self.update_appointment_status(id, "Cancelada")
                    ).pack(side="left", padx=2)

                if estado == "Pendiente":
                    ctk.CTkButton(
                        action_frame,
                        text="Editar",
                        width=80,
                        fg_color="green",
                        command=lambda id=cita_id: self.edit_appointment(id)
                    ).pack(side="left", padx=2)

        except Exception as e:
            print(f"Error al mostrar citas: {e}")
            self.show_error(f"Error al cargar las citas: {str(e)}")

    def update_appointment_status(self, cita_id, new_status):
        try:
            query = "UPDATE Cita SET Estado = %s WHERE ID_Cita = %s"
            self.cursor.execute(query, (new_status, cita_id))
            self.conn.commit()
            self.display_appointments()
        except Exception as e:
            print(f"Error al actualizar estado de cita: {e}")
            self.show_error(f"Error al actualizar la cita: {str(e)}")

    def filter_appointments_by_date(self, date):
        self.display_appointments(date)

    def update_appointments(self, *args):
        self.display_appointments()

    def edit_appointment(self, cita_id):
        try:
            # Obtener los datos de la cita
            appointment = self.get_appointment_by_id(cita_id)
            if appointment:
                # Mostrar el formulario de edición
                self.show_appointment_form(appointment)
            else:
                self.show_error("No se encontró la cita seleccionada")
        except Exception as e:
            self.show_error(f"Error al cargar la cita: {str(e)}")

    def show_appointment_form(self, appointment=None):
        # Crear una nueva ventana para el formulario de cita
        self.form_window = ctk.CTkToplevel(self)
        self.form_window.title("Nueva Cita" if appointment is None else "Editar Cita")
        self.form_window.geometry("450x650")  # Incrementado para acomodar el nuevo campo
        self.form_window.resizable(False, False)

        # Configurar pesos de la cuadrícula para centrar
        self.form_window.grid_columnconfigure(0, weight=1)
        self.form_window.grid_columnconfigure(1, weight=1)

        # Título con texto coloreado
        title_label = ctk.CTkLabel(
            self.form_window,
            text="Nueva Cita" if appointment is None else "Editar Cita",
            font=("Arial", 20, "bold"),
            anchor="center"
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(20, 30), sticky="ew")

        # Selección de paciente
        patient_label = ctk.CTkLabel(
            self.form_window,
            text="Paciente:",
            font=("Arial", 12),
            anchor="center",
            width=300
        )
        patient_label.grid(row=1, column=0, columnspan=2, padx=10, sticky="ew", pady=(0, 5))

        # Obtener pacientes disponibles
        self.available_patients = self.get_available_patients()

        if appointment:
            # Obtener los datos del paciente actual
            query = """
                SELECT p.ID_Paciente, p.Nombre, p.Apellidos 
                FROM paciente p 
                WHERE p.ID_Paciente = %s
            """
            self.cursor.execute(query, (appointment['paciente_id'],))
            current_patient = self.cursor.fetchone()
        
            # Agregar el paciente actual a la lista si no está
            current_patient_in_list = False
            for p in self.available_patients:
                if p[0] == current_patient[0]:  # Comparar ID_Paciente
                    current_patient_in_list = True
                    break
        
            if not current_patient_in_list:
                self.available_patients.append(current_patient)
        
            # Para edición, solo mostrar el paciente actual
            patient_names = [f"{current_patient[1]} {current_patient[2]}"]
            initial_value = f"{current_patient[1]} {current_patient[2]}"
        else:
            # Para nueva cita, mostrar todos los pacientes disponibles
            patient_names = [f"{p[1]} {p[2]}" for p in self.available_patients]
            initial_value = "Seleccione un paciente"

        self.patient_var = ctk.StringVar(value=initial_value)
        self.patient_dropdown = ctk.CTkComboBox(
            self.form_window,
            variable=self.patient_var,
            values=patient_names,
            width=300,
            state="disabled" if appointment else "normal"  # Deshabilitar si es edición
        )
        self.patient_dropdown.grid(row=2, column=0, columnspan=2, padx=10, pady=(0, 20))

        # Selección de médico
        doctor_label = ctk.CTkLabel(
            self.form_window,
            text="Médico:",
            font=("Arial", 12),
            anchor="center",
            width=300
        )
        doctor_label.grid(row=3, column=0, columnspan=2, padx=10, sticky="ew", pady=(0, 5))

        # Obtener médicos disponibles
        self.available_doctors = self.get_available_doctors()

        if appointment:
            # Obtener los datos del médico actual
            query = """
                SELECT u.ID_Usuario, u.Nombre, u.Apellidos 
                FROM Usuario u 
                WHERE u.ID_Usuario = %s
            """
            self.cursor.execute(query, (appointment['medico_id'],))
            current_doctor = self.cursor.fetchone()
            
            # Para edición, solo mostrar el médico actual
            doctor_names = [f"{current_doctor[1]} {current_doctor[2]}"]
            initial_doctor = f"{current_doctor[1]} {current_doctor[2]}"
        else:
            # Para nueva cita, mostrar todos los médicos
            doctor_names = [f"{d[1]} {d[2]}" for d in self.available_doctors]
            initial_doctor = "Seleccione un médico"

        self.doctor_var = ctk.StringVar(value=initial_doctor)
        self.doctor_dropdown = ctk.CTkComboBox(
            self.form_window,
            variable=self.doctor_var,
            values=doctor_names,
            width=300,
            state="disabled" if appointment else "normal"  # Deshabilitar si es edición
        )
        self.doctor_dropdown.grid(row=4, column=0, columnspan=2, padx=10, pady=(0, 20))

        # Campo de fecha
        date_label = ctk.CTkLabel(
            self.form_window,
            text="Fecha:",
            font=("Arial", 12),
            anchor="center",
            width=300
        )
        date_label.grid(row=5, column=0, columnspan=2, padx=10, sticky="ew", pady=(0, 5))

        self.date_entry = ctk.CTkEntry(
            self.form_window,
            width=300,
            placeholder_text="YYYY-MM-DD"
        )
        self.date_entry.grid(row=6, column=0, columnspan=2, padx=10, pady=(0, 20))

        if appointment:
            self.date_entry.insert(0, appointment['fecha'])

        # Campo de hora
        time_label = ctk.CTkLabel(
            self.form_window,
            text="Hora:",
            font=("Arial", 12),
            anchor="center",
            width=300
        )
        time_label.grid(row=7, column=0, columnspan=2, padx=10, sticky="ew", pady=(0, 5))

        self.time_entry = ctk.CTkEntry(
            self.form_window,
            width=300,
            placeholder_text="HH:MM"
        )
        self.time_entry.grid(row=8, column=0, columnspan=2, padx=10, pady=(0, 20))

        if appointment:
            self.time_entry.insert(0, appointment['hora'])

        # Campo de motivo
        reason_label = ctk.CTkLabel(
            self .form_window,
            text="Motivo:",
            font=("Arial", 12),
            anchor="center",
            width=300
        )
        reason_label.grid(row=10, column=0, columnspan=2, padx=10, sticky="ew", pady=(0, 5))

        self.reason_entry = ctk.CTkEntry(
            self.form_window,
            width=300
        )
        self.reason_entry.grid(row=11, column=0, columnspan=2, padx=10, pady=(0, 20))

        if appointment:
            self.reason_entry.insert(0, appointment['motivo'])

        # Botones de acción
        buttons_frame = ctk.CTkFrame(self.form_window)
        buttons_frame.grid(row=12, column=0, columnspan=2, pady=30)

        # Botones de acción
        save_button = ctk.CTkButton(
            buttons_frame,
            text="Guardar",
            width=120,
            fg_color="#1E90FF",
            hover_color="#1871CD",
            command=lambda: self.handle_save_appointment(appointment)
        )
        save_button.grid(row=0, column=0, padx=10)

        cancel_button = ctk.CTkButton(
            buttons_frame,
            text="Cancelar",
            width=120,
            fg_color="#1E90FF",
            hover_color="#1871CD",
            command=self.close_appointment_form
        )
        cancel_button.grid(row=0, column=1, padx=10)
        
    def get_available_doctors(self):
        """Obtener lista de médicos disponibles"""
        try:
            query = """
                SELECT ID_Usuario, Nombre, Apellidos
                FROM Usuario
                WHERE Rol = 2
                ORDER BY Nombre, Apellidos
            """
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error al obtener médicos disponibles: {e}")
            self.show_error(f"Error al obtener médicos disponibles: {str(e)}")
            return []

    def get_appointment_by_id(self, cita_id):
        query = """
            SELECT c.ID_Cita, c.ID_Paciente, c.Fecha, c.Hora, c.Motivo, c.Estado
            FROM Cita c
            WHERE c.ID_Cita = %s
        """
        self.cursor.execute(query, (cita_id,))
        result = self.cursor.fetchone()
        
        if result:
            return {
                'id': result[0],           # ID_Cita
                'paciente_id': result[1],  # ID_Paciente
                'fecha': result[2],        # Fecha
                'hora': result[3],         # Hora
                'motivo': result[4],       # Motivo
                'estado': result[5]        # Estado
            }
        return None

    def handle_save_appointment(self, appointment=None):
        try:
            # Validar selección de paciente
            selected_patient_name = self.patient_var.get()
            if selected_patient_name == "Seleccione un paciente":
                raise ValueError("Por favor seleccione un paciente")

            # Validar selección de médico
            selected_doctor_name = self.doctor_var.get()
            if selected_doctor_name == "Seleccione un médico":
                raise ValueError("Por favor seleccione un médico")

            # Encontrar el ID del paciente seleccionado
            selected_patient = None
            for patient in self.available_patients:
                if f"{patient[1]} {patient[2]}" == selected_patient_name:
                    selected_patient = patient
                    break

            if not selected_patient:
                raise ValueError("No se pudo encontrar el paciente seleccionado")

            # Encontrar el ID del médico seleccionado
            selected_doctor = None
            for doctor in self.available_doctors:
                if f"{doctor[1]} {doctor[2]}" == selected_doctor_name:
                    selected_doctor = doctor
                    break

            if not selected_doctor:
                raise ValueError("No se pudo encontrar el médico seleccionado")

            # Validar fecha
            fecha = self.date_entry.get()
            if not fecha:
                raise ValueError("La fecha es obligatoria")
            try:
                # Validar formato de fecha
                datetime.strptime(fecha, '%Y-%m-%d')
            except ValueError:
                raise ValueError("Formato de fecha inválido. Use YYYY-MM-DD")

            # Validar hora
            hora = self.time_entry.get()
            if not hora:
                raise ValueError("La hora es obligatoria")
            try:
                # Validar formato de hora
                datetime.strptime(hora, '%H:%M')
            except ValueError:
                raise ValueError("Formato de hora inválido. Use HH:MM")

            # Validar motivo
            motivo = self.reason_entry.get()
            if not motivo:
                raise ValueError("El motivo es obligatorio")
            if len(motivo) > 100:
                raise ValueError("El motivo no puede exceder los 100 caracteres")

            # Recolectar datos del formulario
            appointment_data = {
                'fecha': self.date_entry.get(),
                'hora': self.time_entry.get(),
                'descripcion': self.reason_entry.get()
            }
            
            # Verificar disponibilidad usando el ID del médico seleccionado
            requested_time = f"{appointment_data['fecha']} {appointment_data['hora']}"
            appointment_id = appointment.get('id') if appointment else None
            
            if not self.is_time_available(requested_time, selected_doctor[0], appointment_id):
                raise ValueError("La hora seleccionada no está disponible para el médico seleccionado")

            # Si se está editando, actualizar la cita
            if appointment and 'id' in appointment:
                self.update_appointment(appointment['id'], selected_patient[0], selected_doctor[0], appointment_data)
            else:
                # Si es una nueva cita, guardarla
                self.save_appointment(selected_patient[0], selected_doctor[0], appointment_data)

            # Si todo sale bien, cerrar el formulario
            self.close_appointment_form()
            
            # Actualizar la vista de citas
            self.display_appointments()

        except Exception as e:
            self.show_error(str(e))
            
    def update_appointment(self, appointment_id, patient_id, doctor_id, appointment_data):
        try:
            query = """
                UPDATE cita
                SET ID_Paciente = %s, ID_Medico = %s, Fecha = %s, Hora = %s, Motivo = %s
                WHERE ID_Cita = %s
            """
            values = (
                patient_id,
                doctor_id,
                appointment_data['fecha'],
                appointment_data['hora'],
                appointment_data['descripcion'],
                appointment_id
            )
            
            self.cursor.execute(query, values)
            self.conn.commit()
            messagebox.showinfo("Éxito", "Cita actualizada correctamente")

        except Exception as e:
            print(f"Error al actualizar la cita: {e}")
            self.show_error(f"Error al actualizar la cita: {str(e)}")
        
    def close_appointment_form(self):
        # Cierra la ventana de formulario de cita
        self.form_window.destroy()
        # Actualizar la lista de citas
        self.display_appointments()

    def get_available_patients(self):
        # Pacientes sin ninguna cita registrada, pacientes disponibles
        query = """
            SELECT p.*
            FROM paciente p
            LEFT JOIN cita c ON p.ID_Paciente = c.ID_Paciente
            GROUP BY p.ID_Paciente
            HAVING SUM(CASE WHEN c.estado NOT IN ('cancelada','completada') THEN 1 ELSE 0 END) = 0
        """
    
        try:
            self.cursor.execute(query)
            available_patients = self.cursor.fetchall()
            print(f"Pacientes disponibles encontrados: {len(available_patients)}")
            return available_patients
        except Exception as e:
            print(f"Error al obtener pacientes disponibles: {e}")
            self.show_error(f"Error al obtener pacientes disponibles: {str(e)}")
            return []

    def save_appointment(self, patient_id, doctor_id, appointment_data):
        try:
            query = """
                INSERT INTO cita (ID_Paciente, ID_Medico, Fecha, Hora, Estado, Motivo)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            values = (
                patient_id,
                doctor_id,
                appointment_data['fecha'],
                appointment_data['hora'],
                'Pendiente',
                appointment_data['descripcion']
            )
            
            self.cursor.execute(query, values)
            self.conn.commit()
            
            # Actualizar el ID_Medico en la tabla paciente
            update_query = """
                UPDATE paciente
                SET ID_Medico = %s
                WHERE ID_Paciente = %s
            """
            update_values = (doctor_id, patient_id)
            
            self.cursor.execute(update_query, update_values)
            self.conn.commit()
            
            messagebox.showinfo("Éxito", "Cita registrada correctamente")

        except Exception as e:
            print(f"Error al guardar la cita: {e}")
            self.show_error(f"Error al guardar la cita: {str(e)}")

    def is_time_available(self, requested_time, secretary_id, appointment_id=None):
        print(f"\n=== Debug is_time_available ===")
        print(f"Verificando disponibilidad para:")
        print(f"Secretaria ID: {secretary_id}")
        print(f"Hora solicitada: {requested_time}")
        print(f"ID de cita actual (si es edición): {appointment_id}")

        # Convertir la hora solicitada a un objeto datetime
        requested_datetime = datetime.strptime(requested_time, '%Y-%m-%d %H:%M')

        # Calcular el rango de tiempo (30 minutos antes y después)
        start_time = requested_datetime - timedelta(minutes=30)
        end_time = requested_datetime + timedelta(minutes=30)

        # Modificar la consulta para excluir la cita actual si estamos editando
        query = """
            SELECT COUNT(*) 
            FROM cita 
            WHERE ID_Medico = %s 
            AND Estado NOT IN ('cancelada', 'completada')
            AND DATE(Fecha) = %s
            AND TIME(Hora) = %s
            AND ID_Cita != COALESCE(%s, -1)
        """

        # Extraer fecha y hora
        date_str = requested_datetime.strftime('%Y-%m-%d')
        time_str = requested_datetime.strftime('%H:%M')

        self.cursor.execute(query, (secretary_id, date_str, time_str, appointment_id))
        count = self.cursor.fetchone()[0]

        if count > 0:
            print("❌ La hora NO está disponible - Existe una cita en el mismo horario")
            return False

        # Verificar superposición de horarios excluyendo la cita actual
        overlap_query = """
            SELECT COUNT(*) 
            FROM cita 
            WHERE ID_Medico = %s 
            AND Estado NOT IN ('cancelada', 'completada')
            AND Fecha = %s
            AND ID_Cita != COALESCE(%s, -1)
            AND (
                (TIME(Hora) BETWEEN TIME(%s) AND TIME(%s))
                OR 
                (TIME(%s) BETWEEN TIME(DATE_SUB(Hora, INTERVAL 30 MINUTE)) 
                    AND TIME(DATE_ADD(Hora, INTERVAL 30 MINUTE)))
            )
        """

        self.cursor.execute(overlap_query, (
            secretary_id,
            date_str,
            appointment_id,
            start_time.strftime('%H:%M'),
            end_time.strftime('%H:%M'),
            time_str
        ))

        overlap_count = self.cursor.fetchone()[0]
        print(f"Citas encontradas en el rango de ±30 minutos: {overlap_count}")

        if overlap_count > 0:
            print("❌ La hora NO está disponible - Existe superposición con otra cita")
            return False
        
        print("✅ La hora está disponible")
        return True

    def create_patients_page(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
                
        # Título
        ctk.CTkLabel(
            self.main_frame,
            text="Gestión de Pacientes",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=(20,10))

        # Frame superior para búsqueda y botón de nuevo paciente
        top_frame = ctk.CTkFrame(self.main_frame)
        top_frame.pack(fill="x", padx=20, pady=10)

        # Barra de búsqueda
        search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(
            top_frame, 
            placeholder_text="Buscar paciente...",
            width=300,
            textvariable=search_var
        )
        search_entry.pack(side="left", padx=(0,10))

        # Botón de búsqueda
        ctk.CTkButton(
            top_frame,
            text="Buscar",
            width=100,
            command=lambda: self.search_patients(search_var.get())
        ).pack(side="left", padx=5)

        # Botón de nuevo paciente
        ctk.CTkButton(
            top_frame,
            text="Nuevo Paciente",
            width=150,
            command=self.show_patient_form
        ).pack(side="right", padx=5)

        # Frame para la lista de pacientes
        list_frame = ctk.CTkFrame(self.main_frame)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Cabeceras de la tabla
        headers = ["Nombre", "Apellidos", "Fecha Nacimiento", "Teléfono", "Acciones"]
        for col, header in enumerate(headers):
            ctk.CTkLabel(
                list_frame,
                text=header,
                font= ctk.CTkFont(weight="bold")
            ).grid(row=0, column=col, padx=10, pady=5, sticky="w")

        # Ejemplo de cómo mostrar los pacientes (esto se conectará con la base de datos)
        self.display_patients(list_frame)

    def display_patients(self, list_frame):
        pacientes = self.get_secretary_patients()  # Esta función obtendría los pacientes de la BD

        for row, paciente in enumerate(pacientes, start=1):
            ctk.CTkLabel(
                list_frame,
                text=paciente[1]  # Nombre
            ).grid(row=row, column=0, padx=10, pady=5, sticky="w")
            
            ctk.CTkLabel(
                list_frame,
                text=paciente[2]  # Apellidos
            ).grid(row=row, column=1, padx=10, pady=5, sticky="w")
            
            ctk.CTkLabel(
                list_frame,
                text=paciente[3]  # Fecha Nacimiento
            ).grid(row=row, column=2, padx=10, pady=5, sticky="w")
            
            ctk.CTkLabel(
                list_frame,
                text=paciente[6]  # Teléfono
            ).grid(row=row, column=3, padx=10, pady=5, sticky="w")

            actions_frame = ctk.CTkFrame(list_frame)
            actions_frame.grid(row=row, column=4, padx=10, pady=5)

            ctk.CTkButton(
                actions_frame,
                text="Editar",
                width=70,
                command=lambda p=paciente: self.show_patient_form(p)
            ).pack(side="left", padx=2)

            ctk.CTkButton(
                actions_frame,
                text="Eliminar",
                width=70,
                fg_color="red",
                command=lambda p=paciente: self.delete_patient(p[0])
            ).pack(side="left", padx=2)

    def show_patient_form(self, patient=None):
        # Crear una nueva ventana para el formulario
        form_window = ctk.CTkToplevel(self)
        form_window.title("Nuevo Paciente" if patient is None else "Editar Paciente")
        form_window.geometry("500x800")

        # Variables para los campos del formulario con valores por defecto vacíos
        nombre_var = ctk.StringVar(value=patient[1] if patient else "")
        apellidos_var = ctk.StringVar(value=patient[2] if patient else "")
        fecha_var = ctk.StringVar(value=patient[3] if patient else "")
        direccion_var = ctk.StringVar(value=patient[4] if patient else "")
        correo_var = ctk.StringVar(value=patient[5] if patient else "")
        telefono_var = ctk.StringVar(value=patient[6] if patient else "")
        nss_var = ctk.StringVar(value=patient[7] if patient else "")

        # Crear los campos del formulario
        fields = [
            ("Nombre:", nombre_var),
            ("Apellidos:", apellidos_var),
            ("Fecha Nacimiento (YYYY-MM-DD):", fecha_var),
            ("Dirección:", direccion_var),
            ("Correo:", correo_var),
            ("Teléfono:", telefono_var),
            ("Número Social:", nss_var)
        ]

        for i, (label, var) in enumerate(fields):
            ctk.CTkLabel(
                form_window,
                text=label
            ).pack(padx=20, pady=(20 if i == 0 else 5))

            entry = ctk.CTkEntry(
                form_window,
                textvariable=var,
                width=300
            )
            entry.pack(padx=20, pady=5)

        # Botones de acción
        buttons_frame = ctk.CTkFrame(form_window)
        buttons_frame.pack(pady=20)

        def on_save():
            data = {
                'nombre': nombre_var.get(),
                'apellidos': apellidos_var.get(),
                'fecha_nacimiento': fecha_var.get(),
                'direccion': direccion_var.get(),
                'correo': correo_var.get(),
                'telefono': telefono_var.get(),
                'numero_social': nss_var.get()
            }
            
            # Validar que los campos no estén vacíos
            if not all(data.values()):
                self.show_error("Todos los campos son obligatorios")
                return
                
            # Validar formato de fecha
            try:
                datetime.strptime(data['fecha_nacimiento'], '%Y-%m-%d')
            except ValueError:
                self.show_error("Formato de fecha inválido. Use YYYY-MM-DD")
                return

            self.save_patient(
                patient[0] if patient else None,
                data,
                form_window
            )

        ctk.CTkButton(
            buttons_frame,
            text="Guardar",
            command=on_save
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            buttons_frame,
            text="Cancelar",
            command=form_window.destroy
        ).pack(side="left", padx=5)

    def get_secretary_patients(self):
        query = "SELECT * FROM Paciente WHERE ID_Medico = %s"
        self.cursor.execute(query, (self.secretary_id,))  # ID de la secretaria actual
        patients = self.cursor.fetchall()
        return patients

    def save_patient(self, patient_id, data, form_window):
        try:
            if not all(data.values()):
                raise ValueError("Todos los campos son obligatorios")

            if patient_id is None:
                # Nuevo paciente
                query = """
                    INSERT INTO Paciente 
                    (Nombre, Apellidos, Fecha_Nacimiento, Direccion, Correo, Telefono, Numero_Social, ID_Medico)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                values = (
                    data['nombre'],
                    data['apellidos'],
                    data['fecha_nacimiento'],
                    data['direccion'],
                    data['correo'],
                    data['telefono'],
                    data['numero_social'],
                    self.secretary_id
                )
            else:
                # Actualizar paciente existente
                query = """
                    UPDATE Paciente
                    SET Nombre = %s, Apellidos = %s, Fecha_Nacimiento = %s, 
                        Direccion = %s, Correo = %s, Telefono = %s, 
                        Numero_Social = %s, ID_Medico = %s
                    WHERE ID_Paciente = %s
                """
                values = (
                    data['nombre'],
                    data['apellidos'],
                    data['fecha_nacimiento'],
                    data['direccion'],
                    data['correo'],
                    data['telefono'],
                    data['numero_social'],
                    self.secretary_id,
                    patient_id
                )

            self.cursor.execute(query, values)
            self.conn.commit()
            form_window.destroy()
            self.create_patients_page()

        except Exception as e:
            self.show_error(f"Error al guardar paciente: {str(e)}")

    def delete_patient(self, patient_id):
        try:
            self.cursor.execute("DELETE FROM Paciente WHERE ID_Paciente = %s", (patient_id,))
            self.conn.commit()
            self.create_patients_page()
        except Exception as e:
            self.show_error(f"Error al eliminar paciente: {str(e)}")

    def show_error(self, message):
        error_window = ctk.CTkToplevel(self)
        error_window.title("Error")
        error_window.geometry("300x150")
        
        ctk.CTkLabel(
            error_window,
            text=message,
            wraplength=250
        ).pack(pady=20)
        
        ctk.CTkButton(
            error_window,
            text="OK",
            command=error_window.destroy
        ).pack(pady=10)

    def search_patients(self, query):
        search_query = """
            SELECT * FROM Paciente
            WHERE Nombre LIKE %s OR Apellidos LIKE %s OR Telefono LIKE %s
        """
        like_query = f"%{query}%"
        self.cursor.execute(search_query, (like_query, like_query, like_query))
        results = self.cursor.fetchall()
        self.create_patients_page(results)

    def change_page(self, page):
        self.current_page.set(page)
        self.show_page()
        
    def show_page(self):
        for page, button in self.nav_buttons.items():
            if page == self.current_page.get():
                button.configure(fg_color=("gray75", "gray25"))
            else:
                button.configure(fg_color=("gray70", "gray30"))
    
        if self.current_page.get() == "appointments":
            self.create_appointments_page()
        elif self.current_page.get() == "patients":
            self.create_patients_page()

user_data = {
    'id': 3,  # Suponiendo que el ID de la secretaria es 3
    'nombre': 'María',
    'apellidos': 'Rodríguez',
    'rol': 3,  # Rol para secretaria
    'correo': 'maria.secretaria@hospital.com'
}


if __name__ == "__main__":
    app = SecretaryScreen(user_data=user_data)  
    
    app.mainloop()