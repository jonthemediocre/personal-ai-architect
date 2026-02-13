#!/usr/bin/env bash
# Secure OpenClaw Wrapper with Leader Election
# Only runs OpenClaw if this machine is the elected leader

set -euo pipefail

SCRIPT_DIR="$(dirname "$(realpath "$0")")"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
cd "$REPO_DIR"

echo "🗳️  Leader Election Check..."
echo "Machine: ${HOSTNAME:-$(hostname)}"
echo "Repo: $REPO_DIR"

# Run leader election
if bash "$SCRIPT_DIR/leader-election.sh"; then
    echo "✅ Elected as leader - starting OpenClaw..."
    
    # Run OpenClaw
    cd /home/jonbrookings/.nvm/versions/node/v22.17.0/lib/node_modules/openclaw
    node ./dist/index.js run
    
else
    echo "🛑 Not elected - another instance is active"
    echo "💤 Sleeping for 60 seconds before re-check..."
    
    sleep 60
    
    # Re-check (in case leader died)
    exec "$0" "$@"
fi
