def registrar_filme(conn, dados):
    """Realiza a inserção de um novo filme no banco de dados."""
    if not dados or not 'titulo' in dados or not 'genero' in dados or not 'ano' in dados:
        return {'message': 'Erro: Dados incompletos para o filme.'}, 400

    titulo = dados['titulo']
    genero = dados['genero']
    ano = dados['ano']

    try:
        cur = conn.cursor()
        query = "INSERT INTO filmes (titulo, genero, ano) VALUES (%s, %s, %s)"
        cur.execute(query, (titulo, genero, ano))
        conn.commit()
        cur.close()
        return {'message': 'Filme cadastrado com sucesso!'}, 201
    except Exception as e:
        print(f"Erro ao inserir filme: {e}")
        return {'message': 'Erro interno no servidor ao cadastrar o filme.'}, 500