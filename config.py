import os

class Settings:
    DB_HOST = os.getenv("MYSQLHOST")
    DB_USER = os.getenv("MYSQLUSER")
    DB_PASS = os.getenv("MYSQLPASSWORD")
    DB_NAME = os.getenv("MYSQLDATABASE")
    DB_PORT = int(os.getenv("MYSQLPORT", 3306))

    ZAPI_INSTANCE = os.getenv("ZAPI_INSTANCE")
    ZAPI_TOKEN = os.getenv("ZAPI_TOKEN")
    ZAPI_CLIENT = os.getenv("ZAPI_CLIENT")

    SECRET_KEY = os.getenv("SECRET_KEY", "super-secret")

settings = Settings()
