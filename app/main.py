from fastapi import FastAPI
from app.routes import assinatura

app = FastAPI()

app.include_router(assinatura.router)

@app.get("/")
def home():
    return {"status": "SmartLar online 🚀"}
