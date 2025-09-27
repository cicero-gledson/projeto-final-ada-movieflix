FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir pandas

COPY etl.py /app

CMD ["python", "etl.py"]