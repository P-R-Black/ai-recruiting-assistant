#!/usr/bin/env bash

set -euo pipefail

PROJECT_DIR="/opt/ai-recruiting-assistant"
COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE="backend/.env.production"
API_SERVICE="api"

cd "$PROJECT_DIR"

echo "=== Deploying AI Recruiting Assistant ==="

echo "Pulling latest main..."
git checkout main
git pull --ff-only origin main

echo "Building production image..."
docker compose \
  --env-file "$ENV_FILE" \
  -f "$COMPOSE_FILE" \
  build "$API_SERVICE"

echo "Starting production services..."
docker compose \
  --env-file "$ENV_FILE" \
  -f "$COMPOSE_FILE" \
  up -d

echo "Waiting for services to become healthy..."

for i in {1..30}; do
    API_STATUS=$(
        docker inspect \
            --format='{{.State.Health.Status}}' \
            "$(docker compose \
                --env-file "$ENV_FILE" \
                -f "$COMPOSE_FILE" \
                ps -q "$API_SERVICE")" \
        2>/dev/null || true
    )

    DB_STATUS=$(
        docker inspect \
            --format='{{.State.Health.Status}}' \
            "$(docker compose \
                --env-file "$ENV_FILE" \
                -f "$COMPOSE_FILE" \
                ps -q db)" \
        2>/dev/null || true
    )

    if [[ "$API_STATUS" == "healthy" && "$DB_STATUS" == "healthy" ]]; then
        echo "API and database are healthy."
        break
    fi

    if [[ "$i" -eq 30 ]]; then
        echo "ERROR: Services did not become healthy in time."
        docker compose \
            --env-file "$ENV_FILE" \
            -f "$COMPOSE_FILE" \
            ps
        exit 1
    fi

    sleep 2
done

echo "Creating pre-deployment database backup..."
"$PROJECT_DIR/scripts/backup_db.sh"

echo "Running database migrations..."
docker compose \
  --env-file "$ENV_FILE" \
  -f "$COMPOSE_FILE" \
  exec -T "$API_SERVICE" \
  /app/.venv/bin/alembic upgrade head

echo "Verifying migration state..."
docker compose \
  --env-file "$ENV_FILE" \
  -f "$COMPOSE_FILE" \
  exec -T "$API_SERVICE" \
  /app/.venv/bin/alembic current

echo "Checking public health endpoint..."
curl --fail --silent --show-error \
    https://recruiting-api.paulrblack.com/health


echo "=== Deployment completed successfully ==="