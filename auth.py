from fastapi import APIRouter
from app.core.security import criar_token

router = APIRouter(prefix="/auth")

@router.post("/login")
def login():
    return {"token": criar_token(1)}
