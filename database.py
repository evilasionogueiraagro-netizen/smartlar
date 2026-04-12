import mysql.connector

def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Ev@91018891",
        database="smartlar"
    )
