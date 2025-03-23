FROM python:3.11

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    libpq-dev \
    postgresql \
    postgresql-contrib \
    postgresql-server-dev-all \
    gcc \
    python3-dev \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Копирование requirements.txt и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода приложения
COPY api/ .

# Делаем скрипт запуска исполняемым
RUN chmod +x start.sh

# Открываем порт
EXPOSE 8000

# Запускаем скрипт вместо прямого запуска uvicorn
CMD ["./start.sh"]