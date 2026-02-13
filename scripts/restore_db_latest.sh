#!/usr/bin/env bash
set -euo pipefail

LATEST=$(ls -1 data/backups/*.sql | tail -n 1)
echo "Restoring: ${LATEST}"
cat "${LATEST}" | docker compose exec -T db psql -U postgres -d sse
echo "Restore complete."
