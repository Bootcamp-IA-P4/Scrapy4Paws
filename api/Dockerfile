FROM python:3.11

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    python3-dev \
    netcat-traditional \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

# Копируем файлы зависимостей
COPY requirements.txt /app/
COPY .env /app/

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код API
COPY ./api /app/api

# Конвертируем конец строк и делаем скрипт запуска исполняемым
RUN dos2unix /app/api/start.sh && \
    chmod +x /app/api/start.sh

# Открываем порт
EXPOSE 8000

# Запускаем приложение через скрипт
CMD ["/bin/bash", "/app/api/start.sh"]