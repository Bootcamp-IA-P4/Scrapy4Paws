FROM python:3.11

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    python3-dev \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код API
COPY api/ /app/api/
COPY .env /app/

# Делаем скрипт запуска исполняемым
RUN chmod +x /app/api/start.sh

# Открываем порт
EXPOSE 8000

# Запускаем приложение через скрипт
CMD ["/app/api/start.sh"]