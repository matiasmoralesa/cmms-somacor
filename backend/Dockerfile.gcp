FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y postgresql-client libpq-dev gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn psycopg2-binary

COPY . .

RUN mkdir -p staticfiles

ENV PORT=8080
EXPOSE 8080

CMD exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 0