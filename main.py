import os
from fastapi import FastAPI
import mysql.connector

app = FastAPI()

def conectar():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT"))
    )

@app.get("/")
def home():
    return {"status": "SmartLar online 🚀"}

@app.get("/teste-banco")
def teste():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM usuarios")
    total = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return {"usuarios": total}
