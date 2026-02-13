#!/usr/bin/env bash
set -euo pipefail
git add -A
git commit -m "Hourly Snapshot" || true
git push || true
