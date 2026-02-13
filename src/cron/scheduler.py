#!/usr/bin/env python3
"""
Scheduled Cron System for Personal AI Architect
Heartbeat, Daily Brief, Weekly Synthesis, Drift Audit
"""

import asyncio
import subprocess
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Callable, Optional
from pathlib import Path
import json

@dataclass
class CronJob:
    name: str
    schedule: str  # "hourly", "daily", "weekly", "monthly"
    hour: Optional[int] = None  # For daily/weekly
    minute: int = 0
    day_of_week: Optional[int] = None  # 0=Monday for weekly
    command: str = ""
    enabled: bool = True
    last_run: Optional[datetime] = None
    last_status: Optional[str] = None
    consecutive_failures: int = 0

class CronScheduler:
    def __init__(self):
        self.jobs: list[CronJob] = []
        self.results: list[dict] = []
        
    def add_job(self, job: CronJob):
        """Add a cron job"""
        self.jobs.append(job)
        
    def get_due_jobs(self) -> list[CronJob]:
        """Get jobs that are due to run"""
        now = datetime.now()
        due = []
        
        for job in self.jobs:
            if not job.enabled:
                continue
                
            if job.schedule == "hourly":
                if job.last_run is None or (now - job.last_run).total_seconds() >= 3600:
                    if now.minute >= job.minute:
                        due.append(job)
                        
            elif job.schedule == "daily":
                if job.last_run is None or job.last_run.date() < now.date():
                    if now.hour >= job.hour and now.minute >= job.minute:
                        due.append(job)
                        
            elif job.schedule == "weekly":
                if job.last_run is None or (now - job.last_run).total_seconds() >= 604800:
                    if now.weekday() == job.day_of_week and now.hour >= job.hour:
                        due.append(job)
                        
        return due
    
    def run_job(self, job: CronJob) -> dict:
        """Execute a cron job"""
        start = datetime.now()
        result = {
            "job": job.name,
            "start": start.isoformat(),
            "success": False,
            "output": "",
            "error": ""
        }
        
        try:
            # Run the command
            proc = subprocess.run(
                job.command,
                shell=True,
                capture_output=True,
                timeout=300  # 5 min timeout
            )
            result["success"] = proc.returncode == 0
            result["output"] = proc.stdout.decode()[:1000]
            result["error"] = proc.stderr.decode()[:500]
            job.consecutive_failures = 0 if result["success"] else job.consecutive_failures + 1
            
        except Exception as e:
            result["error"] = str(e)
            job.consecutive_failures += 1
            
        result["end"] = datetime.now().isoformat()
        job.last_run = datetime.now()
        job.last_status = "ok" if result["success"] else "failed"
        
        self.results.append(result)
        return result

def create_heartbeat_job() -> CronJob:
    """Create heartbeat health check job"""
    return CronJob(
        name="heartbeat",
        schedule="hourly",
        minute=0,
        command="""
echo "[$(date)] Heartbeat check..."
# Check gateway
curl -s http://127.0.0.1:18789/health || echo "Gateway unhealthy"
# Check DB
pg_isready -h localhost -p 5432 || echo "DB unreachable"
# Log result
echo "Heartbeat complete"
""".strip()
    )

def create_backup_job() -> CronJob:
    """Create git backup job"""
    return CronJob(
        name="backup_git",
        schedule="hourly",
        minute=5,
        command="""
cd ~/vibe_coding_projects/CLAWD-BOSS/personal-ai-architect
git add -A
git commit -m "Hourly Snapshot $(date +'%Y-%m-%d %H:%M')" || true
git push origin main || echo "Push failed"
""".strip()
    )

def create_daily_brief_job() -> CronJob:
    """Create daily brief job (7 AM)"""
    return CronJob(
        name="daily_brief",
        schedule="daily",
        hour=7,
        minute=0,
        command="""
cd ~/vibe_coding_projects/CLAWD-BOSS/personal-ai-architect
python3 -c "
from src.council import TrinityCouncil
from src.memory import DualDomainMemory

memory = DualDomainMemory()
council = TrinityCouncil()

# Generate brief
brief = '''# Daily Brief - ''' + datetime.now().strftime('%Y-%m-%d') + '''

## Pending Decisions
''' + str(len(council.get_pending_proposals())) + ''' proposals awaiting council

## Recent Memory
''' + str(len(memory.get_recent(1))) + ''' new memories added

## Next Actions
- Review pending council proposals
- Check system health
- Process inbox
'''
print(brief)
"
""".strip()
    )

def create_weekly_synthesis_job() -> CronJob:
    """Create weekly synthesis job (Sunday 11 PM)"""
    return CronJob(
        name="weekly_synthesis",
        schedule="weekly",
        day_of_week=6,  # Sunday
        hour=23,
        minute=0,
        command="""
cd ~/vibe_coding_projects/CLAWD-BOSS/personal-ai-architect
echo "# Weekly Synthesis - $(date +'%Y-%m-%d')" >> outputs/weekly_synthesis.md
echo "Generated: $(date)" >> outputs/weekly_synthesis.md
echo "TODO: Summarize week's decisions and learnings" >> outputs/weekly_synthesis.md
""".strip()
    )

def create_drift_audit_job() -> CronJob:
    """Create drift audit job (4 AM daily)"""
    return CronJob(
        name="drift_audit",
        schedule="daily",
        hour=4,
        minute=0,
        command="""
cd ~/vibe_coding_projects/CLAWD-BOSS/personal-ai-architect
python3 -c "
from datetime import datetime
print(f'Drift Audit - {datetime.now().isoformat()}')
print('Checking for configuration drift...')
print('TODO: Implement drift detection')
"
""".strip()
    )

class HeartbeatService:
    """Lightweight heartbeat for system monitoring"""
    def __init__(self):
        self.last_beat = None
        self.status = "unknown"
        
    def check(self) -> dict:
        """Perform heartbeat check"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "checks": {}
        }
        
        # Check gateway
        try:
            import requests
            r = requests.get("http://127.0.0.1:18789/health", timeout=5)
            result["checks"]["gateway"] = "ok" if r.status_code == 200 else "error"
        except:
            result["checks"]["gateway"] = "unreachable"
            
        # Check DB
        import subprocess
        p = subprocess.run(
            ["pg_isready", "-h", "localhost", "-p", "5432"],
            capture_output=True, timeout=5
        )
        result["checks"]["database"] = "ok" if p.returncode == 0 else "error"
        
        # Overall status
        all_ok = all(v == "ok" for v in result["checks"].values())
        result["status"] = "healthy" if all_ok else "degraded"
        
        self.last_beat = result
        self.status = result["status"]
        
        return result

if __name__ == "__main__":
    # Initialize scheduler
    scheduler = CronScheduler()
    scheduler.add_job(create_heartbeat_job())
    scheduler.add_job(create_backup_job())
    scheduler.add_job(create_daily_brief_job())
    scheduler.add_job(create_weekly_synthesis_job())
    scheduler.add_job(create_drift_audit_job())
    
    print("Cron Jobs Registered:")
    for job in scheduler.jobs:
        print(f"  - {job.name}: {job.schedule} @ {job.hour or ''}:{job.minute:02d}")
