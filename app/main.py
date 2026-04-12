from fastapi import FastAPI
from fastapi import APIRouter
from app.db.database import get_conn

from app.routes import assinatura

from app.routes import usuarios
from app.routes import inquilinos
from app.routes import imoveis
from app.routes import contratos
from app.routes import assinatura
from app.routes import residencial

router = APIRouter()


app.include_router(usuarios.router)
app.include_router(inquilinos.router)
app.include_router(imoveis.router)
app.include_router(contratos.router)
app.include_router(assinatura.router)

app = FastAPI()

app.include_router(assinatura.router)

@app.get("/")
def home():
    return {"status": "SmartLar online 🚀"}

# 🔥 DEBUG BANCO
@app.get("/debug/contratos")
def listar():
    try:
        conn = get_conn()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM contratos")
        dados = cursor.fetchall()

        return dados

    except Exception as e:
        return {"erro_real": str(e)}

    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass
@app.get("/debug/env")
def debug_env():
    import os
    return {
        "host": os.getenv("MYSQLHOST"),
    }
