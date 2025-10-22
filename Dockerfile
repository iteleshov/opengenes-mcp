FROM python:3.11.8-slim

RUN apt-get update && apt-get install -y curl build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:$PATH"
ENV POETRY_VIRTUALENVS_CREATE=false
ENV POETRY_IGNORE_PYTHON=true

WORKDIR /app

COPY pyproject.toml poetry.lock* /app/

RUN poetry install --no-root --without dev

COPY src ./src

EXPOSE 8000

CMD ["poetry", "run", "python", "src/opengenes_mcp/server.py"]
