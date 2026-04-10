import os
from fastapi import FastAPI
import mysql.connector
from urllib.parse import urlparse

app = FastAPI()

# =========================================
# CONEXÃO COM BANCO (RAILWAY - DATABASE_URL)
# =========================================
def conectar():
    try:
        url = os.getenv("DATABASE_URL")

        if not url:
            raise Exception("DATABASE_URL não definida")

        parsed = urlparse(url)

        return mysql.connector.connect(
            host=parsed.hostname,
            user=parsed.username,
            password=parsed.password,
            database=parsed.path.replace("/", ""),
            port=parsed.port or 3306
        )

    except Exception as e:
        print("ERRO CONEXÃO:", e)
        raise e


# =========================================
# HOME
# =========================================
@app.get("/")
def home():
    return {"status": "SmartLar online 🚀"}


# =========================================
# TESTE BANCO
# =========================================
@app.get("/teste-banco")
def teste_banco():
    try:
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM usuarios")
        total = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        return {"usuarios": total}

    except Exception as e:
        return {"erro": str(e)}


# =========================================
# CRIAR USUÁRIO
# =========================================
@app.post("/usuarios")
def criar_usuario(nome: str, telefone: str):
    try:
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO usuarios (nome, telefone) VALUES (%s, %s)",
            (nome, telefone)
        )

        conn.commit()

        cursor.close()
        conn.close()

        return {"msg": "Usuário criado com sucesso"}

    except Exception as e:
        return {"erro": str(e)}
