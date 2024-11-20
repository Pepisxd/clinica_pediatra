import tkinter as tk
from customtkinter import CTkTextbox
import customtkinter as ctk
from sklearn.neural_network import MLPClassifier
import pandas as pd
from db_connection import conexion_db

class SistemaDiagnostico(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración de la ventana
        self.title("Sistema de Diagnóstico Médico")
        self.geometry("700x800")
        
        # Configuración de colores
        self.configure(fg_color="#E0E0E0")  # Fondo gris claro
        ctk.set_appearance_mode("light")
        
        # Inicializar conexión a la base de datos
        self.conexion = conexion_db()
        self.todos_sintomas = self.cargar_sintomas_desde_db()
        
        # Normalizar nombres de síntomas
        self.todos_sintomas = [self.normalizar_nombre(sintoma) for sintoma in self.todos_sintomas]

        # Cargar el modelo entrenado
        self.modelo = self.cargar_modelo()

        # Crear un mapeo para alinear los nombres entre los datos y el modelo
        self.mapeo_sintomas = self.generar_mapeo_sintomas()

        self.sintomas_seleccionados = []
        self.checkboxes = []
        self.crear_interfaz()

    def show_patient_data(nombre, apellidos, fecha_nacimiento, direccion, correo, telefono, numero_social, diagnosis_window):
        """
        Muestra los datos del paciente en una ventana de diagnóstico.
        """
        # Crear un texto para mostrar la información del paciente
        patient_info = (
            f"Nombre: {nombre} {apellidos}\n"
            f"Fecha de Nacimiento: {fecha_nacimiento}\n"
            f"Dirección: {direccion}\n"
            f"Correo: {correo}\n"
            f"Teléfono: {telefono}\n"
            f"Número Social: {numero_social}"
        )

        patient_data_textbox = CTkTextbox(diagnosis_window, width=780, height=200)
        patient_data_textbox.pack(padx=10, pady=10)
        patient_data_textbox.insert("0.0", patient_info)
        patient_data_textbox.configure(state="disabled")  # Hacer el textbox de solo lectura

        # Botón para cerrar la ventana
        close_button = ctk.CTkButton(diagnosis_window, text="Cerrar", command=diagnosis_window.destroy)
        close_button.pack(pady=10)
    

    def cargar_modelo(self):
        """Carga el modelo entrenado desde un archivo."""
        try:
            from joblib import load
            modelo = load("modelo_red_neuronal.pkl")
            return modelo
        except FileNotFoundError:
            print("Error: No se encontró el archivo del modelo.")
            exit()
        except Exception as e:
            print(f"Error al cargar el modelo: {e}")
            exit()

    def cargar_sintomas_desde_db(self):
        """Carga la lista de síntomas desde la base de datos."""
        sintomas = []
        try:
            cursor = self.conexion.cursor()
            cursor.execute("SELECT descripcion FROM sintoma")
            sintomas = [row[0] for row in cursor.fetchall()]
            cursor.close()
        except Exception as e:
            print(f"Error al cargar síntomas desde la base de datos: {e}")
            exit()
        return sorted(sintomas)

    def normalizar_nombre(self, nombre):
        """Normaliza los nombres de los síntomas para garantizar consistencia."""
        return nombre.strip().lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("ñ", "n")

    def generar_mapeo_sintomas(self):
        """Genera un mapeo entre los síntomas del modelo y los cargados."""
        sintomas_modelo = [self.normalizar_nombre(s) for s in self.modelo.feature_names_in_]
        mapeo = {}
        for sintoma_modelo in sintomas_modelo:
            for sintoma_cargado in self.todos_sintomas:
                if sintoma_modelo == sintoma_cargado:
                    mapeo[sintoma_modelo] = sintoma_cargado
        return mapeo

    def crear_interfaz(self):
        # Panel izquierdo
        panel_izquierdo = ctk.CTkFrame(self, fg_color="#D0D0D0", width=200)
        panel_izquierdo.pack(side="left", fill="y", padx=10, pady=10)
        
        titulo = ctk.CTkLabel(
            panel_izquierdo, 
            text="Panel de Diagnóstico",
            font=("Arial", 16, "bold")
        )
        titulo.pack(pady=20)

        # Panel principal
        panel_principal = ctk.CTkFrame(self, fg_color="white")
        panel_principal.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Frame para la lista de síntomas
        frame_sintomas = ctk.CTkFrame(panel_principal)
        frame_sintomas.pack(fill="both", expand=True, padx=20, pady=20)

        label_sintomas = ctk.CTkLabel(
            frame_sintomas,
            text="Seleccione los síntomas:",
            font=("Arial", 14)
        )
        label_sintomas.pack(pady=10)

        # Frame para checkboxes en columnas
        frame_checkboxes = ctk.CTkFrame(frame_sintomas, fg_color="transparent")
        frame_checkboxes.pack(fill="both", expand=True)

        # Crear checkboxes en dos columnas
        for i, sintoma in enumerate(self.todos_sintomas):
            col = i % 2
            row = i // 2
            var = tk.BooleanVar()
            checkbox = ctk.CTkCheckBox(
                frame_checkboxes,
                text=sintoma,
                variable=var,
                command=lambda s=sintoma: self.toggle_sintoma(s),
                fg_color="#3498DB",
                hover_color="#2980B9"
            )
            checkbox.grid(row=row, column=col, padx=10, pady=5, sticky="w")
            self.checkboxes.append((checkbox, var))

        # Área de diagnóstico
        self.area_diagnostico = ctk.CTkTextbox(
            panel_principal,
            height=150,
            width=400,
            font=("Arial", 12)
        )
        self.area_diagnostico.pack(pady=20, padx=20)

        # Frame para botones
        frame_botones = ctk.CTkFrame(panel_principal, fg_color="transparent")
        frame_botones.pack(pady=20)

        # Botones
        ctk.CTkButton(
            frame_botones,
            text="Diagnosticar",
            command=self.realizar_diagnostico,
            fg_color="#3498DB",
            hover_color="#2980B9"
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            frame_botones,
            text="Cancelar",
            command=self.cancelar,
            fg_color="#FF0000",
            hover_color="#CC0000"
        ).pack(side="left", padx=5)

    def toggle_sintoma(self, sintoma: str):
        if sintoma in self.sintomas_seleccionados:
            self.sintomas_seleccionados.remove(sintoma)
        else:
            self.sintomas_seleccionados.append(sintoma)

    def realizar_diagnostico(self):
        if not self.sintomas_seleccionados:
            self.area_diagnostico.delete("1.0", "end")
            self.area_diagnostico.insert("1.0", "Por favor, seleccione al menos un síntoma.")
            return

        # Normalizar los nombres de los síntomas seleccionados
        sintomas_normalizados = [self.normalizar_nombre(s) for s in self.sintomas_seleccionados]

        # Crear un vector de entrada para la red neuronal
        vector_entrada = [1 if self.mapeo_sintomas.get(sintoma) in sintomas_normalizados else 0 for sintoma in self.modelo.feature_names_in_]

        # Reorganizar el vector de entrada según el orden del modelo
        entrada_df = pd.DataFrame([vector_entrada], columns=self.modelo.feature_names_in_)

        # Realizar la predicción de probabilidades
        probabilidades = self.modelo.predict_proba(entrada_df)[0]

        # Obtener las tres enfermedades más probables
        indices_top3 = probabilidades.argsort()[-3:][::-1]
        enfermedades_top3 = [(self.modelo.classes_[i], probabilidades[i]) for i in indices_top3]

        # Mostrar diagnóstico
        self.area_diagnostico.delete("1.0", "end")
        diagnostico = "Diagnósticos más probables:\n\n"
        for enfermedad, probabilidad in enfermedades_top3:
            diagnostico += f"{enfermedad}: {probabilidad * 100:.2f}%\n"
        self.area_diagnostico.insert("1.0", diagnostico)

        #sintomas seleccionados
        self.area_diagnostico.insert("end", "\n\nSíntomas seleccionados:\n")
        for sintoma in self.sintomas_seleccionados:
            self.area_diagnostico.insert("end", f"{sintoma}\n")
            

        # Desmarcar todas las casillas
        for checkbox, var in self.checkboxes:
            var.set(False)
        self.sintomas_seleccionados.clear()
        # Aviso para consultar un medico profesional 
        self.area_diagnostico.insert("end", "\n\nPor favor, consulte a un médico profesional para obtener un diagnóstico preciso.")

    def cancelar(self):
        # Limpiar selección y diagnóstico
        self.sintomas_seleccionados.clear()
        self.area_diagnostico.delete("1.0", "end")
        
        # Desmarcar todos los checkboxes
        for checkbox, var in self.checkboxes:
            var.set(False)

if __name__ == "__main__":
    app = SistemaDiagnostico()
    app.mainloop()
