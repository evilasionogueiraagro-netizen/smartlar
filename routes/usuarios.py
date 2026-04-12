from fastapi import APIRouter
from app.db.database import get_conn

router = APIRouter()

@router.post("/usuarios")
def criar_usuario(nome: str, telefone: str):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO usuarios (nome, telefone) VALUES (%s, %s)",
        (nome, telefone)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return {"status": "usuário criado"}
