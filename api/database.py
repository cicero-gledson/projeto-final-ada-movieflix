import os
import psycopg2

def get_db_connection():
    """
    Cria uma conexão com o banco de dados usando a URL
    fornecida pela variável de ambiente 'DATABASE_URL'.
    """
    try:
        # Pega a URL completa do banco da variável de ambiente
        db_url = os.environ.get("DATABASE_URL")
        
        if not db_url:
            raise ValueError("A variável de ambiente DATABASE_URL não foi definida.")
            
        # Usa a URL para se conectar. Simples e flexível!
        conn = psycopg2.connect(db_url)
        return conn

    except Exception as e:
        print(f"ERRO: Não foi possível conectar ao banco de dados: {e}")
        return None