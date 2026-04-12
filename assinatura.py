from fastapi import APIRouter
from app.db.database import get_conn
from app.services.whatsapp import enviar_whatsapp
import random

router = APIRouter()

@router.post("/assinatura/enviar/{contrato_id}")
def enviar_codigo(contrato_id: int):

    conn = get_conn()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT inquilino_id FROM contratos WHERE id=%s", (contrato_id,))
    contrato = cursor.fetchone()

    if not contrato:
        return {"erro": "Contrato não encontrado"}

    codigo = str(random.randint(100000, 999999))

    cursor.execute(
        "INSERT INTO assinaturas (contrato_id, codigo_verificacao, status) VALUES (%s, %s, 'pendente')",
        (contrato_id, codigo)
    )

    cursor.execute("SELECT telefone FROM inquilinos WHERE id=%s", (contrato["inquilino_id"],))
    tel = cursor.fetchone()

    enviar_whatsapp(tel["telefone"], f"🔐 Código SmartLar: {codigo}")

    conn.commit()
    cursor.close()
    conn.close()

    return {"status": "Código enviado"}
