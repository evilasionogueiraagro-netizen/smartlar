from fastapi import FastAPI

from app.routes import (
    usuarios,
    residenciais,
    inquilinos,
    imoveis,
    contratos,
    assinatura
)

app = FastAPI()

app.include_router(usuarios.router)
app.include_router(residenciais.router)
app.include_router(inquilinos.router)
app.include_router(imoveis.router)
app.include_router(contratos.router)
app.include_router(assinatura.router)

@app.get("/")
def home():
    return {"status": "SmartLar online 🚀"}
