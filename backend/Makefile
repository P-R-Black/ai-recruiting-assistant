.DEFAULT_GOAL := help

.PHONY: help run test lint format migrate upgrade downgrade

help:
	@echo ""
	@echo "AI Recruiting Assistant"
	@echo ""
	@echo "Available commands:"
	@echo "  make run                 Start the FastAPI development server"
	@echo "  make test                Run the test suite"
	@echo "  make lint                Check code with Ruff"
	@echo "  make format              Automatically fix Ruff issues"
	@echo "  make migrate MSG=\"...\"   Generate a new Alembic migration"
	@echo "  make upgrade             Apply all migrations"
	@echo "  make downgrade           Roll back the latest migration"

run:
	uv run uvicorn app.main:app --reload

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff check . --fix

migrate:
	uv run alembic revision --autogenerate -m "$(MSG)"

upgrade:
	uv run alembic upgrade head

downgrade:
	uv run alembic downgrade -1