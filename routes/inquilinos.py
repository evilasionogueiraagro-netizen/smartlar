@router.post("/inquilinos")
def criar_inquilino(
    nome: str,
    cpf: str,
    rg: str,
    telefone: str,
    email: str,
    nacionalidade: str,
    estado_civil: str,
    profissao: str,
    data_nascimento: str,
    endereco_rua: str,
    endereco_numero: str,
    bairro: str,
    cidade: str,
    estado: str,
    cep: str,
    residencial_id: int
):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO inquilinos (
            nome, cpf, rg, telefone, email,
            nacionalidade, estado_civil, profissao, data_nascimento,
            endereco_rua, endereco_numero, bairro, cidade, estado, cep,
            residencial_id
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        nome, cpf, rg, telefone, email,
        nacionalidade, estado_civil, profissao, data_nascimento,
        endereco_rua, endereco_numero, bairro, cidade, estado, cep,
        residencial_id
    ))

    conn.commit()
    cursor.close()
    conn.close()

    return {"status": "inquilino completo criado"}
