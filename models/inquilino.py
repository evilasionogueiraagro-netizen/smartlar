from pydantic import BaseModel

class Inquilino(BaseModel):
    nome: str
    cpf: str
    telefone: str
    residencial_id: int
