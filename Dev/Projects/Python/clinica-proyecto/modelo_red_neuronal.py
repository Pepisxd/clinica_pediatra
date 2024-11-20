import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib

# Cargar los datos simulados
df = pd.read_csv('datos_simulados_realistas.csv')

# Separar características (X) y etiquetas (y)
X = df.drop(columns=['Diagnóstico'])
y = df['Diagnóstico']

# Dividir los datos en entrenamiento y validación (80%, 20%)
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Entrenar el modelo de Red Neuronal
print("Entrenando Red Neuronal...")
mlp_clf = MLPClassifier(random_state=42, max_iter=500, hidden_layer_sizes=(50,))
mlp_clf.fit(X_train, y_train)

# Evaluar el modelo
print("Evaluando el modelo...")
y_val_pred = mlp_clf.predict(X_val)
accuracy = accuracy_score(y_val, y_val_pred)
print(f"Accuracy: {accuracy:.2f}")
print("Reporte de Clasificación:")
print(classification_report(y_val, y_val_pred))
 
# Guardar el modelo entrenado
joblib.dump(mlp_clf, 'modelo_red_neuronal.pkl')
print("Modelo guardado como 'modelo_red_neuronal.pkl'")
