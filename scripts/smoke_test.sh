#!/usr/bin/env bash
set -euo pipefail
docker compose exec app python -m src.cli smoke-test
echo "Smoke test passed."
