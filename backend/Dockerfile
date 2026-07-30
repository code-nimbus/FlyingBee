FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY . .

WORKDIR /app/backend

RUN uv sync --frozen --no-cache

WORKDIR /app

CMD ["uv", "run", "--project", "backend", "python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "80"]