from fastapi import FastAPI
from app.routes import assinatura
from app.db.database import get_conn

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
