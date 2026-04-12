from fastapi import APIRouter
from app.db.database import get_conn
from app.services.whatsapp import enviar_whatsapp
import random

router = APIRouter()

@router.post("/assinatura/enviar/{contrato_id}")
def enviar_codigo(contrato_id: int):

    try:
        conn = get_conn()
        cursor = conn.cursor(dictionary=True)

        # contrato
        cursor.execute("SELECT inquilino_id FROM contratos WHERE id=%s", (contrato_id,))
        contrato = cursor.fetchone()

        if not contrato:
            return {"erro": "Contrato não encontrado"}

        inquilino_id = contrato.get("inquilino_id")

        if not inquilino_id:
            return {"erro": "Contrato sem inquilino"}

        # telefone
        cursor.execute("SELECT telefone FROM inquilinos WHERE id=%s", (inquilino_id,))
        tel = cursor.fetchone()

        if not tel or not tel.get("telefone"):
            return {"erro": "Telefone não encontrado"}

        telefone = tel["telefone"]

        # código
        codigo = str(random.randint(100000, 999999))

        cursor.execute("""
            INSERT INTO assinaturas (contrato_id, codigo_verificacao, status)
            VALUES (%s, %s, 'pendente')
        """, (contrato_id, codigo))

        conn.commit()

        enviar_whatsapp(telefone, f"🔐 Código SmartLar: {codigo}")

        return {"status": "Código enviado"}

    except Exception as e:
        return {"erro_real": str(e)}

    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass
