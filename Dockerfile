FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY python/ ./python/
COPY resources/ ./resources/

RUN mkdir -p /data

WORKDIR /app/python

CMD ["python", "crator.py"]