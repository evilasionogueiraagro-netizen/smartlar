import os
from fastapi import FastAPI
import mysql.connector

app = FastAPI()

import os
import mysql.connector
from urllib.parse import urlparse

def conectar():
    url = os.getenv("DATABASE_URL")

    parsed = urlparse(url)

    return mysql.connector.connect(
        host=parsed.hostname,
        user=parsed.username,
        password=parsed.password,
        database=parsed.path[1:],
        port=parsed.port
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
