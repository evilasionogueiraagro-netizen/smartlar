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

    # contrato
    cursor.execute("SELECT * FROM contratos WHERE id=%s", (contrato_id,))
    contrato = cursor.fetchone()

    # inquilino
    cursor.execute("SELECT * FROM inquilinos WHERE id=%s", (contrato["inquilino_id"],))
    inquilino = cursor.fetchone()

    # imóvel
    cursor.execute("SELECT * FROM imoveis WHERE id=%s", (contrato["imovel_id"],))
    imovel = cursor.fetchone()

    # locador
    cursor.execute("SELECT * FROM usuarios LIMIT 1")
    locador = cursor.fetchone()

    # assinatura (AGORA COM IP ✅)
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

    # template
    from jinja2 import Environment, FileSystemLoader
    env = Environment(loader=FileSystemLoader('.'), auto_reload=True)
    env.cache = {}

    # 🔥 QR CODE EM BASE64 (FUNCIONA NO HTML)
    import qrcode
    import base64
    from io import BytesIO

    url_validacao = f"https://smartlar-production.up.railway.app/contratos/visualizar/{contrato_id}"

    qr = qrcode.make(url_validacao)

    buffer = BytesIO()
    qr.save(buffer, format="PNG")

    qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    template = env.get_template("contrato.html")

    html = template.render({

        # LOCADOR
        "nome_locador": locador["nome"],
        "nacionalidade_locador": "Brasileiro",
        "estado_civil_locador": "Solteiro",
        "profissao_locador": "Locador",
        "rg_locador": "0000000",
        "cpf_locador": "00000000000",
        "endereco_locador": "Endereço do locador",

        # INQUILINO
        "nome_inquilino": inquilino["nome"],
        "cpf_inquilino": inquilino["cpf"],
        "nacionalidade_inquilino": "Brasileiro",
        "estado_civil_inquilino": "Solteiro",
        "documento_inquilino": "RG",
        "endereco_inquilino": "Endereço do inquilino",

        # IMÓVEL
        "endereco_imovel": imovel["descricao"],
        "numero_imovel": imovel["numero"],
        "bairro": "Centro",
        "cidade": "Manaus",
        "estado": "AM",
        "uc_energia": "123456",

        # CONTRATO
        "valor_aluguel": contrato["valor"],
        "dia_vencimento": contrato["vencimento_dia"],
        "prazo": "12",
        "data_inicio": contrato["data_inicio"],
        "data_fim": contrato["data_fim"],

        # TAXAS
        "juros": "1",
        "multa": "2",
        "indice_reajuste": "IGP-M",
        "multa_contrato": "3",
        "multa_rescisao": "2",

        # ASSINATURA
        "status_assinatura": status,
        "data_assinatura": data_assinatura,
        "ip_assinatura": ip_assinatura,

        # QR CODE
        "qr_code": qr_base64
    })

    return HTMLResponse(content=html)

# ================================
# ENVIAR CONTRATO
# ================================
import random
from datetime import datetime

from fastapi import Request
import random
from datetime import datetime

@app.post("/assinatura/enviar/{contrato_id}")
def enviar_codigo(contrato_id: int):

    import random
    from datetime import datetime

    codigo = str(random.randint(100000, 999999))

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT inquilino_id FROM contratos WHERE id=%s", (contrato_id,))
    contrato = cursor.fetchone()

    # 🔥 CORREÇÃO AQUI
    if not contrato:
        cursor.close()
        conn.close()
        return {"erro": "Contrato não encontrado"}

    inquilino_id = contrato[0]

    cursor.execute("""
        INSERT INTO assinaturas (contrato_id, inquilino_id, codigo, criado_em)
        VALUES (%s, %s, %s, %s)
    """, (contrato_id, inquilino_id, codigo, datetime.now()))

    conn.commit()
    cursor.close()
    conn.close()

    return {
        "msg": "Código gerado",
        "codigo": codigo
    }

# ================================
# VALIDAR ASSINATURA
# ================================
from fastapi import Request

@app.post("/assinatura/validar")
def validar_assinatura(contrato_id: int, codigo: str, request: Request):

    from datetime import datetime

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

    # 🔥 AQUI ESTÁ O IP
    ip = request.client.host

    cursor.execute("""
        UPDATE assinaturas
        SET status='assinado',
            data_assinatura=%s,
            ip=%s
        WHERE id=%s
    """, (datetime.now(), ip, assinatura["id"]))

    conn.commit()
    cursor.close()
    conn.close()

    return {"status": "Contrato assinado com sucesso"}
@app.get("/validar/{contrato_id}")
def validar_contrato(contrato_id: int):

    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT a.status, a.data_assinatura, a.ip, i.nome
        FROM assinaturas a
        JOIN inquilinos i ON a.inquilino_id = i.id
        WHERE a.contrato_id=%s
        ORDER BY a.id DESC LIMIT 1
    """, (contrato_id,))
    
    cursor.execute("""
    UPDATE contratos 
    SET html_contrato=%s 
    WHERE id=%s
    """, (html, contrato_id))
    assinatura = cursor.fetchone()

    cursor.close()
    conn.close()

    if not assinatura:
        return {"status": "Contrato não encontrado"}

    return {
        "contrato": contrato_id,
        "inquilino": assinatura["nome"],
        "status": assinatura["status"],
        "data": assinatura["data_assinatura"],
        "ip": assinatura["ip"]
    }
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
from fastapi.responses import HTMLResponse

@app.get("/contratos/visualizar/{contrato_id}", response_class=HTMLResponse)
def visualizar_contrato(contrato_id: int):

    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT html_contrato FROM contratos WHERE id=%s", (contrato_id,))
    contrato = cursor.fetchone()

    cursor.close()
    conn.close()

    if not contrato or not contrato["html_contrato"]:
        return "Contrato não encontrado"

    return HTMLResponse(content=contrato["html_contrato"])
