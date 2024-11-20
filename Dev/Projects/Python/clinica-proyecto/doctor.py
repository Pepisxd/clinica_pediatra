import customtkinter as ctk
from tkcalendar import Calendar
from datetime import datetime
import locale
import os
from datetime import datetime, timedelta
from tkinter import messagebox
import diagnostico
from db_connection import conexion_db
from dateutil.relativedelta import relativedelta
import pandas as pd
from diagnostico import SistemaDiagnostico
# Configurar el tema y el modo por defecto
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class DBConnection:
    _connection = None

    @staticmethod
    def get_connection():
        if DBConnection._connection is None:
            DBConnection._connection = conexion_db()  # Asegúrate de usar el método adecuado
        return DBConnection._connection


class DoctorScreen(ctk.CTk):
    def __init__(self, user_data , *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.conn = DBConnection._connection is None

  

        self.conn = DBConnection.get_connection()
        self.cursor = self.conn.cursor()

        self.user_data = user_data
        self.secretary_email = user_data.get("correo")
        self.doctor_id = user_data.get("id") # Extraer el ID desde el diccionario
        self.secretary_name = f"{user_data.get('nombre')} {user_data.get('apellidos')}"
        self.cargar_pacientes()

    def cargar_pacientes(self):
        query = "SELECT * FROM paciente WHERE ID_Medico = %s"
        self.cursor.execute(query, (self.doctor_id,))
        self.pacientes = self.cursor.fetchall()      
      




        


        self.conn = self.conexion_db()
        if not self.conn:
            raise ConnectionError("No se pudo establecer conexión con la base de datos")
        
        self.cursor = self.conn.cursor()
    
        print(f"ID del médico: {self.doctor_id}")
        # Configuración básica de la ventana
        self.title("Sistema de Gestión Médica")
        self.geometry("1420x700")

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
                # Hacer commit de cualquier transacción pendiente
                self.conn.commit()
                
                if hasattr(self, 'cursor') and self.cursor:
                    self.cursor.close()
                self.conn.close()
        except Exception as e:
            print(f"Error al cerrar la conexión: {e}")
        finally:
            self.destroy()

    def get_doctor_id(self, email):
        if not email:
            raise ValueError("Email no proporcionado")
            
        query = """
            SELECT ID_Usuario FROM Usuario
            WHERE Correo = %s AND Rol = 2
        """
        try:
            self.cursor.execute(query, (email,))
            result = self.cursor.fetchone()
            if result:
                return result[0]
            else:
                raise ValueError(f"No se encontró el médico con email: {email}")
        except Exception as e:
            raise ValueError(f"Error en la consulta: {str(e)}")
    
        
    def get_doctor_name(self):
        query = "SELECT Nombre, Apellidos FROM Usuario WHERE ID_Usuario = %s"
        self.cursor.execute(query, (self.doctor_id,))
        result = self.cursor.fetchone()
        if result:
            return f" {result[0]} {result[1]}"
        return "Doctor"
        
    def create_layout(self):
        # Frame lateral (sidebar)
        self.sidebar = ctk.CTkFrame(self, width=200)
        self.sidebar.pack(side="left", fill="y", padx=10, pady=10)

        doctor_name = self.get_doctor_name()
        ctk.CTkLabel(
            self.sidebar,
            text=doctor_name,
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(20, 10))

        # Título del sidebar
        ctk.CTkLabel(
            self.sidebar,
            text="Panel de Médico",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(0, 30))
        
        # Botones de navegación
        self.nav_buttons = {}
        # Agregar esta línea en la sección de navegación
        for page in [("appointments", "Mis Citas"), 
                    ("patients", "Pacientes"),
                    ("diseases", "Enfermedades"),
                    ("diagnosis", "Diagnóstico"),
                    ("laboratory_tests", "Pruebas de Laboratorio & Post-Mortem")]:  # Nueva pestaña
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
        self.main_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
    def create_appointments_page(self):
        # Limpiar el frame principal
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
        # Título
        ctk.CTkLabel(
            self.main_frame,
            text="Agenda de Citas Pediátricas",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=(20, 10))

        # Botón de Agendar Cita (ahora en la parte superior)
        ctk.CTkButton(
            self.main_frame,
            text="Agendar Cita",
            width=200,
            height=40,
            fg_color="#4CAF50",  # Color verde
            hover_color="#45a049",  # Verde más oscuro al pasar el mouse
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

    def display_appointments(self, date_filter=None):
        # Limpiar tabla existente
        for widget in self.table_frame.winfo_children():
            widget.destroy()

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
        params = [self.doctor_id]

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
                # Asegurarse de que la fecha y hora sean objetos datetime
                if isinstance(appt[0], datetime):
                    fecha = appt[0].strftime("%Y-%m-%d")
                else:
                    fecha = appt[0]  # Asumir que ya es una cadena de texto

                if isinstance(appt[1], datetime):
                    hora = appt[1].strftime("%H:%M")
                else:
                    hora = appt[1]  # Asumir que ya es una cadena de texto
                paciente = f"{appt[2]} {appt[3]}"
            
                # Asegurarse de que la fecha de nacimiento sea un string en formato correcto
                fecha_nac = appt[4]
                if not isinstance(fecha_nac, str):
                    fecha_nac = fecha_nac.strftime("%Y-%m-%d")
            
                # Calcular edad del paciente
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
            
                # Estado con color
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
                        hover_color="#C62828",
                        command=lambda id=cita_id: self.update_appointment_status(id, "Cancelada")
                    ).pack(side="left", padx=2)
                    
                if estado == "Pendiente":
                    ctk.CTkButton(
                    action_frame,
                    text="Editar",
                    width=80,
                    fg_color="#3E8E41",
                    hover_color="#2E7D32",
                    command=lambda id=cita_id: self.edit_appointment(id)
                ).pack(side="left", padx=2)

        except Exception as e:
            print(f"Error al mostrar citas: {e}")
            self.show_error(f"Error al cargar las citas: {str(e)}")

        except Exception as e:
            print(f"Error al mostrar citas: {e}")
            self.show_error(f"Error al cargar las citas: {str(e)}")
            
        # Botón de Diagnóstico solo para citas en estado "Confirmada"
        if appt[5] == "Confirmada":
            diagnosis_button = ctk.CTkButton(
                action_frame,
                text="Diagnóstico",
                width=100,
                command=lambda id=appt[7]: self.open_diagnosis_window(id)
            )
            diagnosis_button.pack(side="left", padx=2)
            
    def open_diagnosis_window(self, cita_id):
        # Abrir una nueva ventana con el archivo "Diagnostico.py"
        diagnosis_window = ctk.CTkToplevel(self)
        diagnosis_window.title("Diagnóstico")
        diagnosis_window.geometry("800x600")

        # Cargar los datos del paciente
        patient_data = self.load_patient_data(cita_id)
        print(patient_data)

        # Abrir el archivo "Diagnostico.py" y mostrar los datos del paciente
        diagnostico.show_patient_data(
            patient_data["nombre"],
            patient_data["apellidos"],
            patient_data["fecha_nacimiento"],
            patient_data["direccion"],
            patient_data["correo"],
            patient_data["telefono"],
            patient_data["numero_social"],
            diagnosis_window
        )

    def load_patient_data(self, cita_id):
        # Consulta para obtener los datos del paciente
        query = """
            SELECT 
                p.Nombre, p.Apellidos, p.Fecha_Nacimiento, p.Direccion, p.Correo, p.Telefono, p.Numero_Social
            FROM 
                Paciente p
                JOIN Cita c ON p.ID_Paciente = c.ID_Paciente
            WHERE 
                c.ID_Cita = %s
        """
        self.cursor.execute(query, (cita_id,))
        patient_data = self.cursor.fetchone()

        if patient_data:
            return {
                "nombre": patient_data[0],
                "apellidos": patient_data[1],
                "fecha_nacimiento": patient_data[2],
                "direccion": patient_data[3],
                "correo": patient_data[4],
                "telefono": patient_data[5],
                "numero_social": patient_data[6]
            }
        else:
            self.show_error(f"No se encontraron datos para la cita con ID {cita_id}")
            return None

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
        # Create new window for appointment form
        self.form_window = ctk.CTkToplevel(self)
        self.form_window.title("Nueva Cita" if appointment is None else "Editar Cita")
        self.form_window.geometry("450x600")
        self.form_window.resizable(False, False)

        # Configure grid weights for centering
        self.form_window.grid_columnconfigure(0, weight=1)
        self.form_window.grid_columnconfigure(1, weight=1)

        # Title with colored text
        title_label = ctk.CTkLabel(
            self.form_window,
            text="Nueva Cita" if appointment is None else "Editar Cita",
            font=("Arial", 20, "bold"),
             anchor="center"
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(20, 30), sticky="ew")

        # Patient selection
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

        # Date field
        date_label = ctk.CTkLabel(
            self.form_window,
            text="Fecha:",
            font=("Arial", 12),
            anchor="center",
            width=300
        )
        date_label.grid(row=3, column=0, columnspan=2, padx=10, sticky="ew", pady=(0, 5))

        self.date_entry = ctk.CTkEntry(
            self.form_window,
            width=300,
            placeholder_text="YYYY-MM-DD"
        )
        self.date_entry.grid(row=4, column=0, columnspan=2, padx=10, pady=(0, 20))

        if appointment:
            self.date_entry.insert(0, appointment['fecha'])

        # Time field
        time_label = ctk.CTkLabel(
            self.form_window,
            text="Hora:",
            font=("Arial", 12),
            anchor="center",
            width=300
        )
        time_label.grid(row=5, column=0, columnspan=2, padx=10, sticky="ew", pady=(0, 5))

        self.time_entry = ctk.CTkEntry(
            self.form_window,
            width=300,
            placeholder_text="HH:MM"
        )
        self.time_entry.grid(row=6, column=0, columnspan=2, padx=10, pady=(0, 20))

        if appointment:
            self.time_entry.insert(0, appointment['hora'])

        # Reason field
        reason_label = ctk.CTkLabel(
        self.form_window,
            text="Motivo:",
            font=("Arial", 12),
            anchor="center",
            width=300
        )
        reason_label.grid(row=9, column=0, columnspan=2, padx=10, sticky="ew", pady=(0, 5))

        self.reason_entry = ctk.CTkEntry(
            self.form_window,
            width=300
        )
        self.reason_entry.grid(row=10, column=0, columnspan=2, padx=10, pady=(0, 20))

        if appointment:
            self.reason_entry.insert(0, appointment['motivo'])

        # Buttons frame
        buttons_frame = ctk.CTkFrame(self.form_window, fg_color="transparent")
        buttons_frame.grid(row=11, column=0, columnspan=2, pady=30)

        # Action buttons
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
            hover_color="#C62828",
            command=self.close_appointment_form
        )
        cancel_button.grid(row=0, column=1, padx=10)
        
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

            # Encontrar el ID del paciente seleccionado
            selected_patient = None
            for patient in self.available_patients:
                if f"{patient[1]} {patient[2]}" == selected_patient_name:
                    selected_patient = patient
                    break

            if not selected_patient:
                raise ValueError("No se pudo encontrar el paciente seleccionado")

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
                'fecha': fecha,
                'hora': hora,
                'descripcion': motivo
            }
        
            # Crear un string que combine fecha y hora para verificar disponibilidad
            requested_time = f"{fecha} {hora}"
        
            print("\n=== Verificando disponibilidad de horario ===")
            # Verificar si estamos en modo edición y obtener el ID de la cita
            appointment_id = appointment.get('id') if appointment else None
            if not self.is_time_available(requested_time, self.doctor_id, appointment_id):
                raise ValueError("❌ La hora seleccionada no está disponible. Por favor elige otra.")

            # Si se está editando, actualizar la cita
            if appointment and 'id' in appointment:
                self.update_appointment(appointment['id'], selected_patient[0], appointment_data)
            else:
                # Si es una nueva cita, guardarla
                self.save_appointment(selected_patient[0], appointment_data)

            # Si todo sale bien, cerrar el formulario
            self.close_appointment_form()
            
            # Actualizar la vista de citas
            self.display_appointments()

        except KeyError as e:
            self.show_error(f"Error en los datos de la cita: Falta el campo {str(e)}")
        except Exception as e:
            self.show_error(str(e))
            
    def update_appointment(self, appointment_id, patient_id, appointment_data):
        try:
            print("=== Debug update_appointment ===")
            print(f"ID Cita: {appointment_id}")
            print(f"ID Paciente: {patient_id}")
            print(f"Datos de la cita: {appointment_data}")
            
            # Consulta para actualizar la cita
            query = """
                UPDATE cita
                SET ID_Paciente = %s, Fecha = %s, Hora = %s, Motivo = %s
                WHERE ID_Cita = %s
            """
            values = (
                patient_id,
                appointment_data['fecha'],
                appointment_data['hora'],
                appointment_data['descripcion'],
                appointment_id
            )

            print("Ejecutando UPDATE con valores:", values)
            
            self.cursor.execute(query, values)
            self.conn.commit()
            print("Cita actualizada exitosamente")
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
        #Pacientes sin niguna cita registrada, pacientes disponibles
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

    def save_appointment(self, patient_id, appointment_data):
        try:
            # Debugging: Imprimir datos recibidos
            print("=== Debug save_appointment ===")
            print(f"Patient ID: {patient_id}")
            print(f"Appointment Data: {appointment_data}")

            # Validar que los datos no estén vacíos
            if not all(appointment_data.values()):
                raise ValueError("Todos los campos son obligatorios")

            # Consulta actualizada para coincidir con la estructura de la tabla cita
            query = """
                INSERT INTO cita (ID_Paciente, ID_Medico, Fecha, Hora, Estado, Motivo)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
        
            # Valores actualizados incluyendo el estado inicial como 'Pendiente'
            values = (
                patient_id,
                self.doctor_id,  # ID del médico actual
                appointment_data['fecha'],
                appointment_data['hora'],
                'Pendiente',  # Estado inicial de la cita
                appointment_data['descripcion']  # Este es el Motivo en la tabla
            )
        
            print("Ejecutando INSERT con valores:", values)

            self.cursor.execute(query, values)
            self.conn.commit()
            print("Cita guardada exitosamente")
            
            # Ahora actualizar la tabla paciente para establecer el ID_Medico
            update_query = """
                UPDATE paciente
                SET ID_Medico = %s
                WHERE ID_Paciente = %s
            """
            update_values = (self.doctor_id, patient_id)

            print("Ejecutando UPDATE con valores:", update_values)

            # Ejecutar la actualización del paciente
            self.cursor.execute(update_query, update_values)
            self.conn.commit()
            print("ID_Medico actualizado en la tabla paciente exitosamente")
        
            # Mostrar mensaje de éxito
            messagebox.showinfo("Éxito", "Cita registrada correctamente")

        except Exception as e:
            print(f"Error al guardar la cita: {e}")
            self.show_error(f"Error al guardar la cita: {str(e)}")

    def is_time_available(self, requested_time, doctor_id, appointment_id=None):
        print(f"\n=== Debug is_time_available ===")
        print(f"Verificando disponibilidad para:")
        print(f"Doctor ID: {doctor_id}")
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

        self.cursor.execute(query, (doctor_id, date_str, time_str, appointment_id))
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
            doctor_id,
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
                font=ctk.CTkFont(weight="bold")
            ).grid(row=0, column=col, padx=10, pady=5, sticky="w")

        # Ejemplo de cómo mostrar los pacientes (esto se conectará con la base de datos)
        self.display_patients(list_frame)


    def display_patients(self, list_frame):
        pacientes = self.get_doctor_patients()  # Esta función obtendría los pacientes de la BD

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
                fg_color="#3E8E41",
                hover_color="#2E7D32",
                command=lambda p=paciente: self.edit_patient(p)
            ).pack(side="left", padx=2)

            ctk.CTkButton(
                actions_frame,
                text="Eliminar",
                width=70,
                fg_color="red",
                hover_color="#C62828",
                command=lambda p=paciente: self.delete_patient(p[0])
            ).pack(side="left", padx=2)

    def show_patient_form(self, patient=None):
        # Crear una nueva ventana para el formulario
        form_window = ctk.CTkToplevel(self)
        form_window.title("Nuevo Paciente" if patient is None else "Editar Paciente")
        form_window.geometry("500x800")

        # Debugging: Imprimir los datos del paciente si existe
        print(f"Datos del paciente recibidos en form: {patient}")

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
            
            # Debugging: Imprimir el valor inicial de cada campo
            print(f"Valor inicial de {label}: {var.get()}")

        # Botones de acción
        buttons_frame = ctk.CTkFrame(form_window)
        buttons_frame.pack(pady=20)

        def on_save():
            # Debugging: Imprimir valores antes de guardar
            data = {
                'nombre': nombre_var.get(),
                'apellidos': apellidos_var.get(),
                'fecha_nacimiento': fecha_var.get(),
                'direccion': direccion_var.get(),
                'correo': correo_var.get(),
                'telefono': telefono_var.get(),
                'numero_social': nss_var.get()
            }
            print("Datos a guardar:", data)
            
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
            hover_color="#C62828",
            command=form_window.destroy
        ).pack(side="left", padx=5)

    def get_doctor_patients(self):
        query = "SELECT * FROM Paciente WHERE ID_Medico = %s"
        print(f"Buscando pacientes para el doctor ID: {self.doctor_id}")  
        self.cursor.execute(query, (self.doctor_id,))  # ID del médico actual
        patients = self.cursor.fetchall()
        print(f"Pacientes encontrados: {len(patients)}")
        return patients

    def save_patient(self, patient_id, data, form_window):
            try:
                # Debugging: Imprimir datos recibidos
                print("=== Debug save_patient ===")
                print(f"Patient ID: {patient_id}")
                print(f"Doctor ID: {self.doctor_id}")
                print(f"Data recibida: {data}")

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
                        self.doctor_id
                    )
                    print("Ejecutando INSERT con valores:", values)
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
                        self.doctor_id,
                        patient_id
                    )
                    print("Ejecutando UPDATE con valores:", values)

                self.cursor.execute(query, values)
                self.conn.commit()
                print("Operación exitosa")
                form_window.destroy()
                self.create_patients_page()

            except Exception as e:
                print(f"Error al guardar paciente: {e}")
                self.show_error(f"Error al guardar: {str(e)}")

    def edit_patient(self, patient):
        self.show_patient_form(patient)

    def show_confirmation_dialog(self, message, on_confirm):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Confirmar eliminación")
        dialog.geometry("425x200")
        dialog.resizable(False, False)

        # Make the dialog modal
        dialog.grab_set()

        # Center the dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry('{}x{}+{}+{}'.format(width, height, x, y))

        ctk.CTkLabel(dialog, text=message, wraplength=380).pack(pady=(20, 30))

        button_frame = ctk.CTkFrame(dialog)
        button_frame.pack(fill="x", padx=20, pady=20)

        ctk.CTkButton(
            button_frame,
            text="Cancelar",
            command=dialog.destroy,
            fg_color="red",
            hover_color="#C62828",
        ).pack(side="left")

        ctk.CTkButton(
            button_frame,
            text="Confirmar",
            command=lambda: [on_confirm(), dialog.destroy()],
        ).pack(side="right")

    def delete_patient(self, patient_id):
        # Consultas para verificar si el paciente tiene diagnósticos o citas
        check_diagnosis_query = "SELECT COUNT(*) FROM Diagnostico WHERE ID_Paciente = %s"
        check_appointments_query = "SELECT COUNT(*) FROM Cita WHERE ID_Paciente = %s"

        try:
            # Verificar si el paciente tiene diagnósticos
            self.cursor.execute(check_diagnosis_query, (patient_id,))
            has_diagnosis = self.cursor.fetchone()[0] > 0
    
            # Verificar si el paciente tiene citas activas
            self.cursor.execute(check_appointments_query, (patient_id,))
            has_appointments = self.cursor.fetchone()[0] > 0

            # Si el paciente tiene diagnósticos o citas, mostrar el cuadro de confirmación personalizado
            if has_diagnosis or has_appointments:
                message = ("Este usuario ya tiene un diagnóstico realizado, ¿Realmente deseas eliminarlo?" 
                        if has_diagnosis 
                        else "Este usuario tiene citas programadas, ¿Realmente deseas eliminarlo?")
            
                def on_confirm():
                    if has_diagnosis:
                        self.cursor.execute("DELETE FROM Diagnostico WHERE ID_Paciente = %s", (patient_id,))
                    if has_appointments:
                        self.cursor.execute("DELETE FROM Cita WHERE ID_Paciente = %s", (patient_id,))
                    self.cursor.execute("DELETE FROM Paciente WHERE ID_Paciente = %s", (patient_id,))
                    self.conn.commit()
                    print("Paciente y datos relacionados eliminados:", patient_id)
                    self.create_patients_page()

                self.show_confirmation_dialog(message, on_confirm)
            else:
                # Si no hay diagnósticos ni citas, eliminar directamente
                self.cursor.execute("DELETE FROM Paciente WHERE ID_Paciente = %s", (patient_id,))
                self.conn.commit()
                print("Paciente eliminado:", patient_id)
                self.create_patients_page()

        except Exception as e:
            print(f"Error al eliminar paciente: {e}")
            self.show_error(f"Error al eliminar paciente: {e}")

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
        print("Resultados de la búsqueda:", results)
        self.create_patients_page(results)  
            
    def create_diagnosis_page(self):
        # Limpiar el frame principal
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Crear encabezado y botón "Nuevo Diagnóstico"
        header_frame = ctk.CTkFrame(self.main_frame)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            header_frame,
            text="Diagnósticos Realizados",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(side="left", padx=10, pady=10)

        new_diagnosis_button = ctk.CTkButton(
            header_frame,
            text="Nuevo Diagnóstico",
            command=self.open_new_diagnosis_window
        )
        new_diagnosis_button.pack(side="right", padx=10, pady=10)

        # Frame para la tabla de diagnósticos
        self.table_frame = ctk.CTkFrame(self.main_frame)
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Mostrar los diagnósticos
        self.display_diagnosis()

    def display_diagnosis(self):
        # Limpiar tabla existente
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        # Crear encabezados
        headers = ["Paciente", "Enfermedad", "Fecha Diagnóstico", "Observaciones", "Acciones"]
        for col, header in enumerate(headers):
            ctk.CTkLabel(
                self.table_frame,
                text=header,
                font=ctk.CTkFont(weight="bold")
            ).grid(row=0, column=col, padx=10, pady=5, sticky="w")

        # Consulta para obtener diagnósticos
        query = """
            SELECT 
                CONCAT(p.Nombre, ' ', p.Apellidos) AS Paciente,
                e.Nombre AS Enfermedad,
                d.Fecha_Diagnostico,
                d.Observaciones,
                d.ID_Diagnostico
            FROM 
                Diagnostico d
            JOIN 
                Paciente p ON d.ID_Paciente = p.ID_Paciente
            JOIN 
                Enfermedad e ON d.ID_Enfermedad = e.ID_Enfermedad
            WHERE 
                d.ID_Medico = %s
        """

        try:
            self.cursor.execute(query, (self.doctor_id,))
            diagnosis_records = self.cursor.fetchall()

            for row, diag in enumerate(diagnosis_records, start=1):
                for col, value in enumerate(diag[:-1]):
                    ctk.CTkLabel(self.table_frame, text=value).grid(row=row, column=col, padx=10, pady=5, sticky="w")

                # Agregar botones de Editar y Eliminar
                edit_button = ctk.CTkButton(
                    self.table_frame,
                    text="Editar",
                    fg_color="#3E8E41",
                    hover_color="#2E7D32",
                    command=lambda d=diag: self.open_edit_diagnosis_window(d)
                )
                edit_button.grid(row=row, column=len(headers)-1, padx=10, pady=5)

                delete_button = ctk.CTkButton(
                    self.table_frame,
                    text="Eliminar",
                    fg_color="red",
                    hover_color="#C62828",
                    command=lambda d=diag: self.open_delete_diagnosis_window(d)
                )
                delete_button.grid(row=row, column=len(headers), padx=10, pady=5)

        except Exception as e:
            print(f"Error al mostrar diagnósticos: {e}")
            self.show_error(f"Error al cargar los diagnósticos: {str(e)}")
    
    def open_new_diagnosis_window(self):
        self.diagnosis_window = ctk.CTkToplevel(self.main_frame)
        self.diagnosis_window.title("Nuevo Diagnóstico")
        self.diagnosis_window.geometry("650x700")
        self.diagnosis_window.resizable(False, False)

        # Configure grid weights for centering
        self.diagnosis_window.grid_columnconfigure(0, weight=1)
        self.diagnosis_window.grid_columnconfigure(1, weight=1)

        # Title with colored text
        title_label = ctk.CTkLabel(
            self.diagnosis_window,
            text="Nuevo Diagnóstico",
            font=("Arial", 20, "bold"),
            anchor="center"
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(20, 30), sticky="ew")

        # Patient selection
        patient_label = ctk.CTkLabel(
            self.diagnosis_window,
            text="Paciente:",
            font=("Arial", 12),
            anchor="center",
            width=300
        )
        patient_label.grid(row=1, column=0, columnspan=2, padx=10, sticky="ew", pady=(0, 5))

        # Obtener pacientes disponibles
        pacientes = self.get_pacientes_disponibles()

        # Crear ComboBox en lugar de OptionMenu para el paciente
        self.patient_var = ctk.StringVar(value="Seleccione un paciente")
        self.patient_dropdown = ctk.CTkComboBox(
            self.diagnosis_window,
            variable=self.patient_var,
            values=pacientes,
            width=300
        )
        self.patient_dropdown.grid(row=2, column=0, columnspan=2, padx=10, pady=(0, 20))

        # Enfermedad selection
        enfermedad_label = ctk.CTkLabel(
            self.diagnosis_window,
            text="Enfermedad:",
            font=("Arial", 12),
            anchor="center",
            width=300
        )
        enfermedad_label.grid(row=3, column=0, columnspan=2, padx=10, sticky="ew", pady=(0, 5))

        # Obtener enfermedades disponibles
        enfermedades = self.get_enfermedades()

        # Crear ComboBox para la enfermedad
        self.enfermedad_var = ctk.StringVar(value="Seleccione una enfermedad")
        self.enfermedad_dropdown = ctk.CTkComboBox(
            self.diagnosis_window,
            variable=self.enfermedad_var,
            values=enfermedades,
            width=300
        )
        self.enfermedad_dropdown.grid(row=4, column=0, columnspan=2, padx=10, pady=(0, 20))

        # Campo para síntomas
        sintomas_label = ctk.CTkLabel(
            self.diagnosis_window,
            text="Síntomas:",
            font=("Arial", 12),
            anchor="center",
            width=300
        )
        sintomas_label.grid(row=5, column=0, columnspan=2, padx=10, sticky="ew", pady=(0, 5))

        # Frame para los checkboxes de síntomas
        sintomas_frame = ctk.CTkFrame(self.diagnosis_window)
        sintomas_frame.grid(row=6, column=0, columnspan=2, padx=10, pady=(0, 20), sticky="ew")

        self.sintomas_vars = {}
        columnas = 5  # Número de columnas deseadas

        for i, sintoma in enumerate(self.get_sintomas()):
            self.sintomas_vars[sintoma] = ctk.BooleanVar()
            fila = i // columnas  # Determina la fila del checkbox
            columna = i % columnas  # Determina la columna del checkbox
            ctk.CTkCheckBox(
                sintomas_frame,
                text=sintoma,
                variable=self.sintomas_vars[sintoma]
            ).grid(row=fila, column=columna, sticky='w', padx=10, pady=2)

        # Campo de Observaciones
        observaciones_label = ctk.CTkLabel(
            self.diagnosis_window,
            text="Observaciones:",
            font=("Arial", 12),
            anchor="center",
            width=300
        )
        observaciones_label.grid(row=7, column=0, columnspan=2, padx=10, sticky="ew", pady=(0, 5))

        self.observaciones_entry = ctk.CTkTextbox(
            self.diagnosis_window,
            height=100,
            width=300
        )
        self.observaciones_entry.grid(row=8, column=0, columnspan=2, padx=10, pady=(0, 20))

        # Botones
        buttons_frame = ctk.CTkFrame(self.diagnosis_window, fg_color="transparent")
        buttons_frame.grid(row=9, column=0, columnspan=2, pady=30)

        save_button = ctk.CTkButton(
            buttons_frame,
            text="Guardar",
            width=120,
            command=self.save_new_diagnosis
        )
        save_button.grid(row=0, column=0, padx=10)

        cancel_button = ctk.CTkButton(
            buttons_frame,
            text="Cancelar",
            hover_color="#C62828",
            width=120,
            command=self.diagnosis_window.destroy
        )
        cancel_button.grid(row=0, column=1, padx=10)
    
    def save_new_diagnosis(self):
        paciente_nombre = self.patient_var.get()
        if paciente_nombre == "Seleccione un paciente":
            self.show_error("Debe seleccionar un paciente.")
            return

        enfermedad_nombre = self.enfermedad_var.get()
        if enfermedad_nombre == "Seleccione una enfermedad":
            self.show_error("Debe seleccionar una enfermedad.")
            return

        # Obtener los IDs a partir de los nombres seleccionados
        paciente_id = self.get_paciente_id(paciente_nombre)
        enfermedad_id = self.get_enfermedad_id(enfermedad_nombre)

        sintomas_seleccionados = [sintoma for sintoma, var in self.sintomas_vars.items() if var.get()]
        observaciones = self.observaciones_entry.get("0.0", "end-1c")
        fecha_diagnostico = datetime.now().strftime("%Y-%m-%d")

        # Guardar el diagnóstico
        query = """
            INSERT INTO Diagnostico (ID_Paciente, ID_Medico, ID_Enfermedad, Fecha_Diagnostico, Observaciones)
            VALUES (%s, %s, %s, %s, %s)
        """
        try:
            self.cursor.execute(query, (paciente_id, self.doctor_id, enfermedad_id, fecha_diagnostico, observaciones))
            diagnostico_id = self.cursor.lastrowid

            # Guardar los síntomas relacionados
            for sintoma in sintomas_seleccionados:
                sintoma_id = self.get_sintoma_id(sintoma)
                query = """
                    INSERT INTO Diagnostico_Sintoma (ID_Diagnostico, ID_Sintoma)
                    VALUES (%s, %s)
                """
                self.cursor.execute(query, (diagnostico_id, sintoma_id))

            self.conn.commit()
            self.show_info("Diagnóstico guardado exitosamente.")
            self.diagnosis_window.destroy()
            self.display_diagnosis()
        except Exception as e:
            print(f"Error al guardar el diagnóstico: {e}")
            self.show_error(f"Error al guardar el diagnóstico: {str(e)}")
            
    def open_edit_diagnosis_window(self, diagnosis_data):
        self.diagnosis_window = ctk.CTkToplevel(self.main_frame)
        self.diagnosis_window.title("Editar Diagnóstico")
        self.diagnosis_window.geometry("650x700")
        self.diagnosis_window.resizable(False, False)

        # Configure grid weights for centering
        self.diagnosis_window.grid_columnconfigure(0, weight=1)
        self.diagnosis_window.grid_columnconfigure(1, weight=1)

        # Title with colored text
        title_label = ctk.CTkLabel(
            self.diagnosis_window,
            text="Editar Diagnóstico",
            font=("Arial", 20, "bold"),
            anchor="center"
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(20, 30), sticky="ew")

        # Patient selection
        patient_label = ctk.CTkLabel(
            self.diagnosis_window,
            text="Paciente:",
            font=("Arial", 12),
            anchor="center",
            width=300
        )
        patient_label.grid(row=1, column=0, columnspan=2, padx=10, sticky="ew", pady=(0, 5))

        # Obtener pacientes disponibles
        pacientes = self.get_pacientes_disponibles()

        # Crear ComboBox para el paciente
        self.patient_var = ctk.StringVar()
        self.patient_dropdown = ctk.CTkComboBox(
            self.diagnosis_window,
            variable=self.patient_var,
            values=pacientes,
            width=300
        )
        self.patient_dropdown.grid(row=2, column=0, columnspan=2, padx=10, pady=(0, 20))

        # Enfermedad selection
        enfermedad_label = ctk.CTkLabel(
            self.diagnosis_window,
            text="Enfermedad:",
            font=("Arial", 12),
            anchor="center",
            width=300
        )
        enfermedad_label.grid(row=3, column=0, columnspan=2, padx=10, sticky="ew", pady=(0, 5))

        # Obtener enfermedades disponibles
        enfermedades = self.get_enfermedades()

        # Crear ComboBox para la enfermedad
        self.enfermedad_var = ctk.StringVar()
        self.enfermedad_dropdown = ctk.CTkComboBox(
            self.diagnosis_window,
            variable=self.enfermedad_var,
            values=enfermedades,
            width=300
        )
        self.enfermedad_dropdown.grid(row=4, column=0, columnspan=2, padx=10, pady=(0, 20))

        # Campo para síntomas
        sintomas_label = ctk.CTkLabel(
            self.diagnosis_window,
            text="Síntomas:",
            font=("Arial", 12),
            anchor="center",
            width=300
        )
        sintomas_label.grid(row=5, column=0, columnspan=2, padx=10, sticky="ew", pady=(0, 5))

        # Frame para los checkboxes de síntomas
        sintomas_frame = ctk.CTkFrame(self.diagnosis_window)
        sintomas_frame.grid(row=6, column=0, columnspan=2, padx=10, pady=(0, 20), sticky="ew")

        self.sintomas_vars = {}
        columnas = 5  # Número de columnas deseadas

        for i, sintoma in enumerate(self.get_sintomas()):
            self.sintomas_vars[sintoma] = ctk.BooleanVar()
            fila = i // columnas  # Determina la fila del checkbox
            columna = i % columnas  # Determina la columna del checkbox
            ctk.CTkCheckBox(
                sintomas_frame,
                text=sintoma,
                variable=self.sintomas_vars[sintoma]
            ).grid(row=fila, column=columna, sticky='w', padx=10, pady=2)

        # Campo de Observaciones
        observaciones_label = ctk.CTkLabel(
            self.diagnosis_window,
            text="Observaciones:",
            font=("Arial", 12),
    anchor="center",
            width=300
        )
        observaciones_label.grid(row=7, column=0, columnspan=2, padx=10, sticky="ew", pady=(0, 5))

        self.observaciones_entry = ctk.CTkTextbox(self.diagnosis_window, width=300, height=100)
        self.observaciones_entry.grid(row=8, column=0, columnspan=2, padx=10, pady=(0, 20))

        # Botón de Actualizar
        update_button = ctk.CTkButton(
            self.diagnosis_window,
            text="Actualizar",
            command=self.update_diagnosis
        )
        update_button.grid(row=9, column=0, columnspan=2, padx=10, pady=(0, 20))

        # Lista de síntomas seleccionados
        self.selected_symptoms_label = ctk.CTkLabel(
            self.diagnosis_window,
            text="Síntomas seleccionados:",
            font=("Arial", 12),
            anchor="center",
            width=300
        )
        self.selected_symptoms_label.grid(row=10, column=0, columnspan=2, padx=10, pady=(0, 5))

        self.selected_symptoms_list = ctk.CTkTextbox(self.diagnosis_window, width=300, height=50)
        self.selected_symptoms_list.grid(row=11, column=0, columnspan=2, padx=10, pady=(0, 20))

        # Cargar datos del diagnóstico
        self.load_diagnosis_data(diagnosis_data)
    
    def load_diagnosis_data(self, diagnosis_data):
        self.diagnosis_id = diagnosis_data[4]  # Guardar el ID del diagnóstico
        paciente_nombre = diagnosis_data[0]
        enfermedad_nombre = diagnosis_data[1]
        self.patient_var.set(paciente_nombre)
        self.enfermedad_var.set(enfermedad_nombre)

        # Obtener los IDs de los síntomas relacionados
        sintomas_ids = self.get_symptoms_for_diagnosis(self.diagnosis_id)

        # Marcar los checkboxes según los síntomas relacionados
        for sintoma_id in sintomas_ids:
            if sintoma_id in self.sintomas_vars:
                self.sintomas_vars[sintoma_id].set(True)  # Marca el checkbox si el ID del síntoma está presente

        # Cargar observaciones
        self.observaciones_entry.delete("0.0", "end")
        self.observaciones_entry.insert("0.0", diagnosis_data[3])

        # Mostrar nombres de síntomas seleccionados
        selected_symptoms_names = [self.sintomas_descripciones[sintoma_id] for sintoma_id in sintomas_ids]
        self.selected_symptoms_list.delete("0.0", "end")
        self.selected_symptoms_list.insert("0.0", "\n".join(selected_symptoms_names))   # Muestra los IDs de los síntomas precargados
        
    def get_symptoms_for_diagnosis(self, diagnosis_id):
        query = """
            SELECT ds.ID_Sintoma
            FROM diagnostico_sintoma ds
            WHERE ds.ID_Diagnostico = %s
        """
        self.cursor.execute(query, (diagnosis_id,))
        result = self.cursor.fetchall()
        return [s[0] for s in result]  # Retorna una lista de IDs de síntomas

    def update_diagnosis(self):
        paciente_id = self.get_paciente_id(self.patient_var.get())
        enfermedad_id = self.get_enfermedad_id(self.enfermedad_var.get())
        sintomas_seleccionados = [sintoma for sintoma, var in self.sintomas_vars.items() if var.get()]
        observaciones = self.observaciones_entry.get("0.0", "end-1c")

        # Actualizar el diagnóstico
        query = """
            UPDATE Diagnostico
            SET ID_Paciente = %s, ID_Enfermedad = %s, Observaciones = %s
            WHERE ID_Diagnostico = %s
        """
        try:
            self.cursor.execute(query, (paciente_id, enfermedad_id, observaciones, self.diagnosis_id))

            # Eliminar los síntomas existentes
            query = "DELETE FROM Diagnostico_Sintoma WHERE ID_Diagnostico = %s"
            self.cursor.execute(query, (self.diagnosis_id,))

            # Guardar los nuevos síntomas relacionados
            for sintoma in sintomas_seleccionados:
                sintoma_id = self.get_sintoma_id(sintoma)
                query = """
                    INSERT INTO Diagnostico_Sintoma (ID_Diagnostico, ID_Sintoma)
                    VALUES (%s, %s)
                """
                self.cursor.execute(query, (self.diagnosis_id, sintoma_id))

            self.conn.commit()
            self.show_info("Diagnóstico actualizado exitosamente.")
            self.diagnosis_window.destroy()  # Cierra la ventana después de actualizar
            self.display_diagnosis()
        except Exception as e:
            print(f"Error al actualizar el diagnóstico: {e}")
            self.show_error(f"Error al actualizar el diagnóstico: {str(e)}")
            
    def get_paciente_id(self, paciente_nombre):
        query = """
            SELECT ID_Paciente 
            FROM Paciente
            WHERE CONCAT(Nombre, ' ', Apellidos) = %s
        """
        self.cursor.execute(query, (paciente_nombre,))
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    def get_enfermedad_id(self, enfermedad_nombre):
        query = """
            SELECT ID_Enfermedad
            FROM Enfermedad
            WHERE Nombre = %s
        """
        self.cursor.execute(query, (enfermedad_nombre,))
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    def get_sintoma_id(self, sintoma_descripcion):
        query = """
            SELECT ID_Sintoma
            FROM Sintoma
            WHERE Descripcion = %s
        """
        self.cursor.execute(query, (sintoma_descripcion,))
        result = self.cursor.fetchone()
        return result[0] if result else None

        
    def get_pacientes_disponibles(self):
        query = """
            SELECT CONCAT(Nombre, ' ', Apellidos) AS Nombre_Completo
            FROM Paciente
            WHERE ID_Paciente NOT IN (SELECT ID_Paciente FROM Diagnostico)
        """
        self.cursor.execute(query)
        pacientes = self.cursor.fetchall()
        return [p[0] for p in pacientes] if pacientes else []
    
    def get_medicos(self):
        query = "SELECT ID_Usuario, CONCAT(Nombre, ' ', Apellidos) AS NombreCompleto FROM Usuario WHERE Rol = 2"  # Asumiendo que Rol 1 es médico
        self.cursor.execute(query)
        medicos = self.cursor.fetchall()
        return [f"{m[1]} (ID: {m[0]})" for m in medicos]  # Retornar una lista de nombres con ID

    def get_enfermedades(self):
        query = "SELECT Nombre FROM Enfermedad"
        self.cursor.execute(query)
        enfermedades = self.cursor.fetchall()
        return [e[0] for e in enfermedades]

    def get_sintomas(self):
        query = "SELECT Descripcion FROM Sintoma"
        self.cursor.execute(query)
        sintomas = self.cursor.fetchall()
        return [s[0] for s in sintomas]
    
    def open_delete_diagnosis_window(self, diagnosis_data):
        confirmation_window = ctk.CTkToplevel(self)
        confirmation_window.title("Eliminar Diagnóstico")
        confirmation_window.geometry("350x150")

        ctk.CTkLabel(confirmation_window, text="¿Estás seguro de que deseas eliminar este diagnóstico?").pack(pady=10)

        def confirm_delete():
            try:
                # Eliminar registros de Diagnostico_Sintoma
                query = "DELETE FROM Diagnostico_Sintoma WHERE ID_Diagnostico = %s"
                self.cursor.execute(query, (diagnosis_data[4],))
                self.conn.commit()

                # Eliminar diagnóstico de Diagnostico
                query = "DELETE FROM Diagnostico WHERE ID_Diagnostico = %s"
                self.cursor.execute(query, (diagnosis_data[4],))
                self.conn.commit()

                self.show_info("Diagnóstico eliminado exitosamente.")
                confirmation_window.destroy()
                self.display_diagnosis()  # Actualizar la tabla de diagnósticos
            except Exception as e:
                print(f"Error al eliminar el diagnóstico: {e}")
                self.show_error(f"Error al eliminar el diagnóstico: {str(e)}")

        ctk.CTkButton(confirmation_window, text="Confirmar", command=confirm_delete).pack(side="left", padx=20, pady=10)
        cancel_button = ctk.CTkButton(confirmation_window, text="Cancelar", command=confirmation_window.destroy, fg_color="red", hover_color="#C62828")
        cancel_button.pack(side="right", padx=20, pady=10)
        
    def show_info(self, message):
        messagebox.showinfo("Información", message)

    def show_error(self, message):
        messagebox.showerror("Error", message)
            
    def create_diseases_page(self):
        # Limpiar el frame principal
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Título
        ctk.CTkLabel(
            self.main_frame,
            text="Gestión de Enfermedades",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=(20, 10))

        # Botón para agregar nueva enfermedad
        ctk.CTkButton(
            self.main_frame,
            text="Nueva Enfermedad",
            command=self.show_disease_form
        ).pack(pady=(0, 20), anchor="w", padx=20)

        # Botón para gestionar síntomas
        ctk.CTkButton(
            self.main_frame,
            text="Gestionar Síntomas",
            command=self.show_symptom_crud
        ).pack(pady=(0, 20), anchor="e", padx=20)  # Botón en la esquina superior derecha

        # Frame para la lista de enfermedades con barra de desplazamiento
        scrollable_frame = ctk.CTkScrollableFrame(self.main_frame)
        scrollable_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Cabeceras de la tabla
        headers = ["Nombre", "Descripción", "Gravedad", "Acciones"]
        for col, header in enumerate(headers):
            ctk.CTkLabel(
                scrollable_frame,
                text=header,
                font=ctk.CTkFont(weight="bold")
            ).grid(row=0, column=col, padx=10, pady=5, sticky="w")

        # Mostrar las enfermedades
        self.display_diseases(scrollable_frame)

    def display_diseases(self, list_frame):
        query = "SELECT * FROM enfermedad"
        self.cursor.execute(query)
        diseases = self.cursor.fetchall()

        for row, disease in enumerate(diseases, start=1):
            ctk.CTkLabel(list_frame, text=disease[1]).grid(row=row, column=0, padx=10, pady=5, sticky="w")  # Nombre
            ctk.CTkLabel(list_frame, text=disease[2]).grid(row=row, column=1, padx=10, pady=5, sticky="w")  # Descripción
            ctk.CTkLabel(list_frame, text=disease[3]).grid(row=row, column=2, padx=10, pady=5, sticky="w")  # Gravedad

            actions_frame = ctk.CTkFrame(list_frame)
            actions_frame.grid(row=row, column=3, padx=10, pady=5)

            ctk.CTkButton(
                actions_frame,
                text="Editar",
                fg_color="#3E8E41",
                hover_color="#2E7D32",
                command=lambda d=disease: self.show_disease_form(d)
            ).pack(side="left", padx=2)

            ctk.CTkButton(
                actions_frame,
                text="Eliminar",
                fg_color="red",
                hover_color="#C62828",
                command=lambda d=disease: self.delete_disease(d[0])  # d[0] es el ID_Enfermedad
            ).pack(side="left", padx=2)
            
    def show_disease_form(self, disease=None):
        # Crear una nueva ventana para el formulario
        self.form_window = ctk.CTkToplevel(self)
        self.form_window.title("Nueva Enfermedad" if disease is None else "Editar Enfermedad")
        self.form_window.geometry("800x600")  # Ajustar el tamaño de la ventana

        # Variables para los campos del formulario
        name_var = ctk.StringVar(value=disease[1] if disease else "")
        description_var = ctk.StringVar(value=disease[2] if disease else "")
        severity_var = ctk.IntVar(value=disease[3] if disease else 1)

        # Crear los campos del formulario
        ctk.CTkLabel(self.form_window, text="Nombre:").pack(pady=3)
        ctk.CTkEntry(self.form_window, textvariable=name_var).pack(pady=4)

        ctk.CTkLabel(self.form_window, text="Descripción:").pack(pady=3)
        ctk.CTkEntry(self.form_window, textvariable=description_var, width=300).pack(pady=4, padx=30)

        ctk.CTkLabel(self.form_window, text="Gravedad (1-10):").pack(pady=3)
        ctk.CTkEntry(self.form_window, textvariable=severity_var).pack(pady=4)

        # Crear un marco para los checkboxes
        checkboxes_frame = ctk.CTkFrame(self.form_window)
        checkboxes_frame.pack(pady=10, fill="both", expand=True)

        # Obtener síntomas
        self.cursor.execute("SELECT ID_Sintoma, Descripcion FROM sintoma")
        sintomas = self.cursor.fetchall()

        # Crear un diccionario para almacenar las variables de los checkboxes
        self.sintoma_vars = {}
        checkboxes_per_column = 5  # Número de checkboxes por columna
        num_columns = (len(sintomas) + checkboxes_per_column - 1) // checkboxes_per_column  # Calcular el número de columnas

        # Crear un marco para cada columna
        for col in range(num_columns):
            column_frame = ctk.CTkFrame(checkboxes_frame)
            column_frame.pack(side="left", padx=10, pady=10)

            # Agregar checkboxes a la columna
            for row in range(checkboxes_per_column):
                index = col * checkboxes_per_column + row
                if index < len(sintomas):
                    sintoma_id, sintoma_desc = sintomas[index]
                    var = ctk.BooleanVar()
                    self.sintoma_vars[sintoma_id] = var

                    # Verificar si la enfermedad ya tiene este síntoma relacionado
                    if disease:
                        self.cursor.execute("SELECT 1 FROM enfermedad_sintoma WHERE ID_Enfermedad = %s AND ID_Sintoma = %s", (disease[0], sintoma_id))
                        if self.cursor.fetchone():
                            var.set(True)  # Marcar el checkbox si ya está relacionado

                    # Centrar el checkbox
                    ctk.CTkCheckBox(column_frame, text=sintoma_desc, variable=var).pack(anchor="w")

        # Botones de acción
        buttons_frame = ctk.CTkFrame(self.form_window)
        buttons_frame.pack(pady=(5, 10))  # Ajustar el espacio entre checkboxes y botones

        ctk.CTkButton(
            buttons_frame,
            text="Guardar",
            command=lambda: self.save_disease(disease[0] if disease else None, name_var.get(), description_var.get(), severity_var.get())
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            buttons_frame,
            text="Cancelar",
            hover_color="#C62828",
            command=self.form_window.destroy
        ).pack(side="left", padx=5)

    def save_disease(self, disease_id, name, description, severity):
        try:
            if disease_id:
                # Actualizar enfermedad existente
                query = """
                    UPDATE enfermedad
                    SET Nombre = %s, Descripcion = %s, Gravedad = %s
                    WHERE ID_Enfermedad = %s
                """
                values = (name, description, severity, disease_id)
            else:
                # Insertar nueva enfermedad
                query = """
                    INSERT INTO enfermedad (Nombre, Descripcion, Gravedad)
                    VALUES (%s, %s, %s)
                """
                values = (name, description, severity)

            self.cursor.execute(query, values)
            self.conn.commit()

            # Obtener el ID de la enfermedad recién creada o actualizada
            if not disease_id:
                disease_id = self.cursor.lastrowid

    # Actualizar la tabla enfermedad_sintoma
            self.cursor.execute("DELETE FROM enfermedad_sintoma WHERE ID_Enfermedad = %s", (disease_id,))  # Eliminar relaciones existentes

            for sintoma_id, var in self.sintoma_vars.items():
                if var.get():  # Si el checkbox está marcado
                    self.cursor.execute("INSERT INTO enfermedad_sintoma (ID_Enfermedad, ID_Sintoma) VALUES (%s, %s)", (disease_id, sintoma_id))

            self.conn.commit()
            self.form_window.destroy()
            self.create_diseases_page()  # Actualizar la lista de enfermedades
        except Exception as e:
            print(f"Error al guardar enfermedad: {e}")
            self.show_error(f"Error al guardar enfermedad: {str(e)}")

    def delete_disease(self, disease_id):
        try:
            # Primero, eliminar la referencia a la enfermedad en la tabla diagnostico
            update_diagnostico_query = """
                UPDATE diagnostico 
                SET ID_Enfermedad = NULL 
                WHERE ID_Enfermedad = %s
            """
            self.cursor.execute(update_diagnostico_query, (disease_id,))
            
            # Luego, eliminar registros relacionados en la tabla enfermedad_sintoma
            delete_relations_query = "DELETE FROM enfermedad_sintoma WHERE ID_Enfermedad = %s"
            self.cursor.execute(delete_relations_query, (disease_id,))
            
            # Finalmente, eliminar la enfermedad
            query = "DELETE FROM enfermedad WHERE ID_Enfermedad = %s"
            self.cursor.execute(query, (disease_id,))
            
            self.conn.commit()
            self.create_diseases_page()  # Actualizar la lista de enfermedades
        except Exception as e:
            print(f"Error al eliminar enfermedad: {e}")
            self.show_error(f"Error al eliminar enfermedad: {str(e)}")
            
    def show_symptom_crud(self):
        # Crear una nueva ventana para gestionar síntomas
        self.symptom_window = ctk.CTkToplevel(self)
        self.symptom_window.title("Gestión de Síntomas")
        self.symptom_window.geometry("600x700")

        # Frame para la lista de síntomas
        self.symptom_frame = ctk.CTkScrollableFrame(self.symptom_window)
        self.symptom_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Cabeceras de la tabla
        ctk.CTkLabel(self.symptom_frame, text="ID").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self.symptom_frame, text="Descripción").grid(row=0, column=1, padx=10, pady=5, sticky="w")
        ctk.CTkButton(self.symptom_frame, text="Agregar Síntoma", command=self.add_symptom).grid(row=0, column=2, padx=10, pady=5)

        # Mostrar los síntomas
        self.display_symptoms()

    def display_symptoms(self):
        query = "SELECT * FROM sintoma"
        self.cursor.execute(query)
        sintomas = self.cursor.fetchall()

        for row, sintoma in enumerate(sintomas, start=1):
            ctk.CTkLabel(self.symptom_frame, text=sintoma[0]).grid(row=row, column=0, padx=10, pady=5, sticky="w")  # ID
            ctk.CTkLabel(self.symptom_frame, text=sintoma[1]).grid(row=row, column=1, padx=10, pady=5, sticky="w")  # Descripción

            actions_frame = ctk.CTkFrame(self.symptom_frame)
            actions_frame.grid(row=row, column=2, padx=10, pady=5)

            ctk.CTkButton(
                actions_frame,
                text="Editar",
                fg_color="#3E8E41",
                hover_color="#2E7D32",
                command=lambda s=sintoma: self.edit_symptom(s)
            ).pack(side="left", padx=2)

            ctk.CTkButton(
                actions_frame,
                text="Eliminar",
                fg_color="red",
                hover_color="#C62828",
                command=lambda s=sintoma: self.delete_symptom(s[0])  # s[0] es el ID_Sintoma
            ).pack(side="left", padx=2)

    def add_symptom(self):
        # Crear una ventana para agregar un nuevo síntoma
        self.add_symptom_window = ctk.CTkToplevel(self)
        self.add_symptom_window.title("Agregar Síntoma")
        self.add_symptom_window.geometry("300x200")

        description_var = ctk.StringVar()

        ctk.CTkLabel(self.add_symptom_window, text="Descripción:").pack(pady=10)
        ctk.CTkEntry(self.add_symptom_window, textvariable=description_var).pack(pady=5)

        ctk.CTkButton(
            self.add_symptom_window,
            text="Guardar",
            command=lambda: self.save_symptom(None, description_var.get())
        ).pack(pady=10)

        ctk.CTkButton(
            self.add_symptom_window,
            text="Cancelar",
            hover_color="#C62828",
            command=self.add_symptom_window.destroy
        ).pack(pady=5)

    def edit_symptom(self, symptom):
        # Crear una ventana para editar un síntoma existente
        self.edit_symptom_window = ctk.CTkToplevel(self)
        self.edit_symptom_window.title("Editar Síntoma")
        self.edit_symptom_window.geometry("300x200")

        description_var = ctk.StringVar(value=symptom[1])

        ctk.CTkLabel(self.edit_symptom_window, text="Descripción:").pack(pady=10)
        ctk.CTkEntry(self.edit_symptom_window, textvariable=description_var).pack(pady=5)

        ctk.CTkButton(
            self.edit_symptom_window,
            text="Guardar",
            command=lambda: self.save_symptom(symptom[0], description_var.get())
        ).pack(pady=10)

        ctk.CTkButton(
            self.edit_symptom_window,
            text="Cancelar",
            hover_color="#C62828",
            command=self.edit_symptom_window.destroy
        ).pack(pady=5)

    def save_symptom(self, symptom_id, description):
        try:
            if symptom_id:
                # Actualizar síntoma existente
                query = "UPDATE sintoma SET Descripcion = %s WHERE ID_Sintoma = %s"
                values = (description, symptom_id)
            else:
                # Insertar nuevo síntoma
                query = "INSERT INTO sintoma (Descripcion) VALUES (%s)"
                values = (description,)

            self.cursor.execute(query, values)
            self.conn.commit()
            self.add_symptom_window.destroy() if not symptom_id else self.edit_symptom_window.destroy()
            self.display_symptoms()  # Actualizar la lista de síntomas
        except Exception as e:
            print(f"Error al guardar síntoma: {e}")
            self.show_error(f"Error al guardar síntoma: {str(e)}")

    def delete_symptom(self, symptom_id):
        try:
            # Eliminar registros relacionados en la tabla enfermedad_sintoma
            delete_relations_query = "DELETE FROM enfermedad_sintoma WHERE ID_Sintoma = %s"
            self.cursor.execute(delete_relations_query, (symptom_id,))
            
            query = "DELETE FROM sintoma WHERE ID_Sintoma = %s"
            self.cursor.execute(query, (symptom_id,))
            self.conn.commit()
            self.display_symptoms()  # Actualizar la lista de síntomas
        except Exception as e:
            print(f"Error al eliminar síntoma: {e}")
            self.show_error(f"Error al eliminar síntoma: {str(e)}")




            
    def create_laboratory_tests_page(self):
        # Limpiar el frame principal
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Título
        ctk.CTkLabel(
            self.main_frame,
            text="Pruebas de Laboratorio & Post-Mortem",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=(20, 10))

        # Botón de nueva prueba
        ctk.CTkButton(
            self.main_frame,
            text="Nueva Prueba",
            command=self.show_laboratory_test_form
        ).pack(pady=(0, 20), anchor="w", padx=20)

        # Frame para la tabla de pruebas
        self.table_frame = ctk.CTkFrame(self.main_frame)
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Mostrar las pruebas
        self.display_laboratory_tests()


    def display_laboratory_tests(self):
        # Limpiar tabla existente
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        # Crear encabezados
        headers = ["ID", "Nombre", "Tipo", "Médico", "Diagnóstico", "Resultado", "Acciones"]
        for col, header in enumerate(headers):
            ctk.CTkLabel(
                self.table_frame,
                text=header,
                font=ctk.CTkFont(weight="bold")
            ).grid(row=0, column=col, padx=10, pady=5, sticky="w")

        # Consulta para obtener las pruebas de laboratorio
        query = """
            SELECT p.ID_Prueba, p.Nombre, 
                CASE p.Tipo 
                    WHEN 1 THEN 'Laboratorio' 
                    WHEN 2 THEN 'Post-Mortem' 
                END AS Tipo, 
                CONCAT(u.Nombre, ' ', u.Apellidos) AS Medico, 
                e.Nombre AS Enfermedad, 
                p.Descripcion,
                p.Resultado
            FROM prueba p
            JOIN usuario u ON p.ID_Medico = u.ID_Usuario
            JOIN diagnostico d ON p.ID_Diagnostico = d.ID_Diagnostico
            JOIN enfermedad e ON d.ID_Enfermedad = e.ID_Enfermedad
            WHERE p.ID_Medico = %s
        """

        self.cursor.execute(query, (self.doctor_id,))
        tests = self.cursor.fetchall()

        for row, test in enumerate(tests, start=1):
            # Mostrar datos en la tabla, omitiendo la descripción si no quieres mostrarla
            ctk.CTkLabel(self.table_frame, text=test[0]).grid(row=row, column=0, padx=10, pady=5, sticky="w")  # ID
            ctk.CTkLabel(self.table_frame, text=test[1]).grid(row=row, column=1, padx=10, pady=5, sticky="w")  # Nombre
            ctk.CTkLabel(self.table_frame, text=test[2]).grid(row=row, column=2, padx=10, pady=5, sticky="w")  # Tipo
            ctk.CTkLabel(self.table_frame, text=test[3]).grid(row=row, column=3, padx=10, pady=5, sticky="w")  # Médico
            ctk.CTkLabel(self.table_frame, text=test[4]).grid(row=row, column=4, padx=10, pady=5, sticky="w")  # Diagnóstico
            ctk.CTkLabel(self.table_frame, text=test[5]).grid(row=row, column=5, padx=10, pady=5, sticky="w")  # Descripción
            ctk.CTkLabel(self.table_frame, text=test[6]).grid(row=row, column=6, padx=10, pady=5, sticky="w")  # Resultado

            # Agregar botones de Editar y Eliminar
            actions_frame = ctk.CTkFrame(self.table_frame)
            actions_frame.grid(row=row, column=len(headers)-1, padx=10, pady=5)

            ctk.CTkButton(
                actions_frame,
                text="Editar",
                fg_color="#3E8E41",
                hover_color="#2E7D32",
                command=lambda t=test: self.show_laboratory_test_form(t)
            ).pack(side="left", padx=2)

            ctk.CTkButton(
                actions_frame,
                text="Eliminar",
                fg_color="red",
                hover_color="#C62828",
                command=lambda t=test: self.delete_laboratory_test(t[0])  # t[0] debe ser el ID_Prueba
            ).pack(side="left", padx=2)
            
            ctk.CTkButton(
                actions_frame,
                text="Diagnosticar con motor",
                command= self.open_diagnosis_window
            ).pack(side="left", padx=2)

    def open_diagnosis_window(self):
        # Crear una nueva ventana de diagnóstico usando la clase SistemaDiagnostico
        diagnosis_window = SistemaDiagnostico()
        diagnosis_window.grab_set()  # Bloquear la ventana principal



    def get_sintomas_from_test(self, test):
        # Simulación de extracción de síntomas asociados a la prueba
        # Puedes personalizar esta lógica según tu estructura de datos
        return ["fiebre", "tos", "dolor de cabeza"]  # Ejemplo

    def show_diagnosis_result(self, result_text):
        result_window = ctk.CTkToplevel(self)
        result_window.title("Resultados del Diagnóstico")
        result_window.geometry("400x300")

        result_label = ctk.CTkTextbox(result_window, width=380, height=260)
        result_label.pack(pady=10, padx=10)
        result_label.insert("1.0", result_text)
        result_label.configure(state="disabled")

        close_button = ctk.CTkButton(result_window, text="Cerrar", command=result_window.destroy)
        close_button.pack(pady=10)

                 
    def show_laboratory_test_form(self, test=None):
        self.form_window = ctk.CTkToplevel(self)
        self.form_window.title("Nueva Prueba" if test is None else "Editar Prueba")
        self.form_window.geometry("400x500")

        # Variables para los campos del formulario
        nombre_var = ctk.StringVar(value=test[1] if test else "")  # Nombre
        descripcion_var = ctk.StringVar(value=test[5] if test else "")  # Descripción, si no está en la consulta
        resultado_var = ctk.StringVar(value=test[6] if test else "")  # Resultado

        # Establecer el tipo visualmente pero usar el valor numérico internamente
        tipo_var = ctk.StringVar(value="Laboratorio" if test and test[2] == "Laboratorio" else "Post-Mortem")

        # Tipo de prueba
        ctk.CTkLabel(self.form_window, text="Tipo de Prueba:").pack(pady=5)
        tipo_menu = ctk.CTkComboBox(self.form_window, variable=tipo_var, 
                                    values=["Laboratorio", "Post-Mortem"], 
                                    state="readonly")
        tipo_menu.pack(pady=5)

        # Nombre
        ctk.CTkLabel(self.form_window, text="Nombre:").pack(pady=5)
        ctk.CTkEntry(self.form_window, textvariable=nombre_var).pack(pady=5)

            # Descripción
        ctk.CTkLabel(self.form_window, text="Descripción:").pack(pady=5)
        ctk.CTkEntry(self.form_window, textvariable=descripcion_var).pack(pady=5)

        # Resultado
        ctk.CTkLabel(self.form_window, text="Resultado:").pack(pady=5)
        ctk.CTkEntry(self.form_window, textvariable=resultado_var).pack(pady=5)

        # Menú desplegable para seleccionar diagnóstico
        ctk.CTkLabel(self.form_window, text="Diagnóstico:").pack(pady=5)
        self.diagnostico_var = ctk.StringVar(value="Seleccione un diagnóstico")
        self.diagnostico_dropdown = ctk.CTkComboBox(self.form_window, variable=self.diagnostico_var, 
                                                    values=self.get_diagnosticos(), width=300)
        self.diagnostico_dropdown.pack(pady=5)

        # Precarga de datos si se está editando
        if test:
            self.diagnostico_var.set(f"{test[4]} (ID: {test[0]})")  # Establecer el diagnóstico basado en el ID

        # Botones de acción
        buttons_frame = ctk.CTkFrame(self.form_window)
        buttons_frame.pack(pady=20)

        ctk.CTkButton(
            buttons_frame,
            text="Guardar",
            command=lambda: self.save_laboratory_test(test[0] if test else None, 
                                                        nombre_var.get(), 
                                                        descripcion_var.get(), 
                                                        resultado_var.get(), 
                                                        tipo_menu.get())
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            buttons_frame,
            text="Cancelar",
            hover_color="#C62828",
            command=self.form_window.destroy
        ).pack(side="left", padx=5)

    def get_diagnosticos(self):
        query = """
            SELECT d.ID_Diagnostico, e.Nombre 
            FROM diagnostico d
            JOIN enfermedad e ON d.ID_Enfermedad = e.ID_Enfermedad
            WHERE d.ID_Medico = %s
        """
        self.cursor.execute(query, (self.doctor_id,))
        results = self.cursor.fetchall()
        return [f"{nombre} (ID: {id_diagnostico})" for id_diagnostico, nombre in results]



    def save_laboratory_test(self, test_id, nombre, descripcion, resultado, tipo):
        try:
            # Convertir tipo visual a valor numérico
            tipo_value = 1 if tipo == "Laboratorio" else 2

            if test_id:
                query = """
                    UPDATE prueba 
                    SET Nombre = %s, Descripcion = %s, Resultado = %s, Tipo = %s 
                    WHERE ID_Prueba = %s
                """
                self.cursor.execute(query, (nombre, descripcion, resultado, tipo_value, test_id))
            else:
                # Obtener el ID del diagnóstico seleccionado
                diagnostico_id = self.diagnostico_var.get().split(" (ID: ")[-1].strip(")")

                query = """
                    INSERT INTO prueba (Nombre, Descripcion, Resultado, Tipo, ID_Diagnostico, ID_Medico) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                self.cursor.execute(query, (nombre, descripcion, resultado, tipo_value, diagnostico_id, self.doctor_id))

            self.conn.commit()
            self.form_window.destroy()
            self.display_laboratory_tests()  # Actualizar la tabla de pruebas
        except Exception as e:
            print(f"Error al guardar la prueba: {e}")
            self.show_error(f"Error al guardar la prueba: {str(e)}")

    def delete_laboratory_test(self, test_id):
        confirmation_window = ctk.CTkToplevel(self)
        confirmation_window.title("Eliminar Prueba")
        confirmation_window.geometry("350x150")

        ctk.CTkLabel(confirmation_window, text="¿Estás seguro de que deseas eliminar esta Prueba?").pack(pady=10)
        try:
            print(f"Intentando eliminar la prueba con ID: {test_id}")  # Verifica el ID que se intenta eliminar
            query = "DELETE FROM prueba WHERE ID_Prueba = %s"
            self.cursor.execute(query, (test_id,))  # Asegúrate de que test_id sea un entero
            self.conn.commit()
            self.display_laboratory_tests()  # Actualizar la lista de pruebas
        except Exception as e:
            print(f"Error al eliminar prueba: {e}")
            self.show_error(f"Error al eliminar prueba: {str(e)}")

    def change_page(self, page):
        self.current_page.set(page)
        self.show_page()
        
    def show_page(self):
        # Actualizar el estilo de los botones
        for page, button in self.nav_buttons.items():
            if page == self.current_page.get():
                button.configure(fg_color=("gray75", "gray25"))
            else:
                button.configure(fg_color=("gray70", "gray30"))
    
        # Mostrar la página correspondiente
        if self.current_page.get() == "appointments":
            self.create_appointments_page()
        elif self.current_page.get() == "patients":
            self.create_patients_page()
        elif self.current_page.get() == "diagnosis":
            self.create_diagnosis_page() # Llama a la función que muestra los diagnósticos
        elif self.current_page.get() == "diseases":
            self.create_diseases_page()
        elif self.current_page.get() == "laboratory_tests":
            self.create_laboratory_tests_page()



user_data = {
    'id': 2,  # Suponiendo que el ID de la secretaria es 3
    'nombre': 'Dr. Juan',
    'apellidos': 'García López',
    'rol': 2,  
    'correo': 'juan.pediatra@hospital.com'
}


if __name__ == "__main__":
    app = DoctorScreen(user_data=user_data)
    app.mainloop()
