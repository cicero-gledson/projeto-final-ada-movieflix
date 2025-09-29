FROM python:3.10-slim

WORKDIR /app

RUN pip install --no-cache-dir pandas psycopg2-binary

# Copia apenas o script Python para o contentor
COPY gera-db-postgres.py .

# Copia todos os ficheiros que terminam em .csv para o contentor
COPY *.csv ./

CMD ["python", "gera-db-postgres.py"]