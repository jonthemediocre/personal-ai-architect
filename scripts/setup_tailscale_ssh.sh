#!/usr/bin/env bash
set -euo pipefail

echo "Run on host (requires tailscale installed and logged in):"
echo "sudo tailscale up --ssh"
echo "Then from client: ssh <user>@<tailscale-hostname>"
