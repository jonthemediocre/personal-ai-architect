#!/usr/bin/env bash
# Secure Heartbeat with Leader Election
# Only sends heartbeat if this machine is the elected leader

set -euo pipefail

SCRIPT_DIR="$(dirname "$(realpath "$0")")"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
cd "$REPO_DIR"

LOCK_FILE="state/active.lock"
LOCK_KEY_FILE=".lock_secret"
MAX_AGE_SECONDS=300

# Ensure state dir exists
mkdir -p "$REPO_DIR/state"

# Generate key if missing
if [[ ! -f "$LOCK_KEY_FILE" ]]; then
    openssl rand -base64 32 > "$LOCK_KEY_FILE"
    chmod 600 "$LOCK_KEY_FILE"
fi

MACHINE_ID="${HOSTNAME:-$(hostname)}-$(whoami)"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
HMAC_KEY=$(cat "$LOCK_KEY_FILE")

sign_data() {
    echo -n "$1" | openssl dgst -sha256 -hmac "$HMAC_KEY" -binary | base64
}

verify_lock() {
    [[ ! -f "$1" ]] && return 1
    local hmac_received
    hmac_received=$(tail -n 1 "$1" 2>/dev/null) || return 1
    local content
    content=$(head -n -1 "$1" 2>/dev/null) || return 1
    local hmac_computed
    hmac_computed=$(sign_data "$content")
    [[ "$hmac_received" == "$hmac_computed" ]]
}

get_lock_age() {
    [[ ! -f "$1" ]] && return 999
    local timestamp
    timestamp=$(head -n 1 "$1" 2>/dev/null) || return 999
    local lock_time
    lock_time=$(date -d "$timestamp" +%s 2>/dev/null) || return 999
    local now
    now=$(date +%s)
    echo $((now - lock_time))
}

claim_lock() {
    local content="$TIMESTAMP
$MACHINE_ID"
    local hmac
    hmac=$(sign_data "$content")
    {
        echo "$content"
        echo "$hmac"
    } > "$LOCK_FILE"
    
    # Atomic commit+push
    git add "$LOCK_FILE" 2>/dev/null || true
    git commit -m "Heartbeat: $MACHINE_ID at $TIMESTAMP" 2>/dev/null || true
    git push origin master 2>/dev/null || true
    echo "🔒 Renewed lock: $MACHINE_ID"
}

# Leader election check
is_leader() {
    git fetch origin master 2>/dev/null || true
    local temp_lock=$(mktemp)
    trap "rm -f '$temp_lock'" EXIT
    
    if git show "origin/master:$LOCK_FILE" > "$temp_lock" 2>/dev/null; then
        if verify_lock "$temp_lock"; then
            local age
            age=$(get_lock_age "$temp_lock")
            if [[ $age -lt $MAX_AGE_SECONDS ]]; then
                # Another machine is leader
                return 1
            fi
        fi
    fi
    # We become leader
    claim_lock
    return 0
}

# Run heartbeat only if leader
if is_leader; then
    echo "✅ Leader - running heartbeat..."
    
    # Your actual heartbeat logic here
    # python -m src.cli heartbeat || openclaw cron heartbeat || etc
    
    # Renew lock
    claim_lock
else
    echo "🛑 Not leader - skipping heartbeat (leader is active)"
    exit 0
fi
