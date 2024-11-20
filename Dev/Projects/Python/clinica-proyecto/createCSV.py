import pandas as pd
import numpy as np

# Lista de síntomas
sintomas = [
    'llanto excesivo', 'Irritabilidad', 'fiebre', 'dificultad para dormir',
    'perdida de apetito', 'diarrea', 'tos', 'congestion nasal', 'dolor de oido',
    'vomitos', 'dolor abdominal', 'dolor de cabeza', 'erupcion cutanea',
    'malestar general', 'dolor muscular', 'dificultad para respirar',
    'dolor en el pecho', 'nauseas', 'dolor de garganta', 'ojos enrojecidos',
    'hinchazon de las glandulas', 'secrecion nasal', 'perdida de peso',
    'cansancio extremo'
]

# Probabilidades ajustadas por enfermedad
probabilidades = {
    'Infección de oído': [0.8, 0.7, 0.3, 0.5, 0.6, 0.2, 0.1, 0.3, 0.9, 0.4, 0.1, 0.2, 0.1, 0.5, 0.2, 0.0, 0.0, 0.1, 0.0, 0.1, 0.8, 0.3, 0.0, 0.4],
    'Gripe': [0.3, 0.5, 0.9, 0.6, 0.7, 0.4, 0.8, 0.7, 0.2, 0.3, 0.2, 0.5, 0.3, 0.9, 0.7, 0.3, 0.1, 0.2, 0.6, 0.2, 0.4, 0.8, 0.1, 0.7],
    'Resfriado común': [0.2, 0.4, 0.5, 0.5, 0.6, 0.1, 0.7, 0.8, 0.2, 0.2, 0.1, 0.3, 0.1, 0.6, 0.3, 0.1, 0.0, 0.1, 0.5, 0.1, 0.3, 0.9, 0.0, 0.5],
    'Gastroenteritis': [0.2, 0.2, 0.4, 0.4, 0.7, 0.9, 0.3, 0.2, 0.2, 0.8, 0.9, 0.2, 0.1, 0.7, 0.4, 0.2, 0.1, 0.8, 0.1, 0.0, 0.1, 0.2, 0.7, 0.6],
    'Neumonía': [0.1, 0.3, 0.8, 0.6, 0.7, 0.3, 0.9, 0.6, 0.4, 0.4, 0.3, 0.4, 0.1, 0.8, 0.7, 0.9, 0.7, 0.4, 0.6, 0.3, 0.5, 0.5, 0.1, 0.8],
    'Migraña': [0.1, 0.2, 0.1, 0.5, 0.3, 0.1, 0.1, 0.0, 0.0, 0.2, 0.5, 0.9, 0.1, 0.6, 0.5, 0.0, 0.0, 0.4, 0.2, 0.1, 0.0, 0.1, 0.0, 0.6],
    'Dermatitis': [0.1, 0.3, 0.0, 0.2, 0.1, 0.1, 0.0, 0.0, 0.0, 0.1, 0.1, 0.0, 0.9, 0.2, 0.1, 0.0, 0.0, 0.1, 0.0, 0.2, 0.0, 0.0, 0.0, 0.1],
    'COVID-19': [0.3, 0.4, 0.8, 0.6, 0.7, 0.3, 0.9, 0.8, 0.2, 0.2, 0.3, 0.5, 0.2, 0.9, 0.8, 0.7, 0.5, 0.4, 0.6, 0.2, 0.3, 0.7, 0.2, 0.8],
    'Faringitis': [0.2, 0.2, 0.5, 0.5, 0.6, 0.1, 0.6, 0.5, 0.1, 0.2, 0.2, 0.3, 0.2, 0.7, 0.3, 0.2, 0.1, 0.3, 0.9, 0.1, 0.5, 0.6, 0.1, 0.5],
    'Conjuntivitis': [0.1, 0.3, 0.1, 0.2, 0.2, 0.0, 0.0, 0.1, 0.0, 0.0, 0.0, 0.0, 0.3, 0.2, 0.1, 0.0, 0.0, 0.0, 0.0, 0.9, 0.5, 0.1, 0.0, 0.3],
    'Mononucleosis': [0.3, 0.4, 0.4, 0.5, 0.5, 0.3, 0.5, 0.4, 0.2, 0.2, 0.2, 0.4, 0.3, 0.7, 0.6, 0.3, 0.2, 0.2, 0.5, 0.3, 0.6, 0.7, 0.1, 0.5],
    'Anemia': [0.0, 0.1, 0.1, 0.3, 0.4, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.2, 0.0, 0.6, 0.3, 0.1, 0.1, 0.3, 0.1, 0.0, 0.2, 0.1, 0.7, 0.8],
    'Depresión': [0.4, 0.5, 0.1, 0.7, 0.8, 0.2, 0.1, 0.1, 0.0, 0.0, 0.1, 0.2, 0.0, 0.9, 0.6, 0.0, 0.0, 0.4, 0.1, 0.0, 0.3, 0.2, 0.6, 0.9]
}

# Generar datos simulados
num_pacientes = 10000
datos = []

for _ in range(num_pacientes):
    enfermedad = np.random.choice(list(probabilidades.keys()))  # Seleccionar una enfermedad
    sintomas_paciente = [1 if np.random.rand() < prob else 0 for prob in probabilidades[enfermedad]]
    datos.append(sintomas_paciente + [enfermedad])

# Crear un DataFrame
columnas = sintomas + ['Diagnóstico']
df = pd.DataFrame(datos, columns=columnas)

# Guardar los datos en un archivo CSV
df.to_csv('datos_simulados_realistas.csv', index=False)


# Mostrar una muestra de los datos
print(df.head())
