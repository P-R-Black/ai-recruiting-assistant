FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency definitions first so Docker can cache this layer
COPY pyproject.toml uv.lock ./

# Install production dependencies from the lockfile
RUN uv sync --frozen --no-dev

# Copy application files
COPY app ./app
COPY alembic.ini .
COPY alembic ./alembic

EXPOSE 8000

ENV PATH="/app/.venv/bin:$PATH"

CMD ["/app/.venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]