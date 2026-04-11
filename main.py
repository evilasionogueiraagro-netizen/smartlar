from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from urllib.parse import urlparse
import os
import mysql.connector
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
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

@app.get("/contratos/html/{contrato_id}", response_class=HTMLResponse)
def gerar_html(contrato_id: int):

    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM contratos WHERE id=%s", (contrato_id,))
    contrato = cursor.fetchone()

    cursor.execute("SELECT * FROM inquilinos WHERE id=%s", (contrato["inquilino_id"],))
    inquilino = cursor.fetchone()

    cursor.execute("SELECT * FROM imoveis WHERE id=%s", (contrato["imovel_id"],))
    imovel = cursor.fetchone()

    cursor.execute("SELECT * FROM usuarios LIMIT 1")
    locador = cursor.fetchone()

    cursor.close()
    conn.close()

    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template("contrato.html")

    html = template.render({
        "nome_locador": locador["nome"],
        "cpf_locador": "00000000000",
        "nacionalidade_locador": "Brasileiro",
        "estado_civil_locador": "Solteiro",
        "profissao_locador": "Locador",
        "rg_locador": "0000000",
        "endereco_locador": "Endereço do locador",

        "nome_inquilino": inquilino["nome"],
        "cpf_inquilino": inquilino["cpf"],
        "nacionalidade_inquilino": "Brasileiro",
        "estado_civil_inquilino": "Solteiro",
        "documento_inquilino": "RG",
        "endereco_inquilino": "Endereço do inquilino",

        "endereco_imovel": imovel["descricao"],
        "numero_imovel": imovel["numero"],
        "bairro": "Centro",
        "cidade": "Manaus",
        "estado": "AM",

        "uc_energia": "123456",

        "valor_aluguel": contrato["valor"],
        "dia_vencimento": contrato["vencimento_dia"],

        "prazo": "12",
        "data_inicio": contrato["data_inicio"],
        "data_fim": contrato["data_fim"],

        "juros": "1",
        "multa": "2",
        "indice_reajuste": "IGP-M",
        "multa_contrato": "3 meses",
        "multa_rescisao": "2 meses",

        "data_assinatura": datetime.now().strftime("%d/%m/%Y")
    })

    return HTMLResponse(content=html)

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
from jinja2 import Environment, FileSystemLoader
import pdfkit

@app.get("/contratos/pdf/{contrato_id}")
def gerar_pdf(contrato_id: int):

    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    # contrato
    cursor.execute("SELECT * FROM contratos WHERE id=%s", (contrato_id,))
    contrato = cursor.fetchone()

    if not contrato:
        return {"erro": "Contrato não encontrado"}

    # inquilino
    cursor.execute("SELECT * FROM inquilinos WHERE id=%s", (contrato["inquilino_id"],))
    inquilino = cursor.fetchone()

    # imóvel
    cursor.execute("SELECT * FROM imoveis WHERE id=%s", (contrato["imovel_id"],))
    imovel = cursor.fetchone()

    # locador
    cursor.execute("SELECT * FROM usuarios LIMIT 1")
    locador = cursor.fetchone()

    cursor.close()
    conn.close()

    # template HTML
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template("contrato.html")

    html = template.render({
        "nome_locador": locador["nome"],
        "nome_inquilino": inquilino["nome"],
        "cpf_inquilino": inquilino["cpf"],
        "endereco_imovel": imovel["descricao"],
        "valor": contrato["valor"],
        "data_inicio": contrato["data_inicio"],
        "data_fim": contrato["data_fim"],
        "data_hoje": datetime.now().strftime("%d/%m/%Y")
    })

    caminho_pdf = f"contrato_{contrato_id}.pdf"

    config = pdfkit.configuration(
        wkhtmltopdf=os.getenv("WKHTMLTOPDF_PATH", "/usr/bin/wkhtmltopdf")
    )
    

    pdfkit.from_string(html, caminho_pdf, configuration=config)
    

    return FileResponse(
        caminho_pdf,
        media_type="application/pdf",
        filename="contrato.pdf"
    )
@app.get("/debug/inquilinos")
def listar_inquilinos():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM inquilinos")
    dados = cursor.fetchall()

    cursor.close()
    conn.close()

    return dados
@app.get("/debug/contratos")
def listar_contratos():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM contratos ORDER BY id DESC")
    dados = cursor.fetchall()

    cursor.close()
    conn.close()

    return dados
