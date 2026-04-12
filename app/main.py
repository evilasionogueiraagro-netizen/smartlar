from fastapi import FastAPI
from app.routes import assinatura

app = FastAPI()

app.include_router(assinatura.router)

@app.get("/")
def home():
    return {"status": "SmartLar online 🚀"}
@app.get("/debug/contratos")
def listar():
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM contratos")
    dados = cursor.fetchall()

    cursor.close()
    conn.close()

    return dados
