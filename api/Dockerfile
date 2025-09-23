# Dockerfile da api
FROM python:3.10-slim

WORKDIR /app

RUN pip install --no-cache-dir pandas psycopg2-binary flask flask-cors

COPY api.py .

CMD ["python", "api.py"]