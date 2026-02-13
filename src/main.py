#!/usr/bin/env python3
"""
Personal AI Architect - Enhanced with Skills
Morning Briefings, Auto-Approve, Task Management, Health Monitoring
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Add src to path
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir.parent))

from src.council import TrinityCouncil
from src.memory import DualDomainMemory
from src.cron.scheduler import CronScheduler, create_heartbeat_job, create_backup_job
from src.channels.adapters import ChannelRouter, WebChatAdapter
from src.nl_parser import NLParser, ConversationManager
from src.skills.morning_briefing import MorningBriefingSkill, AutoApproveRules, TaskManager, HealthMonitor

class PersonalAIArchitect:
    """Enhanced Personal AI Architect with skills"""
    
    def __init__(self):
        self.started = datetime.now()
        self.council = TrinityCouncil()
        self.memory = DualDomainMemory()
        self.router = ChannelRouter()
        self.router.register("webchat", WebChatAdapter())
        
        # Skills
        self.briefing = MorningBriefingSkill()
        self.auto_approve = AutoApproveRules()
        self.tasks = TaskManager()
        self.health = HealthMonitor()
        
        # Crons
        self.crons = CronScheduler()
        self.crons.add_job(create_heartbeat_job())
        self.crons.add_job(create_backup_job())
        
        # State
        self.active_domain = "personal"
        self.state_file = Path(__file__).parent.parent / "state" / "architect_state.json"
        
    # Domain switching
    def switch_domain(self, domain: str):
        if domain in ["personal", "work"]:
            self.active_domain = domain
            return f"Switched to {domain} domain"
        return f"Unknown domain: {domain}"
    
    # Memory operations
    def query_memory(self, query: str, domain: str = None):
        results = self.memory.query_all(query, domain or self.active_domain)
        response = f"Query: '{query}'\n\n"
        domain_name = domain or self.active_domain
        response += f"[{domain_name.upper()}]\n"
        
        if results.get(domain_name):
            for r in results[domain_name]:
                response += f"- {r.content[:150]}\n"
        else:
            response += "No matching memories.\n"
        return response
    
    def remember(self, content: str, importance: int = 3, category: str = "note"):
        if self.active_domain == "personal":
            self.memory.add_personal(category, content, importance)
        else:
            self.memory.add_work(category, content, importance)
        return f"✅ Saved to {self.active_domain} memory"
    
    # Task management
    def add_task(self, title: str, priority: int = 3):
        return self.tasks.add(title, self.active_domain, priority)
    
    def list_tasks(self, domain: str = None):
        return self.tasks.list(domain or self.active_domain)
    
    def complete_task(self, task_id: str):
        return self.tasks.complete(task_id)
    
    # Proposals
    def propose(self, title: str, description: str, priority: int = 3):
        proposal = self.council.submit_proposal(
            title=title,
            description=description,
            domain=self.active_domain,
            priority=priority
        )
        decision = self.council.deliberated(proposal)
        
        emoji = "✅" if decision["decision"] == "approved" else "❌" if decision["decision"] == "rejected" else "⏳"
        response = f"{emoji} **Proposal:** {title}\n"
        response += f"**Decision:** {decision['decision'].upper()}\n"
        response += f"**Reasoning:** {decision['reasoning']}\n"
        
        if decision.get('requires_human_approval'):
            response += "\n⚠️ **Requires human approval**"
        return response
    
    # Skills
    def configure_briefing(self, **kwargs):
        return self.briefing.configure(**kwargs)
    
    def generate_briefing(self):
        return self.briefing.generate()
    
    def check_health(self):
        return self.health.get_status()
    
    # Status
    def get_status(self):
        return f"""# Personal AI Architect Status

**Active Domain:** {self.active_domain}
**Started:** {self.started.strftime('%Y-%m-%d %H:%M:%S')}
**Uptime:** {datetime.now() - self.started}

**Memory:**
- Personal entries: {len(self.memory.personal._entries)}
- Work entries: {len(self.memory.work._entries)}

**Tasks:** {len([t for t in self.tasks.tasks if t['status'] == 'pending'])} pending

**Council:**
- Pending proposals: {len(self.council.get_pending_proposals())}
- Total decisions: {len(self.council.decisions)}

**Skills:**
- Morning Briefing: ✅
- Auto-Approve: ✅
- Task Manager: ✅
- Health Monitor: ✅

**Cron Jobs:** {len(self.crons.jobs)} registered
"""
    
    def run_crons(self):
        due = self.crons.get_due_jobs()
        if not due:
            return "No cron jobs due right now."
        results = []
        for job in due:
            result = self.crons.run_job(job)
            status = "✅" if result["success"] else "❌"
            results.append(f"{status} {job.name}")
        return "\n".join(results)
    
    # Persistence
    def save_state(self):
        state = {
            "active_domain": self.active_domain,
            "started": self.started.isoformat(),
            "pending_proposals": len(self.council.get_pending_proposals()),
            "memory_personal": len(self.memory.personal._entries),
            "memory_work": len(self.memory.work._entries),
            "tasks_pending": len([t for t in self.tasks.tasks if t['status'] == 'pending']),
            "last_saved": datetime.now().isoformat()
        }
        import json
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def load_state(self):
        if self.state_file.exists():
            import json
            with open(self.state_file, 'r') as f:
                state = json.load(f)
            self.active_domain = state.get("active_domain", "personal")
            return True
        return False


def main():
    print("=" * 60)
    print("🤖 Personal AI Architect - Enhanced Edition")
    print("=" * 60)
    
    architect = PersonalAIArchitect()
    
    if architect.load_state():
        print(f"Loaded state: {architect.active_domain} domain")
    
    # Initialize NL parser
    conversation = ConversationManager(architect)
    
    print("\n" + "=" * 60)
    print("New Skills Available:")
    print("  • 'Give me a morning briefing'")
    print("  • 'Add task: Review proposals'")
    print("  • 'What are my tasks?'")
    print("  • 'Check system health'")
    print("  • 'Configure briefing for SF weather'")
    print("=" * 60)
    
    # Interactive loop
    while True:
        try:
            cmd = input(f"\n[{architect.active_domain}] > ").strip()
            
            if not cmd:
                continue
                
            if cmd.lower() in ["quit", "exit", "q", "bye"]:
                architect.save_state()
                print("Goodbye! 👋")
                break
            
            # Handle special commands
            if cmd.lower() in ["briefing", "morning briefing", "give me a morning briefing"]:
                print(f"\n{architect.generate_briefing()}")
                continue
            elif cmd.lower() in ["health", "check health", "system health"]:
                print(f"\n{architect.check_health()}")
                continue
            elif cmd.lower().startswith("task ") or cmd.lower().startswith("add task "):
                task = cmd.replace("add task ", "").replace("task ", "").strip()
                print(f"\n{architect.add_task(task)}")
                continue
            elif cmd.lower() in ["tasks", "list tasks", "show tasks", "what are my tasks"]:
                print(f"\n{architect.list_tasks()}")
                continue
            elif cmd.lower().startswith("complete ") or cmd.lower().startswith("done "):
                task_id = cmd.replace("complete ", "").replace("done ", "").strip()
                print(f"\n{architect.complete_task(task_id)}")
                continue
            elif cmd.lower().startswith("configure briefing"):
                # Parse remaining kwargs
                import re
                location = re.search(r"for (\w+)", cmd)
                if location:
                    print(f"\n{architect.configure_briefing(location=location.group(1))}")
                else:
                    print(f"\n{architect.configure_briefing()}")
                continue
            
            # Default to NL processing
            response = conversation.process(cmd)
            print(f"\n{response}")
                
        except KeyboardInterrupt:
            print("\n\nUse 'quit' to exit.")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
