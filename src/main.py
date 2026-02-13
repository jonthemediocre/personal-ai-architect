#!/usr/bin/env python3
"""
Personal AI Architect - Main Runner
Dual-domain, council-based, memory-backed AI system
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Add src to path
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir.parent))

from src.council import TrinityCouncil, Proposal, AgentRole
from src.memory import DualDomainMemory
from src.cron.scheduler import CronScheduler, create_heartbeat_job, create_backup_job
from src.channels.adapters import ChannelRouter, WebChatAdapter, NotificationManager

class PersonalAIArchitect:
    """Main Personal AI Architect system"""
    
    def __init__(self):
        self.started = datetime.now()
        self.council = TrinityCouncil()
        self.memory = DualDomainMemory()
        self.router = ChannelRouter()
        self.router.register("webchat", WebChatAdapter())
        self.notifier = NotificationManager(self.router)
        self.crons = CronScheduler()
        
        # Initialize cron jobs
        self.crons.add_job(create_heartbeat_job())
        self.crons.add_job(create_backup_job())
        
        # State
        self.active_domain = "personal"  # or "work"
        self.state_file = Path(__file__).parent.parent / "state" / "architect_state.json"
        
    def switch_domain(self, domain: str):
        """Switch between personal and work domains"""
        if domain in ["personal", "work"]:
            self.active_domain = domain
            return f"Switched to {domain} domain"
        return f"Unknown domain: {domain}"
    
    def query_memory(self, query: str, domain: str = None) -> str:
        """Query memory across domains"""
        results = self.memory.query_all(query, domain or self.active_domain)
        
        response = f"Query: '{query}'\n\n"
        
        if domain:
            domain_name = domain
        else:
            domain_name = self.active_domain
            
        response += f"[{domain_name.upper()}]\n"
        
        if results.get(domain_name):
            for r in results[domain_name]:
                response += f"- {r.content[:100]}\n"
        else:
            response += "No matching memories found.\n"
            
        return response
    
    def add_memory(self, category: str, content: str, 
                  importance: int = 3, tags: list = None):
        """Add a memory"""
        if self.active_domain == "personal":
            self.memory.add_personal(category, content, importance, tags)
        else:
            self.memory.add_work(category, content, importance, tags)
        return f"Added to {self.active_domain} memory"
    
    def submit_proposal(self, title: str, description: str,
                       priority: int = 3, external_action: bool = False,
                       estimated_cost: float = 0.0, risk_level: str = "low") -> str:
        """Submit a proposal to the council"""
        proposal = self.council.submit_proposal(
            title=title,
            description=description,
            domain=self.active_domain,
            priority=priority,
            external_action=external_action,
            estimated_cost=estimated_cost,
            risk_level=risk_level
        )
        
        # Run deliberation
        decision = self.council.deliberated(proposal)
        
        response = f"Proposal: {title}\n"
        response += f"Decision: {decision['decision'].upper()}\n"
        response += f"Reasoning: {decision['reasoning']}\n"
        
        if decision['requires_human_approval']:
            response += "\n⚠️ Requires human approval"
            
        return response
    
    def get_status(self) -> str:
        """Get system status"""
        return f"""# Personal AI Architect Status

**Active Domain:** {self.active_domain}
**Started:** {self.started.strftime('%Y-%m-%d %H:%M:%S')}
**Uptime:** {datetime.now() - self.started}

**Memory:**
- Personal entries: {len(self.memory.personal._entries)}
- Work entries: {len(self.memory.work._entries)}

**Council:**
- Pending proposals: {len(self.council.get_pending_proposals())}
- Total decisions: {len(self.council.decisions)}

**Cron Jobs:** {len(self.crons.jobs)} registered
"""
    
    def run_crons(self) -> str:
        """Run any due cron jobs"""
        due = self.crons.get_due_jobs()
        
        if not due:
            return "No cron jobs due"
            
        results = []
        for job in due:
            result = self.crons.run_job(job)
            status = "✅" if result["success"] else "❌"
            results.append(f"{status} {job.name}: {result.get('status', 'unknown')}")
            
        return "\n".join(results)
    
    def save_state(self):
        """Save current state"""
        state = {
            "active_domain": self.active_domain,
            "started": self.started.isoformat(),
            "pending_proposals": len(self.council.get_pending_proposals()),
            "memory_entries_personal": len(self.memory.personal._entries),
            "memory_entries_work": len(self.memory.work._entries),
            "last_saved": datetime.now().isoformat()
        }
        
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
            
    def load_state(self):
        """Load previous state"""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                state = json.load(f)
            self.active_domain = state.get("active_domain", "personal")
            return True
        return False

def main():
    """Main entry point"""
    import sys
    
    print("=" * 60)
    print("Personal AI Architect")
    print("=" * 60)
    
    architect = PersonalAIArchitect()
    
    # Load previous state
    if architect.load_state():
        print(f"Loaded previous state: {architect.active_domain} domain")
    
    # Show status
    print(architect.get_status())
    
    # Interactive loop (only if stdin is a terminal)
    if sys.stdin.isatty():
        print("\n--- Example Commands ---")
        print("  status          - Show system status")
        print("  domain <name>   - Switch domain (personal/work)")
        print("  memory <query>  - Query memory")
        print("  remember <text> - Add to memory")
        print("  propose <title> <desc> - Submit proposal")
        print("  run crons       - Run scheduled jobs")
        print("  quit            - Exit\n")
        
        while True:
            try:
                cmd = input(f"[{architect.active_domain}] > ").strip()
                
                if cmd in ["quit", "exit", "q"]:
                    architect.save_state()
                    print("Goodbye!")
                    break
                    
                elif cmd == "status":
                    print(architect.get_status())
                    
                elif cmd.startswith("domain "):
                    domain = cmd.split(" ", 1)[1]
                    print(architect.switch_domain(domain))
                    
                elif cmd.startswith("memory "):
                    query = cmd.split(" ", 1)[1]
                    print(architect.query_memory(query))
                    
                elif cmd.startswith("remember "):
                    content = cmd.split(" ", 1)[1]
                    print(architect.add_memory("note", content))
                    
                elif cmd.startswith("propose "):
                    parts = cmd.split(" ", 2)
                    if len(parts) >= 3:
                        title, description = parts[1], parts[2]
                        print(architect.submit_proposal(title, description))
                    else:
                        print("Usage: propose <title> <description>")
                        
                elif cmd == "run crons":
                    print(architect.run_crons())
                    
                else:
                    print(f"Unknown command: {cmd}")
                    
            except KeyboardInterrupt:
                print("\nUse 'quit' to exit")
                break
                
            except Exception as e:
                print(f"Error: {e}")
    else:
        print("(Non-interactive mode. Run with stdin for interactive mode.)")

if __name__ == "__main__":
    main()
