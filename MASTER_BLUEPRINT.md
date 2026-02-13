# MASTER_BLUEPRINT — Personal AI Architect (2026)

This repository implements a local-first Agentic OS for personal productivity and life automation.
Designed to run 24/7 on a dedicated host, with secure remote access, sandboxed execution, and strict governance:
- approval gates
- cost caps
- moderated multi-agent consensus
- self-evolution via proposal-only drift audits
- proactive voice control (Humanizer governor)

## Functional Requirements
1) Daily briefing at 07:00 local
2) Nightly council at 00:00 local
3) Weekly synthesis at Sunday 23:00 local
4) Drift audit daily at 04:00 local (proposal-only)
5) Heartbeat every 5 minutes (self-heal + alert)
6) Timestamped DB backup hourly; git snapshot hourly

## Dual-Domain Architecture

| Domain | Context | Storage |
|--------|---------|---------|
| `personal` | Life, projects, relationships, health | `memory/personal/` |
| `work` | Professional context (optional) | `memory/work/` |

## Core Components
- **LaneQueue**: sequential task runner with idempotent steps + audit trail
- **Budget Governor**: token and $ caps per task/day; "BOOST REQUIRED" gate
- **Approval System**: creates approval requests and waits for Telegram confirm
- **Council Runner**: Strategist + Skeptic + Guardian + Moderator reconciliation
- **Humanizer Governor**: proactive voice constraints + smell lexicon updates
- **Memory System**:
  - Markdown: MEMORY.md, LEARNINGS.md, daily logs
  - PostgreSQL + pgvector: durable structured + semantic retrieval

## Execution Model (Lane Queue)
A "lane" is an isolated task stream (e.g., projects, admin, life).
Each lane processes one job at a time:
- Observe → Plan → Tool Calls → Verify → Persist → Notify
Every step is recorded to a JSONL audit log.

## Governance Model
- Approval gate for outbound actions
- Council consensus gate for reports and decisions
- Drift audits propose changes; never auto-apply

## Safety Model
- Tool allowlists (commands, domains)
- Secrets never logged
- Sandbox by default

## Leader Election
Multi-machine failover using GitHub-based locks with HMAC signatures.
- Lock file: `state/active.lock`
- HMAC signatures prevent spoofing
- 5-minute stale lock detection
- Machine-specific keys in `.lock_secret`

---

*This repo contains full scaffolding and runnable reference code for your personal AI operating system.*
