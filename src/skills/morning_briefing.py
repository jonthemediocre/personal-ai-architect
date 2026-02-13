#!/usr/bin/env python3
"""
Morning Briefing Skill for Personal AI Architect
Automated daily summary with weather, calendar, tasks, and priorities
"""

from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Optional, Dict
import json

@dataclass
class BriefingSection:
    name: str
    content: str
    priority: int = 1  # 1=high, 2=medium, 3=low

class MorningBriefingSkill:
    """Generate automated morning briefings"""
    
    def __init__(self):
        self.preferences = {
            "location": "San Francisco",
            "check_personal_calendar": True,
            "check_work_calendar": True,
            "check_emails": True,
            "check_weather": True,
            "trending_topics": ["AI", "tech", "startups"],
            "output_channel": "telegram"
        }
        self.last_briefing = None
        
    def configure(self, **kwargs):
        """Configure briefing preferences"""
        self.preferences.update(kwargs)
        return f"Morning briefing updated: {json.dumps(self.preferences, indent=2)}"
    
    def generate(self) -> str:
        """Generate morning briefing"""
        now = datetime.now()
        
        sections = []
        
        # Weather (if enabled)
        if self.preferences.get("check_weather"):
            weather = self._get_weather()
            sections.append(BriefingSection(
                name="🌤️ Weather",
                content=weather,
                priority=1
            ))
        
        # Calendar (if enabled)
        if self.preferences.get("check_personal_calendar"):
            personal = self._get_calendar_events("personal")
            if personal:
                sections.append(BriefingSection(
                    name="📅 Personal Calendar",
                    content=personal,
                    priority=1
                ))
        
        if self.preferences.get("check_work_calendar"):
            work = self._get_calendar_events("work")
            if work:
                sections.append(BriefingSection(
                    name="💼 Work Calendar",
                    content=work,
                    priority=1
                ))
        
        # Tasks (from memory)
        tasks = self._get_priority_tasks()
        if tasks:
            sections.append(BriefingSection(
                name="✅ Priority Tasks",
                content=tasks,
                priority=2
            ))
        
        # Trending topics (if enabled)
        if self.preferences.get("trending_topics"):
            trending = self._get_trending_topics()
            sections.append(BriefingSection(
                name="🔥 Trending",
                content=trending,
                priority=3
            ))
        
        # Build the briefing
        briefing = f"# 🌅 Morning Briefing - {now.strftime('%A, %B %d, %Y')}\n\n"
        
        # Sort by priority
        sections.sort(key=lambda x: x.priority)
        
        for section in sections:
            briefing += f"## {section.name}\n{section.content}\n\n"
        
        briefing += f"---\n*Generated at {now.strftime('%I:%M %p')}*"
        
        self.last_briefing = briefing
        return briefing
    
    def _get_weather(self) -> str:
        """Get weather for configured location"""
        # In real implementation, would call weather API
        location = self.preferences.get("location", "San Francisco")
        return f"Weather for {location}: ☀️ Sunny, 72°F\nFeels like 75°F"
    
    def _get_calendar_events(self, domain: str) -> str:
        """Get calendar events for domain"""
        # In real implementation, would call Google Calendar API
        return f"No events scheduled for {domain} calendar"
    
    def _get_priority_tasks(self) -> str:
        """Get priority tasks from memory"""
        # In real implementation, would query task manager
        tasks = [
            "1. Review pending proposals",
            "2. Check system health",
            "3. Process morning emails"
        ]
        return "\n".join(tasks)
    
    def _get_trending_topics(self) -> str:
        """Get trending topics"""
        topics = self.preferences.get("trending_topics", ["AI"])
        return f"Watching: {', '.join(topics)}"
    
    def run_cron(self) -> str:
        """Execute as cron job"""
        briefing = self.generate()
        # In real implementation, would send to configured channel
        return f"Briefing generated ({len(briefing)} chars)"


class AutoApproveRules:
    """Rules for automatic approval of low-risk actions"""
    
    RULES = [
        {
            "name": "Internal Memory Operations",
            "conditions": ["action_type == 'memory_write'", "risk_level == 'low'"],
            "result": "approve",
            "reason": "Memory operations are safe"
        },
        {
            "name": "Read-Only Queries",
            "conditions": ["action_type == 'read'", "risk_level == 'low'"],
            "result": "approve",
            "reason": "Read operations are safe"
        },
        {
            "name": "Local File Reads",
            "conditions": ["action_type == 'file_read'", "risk_level == 'low'"],
            "result": "approve",
            "reason": "Reading local files is safe"
        },
        {
            "name": "Status Checks",
            "conditions": ["action_type == 'status_check'", "risk_level == 'none'"],
            "result": "approve",
            "reason": "Status checks are always safe"
        }
    ]
    
    def evaluate(self, action_type: str, risk_level: str, details: Dict) -> Dict:
        """Evaluate if action should be auto-approved"""
        for rule in self.RULES:
            matches = True
            for condition in rule["conditions"]:
                # Simple condition matching
                if "==" in condition:
                    key, value = condition.split("==")
                    key = key.strip()
                    value = value.strip().strip("'").strip('"')
                    actual_value = details.get(key)
                    if actual_value != value:
                        matches = False
                        break
                elif "!=" in condition:
                    key, value = condition.split("!=")
                    key = key.strip()
                    value = value.strip().strip("'").strip('"')
                    actual_value = details.get(key)
                    if actual_value == value:
                        matches = False
                        break
            
            if matches:
                return {
                    "auto_approved": True,
                    "rule": rule["name"],
                    "reason": rule["reason"]
                }
        
        # Default: require approval for actions
        return {
            "auto_approved": False,
            "reason": "No auto-approve rule matches - requires human approval"
        }


class TaskManager:
    """Simple task management"""
    
    def __init__(self):
        self.tasks: List[Dict] = []
        
    def add(self, title: str, domain: str = "personal", priority: int = 3):
        """Add a task"""
        task = {
            "id": f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "title": title,
            "domain": domain,
            "priority": priority,
            "status": "pending",
            "created": datetime.now().isoformat()
        }
        self.tasks.append(task)
        return f"✅ Task added: {title} ({domain}, priority {priority})"
    
    def list(self, domain: str = None, status: str = "pending") -> str:
        """List tasks"""
        filtered = [t for t in self.tasks if t["status"] == status]
        if domain:
            filtered = [t for t in filtered if t["domain"] == domain]
        
        if not filtered:
            return "No tasks found."
        
        result = f"📋 Tasks ({len(filtered)}):\n"
        for t in filtered:
            emoji = "🔴" if t["priority"] >= 4 else "🟡" if t["priority"] >= 3 else "🟢"
            result += f"{emoji} {t['title']} ({t['domain']})\n"
        
        return result
    
    def complete(self, task_id: str) -> str:
        """Mark task as complete"""
        for t in self.tasks:
            if t["id"] == task_id or task_id in t["title"]:
                t["status"] = "completed"
                t["completed"] = datetime.now().isoformat()
                return f"✅ Completed: {t['title']}"
        return "Task not found"


class HealthMonitor:
    """System health monitoring"""
    
    def __init__(self):
        self.checks = []
        
    def add_check(self, name: str, check_func):
        """Add a health check"""
        self.checks.append({"name": name, "func": check_func})
    
    def run_all(self) -> Dict:
        """Run all health checks"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "checks": [],
            "overall": "healthy"
        }
        
        healthy_count = 0
        
        for check in self.checks:
            try:
                result = check["func"]()
                results["checks"].append({
                    "name": check["name"],
                    "status": "ok" if result else "warning",
                    "result": result
                })
                if result:
                    healthy_count += 1
            except Exception as e:
                results["checks"].append({
                    "name": check["name"],
                    "status": "error",
                    "error": str(e)
                })
                results["overall"] = "degraded"
        
        results["healthy_count"] = healthy_count
        results["total_checks"] = len(self.checks)
        
        return results
    
    def get_status(self) -> str:
        """Get human-readable status"""
        results = self.run_all()
        
        lines = [f"# 🏥 Health Status - {results['timestamp']}"]
        lines.append(f"**Overall:** {results['overall'].upper()}")
        lines.append(f"**Checks:** {results['healthy_count']}/{results['total_checks']} healthy\n")
        
        for check in results["checks"]:
            emoji = "✅" if check["status"] == "ok" else "⚠️" if check["status"] == "warning" else "❌"
            lines.append(f"{emoji} {check['name']}")
            if check.get("result"):
                lines.append(f"   {check['result']}")
            if check.get("error"):
                lines.append(f"   Error: {check['error']}")
        
        return "\n".join(lines)


# Default health checks
def default_health_checks():
    """Create default health monitoring setup"""
    monitor = HealthMonitor()
    
    # Gateway check
    monitor.add_check("Gateway", lambda: True)  # Would check actual gateway
    
    # Database check
    monitor.add_check("Database", lambda: True)  # Would check PostgreSQL
    
    # Memory check
    monitor.add_check("Memory", lambda: True)  # Would verify memory system
    
    # Council check
    monitor.add_check("Council", lambda: True)  # Would verify council ready
    
    return monitor


if __name__ == "__main__":
    # Test briefing
    briefing = MorningBriefingSkill()
    print("=== Morning Briefing ===")
    print(briefing.generate())
    
    print("\n=== Health Check ===")
    health = default_health_checks()
    print(health.get_status())
    
    print("\n=== Task Manager ===")
    tasks = TaskManager()
    print(tasks.add("Review proposals", "personal", 3))
    print(tasks.add("Check system health", "work", 4))
    print(tasks.list())
