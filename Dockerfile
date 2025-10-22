FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app

# Копируем файлы проекта
COPY . .

RUN poetry install --no-root --no-dev

# Открываем порт для приложения
EXPOSE 8000

# Запускаем приложение
CMD ["poetry", "run", "uvicorn", "src.opengenes_mcp.main:app", "--host", "0.0.0.0", "--port", "8000"]
