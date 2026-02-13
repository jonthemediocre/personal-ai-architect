#!/usr/bin/env bash
set -euo pipefail
docker compose up -d --build
docker compose exec app python -m src.cli init-db
docker compose exec app python -m src.cli run
