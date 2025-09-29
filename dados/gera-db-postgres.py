import os
import pandas as pd
import psycopg2

def get_db_connection():
    """
    Conecta ao banco de dados usando a variável de ambiente DATABASE_URL.
    """
    print("Tentando conectar ao banco de dados...")
    try:
        db_url = os.environ.get("DATABASE_URL")
        if not db_url:
            raise ValueError("ERRO: A variável de ambiente DATABASE_URL não foi definida.")
        conn = psycopg2.connect(db_url)
        print("✅ Conexão bem-sucedida!")
        return conn
    except Exception as e:
        print(f"❌ ERRO CRÍTICO ao conectar ao banco de dados: {e}")
        return None

def criar_esquema(conn):
    """
    Deleta e recria as tabelas e views para garantir um estado limpo
    e espelhar a estrutura do script original.
    """
    print("\nIniciando a reconstrução completa do esquema do banco de dados...")
    try:
        with conn.cursor() as cur:
            # --- Deletar Estruturas Antigas ---
            print("Deletando views e tabelas antigas (se existirem)...")
            cur.execute("DROP VIEW IF EXISTS notas_medias_por_genero_por_idade;")
            cur.execute("DROP VIEW IF EXISTS notas_medias_por_filme_por_idade;")
            cur.execute("DROP VIEW IF EXISTS notas_medias_filmes;")
            cur.execute("DROP TABLE IF EXISTS avaliacoes CASCADE;")
            cur.execute("DROP TABLE IF EXISTS usuarios CASCADE;")
            cur.execute("DROP TABLE IF EXISTS filmes CASCADE;")

            # --- Criação das Tabelas (idêntica ao original) ---
            print("Criando novas tabelas...")
            cur.execute("""
                CREATE TABLE usuarios (
                    id SERIAL PRIMARY KEY,
                    nome_de_usuario VARCHAR(255) UNIQUE,
                    nome VARCHAR(255),
                    senha VARCHAR(255),
                    pais VARCHAR(255),
                    data_de_nascimento DATE
                );
            """)
            cur.execute("""
                CREATE TABLE filmes (
                    id SERIAL PRIMARY KEY,
                    titulo VARCHAR(255) UNIQUE,
                    genero VARCHAR(255),
                    ano INT
                );
            """)
            cur.execute("""
                CREATE TABLE avaliacoes (
                    id SERIAL PRIMARY KEY,
                    usuario_id INT REFERENCES usuarios(id) ON DELETE CASCADE,
                    filme_id INT REFERENCES filmes(id) ON DELETE CASCADE,
                    nota DECIMAL(3, 1)
                );
            """)
            print("✅ Tabelas criadas com a estrutura original.")

            # --- Criação das Views (idêntica ao original) ---
            print("Criando novas views...")
            cur.execute("""
                CREATE OR REPLACE VIEW notas_medias_filmes AS
                SELECT fi.*, ROUND(AVG(av.nota), 1) as nota_media
                FROM filmes as fi
                JOIN avaliacoes as av ON fi.id = av.filme_id
                GROUP BY fi.id;
            """)
            cur.execute("""
                CREATE OR REPLACE VIEW notas_medias_por_filme_por_idade AS
                WITH avaliacoes_com_detalhes AS (
                    SELECT
                        fi.titulo,
                        av.nota,
                        CASE
                            WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, us.data_de_nascimento)) <= 12 THEN 'criancas'
                            WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, us.data_de_nascimento)) BETWEEN 13 AND 17 THEN 'adolescentes'
                            WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, us.data_de_nascimento)) BETWEEN 18 AND 29 THEN 'jovens_adultos'
                            WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, us.data_de_nascimento)) BETWEEN 30 AND 49 THEN 'adultos'
                            ELSE '50_mais'
                        END AS faixa_etaria
                    FROM filmes AS fi
                    LEFT JOIN avaliacoes AS av ON fi.id = av.filme_id
                    LEFT JOIN usuarios AS us ON av.usuario_id = us.id
                )
                SELECT
                    titulo,
                    ROUND(AVG(CASE WHEN faixa_etaria = 'criancas' THEN nota END), 2) AS media_criancas_ate_12,
                    ROUND(AVG(CASE WHEN faixa_etaria = 'adolescentes' THEN nota END), 2) AS media_adolescentes_13_a_17,
                    ROUND(AVG(CASE WHEN faixa_etaria = 'jovens_adultos' THEN nota END), 2) AS media_jovens_adultos_18_a_29,
                    ROUND(AVG(CASE WHEN faixa_etaria = 'adultos' THEN nota END), 2) AS media_adultos_30_a_49,
                    ROUND(AVG(CASE WHEN faixa_etaria = '50_mais' THEN nota END), 2) AS media_50_mais,
                    ROUND(AVG(nota), 2) AS media_geral
                FROM avaliacoes_com_detalhes
                GROUP BY titulo;
            """)
            cur.execute("""
                CREATE OR REPLACE VIEW notas_medias_por_genero_por_idade AS
                WITH avaliacoes_por_genero_e_idade AS (
                    SELECT
                        fi.genero,
                        av.nota,
                        CASE
                            WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, us.data_de_nascimento)) <= 12 THEN 'criancas'
                            WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, us.data_de_nascimento)) BETWEEN 13 AND 17 THEN 'adolescentes'
                            WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, us.data_de_nascimento)) BETWEEN 18 AND 29 THEN 'jovens_adultos'
                            WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, us.data_de_nascimento)) BETWEEN 30 AND 49 THEN 'adultos'
                            ELSE '50_mais'
                        END AS faixa_etaria
                    FROM filmes AS fi
                    LEFT JOIN avaliacoes AS av ON fi.id = av.filme_id
                    LEFT JOIN usuarios AS us ON av.usuario_id = us.id
                    WHERE us.id IS NOT NULL
                )
                SELECT
                    genero,
                    ROUND(AVG(CASE WHEN faixa_etaria = 'criancas' THEN nota END), 2) AS media_criancas_ate_12,
                    ROUND(AVG(CASE WHEN faixa_etaria = 'adolescentes' THEN nota END), 2) AS media_adolescentes_13_a_17,
                    ROUND(AVG(CASE WHEN faixa_etaria = 'jovens_adultos' THEN nota END), 2) AS media_jovens_adultos_18_a_29,
                    ROUND(AVG(CASE WHEN faixa_etaria = 'adultos' THEN nota END), 2) AS media_adultos_30_a_49,
                    ROUND(AVG(CASE WHEN faixa_etaria = '50_mais' THEN nota END), 2) AS media_50_mais,
                    ROUND(AVG(nota), 2) AS media_geral_por_genero
                FROM avaliacoes_por_genero_e_idade
                GROUP BY genero;
            """)
            print("✅ Views recriadas com sucesso.")

        conn.commit()
        print("🎉 Esquema do banco de dados reconstruído com sucesso, seguindo a estrutura original.")
    except Exception as e:
        conn.rollback()
        print(f"❌ ERRO ao recriar o esquema: {e}")
        raise

def importar_dados(conn, df_filmes, df_usuarios, df_avaliacoes):
    """
    Importa os dados dos dataframes para as tabelas, de forma similar ao script original.
    """
    print("\nIniciando importação de dados...")
    try:
        with conn.cursor() as cur:
            # --- Limpeza dos dados antigos ---
            print("Limpando dados antigos das tabelas...")
            cur.execute("TRUNCATE TABLE avaliacoes RESTART IDENTITY;")
            cur.execute("TRUNCATE TABLE usuarios RESTART IDENTITY CASCADE;")
            cur.execute("TRUNCATE TABLE filmes RESTART IDENTITY CASCADE;")
            print("✅ Tabelas limpas.")

            # --- Importação de dados usando a lógica original com DataFrames ---
            print("Importando dados para 'usuarios'...")
            for index, row in df_usuarios.iterrows():
                cur.execute(
                    "INSERT INTO usuarios (nome_de_usuario, nome, senha, pais, data_de_nascimento) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (nome_de_usuario) DO NOTHING;",
                    (row['nome_de_usuario'], row['nome'], row['senha'], row['pais'], row['data_de_nascimento'])
                )
            print("Importando dados para 'filmes'...")
            for index, row in df_filmes.iterrows():
                cur.execute(
                    "INSERT INTO filmes (titulo, genero, ano) VALUES (%s, %s, %s) ON CONFLICT (titulo) DO NOTHING;",
                    (row['titulo'], row['genero'], row['ano'])
                )
            conn.commit()

            print("Mapeando IDs de usuários e filmes para importar avaliações...")
            cur.execute("SELECT id, nome_de_usuario FROM usuarios;")
            usuario_map = {row[1]: row[0] for row in cur.fetchall()}
            
            cur.execute("SELECT id, titulo FROM filmes;")
            filme_map = {row[1]: row[0] for row in cur.fetchall()}

            df_avaliacoes['usuario_id'] = df_avaliacoes['nome_de_usuario'].map(usuario_map)
            df_avaliacoes['filme_id'] = df_avaliacoes['titulo'].map(filme_map)

            print("Importando dados para 'avaliacoes'...")
            linhas_inseridas = 0
            for index, row in df_avaliacoes.iterrows():
                if pd.notnull(row['usuario_id']) and pd.notnull(row['filme_id']):
                    cur.execute(
                        "INSERT INTO avaliacoes (usuario_id, filme_id, nota) VALUES (%s, %s, %s);",
                        (int(row['usuario_id']), int(row['filme_id']), row['nota'])
                    )
                    linhas_inseridas += 1
            
            print(f"✅ {linhas_inseridas} avaliações importadas com sucesso.")
            
            conn.commit()
            print("\n🎉 Todas as importações foram concluídas e salvas no banco de dados.")

    except Exception as e:
        conn.rollback()
        print(f"❌ ERRO GERAL durante a importação: {e}")
    finally:
        if conn and not conn.closed:
            print("Fechando conexão com o banco de dados.")
            conn.close()

if __name__ == "__main__":
    conn = get_db_connection()
    if conn:
        try:
            # Carrega os arquivos CSV usando a lógica original
            print("\nCarregando arquivos CSV para a memória...")
            df_filmes = pd.read_csv('filmes.csv')
            df_usuarios = pd.read_csv('usuarios.csv')
            df_avaliacoes = pd.read_csv('avaliacoes.csv')
            print("✅ Arquivos CSV carregados.")

            criar_esquema(conn)
            importar_dados(conn, df_filmes, df_usuarios, df_avaliacoes)

        except FileNotFoundError as e:
            print(f"❌ ERRO: Arquivo CSV não encontrado. Verifique o caminho. Erro: {e}")
        except Exception as e:
            print(f"O processo foi interrompido devido a um erro: {e}")

