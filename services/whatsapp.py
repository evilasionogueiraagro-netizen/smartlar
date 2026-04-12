import requests
from app.config import ZAPI_INSTANCE, ZAPI_TOKEN, ZAPI_CLIENT

def enviar_whatsapp(numero, msg):
    url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE}/token/{ZAPI_TOKEN}/send-text"

    headers = {
        "Client-Token": ZAPI_CLIENT,
        "Content-Type": "application/json"
    }

    response = requests.post(url, json={
        "phone": numero,
        "message": msg
    }, headers=headers)

    print(response.text)
    return response.json()
