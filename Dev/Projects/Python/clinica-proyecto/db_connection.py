import mysql.connector

def conexion_db():
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user= "root",
            password="",
            database="pediatria"
        )
        return conexion
    except mysql.connector.Error as e:
        print(e)
        return None
