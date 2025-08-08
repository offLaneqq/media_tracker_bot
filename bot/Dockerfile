# bot/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Скопіювати файл залежностей і встановити
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Скопіювати код бота
COPY bot.py .
COPY handlers ./handlers

# Запуск бота
CMD ["python", "bot.py"]
