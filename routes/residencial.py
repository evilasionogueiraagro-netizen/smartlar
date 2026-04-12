@router.post("/residenciais")
def criar_residencial(nome: str, cidade: str, usuario_id: int):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO residenciais (nome, cidade, usuario_id) VALUES (%s, %s, %s)",
        (nome, cidade, usuario_id)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return {"status": "residencial criado"}
