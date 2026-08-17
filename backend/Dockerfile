FROM python:3.12-slim

WORKDIR /app

# Copy project files
COPY pyproject.toml ./
COPY alembic.ini ./
COPY alembic/ ./alembic/
COPY application/ ./application/
COPY domain/ ./domain/
COPY infrastructure/ ./infrastructure/
COPY main.py ./
COPY scripts/ ./scripts/

# Install dependencies with pip (no uv needed)
RUN pip install --no-cache-dir .

# Expose port (Railway sets $PORT)
EXPOSE 8000

# Start: run migrations (fast no-op if already applied) then uvicorn
CMD alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
