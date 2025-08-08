# api/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Скопіювати файл залежностей і встановити
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Скопіювати код API
COPY alembic.ini .
COPY alembic ./alembic
COPY app ./app

# Запуск FastAPI за допомогою Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]