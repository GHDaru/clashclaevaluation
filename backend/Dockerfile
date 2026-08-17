FROM python:3.12-slim

WORKDIR /app

# Install uv for fast dependency resolution
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files
COPY pyproject.toml ./
COPY alembic.ini ./
COPY alembic/ ./alembic/
COPY application/ ./application/
COPY domain/ ./domain/
COPY infrastructure/ ./infrastructure/
COPY main.py ./
COPY scripts/ ./scripts/

# Install dependencies
RUN uv pip install --system .

# Expose port (Railway sets $PORT)
EXPOSE 8000

# Start script: run migrations then start uvicorn
CMD alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
