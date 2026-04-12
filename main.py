from fastapi import FastAPI
from app.routes import auth, assinatura

app = FastAPI(title="SmartLar API")

app.include_router(auth.router)
app.include_router(assinatura.router)

@app.get("/")
def root():
    return {"status": "SmartLar PRO rodando 🚀"}
