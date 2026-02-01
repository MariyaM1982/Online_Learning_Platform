FROM python:3.11-slim

# Установка зависимостей
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY . .

# Экспорт порта
EXPOSE 8000

# Команда по умолчанию — можно переопределить в docker-compose
CMD ["gunicorn", "online_learning_platform.wsgi:application", "--bind", "0.0.0.0:8000"]