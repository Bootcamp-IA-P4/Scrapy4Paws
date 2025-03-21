FROM python:3.11-slim

WORKDIR /app

# Устанавливаем зависимости из корневого requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY frontend/ .

# Открываем порт для Streamlit
EXPOSE 8501

# Запускаем приложение
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"] 