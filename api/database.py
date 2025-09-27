import os
import psycopg2

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
        return conn
    except psycopg2.OperationalError as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None