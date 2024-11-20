import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report, accuracy_score

# Cargar los datos simulados
df = pd.read_csv('datos_simulados_realistas.csv')

# Separar características (X) y etiquetas (y)
X = df.drop(columns=['Diagnóstico'])
y = df['Diagnóstico']

# Dividir los datos en entrenamiento, validación y prueba (80%, 10%, 10%)
X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp)

# **Entrenar Red Neuronal**
print("Entrenando Red Neuronal...")
mlp_clf = MLPClassifier(random_state=42, max_iter=500, hidden_layer_sizes=(50,))
mlp_clf.fit(X_train, y_train)

# Validar el modelo
y_val_pred = mlp_clf.predict(X_val)
accuracy = accuracy_score(y_val, y_val_pred)
report = classification_report(y_val, y_val_pred)

# Mostrar resultados
print(f"\nResultados de Red Neuronal:")
print(f"Accuracy en validación: {accuracy:.2f}")
print("Reporte de Clasificación:")
print(report)

# Evaluar en el conjunto de prueba
print("\nEvaluando en el conjunto de prueba...")
y_test_pred = mlp_clf.predict(X_test)
test_accuracy = accuracy_score(y_test, y_test_pred)
test_report = classification_report(y_test, y_test_pred)

print(f"Accuracy en prueba: {test_accuracy:.2f}")
print("Reporte de Clasificación en Prueba:")
print(test_report)
