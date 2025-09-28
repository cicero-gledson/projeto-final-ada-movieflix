import os
import decimal
import psycopg2
from psycopg2 import sql
from flask import Flask, jsonify, request
from flask_cors import CORS


from database import get_db_connection
from filmes_logic import registrar_filme
from usuarios_logic import registrar_usuario
from avaliacoes_logic import registrar_avaliacao


app = Flask(__name__)
CORS(app) 


# --- NOVA ROTA DE HEALTH CHECK ---
@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Endpoint simples que não usa o banco de dados,
    apenas para verificar se a API está online.
    """
    return jsonify({"status": "ok"}), 200


# --- ROTAS DE CADASTRO (POST) ---

@app.route('/api/cadastrar-filme', methods=['POST'])
def rota_cadastrar_filme():
    conn = get_db_connection()
    if conn is None: return jsonify({"error": "Falha na conexão com o banco."}), 500
    try:
        response, status = registrar_filme(conn, request.get_json())
        return jsonify(response), status
    finally:
        if conn: conn.close()

@app.route('/api/cadastrar-usuario', methods=['POST'])
def rota_cadastrar_usuario():
    conn = get_db_connection()
    if conn is None: return jsonify({"error": "Falha na conexão com o banco."}), 500
    try:
        response, status = registrar_usuario(conn, request.get_json())
        return jsonify(response), status
    finally:
        if conn: conn.close()

@app.route('/api/cadastrar-avaliacao', methods=['POST'])
def rota_cadastrar_avaliacao():
    conn = get_db_connection()
    if conn is None: return jsonify({"error": "Falha na conexão com o banco."}), 500
    try:
        response, status = registrar_avaliacao(conn, request.get_json())
        return jsonify(response), status
    finally:
        if conn: conn.close()


# --- ROTAS DE CONSULTA (GET) ---

@app.route('/api/top-filmes-genero', methods=['GET'])
def top_filmes_por_genero():
    conn = get_db_connection()
    if conn is None: return jsonify({"error": "Falha na conexão com o banco."}), 500
    
    try:
        cur = conn.cursor()
        query = """
            WITH FilmesRanqueados AS (
                SELECT
                    f.genero,
                    f.titulo,
                    ROUND(AVG(a.nota), 1) as nota_media,
                    ROW_NUMBER() OVER (PARTITION BY f.genero ORDER BY AVG(a.nota) DESC) as ranking
                FROM
                    filmes AS f
                JOIN
                    avaliacoes AS a ON f.id = a.filme_id
                GROUP BY
                    f.genero, f.titulo
            )
            SELECT genero, titulo, nota_media, ranking
            FROM FilmesRanqueados
            WHERE ranking <= 10
            ORDER BY genero, nota_media DESC;
        """
        cur.execute(query)
        data = cur.fetchall()
        cur.close()

        result = {}
        for genero, titulo, nota, ranking in data:
            if genero not in result:
                result[genero] = []
            result[genero].append({'titulo': titulo, 'nota_media': float(nota), 'posicao_no_genero': int(ranking)})
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

@app.route('/api/cinco-populares', methods=['GET'])
def cinco_populares():
    conn = get_db_connection()
    if conn is None: return jsonify({"error": "Falha na conexão com o banco."}), 500

    try:
        cur = conn.cursor()
        query = """
            SELECT
                f.titulo, f.genero, f.ano, COUNT(a.filme_id) AS quantidade_avaliacoes
            FROM
                filmes AS f
            JOIN
                avaliacoes AS a ON f.id = a.filme_id
            GROUP BY
                f.id, f.titulo, f.genero, f.ano
            ORDER BY
                quantidade_avaliacoes DESC
            LIMIT 5;
        """
        cur.execute(query)
        # É preciso pegar os nomes das colunas para criar o dicionário depois
        column_names = [desc[0] for desc in cur.description]
        data = cur.fetchall()
        cur.close()

        result = [
            {'indice': indice, **dict(zip(column_names, row))} 
            for indice, row in enumerate(data, start=1)
        ]
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()


@app.route('/api/avaliacoes-pais', methods=['GET'])
def avaliacoes_por_pais():
    conn = get_db_connection()
    if conn is None: return jsonify({"error": "Falha na conexão com o banco."}), 500

    try:
        cur = conn.cursor()
        query = """
            SELECT u.pais, COUNT(a.id) AS total_avaliacoes
            FROM avaliacoes AS a
            JOIN usuarios AS u ON a.usuario_id = u.id
            GROUP BY u.pais
            ORDER BY total_avaliacoes DESC;
        """
        cur.execute(query)
        data = cur.fetchall()
        cur.close()
        
        result = [{'pais': pais, 'total_avaliacoes': count} for pais, count in data]
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()


@app.route('/api/notas-medias-faixa-etaria', methods=['GET'])
def notas_medias_faixa_etaria():
    conn = get_db_connection()
    if conn is None: return jsonify({"error": "Falha na conexão com o banco."}), 500

    try:
        cur = conn.cursor()
        query = "SELECT * FROM public.notas_medias_por_filme_por_idade ORDER BY titulo"
        cur.execute(query)
        
        column_names = [desc[0] for desc in cur.description]
        data = cur.fetchall()
        cur.close()
        
        result_list = []
        for row in data:
            movie_dict = dict(zip(column_names, row))
            for key, value in movie_dict.items():
                if isinstance(value, decimal.Decimal):
                    movie_dict[key] = float(value)
            result_list.append(movie_dict)
            
        return jsonify(result_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()


@app.route('/api/generos-melhor-avaliacao', methods=['GET'])
def generos_melhor_avaliacao():
    conn = get_db_connection()
    if conn is None: return jsonify({"error": "Falha na conexão com o banco."}), 500

    try:
        cur = conn.cursor()
        query = """
            SELECT fi.genero, AVG(av.nota)::numeric(10,2) AS nota_media 
            FROM filmes AS fi JOIN avaliacoes AS av 
            ON fi.id = av.filme_id 
            GROUP BY fi.genero 
            ORDER BY nota_media DESC;
        """
        cur.execute(query)
        data = cur.fetchall()
        cur.close()

        result = [{'genero': g, 'nota_media': float(n)} for g, n in data]
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

# --- ROTAS DE BUSCA (GET com parâmetros) ---

@app.route('/api/usuarios/buscar', methods=['GET'])
def buscar_usuario():
    nome_query = request.args.get('nome')
    if not nome_query:
        return jsonify({"error": "Parâmetro 'nome' é obrigatório."}), 400

    conn = get_db_connection()
    if conn is None: return jsonify({"error": "Falha na conexão com o banco."}), 500
    
    try:
        cur = conn.cursor()
        query = "SELECT id, nome_de_usuario, nome FROM usuarios WHERE nome_de_usuario ILIKE %s"
        cur.execute(query, (f'%{nome_query}%',))
        usuarios = cur.fetchall()
        cur.close()

        resultado = [{'id': u[0], 'nome_de_usuario': u[1], 'nome': u[2]} for u in usuarios]
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": "Erro interno ao buscar usuários."}), 500
    finally:
        if conn: conn.close()

@app.route('/api/filmes/buscar', methods=['GET'])
def buscar_filme():
    titulo_query = request.args.get('titulo')
    if not titulo_query:
        return jsonify({"error": "Parâmetro 'titulo' é obrigatório."}), 400

    conn = get_db_connection()
    if conn is None: return jsonify({"error": "Falha na conexão com o banco."}), 500
    
    try:
        cur = conn.cursor()
        query = "SELECT id, titulo, ano FROM filmes WHERE titulo ILIKE %s"
        cur.execute(query, (f'%{titulo_query}%',))
        filmes = cur.fetchall()
        cur.close()

        resultado = [{'id': f[0], 'titulo': f[1], 'ano': f[2]} for f in filmes]
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": "Erro interno ao buscar filmes."}), 500
    finally:
        if conn: conn.close()

# --- EXECUÇÃO DA APLICAÇÃO ---

if __name__ == '__main__':
    # Roda a API no container, escutando em todas as interfaces de rede
    app.run(host='0.0.0.0', port=5000)
