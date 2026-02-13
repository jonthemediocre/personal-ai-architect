#!/usr/bin/env bash
set -euo pipefail
TS=$(date +"%Y%m%d_%H%M%S")
mkdir -p data/backups
docker compose exec -T db pg_dump -U postgres sse > "data/backups/sse_${TS}.sql"
echo "DB backup written: data/backups/sse_${TS}.sql"
