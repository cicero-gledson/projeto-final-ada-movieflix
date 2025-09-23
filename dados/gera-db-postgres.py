import pandas as pd
import psycopg2
from psycopg2 import sql
import os

def connect_to_db():
    """Conecta ao banco de dados PostgreSQL."""
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME", "MovieFlix-db"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "postgres"),
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5433")
        )
        print("Conexão com o banco de dados estabelecida com sucesso.")
        return conn
    except psycopg2.OperationalError as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

def create_tables(conn):
    """Cria as tabelas no banco de dados com chaves primárias e estrangeiras."""
    cur = conn.cursor()
    try:
        # Tabela de filmes com id como chave primária
        cur.execute("""
            CREATE TABLE IF NOT EXISTS filmes (
                id SERIAL PRIMARY KEY,
                titulo VARCHAR(255) UNIQUE,
                genero VARCHAR(255),
                ano INT
            );
        """)
        
        # Tabela de usuários com id como chave primária
        cur.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                nome_de_usuario VARCHAR(255) UNIQUE,
                nome VARCHAR(255),
                senha VARCHAR(255),
                pais VARCHAR(255),
                data_de_nascimento DATE
            );
        """)

        # Tabela de avaliações com chaves estrangeiras para filmes e usuários
        cur.execute("""
            CREATE TABLE IF NOT EXISTS avaliacoes (
                id SERIAL PRIMARY KEY,
                usuario_id INT REFERENCES usuarios(id),
                filme_id INT REFERENCES filmes(id),
                nota DECIMAL(3, 1)
            );
        """)
        
        
        # Tabela VIEW com filmes e a média geral da notas, ordenado da maior para menor nota
        cur.execute("""
                DROP VIEW IF EXISTS notas_medias_filmes;
                CREATE VIEW notas_medias_filmes AS
                SELECT fi.*, ROUND(AVG(av.nota), 1) as nota_media
                FROM filmes as fi
                JOIN avaliacoes as av ON fi.id = av.filme_id
                GROUP BY fi.id;
        """)        
        
        # Tabela VIEW com notas médias dos filmes por faixa etária
        cur.execute("""
                CREATE OR REPLACE VIEW notas_medias_por_filme_por_idade AS

                -- A CTE (cláusula WITH) é incluída na definição da VIEW
                WITH avaliacoes_com_detalhes AS (
                    SELECT
                        fi.titulo,
                        av.nota,
                        -- Lógica para calcular a faixa etária de cada avaliação
                        CASE
                            WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, us.data_de_nascimento)) <= 12 THEN 'criancas'
                            WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, us.data_de_nascimento)) BETWEEN 13 AND 17 THEN 'adolescentes'
                            WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, us.data_de_nascimento)) BETWEEN 18 AND 29 THEN 'jovens_adultos'
                            WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, us.data_de_nascimento)) BETWEEN 30 AND 49 THEN 'adultos'
                            ELSE '50_mais'
                        END AS faixa_etaria
                    FROM
                        filmes AS fi
                    LEFT JOIN
                        avaliacoes AS av ON fi.id = av.filme_id
                    LEFT JOIN
                        usuarios AS us ON av.usuario_id = us.id
                )
                -- A consulta principal que a VIEW irá armazenar e executar
                SELECT
                    titulo,
                    ROUND(AVG(CASE WHEN faixa_etaria = 'criancas' THEN nota END), 2) AS media_criancas_ate_12,
                    ROUND(AVG(CASE WHEN faixa_etaria = 'adolescentes' THEN nota END), 2) AS media_adolescentes_13_a_17,
                    ROUND(AVG(CASE WHEN faixa_etaria = 'jovens_adultos' THEN nota END), 2) AS media_jovens_adultos_18_a_29,
                    ROUND(AVG(CASE WHEN faixa_etaria = 'adultos' THEN nota END), 2) AS media_adultos_30_a_49,
                    ROUND(AVG(CASE WHEN faixa_etaria = '50_mais' THEN nota END), 2) AS media_50_mais,
                    ROUND(AVG(nota), 2) AS media_geral
                FROM
                    avaliacoes_com_detalhes
                GROUP BY
                    titulo;
        """)

        # Tabela VIEW com notas médias dos gêneros dos filmes por faixa etária
        cur.execute("""
                CREATE OR REPLACE VIEW notas_medias_por_genero_por_idade AS

                -- A CTE (cláusula WITH) faz parte da consulta da VIEW
                WITH avaliacoes_por_genero_e_idade AS (
                    SELECT
                        fi.genero,
                        av.nota,
                        -- Lógica para calcular a faixa etária
                        CASE
                            WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, us.data_de_nascimento)) <= 12 THEN 'criancas'
                            WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, us.data_de_nascimento)) BETWEEN 13 AND 17 THEN 'adolescentes'
                            WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, us.data_de_nascimento)) BETWEEN 18 AND 29 THEN 'jovens_adultos'
                            WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, us.data_de_nascimento)) BETWEEN 30 AND 49 THEN 'adultos'
                            ELSE '50_mais'
                        END AS faixa_etaria
                    FROM
                        filmes AS fi
                    LEFT JOIN
                        avaliacoes AS av ON fi.id = av.filme_id
                    LEFT JOIN
                        usuarios AS us ON av.usuario_id = us.id
                    WHERE us.id IS NOT NULL
                )
                -- A consulta principal (SELECT) que a VIEW irá armazenar
                SELECT
                    genero,
                    ROUND(AVG(CASE WHEN faixa_etaria = 'criancas' THEN nota END), 2) AS media_criancas_ate_12,
                    ROUND(AVG(CASE WHEN faixa_etaria = 'adolescentes' THEN nota END), 2) AS media_adolescentes_13_a_17,
                    ROUND(AVG(CASE WHEN faixa_etaria = 'jovens_adultos' THEN nota END), 2) AS media_jovens_adultos_18_a_29,
                    ROUND(AVG(CASE WHEN faixa_etaria = 'adultos' THEN nota END), 2) AS media_adultos_30_a_49,
                    ROUND(AVG(CASE WHEN faixa_etaria = '50_mais' THEN nota END), 2) AS media_50_mais,
                    ROUND(AVG(nota), 2) AS media_geral_por_genero
                FROM
                    avaliacoes_por_genero_e_idade
                GROUP BY
                    genero;
    """)




        conn.commit()
        print("Tabelas criadas ou já existem no banco de dados.")
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Erro ao criar tabelas: {e}")
    finally:
        cur.close()

def import_data(conn, df_filmes, df_usuarios, df_avaliacoes):
    """Importa os dados dos dataframes para as tabelas com depuração."""
    cur = conn.cursor()
    try:
        # Importa dados de usuarios
        for index, row in df_usuarios.iterrows():
            cur.execute(
                "INSERT INTO usuarios (nome_de_usuario, nome, senha, pais, data_de_nascimento) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (nome_de_usuario) DO NOTHING;",
                (row['nome_de_usuario'], row['nome'], row['senha'], row['pais'], row['data_de_nascimento'])
            )
        conn.commit()

        # Importa dados de filmes (Corrigido para usar os nomes de coluna do seu CSV)
        for index, row in df_filmes.iterrows():
            cur.execute(
                "INSERT INTO filmes (titulo, genero, ano) VALUES (%s, %s, %s) ON CONFLICT (titulo) DO NOTHING;",
                # Ajuste os nomes de coluna se forem diferentes nos seus arquivos
                (row['titulo'], row['genero'], row['ano'])
            )
        conn.commit()

        # Obtém os IDs dos filmes e usuários para a tabela de avaliações
        cur.execute("SELECT id, nome_de_usuario FROM usuarios;")
        usuario_map = {row[1]: row[0] for row in cur.fetchall()}
        
        cur.execute("SELECT id, titulo FROM filmes;")
        filme_map = {row[1]: row[0] for row in cur.fetchall()}

        # Mapeia as avaliações com os IDs correspondentes
        df_avaliacoes['usuario_id'] = df_avaliacoes['nome_de_usuario'].map(usuario_map)
        df_avaliacoes['filme_id'] = df_avaliacoes['titulo'].map(filme_map)

        # Contador para as linhas realmente inseridas
        linhas_inseridas = 0
        
        # Importa dados de avaliações usando os IDs
        for index, row in df_avaliacoes.iterrows():
            if pd.notnull(row['usuario_id']) and pd.notnull(row['filme_id']):
                cur.execute(
                    "INSERT INTO avaliacoes (usuario_id, filme_id, nota) VALUES (%s, %s, %s);",
                    (int(row['usuario_id']), int(row['filme_id']), row['nota'])
                )
                linhas_inseridas += 1
            else:
                # BLOCO DE DEPURAÇÃO: Mostra por que a linha foi pulada
                if pd.isnull(row['usuario_id']):
                    print(f"AVISO: Usuário '{row['nome_de_usuario']}' da avaliação não encontrado na tabela de usuários. Linha {index} pulada.")
                if pd.isnull(row['filme_id']):
                    print(f"AVISO: Filme '{row['titulo']}' da avaliação não encontrado na tabela de filmes. Linha {index} pulada.")

        conn.commit()
        # Imprime a contagem correta
        print(f"Dados importados para a tabela 'avaliacoes' com sucesso: {linhas_inseridas} linhas inseridas.")

    except psycopg2.Error as e:
        conn.rollback()
        print(f"Erro ao importar dados: {e}")
    finally:
        cur.close()
        
        
if __name__ == "__main__":
    conn = connect_to_db()
    if conn:
        try:
            # Carrega os arquivos CSV
            df_filmes = pd.read_csv('filmes.csv')
            df_usuarios = pd.read_csv('usuarios.csv')
            df_avaliacoes = pd.read_csv('avaliacoes.csv',)

            create_tables(conn)
            import_data(conn, df_filmes, df_usuarios, df_avaliacoes)

        except FileNotFoundError as e:
            print(f"Erro: Arquivo CSV não encontrado. Verifique se os arquivos estão na mesma pasta que o script. Erro: {e}")
        except Exception as e:
            print(f"Ocorreu um erro: {e}")
        finally:
            conn.close()