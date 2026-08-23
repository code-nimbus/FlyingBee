FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Project root
WORKDIR /app

# Copy dependency files
COPY backend/pyproject.toml backend/uv.lock ./backend/

# uv needs to run where pyproject.toml exists
WORKDIR /app/backend

# Create virtual environment
RUN uv venv --python 3.12 /opt/venv

# Install dependencies
RUN uv export --frozen --format requirements-txt > /tmp/requirements.txt \
    && uv pip sync --python /opt/venv/bin/python /tmp/requirements.txt \
    && rm /tmp/requirements.txt

# Copy application
COPY backend/ ./

# IMPORTANT: runtime working directory is project root
WORKDIR /app

ENV PATH="/opt/venv/bin:$PATH"

CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "80"]