from fastapi import APIRouter, Request
from app.database import conectar
from app.services.whatsapp import enviar_whatsapp
import random
from datetime import datetime

router = APIRouter()

@router.post("/assinatura/enviar/{contrato_id}")
def enviar_codigo(contrato_id: int):

    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT inquilino_id FROM contratos WHERE id=%s", (contrato_id,))
    contrato = cursor.fetchone()

    if not contrato:
        return {"erro": "Contrato não encontrado"}

    codigo = str(random.randint(100000, 999999))

    cursor.execute("""
        INSERT INTO assinaturas (contrato_id, codigo, status)
        VALUES (%s, %s, 'pendente')
    """, (contrato_id, codigo))

    cursor.execute("SELECT telefone FROM inquilinos WHERE id=%s", (contrato["inquilino_id"],))
    tel = cursor.fetchone()

    enviar_whatsapp(tel["telefone"], f"Seu código: {codigo}")

    conn.commit()
    cursor.close()
    conn.close()

    return {"status": "Código enviado"}
    from fastapi import Request

@router.post("/assinatura/validar")
def validar_codigo(contrato_id: int, codigo: str, request: Request):

    try:
        conn = get_conn()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT * FROM assinaturas
            WHERE contrato_id=%s AND codigo_verificacao=%s AND status='pendente'
            ORDER BY id DESC LIMIT 1
        """, (contrato_id, codigo))

        assinatura = cursor.fetchone()

        if not assinatura:
            return {"erro": "Código inválido"}

        ip = request.client.host

        cursor.execute("""
            UPDATE assinaturas
            SET status='assinado',
                data_assinatura=NOW(),
                ip=%s
            WHERE id=%s
        """, (ip, assinatura["id"]))

        conn.commit()

        return {
            "status": "Contrato assinado com sucesso",
            "ip": ip
        }

    except Exception as e:
        return {"erro": str(e)}

    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass
