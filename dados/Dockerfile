FROM python:3.10-slim

WORKDIR /app

RUN pip install --no-cache-dir pandas psycopg2-binary

COPY gera-db-postgres.py .

CMD ["python", "gera-db-postgres.py"]
