import mysql.connector.pooling
from app.core.config import settings

pool = None

def get_conn():
    global pool

    if pool is None:
        pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="smartlar_pool",
            pool_size=5,
            host=settings.DB_HOST,
            user=settings.DB_USER,
            password=settings.DB_PASS,
            database=settings.DB_NAME,
            port=settings.DB_PORT
        )

    return pool.get_connection()
