from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import mysql.connector
import os
from datetime import datetime
import random

app = FastAPI()

# ================================
# CONEXÃO DATABASE (RAILWAY)
# ================================
def conectar():
    return mysql.connector.connect(
        host=os.getenv("MYSQLHOST"),
        user=os.getenv("MYSQLUSER"),
        password=os.getenv("MYSQLPASSWORD"),
        database=os.getenv("MYSQLDATABASE"),
        port=int(os.getenv("MYSQLPORT"))
    )

# ================================
# HOME
# ================================
@app.get("/")
def home():
    return {"status": "SmartLar online 🚀"}

# ================================
# USUÁRIOS
# ================================
class Usuario(BaseModel):
    nome: str
    telefone: str

@app.post("/usuarios")
def criar_usuario(usuario: Usuario):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO usuarios (nome, telefone) VALUES (%s, %s)",
        (usuario.nome, usuario.telefone)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return {"status": "usuário criado"}

# ================================
# RESIDENCIAIS
# ================================
class Residencial(BaseModel):
    nome: str
    cidade: str
    usuario_id: int

@app.post("/residenciais")
def criar_residencial(res: Residencial):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO residenciais (nome, cidade, usuario_id) VALUES (%s, %s, %s)",
        (res.nome, res.cidade, res.usuario_id)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return {"status": "residencial criado"}

# ================================
# INQUILINOS
# ================================
class Inquilino(BaseModel):
    nome: str
    cpf: str
    telefone: str
    residencial_id: int

@app.post("/inquilinos")
def criar_inquilino(inq: Inquilino):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO inquilinos (nome, cpf, telefone, residencial_id)
        VALUES (%s, %s, %s, %s)
    """, (inq.nome, inq.cpf, inq.telefone, inq.residencial_id))

    conn.commit()
    cursor.close()
    conn.close()

    return {"status": "inquilino criado"}

# ================================
# IMÓVEIS
# ================================
class Imovel(BaseModel):
    numero: str
    descricao: str
    valor_aluguel: float
    residencial_id: int

@app.post("/imoveis")
def criar_imovel(im: Imovel):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO imoveis (numero, descricao, valor_aluguel, residencial_id)
        VALUES (%s, %s, %s, %s)
    """, (im.numero, im.descricao, im.valor_aluguel, im.residencial_id))

    conn.commit()
    cursor.close()
    conn.close()

    return {"status": "imóvel criado"}

# ================================
# CONTRATOS
# ================================
class Contrato(BaseModel):
    inquilino_id: int
    imovel_id: int
    valor: float
    data_inicio: str
    data_fim: str
    vencimento_dia: int

@app.post("/contratos")
def criar_contrato(c: Contrato):
    conn = conectar()
    cursor = conn.cursor()

    # pega residencial automaticamente
    cursor.execute("SELECT residencial_id FROM inquilinos WHERE id=%s", (c.inquilino_id,))
    res = cursor.fetchone()

    if not res:
        raise HTTPException(404, "Inquilino não encontrado")

    residencial_id = res[0]

    cursor.execute("""
        INSERT INTO contratos 
        (residencial_id, inquilino_id, imovel_id, valor, data_inicio, data_fim, vencimento_dia)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (residencial_id, c.inquilino_id, c.imovel_id, c.valor, c.data_inicio, c.data_fim, c.vencimento_dia))

    conn.commit()
    cursor.close()
    conn.close()

    return {"status": "contrato criado"}

# ================================
# GERAR CÓDIGO ASSINATURA
# ================================
@app.post("/assinatura/enviar")
def enviar_codigo(inquilino_id: int):
    codigo = str(random.randint(100000, 999999))

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO assinaturas (inquilino_id, codigo, status)
        VALUES (%s, %s, 'pendente')
    """, (inquilino_id, codigo))

    conn.commit()
    cursor.close()
    conn.close()

    return {"codigo": codigo}  # depois troca por WhatsApp

# ================================
# VALIDAR ASSINATURA
# ================================
@app.post("/assinatura/validar")
def validar(inquilino_id: int, codigo: str, request: Request):

    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM assinaturas 
        WHERE inquilino_id=%s AND codigo=%s AND status='pendente'
        ORDER BY id DESC LIMIT 1
    """, (inquilino_id, codigo))

    assinatura = cursor.fetchone()

    if not assinatura:
        raise HTTPException(400, "Código inválido")

    cursor.execute("""
        UPDATE assinaturas
        SET status='assinado', data_assinatura=%s, ip=%s
        WHERE id=%s
    """, (datetime.now(), request.client.host, assinatura["id"]))

    conn.commit()
    cursor.close()
    conn.close()

    return {"status": "assinado com sucesso"}

# ================================
# TESTE BANCO
# ================================
@app.get("/teste-banco")
def teste():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM usuarios")
    total = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return {"usuarios": total}
@app.get("/debug-db")
def debug():
    import os
    return {
        "host": os.getenv("MYSQLHOST"),
        "user": os.getenv("MYSQLUSER"),
        "db": os.getenv("MYSQLDATABASE"),
        "port": os.getenv("MYSQLPORT")
    }
