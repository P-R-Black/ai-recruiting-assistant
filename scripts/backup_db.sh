#!/usr/bin/env bash

set -euo pipefail

BACKUP_DIR="/opt/ai-recruiting-assistant/backups"
TIMESTAMP="$(date +"%Y-%m-%d_%H-%M-%S")"
BACKUP_FILE="${BACKUP_DIR}/ai_recruiting_${TIMESTAMP}.sql.gz"

mkdir -p "$BACKUP_DIR"

echo "Creating database backup..."
echo "Destination: $BACKUP_FILE"

docker exec ai-recruiting-db \
  pg_dump -U ai_recruiting -d ai_recruiting \
  | gzip > "$BACKUP_FILE"

echo "Backup completed successfully."

echo "Removing backups older than 7 days..."

find "$BACKUP_DIR" \
  -type f \
  -name "*.sql.gz" \
  -mtime +7 \
  -delete

echo "Current backups:"
ls -lh "$BACKUP_DIR"