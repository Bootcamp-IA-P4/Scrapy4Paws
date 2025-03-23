#!/bin/bash

# Ждем, пока база данных будет готова
echo "Waiting for database to be ready..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "Database is ready!"

# Запускаем скрапер из корневой директории
echo "Starting scraper..."
cd /app && python -m scripts.run_scraper

# После успешного скрапинга запускаем FastAPI
echo "Starting FastAPI application..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload 