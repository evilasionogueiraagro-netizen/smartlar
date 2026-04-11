import os
import mysql.connector

def conectar():
    return mysql.connector.connect(
        host=os.getenv("MYSQLHOST"),
        user=os.getenv("MYSQLUSER"),
        password=os.getenv("MYSQLPASSWORD"),
        database=os.getenv("MYSQLDATABASE"),
        port=int(os.getenv("MYSQLPORT"))
    )
@app.get("/")
def home():
    return {"status": "SmartLar online 🚀"}

@app.get("/teste-banco")
def teste():
    try:
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM usuarios")
        total = cursor.fetchone()[0]

        return {"usuarios": total}

    except Exception as e:
        return {"erro": str(e)}
