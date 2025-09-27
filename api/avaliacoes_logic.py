def registrar_avaliacao(conn, dados):
    """Realiza a inserção de uma nova avaliação no banco de dados."""
    if not dados or not 'usuario_id' in dados or not 'filme_id' in dados or not 'nota' in dados:
        return {'message': 'Erro: Dados incompletos para a avaliação.'}, 400

    try:
        cur = conn.cursor()
        query = "INSERT INTO avaliacoes (usuario_id, filme_id, nota) VALUES (%s, %s, %s)"
        
        cur.execute(query, (
            dados['usuario_id'], 
            dados['filme_id'], 
            dados['nota']
        ))
        
        conn.commit()
        cur.close()
        return {'message': 'Avaliação registrada com sucesso!'}, 201
    except Exception as e:
        print(f"Erro ao inserir avaliação: {e}")
        return {'message': 'Erro interno no servidor ao registrar a avaliação.'}, 500