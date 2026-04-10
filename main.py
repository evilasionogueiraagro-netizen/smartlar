import os
from fastapi import FastAPI
import mysql.connector

app = FastAPI()

# =========================================
# CONEXÃO BANCO (VERSÃO ROBUSTA)
# =========================================
def conectar():
    try:
        url = os.getenv("DATABASE_URL")

        if not url:
            raise Exception("DATABASE_URL não encontrada")

        # DEBUG
        print("DATABASE_URL:", url)

        # Exemplo:
        # mysql://user:pass@host:port/database

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

    except Exception as e:
        print("ERRO CONEXÃO:", str(e))
        raise e


# =========================================
# HOME
# =========================================
@app.get("/")
def home():
    return {"status": "SmartLar online 🚀"}


# =========================================
# TESTE BANCO (COM DEBUG)
# =========================================
@app.get("/teste-banco")
def teste_banco():
    try:
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("SHOW TABLES")
        tabelas = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) FROM usuarios")
        total = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        return {
            "status": "ok",
            "tabelas": tabelas,
            "usuarios": total
        }

    except Exception as e:
        return {
            "erro": str(e)
        }
