from datetime import datetime, timedelta
import jwt
from app.core.config import settings

def criar_token(user_id: int):
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(days=1)
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
