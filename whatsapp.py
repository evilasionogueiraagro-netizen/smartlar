import requests
from app.core.config import settings

def enviar_whatsapp(numero, mensagem):
    url = f"https://api.z-api.io/instances/{settings.ZAPI_INSTANCE}/token/{settings.ZAPI_TOKEN}/send-text"

    headers = {
        "Client-Token": settings.ZAPI_CLIENT,
        "Content-Type": "application/json"
    }

    response = requests.post(url, json={
        "phone": numero,
        "message": mensagem
    }, headers=headers)

    print("ZAPI:", response.text)
    return response.json()
