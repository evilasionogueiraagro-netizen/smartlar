import mysql.connector.pooling
from app.core.config import settings

pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="smartlar_pool",
    pool_size=5,
    host=settings.DB_HOST,
    user=settings.DB_USER,
    password=settings.DB_PASS,
    database=settings.DB_NAME,
    port=settings.DB_PORT
)

def get_conn():
    return pool.get_connection()
