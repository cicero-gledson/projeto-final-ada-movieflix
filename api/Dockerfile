# Dockerfile da api
FROM python:3.10-slim

WORKDIR /app

RUN pip install --no-cache-dir pandas psycopg2-binary flask flask-cors

COPY api.py .
COPY avaliacoes_logic.py .
COPY database.py .
COPY filmes_logic.py .
COPY usuarios_logic.py .

CMD ["python", "api.py"]