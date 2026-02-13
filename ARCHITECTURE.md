# Personal AI Architect — Architecture Improvements

Based on OpenClaw best practices and common use cases.

## Core Architecture

### 1. Dual-Domain Context Separation
```
┌─────────────────────────────────────────┐
│           Personal AI Architect           │
├─────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    │
│  │   PERSONAL   │    │    WORK    │    │
│  │   Domain    │    │   Domain    │    │
│  │  - Projects │    │  - Career   │    │
│  │  - Health   │    │  - Ops      │    │
│  │  - Finance  │    │  - Clients  │    │
│  └──────┬──────┘    └──────┬──────┘    │
│         │                   │             │
│         └───────┬───────────┘             │
│                 ▼                         │
│         ┌─────────────┐                  │
│         │   COUNCIL   │                  │
│         │  (Trinity)  │                  │
│         └──────┬──────┘                  │
│                │                          │
│    ┌───────────┼───────────┐              │
│    ▼           ▼           ▼              │
│ ┌──────┐  ┌──────┐  ┌──────────┐         │
│ │Write │  │ Code │  │ Analyze  │         │
│ └──────┘  └──────┘  └──────────┘         │
└─────────────────────────────────────────┘
```

### 2. Channel Architecture

| Channel | Purpose | Priority |
|---------|---------|----------|
| **Webchat** | Primary interaction | High |
| **Discord** | Commands + notifications | Medium |
| **Telegram** | Mobile alerts | Low (if working) |

### 3. Crons Hierarchy

```
Hourly
  ├── Git backup (configs)
  ├── DB dump
  └── Heartbeat check

Daily (07:00)
  ├── Daily brief (signals, actions, approvals)
  └── Memory sync

Weekly (Sunday 23:00)
  └── Weekly synthesis

Monthly
  └── Restore test
```

### 4. Leader Election (Multi-Machine)

```
┌─────────────┐     ┌─────────────┐
│   Machine A │     │   Machine B │
│   (Active)  │────▶│   (Standby) │
│  CLAIM LOCK │     │  WATCH LOCK │
└─────────────┘     └─────────────┘
       │                   │
       ▼                   ▼
  GitHub Lock          Detect stale
  + HMAC               → CLAIM LOCK
```

## Use Cases Implemented

### ✅ Daily Briefing
- Top 5 signals with sources
- Risks and blockers
- Next 3 actions
- Approvals pending

### ✅ Coding Workflow
- Strategy → Skeptical Review → Implementation → Verification
- Git-backed version control
- Local-first execution

### ✅ Memory System
- Daily logs → MEMORY.md
- Long-term → LEARNINGS.md
- Context preservation across sessions

### ✅ Notification Routing
```
Event → Council Decision → Human Approval → Notification
```

## Files Structure

```
personal-ai-architect/
├── agents/           # Council members
├── config/           # Models, lanes, MCP servers
├── crons/            # Scheduled tasks
├── governance/       # Approval rules, risk matrix
├── humanizer/       # Voice/tone governor
├── memory/          # Personal + Work contexts
├── scripts/        # Backup, heartbeat, leader election
├── state/          # Active lock file
└── outputs/        # Generated reports
```

## Key Scripts

| Script | Purpose |
|--------|---------|
| `run-safe.sh` | Leader-aware startup |
| `heartbeat-safe.sh` | Health check with lock |
| `leader-election.sh` | Acquire/release lock |
| `backup_git_hourly.sh` | Auto-commit changes |

## Next Improvements

1. **Voice Interface** — Text-to-speech for briefings
2. **Auto-Approve Rules** — Low-risk actions auto-approved
3. **Context Compression** — Summarize old memory automatically
4. **Multi-Machine Sync** — Full state replication
5. **Plugin System** — Extensible skill architecture

---

*Architecture v1.0 — Built from OpenClaw best practices*
