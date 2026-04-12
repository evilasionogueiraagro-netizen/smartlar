from fastapi import APIRouter
from app.db.database import get_conn

router = APIRouter()

@router.post("/inquilinos")
def criar_inquilino(nome: str, cpf: str, telefone: str, residencial_id: int):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO inquilinos (nome, cpf, telefone, residencial_id)
        VALUES (%s, %s, %s, %s)
    """, (nome, cpf, telefone, residencial_id))

    conn.commit()
    cursor.close()
    conn.close()

    return {"status": "inquilino criado"}
