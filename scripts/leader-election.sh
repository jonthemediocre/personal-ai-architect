#!/usr/bin/env bash
# Leader Election for Multi-Host OpenClaw Handoff
# Ensures only one instance runs at a time via GitHub-based lock

set -euo pipefail

REPO_DIR="${1:-$(dirname "$(dirname "$(realpath "$0")")")}"
cd "$REPO_DIR"

LOCK_FILE="state/active.lock"
LOCK_KEY_FILE=".lock_secret"
MAX_AGE_SECONDS=300  # 5 minutes

# Create state directory if missing
mkdir -p "$REPO_DIR/state"

# Generate key if missing (run once per machine)
if [[ ! -f "$LOCK_KEY_FILE" ]]; then
    openssl rand -base64 32 > "$LOCK_KEY_FILE"
    chmod 600 "$LOCK_KEY_FILE"
    echo "🔐 Generated new lock key at $LOCK_KEY_FILE"
fi

# Read machine identity
MACHINE_ID="${HOSTNAME:-$(hostname)}-$(whoami)"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
HMAC_KEY=$(cat "$LOCK_KEY_FILE")

# Sign the lock data
sign_data() {
    local data="$1"
    echo -n "$data" | openssl dgst -sha256 -hmac "$HMAC_KEY" -binary | base64
}

# Verify a lock file
verify_lock() {
    local lock_file="$1"
    [[ ! -f "$lock_file" ]] && return 1
    
    local hmac_received
    hmac_received=$(tail -n 1 "$lock_file" 2>/dev/null) || return 1
    
    local content
    content=$(head -n -1 "$lock_file" 2>/dev/null) || return 1
    
    local hmac_computed
    hmac_computed=$(sign_data "$content")
    
    # Constant-time comparison to prevent timing attacks
    [[ "$hmac_received" == "$hmac_computed" ]]
}

# Get lock age in seconds
get_lock_age() {
    local lock_file="$1"
    [[ ! -f "$lock_file" ]] && return 999
    
    local timestamp
    timestamp=$(head -n 1 "$lock_file" 2>/dev/null) || return 999
    
    local lock_time
    lock_time=$(date -d "$timestamp" +%s 2>/dev/null) || return 999
    
    local now
    now=$(date +%s)
    
    echo $((now - lock_time))
}

# Claim the lock
claim_lock() {
    local content="$TIMESTAMP
$MACHINE_ID"
    
    local hmac
    hmac=$(sign_data "$content")
    
    {
        echo "$content"
        echo "$hmac"
    } > "$LOCK_FILE"
    
    git add "$LOCK_FILE" 2>/dev/null || true
    git commit -m "Lock: $MACHINE_ID at $TIMESTAMP" 2>/dev/null || true
    git push origin master 2>/dev/null || true
    
    echo "🔒 Claimed lock: $MACHINE_ID"
}

# Check if we should be leader
should_run() {
    # Fetch latest lock from remote
    git fetch origin master 2>/dev/null || true
    
    local remote_lock="origin/master:$LOCK_FILE"
    local temp_lock=$(mktemp)
    trap "rm -f '$temp_lock'" EXIT
    
    # Try to get remote lock
    if git show "$remote_lock" > "$temp_lock" 2>/dev/null; then
        if verify_lock "$temp_lock"; then
            local age
            age=$(get_lock_age "$temp_lock")
            
            if [[ $age -lt $MAX_AGE_SECONDS ]]; then
                # Lock is fresh, someone else is leader
                return 1
            fi
            # Lock is stale, we can claim it
        fi
    fi
    
    # We're claiming or already have the lock
    claim_lock
    return 0
}

# Main: claim lock if eligible
should_run
