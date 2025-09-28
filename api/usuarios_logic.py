
def registrar_usuario(conn, dados):
    """Realiza a inserção de um novo usuário no banco de dados."""
    # Lista de campos obrigatórios, conforme a imagem da tabela
    required_fields = ['nome_de_usuario', 'nome', 'senha', 'pais', 'data_de_nascimento'] # <-- ALTERADO
    
    if not dados or not all(field in dados for field in required_fields):
        return {'message': 'Erro: Dados incompletos para o usuário.'}, 400

    try:
        cur = conn.cursor()
        
        # Query SQL com as colunas corretas da tabela 'usuarios'
        query = """ 
            INSERT INTO usuarios (nome_de_usuario, nome, senha, pais, data_de_nascimento) 
            VALUES (%s, %s, %s, %s, %s)
        """ # <-- ALTERADO

        # Executa a query com os valores corretos
        cur.execute(query, (
            dados['nome_de_usuario'], 
            dados['nome'], 
            dados['senha'], # Lembre-se da nota de segurança sobre a senha!
            dados['pais'], 
            dados['data_de_nascimento'] # Ex: '2005-10-25'
        )) # <-- ALTERADO
        
        conn.commit()
        cur.close()
        return {'message': 'Usuário cadastrado com sucesso!'}, 201
    except Exception as e:
        print(f"Erro ao inserir usuário: {e}")
        return {'message': 'Erro interno no servidor ao cadastrar o usuário.'}, 500