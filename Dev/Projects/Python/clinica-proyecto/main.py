from login import Login
from register import Register

def main():
    # Solo carga la pantalla de Login inicialmente
    login = Login()
    login.mainloop()  # Mantén el loop principal aquí para que solo una ventana esté activa

if __name__ == "__main__":
    main()
"""
|          1 | Admin    | Sistema        | admin@hospital.com            | admin123                                                     |   1 |
|          2 | Dr. Juan | García López   | juan.pediatra@hospital.com    | medico123                                                    |   2 |
|          3 | María    | Rodríguez      | maria.secretaria@hospital.com | secre123                                                     |   3 |              
"""