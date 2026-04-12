from fastapi import APIRouter
from app.db.database import get_conn

router = APIRouter()

@router.post("/imoveis")
def criar_imovel(numero: str, descricao: str, valor_aluguel: float, residencial_id: int):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO imoveis (numero, descricao, valor_aluguel, residencial_id)
        VALUES (%s, %s, %s, %s)
    """, (numero, descricao, valor_aluguel, residencial_id))

    conn.commit()
    cursor.close()
    conn.close()

    return {"status": "imóvel criado"}
