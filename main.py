from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import os
import mysql.connector
from datetime import datetime
import random
import hashlib

app = FastAPI()

# ================================
# CONEXÃO DATABASE
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
# GERAR CONTRATO (COM CONGELAMENTO)
# ================================
from jinja2 import Environment, FileSystemLoader

@app.get("/contratos/html/{contrato_id}", response_class=HTMLResponse)
def gerar_html(contrato_id: int):

    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    # 🔒 contrato congelado
    cursor.execute("SELECT status, html_contrato FROM contratos WHERE id=%s", (contrato_id,))
    c = cursor.fetchone()

    if c and c["status"] == "assinado" and c["html_contrato"]:
        cursor.close()
        conn.close()
        return HTMLResponse(content=c["html_contrato"])

    cursor.execute("SELECT * FROM contratos WHERE id=%s", (contrato_id,))
    contrato = cursor.fetchone()

    cursor.execute("SELECT * FROM inquilinos WHERE id=%s", (contrato["inquilino_id"],))
    inquilino = cursor.fetchone()

    cursor.execute("SELECT * FROM imoveis WHERE id=%s", (contrato["imovel_id"],))
    imovel = cursor.fetchone()

    cursor.execute("SELECT * FROM usuarios LIMIT 1")
    locador = cursor.fetchone()

    cursor.execute("""
        SELECT status, data_assinatura, ip 
        FROM assinaturas
        WHERE contrato_id=%s
        ORDER BY id DESC LIMIT 1
    """, (contrato_id,))
    
    assinatura = cursor.fetchone()

    status = assinatura["status"] if assinatura else "pendente"
    data_assinatura = assinatura["data_assinatura"] if assinatura else "-"
    ip_assinatura = assinatura["ip"] if assinatura and assinatura["ip"] else "-"

    cursor.close()
    conn.close()

    env = Environment(loader=FileSystemLoader('.'), auto_reload=True)
    env.cache = {}

    import qrcode, base64
    from io import BytesIO

    url = f"https://smartlar-production.up.railway.app/contratos/visualizar/{contrato_id}"

    qr = qrcode.make(url)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    qr_code = base64.b64encode(buffer.getvalue()).decode()

    template = env.get_template("contrato.html")

    html = template.render({
        "nome_locador": locador["nome"],
        "nome_inquilino": inquilino["nome"],
        "cpf_inquilino": inquilino["cpf"],
        "endereco_imovel": imovel["descricao"],
        "valor_aluguel": contrato["valor"],
        "data_inicio": contrato["data_inicio"],
        "data_fim": contrato["data_fim"],
        "status_assinatura": status,
        "data_assinatura": data_assinatura,
        "ip_assinatura": ip_assinatura,
        "qr_code": qr_code
    })

    return HTMLResponse(content=html)

# ================================
# ENVIAR CÓDIGO (BLOQUEADO SE ASSINADO)
# ================================
@app.post("/assinatura/enviar/{contrato_id}")
def enviar_codigo(contrato_id: int):

    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT status FROM contratos WHERE id=%s", (contrato_id,))
    c = cursor.fetchone()

    if c and c["status"] == "assinado":
        return {"erro": "Contrato já assinado"}

    codigo = str(random.randint(100000, 999999))

    cursor.execute("SELECT inquilino_id FROM contratos WHERE id=%s", (contrato_id,))
    contrato = cursor.fetchone()

    cursor.execute("""
        INSERT INTO assinaturas (contrato_id, inquilino_id, codigo, criado_em)
        VALUES (%s, %s, %s, %s)
    """, (contrato_id, contrato["inquilino_id"], codigo, datetime.now()))

    conn.commit()
    cursor.close()
    conn.close()

    return {"codigo": codigo}

# ================================
# VALIDAR ASSINATURA + HASH + CONGELAR
# ================================
@app.post("/assinatura/validar")
def validar(contrato_id: int, codigo: str, request: Request):

    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM assinaturas
        WHERE contrato_id=%s AND codigo=%s AND status='pendente'
        ORDER BY id DESC LIMIT 1
    """, (contrato_id, codigo))

    assinatura = cursor.fetchone()

    if not assinatura:
        return {"erro": "Código inválido"}

    ip = request.client.host

    cursor.execute("""
        UPDATE assinaturas
        SET status='assinado', data_assinatura=%s, ip=%s
        WHERE id=%s
    """, (datetime.now(), ip, assinatura["id"]))

    html_final = gerar_html(contrato_id).body.decode()
    hash_contrato = hashlib.sha256(html_final.encode()).hexdigest()

    cursor.execute("""
        UPDATE contratos
        SET html_contrato=%s, status='assinado', hash_contrato=%s
        WHERE id=%s
    """, (html_final, hash_contrato, contrato_id))

    conn.commit()
    cursor.close()
    conn.close()

    return {"status": "assinado", "hash": hash_contrato}

# ================================
# VISUALIZAR CONTRATO + LOG
# ================================
@app.get("/contratos/visualizar/{contrato_id}", response_class=HTMLResponse)
def visualizar(contrato_id: int, request: Request):

    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT inquilino_id FROM contratos WHERE id=%s", (contrato_id,))
    c = cursor.fetchone()

    if not c:
        return "Contrato não encontrado"

    cursor.execute("""
        INSERT INTO logs_acesso (dispositivo_id, inquilino_id, data, tipo, sucesso)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        request.client.host,
        c["inquilino_id"],
        datetime.now(),
        "visualizacao",
        1
    ))

    cursor.execute("SELECT html_contrato FROM contratos WHERE id=%s", (contrato_id,))
    contrato = cursor.fetchone()

    conn.commit()
    cursor.close()
    conn.close()

    if not contrato or not contrato["html_contrato"]:
        return "Contrato não encontrado"

    return HTMLResponse(content=contrato["html_contrato"])
