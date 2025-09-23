import os
import psycopg2
from psycopg2 import sql
from flask import Flask, jsonify, request
from flask_cors import CORS
import decimal

app = Flask(__name__)
# Permite requisições de outras origens (seu arquivo HTML)
CORS(app)

def get_db_connection():
    """Conecta ao banco de dados PostgreSQL usando variáveis de ambiente."""
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME", "MovieFlix-db"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "postgres"),
            host=os.getenv("DB_HOST", "movieflix"),
            port=os.getenv("DB_PORT", "5433")
        )
        print("Conexão com o banco de dados estabelecida com sucesso.")
        return conn
    except psycopg2.OperationalError as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

@app.route('/api/top-filmes-genero', methods=['GET'])
def top_filmes_por_genero():
    conn = get_db_connection()
    cur = conn.cursor()
    
    query = """
        -- Passo 1: Definir um Bloco (CTE) para ranquear os filmes
        WITH FilmesRanqueados AS (
            SELECT
                f.genero,
                f.titulo,
                ROUND(AVG(a.nota), 1) as nota_media,
                -- A "mágica" acontece aqui:
                -- ROW_NUMBER() cria um ranking para cada filme...
                -- ...dentro de cada 'genero' (PARTITION BY)...
                -- ...ordenado pela maior 'nota_media' (ORDER BY).
                ROW_NUMBER() OVER (PARTITION BY f.genero ORDER BY AVG(a.nota) DESC) as ranking
            FROM
                filmes AS f
            JOIN
                avaliacoes AS a ON f.id = a.filme_id
            GROUP BY
                f.genero, f.titulo
        )
        -- Passo 2: Selecionar do bloco CTE apenas os filmes com ranking de 1 a 10
        SELECT
            genero,
            titulo,
            nota_media,
            ranking
        FROM
            FilmesRanqueados
        WHERE
            ranking <= 10
        ORDER BY
            genero, nota_media DESC;
    """
    
    cur.execute(query)
    data = cur.fetchall()
    cur.close()
    conn.close()

    result = {}
    for genero, titulo, nota, ranking in data:
        if genero not in result:
            result[genero] = []
        result[genero].append({'titulo': titulo, 'nota_media': float(nota), 'posicao_no_genero': int(ranking)})
    
    return jsonify(result)

@app.route('/api/cinco-populares', methods=['GET'])
def cinco_populares():
    conn = get_db_connection()
    cur = conn.cursor()
    
    query = """
        select titulo, genero, ano, nota_media from notas_medias_filmes order by nota_media DESC limit 5
    """
    
    cur.execute(query)
    data = cur.fetchall()
    cur.close()
    conn.close()

    result = [
    {'indice': indice, 'titulo': titulo, 'genero': genero, 'ano': ano, "nota_media": nota_media} 
    for indice, (titulo, genero, ano, nota_media) in enumerate(data, start=1)
    ]   
    
    return jsonify(result)

@app.route('/api/avaliacoes-pais', methods=['GET'])
def avaliacoes_por_pais():
    conn = get_db_connection()
    cur = conn.cursor()

    query = """
    SELECT
        u.pais,
        COUNT(a.id) AS total_avaliacoes
    FROM
        avaliacoes AS a
    JOIN
        usuarios AS u ON a.usuario_id = u.id
    GROUP BY
        u.pais
    ORDER BY
        total_avaliacoes DESC;
    """

    cur.execute(query)
    data = cur.fetchall()
    cur.close()
    conn.close()
    
    result = [{'pais': pais, 'total_avaliacoes': count} for pais, count in data]
    return jsonify(result)

@app.route('/api/notas-medias-faixa-etaria', methods=['GET'])
def notas_medias_faixa_etaria():
    conn = get_db_connection()
    cur = conn.cursor()

    query = """
    SELECT * FROM public.notas_medias_por_filme_por_idade order by titulo
    """
    try:
        cur.execute(query)
        # Pega os nomes das colunas a partir do cursor
        column_names = [desc[0] for desc in cur.description]
        # Pega todos os registros
        data = cur.fetchall()
        
        # O resultado será uma lista de filmes
        result_list = []
        for row in data:
            # Cria um dicionário para cada filme, combinando nomes de colunas com os dados da linha
            movie_dict = dict(zip(column_names, row))
            
            # Converte valores do tipo Decimal para float, para que possam ser convertidos em JSON
            for key, value in movie_dict.items():
                if isinstance(value, decimal.Decimal):
                    movie_dict[key] = float(value)
            
            result_list.append(movie_dict)
            
        return jsonify(result_list)

    except Exception as e:
        # Retorna uma mensagem de erro em formato JSON
        return jsonify({"error": str(e)}), 500
        
    finally:
        # Garante que a conexão seja sempre fechada
        cur.close()
        conn.close()

@app.route('/api/generos-melhor-avaliacao', methods=['GET'])
def generos_melhor_avaliacao():
    conn = get_db_connection()
    cur = conn.cursor()
    
    query = """
        SELECT fi.genero, AVG(av.nota) AS nota_media 
        FROM filmes AS fi JOIN avaliacoes AS av 
        ON fi.id = av.filme_id 
        GROUP BY fi.genero 
        ORDER BY nota_media DESC    
    """
    
    cur.execute(query)
    data = cur.fetchall()
    cur.close()
    conn.close()

    result = [
    {'genero': genero, 'nota_media': nota_media} 
    for genero, nota_media in data
    ]   

    return jsonify(result)


# Adicione outras rotas de API aqui
# Exemplo: @app.route('/api/cinco-populares', methods=['GET'])

if __name__ == '__main__':
    # Roda a API no container
    app.run(host='0.0.0.0', port=5000)