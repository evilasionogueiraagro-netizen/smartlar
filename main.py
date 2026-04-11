import os
from fastapi import FastAPI
import mysql.connector

app = FastAPI()

def conectar():
    url = os.getenv("DATABASE_URL")

    if not url:
        raise Exception("DATABASE_URL não encontrada")

    url = url.replace("mysql://", "")

    user_pass, host_db = url.split("@")
    user, password = user_pass.split(":")
    host_port, database = host_db.split("/")
    host, port = host_port.split(":")

    return mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        port=int(port)
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
