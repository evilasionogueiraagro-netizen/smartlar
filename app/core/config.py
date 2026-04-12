import os

class Settings:
    DB_HOST = os.getenv("mysql.railway.internal")
    DB_USER = os.getenv("root")
    DB_PASS = os.getenv("SVYTByDzVrvqBsrfkEaMpyXnUFzpkzKx")
    DB_NAME = os.getenv("railway")
    DB_PORT = int(os.getenv("${{MySQL.MYSQLPORT}}", 44842))

    ZAPI_INSTANCE = os.getenv("3F1847ADAFDE21F3ABE79ED390C0144C")
    ZAPI_TOKEN = os.getenv("C619984FEC04E144B8F2E9C2")
    ZAPI_CLIENT = os.getenv("F197903852ddf43358ce450b7eea92399S")

settings = Settings()
