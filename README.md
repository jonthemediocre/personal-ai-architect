# Personal AI Architect

Local-first agentic operating system for personal productivity and life automation:

- **Trinity Council** (Strategist / Skeptic / Guardian) + Moderator consensus
- **Proactive Humanizer** voice governor
- **Lane queue** reliability + full audit logs
- **Approval gate** for all external actions
- **Cost governance** (tokens + $)
- **Self-evolution** drift audit (proposal-only)
- **Dual-domain architecture** — personal + optional work contexts
- **Leader election** — secure multi-machine failover with HMAC signatures

## Domains

| Domain | Purpose | Data Isolation |
|--------|---------|----------------|
| `personal` | Life ops, projects, relationships, health | Encrypted at rest |
| `work` | Professional context (optional) | Separate storage |

## Quick Start

```bash
cd ~/vibe_coding_projects/CLAWD-BOSS/personal-ai-architect
cp .env.example .env  # Fill secrets
docker compose up -d
```

## Core Capabilities

- **Messaging** — Telegram, email, Slack via MCP
- **Calendar** — Google Calendar integration
- **Memory** — Persistent context across sessions
- **Coding** — Cursor, GitHub, file system access
- **Automation** — Crons for daily briefs, drift audits, backups

## Governance

All external actions require explicit approval. The Trinity Council debates, Humanizer checks tone, Guardian validates safety before execution.

## Dual-Domain Operation

```bash
# Run with personal domain (default)
./run-safe.sh personal

# Run with work domain (if configured)
./run-safe.sh work
```

## Leader Election

Multi-machine failover using GitHub-based locks with HMAC signatures. Only one instance runs at a time.

---

*Vanta is your AI architect, coding genius, and operational co-pilot.*
