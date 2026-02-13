#!/usr/bin/env bash
set -euo pipefail

cp -n .env.example .env || true
mkdir -p outputs data/backups memory/daily

echo "Bootstrap complete."
echo "Next: edit .env then run: docker compose up -d --build"
