#!/usr/bin/env bash
# Setup script for new machine
# Generates machine-specific lock key and configures git

set -euo pipefail

REPO_DIR="${1:-$(pwd)}"
cd "$REPO_DIR"

echo "🚀 Setting up leader election for machine: ${HOSTNAME:-$(hostname)}"

# Generate lock key (unique per machine)
LOCK_KEY_FILE="$REPO_DIR/.lock_secret"
if [[ ! -f "$LOCK_KEY_FILE" ]]; then
    openssl rand -base64 32 > "$LOCK_KEY_FILE"
    chmod 600 "$LOCK_KEY_FILE"
    echo "🔐 Generated lock key: $LOCK_KEY_FILE"
else
    echo "✅ Lock key exists: $LOCK_KEY_FILE"
fi

# Create state directory
mkdir -p "$REPO_DIR/state"
echo "📁 Created state directory: $REPO_DIR/state"

# Add .lock_secret to .gitignore (CRITICAL - never commit!)
if ! grep -q "lock_secret" "$REPO_DIR/.gitignore" 2>/dev/null; then
    echo "# Lock secret (machine-specific, never commit)" >> "$REPO_DIR/.gitignore"
    echo ".lock_secret" >> "$REPO_DIR/.gitignore"
    echo "🚫 Added .lock_secret to .gitignore"
else
    echo "✅ .lock_secret already in .gitignore"
fi

# Create symlink for easy access from anywhere
SYMLINK_DIR="${HOME}/.local/bin"
mkdir -p "$SYMLINK_DIR"
ln -sf "$REPO_DIR/scripts/leader-election.sh" "$SYMLINK_DIR/sse-leader"
ln -sf "$REPO_DIR/scripts/run-safe.sh" "$SYMLINK_DIR/sse-run"
ln -sf "$REPO_DIR/scripts/heartbeat-safe.sh" "$SYMLINK_DIR/sse-heartbeat"
echo "🔗 Created symlinks in $SYMLINK_DIR/"

# Test leader election
echo ""
echo "🗳️  Testing leader election..."
if bash "$REPO_DIR/scripts/leader-election.sh"; then
    echo "✅ Successfully claimed initial lock"
else
    echo "🤝 Another machine holds the lock (expected)"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Usage:"
echo "  sse-leader        # Check if you're leader"
echo "  sse-run          # Run OpenClaw (only if leader)"
echo "  sse-heartbeat    # Run heartbeat (only if leader)"
echo ""
echo "Your lock key: $LOCK_KEY_FILE (keep this secret!)"
