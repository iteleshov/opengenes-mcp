FROM python:3.11-slim

RUN apt-get update && apt-get install -y curl git build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

COPY . .

EXPOSE 3001

ENTRYPOINT ["sh", "-c", "uvx opengenes-mcp && tail -f /dev/null"]
